#!/usr/bin/env python3
"""Build a complete packet and retain one advisory native review exchange.

Standard library only; macOS/Linux. See ../references/runner.md.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import signal
import stat
import subprocess
import sys
import tempfile

# Importing this helper must not add bytecode to a reviewed or installed skill.
sys.dont_write_bytecode = True
from adapters import AdapterError, DEFAULT_EFFORT, DEFAULT_MODELS, build, environment


MAX_EXCHANGES = 3
LIMIT = 2 * 1024 * 1024
REFERENCES = Path(__file__).resolve().parent.parent / "references"
UNCERTAIN = {"starting", "running", "timeout", "cancelled", "unknown"}


class ReviewError(ValueError):
    def __init__(self, message, **details):
        super().__init__(message)
        self.details = details


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_text(path, limit=LIMIT):
    if not path.is_file():
        raise ReviewError(f"Not a readable file: {path}")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ReviewError(f"Input exceeds {limit} bytes; split the task: {path}")
    if b"\0" in data:
        raise ReviewError(f"Binary input cannot be represented completely: {path}")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewError(f"Input is not UTF-8 text: {path}") from exc


def git(root, *args, check=True, input=None):
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                            env=environment(), input=input, capture_output=True, timeout=30)
    if check and result.returncode:
        raise ReviewError("Git inspection failed: " + " ".join(args[:3]) + "\n"
                          + result.stderr.decode("utf-8", "replace"))
    return result.stdout if result.returncode == 0 else None


def decode(data):
    if b"\0" in data:
        raise ReviewError("Captured text contains NUL bytes; use an explicit exclusion or another review method")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewError("Git output is not UTF-8; packet would be incomplete") from exc


def exclude_paths(values):
    result = []
    for value in values:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] == ".git":
            raise ReviewError(f"Exclusions must be repository-relative files/directories: {value!r}")
        result.append(str(path))
    return sorted(set(result))


def excluded(path, exclusions):
    return any(path == x or path.startswith(x + "/") for x in exclusions)


def pathspec(exclusions):
    return ["--", ".", *[":(top,literal,exclude)" + x for x in exclusions]]


def block(title, content):
    # A fence longer than any input fence keeps arbitrary source text intact.
    fence = "`" * max(3, 1 + max((len(m[0]) for m in re.finditer(r"`+", content)), default=0))
    return f"## {title}\n\n{fence}\n{content}\n{fence}\n\n"


def committed_history(root, base, head, exclusions):
    if not exclusions:
        return decode(git(root, "log", "--oneline", "--no-color", "--no-decorate", base + ".." + head))
    # Path-limited git log simplifies away empty commits and merge topology.
    # Walk the full graph, then omit only history confined to excluded paths.
    # An explicit format alone does not suppress configured signature display.
    records = git(root, "log", "--no-show-signature", "--topo-order", "--format=%H %P%x00%h %s", "-z",
                  "--no-color", "--no-decorate", base + ".." + head).split(b"\0")
    commits = list(zip(records[::2], records[1::2]))
    visible = set()
    for identity, _ in reversed(commits):
        commit, *parents = identity.decode("ascii").split()
        comparison = (parents[0], commit) if parents else (commit,)
        diff = ("diff-tree", "--root", "--no-commit-id", "--name-only", "-r",
                "--no-renames", "--no-ext-diff", "--no-textconv", *comparison)
        changed = git(root, *diff)
        included = bool(git(root, *diff, *pathspec(exclusions))) if changed else not parents[1:]
        if len(parents) > 1 and not included:
            # Comparing every parent would expose a private-only merge merely
            # because its first parent already contained a public change.
            introduced = set(git(root, "rev-list", *parents[1:], "--not", parents[0], base).splitlines())
            included = bool(introduced & visible) or (not changed and not introduced)
        if included:
            visible.add(commit.encode("ascii"))
    lines = [summary for identity, summary in commits if identity.split(b" ", 1)[0] in visible]
    return decode(b"\n".join(lines) + (b"\n" if lines else b""))


def capture(root, base, exclusions, limit):
    specs = pathspec(exclusions)
    if git(root, "ls-files", "--unmerged", "-z", *specs):
        raise ReviewError("Unmerged index has multiple staged versions; resolve or explicitly exclude those paths")
    flags = git(root, "ls-files", "-v", "-z", *specs).split(b"\0")
    if any(record[:1] == b"S" or record[:1].islower() for record in flags if record):
        raise ReviewError("Tracked paths marked assume-unchanged or skip-worktree cannot be captured completely; "
                          "clear those flags yourself or explicitly exclude those paths")
    head = decode(git(root, "rev-parse", "HEAD")).strip()
    branch = decode(git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False) or b"(detached)").strip()
    sections = [("Git status", decode(git(root, "status", "--porcelain", "--untracked-files=all", *specs))),
                ("Committed history", committed_history(root, base, head, exclusions))]
    for title, args in (("Committed change against base", (base, "HEAD")),
                        ("Staged change against HEAD", ("--cached", "HEAD")),
                        ("Working tree against index", ())):
        raw = git(root, "diff", "--raw", "-z", "--no-renames", "--ignore-submodules=none", "--no-ext-diff", "--no-textconv", *args, *specs)
        nums = git(root, "diff", "--numstat", "-z", "--no-renames", "--ignore-submodules=none", "--no-ext-diff", "--no-textconv", *args, *specs)
        binary = any(record.split(b"\t", 2)[:2] == [b"-", b"-"] for record in nums.split(b"\0") if record)
        submodule = any(re.match(rb":(?:160000 \d+|\d+ 160000) ", record)
                        for record in raw.split(b"\0")[::2] if record)
        if binary or submodule:
            raise ReviewError("Binary or submodule changes need an explicit exclusion or a separate review")
        data = git(root, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--no-renames",
                   "--ignore-submodules=none", *args, *specs)
        if len(data) > limit:
            raise ReviewError("Complete diff exceeds packet budget; split the task")
        sections.append((title, decode(data)))
    names = git(root, "ls-files", "--others", "--exclude-standard", "-z", *specs).split(b"\0")
    for name in sorted(n for n in names if n):
        relative = decode(name)
        file = root / relative
        mode = file.lstat().st_mode
        if stat.S_ISLNK(mode):
            content = "Symbolic link target (not followed): " + os.readlink(file)
        elif stat.S_ISREG(mode):
            content = read_text(file, limit)
        else:
            raise ReviewError(f"Cannot capture special file: {relative!r}")
        sections.append(("New untracked file " + json.dumps(relative, ensure_ascii=False), content))
    result = f"HEAD: {head}\nBranch: {branch}\nBase commit: {base}\n\n"
    result += "".join(block(title, content) for title, content in sections)
    if len(result.encode()) > limit:
        raise ReviewError("Complete change exceeds packet budget; split the task")
    return result


def atomic_json(path, value):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".review-state-", delete=False) as stream:
        temp = Path(stream.name)
        try:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def continuation_names(n):
    return {"decision": f"review-continuation-{n}.json", "brief": f"review-brief-{n}.md"}


def decision(data):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ReviewError(f"Duplicate continuation field: {key}")
            result[key] = value
        return result

    value = json.loads(decode(data), object_pairs_hook=unique_keys)
    fields = {"version", "after_round", "history_sha256", "allowance", "brief_sha256",
              "owner", "authorization_source", "basis", "rationale"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ReviewError("Continuation must contain exactly the documented decision fields")
    if (type(value["version"]) is not int or value["version"] != 1
            or type(value["after_round"]) is not int or value["after_round"] < 0
            or type(value["allowance"]) is not int or not 1 <= value["allowance"] <= MAX_EXCHANGES):
        raise ReviewError("Continuation requires version 1, a nonnegative round and an allowance of 1–3")
    for key in ("history_sha256", "brief_sha256"):
        if not isinstance(value[key], str) or not re.fullmatch(r"[0-9a-f]{64}", value[key]):
            raise ReviewError(f"Invalid continuation {key}")
    for key in ("owner", "authorization_source", "rationale"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise ReviewError(f"Continuation requires nonempty {key}")
    if value["basis"] not in ("new_authorized_work", "distinct_finding", "changed_approach", "repaired_prerequisite"):
        raise ReviewError("Unrecognized continuation basis")
    return value


def allowance_limit(directory, state):
    records = state.get("continuations", [])
    if not records:
        return MAX_EXCHANGES
    last = decision((directory / records[-1]["files"]["decision"]).read_bytes())
    return last["after_round"] + last["allowance"]


def active_brief(state):
    records = state.get("continuations", [])
    return records[-1]["hashes"]["brief"] if records else state["brief_sha256"]


def allowance_info(directory, state):
    used = len(state["exchanges"])
    limit = allowance_limit(directory, state)
    return {"allowance_used": used, "allowance_limit": limit, "allowance_remaining": limit - used,
            "reassessment_required": used == limit,
            "history_sha256": digest((directory / "review-state.json").read_bytes())}


@contextmanager
def locked(directory, *, create=True):
    if directory.is_symlink():
        raise ReviewError("Review directory must not be a symlink")
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(directory / ".review.lock", os.O_RDWR | os.O_NOFOLLOW | (os.O_CREAT if create else 0), 0o600)
    # Keep the lock inode after release: unlinking it can let another caller
    # acquire a different inode while an existing opener still owns this one.
    with os.fdopen(fd, "r+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReviewError("Another review call owns this directory") from exc
        yield


def load_state(directory):
    path = directory / "review-state.json"
    if path.is_symlink():
        raise ReviewError("Review state must not be a symlink")
    if not path.exists():
        if any(directory.glob("review-*")):
            raise ReviewError("Existing artifacts have no runner history; reconcile the legacy history, do not reset its allowance")
        return None
    state = json.loads(read_text(path))
    if (not isinstance(state, dict) or type(state.get("version")) is not int
            or state["version"] not in (1, 2) or not isinstance(state.get("exchanges"), list)):
        raise ReviewError("Unsupported or damaged review history")
    if any(not isinstance(state.get(k), str)
            for k in ("repo", "git_common_dir", "base", "brief_sha256")):
        raise ReviewError("Damaged task identity or exchange allowance")
    if state["version"] == 1:
        if len(state["exchanges"]) > MAX_EXCHANGES or "continuations" in state:
            raise ReviewError("Damaged version 1 exchange allowance")
    elif not isinstance(state.get("continuations"), list):
        raise ReviewError("Missing continuation history")
    for i, entry in enumerate(state["exchanges"], 1):
        if (not isinstance(entry, dict) or type(entry.get("round")) is not int or entry["round"] != i
                or not isinstance(entry.get("status"), str) or entry.get("status") not in UNCERTAIN | {
                "completed", "failed", "invalid_output", "reconciled"}):
            raise ReviewError("Damaged exchange history; reconcile before another invocation")
        if entry.get("files") != artifact_names(i):
            raise ReviewError("Invalid artifact names in review history")
        if entry.get("pid") is not None and (type(entry["pid"]) is not int or entry["pid"] <= 0):
            raise ReviewError("Invalid process identity in review history")
        hashes = entry.get("hashes", {})
        if not isinstance(hashes, dict) or not set(hashes) <= set(entry["files"]):
            raise ReviewError("Invalid evidence hashes in review history")
        if entry["status"] in {"completed", "failed", "invalid_output", "reconciled"} and set(hashes) != set(entry["files"]):
            raise ReviewError("Terminal exchange has incomplete evidence")
        for kind, expected in entry.get("hashes", {}).items():
            file = directory / entry["files"][kind]
            if expected is None and entry["status"] == "reconciled":
                if file.exists() or file.is_symlink():
                    raise ReviewError(f"Previously absent evidence appeared: {file}")
                continue
            if not file.is_file() or file.is_symlink() or digest(file.read_bytes()) != expected:
                raise ReviewError(f"Retained evidence changed: {file}")
        if "reconciliation_sha256" in entry:
            note_name = f"review-reconciliation-{i}.md"
            note = directory / note_name
            if (entry.get("reconciliation") != note_name or not note.is_file() or note.is_symlink()
                    or digest(note.read_bytes()) != entry["reconciliation_sha256"]):
                raise ReviewError("Retained reconciliation evidence changed")
    boundary, previous_round = MAX_EXCHANGES, 0
    for i, entry in enumerate(state.get("continuations", []), 1):
        names = continuation_names(i)
        if (not isinstance(entry, dict) or entry.get("files") != names
                or not isinstance(entry.get("hashes"), dict) or set(entry["hashes"]) != set(names)
                or not isinstance(entry.get("recorded_at"), str) or not entry["recorded_at"].strip()):
            raise ReviewError("Damaged continuation record")
        content = {}
        for kind, filename in names.items():
            file = directory / filename
            if not file.is_file() or file.is_symlink():
                raise ReviewError(f"Missing or nonregular continuation evidence: {file}")
            content[kind] = read_text(file).encode("utf-8")
            if digest(content[kind]) != entry["hashes"][kind]:
                raise ReviewError(f"Retained continuation evidence changed: {file}")
        recorded = decision(content["decision"])
        if not content["brief"].decode("utf-8").strip() or recorded["brief_sha256"] != digest(content["brief"]):
            raise ReviewError("Continuation brief identity differs")
        after = recorded["after_round"]
        if not previous_round <= after <= min(boundary, len(state["exchanges"])):
            raise ReviewError("Continuation round is outside its preceding allowance or retained history")
        boundary, previous_round = after + recorded["allowance"], after
    if len(state["exchanges"]) > boundary:
        raise ReviewError("Retained attempts exceed the recorded allowance")
    return state


def outcome(data):
    text = decode(data).strip()
    lines = text.splitlines()
    if not lines:
        raise ReviewError("Reviewer returned no report")
    match = re.fullmatch(r"Outcome: (SUGGESTIONS|NO_FURTHER_SUGGESTIONS|BLOCKED)", lines[0].strip())
    if not match or len(re.findall(r"^Outcome:", text, re.M)) != 1:
        raise ReviewError("Reviewer report has no single valid outcome line")
    headings = list(re.finditer(r"^(Summary|Observations|Tests run|Unknowns):[ \t]*", text, re.M))
    if [h[1] for h in headings] != ["Summary", "Observations", "Tests run", "Unknowns"]:
        raise ReviewError("Reviewer report is missing or repeats required fields")
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        if not text[heading.end():end].strip():
            raise ReviewError(f"Reviewer report has an empty {heading[1]}")
    return match[1]


def artifact_names(n):
    return {"packet": "review-packet.md" if n == 1 else f"review-packet-{n}.md",
            "command": f"review-command-{n}.txt", "report": f"review-round-{n}.md",
            "stderr": f"review-round-{n}.stderr.log", "stdout": f"review-round-{n}.stdout.log"}


def terminate(process):
    # Each reviewer is a new process session. Never signal other sessions.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)


def reconcile(args, directory, state, *, save=True):
    if not state or not args.reconciliation:
        raise ReviewError("Reconciliation requires existing history and --reconciliation FILE")
    note = read_text(Path(args.reconciliation).resolve())
    if not note.strip():
        raise ReviewError("Reconciliation must describe how all possible reviewer processes were stopped")
    entries = [e for e in state["exchanges"] if e["round"] == args.reconcile_round]
    if not entries:
        raise ReviewError("That round is not in the retained history")
    entry = entries[0]
    name = f"review-reconciliation-{entry['round']}.md"
    note_path = directory / name
    result = {"execution": "reconciled", "round": entry["round"], "allowance_used": len(state["exchanges"]),
              "evidence": str(note_path)}
    if entry["status"] == "reconciled":
        if note_path.is_symlink() or not note_path.is_file() or note_path.read_bytes() != note.encode():
            raise ReviewError("Round is already reconciled with different evidence")
        return result
    if entry["status"] not in UNCERTAIN:
        raise ReviewError("That round does not have uncertain execution")
    if entry.get("pid"):
        try:
            os.killpg(entry["pid"], 0)
        except ProcessLookupError:
            pass
        else:
            raise ReviewError("Recorded reviewer process group still exists; stop it before reconciling")
    hashes = {}
    for kind, filename in entry["files"].items():
        file = directory / filename
        if file.is_symlink() or (file.exists() and not file.is_file()):
            raise ReviewError(f"Reconciliation requires regular artifact files: {file}")
        hashes[kind] = digest(file.read_bytes()) if file.exists() else None
    if note_path.exists() or note_path.is_symlink():
        # A prior attempt may have saved the note before the journal update failed.
        if note_path.is_symlink() or not note_path.is_file() or note_path.read_bytes() != note.encode():
            raise ReviewError("An existing reconciliation note differs; refusing to overwrite it")
    if not save:
        return result
    if not note_path.exists():
        write_new(note_path, note)
    entry.update(reconciled_from=entry["status"], status="reconciled", hashes=hashes,
                 reconciliation=name, reconciliation_sha256=digest(note.encode()), reconciled_at=now())
    atomic_json(directory / "review-state.json", state)
    return result


def repository(path):
    supplied = Path(path).resolve()
    root = Path(decode(git(supplied, "rev-parse", "--show-toplevel")).strip()).resolve()
    if supplied != root:
        raise ReviewError("--repo must name the repository/worktree root")
    common = decode(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).strip()
    return root, common


def check_output(directory, root, exclusions, boundary, continuation_count):
    if not directory.is_relative_to(root):
        return
    relative = directory.relative_to(root).as_posix()
    if git(root, "ls-files", "-z", "--", ":(top,literal)" + relative):
        raise ReviewError("Review artifacts must not overlap tracked files")
    if excluded(relative, exclusions):
        return
    names = {".review.lock", "review-state.json", ".review-state-probe"}
    for n in range(1, boundary + 1):
        names.update(artifact_names(n).values())
        names.add(f"review-reconciliation-{n}.md")
    for n in range(1, continuation_count + 1):
        names.update(continuation_names(n).values())
    paths = [relative + "/", *[relative + "/" + name for name in sorted(names)]]
    ignored = git(root, "check-ignore", "-z", "--stdin", check=False,
                  input=b"\0".join(path.encode() for path in paths) + b"\0") or b""
    if not {path.encode() for path in paths} <= set(ignored.split(b"\0")):
        raise ReviewError("The review directory and every artifact must be Git-ignored or explicitly --exclude'd")


def continue_review(args, directory, state, *, save=True):
    if not state:
        raise ReviewError("Continuation requires existing valid runner history")
    if any(e["status"] in UNCERTAIN for e in state["exchanges"]):
        raise ReviewError("Prior execution is uncertain; reconcile it before continuation or replay")
    if not args.repo or not args.brief:
        raise ReviewError("Continuation requires --repo and --brief")
    root, common = repository(args.repo)
    if state["repo"] != str(root) or state["git_common_dir"] != common:
        raise ReviewError("Repository differs from the retained review history")
    if args.base:
        base = decode(git(root, "rev-parse", "--verify", "--end-of-options", args.base + "^{commit}")).strip()
        if base != state["base"]:
            raise ReviewError("Base differs from the retained review history")
    raw = read_text(Path(args.continue_with).resolve()).encode("utf-8")
    requested = decision(raw)
    brief = read_text(Path(args.brief).resolve()).encode("utf-8")
    if not brief.decode("utf-8").strip() or digest(brief) != requested["brief_sha256"]:
        raise ReviewError("Supplied brief differs from the continuation decision")
    exclusions = exclude_paths(args.exclude)
    records = state.get("continuations", [])
    boundary = allowance_limit(directory, state)
    for n, entry in enumerate(records, 1):
        if (directory / entry["files"]["decision"]).read_bytes() == raw:
            if (directory / entry["files"]["brief"]).read_bytes() != brief:
                raise ReviewError("Replay brief differs from the retained snapshot")
            check_output(directory, root, exclusions, boundary, len(records))
            return {"execution": "continuation_recorded", "continuation": n, "replayed": True,
                    **{k: str(directory / v) for k, v in entry["files"].items()},
                    **allowance_info(directory, state)}
    if (requested["after_round"] != len(state["exchanges"])
            or requested["history_sha256"] != digest((directory / "review-state.json").read_bytes())):
        raise ReviewError("Continuation round or history token is stale; reassess the exact current history")
    n = len(records) + 1
    names = continuation_names(n)
    new_boundary = requested["after_round"] + requested["allowance"]
    check_output(directory, root, exclusions, max(boundary, new_boundary), n)
    known = {name for entry in records for name in entry["files"].values()}
    found = {p.name for pattern in ("review-continuation-*", "review-brief-*") for p in directory.glob(pattern)}
    if found - known - set(names.values()):
        raise ReviewError("Unexpected unrecorded continuation evidence; preserve and reconcile it with its owner")
    content = {"decision": raw, "brief": brief}
    present = [(directory / filename).exists() or (directory / filename).is_symlink() for filename in names.values()]
    if any(present):
        if not all(present):
            raise ReviewError("Partial unrecorded continuation evidence; refusing to overwrite or complete it")
        for kind, filename in names.items():
            file = directory / filename
            if file.is_symlink() or not file.is_file() or file.read_bytes() != content[kind]:
                raise ReviewError("Unrecorded continuation evidence differs; refusing to overwrite it")
    if not save:
        return None
    if not any(present):
        for kind, filename in names.items():
            write_new(directory / filename, content[kind])
    updated = {**state, "version": 2, "continuations": [*records, {
        "files": names, "hashes": {k: digest(v) for k, v in content.items()}, "recorded_at": now()}]}
    atomic_json(directory / "review-state.json", updated)
    return {"execution": "continuation_recorded", "continuation": n, "replayed": False,
            **{k: str(directory / v) for k, v in names.items()}, **allowance_info(directory, updated)}


def run(args):
    if args.continue_with is not None:
        forbidden = ("checks", "authorization", "author_model", "model", "tool", "effort", "dispositions",
                     "timeout", "max_packet_bytes", "reconcile_round", "reconciliation")
        if any(getattr(args, name) is not None for name in forbidden):
            raise ReviewError("--continue-with is metadata-only; do not combine it with review or reconciliation inputs")
    else:
        if args.effort is None:
            args.effort = DEFAULT_EFFORT
        if args.timeout is None:
            args.timeout = 1800
        if args.max_packet_bytes is None:
            args.max_packet_bytes = LIMIT
    directory = Path(args.review_dir).absolute()
    with ExitStack() as locks:
        if directory.is_symlink():
            raise ReviewError("Review directory must not be a symlink")
        directory = directory.resolve()
        if directory.exists() and not directory.is_dir():
            raise ReviewError("Review directory must be a directory")
        lock = directory / ".review.lock"
        acquired = lock.exists() or lock.is_symlink()
        if acquired:
            # Read existing history under its persistent lock, without creating
            # any output while arguments and locations are still unvalidated.
            locks.enter_context(locked(directory, create=False))
        state = load_state(directory)
        if args.continue_with is not None:
            continue_review(args, directory, state, save=False)
            if not acquired:
                locks.enter_context(locked(directory))
            if load_state(directory) != state:
                raise ReviewError("Review history changed during continuation preflight; reassess the current history")
            return continue_review(args, directory, state)
        if args.reconcile_round is not None:
            reconcile(args, directory, state, save=False)
            if not acquired:
                locks.enter_context(locked(directory))
            result = reconcile(args, directory, load_state(directory))
            return {**result, **allowance_info(directory, load_state(directory))}
        for name in ("repo", "brief", "checks", "authorization", "tool", "author_model"):
            if not getattr(args, name):
                raise ReviewError(f"--{name.replace('_', '-')} is required")
        if state and any(e["status"] in UNCERTAIN for e in state["exchanges"]):
            raise ReviewError("Prior execution is uncertain; stop its possible processes and use --reconcile-round with evidence")
        used = len(state["exchanges"]) if state else 0
        boundary = allowance_limit(directory, state) if state else MAX_EXCHANGES
        if used >= boundary:
            raise ReviewError("Review allowance exhausted; coordinator or authorized owner reassessment is required",
                              **allowance_info(directory, state))
        model = (args.model if args.model is not None else DEFAULT_MODELS[args.tool]).strip()
        author_model = args.author_model.strip()
        for value in (model, author_model):
            if not value or value.casefold() in {"unknown", "auto", "default", "latest", "opus", "sonnet", "haiku"}:
                raise ReviewError("Supply resolved model identities; aliases or unknown identity cannot establish independence")
        if model.casefold() == author_model.casefold():
            raise ReviewError("Reviewer and implementer must be separate models")
        root, common = repository(args.repo)
        exclusions = exclude_paths(args.exclude)
        check_output(directory, root, exclusions, boundary, len(state.get("continuations", [])) if state else 0)
        inputs = {}
        for name in ("brief", "checks", "authorization"):
            file = Path(getattr(args, name)).resolve()
            text = read_text(file, args.max_packet_bytes)
            if not text.strip():
                raise ReviewError(f"Empty {name} input")
            inputs[name] = (str(file), text)
        if state and (state["repo"] != str(root) or state["git_common_dir"] != common
                      or active_brief(state) != digest(inputs["brief"][1].encode())):
            raise ReviewError("Repository or brief differs from this task's history; reconcile scope with its owner")
        if args.base:
            base = decode(git(root, "rev-parse", "--verify", "--end-of-options", args.base + "^{commit}")).strip()
        elif state:
            base = state["base"]
        else:
            base = decode(git(root, "merge-base", "HEAD", "origin/main", check=False)
                          or git(root, "merge-base", "HEAD", "main")).strip()
        if state and state["base"] != base:
            raise ReviewError("Base differs from the retained review history")
        prior = ""
        if used:
            if not args.dispositions:
                raise ReviewError("Subsequent exchanges require --dispositions FILE, including treatment of failed attempts")
            dispositions = read_text(Path(args.dispositions).resolve(), args.max_packet_bytes)
            if not dispositions.strip():
                raise ReviewError("Disposition input must explain prior findings or failed attempts")
            prior += block("Implementer dispositions", dispositions)
            for e in state["exchanges"]:
                prior_scope = {k: e.get(k) for k in ("status", "outcome", "tool", "model", "effort", "author_model", "error")}
                prior_scope["exclusions"] = e.get("exclusions", "Not indexed by the earlier runner; consult the original packet")
                prior_scope["original_packet"] = str(directory / e["files"]["packet"])
                prior += block(f"Prior exchange {e['round']} execution and scope", json.dumps(prior_scope, indent=2))
                report = directory / e["files"]["report"]
                if report.exists():
                    data = report.read_bytes()
                    if len(data) > args.max_packet_bytes:
                        raise ReviewError("Prior raw report exceeds the packet budget; no evidence was truncated")
                    try:
                        original = data.decode("utf-8")
                        if "\0" in original:
                            raise UnicodeError
                        prior += block(f"Original reviewer report {e['round']}", original)
                    except UnicodeError:
                        prior += block(f"Invalid original output {e['round']} — complete bytes in base64",
                                       base64.b64encode(data).decode("ascii"))
        if state and state.get("continuations"):
            initial_packet = directory / artifact_names(1)["packet"]
            prior += block("Initial brief provenance", f"SHA-256: {state['brief_sha256']}\n"
                           f"Original packet: {initial_packet}\n"
                           f"Packet present: {initial_packet.is_file()}\n"
                           "Initial brief text is not embedded here; the original packet may be unavailable "
                           "under the reviewer's access restrictions. Do not invent missing requirements.")
            prior_boundary = MAX_EXCHANGES
            records = state["continuations"]
            for i, record in enumerate(records, 1):
                raw = read_text(directory / record["files"]["decision"])
                recorded = decision(raw.encode())
                after = recorded["after_round"]
                prior += block(f"Continuation {i} — retained caller claims, not authenticated authority", raw)
                prior += block(f"Continuation {i} allowance replacement",
                               f"After cumulative round: {after}\nUnused slots retired: {prior_boundary - after}\n"
                               f"New boundary: {after + recorded['allowance']}")
                label = "Current" if i == len(records) else "Historical"
                prior += block(f"{label} brief snapshot from continuation {i}",
                               read_text(directory / record["files"]["brief"]))
                prior_boundary = after + recorded["allowance"]
        change = capture(root, base, exclusions, args.max_packet_bytes)
        prompt = read_text(REFERENCES / "reviewer-instructions.md") + "\n\n"
        prompt += read_text(REFERENCES / "results.md") + "\n\n"
        for name in ("brief", "authorization"):
            prompt += block(name.title() + " — " + inputs[name][0], inputs[name][1])
        prompt += block("Review scope", f"Repository: {root}\nAuthor model: {author_model}\nReviewer: {args.tool} / {model}\nEffort: {args.effort}\nExclusions (literal paths and subtrees): {json.dumps(exclusions)}\nDo not inspect excluded paths or unrelated private material.")
        prompt += change + block("Implementer's check evidence — " + inputs["checks"][0], inputs["checks"][1]) + prior
        encoded = prompt.encode("utf-8")
        if len(encoded) > args.max_packet_bytes:
            raise ReviewError("Complete packet exceeds --max-packet-bytes; split the task or explicitly raise the limit")
        n = used + 1
        files = artifact_names(n)
        if any((directory / file).exists() or (directory / file).is_symlink() for file in files.values()):
            raise ReviewError("Round artifacts already exist; refusing to overwrite evidence")
        env = environment()
        argv = build(args.tool, model, args.effort, root, directory / files["packet"], directory / files["report"], env)
        # A configuration probe must not race a changing index/worktree.
        if capture(root, base, exclusions, args.max_packet_bytes) != change:
            raise ReviewError("Repository changed while assembling the packet; capture again after writers stop")
        if not acquired:
            locks.enter_context(locked(directory))
        if load_state(directory) != state:
            raise ReviewError("Review history changed during preflight; retry with the current history and dispositions")
        if state is None:
            state = {"version": 2, "repo": str(root), "git_common_dir": common, "base": base,
                     "brief_sha256": digest(inputs["brief"][1].encode()), "exchanges": [], "continuations": []}
        entry = {"round": n, "status": "starting", "tool": args.tool, "model": model,
                 "effort": args.effort, "author_model": author_model, "files": files,
                 "exclusions": exclusions,
                 "started_at": now(), "argv": argv, "pid": None, "outcome": None}
        state["exchanges"].append(entry)
        args.reserved_round = n
        atomic_json(directory / "review-state.json", state)
        write_new(directory / files["packet"], encoded)
        command = shlex.join(argv)
        if args.tool != "muse":
            command += " < " + shlex.quote(str(directory / files["packet"]))
        command += " > " + shlex.quote(str(directory / files["stdout"])) + " 2> " + shlex.quote(str(directory / files["stderr"])) + "\n"
        write_new(directory / files["command"], command)
        process = None
        status, error, returncode = "failed", None, None
        old_term = signal.getsignal(signal.SIGTERM)
        def interrupted(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, interrupted)
        try:
            with (directory / files["packet"]).open("rb") as stdin, \
                    (directory / files["stdout"]).open("xb") as stdout, \
                    (directory / files["stderr"]).open("xb") as stderr:
                process = subprocess.Popen(argv, cwd=root, env=env, stdin=stdin,
                                           stdout=stdout, stderr=stderr, start_new_session=True)
                entry.update(status="running", pid=process.pid)
                atomic_json(directory / "review-state.json", state)
                returncode = process.wait(timeout=args.timeout)
            status = "completed" if returncode == 0 else "failed"
            if returncode:
                error = f"Native reviewer exited {returncode}"
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                pass
            else:
                terminate(process)
                status, error = "unknown", "Reviewer children outlived the native process; reconcile before another exchange"
        except subprocess.TimeoutExpired:
            status, error = "timeout", "Native reviewer exceeded timeout; reconcile before another exchange"
        except KeyboardInterrupt:
            status, error = "cancelled", "Invocation interrupted; reconcile before another exchange"
        except OSError as exc:
            status, error = "failed", str(exc)
        finally:
            signal.signal(signal.SIGTERM, old_term)
            if process is not None and process.poll() is None:
                terminate(process)
        report_path = directory / files["report"]
        if args.tool != "codex":
            write_new(report_path, (directory / files["stdout"]).read_bytes())
        elif not report_path.exists():
            write_new(report_path, b"")
        if status == "completed":
            try:
                entry["outcome"] = outcome(report_path.read_bytes())
            except ReviewError as exc:
                status, error = "invalid_output", str(exc)
        entry.update(status=status, error=error, returncode=returncode, finished_at=now())
        entry["hashes"] = {kind: digest((directory / name).read_bytes()) for kind, name in files.items()}
        atomic_json(directory / "review-state.json", state)
        return {"execution": status, "outcome": entry["outcome"], "round": n,
                "model": model, "effort": args.effort, "error": error,
                **{key: str(directory / value) for key, value in files.items()}, **allowance_info(directory, state)}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "brief", "checks", "authorization", "author-model", "model", "base", "dispositions"):
        p.add_argument("--" + name)
    p.add_argument("--tool", choices=sorted(DEFAULT_MODELS))
    p.add_argument("--effort", help=f"Reviewer effort (default: {DEFAULT_EFFORT})")
    p.add_argument("--review-dir", required=True)
    p.add_argument("--exclude", action="append", default=[], help="Literal repository-relative path/subtree; repeatable")
    p.add_argument("--timeout", type=float, help="Reviewer timeout in seconds (default: 1800)")
    p.add_argument("--max-packet-bytes", type=int, help=f"Packet size limit (default: {LIMIT})")
    p.add_argument("--continue-with", help="Record a bounded continuation decision JSON without invoking a reviewer")
    p.add_argument("--reconcile-round", type=int)
    p.add_argument("--reconciliation", help="Evidence that all possible prior reviewer processes stopped")
    return p


def main():
    args = parser().parse_args()
    try:
        if ((args.timeout is not None and (not math.isfinite(args.timeout) or args.timeout <= 0))
                or (args.max_packet_bytes is not None and args.max_packet_bytes <= 0)):
            raise ReviewError("Timeout and packet size must be positive")
        result = run(args)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["execution"] in {"completed", "reconciled", "continuation_recorded"} else 1
    except (ReviewError, AdapterError, OSError, ValueError, subprocess.SubprocessError) as exc:
        reserved = getattr(args, "reserved_round", None)
        print(json.dumps({"execution": "unknown" if reserved else "not_run", "error": str(exc),
                          "round": reserved, "review_dir": str(Path(args.review_dir).absolute()),
                          **getattr(exc, "details", {})}, ensure_ascii=False))
        return 1 if reserved else 2


if __name__ == "__main__":
    sys.exit(main())
