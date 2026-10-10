# Skills Repository

This repository houses reusable Codex skills that standardize development workflows across projects.

Put portable, cross-project behavior in these skills. Don't project-specific commands, constraints, and exceptions in skills. Those belong in the project's local `AGENTS.md`.

When creating or changing a skill:

- Use one clearly named directory per skill with `SKILL.md` as its entry point. A role may use several skills, and a skill may support several roles.
- Keep instructions concise, role-scoped, and independent of any one project.
- Don’t add scripts, references, or assets unless the skill’s required behavior can't be expressed clearly without them.
- Validate changed instructions and supporting resources before considering the work complete.

# Roles workflow skill 
- Preserve the contracts between roles and update affected handoffs together.
- When adding, changing, renaming, or retiring a delegable skill, review the coordinator's role menu and update affected entries and handoffs in the same change. A new skill may strengthen existing roles; add a role when it owns a distinct useful outcome. Keep detailed procedures in the skill, and validate new or changed routing with a representative task.
