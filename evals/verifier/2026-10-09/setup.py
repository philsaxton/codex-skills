#!/usr/bin/env python3
"""Organizer-only fixture materializer; never supply this file to reviewers."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "setup/variants.json"


def read_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def source_files(case):
    files = {}
    for source in (ROOT / "fixtures" / case, ROOT / "setup/products" / case):
        for path in sorted(source.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files[path.relative_to(source).as_posix()] = path
    return files


def child(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe setup path: {relative}")
    target = root / path
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
        raise ValueError(f"refusing symlinked target: {target}")
    return target


def materialize(case, variant, target, update=False):
    catalog = read_catalog()
    spec = catalog[case][variant]
    target = Path(target).absolute()
    resolved = target.resolve()
    if resolved == ROOT or ROOT in resolved.parents or resolved in ROOT.parents:
        raise ValueError("run copies must be outside this evaluation bundle")
    files = source_files(case)
    if update:
        request = target / "REQUEST.md"
        if not request.is_file() or request.read_bytes() != files["REQUEST.md"].read_bytes():
            raise ValueError("update requires a matching, unchanged raw REQUEST.md")
    elif target.exists():
        raise ValueError("new target already exists; choose a fresh run directory")
    target.mkdir(parents=True, exist_ok=update)
    for relative, source in files.items():
        destination = child(target, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    for patch in spec.get("replace", []):
        if patch["file"] not in files:
            raise ValueError("replacement must target a supplied file")
        path = child(target, patch["file"])
        text = path.read_text(encoding="utf-8")
        if text.count(patch["old"]) != 1:
            raise ValueError(f"replacement not unique in {path.name}")
        path.write_text(text.replace(patch["old"], patch["new"]), encoding="utf-8")
    for relative in spec.get("remove", []):
        if relative not in files:
            raise ValueError("removal must target a supplied file")
        child(target, relative).unlink()
    return target


def main():
    catalog = read_catalog()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("new", "update"))
    parser.add_argument("case", choices=sorted(catalog))
    parser.add_argument("variant")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    if args.variant not in catalog[args.case]:
        parser.error("variant must be one of: " + ", ".join(catalog[args.case]))
    try:
        target = materialize(args.case, args.variant, args.target, update=args.action == "update")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(target)


if __name__ == "__main__":
    main()
