#!/usr/bin/env python3
"""Record agent-supplied slice decisions in Markdown; never decide readiness."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys
import tempfile


OPEN = "<!-- implementation-tracker:v1 -->"
CLOSE = "<!-- /implementation-tracker -->"
STATUSES = ("planned", "ready", "assigned", "in_progress", "review", "blocked",
            "done", "deferred", "superseded")
COLUMNS = {"id": "ID", "title": "Title", "status": "Status", "checkpoint": "Checkpoint",
           "type": "Type", "priority": "Priority", "owner": "Owner",
           "dependencies": "Dependencies", "blocker": "Blocker", "evidence": "Evidence",
           "parent": "Parent"}
REQUIRED = ("id", "title", "status", "checkpoint")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


class TrackerError(Exception):
    def __init__(self, code, message, exit_code=2, **details):
        super().__init__(message)
        self.exit_code = exit_code
        self.error = {"code": code, "message": message, **details}


def revision(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def empty_record():
    return {**dict.fromkeys(COLUMNS, ""), "type": "slice", "status": "planned", "dependencies": []}


def field_value(key, value):
    if any(character in value for character in ("\n", "\r", "\x00")):
        raise TrackerError("invalid_field", f"{COLUMNS[key]} must occupy one physical line.")
    value = value.strip()
    if key == "dependencies":
        return [item.strip() for item in value.split(",")] if value else []
    if key == "type":
        return value or "slice"
    return value


def table_cells(line):
    """Split Markdown cells, honoring escaped pipes and backslashes."""
    source = line.strip()
    if not source.startswith("|") or not source.endswith("|"):
        raise TrackerError("invalid_table", "Every table line must start and end with a pipe.")
    cells, current = [], []
    index = 1
    while index < len(source):
        char = source[index]
        if char == "\\" and index + 1 < len(source) and source[index + 1] in "\\|":
            current.append(source[index + 1])
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    if current:
        raise TrackerError("invalid_table", "The final pipe must be an unescaped cell delimiter.")
    return cells


def marker_bounds(lines):
    starts, ends = [], []
    fence = None
    for index, line in enumerate(lines):
        content = line.rstrip("\r\n")
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", content):
                fence = None
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content)
        # Backtick fence info cannot contain backticks; such text can be inline code.
        if opening and (opening[1][0] == "~" or "`" not in opening[2]):
            fence = (opening[1][0], len(opening[1]))
            continue
        if content == OPEN:
            starts.append(index)
        elif content == CLOSE:
            ends.append(index)
        elif re.fullmatch(r"<!-- implementation-tracker:.* -->", content):
            raise TrackerError("unsupported_version", "Only implementation-tracker:v1 is supported.")
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise TrackerError("invalid_markers", "Expected exactly one unfenced v1 tracker marker pair; normalize legacy formats explicitly.")
    return starts[0], ends[0]


def check_acyclic(graph, label):
    """Kahn's algorithm avoids recursion limits for large human-edited trackers."""
    remaining = {item: len(references) for item, references in graph.items()}
    consumers = {item: [] for item in graph}
    for item, references in graph.items():
        for reference in references:
            consumers[reference].append(item)
    available = [item for item, count in remaining.items() if count == 0]
    visited = 0
    while available:
        item = available.pop()
        visited += 1
        for consumer in consumers[item]:
            remaining[consumer] -= 1
            if remaining[consumer] == 0:
                available.append(consumer)
    if visited != len(graph):
        raise TrackerError("reference_cycle", f"{label} contains a cycle.")


def validate_records(records):
    ids = set()
    for row in records:
        item = row["id"]
        if not IDENTIFIER.fullmatch(item):
            raise TrackerError("invalid_id", f"Invalid item ID: {item!r}.")
        if item in ids:
            raise TrackerError("duplicate_id", f"Duplicate item ID: {item}.")
        ids.add(item)
        for key in REQUIRED:
            if not row[key]:
                raise TrackerError("missing_field", f"{item} requires {COLUMNS[key]}.")
        if row["status"] not in STATUSES:
            raise TrackerError("invalid_status", f"{item} has an unsupported recorded status: {row['status']!r}.")
        if row["type"] not in ("slice", "epic"):
            raise TrackerError("invalid_type", f"{item} type must be slice or epic.")
        if row["priority"] not in ("", "P0", "P1", "P2", "P3"):
            raise TrackerError("invalid_priority", f"{item} priority must be empty or P0–P3.")
    for row in records:
        for label, refs in (("Dependencies", row["dependencies"]),
                            ("Parent", [row["parent"]] if row["parent"] else [])):
            if len(refs) != len(set(refs)):
                raise TrackerError("duplicate_reference", f"{row['id']} repeats a {label} reference.")
            for reference in refs:
                if reference not in ids or reference == row["id"]:
                    raise TrackerError("invalid_reference", f"{row['id']} {label} must reference another existing ID: {reference!r}.")
    check_acyclic({row["id"]: row["dependencies"] for row in records}, "Dependencies")
    check_acyclic({row["id"]: [row["parent"]] if row["parent"] else [] for row in records}, "Parent")


def render_line(values, newline):
    escaped = [value.replace("\\", "\\\\").replace("|", "\\|") for value in values]
    return "| " + " | ".join(escaped) + " |" + newline


class Document:
    def __init__(self, data):
        self.data = data
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise TrackerError("invalid_encoding", "The tracker must be UTF-8 Markdown.") from error
        if "\r" in text.replace("\r\n", ""):
            raise TrackerError("invalid_newlines", "Use LF or CRLF line endings.")
        # Markdown rows end at LF/CRLF, not at Unicode separators in cell text.
        parts = text.split("\n")
        self.lines = [part + "\n" for part in parts[:-1]]
        if parts[-1]:
            self.lines.append(parts[-1])
        self.start, self.end = marker_bounds(self.lines)
        table = self.lines[self.start + 1:self.end]
        if len(table) < 2:
            raise TrackerError("invalid_table", "The marker pair must contain a table header and separator.")
        self.newline = "\r\n" if table[0].endswith("\r\n") else "\n"
        labels = table_cells(table[0])
        names = {label: key for key, label in COLUMNS.items()}
        if len(set(labels)) != len(labels) or any(label not in names for label in labels):
            raise TrackerError("invalid_columns", "Column names must be supported and unique.")
        self.columns = [names[label] for label in labels]
        if not set(REQUIRED).issubset(self.columns):
            raise TrackerError("missing_columns", "The table requires ID, Title, Status, and Checkpoint.")
        separators = table_cells(table[1])
        if len(separators) != len(labels) or any(not re.fullmatch(r":?-{3,}:?", value) for value in separators):
            raise TrackerError("invalid_table", "The header separator must match the columns.")
        self.records = []
        self.original_rows = {}
        for line in table[2:]:
            values = table_cells(line)
            if len(values) != len(labels):
                raise TrackerError("invalid_table", "A row has a different number of cells than the header; escape literal pipes.")
            row = empty_record()
            row.update({key: field_value(key, value) for key, value in zip(self.columns, values)})
            self.records.append(row)
            self.original_rows[row["id"]] = (row, line)
        validate_records(self.records)

    def render(self, records):
        if records == self.records:
            return self.data
        columns = self.columns[:]
        defaults = empty_record()
        columns.extend(key for key in COLUMNS if key not in columns and
                       any(row[key] != defaults[key] for row in records))
        if columns == self.columns:
            lines = self.lines[self.start + 1:self.start + 3]
        else:
            lines = [render_line([COLUMNS[key] for key in columns], self.newline),
                     render_line(["---"] * len(columns), self.newline)]
        for row in records:
            old = self.original_rows.get(row["id"])
            if columns == self.columns and old and row == old[0]:
                lines.append(old[1])
            else:
                values = [", ".join(row[key]) if key == "dependencies" else row[key] for key in columns]
                lines.append(render_line(values, self.newline))
        return "".join(self.lines[:self.start + 1] + lines + self.lines[self.end:]).encode("utf-8")


def read_file(path):
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise TrackerError("invalid_file", "The tracker must be a regular file.")
    return path.read_bytes(), info


def require_revision(data, expected):
    actual = revision(data)
    if actual != expected:
        raise TrackerError("stale_revision", "The document changed. Reread the affected records before retrying.",
                           exit_code=3, expected_revision=expected, actual_revision=actual)


@contextmanager
def writer_lock(path):
    lock = path.with_name("." + path.name + ".lock")
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise TrackerError("writer_busy", f"Writer lock exists: {lock}. Inspect its owner; never remove an active writer's lock.",
                           exit_code=4) from error
    identity = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "host": socket.gethostname()}, stream)
            stream.write("\n")
        yield
    finally:
        try:
            current = lock.lstat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                lock.unlink()
        except FileNotFoundError:
            pass


def publish(path, candidate, original=None, mode=0o600):
    descriptor, name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(candidate)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, stat.S_IMODE(mode))
        if original is None:
            # A hard-link publication is atomic and never replaces a new arrival.
            try:
                os.link(temporary, path)
            except FileExistsError as error:
                raise TrackerError("file_exists", f"Refusing to overwrite an existing file: {path}.") from error
        else:
            latest, info = read_file(path)
            require_revision(latest, revision(original))
            if info.st_nlink != 1:
                raise TrackerError("hardlinked_file", "Writes require a tracker with one filesystem link.")
            os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def find_record(records, item):
    for index, row in enumerate(records):
        if row["id"] == item:
            return index
    raise TrackerError("missing_item", f"No item with ID {item!r} exists in this tracker.")


def edit_document(document, args):
    changes = {key: field_value(key, getattr(args, key)) for key in COLUMNS
               if key != "id" and hasattr(args, key)}
    records = list(document.records)
    if args.command == "update":
        if not changes:
            raise TrackerError("missing_change", "Supply at least one field to update.")
        index = find_record(records, args.id)
        row = {**records[index], **changes}
        records[index] = row
    else:
        if any(row["id"] == args.id for row in records):
            raise TrackerError("duplicate_id", f"An item with ID {args.id!r} already exists.")
        row = {**empty_record(), "id": args.id, **changes}
        index = len(records)
        if args.before:
            index = find_record(records, args.before)
        elif args.after:
            index = find_record(records, args.after) + 1
        records.insert(index, row)
    validate_records(records)
    return document.render(records), row


def execute(args):
    requested = Path(args.file).expanduser()
    if args.command == "init" and os.path.lexists(requested):
        raise TrackerError("file_exists", f"Refusing to overwrite an existing file: {requested}.")
    path = requested.resolve()
    base = {"file": str(path)}
    if args.command == "init":
        data = ("# Implementation\n\n" + OPEN + "\n" +
                render_line([COLUMNS[key] for key in REQUIRED], "\n") +
                render_line(["---"] * len(REQUIRED), "\n") + CLOSE + "\n").encode()
        with writer_lock(path):
            publish(path, data)
        return {**base, "revision": revision(data), "changed": True, "count": 0}
    if args.command in ("insert", "update"):
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.expected_revision):
            raise TrackerError("invalid_revision", "Use the sha256 revision returned by a read command.")
        with writer_lock(path):
            data, info = read_file(path)
            require_revision(data, args.expected_revision)
            if info.st_nlink != 1:
                raise TrackerError("hardlinked_file", "Writes require a tracker with one filesystem link.")
            candidate, row = edit_document(Document(data), args)
            if candidate != data:
                publish(path, candidate, original=data, mode=info.st_mode)
        return {**base, "revision": revision(candidate), "slice": row, "changed": candidate != data}
    data, _ = read_file(path)
    document = Document(data)
    result = {**base, "revision": revision(data)}
    if args.command == "validate":
        return {**result, "valid": True, "count": len(document.records)}
    if args.command == "inspect":
        return {**result, "slice": document.records[find_record(document.records, args.id)]}
    records = [row for row in document.records if (args.type == "all" or row["type"] == args.type)
               and (args.status is None or row["status"] == args.status)]
    return {**result, "slices": records}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise TrackerError("invalid_arguments", message)


def parser():
    root = Parser(description=__doc__)
    root.add_argument("--file", default="IMPLEMENTATION.md", help="Tracker path (default: ./IMPLEMENTATION.md).")
    root.add_argument("--json", action="store_true", help="Emit structured success or error output.")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("init", "list", "inspect", "validate", "insert", "update"):
        command = commands.add_parser(name)
        command.add_argument("--file", default=argparse.SUPPRESS)
        command.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        if name == "list":
            command.add_argument("--status", choices=STATUSES)
            command.add_argument("--type", choices=("slice", "epic", "all"), default="slice")
        if name in ("inspect", "insert", "update"):
            command.add_argument("id")
        if name in ("insert", "update"):
            command.add_argument("--expected-revision", required=True)
            for key in COLUMNS:
                if key == "id":
                    continue
                command.add_argument("--" + key, default=argparse.SUPPRESS,
                                     required=name == "insert" and key in ("title", "checkpoint"))
        if name == "insert":
            position = command.add_mutually_exclusive_group()
            position.add_argument("--before")
            position.add_argument("--after")
    return root


def print_human(result):
    print(f"File: {result['file']}")
    print(f"Revision: {result['revision']}")
    if "slices" in result:
        for row in result["slices"]:
            print(f"{row['id']}\t{row['status']}\t{row['title']}")
    elif "slice" in result:
        for key, value in result["slice"].items():
            print(f"{COLUMNS[key]}: {', '.join(value) if isinstance(value, list) else value}")
    elif "valid" in result:
        print(f"Valid structure: {result['count']} records")
    else:
        print("Created empty tracker")
    if "changed" in result and not result["changed"]:
        print("Unchanged")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    try:
        args = parser().parse_args(argv)
        result = execute(args)
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print_human(result)
        return 0
    except TrackerError as error:
        payload, exit_code = error.error, error.exit_code
    except (OSError, RuntimeError) as error:
        payload, exit_code = {"code": "filesystem_error", "message": str(error)}, 1
    if as_json:
        print(json.dumps({"error": payload}, ensure_ascii=False), file=sys.stderr)
    else:
        print(f"{payload['code']}: {payload['message']}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
