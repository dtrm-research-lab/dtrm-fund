# G2.7 — Predeclare A2 threshold sensitivity under the original weighted validation P10 source

**Case**: ICOMPUTING-D-26-01069 · **Date**: 2026-10-27
**Gate**: G2 ACTIVE; G3 BLOCKED.
**Reviewer demands**: R1-03 and R2-02.

## G2.6 operator result — PASS, source only

The original V0/P10 validation source-binding preflight completed
`G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED`.

Operator terminal evidence:
- Source commit: `c7502a690162459cdfb3413573e3133c42efb126`.
- Original validation q25:
  `-0.16665692627429962` reproduced from earlier
  12/12 historic V0 numeric replay and source route.
- **9/9 original source-code method tokens verified**:
  original weighted empirical quantile, array sort,
  cumulative legacy news weights, `side='left'`
  first cumulative crossing, 19,880 original validation
  rows, P10 iteration 18 and calibration offset.
- Eight old-cohort input/anchor hashes referenced by G2.6.
- G2.5 original metadata report SHA256:
  `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.
- G2.6 did not load targets, Pickles, prices or run a model.
  Neither alternative q15/q35 values nor new results exist.

## Fixed A2 scientific design (draft committed, NOT yet frozen)

Machine-readable protocol:
`G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json`.
This fixes before any new G3 analysis:
- A **single unchanged, reconstructed historical P10 XGBoost**
  predictive quantile model, best iteration 18, original
  calibration offset `-0.06494169682264328`.
- Three *validation-distribution* weighted cutoffs
  `q∈{0.15,0.25,0.35}` of calibrated P10, using 19,880
  ORIGINAL V0 validation predictions and legacy news
  weights. These are NOT three newly trained predictive
  P15/P25/P35 quantile models.
- Original first-cumulative-weight crossing algorithm
  `np.argsort / np.cumsum / np.searchsorted(side='left')`.
  Original q25 must reproduce frozen veto
  `-0.16665692627429962` (absolute tolerance 1e-6)
  or stop; never adjust threshold using V2/V3/V4 labels.
- Original old consumed event/ticker pair cohorts V2 (4,449
  rows; K444), V3 (2,827; K282), V4 (40,320; K4032).
  All **3×3=9** cells must report acceptance, full-K
  feasibility, actual selected count, per-arm historical
  excess-beta mean/hit rate and candidate-minus-baseline.
  Infeasible fill => `INFEASIBLE`, not reduced K.
- Baseline frozen ex-ante ranker iteration 10; candidate
  same baseline ordering and veto. Existing old outcomes,
  not independent new observations.
- Prespecified original news-id and ticker-cluster 10,000
  replicate resampling seeds 20260821/20260822 and 95%
  percentile CI. If any replicate lacks full-K, report
  count and WITHHOLD its interval until a separately fixed
  treatment is specified.
- All results, including worse thresholds and lost
  feasibility, are published. No winner selection,
  retraining, price leakage, pooled independence test,
  promotion or new absolute trading P&L inference.

The original G1.2k dossier SHA remains
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
The separate original V1 date selection SHA remains
`388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.

## G2.7 operator preflight (JSON ONLY, never financial data)

Run from `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_a2_protocol_preflight.py" \
  -o "$AUDIT/ic_g2_a2_protocol_preflight.py"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  -o "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json"

python3 -m py_compile "$AUDIT/ic_g2_a2_protocol_preflight.py"

python3 "$AUDIT/ic_g2_a2_protocol_preflight.py" \
  --plan "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json"
```

Expected metadata-only status:
`G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN`.

**This status DOES NOT mean G2 is frozen, G3 is authorized,
q15/q35 have been calculated, or that old-cohort performance
is statistically confirmatory.**

## Remaining G2 tasks (G2→G3 gate)

1. Confirm A2 actual validation array generation can be
   executed with exactly source/hash-bound old inputs
   *after* G2 freeze. Do not treat a G2 source-token test
   as mathematical parity of uncomputed q15/q35 values.
2. Record fair/as-of feasibility for **A3** traditional
   volatility control, with same original ranking and
   K capacity. If source lineage lacking, mark justified
   `NOT_EXECUTABLE` (not zero-effect).
3. Define **A4** economic interpretability and no-action
   concept without claiming realized P&L; any historical
   trade simulation needs fixed as-of fills/capital/fees.
4. Freeze **A6** K-grid implementation or disclose
   limitation. Any prior V2/V3/V4 exploratory analysis
   must retain unfavorable results and explicit
   overlapping-forward-window uncertainty.
5. Inspect verified 22-item reviewer map, run G2
   freeze preflight and adversarial review, then
   SHA-seal final G2 decision/allowed G3 work.
6. G1.3 genuinely independent new holdout remains
   blocked due lack of source-and-date-verified
   eligible event data in searched roots.

**Status:** G2.7 PREPARED / OPERATOR NOT RUN.

## 2026-10-27 operator G2.7 PASS: report summary

The operator executed the G2.7 **metadata-only**
A2 source/method preflight, yielding:
`G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN`.

- 8 original historic input SHA references passed.
- Weighted P10 validation cutoff grid fixed q15/q25/q35.
- 3 consumed V2/V3/V4 cohorts × 3 grid positions = 9
  **post-outcome exploratory** comparison cells.
- G2.6 binding SHA256
  `1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`.
- Preanalysis plan local SHA256
  `5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8`.
- Report:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json`.
  Its own SHA256 was not yet shared.

This operator outcome supersedes earlier 'NOT RUN'
text in the original runbook above. No q15/q35
values or financial outcome comparisons calculated.
Full G2 remains NOT FROZEN and G3 remains BLOCKED;
next A3 source-only triage:
`G2_8_A3_PRICE_SOURCE_TRIAGE.md`.
