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
- Authoritative remote amendment commit:
  `a1e7ce59d9e99a0b7d36d3989664508536dbb0ae`; amended contract SHA-256:
  `331ad4aaa2a60d4f2a3d172963e71052873d5942a475d4d3aa600d05495286f6`.
  The amended tree exactly matched the locally validated tree before publish.
- Pre/post source preservation passed for all 157 inherited files and the
  original Stage-0 contract. Scoped Ruff passed; strict mypy passed for 13
  files; the complete suite passed with 453 tests and three expected skips;
  all prior synthetic reports and the 12-finding lineage report reproduced;
  and the wheel built from a disposable archive. No implementation or live
  query occurred while making or validating these clarifications.

## 2026-09-09 — Contract integration and synthetic graph implementation

- The user authorized PR #7 integration by merge commit and continuation with
  the synthetic implementation. Reviewed head
  `d24f64e7179d76c55bdce992793ba09c07a01adb` was current and mergeable; both
  current-head PR workflows passed and all three review threads were resolved.
- PR #7 was integrated as merge commit
  `92006f523fd100719e93f837ce5c697ae9a65e83`, with parents
  `1912cc9685ad7cfaa584c031dd330a46cdac053c` and
  `d24f64e7179d76c55bdce992793ba09c07a01adb`. Registration
  `b38b3fc1851e1f636240e7fa418da2dcc933db8d` remains an ancestor. The 157-file
  preservation gate passed after branching from the exact merge.
- Opened `feature/phase4-retrospective-salvage-implementation-v0` from that
  merge. Implemented immutable projected-row state, fixed query metadata,
  deterministic provider-day/ObjectId diagnostics, exact content and URL
  grouping, source-ID/ticker/dedupe counters, sanitized index reuse, complete
  reconciliations and the exactly-one-state decision lattice.
- The injected census boundary independently enforces the preliminary cap and
  the cap-plus-one cursor stop, bounds index consumption and closes resources
  on success and failure. Exceptions expose fixed codes only.
- The CLI is synthetic-only and refuses overwrites and symlinks. It contains no
  Mongo connector, driver import, environment lookup or dotenv loading. Live
  source configuration and real-BSON/isolated-Mongo coverage remain explicitly
  pending rather than being inferred from synthetic success.
- The tracked ten-row fixture exercises a synthetic `PARTIAL` state and emits
  aggregate-only evidence. It is not a source conclusion: production access,
  history construction, training, outcomes, fitting and MM1 execution remain
  false and did not occur.

## Synthetic implementation validation

- Authoritative remote implementation commit:
  `77d80fd47f8cb816d35d4040d8decf2e378b329f`; tree
  `2e969eaaffd3f93e2b2c3a1a3d7973d4d02e68a6` exactly matched the locally
  tested implementation tree before publication.
- Added 80 unit and functional tests. The complete suite passed with 533 tests
  and the three pre-existing dedicated-CI Mongo tests skipped locally. The new
  tests cover every day-lag and group-size boundary, calendar parsing,
  ObjectId/non-ObjectId and future-clock cases, exact UTF-8 hashing, URL/source
  precedence, ticker/dedupe/version aggregates, reconciliation, immutability,
  all decision states, cap races, bounded consumption, resource closure,
  fixed-error redaction and CLI filesystem defenses.
- Scoped Ruff passed; strict mypy passed for 16 files. All four synthetic
  reports reproduced byte for byte, the 12-finding collector validator passed,
  the wheel built from a disposable archive, and the 157 inherited files plus
  original Stage-0 contract passed preservation before and after validation.
- Synthetic report SHA-256:
  `5c25ef1dd4eac262b36523cee31304fd50eceb8c36557dd7eefbc95f761abc7a`;
  its pipeline and evidence hashes are
  `4ae55be2684962e67c4b4843b417be1b337f95e70f00219a0712bcba67829114`
  and `78cc1cd525b1990cc9f10352e78af11ecea4fdc86ca8bf09a65918f23488aca0`.
- Full machine-readable evidence is recorded in
  `DTRM_PHASE4_RETROSPECTIVE_SALVAGE_VALIDATION_V0.json`. Current-head remote
  CI and human review remain pending. The unimplemented live tests are listed
  explicitly; this increment makes no claim of completing the live audit.
