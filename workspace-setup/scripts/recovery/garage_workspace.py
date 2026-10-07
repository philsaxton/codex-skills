#!/usr/bin/env python3
"""Default garage recovery: connector-supplied source files, never Git history."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from urllib.parse import quote, urlsplit

import garage_rebuild as core

VERSION = 2
BUNDLE_NAME = ".garage-source-bundle.json"
MAX_BUNDLE_BYTES = 128 * 1024 * 1024
MAX_BLOB_BYTES = 32 * 1024 * 1024
# Count path occurrences, including directories and symlinks, across every
# selected checkpoint in a bundle. Shared Git objects do not share this budget.
MAX_EXPANDED_ENTRIES = 10_000
BASE_REPO_KEYS = {"path", "origin", "base_branch", "checkout", "branches", "ignored_exclusions"}


def oid(value):
    core.need(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), "invalid Git SHA-1 object ID")
    return value


def repository_name(value):
    core.need(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value), "invalid GitHub repository name")
    core.need(all(p not in {".", ".."} for p in value.split("/")), "invalid GitHub repository name")
    return value


def github_origin(origin):
    core.origin_url(origin, False)
    if origin.startswith("git@github.com:"):
        path = origin[len("git@github.com:"):]
    else:
        url = urlsplit(origin)
        core.need(url.hostname == "github.com" and url.port is None, "connector mode requires a github.com origin")
        path = url.path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return repository_name(path)


def validate_plan(plan):
    core.need(isinstance(plan, dict), "invalid selection")
    core.validate_selection({k: v for k, v in plan.items() if k != "private_restore"}, False)
    mappings = plan.get("private_restore", [])
    core.need(isinstance(mappings, list), "private_restore must be a list")
    destinations = []
    for mapping in mappings:
        core.fields(mapping, {"source", "destination"})
        core.relpath(mapping["source"])
        destination = core.relpath(mapping["destination"])
        core.need(any(destination.startswith(r["path"] + "/") for r in plan["repositories"]),
                  "private restore destination must be beneath a selected app")
        key = core.path_key(destination)
        core.need(not any(key == p or key.startswith(p + "/") or p.startswith(key + "/") for p in destinations),
                  "overlapping private restore destinations")
        destinations.append(key)
    for path in plan["include"]:
        core.need(core.path_key(PurePosixPath(path).parts[0]) != BUNDLE_NAME, "reserved connector bundle path")
    for repo in plan["repositories"]:
        github_origin(repo["origin"])


def overlay_inventory(manifest):
    private = {entry["path"]: entry for entry in manifest["private_files"]}
    overlays = []
    for mapping in manifest["selection"].get("private_restore", []):
        source = mapping["source"]
        core.need(source in private, "private restore source is not selected: " + source)
        root = private[source]
        selected = [entry for path, entry in private.items() if path == source or
                    (root["type"] == "directory" and path.startswith(source + "/"))]
        core.need(not any(entry["type"] == "symlink" for entry in selected), "symlink private overlays are unsupported")
        files = [entry for entry in selected if entry["type"] == "file"]
        core.need(files, "private restore mapping contains no regular files")
        for entry in files:
            suffix = entry["path"][len(source):] if root["type"] == "directory" else ""
            overlays.append({**entry, "source": entry["path"], "path": mapping["destination"] + suffix})
    core.validate_entries([{k: v for k, v in entry.items() if k != "source"} for entry in overlays], private=True)
    return sorted(overlays, key=lambda entry: entry["path"])


def require_checkpoint_ignore_rules(source, paths):
    """Evaluate only tracked .gitignore bytes in an isolated, credential-free repo."""
    with tempfile.TemporaryDirectory(prefix="garage-ignore-check-") as directory:
        root = Path(directory)
        core.git(root, "init", "--template=", "-q")
        for entry in source["entries"]:
            if PurePosixPath(entry["path"]).name == ".gitignore":
                core.need(entry["type"] == "file", "tracked .gitignore must be a regular file for private restoration")
                destination = root / entry["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source["bytes"][entry["path"]])
        for path in paths:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
        result = core.git(root, "-c", "core.excludesFile=" + os.devnull,
                          "check-ignore", "--no-index", "-z", "--stdin", allow_failure=True,
                          input_bytes=b"\0".join(path.encode("utf-8") for path in paths) + b"\0")
        core.need(result.returncode in {0, 1}, "could not evaluate checkpoint ignore rules")
        ignored = {p.decode("utf-8") for p in result.stdout.split(b"\0") if p}
        missing = sorted(set(paths) - ignored)
        core.need(not missing, "private destination is not ignored by tracked checkpoint rules: " + (missing[0] if missing else ""))


def prepare_overlays(manifest, sources):
    overlays = overlay_inventory(manifest)
    for repo in manifest["repositories"]:
        prefix = repo["path"] + "/"
        selected = [entry for entry in overlays if entry["path"].startswith(prefix)]
        if not selected:
            continue
        source = sources[(repo["github_repository"], repo["source_head"])]
        tracked = {entry["path"]: entry for entry in source["entries"]}
        keys = {}
        for path in tracked:
            core.register_path(keys, path)
        paths = []
        for entry in selected:
            path = entry["path"][len(prefix):]
            core.need(path not in tracked, "private restore collides with tracked path: " + entry["path"])
            for parent in PurePosixPath(path).parents:
                ancestor = tracked.get(str(parent))
                core.need(not ancestor or ancestor["type"] == "directory", "private restore traverses tracked file/symlink: " + entry["path"])
            core.register_path(keys, path)
            paths.append(path)
        require_checkpoint_ignore_rules(source, paths)
    return overlays


def apply_private_overlays(snapshot, target, overlays):
    for entry in overlays:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        core.copy_file_verified(snapshot / "private" / entry["source"], destination, entry, private=True)


def inspect_repo(source, selected, private_paths):
    result = core.check_source_repo(source, selected, private_paths)
    result["github_repository"] = github_origin(selected["origin"])
    result["remote_verification"] = "pending_connector"
    return result


def validate_recorded_repos(repositories):
    core.need(isinstance(repositories, list), "invalid repository inventory")
    selected = []
    for repo in repositories:
        core.fields(repo, BASE_REPO_KEYS | {"source_head", "ignored_files", "github_repository", "remote_verification"})
        candidate = {k: repo[k] for k in BASE_REPO_KEYS}
        candidate["branches"] = []
        for branch in repo["branches"]:
            core.fields(branch, {"name", "remote_ref", "commit"}, {"pull_request"})
            oid(branch["commit"])
            candidate["branches"].append({k: v for k, v in branch.items() if k != "commit"})
        selected.append(candidate)
        core.need(repo["github_repository"] == github_origin(repo["origin"]), "repository provenance mismatch")
        core.need(repo["remote_verification"] == "pending_connector", "invalid remote verification state")
        oid(repo["source_head"])
        checkout = [b for b in repo["branches"] if b["name"] == repo["checkout"]]
        core.need(len(checkout) == 1 and checkout[0]["commit"] == repo["source_head"], "checkpoint HEAD mismatch")
        core.string_list(repo["ignored_files"])
    core.validate_repositories(selected, False)


def export_snapshot(args):
    source, out = core.real_root(args.source), core.fresh_path(args.out)
    core.need(not core.is_within(out, source), "snapshot destination must be outside source")
    plan = core.read_json(Path(args.selection))
    validate_plan(plan)
    files, skipped = core.collect(source, plan["include"], plan["exclude"])
    private, private_skipped = core.collect(source, plan["private_include"], plan["exclude"], private=True)
    private_paths = {f["path"] for f in private}
    repos = [inspect_repo(source, r, private_paths) for r in plan["repositories"]]
    overlay_inventory({"selection": plan, "private_files": private})
    out.mkdir(mode=0o700)
    (out / ".incomplete").write_text("Connector-mode export not complete\n")
    core.copy_entries(source, out / "garage", files)
    (out / "garage/apps").mkdir(mode=0o700)
    core.copy_entries(source, out / "private", private, private=True)
    files2, _ = core.collect(source, plan["include"], plan["exclude"])
    private2, _ = core.collect(source, plan["private_include"], plan["exclude"], private=True)
    core.need(files2 == files and private2 == private, "source changed during export")
    core.need([inspect_repo(source, r, private_paths) for r in plan["repositories"]] == repos, "source repository changed during export")
    files.append({"path": "apps", "type": "directory"})
    manifest = {"version": VERSION, "mode": "source_snapshot", "created_at": core.now(),
                "source": str(source), "files": files, "private_files": private,
                "repositories": repos, "excluded": skipped + private_skipped, "selection": plan}
    data = core.json_bytes(manifest)
    (out / "manifest.json").write_bytes(data)
    (out / "manifest.sha256").write_text(core.sha(data) + "\n")
    verify_snapshot(out, incomplete_ok=True)
    (out / ".incomplete").unlink()
    print("Garage export verified; application remote verification is pending connector retrieval")
    print("Manifest SHA-256: " + core.sha(data))


def verify_snapshot(snapshot, incomplete_ok=False):
    root = core.real_root(snapshot)
    allowed = {"manifest.json", "manifest.sha256", "garage", "private"} | ({".incomplete"} if incomplete_ok else set())
    core.need({p.name for p in root.iterdir()} == allowed, "snapshot root inventory mismatch or incomplete export")
    for name in ("manifest.json", "manifest.sha256"):
        safe_file(root / name)
    raw = (root / "manifest.json").read_bytes()
    core.need(core.sha(raw) == (root / "manifest.sha256").read_text().strip(), "manifest integrity mismatch")
    manifest = core.read_json(root / "manifest.json")
    core.fields(manifest, {"version", "mode", "created_at", "source", "files", "private_files", "repositories", "excluded", "selection"})
    core.need(manifest["version"] == VERSION and manifest["mode"] == "source_snapshot", "not a connector source-snapshot export")
    validate_plan(manifest["selection"])
    validate_recorded_repos(manifest["repositories"])
    core.validate_entries(manifest["files"])
    core.validate_entries(manifest["private_files"], private=True)
    overlay_inventory(manifest)
    core.need(not any(core.path_key(PurePosixPath(e["path"]).parts[0]) == BUNDLE_NAME for e in manifest["files"]), "reserved connector bundle path")
    core.need({"path": "apps", "type": "directory"} in manifest["files"], "empty apps directory missing")
    core.verify_payload(root / "garage", manifest["files"])
    core.verify_payload(root / "private", manifest["private_files"], private=True)
    return manifest


def safe_file(path):
    st = path.lstat()
    core.need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and path.parent.resolve() == path.parent,
              "unsafe metadata file: " + path.name)
    core.need(st.st_size <= MAX_BUNDLE_BYTES, "metadata/bundle exceeds 128 MiB limit")


def object_hash(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def object_map(objects, kind):
    core.need(isinstance(objects, list), "invalid " + kind + " object list")
    result = {}
    for obj in objects:
        core.need(isinstance(obj, dict), "invalid " + kind + " object")
        key = oid(obj.get("sha"))
        core.need(key not in result, "duplicate " + kind + " object")
        result[key] = obj
    return result


def validate_virtual_links(entries):
    indexed = {e["path"]: e for e in entries}
    def resolve(path):
        pending, resolved, expansions = path.split("/"), [], 0
        while pending:
            part = pending.pop(0)
            if part in {"", "."}:
                continue
            if part == "..":
                core.need(resolved, "escaping symlink")
                resolved.pop()
                continue
            candidate = "/".join(resolved + [part])
            entry = indexed.get(candidate)
            core.need(entry is not None, "missing symlink target")
            if entry["type"] == "symlink":
                expansions += 1
                core.need(expansions < 100, "cyclic or excessively deep symlink")
                core.need(not entry["target"].startswith("/"), "absolute symlink target")
                pending = entry["target"].split("/") + pending
            else:
                core.need(not pending or entry["type"] == "directory", "non-directory symlink ancestor")
                resolved.append(part)
        core.need(resolved and "/".join(resolved) in indexed, "missing/root symlink target")
        return "/".join(resolved)
    for entry in entries:
        if entry["type"] == "symlink":
            core.need(entry["target"] and not entry["target"].startswith("/") and "\\" not in entry["target"] and
                      not any(ord(c) < 32 or ord(c) == 127 for c in entry["target"]), "unsafe symlink target")
            resolve(entry["path"])


def validate_source_objects(item, *, entry_limit=MAX_EXPANDED_ENTRIES):
    core.need(type(entry_limit) is int and 0 <= entry_limit <= MAX_EXPANDED_ENTRIES,
              "invalid expanded source entry limit")
    core.fields(item, {"repository", "requested_commit", "retrieved_at", "commit", "trees", "blobs"})
    repository_name(item["repository"])
    requested = oid(item["requested_commit"])
    core.need(isinstance(item["commit"], dict) and item["commit"].get("sha") == requested, "commit metadata does not match requested checkpoint")
    core.need(isinstance(item["commit"].get("tree"), dict), "commit tree metadata missing")
    root_tree = oid(item["commit"]["tree"].get("sha"))
    core.need(isinstance(item["retrieved_at"], str) and item["retrieved_at"], "retrieval timestamp missing")
    trees, blobs = object_map(item["trees"], "tree"), object_map(item["blobs"], "blob")
    decoded = {}
    for key, blob in blobs.items():
        core.fields(blob, {"sha", "encoding", "content", "size"}, {"url", "node_id"})
        core.need(blob["encoding"] == "base64" and isinstance(blob["content"], str), "blob must contain complete base64 data")
        core.need(type(blob["size"]) is int and 0 <= blob["size"] <= MAX_BLOB_BYTES, "blob exceeds 32 MiB limit or has invalid size")
        data = base64.b64decode("".join(blob["content"].split()), validate=True)
        core.need(len(data) == blob["size"], "blob size mismatch")
        core.need(object_hash("blob", data) == key, "blob hash mismatch")
        core.need(not data.startswith(b"version https://git-lfs.github.com/spec/v1\n"), "LFS pointer unsupported")
        core.scan_secret(data, "connector blob " + key)
        decoded[key] = data
    for key, tree in trees.items():
        core.fields(tree, {"sha", "truncated", "tree"}, {"url"})
        core.need(tree["truncated"] is False, "truncated tree cannot establish completeness")
        core.need(isinstance(tree["tree"], list), "invalid tree entries")
        names, wire = set(), []
        for entry in tree["tree"]:
            core.fields(entry, {"path", "mode", "type", "sha"}, {"size", "url"})
            name = core.relpath(entry["path"])
            core.need("/" not in name and name not in names, "tree must be complete non-recursive entries with unique names")
            names.add(name)
            child = oid(entry["sha"])
            mode = entry["mode"]
            core.need((mode == "040000" and entry["type"] == "tree") or
                      (mode in {"100644", "100755", "120000"} and entry["type"] == "blob"),
                      "unsupported tree mode/type (submodules are unsupported)")
            if "size" in entry and mode != "040000":
                core.need(child in decoded, "missing blob object")
                core.need(entry["size"] == len(decoded[child]), "tree/blob size mismatch")
            raw_name = name.encode("utf-8")
            sort_key = raw_name + (b"/" if mode == "040000" else b"")
            wire.append((sort_key, str(int(mode)).encode() + b" " + raw_name + b"\0" + bytes.fromhex(child)))
        content = b"".join(raw for _, raw in sorted(wire))
        core.need(object_hash("tree", content) == key, "tree hash mismatch")
    entries, file_bytes, used_trees, used_blobs = [], {}, set(), set()
    def walk(tree_id, prefix="", depth=0):
        core.need(depth < 100, "excessively deep source tree")
        core.need(tree_id in trees, "missing tree object")
        used_trees.add(tree_id)
        for entry in trees[tree_id]["tree"]:
            # Refuse before allocating another expanded path, entry or byte-map
            # key. A small shared-object DAG can otherwise expand exponentially.
            core.need(len(entries) < entry_limit, "expanded source entry limit exceeded")
            path = prefix + entry["path"]
            mode, child = entry["mode"], entry["sha"]
            if mode == "040000":
                entries.append({"path": path, "type": "directory"})
                walk(child, path + "/", depth + 1)
            else:
                core.need(child in decoded, "missing blob object")
                used_blobs.add(child)
                data = decoded[child]
                if mode == "120000":
                    target = data.decode("utf-8", "strict")
                    entries.append({"path": path, "type": "symlink", "target": target, "sha256": core.sha(data)})
                else:
                    entries.append({"path": path, "type": "file", "size": len(data), "sha256": core.sha(data),
                                    "mode": 0o755 if mode == "100755" else 0o644})
                    file_bytes[path] = data
    walk(root_tree)
    core.need(used_trees == set(trees) and used_blobs == set(blobs), "extra unused source objects")
    core.validate_entries(entries, private=True)
    validate_virtual_links(entries)
    return {"commit": requested, "tree": root_tree, "entries": entries, "bytes": file_bytes, "retrieved_at": item["retrieved_at"]}


def validate_bundle(bundle, manifest):
    core.fields(bundle, {"version", "provider", "snapshots", "references"})
    core.need(bundle["version"] == 1 and bundle["provider"] == "github_connector", "unsupported source bundle")
    core.need(isinstance(bundle["snapshots"], list) and isinstance(bundle["references"], list), "invalid source bundle inventories")
    expected = {(r["github_repository"], b["commit"]) for r in manifest["repositories"] for b in r["branches"]}
    expected_refs = {(r["github_repository"], b["remote_ref"]) for r in manifest["repositories"] for b in r["branches"]}
    sources = {}
    remaining_entries = MAX_EXPANDED_ENTRIES
    for item in bundle["snapshots"]:
        core.need(isinstance(item, dict), "invalid checkpoint entry")
        key = (item.get("repository"), item.get("requested_commit"))
        core.need(key in expected and key not in sources, "checkpoint inventory mismatch")
        sources[key] = validate_source_objects(item, entry_limit=remaining_entries)
        remaining_entries -= len(sources[key]["entries"])
    core.need(set(sources) == expected, "checkpoint inventory missing requested commits")
    refs = {}
    for ref in bundle["references"]:
        core.fields(ref, {"repository", "ref", "observed_commit", "observed_at"})
        key = (ref["repository"], ref["ref"])
        core.need(key in expected_refs and key not in refs, "ref observation inventory mismatch")
        oid(ref["observed_commit"])
        core.need(isinstance(ref["observed_at"], str) and ref["observed_at"], "ref observation timestamp missing")
        refs[key] = ref
    core.need(set(refs) == expected_refs, "ref observation inventory incomplete")
    return sources, refs


def read_bundle(path, manifest):
    safe_file(path)
    raw = path.read_bytes()
    bundle = core.read_json(path)
    # Refuse mutation between preserving bytes and parsing the document.
    core.need(path.read_bytes() == raw, "source bundle changed while reading")
    sources, refs = validate_bundle(bundle, manifest)
    return raw, sources, refs


def project_receipts(manifest, sources, refs):
    result = []
    for repo in manifest["repositories"]:
        name = repo["github_repository"]
        source = sources[(name, repo["source_head"])]
        checkpoints = [{"branch": b["name"], "ref": b["remote_ref"], "commit": b["commit"],
                        "tree": sources[(name, b["commit"])]["tree"],
                        "retrieved_at": sources[(name, b["commit"])]["retrieved_at"],
                        "observed_ref": refs[(name, b["remote_ref"])]} for b in repo["branches"]]
        result.append({"path": repo["path"], "repository": name, "checkout_branch": repo["checkout"],
                       "checkpoint_commit": repo["source_head"], "root_tree": source["tree"],
                       "checkpoints": checkpoints})
    return result


def materialize_source(target, source):
    target.mkdir(mode=0o700)
    for entry in sorted(source["entries"], key=lambda e: (e["type"] == "symlink", len(PurePosixPath(e["path"]).parts), e["path"])):
        path = target / entry["path"]
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        core.need(path.parent.resolve() == path.parent, "unsafe destination ancestor")
        if entry["type"] == "directory":
            path.mkdir(mode=0o700, exist_ok=True)
        elif entry["type"] == "symlink":
            path.symlink_to(entry["target"])
        else:
            with path.open("xb") as output:
                output.write(source["bytes"][entry["path"]])
            path.chmod(entry["mode"])


def verify_target(snapshot, target, manifest, raw, sources, refs, receipt):
    stored_bundle = target / BUNDLE_NAME
    safe_file(stored_bundle)
    core.need(core.sha(stored_bundle.read_bytes()) == core.sha(raw), "stored source bundle integrity mismatch")
    core.fields(receipt, {"version", "mode", "verified_at", "manifest_sha256", "source_bundle_sha256", "projects"}, {"private_overlay"})
    core.need(receipt["version"] == VERSION and receipt["mode"] == "source_snapshot", "invalid source snapshot receipt")
    core.need(receipt["manifest_sha256"] == core.sha((snapshot / "manifest.json").read_bytes()) and
              receipt["source_bundle_sha256"] == core.sha(raw), "receipt integrity mismatch")
    core.need(receipt["projects"] == project_receipts(manifest, sources, refs), "receipt project provenance mismatch")
    overlay_record = receipt.get("private_overlay", {"applied": False, "files": []})
    core.fields(overlay_record, {"applied", "files"})
    core.need(type(overlay_record["applied"]) is bool, "invalid private overlay receipt")
    overlays = prepare_overlays(manifest, sources) if overlay_record["applied"] else []
    core.need(overlay_record["files"] == overlays, "private overlay receipt inventory mismatch")
    expected = {entry["path"] for entry in manifest["files"]} | {BUNDLE_NAME, ".garage-private"}
    expected.update(entry["path"] for entry in overlays)
    expected.update(".garage-private/" + entry["path"] for entry in manifest["private_files"])
    for repo in manifest["repositories"]:
        expected.add(repo["path"])
        expected.update(repo["path"] + "/" + entry["path"]
                        for entry in sources[(repo["github_repository"], repo["source_head"])]["entries"])
    for name in (".garage-recovery.json", ".incomplete"):
        if os.path.lexists(target / name):
            expected.add(name)
    for path in list(expected):
        expected.update(str(p) for p in PurePosixPath(path).parents if str(p) != ".")
    core.need(core.actual_paths(target) == expected, "source workspace inventory mismatch")
    core.verify_payload(target, manifest["files"], exact=False)
    core.verify_payload(target / ".garage-private", manifest["private_files"], private=True)
    core.need({p.name for p in (target / "apps").iterdir()} == {PurePosixPath(r["path"]).name for r in manifest["repositories"]}, "application inventory mismatch")
    for repo in manifest["repositories"]:
        path = target / repo["path"]
        core.verify_payload(path, sources[(repo["github_repository"], repo["source_head"])]["entries"],
                            exact=not bool(overlays), private=True)
    core.verify_payload(target, [{k: v for k, v in entry.items() if k != "source"} for entry in overlays], exact=False, private=True)


def bootstrap(args):
    snapshot = core.real_root(args.snapshot)
    manifest = verify_snapshot(snapshot)
    target = core.fresh_path(args.target)
    core.need(not core.is_within(target, snapshot), "target must be outside snapshot")
    raw, sources, refs = read_bundle(Path(os.path.abspath(args.sources)), manifest)
    restore_private = getattr(args, "restore_private", False)
    core.need(not restore_private or manifest["selection"].get("private_restore"), "no private restore mappings selected")
    overlays = prepare_overlays(manifest, sources) if restore_private else []
    target.mkdir(mode=0o700)
    (target / ".incomplete").write_text("Source snapshot materialization not complete\n")
    core.copy_entries(snapshot / "garage", target, manifest["files"])
    core.copy_entries(snapshot / "private", target / ".garage-private", manifest["private_files"], private=True)
    for repo in manifest["repositories"]:
        materialize_source(target / repo["path"], sources[(repo["github_repository"], repo["source_head"])])
        for branch in repo["branches"]:
            if refs[(repo["github_repository"], branch["remote_ref"])]["observed_commit"] != branch["commit"]:
                print("Observed remote ref moved; retained exact checkpoint: " + repo["path"] + ":" + branch["name"])
    apply_private_overlays(snapshot, target, overlays)
    (target / BUNDLE_NAME).write_bytes(raw)
    receipt = {"version": VERSION, "mode": "source_snapshot", "verified_at": core.now(),
               "manifest_sha256": core.sha((snapshot / "manifest.json").read_bytes()),
               "source_bundle_sha256": core.sha(raw), "projects": project_receipts(manifest, sources, refs),
               "private_overlay": {"applied": restore_private, "files": overlays}}
    verify_target(snapshot, target, manifest, raw, sources, refs, receipt)
    (target / ".garage-recovery.json").write_bytes(core.json_bytes(receipt))
    (target / ".incomplete").unlink()
    print("Verified source snapshot materialized: " + str(target))
    print("Files only: no .git, local commits, worktrees, or Git history were created")
    if restore_private:
        print("Explicit private input files restored and verified: " + str(len(overlays)))


def requests(manifest):
    commits, refs = {}, {}
    for repo in manifest["repositories"]:
        name = repo["github_repository"]
        for branch in repo["branches"]:
            commit = branch["commit"]
            commits[(name, commit)] = {"repository": name, "requested_commit": commit,
                                      "commit_url": "https://api.github.com/repos/" + name + "/git/commits/" + commit}
            ref = branch["remote_ref"]
            refs[(name, ref)] = {"repository": name, "ref": ref,
                               "ref_url": "https://api.github.com/repos/" + name + "/git/ref/" + quote(ref[len("refs/"):], safe="/")}
    return {"snapshots": list(commits.values()), "references": list(refs.values())}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Copy garage and record local checkpoint requests; no network")
    export.add_argument("--source", required=True)
    export.add_argument("--selection", required=True)
    export.add_argument("--out", required=True)
    request = sub.add_parser("requests", help="Print exact connector metadata request URLs")
    request.add_argument("--snapshot", required=True)
    restore = sub.add_parser("bootstrap", help="Materialize connector source snapshots, not Git history")
    restore.add_argument("--snapshot", required=True)
    restore.add_argument("--sources", required=True)
    restore.add_argument("--target", required=True)
    restore.add_argument("--restore-private", action="store_true", help="Apply explicit private_restore mappings into ignored app paths")
    verify = sub.add_parser("verify", help="Verify garage export and optional files-only workspace")
    verify.add_argument("--snapshot", required=True)
    verify.add_argument("--target")
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            export_snapshot(args)
        elif args.command == "bootstrap":
            bootstrap(args)
        else:
            snapshot = core.real_root(args.snapshot)
            manifest = verify_snapshot(snapshot)
            if args.command == "requests":
                print(json.dumps(requests(manifest), indent=2))
            else:
                if args.target:
                    target = core.real_root(args.target)
                    core.need(not os.path.lexists(target / ".incomplete"), "target is incomplete")
                    raw, sources, refs = read_bundle(target / BUNDLE_NAME, manifest)
                    receipt_path = target / ".garage-recovery.json"
                    safe_file(receipt_path)
                    verify_target(snapshot, target, manifest, raw, sources, refs, core.read_json(receipt_path))
                print("Integrity verified; mode is source_snapshot (files only)")
        return 0
    except (core.Refusal, OSError, ValueError, UnicodeError, KeyError, TypeError, RecursionError) as error:
        print("Refused: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
