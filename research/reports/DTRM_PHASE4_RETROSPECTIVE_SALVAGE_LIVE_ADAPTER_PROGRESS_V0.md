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
