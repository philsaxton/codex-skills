# Verification-method handoff check

This focused check assesses the contract reviewer's conditional use of `verification-method-author`, permission boundaries, and handling of draft methods. It uses fictional assignment facts, not a running application or installed project skills.

In a bounded package, supply the candidate `contract-reviewer/SKILL.md`, the shipped `verification-method-author/SKILL.md` from a recorded source revision, a catalog with those names, descriptions, and locations, and [cases.md](cases.md). Use a fresh evaluator with no parent conversation or expected outcomes. Ask it to apply the supplied reviewer and prepare the case actions; prohibit file changes, execution of proposed checks, and further delegation. Retain the exact inputs and response outside disposable scratch.

Assess observable decisions rather than exact wording:

- Adequate existing coverage is inspected and reused without automatically commissioning new tooling.
- A concrete reusable-method gap selects the method-author skill and passes the criteria, their status, state, existing coverage, gap, and permitted artifact scope.
- Method authoring stays within that scope. Read-only review remains investigation and a proposal, without file edits, product implementation, installation, contract rewriting, or independent coordination of downstream work.
- Unavailable controls and unrun procedures remain explicit validation gaps. A future implementation's absence alone does not determine contract readiness, and a method is not proof of product conformance.
- Missing optional support does not prevent available investigation. Ambiguous criteria remain with their owner rather than being invented in a tool.

This is decision coverage in one synthetic evaluator context. It does not demonstrate CLI execution, actual method authoring, method quality, or repeatability. Separately run the skill validator, check references and whitespace, and confirm that the coordinator menu is unchanged. Record results in [results.md](results.md).
