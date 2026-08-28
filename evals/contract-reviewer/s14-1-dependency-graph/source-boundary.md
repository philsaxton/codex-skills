# Source boundary and artifact identities

## Permitted historical review basis

- Project repository: `philsaxton/client-agent-workspace`
- Project baseline: `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`
- Preserved adverse S2.1 checkpoint: `d91e68065aa99c7368eab21c8a93eeac6d7d3893`
- Exclude every original FR-07 artifact, every later S14.1 artifact, all prior counterfactual reviews, and every project commit at or after `e707602f75391eeed5605c0fd25de39bac9400c4` during a blinded run.

The reviewer may directly inspect relevant files from the two permitted commits. It must not use summaries of excluded material.

## Frozen artifacts

| Artifact | Lines | SHA-256 |
| --- | ---: | --- |
| `artifacts/counterfactual-contract.md` | 231 | `6a750764c946134ede1cf405f07b83b77f806f87fddb86b5cae3933c4b8a9c2a` |
| `artifacts/original-contract-v1.0.0.md` | 333 | `021da09fc937958c84db8334662a6bb869d52f643d8e5476b26dcb87c2d5780d` |
| `artifacts/original-contract-v1.1.0.md` | 341 | `a9cc6d730fcafd633bd13940b3631add72eae79aaf4c4d625d4125d0e5c60c51` |
| `artifacts/original-review-history.md` | 169 | `ec69ea5da14ce4268a4977da9ea4738a2b074fcc921ea6c5ac17402eefb6def9` |
| `artifacts/review-project-role-run.md` | 192 | `e5179b1765ab6e046e42b2d1101ae1dc8e2d80e90f1a733763cb7f10167ce588` |
| `artifacts/review-portable-skill-run.md` | 142 | `b9c0d6226fcde5002077763784afbd9476c2142f56b0d621681e6b452fcce141` |

The original v1.0.0 and v1.1.0 contracts were recovered from commits `e707602f75391eeed5605c0fd25de39bac9400c4` and `3bd6a1ef4e56cfd480688463b2f72a3c2fb91669`, respectively.

## Baseline-run limitations

- The first counterfactual review used the current project reviewer role/guidance and was not a portable-skill-only test.
- The portable-skill rerun also ran inside the client's current control-plane environment. It tested the skill as used in that project, not in isolation.
- Exact elapsed time was not captured reliably. Do not convert conversational estimates into measured runtime.
- The counterfactual deliberately uses non-authoritative identifiers and lives outside the project repository. Those properties limit project approval but are not the target semantic defect.
