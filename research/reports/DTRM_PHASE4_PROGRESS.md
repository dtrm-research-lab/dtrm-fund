# Phase IV progress ledger

Parallel contract-only increment (not Stage-2 implementation):
[Temporal boundary v0 progress](DTRM_PHASE4_TEMPORAL_BOUNDARY_PROGRESS_V0.md).

Current Stage-1 salvage increment:
[Retrospective salvage audit progress](DTRM_PHASE4_RETROSPECTIVE_SALVAGE_PROGRESS_V0.md).

## 2026-09-07 — Contract and event ontology

- User accepted the Stage-0 direction and instructed repository persistence and the project's Agentic Graph Engineering validation cycle.
- Archived the original research contract v0.1 without changing its bytes or declaring the complete experiment preregistered.
- Inherited source: `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`; Phase III remains frozen.
- Registered ontology v0 and the graph's node boundaries, failure modes, invariants, and acceptance cases before implementation.
- The proposed implementation is limited to typed observations, revision validation, metadata-completeness evidence, synthetic tests, and source preservation.
- Repository preregistration commit: `46a049021d96b84725e2636c9d24e5d5de8c1d18`.
- Implemented the three pure ontology nodes, immutable state, exact JSON boundary, revision-chain checks, and CLI that refuses to overwrite review evidence.
- Baseline regression suite: 291 passed. Added 44 synthetic contract/failure tests. Combined suite: 335 passed; targeted tests also passed after making the preservation test independent of shallow checkout history.
- Scoped lint and strict typing passed; wheel build passed in a disposable source copy. The build reports the inherited license-metadata deprecation warning; the frozen `pyproject.toml` was preserved.
- Verified all 157 inherited tracked files and the original Stage-0 contract by content identity.
- Synthetic output is tracked in `DTRM_PHASE4_ONTOLOGY_SYNTHETIC_REVIEW_V0.json`. The local validation record is `DTRM_PHASE4_ONTOLOGY_VALIDATION_V0.json`.
- Remote gates are recorded on the active PR head by GitHub `Tests` and `Phase IV gates`; this ledger does not replace or assume their conclusions.
- Human review and integration remain pending. Root `AGENTS.md` carries the delivery and scientific boundaries forward.
- Scientific status: `BLOCKED_SOURCE_AUDIT`; the inspected legacy projection does not establish precise version/link availability.
- Model fitting, history construction, MM1 runs, outcome access, scientific promotion, and release are not part of this increment.
- Next operation after review: read-only source metadata/vintage inventory and decision-clock binding. A passing ontology PR alone does not establish data readiness.

## 2026-09-07 — User-reported local validation

The user supplied the following terminal output from their local Mac validation:

```json
{"graph": "phase4_event_ontology_v0", "status": "succeeded", "scientific_status": "BLOCKED_SOURCE_AUDIT"}
{"inherited_commit": "a853d5d3f2d6c93a3483a0126ab3475b02960bfc", "inherited_tree": "fae65d7457225dff1601eaf43fb0ef2b2d4b2c19", "stage0_contract_sha256": "1ec55a67aaa89289e7f167564fb9788fde136f6decc8f5dbfebc54e7d6009f03", "status": "PASS_SOURCE_PRESERVATION", "verified_inherited_files": 157}
```

- This records user-reported ontology success and preservation of all 157 inherited files and the original Stage-0 contract, with the expected scientific block still active.
- The supplied excerpt does not include the tested HEAD, a local test-suite summary, or the synthetic comparison's exit status; these are not inferred from the preservation pass. Existing implementation and CI evidence remains separately attributed above and on PR #1.
- Human review and integration remain pending. This evidence update changes only the progress ledger and does not close the real-source audit gate.

## 2026-09-07 — Complete local validation supplied by the user

- Evidence: uploaded terminal transcript `Pegado text(8).txt`, SHA-256 `9dff12e0ef85e6f56479e35d84fcea00ecc1087303f4a445e923f122c6808db1`. This is user-supplied local execution evidence, distinct from agent execution and remote CI.
- Tested HEAD is explicitly printed: `b0b7612e9078d17e6c8c537ac62a4f05f3ff3ce1`. Build output identifies Python 3.11 and a macOS ARM64 build target.
- Scoped Ruff: `All checks passed!`; strict mypy: `Success: no issues found in 5 source files`.
- Full regression suite: `335 passed in 2.33s`.
- Ontology graph: `succeeded`, with scientific status `BLOCKED_SOURCE_AUDIT`.
- Synthetic comparison passed: the transcript reaches the final `PASS_LOCAL_PHASE4` marker after the supplied fail-fast command block's silent `cmp` step.
- Wheel build: `Successfully built dtrm_fund-0.1.0-py3-none-any.whl`, using a disposable archived source copy. The inherited license-metadata deprecation and deliberately disabled byte-compilation produced non-blocking warnings.
- Preservation before and after validation: `PASS_SOURCE_PRESERVATION`, 157 inherited files, with the pinned inherited commit/tree and Stage-0 contract hash unchanged.
- The final `git diff --exit-code` and `git status --short` produced no output before `PASS_LOCAL_PHASE4`.
- The local engineering validation is complete; the evidence gaps noted for the earlier excerpt are resolved. This append changes only the ledger and does not require the user to repeat the same local checks. Current-head CI remains the remote gate for this documentation update.
- Human review before integration remains pending under `AGENTS.md`. Real-source audit, decision-clock binding, and all subsequent scientific stages remain pending.

## 2026-09-07 — Review follow-up: incomplete revision timestamps

- PR #1 review threads `PRRT_kwDOT2PA1c6f3uUG` and `PRRT_kwDOT2PA1c6f3uUK` identified two implementation gaps against the existing ontology's clock semantics. No contract, scientific hypothesis, frozen source, or fixture was changed.
- The sole known logical `first_seen_at` now constrains every version observation in its logical record, including versions that omit that field. Validation does not fill missing metadata.
- Revision traversal carries the last known observation time across unknown intermediate versions. It rejects a later revision whose known time predates a known ancestor; equal times and unknown metadata remain allowed. Traversal follows predecessor links rather than lexical identifiers or input order.
- Added eight parameterized regression cases covering contradictory/consistent logical first-seen metadata, reordered input, and backwards/equal/forward/unknown timestamps across an unknown revision with nonchronological lexical IDs.
- Before the fix, the eight new cases produced three failures and five passes, reproducing both review findings. After the fix, the full suite passed: `343 passed in 3.37s` (291 inherited plus 52 Phase-IV cases).
- Scoped Ruff and strict mypy passed; the original synthetic review reproduced byte for byte; the wheel built successfully from a disposable staged-tree archive. Source preservation passed before and after the build for all 157 inherited files and the original Stage-0 contract.
- Ancestry thread `PRRT_kwDOT2PA1c6f3uUA` was checked against the actual feature branch: `git merge-base --is-ancestor` succeeds for both preregistration `46a049021d96b84725e2636c9d24e5d5de8c1d18` and implementation `5046fbcc24b4a00300ad33be97d37b92b7bfe135` at parent `50eafa63e0cd779ad6d7e0843993c99a4176e7c0`. The implementation's parent is the preregistration, whose parent is the frozen source. The branch retains the required chronology; integration must preserve it rather than squash it.
- The user's 335-test Mac evidence remains valid for its explicitly recorded commit. The 343-test result is agent-run evidence for this subsequent fix; current-head CI is the remote acceptance gate. Human review before integration and `BLOCKED_SOURCE_AUDIT` remain in force.

## 2026-09-07 — Human approval, integration, and next source-audit contract

- User explicitly authorized: "Integra y continua con el proceso".
- Merged PR #1 into `research/phase4-temporal-state` as `c6f07549ba733866809aa05156365611e2002b62`, preserving both parents and preregistration ancestry. The accepted feature head is `e502f892258df273d4207d606c176bcb039d4be1`; all four push/PR workflows passed and the three review threads were resolved before merge.
- Verified the merged tree and all 157 inherited files plus the original Stage-0 contract. Phase III remains frozen; human approval closes this ontology increment's integration gate only.
- Opened `feature/phase4-source-metadata-audit-v0` from the merge. Registered `DTRM_PHASE4_SOURCE_METADATA_AUDIT_V0.md` before its implementation or any live source query.
- The next operation is a bounded type/presence inventory of candidate metadata fields in `trumpMinMax.trumpNews`; no values or outcomes are returned. Live source access remains to be executed locally by the user. The inventory cannot authenticate historical availability or close Stage 1 by itself.

## 2026-09-07 — Source metadata inventory implementation and synthetic validation

- Registration commit: `c6bdb927f16aea1919b4c5c219c9c21dca544147`, before implementation. Added pure immutable counters/reporting, the fixed read aggregation, an optional local Mongo adapter, and a CLI with separate synthetic/live modes and no-overwrite behavior.
- Query scope is fixed at 19 candidate top-level fields, at most 1,000 records in ascending `_id` order, returning only BSON type/count aggregates. Missing/null remain distinct, input counts are reconciled, credentials and driver messages are excluded from output, and the client closes on failures.
- Added 32 synthetic/transport/CLI cases. Full suite: `375 passed in 3.23s` (343 prior plus 32 new). Ruff passed and strict mypy passed for eight source files. Tests exercise a fake transport, not an actual Mongo server.
- The synthetic metadata inventory reproduces byte for byte against `DTRM_PHASE4_SOURCE_METADATA_SYNTHETIC_V0.json`; the original ontology evidence also reproduces unchanged. Wheel build passed in a disposable staged-tree archive. All 157 inherited files and the original Stage-0 contract passed preservation before and after validation.
- Updated Phase-IV CI to cover the new code/tests and synthetic comparison. Added `docs/phase4/source-metadata-audit.md` with local execution instructions and precise limits of the counters. Current-head PR checks remain the authoritative remote gate.
- No live source query, source values, model fitting, sequence construction, MM1 run, outcome access, or scientific promotion occurred. The actual metadata report and source/decision-clock bindings remain pending; scientific status stays `BLOCKED_SOURCE_AUDIT`.

## 2026-09-07 — First user-supplied live metadata inventory

- The user executed the registered Mongo inventory locally and supplied its complete JSON plus terminal success and preservation output. Audit interval reported: `2026-09-07T18:34:59.820740+00:00` to `2026-09-07T18:35:00.580305+00:00`.
- Saved the JSON content as `DTRM_PHASE4_SOURCE_METADATA_LIVE_20260907T183459Z.json`. This is a transcription of the user-supplied report, not an independently retrieved database snapshot or a byte-authenticated copy of the original local file.
- Independently recomputed the normalized counters and fixed pipeline hashes: `21600f60d2609983062153e83c2056a3fbb15e6c8583c40f3646db96aff2f21a` and `b95f1ffbbfd8164d304756b3572ba5fcdf859509affb0f41bf9c977ca88ef3bb`; both match the supplied report. The terminal does not print the executed HEAD; query identity is corroborated by its matching pipeline digest.
- Source: `trumpMinMax.trumpNews`; 1,000 sampled documents. `_id` is `objectId`, `date` is `string`, and `matched_tickers` is `array` in all 1,000. Each of the other 16 registered top-level candidates is `missing` in all 1,000, including first-seen/version observation, version lineage, content digest, and link/mapping provenance fields.
- The returned `PASS_METADATA_COUNTERS_SCHEMA` establishes a successful local transport/protocol exercise and consistent counters. The user also reported `PASS_SOURCE_PRESERVATION` for all 157 inherited files and the original Stage-0 contract. Local dependency output reports PyMongo 4.17.0, python-dotenv 1.2.3, and dnspython 2.8.0.
- Interpretation is restricted to these exact paths in this bounded, nonrepresentative current-collection sample. It does not establish all-collection absence, nested/alternate schema absence, lack of upstream archives, date precision/timezone, empty ticker arrays, or historical point-in-time availability. `_id` is not an observation clock, and a string-valued `date` cannot substitute for authenticated version/link availability.
- `BLOCKED_SOURCE_AUDIT` remains necessary. The next permitted evidence step is read-only collector/writer and archive lineage inspection, followed by an explicit source/decision-clock binding. No sample expansion, new field mapping, historical imputation, fitting, or outcome access was introduced in response to these counters.
- Reviewed ancestry comment `PRRT_kwDOT2PA1c6f9oH7` against actual Git history: implementation `1c8f846b66c3277d16c4567494dd0cbf7d01497e` directly descends from preregistration `c6bdb927f16aea1919b4c5c219c9c21dca544147`; `git merge-base --is-ancestor` passes. The comment's squashed snapshot is not the feature head. Integration must preserve this existing ancestry.
- This evidence-only update preserves implementation and contracts. PR #2's current-head CI and human integration review remain the delivery gates; the first live inventory does not close the scientific source audit.

## 2026-09-07 — Source inventory integration and collector-audit registration

- User explicitly authorized: "integra y continua".
- Merged PR #2 into `research/phase4-temporal-state` as `ebe77c66ad74b3fc75791be10b502f6ab613b12d` using a merge commit. The accepted head `ff40e4db0a24fc692f96bcdd40a97aa5dde92e82` retains preregistration `c6bdb927f16aea1919b4c5c219c9c21dca544147` as an ancestor. Both post-merge workflows passed.
- `research/phase3-minmax-contract` remains pinned to `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`; all 157 inherited files and the original Stage-0 contract passed preservation after branching from the merge.
- Opened `feature/phase4-collector-lineage-audit-v0`. Registered `DTRM_PHASE4_COLLECTOR_LINEAGE_AUDIT_V0.md` before inspecting repository contents.
- Bound the static audit to `tech-com-UA00001/DTRM_Fund_Agent_API@badb20158890e9982c7806382cc3e151782af372` and `tech-com-UA00001/theresistance-back@7a8107e4451891535366acaf766348785ccc157b`. No runtime, database, endpoint, artifact, or outcome inspection is part of this cut.

## 2026-09-07 — Static collector-lineage audit implementation and evidence

- Registration commit `6d7b41424dc65d6234a98a916e494f42bc0ee62d` precedes repository-content inspection. Implementation commit: `5c2a1cbd3c189a30f584a591ac9f4de894ad2582`.
- Read the complete recursive trees at the two registered commits. `DTRM_Fund_Agent_API` tree `b5107d0ee17f2909e0b0c060a7d00d00bb91a567` returned 4,384 entries; `theresistance-back` tree `f295888372d9ef3c089cc24dd1e72e6b1f2c92cf` returned 235. Both reported non-truncated. Every cited file is bound to its Git blob SHA in `DTRM_PHASE4_COLLECTOR_LINEAGE_EVIDENCE_V0.json`.
- The visible collector writes provider date/current-time fallback, text, source, ticker matches, raw payload, and normally a dedupe key. It does not persist a distinct collection/first-seen/version-observed clock, content-version identity, predecessor, mapping version, or link-availability time. The best-effort unique-index setup and broad unkeyed insert fallback do not establish immutable revision lineage.
- Incremental collection begins the day after the maximum stored `date`, with no overlap. Static schedule and entrypoint evidence therefore cannot guarantee capture of late, revised, or later-same-day items. This is a code-path finding, not a claim about which historical workflows actually executed.
- The governed ranking path separately hashes the exact ordered news evidence used by a run, freezes two-day/five-day candidate files, and tests fail-closed append-only prefix recovery. This supports bounded ranking-time integrity when those artifacts exist; it does not repair missing source observation clocks or establish long-horizon archives. The daily artifact retention visible in code is 30 days.
- The inspected API dispatches workflows and retrieves parsed artifacts; its complete non-vendor source set adds no news provenance store. Static inspection cannot authenticate past deployment versions, run success, database state, or artifact survival.
- Added a typed immutable manifest parser and deterministic serializer, exact source/commit/tree/path/blob allowlists, registered finding/status bindings, report identity checks, credential-material rejection, and scientific-promotion guards. The manifest SHA-256 is `239559b068835544d87f4101e5011c694b2c4ba37253e66e327e3ced3e32a1d8`; report SHA-256 is `70ce5efe390872b9f794b52d4c7c05edacfb82722918f9ee78fc78d0ce23845d`.
- Added 31 mutation and boundary tests. Targeted suite: 31 passed. Full suite: 406 passed (375 prior plus 31 new). Scoped Ruff passed; strict mypy passed for ten Phase-IV source/experiment files; both existing synthetic reports reproduced byte for byte; the collector-lineage manifest/report validator passed with 12 findings.
- Built `dtrm_fund-0.1.0-py3-none-any.whl` from the staged tree in a disposable directory. The inherited license-metadata deprecation and disabled byte-compilation warnings remain non-blocking. Source preservation passed before and after all gates for all 157 inherited files and the original Stage-0 contract.
- No workflow log, artifact, live system, database, endpoint, outcome, target, score, return, history construction, model fit, or MM1 execution was accessed. Scientific status remains `BLOCKED_SOURCE_AUDIT`; `training_permitted=false` and `history_construction_permitted=false`.
- Next operation after current-head CI and human review: preregister a bounded read-only nested-raw/index/coverage audit and a distinct decision-clock feasibility addendum. A day-level experiment or prospective collector change is not authorized by this evidence increment.

## 2026-09-08 — Resume after approved PR #3 integration

- User approved PR #3, merged as `f5148f2f6787d3282c04a357e59d32ed3c515ba8`; both post-merge workflows passed. Actual remote implementation is `504ddb704bb94ebb75c33144370a65eefac712b3` (same tree as local-only `5c2a1cbd3c189a30f584a591ac9f4de894ad2582` recorded above). Remote evidence head is `f720f00aa55d9a801091a179539b67b9f07f1daa`. Registration remains an ancestor; review ancestry concern was resolved with local and GitHub compare evidence.
- User resumed work and requested unit, functional and regression validation without requiring their Mac; report results before integration. Phase III remains frozen.
- Opened `feature/phase4-source-feasibility-v0` from the approved merge. Registered `DTRM_PHASE4_SOURCE_FEASIBILITY_V0.md` before implementation/new live queries, including fixed nested paths, sample-only date-year diagnostics, sanitized index counters and a decision-clock non-promotion guard.
- Presence-only environment check: neither configured `MONGO_URI`/`db_password` nor a repo-root dotenv file is available here. No credential value was printed and no database connection attempted. Development and isolated synthetic-server testing may proceed; actual source validation remains pending configured access.

## 2026-09-08 — Source feasibility implementation and validation (PR #4)

- Preregistration `bcee8fb45c8ca8f1f40ae3c48049ea67928d4c24` precedes implementation `61e3302963e4743b9f6af846f2e76108b2b2de85`. PR #4 targets only `research/phase4-temporal-state`; no integration yet.
- Implemented fixed type counters for 17 nested/top-level metadata paths, three sample-only date-class/year histograms, and sanitized index-definition counters. Client/cursors close on failures; errors and reports contain no credential values. Full source census, historical availability, observed revisions and point-in-time ticker linkage remain unauthenticated.
- Agent-run validation: 46 new unit/functional tests; full suite 452 passed, with three real-server tests explicitly skipped outside dedicated CI. Ruff passed; strict mypy passed for 13 files. Three synthetic reports reproduced byte for byte; prior lineage validator passed. Disposable staged-tree wheel build succeeded. All 157 inherited files and original Phase-IV contract passed preservation before/after gates.
- Independent execution environment (not an independent scientific review): CI Mongo 7.0.14 service using only synthetic fixture documents. Job `102036979934` logged `3 passed in 0.20s`; tests exercise actual pipeline/CLI equivalence, missing/null/numeric/array/date classes, timezone year rollover, nested arrays, 1000-record cap and partial-index rejection. No production credentials are used in CI.
- Implementation-head PR workflows `34218860339` (Tests) and `34218860322` (Phase IV gates), and push workflows `34218855726`/`34218855745`, all passed. Detailed evidence: `DTRM_PHASE4_SOURCE_FEASIBILITY_VALIDATION_V0.json`. Evidence-only commits must pass current-head CI again.
- Actual source entrypoint returned `MISSING_LOCAL_CREDENTIALS` before importing a driver or connecting, and created no successful report. The env presence check did not expose values. No cross-project credential search, secret extraction, production queries, source writes, outcomes, fits, sequence construction or MM1 execution occurred.
- User-local validation is not required for this development increment. Actual Mongo audit remains pending credentials configured in the executing environment; a green synthetic integration test is not a production-source audit. `BLOCKED_SOURCE_AUDIT` stays active and the later decision-clock addendum is not approved by these results.

## 2026-09-08 — PR #4 integration and authenticated live-report bytes

- The user declared PR #4 locally validated and explicitly authorized a merge
  commit. Head `08d8669996592a30df875b64f3aea429a5813e56` was unchanged,
  mergeable, free of review comments and green before integration. PR #4 was
  merged as `350a75ca9e2ab8ea0dc1e3844be2c4bb25f13232`, retaining the
  integration parent and exact feature parent. Both post-merge workflows passed;
  all 157 inherited files and the original contract passed preservation.
- The user then supplied the complete sanitized live feasibility report and
  SHA-256 `0c0c633cd7eb9fef439788db894795f02edcfb10a844eb3f192a1c4b5d7d2995`.
  Repository reconstruction matches that digest byte for byte. The fixed
  pipeline and normalized evidence hashes independently recompute to the exact
  values stored in the report. No credential-bearing content is present.
- The 1,000-record nonrepresentative sample contains naive publication/date
  strings and current URL variants, but none of the registered observation,
  revision, content-vintage or mapping/link-availability provenance fields.
  `dedupe_key` is absent throughout despite a current qualifying sparse unique
  index. Current index definitions do not establish historical enforcement.
- Scientific decision: the current collection alone cannot authenticate which
  exact content/ticker vintage the machine knew at a historical cutoff.
  Retrospective authentic `as-of` history, model fitting, outcomes and MM1 runs
  remain prohibited. This is a negative feasibility result, not a test of the
  representation hypothesis. See
  `DTRM_PHASE4_SOURCE_FEASIBILITY_LIVE_INTERPRETATION_V0.md`.
- Next scientific fork, fixed without outcomes: first permit one separately
  preregistered salvage audit of `ObjectId` insertion semantics, append-only
  writer/runtime evidence, backfill lag and repeated-URL vintages. `ObjectId`
  remains inadmissible unless that evidence supports it. If the gate fails,
  proceed to prospective immutable event collection and bind its decision
  clock/control dependencies before Stage 2. A weaker publication-time
  retrospective estimand requires explicit approval and cannot be substituted.
- Added a regression assertion pinning the live report bytes, both internal
  digests, execution mode and all scientific blocks. Agent validation: 47
  targeted tests and full suite 453 passed with three expected dedicated-CI
  skips; Ruff, strict mypy, three synthetic reproductions, lineage validator,
  disposable wheel build and pre/post source preservation all passed. Remote
  current-head CI and human review remain the integration gates.

## 2026-09-09 — Retrospective-salvage live-adapter registration

- PR #8 was integrated by merge commit
  `a8bf5353f4fa46ad59d66faa980a1004276f97a8` only after its exact head passed
  both workflows and both review findings were corrected and resolved.
- Opened
  `feature/phase4-retrospective-salvage-live-adapter-contract-v0` from that
  merge and registered
  `DTRM_PHASE4_RETROSPECTIVE_SALVAGE_LIVE_ADAPTER_V0.md` before implementation
  or live execution.
- The addendum fixes the user-local configuration, read-only Mongo transport,
  exact streamed census, aggregate-only live report, disposable-CI boundary
  and required tests. It accepts no writer-state override: existing static
  evidence leaves material runtime fields unknown, so adapter v0 cannot emit a
  candidate result.
- No source configuration, credential, database, outcome, history, model or
  MM1 execution was accessed. `BLOCKED_SOURCE_AUDIT`, no history construction
  and no training remain in force. The next gate is validation and human review
  of this registration, not implementation.
- Remote registration `13625046e8b258f085fab59966a31937786a5eec`
  preserves the contract at SHA-256
  `f98ce5e5d22810618571725d1645806729da358ff7622a7c47150cdc3e5cfcad`.
  Agent validation passed 534 tests with three expected disposable-CI skips,
  scoped Ruff, strict mypy, four synthetic reproductions, the 12-finding
  lineage validator, disposable wheel build and pre/post preservation of all
  157 inherited files. Current-head CI and human review remain pending.

## 2026-09-09 — Retrospective-salvage live adapter implemented

- After PR #9 merge `d11b9cff62e656cb64664d126e48dca9381ffc7e`, PR #10
  implements the registered read-only adapter, immutable aggregate report,
  explicit configuration boundary and exclusive atomic report publication.
- Final corrected implementation head `ff5024c4cc1808d535339e4b362c697a1e892718`
  passed both CI workflows: 579 regression tests, six dedicated synthetic-Mongo functional
  tests, scoped quality checks, four synthetic reproductions, lineage check,
  wheel build and preservation of all 157 inherited files. The six ordinary
  test skips are exercised by the dedicated Mongo job.
- Local adapter tests: 45 passed; all Phase IV tests pass 288 with six
  dedicated-Mongo skips. Full local regression is blocked by native
  XGBoost loading; it is not reported as a local pass. The clean CI regression
  is independently successful. Full details and tested commit/tree are in
  the live-adapter progress and implementation-validation records.
- No production configuration, secret or source connection was accessed.
  `BLOCKED_SOURCE_AUDIT` is unchanged. Engineering success does not authenticate
  observation times or authorize history, outcomes or training.
- Next gate: current-head checks and human review of PR #10, followed by
  explicit merge authorization. Only then should the operator perform the
  documented local live audit and share the sanitized aggregate and hash.
- Review-driven corrections preserve legacy BSON `undefined` and `symbol`
  wire types and enforce ObjectId cross-counter reconciliation. The standalone
  Mongo 7.0.14 CI service passed the explicit majority-read path, so no
  unregistered replica-set change was introduced.
- Current-head rereview also closed nested legacy BSON dedupe hashing and the
  post-publication cleanup edge case. All five review threads are answered and
  resolved; no raw values or scientific gates were changed.
- Final rereview closed stdout failure after publication. All six review
  threads are now answered and resolved, and the published aggregate—not a
  best-effort console notification—is the authoritative completion artifact.

## 2026-09-10 — Retrospective-salvage live evidence

- PR #10 was integrated by authorized merge commit
  `2b0dbeac662f2c0bd51db24b9045a600be83d0da`. The operator then ran the
  integrated read-only adapter and supplied the sanitized aggregate plus SHA.
- Canonical report SHA-256
  `e061be9a0dea615d87178903d87d997564befc9062341e0be0b096ba31d650cd`
  covers 63,873 rows with zero count/cursor delta. Canonical bytes, pipeline,
  writer-manifest, evidence hash, contract identity and reconciliation all
  validate; no sensitive pattern was reported or observed in the transfer.
- The fixed decision is `RETROSPECTIVE_PROXY_PARTIAL` /
  `BLOCKED_SOURCE_AUDIT`. All rows have genuine BSON ObjectIds, provider days,
  text, URLs and nonempty outer ticker arrays. However, 29.33% have an ObjectId
  generation day 31–365 days after provider day, 46.71% lack `dedupe_key`, one
  repeated URL group has multiple content digests, all three audited provider-ID
  paths are absent, and 405,565 ticker elements violate the registered
  string-element assumption. The day delta does not authenticate insertion or
  prove backfill, and unaudited provider-ID paths remain unknown.
- Database structure still cannot authenticate relevant-writer coverage,
  deployed intervals, later mutation, client clock, runtime immutability or
  exclusive write authority. The report does not authorize history,
  representation learning, outcomes, training, Transformer or MM1.
- Scientific fork: the confirmatory Phase-IV path must be prospective and
  immutable. An optional retrospective exploratory path requires a separate
  outcome-blind preregistration for ticker element shape, writer/runtime
  evidence and conservative ObjectId chronology rules before any history is
  built. See the live report, intake validation and interpretation records.
- PR #11 corrected the interpretation to generation-day—not authenticated
  insertion—semantics and limited the provider-ID conclusion to the three
  audited paths. Corrected-head CI passed 580 tests, six disposable-Mongo
  tests, scoped quality gates, reproductions, lineage, wheel and preservation;
  both review findings are resolved.
