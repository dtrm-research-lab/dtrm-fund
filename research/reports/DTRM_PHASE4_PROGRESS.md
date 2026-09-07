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
