# G1.2b — HDPG frozen 40,320-row prediction parity

Manuscript: ICOMPUTING-D-26-01069. Date: 2026-10-27.

## Completed reconstruction: operator-reported
Operator environment: numpy 1.26.4; pandas 2.2.2; xgboost 3.0.2;
sentence-transformers 2.6.1. Re-ran historical pinned training on the
original Mac from Git commit `c7502a690162459cdfb3413573e3133c42efb126`.

Output: `G1.2: HISTORICAL_AGGREGATE_PARITY_ONLY` with 12/12 PASS:
- 390 features
- best ex-ante ranker iteration 6, RMSE matched
- selected Top-K iteration 10, VALID Top-K mean/hit matched
- quantiles P10/P50/P90 best iterations 18/19/0 matched
- P10 best pinball matched
- VALID P10 calibration offset -0.06494169682264328 matched
- frozen V2/V4 veto threshold -0.16665692627429962 matched

Outputs stay `$HOME/dtrm-ic-audit/g1-reconstruction/reconstructed_UNAPPROVED`
until strict rowwise parity and order provenance are established. No
holdout newly inspected.

## Why a second gate
Metrics parity is weaker than individual prediction parity.
The V1 2026-05-02 to 2026-06-06 original 40,320-row feature matrix
and signal files have independent historical SHA256 commitments in
`research/contracts/DTRM_XGB_PROBABILISTIC_V4.yaml`.

- V1 stage used **strict calibrated P10 > 0** as original admission,
  with 0/40,320 passing.
- V4 replay of the same calendar cohort used the **relative P25 threshold**
  -0.16665692627429962, with 23,348/40,320 passing.
- The parity checker explicitly distinguishes both decisions and
  key-joins V1 and V4 signals on `(news_id, ticker)`.
- Original V4 signal artifact lacks an independent frozen historical
  SHA commitment in the V4 contract; it is guarded by the **operator's
  original discovery manifest SHA**, which is weaker evidence.
- The V1 original features .npy do not carry their own pair IDs.
  Numeric match and V1/V4 key linkage are necessary but do not
  independently establish original feature row construction provenance.
- Only supported, **explicitly labeled numeric P10 columns** are used
  for numeric value parity. An ambiguous `p10_prediction` is flagged,
  not guessed to be raw or calibrated.

## Command
Run locally from any directory. No need to retrain:

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_row_parity.py" \
  -o "$AUDIT/ic_g1_row_parity.py"

python3 -m py_compile "$AUDIT/ic_g1_row_parity.py"

python3 "$AUDIT/ic_g1_row_parity.py" \
  --search-root "$HOME" \
  --discovery-manifest "$AUDIT/IC_G0_discovery_manifest.json" \
  --rebuild-report "$AUDIT/g1-reconstruction/IC_G1_2_rebuild.json" \
  --models-dir "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_row_parity.json" \
  --trust-original-pickles
```

The original V1 and V4 signals, plus V1 features, are read only.
No outcomes/labels or raw market returns are loaded in this stage.
Reports expose aggregate deviations and column *names*, not individual
scores/news IDs. Do not upload Pickles, .npy or booster models.

## Gate outcomes
- `HISTORICAL_ROW_PARITY_FAIL`: stop; diagnose hash, row order,
  feature construction, sample identity and version differences; NO tuning.
- `PARTIAL_BASELINE_AND_P10_VETO_PARITY_ONLY`: ranker numeric values and
  both historic veto decisions match, but no unambiguous numeric P10
  stored column found. Must continue provenance investigation.
- `HISTORICAL_NUMERIC_PARITY_PASS_PROVENANCE_PENDING`: ranker numeric
  and numeric P10 predictions, plus V1 and V4 veto rules match.
  Still requires independent feature-to-signal pair-order corroboration.
- Never promote reconstructed weights to `frozen_HDPG` solely from this step.
- Independent temporal cohort, new news ingest and later price maturity remain open.
