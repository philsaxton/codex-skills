# Codex Skills

This repository contains portable Codex skills. Install it at `.agents/skills/` in another project as a Git submodule:

```sh
git submodule add https://github.com/philsaxton/codex-skills.git .agents/skills
```

Copy [config.toml.template](config.toml.template), or append its contents, to `.codex/config.toml` in the consuming project root. All implemented skills start disabled; enable them gradually by changing the corresponding `enabled` value to `true`, then restart Codex after config changes.

The relative entries assume the repository is installed at `.agents/skills/` in that project root. If the installed Codex version does not resolve skill overrides from the project root, prefix each `.agents/skills/.../` entry with the project's absolute root.

The proposed candidates in the template are commented out because their skill folders have not been implemented.
