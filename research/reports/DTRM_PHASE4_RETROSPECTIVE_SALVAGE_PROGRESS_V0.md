# Phase IV retrospective salvage audit progress v0

## 2026-09-08 — Preregistration

- The user authorized integration of PR #5 and continuation with the
  retrospective-salvage preregistration.
- PR #5 reviewed head `b60ab2952e4c98eb5e01b383dd6942335ab20b9b`
  was current, mergeable, free of comments and had four successful workflows.
  It was integrated as merge commit
  `1912cc9685ad7cfaa584c031dd330a46cdac053c`, preserving both parent histories.
- Opened `feature/phase4-retrospective-salvage-audit-v0` from that integration.
  The contract fixes the final outcome-blind test of ObjectId/insertion evidence
  before implementation or any new database query.
- The audit cannot declare ObjectId an observation clock. It defines
  contradicted, partial and candidate states; every state keeps history,
  training and outcomes disabled. A candidate result would require a separate
  decision-clock binding before history construction.
- Live reads remain operator-only. Agent/CI environments may use synthetic data
  and must not inspect secrets or production configuration.
- No Mongo query, source value, outcome, history construction, fit, MM1 run,
  prospective collector change or scientific promotion occurred in preparing
  this registration. Phase III and the original Phase-IV contract remain frozen.

## Contract validation

- Registration commit: `6ce50a46de1320c558bd4ac051a051fd95a53bda`;
  contract SHA-256:
  `e9ed93bcd39181f2037227eee39690b9259753a686b3f9e89614243f41d8e5c9`.
- Scoped Ruff passed; strict mypy passed for 13 existing source/experiment
  files. The complete suite passed with 453 tests and the three expected
  dedicated-CI Mongo tests skipped locally.
- All three existing synthetic reports reproduced byte for byte. The pinned
  collector-lineage validator passed with 12 findings. The wheel built from a
  disposable archived source tree.
- Source preservation passed before and after all gates for all 157 inherited
  files and the original Stage-0 contract. The working tree was clean after
  validation.
- These are contract/regression checks, not implementation tests for the future
  salvage graph. Current-head CI and human review remain required. No live query
  is authorized by these checks.
