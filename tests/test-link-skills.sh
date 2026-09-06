#!/bin/sh
set -eu

source_repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture=$(mktemp -d)
trap 'rm -rf "$fixture"' EXIT HUP INT TERM

mkdir -p "$fixture/vendor/codex-skills/alpha" "$fixture/vendor/codex-skills/beta"
mkdir -p "$fixture/vendor/codex-skills/scripts"
touch "$fixture/vendor/codex-skills/alpha/SKILL.md" "$fixture/vendor/codex-skills/beta/SKILL.md"
cp "$source_repo/scripts/link-skills.sh" "$fixture/vendor/codex-skills/scripts/link-skills.sh"

cd "$fixture"
./vendor/codex-skills/scripts/link-skills.sh alpha
test "$(readlink .agents/skills/alpha)" = '../../vendor/codex-skills/alpha'

./vendor/codex-skills/scripts/link-skills.sh alpha

./vendor/codex-skills/scripts/link-skills.sh --all
test "$(readlink .agents/skills/beta)" = '../../vendor/codex-skills/beta'

if ./vendor/codex-skills/scripts/link-skills.sh missing >/dev/null 2>&1; then
  echo 'unknown skill unexpectedly succeeded' >&2
  exit 1
fi

rm .agents/skills/alpha
touch .agents/skills/alpha
if ./vendor/codex-skills/scripts/link-skills.sh alpha >/dev/null 2>&1; then
  echo 'destination conflict unexpectedly succeeded' >&2
  exit 1
fi
