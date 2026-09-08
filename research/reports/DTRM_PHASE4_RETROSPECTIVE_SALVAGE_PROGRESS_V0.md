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

- Remote registration commit: `b38b3fc1851e1f636240e7fa418da2dcc933db8d`;
  its tree `0528d5aa7a121d59d82aeba80f1c8a26dd055883` is identical to the
  earlier local-only registration commit
  `6ce50a46de1320c558bd4ac051a051fd95a53bda`;
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

## 2026-09-08 — Pre-implementation review amendments

- The remote registration commit remains an ancestor of the review branch;
  its original contract and tree are preserved in history. The reviewed branch
  therefore records preregistration before both these clarifications and any
  implementation or new source query.
- Review identified two underspecified failure boundaries. The contract now
  assigns an empty census, a census without genuine BSON ObjectIds, and zero
  structurally eligible ObjectId-bearing observations deterministically to
  `RETROSPECTIVE_PROXY_CONTRADICTED`.
- The live cursor is now independently bounded to 250,001 rows. Observing the
  cap-plus-one row fails without an accepted report, even if a non-atomic
  preliminary count had reported at most 250,000.
- A review warning about missing preregistration ancestry arose from a squashed
  review snapshot. The remote branch history is linear from registration
  `b38b3fc1851e1f636240e7fa418da2dcc933db8d` to its validation commit and
  preserves the registered tree above.
- The amended contract hash and authoritative remote amendment commit will be
  recorded after the amended commit is published. No implementation or live
  query occurred while making these clarifications.
