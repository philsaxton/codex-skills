# Codex Skills

This repository contains portable Codex skills.

## Install

From the root of the project where you want to use the skills, add this repository as a vendored submodule outside Codex's skill-discovery directory:

```sh
git submodule add https://github.com/philsaxton/codex-skills.git vendor/codex-skills
```

Then activate only the skills that project should discover. From the consuming project's root, use the included helper with one or more skill names:

```sh
./vendor/codex-skills/link-skills.sh contract-author contract-reviewer
```

To activate every implemented skill:

```sh
./vendor/codex-skills/link-skills.sh --all
```

The helper validates skill names, creates `.agents/skills/`, and refuses to replace an existing path. It is safe to rerun for links it already manages. Add or remove these symlinks to control the project's startup skill inventory. Do not delete or move directories inside the submodule: keeping it intact allows normal submodule updates and lets dormant skills be loaded explicitly by path for testing. Commit the submodule registration and the selected symlinks so the project records both the library version and its active skill set.

To create a link manually instead:

```sh
mkdir -p .agents/skills
ln -s ../../vendor/codex-skills/contract-author .agents/skills/contract-author
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for skill authoring and validation requirements.
