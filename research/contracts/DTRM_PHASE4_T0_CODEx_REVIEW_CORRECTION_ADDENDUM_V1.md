# Phase IV — Codex P1/P2 response for T0 source-clock synthetic preflight

**2026-10-16; before correction code; design-only.** This amends the synthetic implementation of `DTRM_PHASE4_PER_ASSET_PROSPECTIVE_COVERAGE_AND_CAPTURE_CLOCK_V0.md` and `DTRM_PHASE4_T0_COLD_START_OBSERVATION_ADDENDUM_V0.md`; does not change Phase III/MM1, G5 prerequisites or scientific admission of real source evidence.

Exact-head Codex review on `9315da251b1e25c0b7c735543a2417e84ee6811c` identified: (P1) the proposed T0 field set omitted `ledger_committed_at` from the eligibility inequality; (P1) a caller-flagged unauthenticated sighting could still emit positive synthetic counts and ages; (P2) the legacy-link synthetic projection lacked the explicit `model_fitting_permitted=false` flag. These are genuine contract violations, not disagreements to waive.

**Fixed semantics to be implemented, with negative tests before review:**

- Add `ledger_committed_at: datetime | None` to the immutable synthetic sighting, independently distinct from `version_observed_at` and `linked_at`. Structural eligibility requires all three UTC-aware clocks and `max(version_observed_at,linked_at,ledger_committed_at)<cutoff`; equality is `UNRESOLVED_CUTOFF_TIE`, missing is explicit `UNKNOWN_COMMIT_CLOCK`. A commit earlier than either observation is `UNRESOLVED_LEDGER_ORDER`, never a positive age.
- If `source_provenance_supported` or `mapping_provenance_supported` is false, the sighting is UNKNOWN and must not contribute to structural event counts, per-role totals or positive age. These caller flags are never independent provenance proof even when true. If another sighting in that candidate has unknown authority, the category remains UNKNOWN (no silent dropping), as required for prospective full-denominator science.
- Age is calculated conservatively from the **latest** of three clocks, not news publication, schedule target or alleged first original link creation. An uncommitted T0 snapshot is never eligible at T0+1 second merely because the content was read by then.
- The synthetic legacy `ticker`/`match_type` projection explicitly outputs `model_fitting_permitted=false` in addition to `temporal_state_training_permitted=false`. No `match_type`→confidence inference.
- Add adversarial tests for missing commit, commit at cutoff, commit after cutoff, commit-before-sighting, untrusted no ages even with otherwise eligible clocks, and T0 capture at T0 with commit later. Keep all proof/trust/model/production flags hardcoded FALSE.

No live Mongo/AWS/source reads, outputs, campaign activation, overwrite of source-vintage or fitting are authorized by these corrections.
