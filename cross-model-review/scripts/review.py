#!/usr/bin/env python3
"""Build a complete packet and retain one advisory native review exchange.

Standard library only; macOS/Linux. See ../references/runner.md.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
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
    pass


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


def capture(root, base, exclusions, limit):
    specs = pathspec(exclusions)
    if git(root, "ls-files", "--unmerged", "-z", *specs):
        raise ReviewError("Unmerged index has multiple staged versions; resolve or explicitly exclude those paths")
    head = decode(git(root, "rev-parse", "HEAD")).strip()
    branch = decode(git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False) or b"(detached)").strip()
    sections = [("Git status", decode(git(root, "status", "--porcelain", "--untracked-files=all", *specs))),
                ("Committed history", decode(git(root, "log", "--oneline", "--no-color",
                    "--no-decorate", base + "..HEAD", *(specs if exclusions else []))))]
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


@contextmanager
def locked(directory):
    if directory.is_symlink():
        raise ReviewError("Review directory must not be a symlink")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(directory / ".review.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
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
    if not isinstance(state, dict) or state.get("version") != 1 or not isinstance(state.get("exchanges"), list):
        raise ReviewError("Unsupported or damaged review history")
    if len(state["exchanges"]) > MAX_EXCHANGES or any(not isinstance(state.get(k), str)
            for k in ("repo", "git_common_dir", "base", "brief_sha256")):
        raise ReviewError("Damaged task identity or exchange allowance")
    for i, entry in enumerate(state["exchanges"], 1):
        if (not isinstance(entry, dict) or entry.get("round") != i
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


def reconcile(args, directory, state):
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
    else:
        write_new(note_path, note)
    entry.update(reconciled_from=entry["status"], status="reconciled", hashes=hashes,
                 reconciliation=name, reconciliation_sha256=digest(note.encode()), reconciled_at=now())
    atomic_json(directory / "review-state.json", state)
    return result


def run(args):
    directory = Path(args.review_dir).absolute()
    with locked(directory):
        directory = directory.resolve()
        state = load_state(directory)
        if args.reconcile_round is not None:
            return reconcile(args, directory, state)
        for name in ("repo", "brief", "checks", "authorization", "tool", "author_model"):
            if not getattr(args, name):
                raise ReviewError(f"--{name.replace('_', '-')} is required")
        if state and any(e["status"] in UNCERTAIN for e in state["exchanges"]):
            raise ReviewError("Prior execution is uncertain; stop its possible processes and use --reconcile-round with evidence")
        used = len(state["exchanges"]) if state else 0
        if used >= MAX_EXCHANGES:
            raise ReviewError("Three-exchange allowance exhausted; return findings to the coordinator or verifier")
        model = args.model or DEFAULT_MODELS[args.tool]
        for value in (model, args.author_model):
            if not value.strip() or value.lower() in {"unknown", "auto", "default", "latest", "opus", "sonnet", "haiku"}:
                raise ReviewError("Supply resolved model identities; aliases or unknown identity cannot establish independence")
        if model.strip().casefold() == args.author_model.strip().casefold():
            raise ReviewError("Reviewer and implementer must be separate models")
        supplied_root = Path(args.repo).resolve()
        root = Path(decode(git(supplied_root, "rev-parse", "--show-toplevel")).strip()).resolve()
        if supplied_root != root:
            raise ReviewError("--repo must name the repository/worktree root")
        common = decode(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")).strip()
        exclusions = exclude_paths(args.exclude)
        if directory.is_relative_to(root):
            relative = directory.relative_to(root).as_posix()
            if git(root, "ls-files", "-z", "--", ":(top,literal)" + relative):
                raise ReviewError("Review artifacts must not overlap tracked files")
            if not excluded(relative, exclusions):
                names = {".review.lock", "review-state.json", ".review-state-probe"}
                for round_number in range(1, MAX_EXCHANGES + 1):
                    names.update(artifact_names(round_number).values())
                    names.add(f"review-reconciliation-{round_number}.md")
                paths = [relative + "/", *[relative + "/" + name for name in sorted(names)]]
                ignored = git(root, "check-ignore", "-z", "--stdin", check=False,
                              input=b"\0".join(path.encode() for path in paths) + b"\0") or b""
                if not {path.encode() for path in paths} <= set(ignored.split(b"\0")):
                    raise ReviewError("The review directory and every artifact must be Git-ignored or explicitly --exclude'd")
        inputs = {}
        for name in ("brief", "checks", "authorization"):
            file = Path(getattr(args, name)).resolve()
            text = read_text(file, args.max_packet_bytes)
            if not text.strip():
                raise ReviewError(f"Empty {name} input")
            inputs[name] = (str(file), text)
        if state and (state["repo"] != str(root) or state["git_common_dir"] != common
                      or state["brief_sha256"] != digest(inputs["brief"][1].encode())):
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
        change = capture(root, base, exclusions, args.max_packet_bytes)
        prompt = read_text(REFERENCES / "reviewer-instructions.md") + "\n\n"
        prompt += read_text(REFERENCES / "results.md") + "\n\n"
        for name in ("brief", "authorization"):
            prompt += block(name.title() + " — " + inputs[name][0], inputs[name][1])
        prompt += block("Review scope", f"Repository: {root}\nAuthor model: {args.author_model}\nReviewer: {args.tool} / {model}\nEffort: {args.effort}\nExclusions (literal paths and subtrees): {json.dumps(exclusions)}\nDo not inspect excluded paths or unrelated private material.")
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
        if state is None:
            state = {"version": 1, "repo": str(root), "git_common_dir": common, "base": base,
                     "brief_sha256": digest(inputs["brief"][1].encode()), "exchanges": []}
        entry = {"round": n, "status": "starting", "tool": args.tool, "model": model,
                 "effort": args.effort, "author_model": args.author_model, "files": files,
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
                "allowance_used": n, "model": model, "effort": args.effort, "error": error,
                **{key: str(directory / value) for key, value in files.items()}}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "brief", "checks", "authorization", "author-model", "model", "base", "dispositions"):
        p.add_argument("--" + name)
    p.add_argument("--tool", choices=sorted(DEFAULT_MODELS))
    p.add_argument("--effort", default=DEFAULT_EFFORT)
    p.add_argument("--review-dir", required=True)
    p.add_argument("--exclude", action="append", default=[], help="Literal repository-relative path/subtree; repeatable")
    p.add_argument("--timeout", type=float, default=1800)
    p.add_argument("--max-packet-bytes", type=int, default=LIMIT)
    p.add_argument("--reconcile-round", type=int)
    p.add_argument("--reconciliation", help="Evidence that all possible prior reviewer processes stopped")
    return p


def main():
    args = parser().parse_args()
    try:
        if not math.isfinite(args.timeout) or args.timeout <= 0 or args.max_packet_bytes <= 0:
            raise ReviewError("Timeout and packet size must be positive")
        result = run(args)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["execution"] in {"completed", "reconciled"} else 1
    except (ReviewError, AdapterError, OSError, ValueError, subprocess.SubprocessError) as exc:
        reserved = getattr(args, "reserved_round", None)
        print(json.dumps({"execution": "unknown" if reserved else "not_run", "error": str(exc),
                          "round": reserved, "review_dir": str(Path(args.review_dir).absolute())}, ensure_ascii=False))
        return 1 if reserved else 2


if __name__ == "__main__":
    sys.exit(main())
