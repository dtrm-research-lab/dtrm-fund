# Temporal boundary v0 progress

## 2026-09-08 — Contract-only increment

- User authorized progress that needs no local validation, while prohibiting
  access to secrets/environment configuration. No such access is part of this
  increment; real-source audit remains operator-only and pending.
- Independent branch `feature/phase4-temporal-boundary-v0` starts at approved
  PR #3 merge `f5148f2f6787d3282c04a357e59d32ed3c515ba8`. PR #4 remains open;
  its unmerged implementation is not included or implicitly approved.
- Added a proposed temporal-boundary contract, typed graph/node specification,
  25 future synthetic acceptance cases and seven later firewall obligations.
  Proposed exact-cutoff equality fails closed pending an ordering binding.
- Stage-1 exit conditions remain unresolved. To respect the registered stage
  sequence, no temporal verifier or Stage-2 firewall was implemented. No history,
  models, production queries, outcome access or scientific promotion occurred.
- This separate progress record avoids conflicting edits to PR #4's pending
  ledger append. The main ledger links this record; subsequent evidence belongs
  here. Human review and current-head CI remain required before integration.

## Agent-run validation of the proposal tree

- Remote registration commit: `7b35dbe407358e999ad20866173708b4f1149d3e`;
  tested tree: `e7c143d5f2b030f77b1a809777e71901b3eebaa5`. The local
  registration had the identical tree; no implementation exists in either.
- Existing unit, functional and regression suite: **406 passed in 3.36s**.
  This branch starts at approved PR #3, so it intentionally excludes PR #4's
  additional tests and isolated Mongo service; this is not a test-count loss.
- Scoped Ruff passed. Strict mypy passed for ten existing Phase-IV source and
  experiment files. Both existing synthetic reports reproduced byte for byte;
  the pinned collector-lineage validator passed with 12 findings.
- Disposable archived-source wheel build succeeded. Source preservation passed
  before and after all gates: all 157 inherited files and original Stage-0
  contract unchanged. Working tree was clean at the end of these checks.
- No new temporal-boundary unit or functional tests are claimed: the 25 cases
  are preregistered requirements for a future implementation, not executed code.
- This evidence append changes documentation only. Current-head remote CI must
  pass again; local results do not imply remote checks or human approval.
- Scientific status remains `BLOCKED_SOURCE_AUDIT`. No local validation by the
  user is needed to review this proposal, but unresolved real-source evidence
  still prevents closing Stage 1 or starting Stage-2 implementation.
