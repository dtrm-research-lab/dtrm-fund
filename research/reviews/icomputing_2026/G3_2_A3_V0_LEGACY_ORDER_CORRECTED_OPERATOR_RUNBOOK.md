# G3.2 A3 — corrected original V0 legacy order, exact pair mapping, 56 tests, VALID-only rerun

**Date:** 2026-10-28  
**Editor:** ICOMPUTING-D-26-01069  
**Original frozen source:** `c7502a690162459cdfb3413573e3133c42efb126`  
**Prior original quality report SHA:** `91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a`  
**New code:** `ic_g3_2_a3_valid_only_cutoff.py` at SHA pinned below.
**Scientific status:** source bugfix prepared; actual operator rerun PENDING.

## Why prior A3 validation source attempt stopped

Original operator executed 51/51 source/synthetic
tests PASS at previously tested
`ec8fd7558e8c4e5de0ac9fa7fbc1f7e3adad18a6`,
but actual V0 cutoff refused:

`G3.2 A3 VALID-ONLY HALTED: RuntimeError Original P10 VALID rows do not match model-row order; no silent join`

Original XGBoost source at
`research/experiments/run_probabilistic_xgb_v0.py`
reorders `model_rows` with
`order_selected_legacy_rows()` before
feature reconstruction. The original saved
training row file read directly by the
new A3 cutoff program retains a different
archive order; direct per-position comparison
is not a valid historical identity assertion.

This **does not** justify ignoring the mismatch.
The repaired A3-only wrapper uses original
frozen sorter on the original full/selected
rows, then requires exact 19,880
`(news_id,ticker)` pair-key bijection and
UTC date agreement before assigning
the already-computed P10 predictions
to original archived validation rows.
Original P10 q25 threshold and source
membership remain fixed, and no old
V2/V3/V4 targets are accessed.

## Step 1 — 56 isolated source/synthetic tests

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="5309886f3eb3caf2e2c05ebbb6aa3a01730e444b"
ROOT="research/reviews/icomputing_2026"

git -C "$REPO" fetch origin research/ic-major-revision-2026
git -C "$REPO" cat-file -e "$COMMIT^{commit}"

for file in \
  ic_g2_g3_exploratory_core.py \
  test_ic_g2_g3_exploratory_core.py \
  ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py \
  ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_1_a2_validation_only_source.py \
  ic_g3_2_a3_valid_only_cutoff.py \
  test_ic_g3_2_a3_valid_only_cutoff.py
do
  git -C "$REPO" show "$COMMIT:$ROOT/$file" > "$AUDIT/$file"
done

cd "$AUDIT"
python3 -m unittest \
  test_ic_g2_g3_exploratory_core.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_2_a3_valid_only_cutoff.py -v

printf '%s\n' "$COMMIT" \
  > "$AUDIT/g1-reconstruction/IC_G3_2_A3_VALID_LEGACY_ORDER_CODE_COMMIT.txt"
echo "REVIEWED_COMMIT=$COMMIT"
BASH
```

**Expected only if real operator-run tests all succeed:**
`Ran 56 tests ... OK`
(22 core + 12 price numeric + 5 V0 P10 + 17
A3 V0 composite key-order tests).

## Step 2 — separately consented original VALID-only replay

All input paths are the same source evidence as before,
apart from a distinct output filename. This invokes
trusted original local Pickle deserialization and
original V0 P10 model source reconstruction
**ONLY AFTER** SHA checks. Pickle loading can
execute code. Use only original trusted local
archives. No original V2/V3/V4 target data are read.
The risk cutoff and any repeated V0 P10 score are
**VALIDATION-only** calculations.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="$(cat "$AUDIT/g1-reconstruction/IC_G3_2_A3_VALID_LEGACY_ORDER_CODE_COMMIT.txt")"
OUT="$AUDIT/g1-reconstruction/IC_G3_2_A3_V0_VALID_ONLY_LEGACY_ORDER_REPAIRED.json"
test ! -e "$OUT"

python3 "$AUDIT/ic_g3_2_a3_valid_only_cutoff.py" \
  --review-repo "$REPO" \
  --code-commit "$COMMIT" \
  --original-price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --original-local-data "$REPO/research/local_data" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --g1-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --reconstructed-models "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12-report "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13-report "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --g3-2-numeric-quality-report "$AUDIT/g1-reconstruction/IC_G3_2_A3_NUMERIC_SOURCE_QUALITY_ONLY.json" \
  --out "$OUT" \
  --authorize-a3-validation-only-volatility-calibration \
  --trust-original-audited-pickles \
  --acknowledge-price-provider-vintage-unverified

shasum -a 256 "$OUT"
BASH
```

**Expected successful scientific status, if verified:**
`G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED`.

Accepted report must disclose exact original
19,880 composite-key bijection and UTC date
agreement, whether native/model orders differ,
how many prediction positions were correctly
remapped, original q25 P10 rate,
conventional trailing volatility cutoff
and the **weighted admission discrepancy due
to ties**. There is no requirement
that *unweighted* P10 and risk admission
counts match, because this is a
**weighted** calibration.

**If actual pair sets or event UTC dates
differ, this remains a genuine provenance
blocker**: stop without guessing rows,
joining on news_id alone, or silently
dropping observations. No q25
adjustment, model re-fit, old outcome
rerun, A3 risk effect, new holdout
or portfolio-P&L claim is authorized.

The original July-5 price snapshot's
acquisition vintage and point-in-time
split/dividend adjustment integrity
remain **UNVERIFIED** even if the
V0 row-order bug is fixed.
