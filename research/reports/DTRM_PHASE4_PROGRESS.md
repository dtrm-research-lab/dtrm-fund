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
