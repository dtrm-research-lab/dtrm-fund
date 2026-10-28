# G3.2 A3: paired 10,000 news-ID and ticker-cluster bootstrap — controlled release

**IC review:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Current stage:** original 3-arm paired *POINT* already executed and sealed;
full paired cluster runner **PREPARED, NOT YET EXECUTED OR AUTHORIZED BY PRIOR CONSENT**.

## Actual original observed A3 point result (do not retune)

Source-dependent original P10-q25 veto and conventional trailing
60-return daily realized-volatility veto have been frozen since the
validation stage. Original Q25 P10 cutoff
`-0.16665692627429962`; V0-only validation
volatility cutoff daily ddof=1
`0.020823002555902668`.

**Operator original A3 point result**:
`G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY`
**SHA256**
`b5b94f09d57d8bb3336ea01eb469f5ef703743a1217422be7e0f4b98484b4087`.

| Cohort | N | K | P10 − baseline mean | Risk − baseline mean | P10 − risk paired mean | P10 − risk hit-rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| V2 | 4,449 | 444 | +0.14429480582475662 | +0.23292389139533043 | **−0.0886290855705738** | **−0.22522522522522526** |
| V3 | 2,827 | 282 | +0.14943748898804188 | +0.24126996472477913 | **−0.09183247573673725** | **−0.1985815602836879** |
| V4 | 40,320 | 4,032 | +0.027561593800783157 | +0.07162084616720676 | **−0.04405925236642361** | **−0.12103174603174599** |

**Scientific reporting obligation:** Conventional stock-volatility
veto outperforms the P10 veto in all old-cohort observed point means
and hit-rates on the original fixed Top-K. This is an
UNADJUSTED, ALREADY-OUTCOME-CONSUMED historical finding,
NOT a demonstration of universal superiority. Even a
nominal paired ticker/news CI excluding zero cannot prove
prospective advantage. Do not revise/select q25 or risk
cutoffs after seeing these outcomes.

## Fully paired original news and ticker cluster interval contract

The pure math module
`ic_g3_2_a3_paired_cluster_bootstrap.py`
accepts original in-memory old V2/V3/V4 score,
native floating original forward targets
(`float32` preserved), original q25 pass,
fixed V0 risk pass and original news ID/ticker
cluster IDs. It has NO source I/O.

For EACH cohort and EACH of two original
groupings (news ID, ticker), perform exactly
**10,000** seeded bootstrap repetitions
(news seed 20260821, ticker seed 20260822).
Sample whole original clusters
WITH replacement, duplicate
all their rows in source order and
recompute original K=floor(.10×
replicate row count) and baseline
`np.argsort(-prediction)`
for all THREE veto arms on the
EXACT SAME resampled row array.
Calculate three **PAIRED**
differences for mean beta-adjusted
forward target and positive-target
hit rate:
P10−risk, P10−baseline, risk−baseline.
The first is the direct A3 reviewer
comparison. A target is not
a trading-account P&L.

If ANY resample's P10 or risk arm
has fewer than K candidate rows,
increment infeasible count and
**withhold all six 95% intervals for
that entire cluster scheme**;
do NOT silently drop infeasible
bootstrap draws and report
conditional success intervals.
Point values remain unchanged.
There are 3 cohorts × 2 schemes
× 10,000 = **60,000 total resamples**.

The full runner
`ic_g3_2_a3_paired_bootstrap_runner.py`
requires a NEW owner opt-in;
before deserializing old target
Pickles it SHA binds its own
source/tests, the protected previous
A3 point-runner source/tests,
the original G3.1 nine source/test
programs, G3.2 preflight eight
source/test programs, 6 old original
signal/target file SHAs, all 174
original saved July-5 prices, and
the operator-certified original
point report SHA above. It then
checks all three new point estimates
and scientific metadata against the
exact previous original report
without numerical retuning.

All intervals are nominal 95% percentile
cluster CIs, **NOT corrected** for
multiple comparisons or calendar
overlap of original rolling 60d
target horizons. Original price
vendor as-of acquisition date and
point-in-time corporate action
adjustments are still UNKNOWN.
No independent matured new
holdout or realized investment
P&L has been established.

## 2026-10-28: failed static assertion in first 138-test dry run; TEST-ONLY fix

The operator fetched the previously pinned `814d2d6e37317cfa17aa9450d8ebf1c32bcd3fad` version and executed all
138 tests. **137 passed; 1 failed**:
`test_prior_original_sha_and_all_scientific_source_gates`.
The test incorrectly expected the literal original A3 source-preflight SHA
`9c03f925be0429b9b70407018d59f1df801682a9e7a821a6bb9c6d3ef80fe317`
to appear verbatim inside the new paired runner, although that runner deliberately
imports `SOURCE_PREFLIGHT_SHA` and `VALID_CUTOFF_SHA` from the
earlier SHA-protected A3 point runner. Its actual runtime call
`evidence(a.g3_2_three_arm_source_preflight_report,SOURCE_PREFLIGHT_SHA)`
**does** verify the exact digest. No original old targets were opened.

The sole change in `2e4cce43f59d23ea5758bc7581cf7f42969cec9e` is a
**test-only change**: verify the exact resolved imported SHA values
and the actual `evidence()` calls for the preflight,
V0 cutoff and previously completed A3 point result. It does **not**
change the A3 bootstrap algorithm, original cohort source files,
original 60d model target, cutoff, cluster seed, 10k repetitions,
or any experimental protocol.

**New 138/138 outcome is pending local operator execution.**
Do not authorize the real 60k bootstrap if any test fails.

## Operator step 1: 138 source/synthetic tests — no original user files

Covers the already locally operator-validated
122 earlier tests, plus **8 new pure paired
bootstrap tests** and **8 new protected
runner tests**. The 138 new total
has NOT yet run locally.

```bash
bash <<'BASH'
set -euo pipefail

AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="2e4cce43f59d23ea5758bc7581cf7f42969cec9e"
BASE="research/reviews/icomputing_2026"

git -C "$REPO" fetch origin research/ic-major-revision-2026
git -C "$REPO" cat-file -e "$COMMIT^{commit}"

PARTS=(
  g2_g3_exploratory_core
  g3_1_a2_a6_join_contract
  g3_1_a2_a6_pure_grid
  g3_1_a2_validation_only_source
  g3_1_a2_a6_protected_runner
  g3_2_a3_numeric_source_quality_gate
  g3_2_a3_valid_only_cutoff
  g3_2_a3_original_3arm_source_preflight
  g3_2_a3_three_arm_pure_points
  g3_2_a3_three_arm_point_runner
  g3_2_a3_paired_cluster_bootstrap
  g3_2_a3_paired_bootstrap_runner
)

TESTS=()
for part in "${PARTS[@]}"; do
  for prefix in ic_ test_ic_; do
    file="${prefix}${part}.py"
    git -C "$REPO" show "$COMMIT:$BASE/$file" > "$AUDIT/$file"
  done
  TESTS+=("test_ic_${part}.py")
done

cd "$AUDIT"
python3 -m unittest "${TESTS[@]}" -v
echo "A3_PAIRED_10K_CODE_COMMIT=$COMMIT"
BASH
```

Expected only on genuine success:
`Ran 138 tests ... OK`.
The synthetic bootstrap tests may be more
compute intensive than earlier static tests.
On any failure, stop before accessing original
data, diagnose at the new test/code boundary,
never change original q25 or risk cutoff,
and never bypass SHA/test provenance.

## Operator step 2: separately authorized real 10k bootstrap

**This actively opens the original previously
consumed V2/V3/V4 forward target Pickles again,
which may execute code during deserialization.
Only run with explicit human agreement to this
separate use of previously SHA-audited trusted
local original files.** Previous A3 point
authorization is NOT reused.

Run ONLY once the complete 138 tests
are clean and the operator agrees to
all scientific scope acknowledgements:

```bash
bash <<'BASH'
set -euo pipefail

AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="2e4cce43f59d23ea5758bc7581cf7f42969cec9e"
REPORT="$AUDIT/g1-reconstruction/IC_G3_2_A3_ORIGINAL_PAIRED_10K_NEWS_TICKER.json"

test ! -e "$REPORT"

python3 "$AUDIT/ic_g3_2_a3_paired_bootstrap_runner.py" \
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
  --g3-2-original-3arm-point-report "$AUDIT/g1-reconstruction/IC_G3_2_A3_ORIGINAL_3ARM_PAIRED_POINT_ONLY.json" \
  --out "$REPORT" \
  --authorize-a3-old-outcomes-paired-news-ticker-bootstrap \
  --acknowledge-no-independent-60d-holdout \
  --acknowledge-retrospective-price-vintage-unverified \
  --acknowledge-no-realized-tradable-pnl \
  --trust-original-audited-pickles

shasum -a 256 "$REPORT"
BASH
```

Output status on completed 60k cluster draws:
`G3_2_A3_ORIGINAL_3ARM_PAIRED_NEWS_TICKER_10K_COMPLETED_POST_OUTCOME_EXPLORATORY`.

Even with that status, each scheme's
`infeasible_replicates` must be
inspected. If >0, ALL 3×2 intervals
for that scheme must be null/withheld.
Never interpret a withheld interval as
zero effect, and do not report an
interval excluding zero unless both
bounds and zero infeasible are verified.

Next gate after full execution is an
**independent aggregate-only report QA**
that checks exact point effect/metadata
preservation, all 6 original cohort×cluster
blocks, all 10k draws/seed values, the
all-or-none CI rule and SHA256. Do not
upgrade inferential status or the
manuscript until independent QA passes.
