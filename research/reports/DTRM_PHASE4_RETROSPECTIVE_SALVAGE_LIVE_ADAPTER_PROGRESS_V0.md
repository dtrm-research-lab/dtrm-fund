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
