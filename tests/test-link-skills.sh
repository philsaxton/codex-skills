#!/bin/sh
set -eu

source_repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT HUP INT TERM

mkdir -p "$fixture/.agents/vendors/codex-skills/alpha" "$fixture/.agents/vendors/codex-skills/beta"
mkdir -p "$fixture/.agents/vendors/codex-skills/scripts"
nested_candidate="$fixture/.agents/vendors/codex-skills/evals/spec-test-dev/2026-10-18/treatments/spec-test-dev"
mkdir -p "$nested_candidate"
touch "$fixture/.agents/vendors/codex-skills/alpha/SKILL.md" "$fixture/.agents/vendors/codex-skills/beta/SKILL.md"
touch "$nested_candidate/SKILL.md"
cp "$source_repo/scripts/link-skills.sh" "$fixture/.agents/vendors/codex-skills/scripts/link-skills.sh"

cd "$fixture"
./.agents/vendors/codex-skills/scripts/link-skills.sh alpha
test "$(readlink .agents/skills/alpha)" = '../../.agents/vendors/codex-skills/alpha'
test -f .agents/skills/alpha/SKILL.md

./.agents/vendors/codex-skills/scripts/link-skills.sh alpha

./.agents/vendors/codex-skills/scripts/link-skills.sh --all
test "$(readlink .agents/skills/beta)" = '../../.agents/vendors/codex-skills/beta'
test -f .agents/skills/beta/SKILL.md
test -f "$nested_candidate/SKILL.md"
test ! -e .agents/skills/spec-test-dev
test ! -L .agents/skills/spec-test-dev
set -- .agents/skills/*
test "$#" -eq 2

if ./.agents/vendors/codex-skills/scripts/link-skills.sh missing >/dev/null 2>&1; then
  echo 'unknown skill unexpectedly succeeded' >&2
  exit 1
fi

rm .agents/skills/alpha
touch .agents/skills/alpha
if ./.agents/vendors/codex-skills/scripts/link-skills.sh alpha >/dev/null 2>&1; then
  echo 'destination conflict unexpectedly succeeded' >&2
  exit 1
fi
