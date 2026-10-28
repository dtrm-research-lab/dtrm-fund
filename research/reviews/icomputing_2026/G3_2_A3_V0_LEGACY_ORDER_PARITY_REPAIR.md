# G3.2 A3 — V0 VALID row-order fail-closed incident and original legacy-order repair

**Case:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Scientific gate:** VALID-only P10-to-stock-volatility cutoff; NO test outcomes.

## Failed run — preserve it as negative audit evidence

The operator ran `ic_g3_2_a3_valid_only_cutoff.py`
using code commit
`ec8fd7558e8c4e5de0ac9fa7fbc1f7e3adad18a6`
after 51 local synthetic/static tests:

`Ran 51 tests in 0.050s — OK`

Then the *actual* original VALID-only cutoff
stopped safely:

`G3.2 A3 VALID-ONLY HALTED: RuntimeError Original P10 VALID rows do not match model-row order; no silent join`

**No risk threshold calculated; no saved result JSON;
no V2/V3/V4 target ever accessed.** Previous
numeric close/source quality remains
`G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED`,
with local report SHA256
`91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a`.

## Original frozen source investigation and root cause

The original Phase II source at immutable historical
`c7502a690162459cdfb3413573e3133c42efb126`:

- `research/experiments/run_probabilistic_xgb_v0.py`,
  `load_ordered_model_rows()` calls
  `order_selected_legacy_rows(full_rows['ticker'],
  full_rows['date_dt'], full_keys, selected_keys)`;
  it then makes `ordered_rows = model_rows.iloc[order].reset_index(drop=True)`.
  This is the order in which `build_exante_feature_matrix`
  constructs the reconstructed XGBoost V0 VALID
  prediction vector.
- `src/dtrm/legacy_model_rows.py` invokes
  `legacy_model_row_order` over the ORIGINAL
  entire pre-filter dataset then retains
  selected `(news_id,ticker)` rows.
- `src/dtrm/legacy_row_order.py` constructs
  a ticker and date ordered index, then
  separately quicksorts ticker-date blocks,
  preserving the old row-order tie behavior.

The first A3 validator independently opened the saved
`legacy_model_rows_2026-05-01.pkl` file and applied
`split=='valid'` **without the same historical
row-order transform**. It then incorrectly
required native saved `news_id` to be
positionally identical to reconstructed
P10 model-output `news_id`.
This is a bug in the new A3 adapter's
identity alignment, **not evidence that
the original XGBoost scores, model, q25,
raw archive identities or price cache
were necessarily incorrect**. We must
still check original key sets and UTC dates
in live original data before declaring
successful recovery.

## Minimal science-neutral correction

Current corrected candidate:

`ic_g3_2_a3_valid_only_cutoff.py`

1. Before any model use, requires original
   G3.2 34-test/66,476-pair quality report
   exact SHA and all five frozen original
   G2 evidence report hashes.
2. Uses existing frozen original
   `reconstruct_valid_p10_only` and its
   unchanged 390-feature, original P10
   validation reconstruction.
3. Independently reconstructs original
   `order_selected_legacy_rows` using the
   saved `legacy_pairs_enriched_2025-01-01_2026-05-01.pkl`
   and original V0 selected model rows.
   The original G1 dossier/commit/source
   proofs protect the same input lineage.
4. Requires exact bijection of all **19,880**
   source-native and reconstructed-original
   VALID **`(news_id,ticker)`** tuples:
   no duplicate, missing or extra pair.
   Checks **event UTC datetime equality**
   per tuple, not only the calendar date.
5. Requires each newly reconstructed P10
   prediction vector `news_id` to match
   the ordered original `news_id` array
   before remapping; never maps
   scores by `news_id` alone (one
   news story may have multiple tickers).
6. Only then uses an explicit bijective
   positional index map to place P10
   predictions in native original
   source-row order used for price
   volatility. Logs only aggregate
   counts, equality booleans and a
   nonidentifying remapped-position count.
7. Original q25 `-0.16665692627429962`
   and q15/q25/q35 VALID source
   thresholds remain under original
   1e-12 replay gates; no new
   model weights, threshold optimization,
   validation membership, score fit,
   price timestamp or source bytes changed.
8. Only after that original
   identity check can weighted
   `P10 admitted` versus
   `volatility <= calibration cutoff`
   be measured on the V0 VALID
   full 19,880 common quality-eligible rows.

New negative synthetic tests for:
permutation of legacy ordered V0 rows,
nonunique `news_id` attached to
different tickers, missing/extra/duplicate
composite pair, mismatch of original UTC
date, and incorrect P10 ordered news vector.
**No outcome-based tuning, no comparison
to V2/V3/V4 forward targets.**

## Operator next steps — code/test fix NOT yet locally verified

The correct next consented step is:
run **56 tests** from one pinned Git SHA:
22 original core + 12 original
G3.2 numeric source + 5 original V0
P10 VALID source + **17** revised
V0 A3 cutoff/identity tests.
If any FAIL, stop and repair
only the scientific implementation.
Then, separately authorized, rerun
V0 source-only cutoff with a DIFFERENT
output pathname, refusing to overwrite
any prior evidence. Verify aggregate
key bijection, native/order mismatch
count, original frozen q25 and
P10-weighted/veto risk cutoff.

**Original provider-price acquisition
vintage is still unverified** even if
all rows align. No prospective
point-in-time claim, no new 60d
holdout and no A3 outcome comparison
is authorized by this report.
