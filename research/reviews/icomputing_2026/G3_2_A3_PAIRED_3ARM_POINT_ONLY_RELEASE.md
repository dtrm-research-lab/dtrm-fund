# ICOMPUTING-D-26-01069: G3.2 A3 paired 3-arm point-only release

**Date:** 2026-10-28.  
**Status:** Source-only original A3 3-arm feasibility PASS. **122/122 new point-only candidate source/synthetic tests operator PASS on 2026-10-28; actual original target outcome run NOT yet executed and separately consented.**

## Original operator-attested evidence sealed

- Original frozen Phase II source `c7502a690162459cdfb3413573e3133c42efb126`.
- Frozen G2 research protocol `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`.
- Corrected, exact reproduced G3.1 q25/K10 original Phase II 18-point science source `0c5e433f10ce742bc129b666dfc4551f4b2fd21b`.
- Original 18-point old historical effect report SHA256:
  `8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb`.
- Original historic price numerical source quality V0 19,880 + old 47,596 eligible, 174 July-5 2026 original cache source files SHA checks; report SHA256:
  `91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a`.
- Original V0 validation-only P10-to-risk admission calibration, 56/56 tests PASS, q25 P10 original frozen:
  `-0.16665692627429962`, fixed daily trailing 60-return
  sample std ddof=1 risk threshold `0.020823002555902668`.
  Calibration report SHA256:
  `f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21`.
- Original operator executed A3 SOURCE-ONLY 63/63 tests PASS.
  Original three-arm source preflight:
  `G3_2_A3_3_ARM_ORIGINAL_SOURCE_ONLY_K10_FEASIBILITY_PASS_OUTCOMES_BLOCKED`,
  report SHA256:
  `9c03f925be0429b9b70407018d59f1df801682a9e7a821a6bb9c6d3ef80fe317`.

| Cohort | N original | Fixed K=floor(.1 N) | Original q25 admitted | Fixed risk admitted | Both selected Top-K common | Three-arm original full K |
|---|---:|---:|---:|---:|---:|---|
| V2 | 4,449 | 444 | 2,530 | 1,870 | 301 | YES |
| V3 | 2,827 | 282 | 1,634 | 1,376 | 212 | YES |
| V4 | 40,320 | 4,032 | 23,348 | 16,217 | 2,946 | YES |

The original V0 weighted risk cutoff closely matched
original q25 P10 validation admissions **by news-weighted
fraction**, not by unweighted pair counts. In V2/V3/V4
saved risk veto admits fewer pairs than P10.
**Do NOT retune either veto using old cohort observations.**
Each of the three policies is full-K feasible.

## Scientific estimands and limitations

The new A3 *point-only* module
`ic_g3_2_a3_three_arm_pure_points.py` computes,
for each original V2,V3,V4 N and same K:
- Original ranking without any veto (baseline).
- Original P10 q25 veto.
- Original V0-only calibrated conventional
  trailing daily stock-volatility risk veto.
- Paired differences in OLD original 60-day
  forward beta-adjusted target mean and
  positive-target hit fractions:
  P10−baseline, risk−baseline, **P10−risk**.
- Admissions, K, observed Top-K selected overlaps,
  and original Phase II q25/K10 1e-12 effect parity.

**These are comparisons on the SAME old cohort rows,
same baseline prediction, same original row ordering,
and same K**, with original native floating target
dtype maintained (original Phase II float32 mean).

No 10k news/ticker cluster uncertainty in point
mode: a positive difference would not be statistical
significance. No after-outcome policy selection or
multiple-testing-controlled claims.
Even later nominal paired bootstrap CIs
cannot establish a **prospective** advantage.

**Price-vintage caveat remains unresolved:** archived
source `2026-07-05` prices postdate the events,
and acquisition-time vendor revisions plus historical
corporate-action price adjustments are unverified.
This is a date-restricted retrospective comparator,
not a verified deployable ex-ante price-risk policy.
Neither original future beta-excess target nor
hit rate is realized self-financing trading P&L.

## Step 1 — 122 source and synthetic tests (NO original data)

A3 source+point code and all original G3.1/G3.2
source/test dependency files MUST match the same
immutable Git candidate. Expected 122 tests:
22 original core + 16 original cohort join + 9 A2/A6
pure grid + 5 original V0 P10 source + 10 original
G3.1 runner + 12 original A3 numeric +
17 original V0 risk cutoff + 12 A3 3-arm
source preflight + 9 new A3 pure paired points
+ 10 new A3 point runner synthetic guards.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="f093543d809742ebcdc8e70ea0218686a4b99a6f"
BASE="research/reviews/icomputing_2026"
git -C "$REPO" fetch origin research/ic-major-revision-2026
git -C "$REPO" cat-file -e "$COMMIT^{commit}"

for file in \
  ic_g2_g3_exploratory_core.py \
  test_ic_g2_g3_exploratory_core.py \
  ic_g3_1_a2_a6_join_contract.py \
  test_ic_g3_1_a2_a6_join_contract.py \
  ic_g3_1_a2_a6_pure_grid.py \
  test_ic_g3_1_a2_a6_pure_grid.py \
  ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_1_a2_validation_only_source.py \
  ic_g3_1_a2_a6_protected_runner.py \
  test_ic_g3_1_a2_a6_protected_runner.py \
  ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py \
  ic_g3_2_a3_valid_only_cutoff.py \
  test_ic_g3_2_a3_valid_only_cutoff.py \
  ic_g3_2_a3_original_3arm_source_preflight.py \
  test_ic_g3_2_a3_original_3arm_source_preflight.py \
  ic_g3_2_a3_three_arm_pure_points.py \
  test_ic_g3_2_a3_three_arm_pure_points.py \
  ic_g3_2_a3_three_arm_point_runner.py \
  test_ic_g3_2_a3_three_arm_point_runner.py
do
  git -C "$REPO" show "$COMMIT:$BASE/$file" > "$AUDIT/$file"
done
cd "$AUDIT"
python3 -m unittest \
  test_ic_g2_g3_exploratory_core.py \
  test_ic_g3_1_a2_a6_join_contract.py \
  test_ic_g3_1_a2_a6_pure_grid.py \
  test_ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_1_a2_a6_protected_runner.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_2_a3_valid_only_cutoff.py \
  test_ic_g3_2_a3_original_3arm_source_preflight.py \
  test_ic_g3_2_a3_three_arm_pure_points.py \
  test_ic_g3_2_a3_three_arm_point_runner.py -v

echo "A3_POINT_CANDIDATE_COMMIT=$COMMIT"
BASH
```

**Observed operator outcome on 2026-10-28:** `Ran 122 tests in 0.492s — OK`.
This confirms source/synthetic unit tests only. Original A3 historical
forward-target point results have **not** been executed or observed.

## Step 2 — new separate owner-authorized old-outcome POINT ONLY

**This step loads the original historical V2/V3/V4
forward target Pickles, which the A3 source-only
preflight explicitly prohibited.** It requires
new, explicit operator authorization. Original
saved Pickles can execute code when deserialized;
use only previously independently SHA-audited
trusted local original archives and a controlled
Python environment. Do not execute if no
consent to this narrowly described data access.
Do not overwrite any older A3 or G3.1 evidence.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="f093543d809742ebcdc8e70ea0218686a4b99a6f"
REPORT="$AUDIT/g1-reconstruction/IC_G3_2_A3_ORIGINAL_3ARM_PAIRED_POINT_ONLY.json"
test ! -e "$REPORT"

python3 "$AUDIT/ic_g3_2_a3_three_arm_point_runner.py" \
  --review-repo "$REPO" \
  --approved-commit "$COMMIT" \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g1-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --original-local-data "$REPO/research/local_data" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --reconstructed-models "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12-report "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13-report "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --original-price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --g3-2-numeric-quality-report "$AUDIT/g1-reconstruction/IC_G3_2_A3_NUMERIC_SOURCE_QUALITY_ONLY.json" \
  --g3-2-valid-cutoff-report "$AUDIT/g1-reconstruction/IC_G3_2_A3_V0_VALID_ONLY_LEGACY_ORDER_REPAIRED.json" \
  --g3-2-three-arm-source-preflight-report "$AUDIT/g1-reconstruction/IC_G3_2_A3_ORIGINAL_3ARM_SOURCE_ONLY_PREFLIGHT.json" \
  --g3-1-original-point-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_POINT_ONLY.json" \
  --out "$REPORT" \
  --authorize-a3-retrospective-old-outcome-point-only \
  --acknowledge-no-independent-60d-holdout \
  --acknowledge-retrospective-price-vintage-unverified \
  --acknowledge-no-realized-tradable-pnl \
  --trust-original-audited-pickles

shasum -a 256 "$REPORT"
BASH
```

**Expected success status, IF original input SHA/semantic parity and
the three old source-only result cell count proofs all pass:**
`G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY`.

**No A3 bootstrap, significance, vintage, independent holdout or
tradable P&L claims are warranted even after successful point results.**
Paired news/ticker cluster confidence intervals would be a separately
consented and auditable next stage; they must reselect
all 3 arms on the same cluster-resampled observation array,
recompute K and withhold all affected CIs if either
veto cannot fill K on ANY resample.
