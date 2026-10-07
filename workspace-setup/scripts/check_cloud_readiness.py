#!/usr/bin/env python3
"""Read-only cloud prerequisites; no acquisition, setup, registration or tests."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import types


MAX_JSON = 1024 * 1024
MAX_ITEMS = 128
SHA256 = r"[0-9a-f]{64}"
OID = r"[0-9a-f]{40}"
ID = r"[a-z][a-z0-9-]{0,63}"
DEPENDENCY_MANIFEST = Path(__file__).resolve().parents[1] / "references/recovery-dependency.json"
DEFAULT_DEPENDENCY = Path(__file__).resolve().parent / "recovery"


class Refusal(Exception):
    def __init__(self, state, code):
        self.state, self.code = state, code


def require(condition, state="malformed", code="invalid_schema"):
    if not condition:
        raise Refusal(state, code)


def fields(value, names):
    require(type(value) is dict and set(value) == set(names))


def pattern(value, expression):
    require(type(value) is str and re.fullmatch(expression, value) is not None)


def sequence(value, *, nonempty=False):
    require(type(value) is list and (not nonempty or value) and len(value) <= MAX_ITEMS)
    return value


def unique(items, key=lambda item: item):
    values = [key(item) for item in items]
    require(len(values) == len(set(values)))


def relative(value):
    require(type(value) is str and 0 < len(value) <= 1024 and "\\" not in value
            and not any(ord(c) < 32 or ord(c) == 127 for c in value))
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and path.parts
            and all(p not in {".", ".."} for p in path.parts))
    return value


def text(value):
    require(type(value) is str and 0 < len(value) <= 4096 and "\0" not in value)


def file_spec(value):
    fields(value, {"path", "sha256"})
    relative(value["path"])
    pattern(value["sha256"], SHA256)


def file_specs(value):
    for item in sequence(value):
        file_spec(item)
    unique(value, lambda item: item["path"])


def ids(value):
    for item in sequence(value):
        pattern(item, ID)
    unique(value)


def safe_path(path, kind="file"):
    """Refuse symlink components before opening; no writes or path resolution escapes."""
    path = Path(os.path.abspath(path))
    for parent in reversed(path.parents):
        st = parent.lstat()
        require(stat.S_ISDIR(st.st_mode), "unsafe", "unsafe_path")
    st = path.lstat()
    if kind == "directory":
        require(stat.S_ISDIR(st.st_mode), "unsafe", "expected_directory")
    else:
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, "unsafe", "expected_regular_file")
    return path


def read_bytes(path, limit=MAX_JSON):
    path = safe_path(path)
    before = path.stat()
    require(before.st_size <= limit, "malformed", "size_limit")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(limit + 1)
        after_open = os.fstat(stream.fileno())
    after = path.lstat()
    keys = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    require(len(data) <= limit and all(getattr(before, k) == getattr(opened, k) == getattr(after_open, k)
                                     == getattr(after, k) for k in keys), "mismatch", "input_changed")
    return data


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: require(False))


def dependency(directory):
    """Load only the exact two reviewed byte strings, never ambient modules or pyc."""
    manifest = parse_json(read_bytes(DEPENDENCY_MANIFEST))
    fields(manifest, {"version", "release", "modules"})
    require(manifest["version"] == 1 and type(manifest["version"]) is int)
    fields(manifest["modules"], {"garage_rebuild.py", "garage_workspace.py"})
    root = safe_path(directory, "directory")
    sources = {}
    for name, expected in manifest["modules"].items():
        pattern(expected, SHA256)
        sources[name] = read_bytes(root / name)
        require(sha(sources[name]) == expected, "mismatch", "dependency_hash")
    # Both modules are verified BEFORE either executes. Explicit module objects
    # prevent a preexisting garage_rebuild import or local pyc from substituting.
    core = types.ModuleType("garage_rebuild")
    source = types.ModuleType("garage_workspace")
    core.__file__, source.__file__ = str(root / "garage_rebuild.py"), str(root / "garage_workspace.py")
    previous = sys.modules.get("garage_rebuild")
    try:
        exec(compile(sources["garage_rebuild.py"], core.__file__, "exec"), core.__dict__)
        sys.modules["garage_rebuild"] = core
        exec(compile(sources["garage_workspace.py"], source.__file__, "exec"), source.__dict__)
    finally:
        if previous is None:
            sys.modules.pop("garage_rebuild", None)
        else:
            sys.modules["garage_rebuild"] = previous
    return core, source


def validate_requirements(value, profile):
    fields(value, {"skills", "tools", "inputs", "git", "files", "report_parents"})
    for name in ("skills", "tools", "inputs"):
        ids(value[name])
        declared = set(profile[name] if name == "inputs" else (item["id"] for item in profile[name]))
        require(set(value[name]) <= declared)
    file_specs(value["files"])
    for parent in sequence(value["report_parents"]):
        relative(parent)
    unique(value["report_parents"])
    apps = {item["id"] for item in profile["applications"]}
    for item in sequence(value["git"]):
        fields(item, {"app", "head", "commits", "complete_history"})
        require(item["app"] in apps and type(item["head"]) is bool and type(item["complete_history"]) is bool)
        for commit in sequence(item["commits"]):
            pattern(commit, OID)
        unique(item["commits"])
    unique(value["git"], lambda item: item["app"])


def validate_profile(profile):
    fields(profile, {"version", "id", "governance", "applications", "skills", "tools", "inputs",
                     "private_manifest", "recipes", "development", "groups"})
    require(type(profile["version"]) is int and profile["version"] == 1)
    pattern(profile["id"], ID)
    sequence(profile["governance"], nonempty=True)
    file_specs(profile["governance"])
    require(any(item["path"] == "AGENTS.md" for item in profile["governance"]))
    for app in sequence(profile["applications"], nonempty=True):
        fields(app, {"id", "path", "repository", "ref", "commit", "tree", "bundle"})
        pattern(app["id"], ID)
        relative(app["path"])
        pattern(app["repository"], r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
        require(all(p not in {".", ".."} for p in app["repository"].split("/")))
        pattern(app["ref"], r"refs/(heads/[A-Za-z0-9_./-]+|pull/[1-9][0-9]*/head)")
        require(".." not in app["ref"] and "//" not in app["ref"] and not app["ref"].endswith(("/", ".", ".lock")))
        require(all(not part.startswith(".") and not part.endswith(".lock") for part in app["ref"].split("/")))
        pattern(app["commit"], OID)
        pattern(app["tree"], OID)
        file_spec(app["bundle"])
    unique(profile["applications"], lambda item: item["id"])
    paths = [item["path"] for item in profile["applications"]]
    require(all(not (a == b or a.startswith(b + "/") or b.startswith(a + "/"))
                for i, a in enumerate(paths) for b in paths[i + 1:]))
    for skill in sequence(profile["skills"]):
        fields(skill, {"id", "sha256", "resources"})
        pattern(skill["id"], ID)
        pattern(skill["sha256"], SHA256)
        file_specs(skill["resources"])
        require({"path": "SKILL.md", "sha256": skill["sha256"]} in skill["resources"])
    for tool in sequence(profile["tools"]):
        fields(tool, {"id", "version"})
        pattern(tool["id"], ID)
        text(tool["version"])
    ids(profile["inputs"])
    private = profile["private_manifest"]
    require(not profile["inputs"] or private is not None)
    if private is not None:
        fields(private, {"path", "sha256", "sha256_file"})
        relative(private["path"])
        relative(private["sha256_file"])
        pattern(private["sha256"], SHA256)
        require(private["path"] != private["sha256_file"])
    for recipe in sequence(profile["recipes"], nonempty=True):
        fields(recipe, {"id", "path", "sha256", "commands"})
        pattern(recipe["id"], ID)
        file_spec({k: recipe[k] for k in ("path", "sha256")})
        for command in sequence(recipe["commands"], nonempty=True):
            text(command)
    for name in ("skills", "tools", "recipes"):
        unique(profile[name], lambda item: item["id"])
    validate_requirements(profile["development"], profile)
    recipes = {item["id"] for item in profile["recipes"]}
    for group in sequence(profile["groups"], nonempty=True):
        fields(group, {"id", "optional", "recipe", "requires"})
        pattern(group["id"], ID)
        require(type(group["optional"]) is bool and group["recipe"] in recipes)
        validate_requirements(group["requires"], profile)
    unique(profile["groups"], lambda item: item["id"])
    requirement_sets = [profile["development"], *(group["requires"] for group in profile["groups"])]
    check_count = len(profile["governance"]) + len(profile["applications"]) + 1 + 3 * len(profile["groups"])
    check_count += sum(len(items) for requirements in requirement_sets for items in requirements.values())
    require(check_count <= 1024, "malformed", "profile_check_limit")


def timestamp(value):
    pattern(value, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def host_observations(path, root, profile_hash, context):
    require(path is not None, "missing", "host_observation_missing")
    data = parse_json(read_bytes(path))
    fields(data, {"version", "profile_sha256", "workspace", "context", "observed_at", "expires_at", "skills", "tools"})
    require(type(data["version"]) is int and data["version"] == 1)
    pattern(data["profile_sha256"], SHA256)
    pattern(data["context"], ID)
    text(data["workspace"])
    require(data["workspace"] == str(root) and data["profile_sha256"] == profile_hash
            and data["context"] == context, "mismatch", "host_binding")
    observed, expires = timestamp(data["observed_at"]), timestamp(data["expires_at"])
    now = datetime.now(timezone.utc)
    require(observed <= now, "malformed", "future_observation")
    require(expires > now, "stale", "host_observation_expired")
    require(0 < (expires - observed).total_seconds() <= 3600, "malformed", "host_observation_window")
    for skill in sequence(data["skills"]):
        fields(skill, {"id", "registered", "sha256", "resources"})
        pattern(skill["id"], ID)
        pattern(skill["sha256"], SHA256)
        require(type(skill["registered"]) is bool)
        for resource in sequence(skill["resources"]):
            fields(resource, {"path", "sha256", "readable"})
            file_spec({k: resource[k] for k in ("path", "sha256")})
            require(type(resource["readable"]) is bool)
        unique(skill["resources"], lambda item: item["path"])
    for tool in sequence(data["tools"]):
        fields(tool, {"id", "version", "available"})
        pattern(tool["id"], ID)
        text(tool["version"])
        require(type(tool["available"]) is bool)
    for name in ("skills", "tools"):
        unique(data[name], lambda item: item["id"])
    return data


def public_error(error):
    # Never forward a dependency error, filename, schema key, Git stderr or data.
    if isinstance(error, Refusal):
        return {"state": error.state, "code": error.code}
    if isinstance(error, FileNotFoundError):
        return {"state": "missing", "code": "required_path_missing"}
    if isinstance(error, PermissionError):
        return {"state": "unavailable", "code": "read_access_denied"}
    if isinstance(error, (NotADirectoryError, IsADirectoryError)):
        return {"state": "unsafe", "code": "path_type"}
    if isinstance(error, (OSError, subprocess.SubprocessError)):
        return {"state": "unavailable", "code": "inspection_unavailable"}
    # The pinned dependency uses Refusal with private details. Only classify it.
    if error.__class__.__name__ == "Refusal":
        mismatch = any(word in str(error) for word in ("mismatch", "changed", "missing blob", "missing tree"))
        return {"state": "mismatch" if mismatch else "malformed", "code": "recovery_validation_failed"}
    return {"state": "malformed", "code": "invalid_evidence"}


def check(kind, action):
    try:
        return {"kind": kind, "state": "verified", **(action() or {})}
    except Exception as error:
        return {"kind": kind, **public_error(error)}


def section(checks):
    states = {item["state"] for item in checks}
    status = "blocked" if states - {"verified", "observed", "unverified"} else (
        "unverified" if "unverified" in states else "ready")
    return {"status": status, "checks": checks}


class Readiness:
    def __init__(self, root, profile, core, source, host):
        self.root, self.profile, self.core, self.source, self.host = root, profile, core, source, host
        self.apps = {item["id"]: item for item in profile["applications"]}
        self.private = None

    def file(self, spec):
        path = safe_path(self.root / spec["path"])
        actual = self.core.stream_file(path, private=True)
        require(actual["sha256"] == spec["sha256"], "mismatch", "file_hash")

    def source_checks(self):
        checks = [check("governance", lambda spec=spec: self.file(spec)) for spec in self.profile["governance"]]
        for app in self.profile["applications"]:
            checks.append(check("application:" + app["id"], lambda app=app: self.application(app)))
        return section(checks)

    def application(self, app):
        raw = read_bytes(self.root / app["bundle"]["path"], self.source.MAX_BUNDLE_BYTES)
        require(sha(raw) == app["bundle"]["sha256"], "mismatch", "bundle_hash")
        bundle = parse_json(raw)
        selected = [a for a in self.profile["applications"] if a["bundle"] == app["bundle"]]
        manifest = {"repositories": [{"github_repository": a["repository"], "branches": [
            {"commit": a["commit"], "remote_ref": a["ref"]}]} for a in selected]}
        sources, refs = self.source.validate_bundle(bundle, manifest)
        source = sources[(app["repository"], app["commit"])]
        require(source["tree"] == app["tree"], "mismatch", "root_tree")
        root = safe_path(self.root / app["path"], "directory")
        for entry in source["entries"]:
            require(entry["type"] != "symlink", "unavailable", "source_symlinks_unsupported")
            safe_path(root / entry["path"], "directory" if entry["type"] == "directory" else "file")
        # Verify the complete selected tree's files, not unrelated private inputs,
        # build outputs or .git. This is not a clean-working-tree claim.
        self.core.verify_payload(root, source["entries"], exact=False, private=True)
        return {"scope": "selected_tree_bytes", "ref_moved": refs[(app["repository"], app["ref"])]["observed_commit"] != app["commit"],
                "identity_trust": "supplied_connector_metadata"}

    def observed(self, category, identifier):
        if isinstance(self.host, Exception):
            raise self.host
        requirement = next(item for item in self.profile[category] if item["id"] == identifier)
        observation = next((item for item in self.host[category] if item["id"] == identifier), None)
        require(observation is not None, "missing", "host_item_missing")
        if category == "tools":
            require(observation["available"], "unavailable", "tool_unavailable")
            require(observation["version"] == requirement["version"], "mismatch", "tool_version")
        else:
            require(observation["registered"], "unavailable", "skill_not_registered")
            require(observation["sha256"] == requirement["sha256"], "mismatch", "skill_identity")
            resources = {item["path"]: item for item in observation["resources"]}
            for item in requirement["resources"]:
                observed = resources.get(item["path"])
                require(observed is not None, "missing", "skill_resource_missing")
                require(observed["readable"], "unavailable", "skill_resource_unreadable")
                require(observed["sha256"] == item["sha256"], "mismatch", "skill_resource_identity")
        return {"state": "observed", "trust": "supplied_host_observation"}

    def private_input(self, identifier):
        if self.private is None:
            try:
                spec = self.profile["private_manifest"]
                require(spec is not None, "missing", "private_manifest_missing")
                raw = read_bytes(self.root / spec["path"])
                companion = read_bytes(self.root / spec["sha256_file"], 65).decode().strip()
                pattern(companion, SHA256)
                require(sha(raw) == spec["sha256"] == companion, "mismatch", "private_manifest_hash")
                data = parse_json(raw)
                fields(data, {"version", "profile_id", "inputs"})
                require(type(data["version"]) is int and data["version"] == 1)
                require(data["profile_id"] == self.profile["id"], "mismatch", "private_profile_binding")
                for item in sequence(data["inputs"]):
                    fields(item, {"id", "path", "sha256", "size"})
                    pattern(item["id"], ID)
                    file_spec({k: item[k] for k in ("path", "sha256")})
                    require(type(item["size"]) is int and 0 <= item["size"] <= self.core.MAX_PRIVATE_FILE_BYTES)
                    require(not self.core.secret_name(item["path"]), "unsafe", "credential_path_refused")
                unique(data["inputs"], lambda item: item["id"])
                self.private = {item["id"]: item for item in data["inputs"]}
            except Exception as error:
                self.private = error
        if isinstance(self.private, Exception):
            raise self.private
        require(identifier in self.private, "missing", "private_input_not_recorded")
        item = self.private[identifier]
        observed = self.core.stream_file(safe_path(self.root / item["path"]), private=True)
        require(observed["sha256"] == item["sha256"] and observed["size"] == item["size"], "mismatch", "private_input_hash")

    def report_parent(self, relative_path):
        path = safe_path(self.root / relative_path, "directory")
        return {"state": "unverified", "code": "future_report_write_unproven", "directory_exists": True,
                "access_observation": os.access(path, os.W_OK | os.X_OK), "write_probe": "not_performed"}

    def git(self, requirement):
        app = self.apps[requirement["app"]]
        root = safe_path(self.root / app["path"], "directory")
        require((root / ".git").exists(), "unavailable", "git_history_absent")
        metadata = safe_path(root / ".git", "directory")
        # V1 supports ordinary local repositories only. Never follow alternates,
        # linked worktrees, replacement objects, promisor files or metadata links.
        count = 0
        for parent, directories, files in os.walk(metadata, followlinks=False):
            for name in directories + files:
                count += 1
                require(count <= 100000, "unavailable", "git_inventory_limit")
                path = Path(parent) / name
                safe_path(path, "directory" if name in directories else "file")
                rel = path.relative_to(metadata).as_posix()
                require(rel not in {"objects/info/alternates", "objects/info/http-alternates", "info/grafts", "commondir", "refs/replace"}
                        and not rel.endswith(".promisor"), "unavailable", "unsupported_git_storage")
        executable = shutil.which("git", path=os.defpath)
        require(executable is not None, "unavailable", "git_unavailable")
        env = {"PATH": os.defpath, "HOME": os.devnull, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GIT_NO_LAZY_FETCH": "1",
               "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_ATTR_NOSYSTEM": "1",
               "GIT_CONFIG_SYSTEM": os.devnull, "GIT_ALLOW_PROTOCOL": ""}

        def run(args):
            result = subprocess.run([executable, "--no-pager", *args], cwd="/", env=env,
                                    stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=False)
            require(result.returncode == 0, "unavailable", "git_object_unavailable")
            require(len(result.stdout) <= 8 * MAX_JSON, "unavailable", "git_output_limit")
            return result.stdout.decode("utf-8", "strict").strip()

        config = safe_path(metadata / "config")
        config_output = run(["config", "--file", str(config), "--no-includes", "--null", "--list"])
        for entry in config_output.split("\0"):
            if not entry:
                continue
            key = entry.partition("\n")[0].lower()
            require(re.fullmatch(r"core\.(repositoryformatversion|filemode|bare|logallrefupdates|ignorecase|precomposeunicode)"
                                 r"|user\.(name|email)|remote\..+\.(url|fetch)|branch\..+\.(remote|merge)", key),
                    "unavailable", "unsupported_git_configuration")
        prefix = ["--git-dir=" + str(metadata), "--work-tree=" + str(root), "--no-replace-objects",
                  "-c", "core.hooksPath=" + os.devnull, "-c", "core.fsmonitor=false", "-c", "credential.helper=",
                  "-c", "protocol.allow=never", "-c", "gc.auto=0", "-c", "maintenance.auto=false"]
        if requirement["head"] or requirement["complete_history"]:
            require(run(prefix + ["rev-parse", "--verify", "HEAD"]) == app["commit"], "mismatch", "git_head")
        for commit in requirement["commits"] + [app["commit"]]:
            require(run(prefix + ["cat-file", "-t", commit]) == "commit", "mismatch", "git_object_type")
        require(run(prefix + ["rev-parse", "--verify", app["commit"] + "^{tree}"]) == app["tree"],
                "mismatch", "git_commit_tree")
        if requirement["complete_history"]:
            require(not (metadata / "shallow").exists(), "unavailable", "shallow_history")
            objects = run(prefix + ["rev-list", "--objects", "--missing=print", app["commit"]])
            require(not any(line.startswith("?") for line in objects.splitlines()), "unavailable", "incomplete_history")

    def prerequisites(self, requirements):
        checks = []
        for category in ("skills", "tools"):
            for identifier in requirements[category]:
                checks.append(check(category + ":" + identifier, lambda c=category, i=identifier: self.observed(c, i)))
        for item in requirements["git"]:
            checks.append(check("git:" + item["app"], lambda item=item: self.git(item)))
        for spec in requirements["files"]:
            checks.append(check("control_file", lambda spec=spec: self.file(spec)))
        for parent in requirements["report_parents"]:
            checks.append(check("report_parent", lambda parent=parent: self.report_parent(parent)))
        for identifier in requirements["inputs"]:
            checks.append(check("input:" + identifier, lambda i=identifier: self.private_input(i)))
        return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, help="Absolute selected garage containing workspace-setup.json and AGENTS.md")
    parser.add_argument("--dependency-dir", default=str(DEFAULT_DEPENDENCY),
                        help="Alternate exact-pinned release; defaults to the skill's bundled recovery directory")
    parser.add_argument("--context", required=True, help="Current host/session observation context identifier")
    parser.add_argument("--host-observations", help="Explicit local host observation JSON; absent is not verified")
    args = parser.parse_args(argv)
    report = {"version": 1, "mode": "read_only", "tests": "not_run", "acceptance": "not_assessed",
              "host_trust": "supplied_observations_not_independently_authenticated"}
    try:
        require(Path(args.workspace).is_absolute(), "malformed", "workspace_must_be_absolute")
        pattern(args.context, ID)
        root = safe_path(args.workspace, "directory")
        core, source = dependency(args.dependency_dir)
        raw = read_bytes(root / "workspace-setup.json")
        core.scan_secret(raw, "profile")
        profile = parse_json(raw)
        validate_profile(profile)
        report["profile_sha256"] = sha(raw)
        try:
            host = host_observations(args.host_observations, root, sha(raw), args.context)
        except Exception as error:
            host = error
        readiness = Readiness(root, profile, core, source, host)
        report["source"] = readiness.source_checks()
        source_gate = {"kind": "source", "state": "verified" if report["source"]["status"] == "ready" else "unavailable"}
        report["development"] = section([source_gate, *readiness.prerequisites(profile["development"])])
        dev_gate = {"kind": "development", "state": "verified" if report["development"]["status"] == "ready" else "unavailable"}
        recipes = {item["id"]: item for item in profile["recipes"]}
        report["groups"] = {}
        for group in profile["groups"]:
            result = section([source_gate, dev_gate,
                              check("recipe", lambda g=group: readiness.file(recipes[g["recipe"]])),
                              *readiness.prerequisites(group["requires"])])
            report["groups"][group["id"]] = {"optional": group["optional"], **result}
        report["limitations"] = ["Selected source bytes only; no clean-working-tree or authenticated-provider claim",
                                 "Host and toolchain checks consume fresh supplied observations",
                                 "No acquisition, setup, registration, tests, report writes or acceptance performed"]
        ready = report["development"]["status"] == "ready" and all(
            g["optional"] or g["status"] == "ready" for g in report["groups"].values())
        code = 0 if ready else 1
    except Exception as error:
        report["error"] = public_error(error)
        code = 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
