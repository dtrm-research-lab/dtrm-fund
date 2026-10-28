# G3.2 A3 — original V0 VALID-only conventional volatility veto calibration

**Revision:** ICOMPUTING-D-26-01069  
**State as of 2026-10-28:** source NUMERIC QUALITY **OPERATOR PASS**;
VALIDATION-only threshold/calibration **PREPARED, NOT EXECUTED**.

## Locked original evidence

A3 price-cache source numeric quality gate was operator-executed:
- `Ran 34 tests in 0.047s — OK`.
- Exact source status:
  `G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED`.
- 174/174 saved original 2026-07-05 stock/SPY cache sources
  checked against original SHA source manifest.
- Exactly **19,880/19,880** V0 VALID pairs and
  **47,596/47,596** old V2/V3/V4 pairs have numeric
  positive finite selected past 61 daily closes,
  yielding the full 60 simple daily returns and
  historical daily volatility `np.std(ddof=1)`.
- No pair excluded, no risk percentile or score
  selected, and **no old target labels** read.
- Original operator local quality source report SHA256:
  `91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a`.

Important: the July-5 saved stock-price snapshot is
**LATER than every original validation/test event**.
The archived bar date is not proof the vendor supplied
the identical price, split/dividend adjustment, or
revision vintage before the old decision. A3 may be
presented as a **DATE-RESTRICTED RETROSPECTIVE CONTROL**,
never a proven point-in-time ex-ante comparator.

## Separate next method: weighted P10 admission matched risk cutoff

The **only** price and P10 data allowed in the
new `ic_g3_2_a3_valid_only_cutoff.py` are:

1. Original SHA-bound model-row
   `legacy_model_rows_2026-05-01.pkl`
   `split=="valid"` exactly 19,880; original
   `news_id,ticker,date_dt` and their source order.
2. Original frozen P10 model prediction reconstruction
   on the **same ordered validation** 19,880 feature rows,
   with SHA-bound original 390-feature model source,
   previously reconstructed original model SHA and
   original weighted q25 calibration cutoff.
   **Not a new fit** and **no target labels**.
3. 174 original SHA-bound July-5 saved price frames
   using the untouched original source-close convention,
   61 prior bars strictly before event UTC day,
   60 simple returns, sample daily std ddof=1.
4. Original weighted P10 q25 validation admission
   `P10_calibrated >= -0.16665692627429962`.
5. Frozen conventional filter:
   `risk <= original_weighted_quantile(valid_risk,
   legacy_news_weights(valid_news_ids), ORIGINAL
   WEIGHTED P10 ADMISSION FRACTION)`.

P10 and risk selectivity must be **matched on original
VALIDATION-only inverse-news-weighted admission**.
Unweighted counts and **weighted tie discrepancy**
are required outputs; ties must not be patched,
broken by target or retroactively threshold-tuned.
No V2/V3/V4 signal or target file is opened,
no old ranking/outcome comparison and
no clustered 10k bootstrap is permitted.
No per-row source price, volatility, prediction,
news ID or ticker is serialized.

The new SHA-bound code and its 12 synthetic/static
tests are prepared in GitHub; no Mac PASS claimed.

## Operator Step 1 — 51 synthetic/static tests, no original prices

Runs 22 frozen core tests, 12 A3 numeric source tests,
5 previously used original V0 P10 validation
source tests, and 12 new A3 matched-cutoff tests,
all from a **single exact immutable code SHA**.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
ROOT="research/reviews/icomputing_2026"

git -C "$REPO" fetch origin research/ic-major-revision-2026
A3_VALID_COMMIT="$(git -C "$REPO" rev-parse FETCH_HEAD)"

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
  git -C "$REPO" show "$A3_VALID_COMMIT:$ROOT/$file" > "$AUDIT/$file"
done

cd "$AUDIT"
python3 -m unittest \
  test_ic_g2_g3_exploratory_core.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_2_a3_valid_only_cutoff.py -v

printf '%s\n' "$A3_VALID_COMMIT" \
  > "$AUDIT/g1-reconstruction/IC_G3_2_A3_VALID_CODE_COMMIT.txt"
echo "A3_VALID_CODE_COMMIT=$A3_VALID_COMMIT"
BASH
```

Expected only if the synthetic code is correct:
`Ran 51 tests ... OK`.
A failure must be diagnosed in the new
implementation/tests; no data source/model change.

## Operator Step 2 — new explicit V0 VALID-only authorization

This deliberately opens trusted ORIGINAL 2026-07-05
price source Pickles, V0 model-row source and
other original frozen feature/model inputs
necessary for the P10 VALID-only replay.
Pandas Pickle loading is potentially code-executing;
only use previously SHA-audited trusted local
files in a controlled environment. Nothing is
uploaded to GitHub.

This is NOT authorization to open old
V2/V3/V4 historical outcome targets.
Only run after 51/51 tests PASS and acceptance
of the later-vintage limitation.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
CODE="$(cat "$AUDIT/g1-reconstruction/IC_G3_2_A3_VALID_CODE_COMMIT.txt")"
OUT="$AUDIT/g1-reconstruction/IC_G3_2_A3_V0_VALIDATION_ONLY_VOLATILITY_CUTOFF.json"

test ! -e "$OUT"

python3 "$AUDIT/ic_g3_2_a3_valid_only_cutoff.py" \
  --review-repo "$REPO" \
  --code-commit "$CODE" \
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

If source and ranker parity gates ALL PASS,
the only acceptable state is:
`G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED`.

The output should report:
P10 weighted admission fraction and unweighted
count, calibrated daily volatility cutoff,
weighted risk admission fraction and count,
the weighted difference from ties, original
19,880 V0 pair count and explicit old-target
access **FALSE**. A q25 reproduction or
VALID-order mismatch is a hard scientific STOP.

**No threshold should be changed after seeing
old historical cohort effects.** Before any
A3 V2/V3/V4 label comparison, separately
audit full common-case construction, old
P10/volatility ranking and all 3 arms,
and require fresh explicitly scoped operator
approval for known-old outcome deserialization.

The conventional downside/volatility comparator
is **retrospectively reconstructed and limited
by provider-vintage uncertainty**. The original
A2/A6 report remains unchanged.
