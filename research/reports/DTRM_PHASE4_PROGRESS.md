# Phase IV progress ledger

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
