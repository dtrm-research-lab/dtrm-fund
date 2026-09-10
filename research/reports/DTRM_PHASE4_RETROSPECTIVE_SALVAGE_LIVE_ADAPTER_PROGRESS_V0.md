# Phase IV retrospective-salvage live adapter progress v0

## 2026-09-09 — Preregistration

- PR #8 was integrated by the user-authorized merge commit
  `a8bf5353f4fa46ad59d66faa980a1004276f97a8`, with reviewed feature head
  `9684492b5e66fed148a8d06ddce84cc2e7e7ce78` as its second parent. Both
  current-head workflows passed and both review findings were resolved before
  integration.
- Opened
  `feature/phase4-retrospective-salvage-live-adapter-contract-v0` from that
  exact merge. This increment registers a separate user-local, read-only Mongo
  adapter before its implementation or any live execution.
- The contract fixes configuration keys and precedence, explicit no-override
  dotenv semantics, CI isolation, exact namespace/projection/count/cursor/index
  reads, majority concern, timeouts, cap-plus-one streaming, resource closure,
  canonical aggregate-only output and the required test matrix.
- Writer/runtime findings are fixed from the already reviewed static evidence.
  Unknown deployed intervals, relevant-writer completeness, later mutation,
  client clock and write authority cannot be self-attested by CLI input.
  Therefore this adapter v0 cannot produce `RETROSPECTIVE_PROXY_CANDIDATE`.
- This registration does not access configuration, Mongo, source rows,
  outcomes, prices, targets or scores. It does not construct history, fit a
  model, execute MM1 or modify the prospective collector. Scientific status
  remains `BLOCKED_SOURCE_AUDIT` and all scientific permissions remain false.
- The next permitted operation is contract validation, current-head CI and
  human review. Implementation must occur in a later descendant commit only
  after this registration is preserved remotely.

## Registration validation

- Authoritative remote registration commit:
  `13625046e8b258f085fab59966a31937786a5eec`; tree
  `0fa23ee5990658faa577a4a6f1e43390eb0e9eae`; contract SHA-256
  `f98ce5e5d22810618571725d1645806729da358ff7622a7c47150cdc3e5cfcad`.
  It directly descends from PR #8 merge `a8bf5353f4fa46ad59d66faa980a1004276f97a8`.
- Full regression passed with 534 tests and three expected local skips reserved
  for the existing disposable-CI Mongo job. Scoped Ruff passed; strict mypy
  passed for 16 files.
- All four prior synthetic reports reproduced byte for byte. The pinned
  collector-lineage validator passed with 12 findings, the wheel built from a
  disposable archive and source preservation passed before and after for all
  157 inherited files and the original Stage-0 contract.
- Validation imported no production driver for this registration, inspected no
  configuration and performed zero source queries. These are contract and
  regression results only; current-head CI and human review remain pending.
- Machine-readable evidence is recorded in
  `DTRM_PHASE4_RETROSPECTIVE_SALVAGE_LIVE_ADAPTER_VALIDATION_V0.json`.

## Implementation after PR #9 integration

- The user authorized integration and continuation. PR #9 was merged as
  `d11b9cff62e656cb64664d126e48dca9381ffc7e`, retaining registration
  `13625046e8b258f085fab59966a31937786a5eec` as an ancestor. The ancestry
  review comment referred to a different review snapshot; the actual feature
  head's direct parent was the registration. The evidence is recorded in the
  PR review thread, which was resolved before merge.
- Branch `feature/phase4-retrospective-salvage-live-adapter-v0` starts at that
  merge. Implemented the separate live CLI, injected configuration/read
  boundaries, genuine BSON classification, shared streamed derivations, fixed
  static writer assessment and typed aggregate-only live serialization.
- Production configuration is never inspected during development. Tests pass
  explicit synthetic mappings; no production connection is attempted. The
  implementation closes resources, redacts errors and third-party debug logs,
  and publishes only a fully serialized report through exclusive creation.
- Added 36 unit/functional-double cases plus three disposable-Mongo cases.
  Initial scoped validation: 117 salvage tests pass; strict typing passes for
  19 files. Full local regression initially stopped before test execution on a
  native XGBoost library Bus error; the same dependency version is being
  reinstalled in the isolated environment. This is not recorded as a pass.
- Current-head CI, full regression and human implementation review remain
  pending. No real-source evidence, history, outcome, fit or MM1 run occurred.

## Implementation validation — PR #10

- Tested remote implementation head `1169058039c6fe1ea3ee2492a1846250afb68a96`
  has tree `d82ae58efc88e7d83e880863d5bcebd37e32c9f4`. Both workflows passed:
  Tests run `34391785303` and Phase IV gates run `34391785409`.
- Authoritative isolated CI: 572 regression tests passed, six skipped in the
  ordinary job; all six Mongo functional tests passed in the dedicated
  disposable service job (three existing, three new). Scoped Ruff, strict
  mypy (19 files), four synthetic reproductions, pinned lineage validation,
  wheel build and pre/post preservation of 157 inherited files passed.
- Final local focused adapter run: 38 passed with `PYTHONPATH=src`. An initial
  invocation without that path failed collection, then the corrected command
  passed. BSON Code subclasses are explicitly excluded from plain-string
  text, URL and ticker derivations.
- Correction to the earlier environment update: the attempted same-version
  XGBoost reinstall was blocked by a cancelled network approval and was not
  retried. Full local regression remains `BLOCKED_ENVIRONMENT` (native Bus
  error), not a pass. Full regression evidence above comes from clean CI.
- Machine-readable implementation evidence is in
  `DTRM_PHASE4_RETROSPECTIVE_SALVAGE_LIVE_ADAPTER_IMPLEMENTATION_VALIDATION_V0.json`.
  This evidence records the tested implementation commit, not its own future
  documentation commit. Current-head CI must also pass before integration.
- PR #10 awaits human review and explicit merge authorization. No production
  environment or database was accessed. Scientific status remains
  `BLOCKED_SOURCE_AUDIT`; history, outcomes and training remain prohibited.

## Review corrections and final implementation evidence

- Automated review of implementation head `1169058039c6fe1ea3ee2492a1846250afb68a96`
  raised three findings. Commit `877751ac9fb8d505e16925ed521214be59511532`,
  tree `9a7cbbf4a9ee83a30faf21377d37553ff35f1d5f`, addresses both valid findings:
  the live cursor now preserves raw BSON wire codes before PyMongo's legacy
  `undefined`/`symbol` decoding can erase them, and live report validation
  reconciles `_id.objectId` type counts with genuine ObjectId evidence.
- Three regressions cover symbol/undefined field, ticker and dedupe semantics
  plus inconsistent ObjectId aggregate rejection. Local focused adapter tests
  now pass 41/41; all local Phase IV tests pass 284 with six dedicated-Mongo
  skips. Strict mypy passes for the changed source. Local Ruff could not execute
  because its native binary segfaulted; clean CI is the authoritative lint run.
- The remaining review claim—that standalone Mongo cannot execute this
  majority read—was empirically contradicted twice. Most recently the unchanged
  standalone `mongo:7.0.14` job passed all six functional tests, including the
  explicit `ReadConcern("majority")` census. No replica-set change was made.
- Current corrected-head CI passed: Tests run `34446222303`; Phase IV gates run
  `34446222322`; 575 regression tests passed with six expected skips, all six
  disposable-Mongo tests passed, and Ruff, strict mypy (19 files), four
  synthetic reproductions, lineage validation, wheel build and both source
  preservation checks succeeded.
- The implementation-validation JSON is updated to this tested code commit and
  tree. A following evidence-only commit must itself pass current-head CI before
  merge. PR #10 still requires explicit human authorization; scientific gates
  remain closed and no production source was accessed.

## Second review corrections and closure

- A requested current-head rereview found two additional edge cases. Commit
  `d3da513a163def2ea5c9cdfe985006d90b8ce9b9`, tree
  `1a9e9229a669ff529d5e0ffcfd51205fa83e671f`, hashes an object/array
  `dedupe_key` containing legacy BSON directly from its exact root wire payload,
  while retaining pure-graph hash equality for ordinary values. It also treats
  failure to remove the temporary hard-link source after successful atomic
  publication as best-effort cleanup, preventing a complete report from being
  announced as a failed audit.
- Added two nested BSON regressions and one post-publication cleanup regression.
  Final local focused adapter tests pass 44/44; all Phase IV tests pass 287 with
  six dedicated-Mongo skips; strict mypy passes for all 19 scoped files. The
  synthetic salvage report remains byte-identical and source preservation
  remains `PASS` for all 157 inherited files.
- Corrected-head CI is fully green: Tests run `34447482573`; Phase IV gates run
  `34447482628`; 578 tests passed with six expected skips; all six disposable
  Mongo tests passed; Ruff, strict mypy, all four reproductions, lineage,
  disposable wheel and both preservation checks passed.
- Both new review threads were answered with corrected-head evidence and
  resolved. No production execution occurred and no scientific permission or
  assessment changed. The next commit records only this evidence and must pass
  both current-head workflows before human merge authorization.

## Final rereview correction

- Final rereview identified one post-publication console edge case. Commit
  `ff5024c4cc1808d535339e4b362c697a1e892718`, tree
  `9b8b56d9ad079020b14c0059a700313994a47ec3`, constructs the accepted summary
  before publication and makes console emission best-effort. Closed or
  unwritable stdout can no longer report failure after the complete aggregate
  file has been atomically published.
- The new regression brings focused adapter validation to 45/45 and all local
  Phase IV tests to 288 passed with six dedicated-Mongo skips. Corrected-head
  CI is green: Tests run `34448699758`; Phase IV gates run `34448699736`; 579
  tests passed with six expected skips and all six disposable-Mongo tests
  passed. Ruff, strict mypy (19 files), reproductions, lineage, wheel and both
  157-file preservation checks passed.
- The sixth review thread was answered and resolved. Across three review
  rounds, all six threads are closed; five valid edge cases were corrected and
  the standalone-majority claim was resolved with direct CI evidence. No
  production source was accessed and scientific status remains blocked.
- This record and the machine-readable evidence now point to the final tested
  code commit. A final evidence-only head must be green before explicit human
  merge authorization.

## Integration and operator live evidence

- The user authorized PR #10 and it was integrated by merge commit
  `2b0dbeac662f2c0bd51db24b9045a600be83d0da`, with base parent
  `d11b9cff62e656cb64664d126e48dca9381ffc7e` and validated head parent
  `a4dbb443a1d9ee9b9e8c743be2e771ec1ec5d987`.
- The operator then executed the integrated live adapter locally. The accepted
  canonical report contains 63,873 documents, has zero count/cursor delta,
  passes all reconciliations and selects `RETROSPECTIVE_PROXY_PARTIAL` with
  `BLOCKED_SOURCE_AUDIT` and every scientific permission false.
- The transferred terminal rendering reconstructs the exact 10,553 canonical
  bytes and operator SHA-256
  `e061be9a0dea615d87178903d87d997564befc9062341e0be0b096ba31d650cd`.
  All three internal hashes and the registered contract identity recompute.
  Operator and transfer scans report no sensitive pattern. The agent made no
  source connection.
- The evidence supports a structural insertion chronology but not an
  authenticated historical information set. A prospective immutable collector
  remains required for confirmatory Phase IV. Any retrospective chronology is
  exploratory/development-only and needs a separate outcome-blind registration
  closing ticker element shape and writer/runtime provenance first.
