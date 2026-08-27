# Codex Skills

This repository contains portable Codex skills.

## Install

From the root of the project where you want to use the skills, add this repository as a vendored submodule outside Codex's skill-discovery directory:

```sh
git submodule add https://github.com/philsaxton/codex-skills.git vendor/codex-skills
```

Then activate only the skills that project should discover by linking them into `.agents/skills/`. For example:

```sh
mkdir -p .agents/skills
ln -s ../../vendor/codex-skills/contract-author .agents/skills/contract-author
ln -s ../../vendor/codex-skills/contract-reviewer .agents/skills/contract-reviewer
```

Add or remove these symlinks to control the project's startup skill inventory. Do not delete or move directories inside the submodule: keeping it intact allows normal submodule updates and lets dormant skills be loaded explicitly by path for testing. Commit the submodule registration and the selected symlinks so the project records both the library version and its active skill set.

Copy [config.toml.template](config.toml.template), or append its contents, to `.codex/config.toml` in the consuming project root. The template requests that all implemented skills start disabled so they can be enabled gradually.

> **Current Codex limitation:** Do not rely on project-local `[[skills.config]]` entries to enforce per-skill enable or disable settings. Codex may ignore those entries and expose every skill under `.agents/skills/`; this is tracked in [openai/codex#20210](https://github.com/openai/codex/issues/20210). Until that behavior is fixed and verified, treat every skill installed under `.agents/skills/` as available to agents.

The relative entries in the template refer to the activated links under `.agents/skills/`. If the installed Codex version does not resolve skill overrides from the project root, prefix each `.agents/skills/.../` entry with the project's absolute root.

The proposed candidates in the template are commented out because their skill folders have not been implemented.
