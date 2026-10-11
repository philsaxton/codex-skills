# Selected guidance and retirement routing

The installation under test selects the six unchanged application roles/methods from application revision `6136fe2ea7bf6229f9654d53719e780e060930d6`: coordinator, solution-design, contract-author, contract-reviewer, verifier and verification-method-author. It also selects unchanged Superpowers systematic-debugging and test-driven-development at `bb92a77741419a4ab5f06e711a283343f1ada0c3`. Exact bytes and symlink destinations are in [guidance-manifest.json](guidance-manifest.json).

| Route | Experimental delivery |
|---|---|
| Every assignment, including prose and pre-implementation work | Project AGENTS.md points to the canonical `shared/completion-evidence.md`, outside skill discovery. |
| Completed application reviewer | The same controlling instructions also point to the pinned upstream Tests block in `shared/reviewer-evidence.md`. |
| Ordinary role selection | `.agents/skills` symlinks expose skill names/descriptions; natural CLI prompts only name TASK.md. |
| Explicit delegated worker | Starting prompt names the project, AGENTS, canonical rule, selected method and task paths. Parent instructions are not assumed to transfer. |
| Debugging → TDD | The retained debugging skill's implementation section invokes `superpowers:test-driven-development` (line 177); AGENTS maps it to the selected local skill. |
| Debugging → old completion skill | The retained debugging skill invokes `superpowers:verification-before-completion` (line 189); AGENTS explicitly maps it to the shared rule and says not to load the replaced skill. |
| TDD support reference → writing-skills | `writing-good-tests.md:51` concerns changing agent behavior. It does not apply to the application changes or human prose fixture. No such skill was invented or selected. |
| Verifier → verification-method-author | The unchanged relative companion link remains available. Method authoring retains its own scope and controls. |
| Optional verifier unavailable | B07 omits both its directory and discovery link; the task explicitly retains an independent bounded review responsibility. |
| Canonical file missing | B06 retains the routing instruction but removes its target. This is failed delivery, even if the document edit is otherwise correct. |

The old completion skill remains as a dormant vendor file with no discovery link. Its presence permits detection of an unintended instruction load without modifying upstream bytes. Inspect actual reads, not filename listings or hashing alone, when judging loading.

This inventory covers the selected experimental installation and its handoffs. Unselected upstream orchestration/branch-finishing skills and another consumer's prompts are not retired by this test. A real migration still needs its own selected-link and direct-reference inventory, canonical file publication, pin update, controlling instructions, and a fresh-session check. No production skill or consuming-project selection is changed by this bundle.
