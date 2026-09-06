#!/bin/sh
set -eu

usage() {
  echo "Usage: $0 SKILL..." >&2
  echo "       $0 --all" >&2
}

project_root=$(pwd -P)
library_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)

case "$library_dir" in
  "$project_root"/*) library_relative=${library_dir#"$project_root"/} ;;
  *)
    echo "Run this helper from the root of the project that vendors this repository." >&2
    exit 1
    ;;
esac

mkdir -p .agents/skills

link_skill() {
  skill=$1
  case "$skill" in
    ''|.|..|*/*)
      echo "Invalid skill name: $skill" >&2
      exit 1
      ;;
  esac

  source_dir=$library_dir/$skill
  destination=.agents/skills/$skill
  target=../../$library_relative/$skill

  if [ ! -f "$source_dir/SKILL.md" ]; then
    echo "Unknown skill: $skill" >&2
    exit 1
  fi

  if [ -L "$destination" ] && [ "$(readlink "$destination")" = "$target" ]; then
    echo "Already linked: $skill"
  elif [ -e "$destination" ] || [ -L "$destination" ]; then
    echo "Refusing to replace existing path: $destination" >&2
    exit 1
  else
    ln -s "$target" "$destination"
    echo "Linked: $skill"
  fi
}

if [ "$#" -eq 0 ]; then
  usage
  exit 1
fi

if [ "$1" = "--all" ]; then
  if [ "$#" -ne 1 ]; then
    usage
    exit 1
  fi
  for candidate in "$library_dir"/*; do
    if [ -f "$candidate/SKILL.md" ]; then
      link_skill "$(basename "$candidate")"
    fi
  done
else
  for skill in "$@"; do
    link_skill "$skill"
  done
fi
