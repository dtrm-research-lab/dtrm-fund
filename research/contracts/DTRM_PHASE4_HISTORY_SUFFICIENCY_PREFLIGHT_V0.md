# Phase IV — History sufficiency preflight v0

**Registered 2026-10-14, before implementation.** Status: **synthetic-only engineering contract**, not G5 scientific preregistration. Parent: \`DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md\`; [Phase IV closeout issue #34](https://github.com/dtrm-research-lab/dtrm-fund/issues/34). Additive Phase IV; never edit frozen Phase III/MM1.

## Prior source evidence and scientific implications

The 2026-09-08 source feasibility audit sampled 1,000 documents: no authenticated observation/version/link availability metadata was identified at inspected paths. The 2026-09-10 retrospective census counted **63,873 current documents** and found ObjectId-generation chronology, but did not establish an authenticated \`as-of\` observation clock, immutable vintage archive, or historically available ticker links. The accepted classification remains \`RETROSPECTIVE_PROXY_PARTIAL / BLOCKED_SOURCE_AUDIT\`. These 63,873 documents are **not** 63,873 admissible histories or independent training sequences. The prospective 14-day × four-slot / 56-slot adequacy requirement measures collection-process reliability, not history sufficiency or maturation of 60-calendar-day forward targets (+ inherited five-day price tolerance).

## Scientific question and cutoff boundary

The prospective research estimand remains the realized paired Top-K \`Delta(T,C0)\` in frozen Phase-II target units. The **same frozen MM1 mapping** is used for C0 (inherited control), S (matched snapshot), B (simple-history baseline), T (sequential representation), and O (order ablation). No fitting, MM1 execution, outcome access, history reconstruction or promotion is allowed by this preflight.

In a future separately registered, source-authenticated aggregation, each common candidate \`(news_id,ticker,decision_cutoff)\` will have a count of **distinct earlier eligible logical news events** with the exact content vintage and asset-link mapping demonstrably available **strictly before** the registered cutoff. Current event is not its own preceding history. Multiple revisions collapse to one logical event; unknown version or asset-link availability is **UNKNOWN**, not zero. Provider publication time, current audit time and Mongo ObjectId creation must not be relabelled as independently observed availability. Shared events, mapping versions, ticker/universe history, ties, left truncation, decision clocks, and baseline beta/price inputs remain separate gate requirements.

### Fixed *descriptive* bins

For a future externally authenticated count, these bins are mutually exclusive and exhaustive:

- \`unknown_availability\`: precise eligible historical count cannot be authenticated;
- \`zero\`: authenticated history count is 0;
- \`one_to_four\`: authenticated count is 1–4;
- \`five_to_nineteen\`: authenticated count is 5–19;
- \`twenty_plus\`: authenticated count >=20.

These are **display bins only**, **not** thresholds for model adequacy, row exclusion, test selection, cohort dates or acceptance. Neither unknowns nor short histories can be deleted after target observation. Any future scientific minimum sample depth, sequence lengths, windows and statistical power criteria must be specified outcome-blind before model fitting. No current data are classified by these bins in this increment.

## Preregistered, deterministic synthetic-only graph

The only accepted input is an explicit synthetic fixture, never raw events or live collection data:

\`\`\`json
{
  "schema_version": "dtrm.phase4.history_sufficiency_fixture.v0",
  "dataset_role": "synthetic",
  "cohorts": [{
    "cohort_tag": "case_a",
    "candidate_count": 8,
    "bins": {"unknown_availability": 2, "zero": 1,
             "one_to_four": 2, "five_to_nineteen": 2, "twenty_plus": 1}
  }]
}
\`\`\`

**Graph:**
1. Schema node: exact key sets at all three levels, role \`synthetic\` only; reject malformed identifiers. The tag pattern is \`[a-z][a-z0-9_]{0,31}\`; no timestamps, tickers, prices, texts, outcomes or credentials can enter the fixture.
2. Counter node: 1–64 uniquely tagged cohorts, per-cohort candidate count 1–1,000,000 (integer only), each fixed bin a nonnegative integer (reject bool/float); each bin sum must equal its candidate count; grand count ≤1,000,000.
3. Canonical report node: sorted cohorts and fixed key sets, SHA-256 of normalized canonical synthetic input, aggregate counters and the permanent flags \`engineering_status=PASS_SYNTHETIC_HISTORY_COUNTERS\`, \`scientific_status=BLOCKED_SOURCE_AUDIT\`, \`source_authenticated=false\`, \`history_construction_permitted=false\`, \`training_permitted=false\`, \`outcome_access_permitted=false\`, \`scientific_counting_permitted=false\`. A synthetic PASS cannot be promoted to an authenticated-source result.
4. Local CLI boundary: explicit fixture file, **new** output file only; refuse existing or symlink output even when dangling, exclusive creation, fixed sanitized error codes. No Mongo, S3, AWS, FMP, secrets, network or protected outcomes.

**Acceptance before PR:** correct synthetic sums and reproducibility under cohort-order permutation; unknown distinct from zero; fail closed on missing/extra fields, real-role input, invalid/doubled tags, invalid counters and overflow; CLI refuses overwrite, symlink and malformed fixtures; scoped tests and source preservation. Contract commit must precede implementation commit in ancestry, with current-head CI and human review before any merge.

## G5 and later gates remain closed

G5 requires separately preregistered and independently verified actual source availability, immutable vintages, mapping/universe, matched cutoff and baseline inputs; a count-by-cutoff coverage acquisition protocol; explicit exposure ledger, TRAIN/VALID/CALIBRATION/untouched test partitioning and purging/embargo for 60+5-day forward outcomes; matched C0/S/B/T/O recipes and uncertainty plan. A separate, noncounting provider provenance diagnostic and prospective campaign (G2/G3/G4) must pass first. This increment **does not** set training eligibility or scientific outcomes and must not alter MM1 or humanclause.com.