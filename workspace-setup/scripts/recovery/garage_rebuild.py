#!/usr/bin/env python3
"""Explicit, private garage snapshots and exact Git checkpoint recovery."""
import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata
from urllib.parse import urlsplit

VERSION = 1
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_PRIVATE_FILE_BYTES = 2 * 1024 * 1024 * 1024
MAX_PRIVATE_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
STREAM_CHUNK_BYTES = 1024 * 1024
RESERVED = {"apps", ".garage-private", ".garage-recovery.json", ".incomplete"}
SECRET_NAMES = {".git", ".git-credentials", ".gitconfig", ".ssh", ".aws", ".gnupg", ".netrc", ".npmrc", ".pypirc",
                ".config", ".kube", ".azure", ".codex", ".claude", "auth.json",
                ".docker", "credentials", "credentials.json", "secrets", "secrets.json",
                "secrets.yaml", "secrets.yml", "id_rsa", "id_ed25519", "id_ecdsa"}
SECRET_PATTERN = re.compile(
    rb"https?://[^\s/@:]+:[^\s/@]+@|-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|"
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    rb"AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{15,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,})\b")


class Refusal(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Refusal(message)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(path.read_bytes(), object_pairs_hook=unique)
    except (ValueError, UnicodeError) as error:
        raise Refusal("invalid JSON") from error


def fields(value, required, optional=()):
    need(isinstance(value, dict), "expected JSON object")
    need(set(required) <= set(value) <= set(required) | set(optional), "invalid schema fields")


def relpath(value):
    need(isinstance(value, str) and value and "\\" not in value and
         not any(ord(c) < 32 or ord(c) == 127 for c in value), "invalid relative path")
    path = PurePosixPath(value)
    need(bool(path.parts) and not path.is_absolute() and str(path) == value and
         all(p not in {".", ".."} for p in path.parts), "unsafe relative path")
    return value


def path_key(value):
    return unicodedata.normalize("NFC", value).casefold()


def register_path(keys, value):
    for path in [value] + [str(p) for p in PurePosixPath(value).parents if str(p) != "."]:
        key = path_key(path)
        need(key not in keys or keys[key] == path, "portable path collision: " + path)
        keys[key] = path


def string_list(value):
    need(isinstance(value, list) and all(isinstance(x, str) and x for x in value), "expected string list")
    return value


def secret_name(path):
    return any(p.casefold() in SECRET_NAMES or p.casefold().startswith(".env") or
               p.casefold().endswith((".pem", ".p12", ".pfx", ".key", ".keychain", ".keychain-db"))
               for p in PurePosixPath(path).parts)


def scan_secret(data, path):
    need(not SECRET_PATTERN.search(data), "recognizable secret content refused in " + path)


def stream_file(path, private=False, output=None):
    """Hash/scan/copy a regular file without allocating its whole contents."""
    before = path.lstat()
    limit = MAX_PRIVATE_FILE_BYTES if private else MAX_FILE_BYTES
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "special or hard-linked file refused: " + str(path))
    need(before.st_size <= limit, "file exceeds " + ("2 GiB private" if private else "128 MiB") + " limit: " + str(path))
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    digest, count, tail = hashlib.sha256(), 0, b""
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as source:
        opened = os.fstat(source.fileno())
        need(all(getattr(opened, key) == getattr(before, key) for key in stable), "source changed before reading: " + str(path))
        while True:
            chunk = source.read(STREAM_CHUNK_BYTES)
            if not chunk:
                break
            if count == 0:
                need(private or not chunk.startswith(b"%PDF-"), "PDF must be selected via private_include: " + str(path))
            count += len(chunk)
            need(count <= limit, "file grew beyond size limit: " + str(path))
            scan_secret(tail + chunk, str(path))
            tail = (tail + chunk)[-1024:]
            digest.update(chunk)
            if output is not None:
                output.write(chunk)
        final_open = os.fstat(source.fileno())
    after = path.lstat()
    need(count == before.st_size and all(getattr(final_open, key) == getattr(before, key) == getattr(after, key) for key in stable),
         "source changed while reading: " + str(path))
    return {"size": count, "sha256": digest.hexdigest(), "mode": 0o755 if before.st_mode & 0o111 else 0o644}


def copy_file_verified(source, destination, entry, private=False):
    need(source.parent.resolve() == source.parent and destination.parent.resolve() == destination.parent,
         "symlink source/destination parent")
    with destination.open("xb") as output:
        observed = stream_file(source, private=private, output=output)
    need(observed["sha256"] == entry["sha256"] and observed["size"] == entry["size"] and observed["mode"] == entry["mode"],
         "source integrity changed: " + str(source))
    destination.chmod(entry["mode"])


def is_within(path, root):
    return path == root or root in path.parents


def real_root(path):
    path = Path(os.path.abspath(path))
    need(path.exists() and path.is_dir() and path.resolve() == path, "root must be a real directory, without symlink components")
    return path


def fresh_path(path):
    path = Path(os.path.abspath(path))
    need(not os.path.lexists(path), "destination already exists: " + str(path))
    need(path.parent.exists() and path.parent.resolve() == path.parent, "destination parent must exist without symlinks")
    return path


def git(cwd, *args, local=False, allow_failure=False, input_bytes=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", GIT_LFS_SKIP_SMUDGE="1",
               GIT_ALLOW_PROTOCOL="https:ssh" + (":file" if local else ""))
    command = ["git", "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false",
               "-c", "core.sshCommand=ssh -F /dev/null -o BatchMode=yes",
               "-c", "credential.helper=", "-c", "protocol.ext.allow=never",
               "-c", "fetch.recurseSubmodules=false", "-c", "submodule.recurse=false",
               "-c", "init.templateDir=", "-C", str(cwd), *args]
    try:
        result = subprocess.run(command, env=env, input=input_bytes, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=300)
    except subprocess.TimeoutExpired as error:
        raise Refusal("Git timed out; check repository access/authentication") from error
    if result.returncode and not allow_failure:
        # Git stderr can contain credentials from local config or transport errors.
        raise Refusal("Git " + args[0] + " failed; check access, credentials, and selected refs (stderr withheld)")
    return result


def git_text(cwd, *args, local=False):
    return git(cwd, *args, local=local).stdout.decode("utf-8", "strict").strip()


def branch_name(value):
    need(isinstance(value, str) and value and not value.startswith("-") and
         not value.startswith("recovery/"), "invalid or reserved branch name")
    result = git(Path.cwd(), "check-ref-format", "refs/heads/" + value, allow_failure=True)
    need(result.returncode == 0, "invalid branch name")
    return value


def origin_url(value, allow_local):
    need(isinstance(value, str) and value and not any(c.isspace() for c in value), "invalid origin")
    if value.startswith("https://"):
        url = urlsplit(value)
        need(url.hostname and not url.username and not url.password and not url.query and not url.fragment,
             "origin must not contain credentials/query/fragment")
    elif value.startswith("ssh://"):
        url = urlsplit(value)
        need(url.hostname and url.username in {None, "git"} and not url.password and not url.query and not url.fragment,
             "invalid SSH origin")
    elif re.fullmatch(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+", value):
        pass
    elif allow_local and Path(value).is_absolute() and Path(value).resolve() == Path(value):
        pass
    else:
        raise Refusal("unsupported origin; HTTPS or SSH required (local paths require --allow-local-origins)")
    return value


def validate_repositories(repositories, allow_local, recorded=False):
    need(isinstance(repositories, list), "repositories must be a list")
    seen = set()
    for repo in repositories:
        required = {"path", "origin", "base_branch", "checkout", "branches", "ignored_exclusions"}
        if recorded:
            required |= {"source_head", "remote_verified_at", "ignored_files", "base_commit"}
        fields(repo, required)
        path = relpath(repo["path"])
        need(len(PurePosixPath(path).parts) == 2 and path.startswith("apps/") and not secret_name(path),
             "repository path must be a direct apps/ child")
        need(path_key(path) not in seen, "repository path collision")
        seen.add(path_key(path))
        origin_url(repo["origin"], allow_local)
        branch_name(repo["base_branch"])
        branch_name(repo["checkout"])
        string_list(repo["ignored_exclusions"])
        need(isinstance(repo["branches"], list) and repo["branches"], "selected branches required")
        names = set()
        for branch in repo["branches"]:
            fields(branch, {"name", "remote_ref"} | ({"commit", "remote_commit"} if recorded else set()), {"pull_request"})
            name = branch_name(branch["name"])
            need(path_key(name) not in names, "branch collision")
            names.add(path_key(name))
            ref = branch["remote_ref"]
            need(isinstance(ref, str) and (ref.startswith("refs/heads/") or re.fullmatch(r"refs/pull/[1-9][0-9]*/head", ref)), "invalid selected remote ref")
            need(git(Path.cwd(), "check-ref-format", ref, allow_failure=True).returncode == 0, "invalid remote ref")
            if "pull_request" in branch:
                pr = branch["pull_request"]
                fields(pr, {"url", "state", "head_ref"})
                origin_url(pr["url"], False)
                need(pr["url"].startswith("https://") and pr["state"] in {"draft", "open", "closed", "merged"} and isinstance(pr["head_ref"], str), "invalid supplied PR metadata")
            if recorded:
                for key in ("commit", "remote_commit"):
                    need(isinstance(branch[key], str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", branch[key]), "invalid commit")
        need(path_key(repo["checkout"]) in names, "checkout branch must be selected")


def validate_selection(plan, allow_local):
    need(not isinstance(plan, dict) or not plan.get("private_restore"),
         "private_restore mappings require garage_workspace.py; full-Git mode does not apply overlays")
    fields(plan, {"version", "include", "exclude", "private_include", "repositories"}, {"notes"})
    need(plan["version"] == VERSION, "unsupported selection version")
    string_list(plan["exclude"])
    for key in ("include", "private_include"):
        paths = string_list(plan[key])
        seen = set()
        for path in paths:
            relpath(path)
            if key == "include":
                need(path_key(PurePosixPath(path).parts[0]) not in RESERVED, "reserved garage path")
            need(not any(path == p or path.startswith(p + "/") or p.startswith(path + "/") for p in seen), "overlapping selected paths")
            seen.add(path)
    validate_repositories(plan["repositories"], allow_local)
    scan_secret(json_bytes(plan.get("notes", {})), "selection notes")


def collect(root, selected, exclusions, private=False):
    entries, skipped, keys = {}, [], {}
    def visit(relative):
        relpath(relative)
        path = root / relative
        if secret_name(relative) or any(fnmatch.fnmatchcase(relative, pattern) for pattern in exclusions):
            skipped.append({"path": relative, "reason": "secret-name or explicit exclusion"})
            return
        need(not (not private and (relative.casefold().endswith(".pdf"))), "PDF must be selected via private_include: " + relative)
        register_path(keys, relative)
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            link = os.readlink(path)
            need(not os.path.isabs(link) and "\\" not in link, "unsafe symlink: " + relative)
            try:
                resolved = path.resolve(strict=True)
            except (OSError, RuntimeError) as error:
                raise Refusal("dangling or cyclic symlink: " + relative) from error
            need(is_within(resolved, root), "escaping symlink: " + relative)
            entries[relative] = {"path": relative, "type": "symlink", "target": link, "sha256": sha(os.fsencode(link))}
        elif stat.S_ISDIR(st.st_mode):
            entries[relative] = {"path": relative, "type": "directory"}
            for child in sorted(path.iterdir()):
                visit(child.relative_to(root).as_posix())
        else:
            metadata = stream_file(path, private=private)
            entries[relative] = {"path": relative, "type": "file", **metadata}
    for selected_path in selected:
        # Do not permit symlinks in ancestors of a selected root.
        parent = (root / selected_path).parent
        need(parent.resolve() == parent, "symlink ancestor in selected path")
        visit(selected_path)
    for relative, entry in entries.items():
        if entry["type"] == "symlink":
            resolved = (root / relative).resolve(strict=True).relative_to(root).as_posix()
            need(resolved in entries, "symlink target is not selected: " + relative)
    need(not private or sum(e.get("size", 0) for e in entries.values()) <= MAX_PRIVATE_TOTAL_BYTES,
         "private payload exceeds 8 GiB total limit")
    return list(entries.values()), skipped


def copy_entries(source, target, entries, private=False):
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    for entry in sorted(entries, key=lambda e: (e["type"] == "symlink", len(PurePosixPath(e["path"]).parts), e["path"])):
        src, dst = source / entry["path"], target / entry["path"]
        dst.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        need(dst.parent.resolve() == dst.parent, "symlink destination parent")
        if entry["type"] == "directory":
            dst.mkdir(exist_ok=True, mode=0o700)
        elif entry["type"] == "symlink":
            need(os.readlink(src) == entry["target"], "source symlink changed")
            dst.symlink_to(entry["target"])
        else:
            copy_file_verified(src, dst, entry, private=private)


def check_source_repo(source, repo, private_paths):
    path = source / repo["path"]
    real_root(path)
    config = check_repo_config(path)
    need(git_text(path, "rev-parse", "--show-toplevel") == str(path), "repository root mismatch")
    need(git_text(path, "rev-parse", "--is-shallow-repository") == "false", "shallow repository unsupported")
    need("extensions.partialclone=" not in config.casefold() and ".promisor=true" not in config.casefold(), "partial clone unsupported")
    need(git_text(path, "remote", "get-url", "origin") == repo["origin"], "selected origin does not match source origin")
    check_index_flags(path)
    status = git_text(path, "status", "--porcelain=v1", "--untracked-files=all")
    need(not status, "dirty or untracked application work in " + repo["path"] + ": " + status)
    need(not git_text(path, "stash", "list"), "local stash is not protected: " + repo["path"])
    ignored = git(path, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").stdout.decode().split("\0")
    ignored = [x for x in ignored if x]
    for item in ignored:
        need(any(fnmatch.fnmatchcase(item, pattern) for pattern in repo["ignored_exclusions"]) or
             repo["path"] + "/" + item in private_paths, "unhandled ignored input in " + repo["path"] + ": " + item)
    need(git_text(path, "branch", "--show-current") == repo["checkout"], "source HEAD must be on selected checkout branch")
    recorded = json.loads(json.dumps(repo))
    recorded.update(source_head=git_text(path, "rev-parse", "HEAD"), ignored_files=ignored)
    for branch in recorded["branches"]:
        commit = git_text(path, "rev-parse", "--verify", "refs/heads/" + branch["name"] + "^{commit}")
        branch["commit"] = commit
        tree = git_text(path, "ls-tree", "-r", commit)
        need(not any(line.startswith("160000 ") for line in tree.splitlines()), "submodules unsupported in v1")
        pointer = git(path, "grep", "-l", "-F", "version https://git-lfs.github.com/spec/v1", commit, allow_failure=True)
        need(pointer.returncode == 1, "LFS pointer or Git inspection failure; LFS unsupported in v1")
    return recorded


def check_repo_config(path):
    config = git_text(path, "config", "--local", "--no-includes", "--list")
    for line in config.splitlines():
        key = line.partition("=")[0].casefold()
        need(key != "extensions.worktreeconfig", "worktree Git configuration unsupported in v1")
        need(not key.startswith(("include.", "includeif.", "filter.", "alias.")),
             "unsupported executable/include Git configuration")
    return config


def check_index_flags(path):
    index = git(path, "ls-files", "--stage", "-z").stdout.split(b"\0")
    head_tree = git(path, "ls-tree", "-r", "-z", "HEAD").stdout.split(b"\0")
    core_entries = index + head_tree
    need(not any(entry.startswith(b"160000 ") for entry in core_entries),
         "submodules unsupported; refused before worktree status inspection")
    entries = git(path, "ls-files", "-v", "-z").stdout.split(b"\0")
    need(all(not entry or (entry[0:1] != b"S" and not entry[0:1].islower()) for entry in entries),
         "unsupported assume-unchanged/skip-worktree index flags: " + str(path))
    for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer", "BISECT_LOG"):
        state_path = Path(git_text(path, "rev-parse", "--git-path", name))
        if not state_path.is_absolute():
            state_path = path / state_path
        need(not os.path.lexists(state_path), "in-progress Git operation is not a recoverable checkpoint: " + name)


def fetch_repo(destination, repo, allow_local):
    destination.mkdir(mode=0o700)
    git(destination, "init", "--template=", "-q")
    git(destination, "remote", "add", "origin", repo["origin"])
    refs = ["refs/heads/" + repo["base_branch"]] + [b["remote_ref"] for b in repo["branches"]]
    mapped = {}
    for index, ref in enumerate(dict.fromkeys(refs)):
        local_ref = "refs/remotes/origin/garage-selected-" + str(index)
        git(destination, "fetch", "--no-tags", "--no-recurse-submodules", "origin", ref + ":" + local_ref, local=allow_local)
        mapped[ref] = git_text(destination, "rev-parse", local_ref + "^{commit}")
    return mapped


def export_snapshot(args):
    source = real_root(args.source)
    out = fresh_path(args.out)
    need(not is_within(out, source) and not is_within(source, out), "snapshot destination must be outside source")
    plan = read_json(Path(args.selection))
    validate_selection(plan, args.allow_local_origins)
    files, skipped = collect(source, plan["include"], plan["exclude"])
    private, private_skipped = collect(source, plan["private_include"], plan["exclude"], private=True)
    private_paths = {f["path"] for f in private}
    repositories = []
    for selected in plan["repositories"]:
        repo = check_source_repo(source, selected, private_paths)
        with tempfile.TemporaryDirectory(prefix="garage-remote-check-") as temp:
            refs = fetch_repo(Path(temp) / "repo", repo, args.allow_local_origins)
            repo["base_commit"] = refs["refs/heads/" + repo["base_branch"]]
            for branch in repo["branches"]:
                remote = refs[branch["remote_ref"]]
                need(remote == branch["commit"], "remote checkpoint differs for " + repo["path"] + ": " + branch["name"])
                branch["remote_commit"] = remote
        repo["remote_verified_at"] = now()
        repositories.append(repo)
    out.mkdir(mode=0o700)
    (out / ".incomplete").write_text("Export has not completed\n")
    copy_entries(source, out / "garage", files)
    (out / "garage/apps").mkdir(mode=0o700)
    files.append({"path": "apps", "type": "directory"})
    copy_entries(source, out / "private", private, private=True)
    # Recheck source inputs/repository checkpoints to detect concurrent edits.
    second_files, _ = collect(source, plan["include"], plan["exclude"])
    second_private, _ = collect(source, plan["private_include"], plan["exclude"], private=True)
    need(second_files == files[:-1] and second_private == private, "source changed during export")
    for selected, recorded in zip(plan["repositories"], repositories):
        current = check_source_repo(source, selected, private_paths)
        need(current["source_head"] == recorded["source_head"] and
             [b["commit"] for b in current["branches"]] == [b["commit"] for b in recorded["branches"]], "source repository changed during export")
    manifest = {"version": VERSION, "created_at": now(), "source": str(source), "files": files,
                "private_files": private, "repositories": repositories,
                "excluded": skipped + private_skipped, "selection": plan,
                "tool_versions": {"python": sys.version.split()[0], "git": git_text(source, "--version")}}
    data = json_bytes(manifest)
    (out / "manifest.json").write_bytes(data)
    (out / "manifest.sha256").write_text(sha(data) + "\n")
    verify_snapshot(out, args.allow_local_origins, incomplete_ok=True)
    (out / ".incomplete").unlink()
    print("Export verified: " + str(out))
    print("Manifest SHA-256: " + sha(data))


def validate_entries(entries, private=False):
    need(isinstance(entries, list), "invalid file inventory")
    paths, types, keys = set(), {}, {}
    for entry in entries:
        need(isinstance(entry, dict) and entry.get("type") in {"file", "directory", "symlink"}, "invalid inventory entry")
        kind = entry["type"]
        extra = {"file": {"sha256", "size", "mode"}, "symlink": {"target", "sha256"}, "directory": set()}[kind]
        fields(entry, {"path", "type"} | extra)
        path = relpath(entry["path"])
        need(path not in paths, "duplicate inventory path")
        register_path(keys, path)
        need(not secret_name(path), "secret path in inventory")
        if not private:
            need(path_key(PurePosixPath(path).parts[0]) not in RESERVED or (path == "apps" and kind == "directory"), "reserved path in inventory")
            need(not path.casefold().endswith(".pdf"), "PDF outside private inventory")
        if kind != "directory":
            need(isinstance(entry["sha256"], str) and re.fullmatch("[0-9a-f]{64}", entry["sha256"]), "invalid inventory hash")
        if kind == "file":
            limit = MAX_PRIVATE_FILE_BYTES if private else MAX_FILE_BYTES
            need(type(entry["size"]) is int and 0 <= entry["size"] <= limit and entry["mode"] in {0o644, 0o755}, "invalid file metadata")
        if kind == "symlink":
            target = entry["target"]
            need(isinstance(target, str) and target and not os.path.isabs(target) and "\\" not in target and not any(ord(c) < 32 for c in target), "unsafe symlink target")
        paths.add(path)
        types[path] = kind
    for path in paths:
        for parent in PurePosixPath(path).parents:
            if str(parent) != ".":
                need(types.get(str(parent), "directory") == "directory", "non-directory ancestor in inventory")
    need(not private or sum(e.get("size", 0) for e in entries) <= MAX_PRIVATE_TOTAL_BYTES, "private payload exceeds 8 GiB total limit")
    return paths


def actual_paths(root):
    result = set()
    def visit(path):
        for child in path.iterdir():
            result.add(child.relative_to(root).as_posix())
            if child.is_dir() and not child.is_symlink():
                visit(child)
    visit(root)
    return result


def verify_payload(root, entries, exact=True, private=False):
    real_root(root)
    expected = {e["path"] for e in entries}
    # Ancestors implicitly created for selected individual files count as inventory.
    for path in list(expected):
        expected.update(str(p) for p in PurePosixPath(path).parents if str(p) != ".")
    if exact:
        need(actual_paths(root) == expected, "payload inventory mismatch: " + str(root))
    for entry in entries:
        path = root / entry["path"]
        need(path.parent.resolve() == path.parent, "symlink parent in payload")
        st = path.lstat()
        kind = entry["type"]
        if kind == "directory":
            need(stat.S_ISDIR(st.st_mode), "directory integrity mismatch")
        elif kind == "symlink":
            need(stat.S_ISLNK(st.st_mode) and os.readlink(path) == entry["target"] and
                 sha(os.fsencode(os.readlink(path))) == entry["sha256"], "symlink integrity mismatch")
            try:
                resolved = path.resolve(strict=True)
            except (OSError, RuntimeError) as error:
                raise Refusal("unsafe symlink in payload") from error
            need(is_within(resolved, root) and resolved.relative_to(root).as_posix() in expected, "escaping/unselected symlink in payload")
        else:
            need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size == entry["size"] and
                 (0o755 if st.st_mode & 0o111 else 0o644) == entry["mode"], "file integrity mismatch: " + entry["path"])
            observed = stream_file(path, private=private)
            need(observed["sha256"] == entry["sha256"] and observed["size"] == entry["size"], "file integrity mismatch: " + entry["path"])


def verify_snapshot(snapshot, allow_local, incomplete_ok=False):
    root = real_root(snapshot)
    need(incomplete_ok or not (root / ".incomplete").exists(), "snapshot is incomplete")
    allowed = {"manifest.json", "manifest.sha256", "garage", "private"} | ({".incomplete"} if incomplete_ok else set())
    need({p.name for p in root.iterdir()} == allowed, "snapshot root inventory mismatch")
    for name in ("manifest.json", "manifest.sha256"):
        need(not (root / name).is_symlink() and (root / name).is_file(), "unsafe manifest path")
    data = (root / "manifest.json").read_bytes()
    need((root / "manifest.sha256").read_text().strip() == sha(data), "manifest integrity mismatch")
    manifest = read_json(root / "manifest.json")
    fields(manifest, {"version", "created_at", "source", "files", "private_files", "repositories", "excluded", "selection", "tool_versions"})
    need(manifest["version"] == VERSION, "unsupported manifest version")
    validate_selection(manifest["selection"], allow_local)
    validate_repositories(manifest["repositories"], allow_local, recorded=True)
    validate_entries(manifest["files"])
    validate_entries(manifest["private_files"], private=True)
    verify_payload(root / "garage", manifest["files"])
    verify_payload(root / "private", manifest["private_files"], private=True)
    need(any(e == {"path": "apps", "type": "directory"} for e in manifest["files"]), "empty apps directory missing")
    return manifest


def restore_repositories(target, repositories, allow_local):
    recovered = []
    for repo in repositories:
        path = target / repo["path"]
        refs = fetch_repo(path, repo, allow_local)
        result = {"path": repo["path"], "branches": [], "head": repo["source_head"]}
        selected_name = None
        for branch in repo["branches"]:
            commit = branch["commit"]
            available = git(path, "cat-file", "-e", commit + "^{commit}", allow_failure=True)
            need(available.returncode == 0, "unavailable checkpoint for " + repo["path"] + ": " + branch["name"])
            moved = refs[branch["remote_ref"]] != commit
            name = ("recovery/" if moved else "") + branch["name"]
            git(path, "branch", "--no-track", name, commit)
            result["branches"].append({"original": branch["name"], "restored": name,
                                       "commit": commit, "remote_commit_now": refs[branch["remote_ref"]], "moved": moved})
            if moved:
                print("Remote ref moved; preserving checkpoint as " + repo["path"] + ":" + name)
            if branch["name"] == repo["checkout"]:
                selected_name = name
        need(selected_name is not None, "checkout branch absent")
        git(path, "checkout", "--no-guess", selected_name)
        result["checkout"] = selected_name
        recovered.append(result)
    return recovered


def verify_target(snapshot, target, manifest, receipt):
    target = real_root(target)
    fields(receipt, {"version", "verified_at", "snapshot", "manifest_sha256", "repositories"})
    need(receipt["version"] == VERSION and isinstance(receipt["repositories"], list), "invalid receipt")
    need(receipt["manifest_sha256"] == sha((snapshot / "manifest.json").read_bytes()), "receipt manifest integrity mismatch")
    verify_payload(target, manifest["files"], exact=False)
    verify_payload(target / ".garage-private", manifest["private_files"], private=True)
    need(len(receipt["repositories"]) == len(manifest["repositories"]), "receipt repository mismatch")
    for repo, recovered in zip(manifest["repositories"], receipt["repositories"]):
        fields(recovered, {"path", "branches", "head", "checkout"})
        need(repo["path"] == recovered["path"], "receipt path mismatch")
        need(recovered["head"] == repo["source_head"], "receipt head mismatch")
        need(isinstance(recovered["branches"], list) and len(recovered["branches"]) == len(repo["branches"]),
             "receipt branch inventory mismatch")
        path = target / repo["path"]
        real_root(path)
        check_repo_config(path)
        check_index_flags(path)
        need(git_text(path, "rev-parse", "HEAD") == repo["source_head"], "restored HEAD integrity mismatch")
        need(git_text(path, "branch", "--show-current") == recovered["checkout"], "restored checkout branch mismatch")
        need(not git_text(path, "status", "--porcelain=v1", "--untracked-files=all"), "restored repository is dirty")
        for branch, restored in zip(repo["branches"], recovered["branches"]):
            fields(restored, {"original", "restored", "commit", "remote_commit_now", "moved"})
            need(restored["original"] == branch["name"] and restored["commit"] == branch["commit"] and
                 type(restored["moved"]) is bool and isinstance(restored["remote_commit_now"], str) and
                 re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", restored["remote_commit_now"]), "receipt branch metadata mismatch")
            need(restored["moved"] == (restored["remote_commit_now"] != branch["commit"]), "receipt branch movement mismatch")
            expected_name = ("recovery/" if restored["moved"] else "") + branch["name"]
            need(restored["restored"] == expected_name, "receipt branch name mismatch")
            if branch["name"] == repo["checkout"]:
                need(recovered["checkout"] == expected_name, "receipt checkout mismatch")
            need(git_text(path, "rev-parse", "refs/heads/" + restored["restored"]) == branch["commit"], "restored branch integrity mismatch")


def bootstrap(args):
    snapshot = real_root(args.snapshot)
    manifest = verify_snapshot(snapshot, args.allow_local_origins)
    target = fresh_path(args.target)
    need(not is_within(target, snapshot), "target must be outside snapshot")
    target.mkdir(mode=0o700)
    (target / ".incomplete").write_text("Bootstrap has not completed\n")
    copy_entries(snapshot / "garage", target, manifest["files"])
    copy_entries(snapshot / "private", target / ".garage-private", manifest["private_files"], private=True)
    recovered = restore_repositories(target, manifest["repositories"], args.allow_local_origins)
    receipt = {"version": VERSION, "verified_at": now(), "snapshot": str(snapshot),
               "manifest_sha256": sha((snapshot / "manifest.json").read_bytes()), "repositories": recovered}
    verify_target(snapshot, target, manifest, receipt)
    (target / ".garage-recovery.json").write_bytes(json_bytes(receipt))
    (target / ".incomplete").unlink()
    print("Rebuilt and verified exact checkpoints: " + str(target))
    print("Private inputs are staged in .garage-private; no setup commands were run")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Create a new private garage snapshot from a reviewed selection")
    export.add_argument("--source", required=True)
    export.add_argument("--selection", required=True)
    export.add_argument("--out", required=True)
    restore = sub.add_parser("bootstrap", help="Restore into a fresh, absent target")
    restore.add_argument("--snapshot", required=True)
    restore.add_argument("--target", required=True)
    verify = sub.add_parser("verify", help="Verify snapshot and optional rebuilt target")
    verify.add_argument("--snapshot", required=True)
    verify.add_argument("--target")
    for command in (export, restore, verify):
        command.add_argument("--allow-local-origins", action="store_true", help="Explicitly permit local Git origins; never implied")
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            export_snapshot(args)
        elif args.command == "bootstrap":
            bootstrap(args)
        else:
            snapshot = real_root(args.snapshot)
            manifest = verify_snapshot(snapshot, args.allow_local_origins)
            if args.target:
                target = real_root(args.target)
                need(not (target / ".incomplete").exists(), "target is incomplete")
                receipt_path = target / ".garage-recovery.json"
                receipt_stat = receipt_path.lstat()
                need(stat.S_ISREG(receipt_stat.st_mode) and receipt_stat.st_nlink == 1, "unsafe receipt path")
                verify_target(snapshot, target, manifest, read_json(receipt_path))
            print("Integrity verified")
        return 0
    except (Refusal, OSError, ValueError, UnicodeError, KeyError, TypeError) as error:
        print("Refused: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
