# G2.13 — Original V0 validation-only price BAR DATE coverage for A3

**Date:** 2026-10-28. **Case:** ICOMPUTING-D-26-01069.
**Reviewer:** R1-04 (conventional volatility/downside risk filter).
**Graph:** G2 ACTIVE, UNFROZEN; G3 BLOCKED.

## Actual G2.12 result (operator-reported PASS)

Original local operator execution:

`G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN`

Seven static source regression tests: **7/7 PASS**.
The same original 174 FMP July-5 prices dated strictly
before every original event showed:
- V4 represented by original V1 signals: **40,320/40,320**,
- V2: **4,449/4,449**,
- V3: **2,827/2,827**,
- original V4 signals: **40,320/40,320**.

No missing stock symbols; old V1 versus V4
event/ticker/date **sets and original row order** agree.
No actual numerical stock close values, forward targets,
volatility, risk comparisons, portfolio outcomes or
new model scores were used.

G2.12 generated local report:
`$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json`.
Its SHA256 will be computed at G2.13 and recorded
in the new report; it has NOT been provided separately
by the operator as of this runbook.

Earlier output SHA pins:
- G2.9 `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`.
- G2.10 `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`.

**SCOPE CEILING:** G2.12 proves only bar **date**
coverage for *test/holdout* pairs, NOT the frozen V0
validation fold on which a fair volatility cutoff
must be set, nor true historical provider vintage.

## Original V0 validation fold source

Pinned code `research/experiments/run_probabilistic_xgb_v0.py`,
original commit `c7502a690162459cdfb3413573e3133c42efb126`:
- Uses `legacy_model_rows_2026-05-01.pkl`
  (original `research/local_data`).
- Original split is assigned by literal
  `model_rows["split"].eq("valid")`.
- Previous historical G1.2 exact numerical reconstruction
  identified **19,880** original `valid` observations.
- Original train/valid/test alignment was rechecked
  at G1.2 (12/12 original numeric controls).
- Source model-row file is not known here to have
  a *pre-outcome signed SHA*. G2.13 computes a
  **retrospective current local file SHA** only:
  it does not authenticate a past vendor collection.
- This step does NOT calculate a volatility cutoff
  or touch historical `forward_excess_beta` targets.

## G2.13 method and security

Script `ic_g2_a3_original_validation_date_coverage.py`:
- Refuses to overwrite a previous audit result.
- Verifies exact G2.9/G2.10 report SHA, original
  G2.12 PASS/metadata genealogy and code commit.
- Re-hashes 174 original price Pickles against
  the G2.9 individual file source manifest before
  loading them.
- Selects original V0 rows with `split="valid"`,
  checks exactly 19,880 records and canonical
  BRK.B/BRK-B key handling.
- Inspects only V0 `news_id,ticker,date_dt,split`
  and original stock/SPY `date` column values,
  never the numeric `close` column, original
  targets, beta, rank scores or P10 values.
- Checks individual validation event dates for
  >=61 strictly earlier bar dates (60 potential
  daily stock returns) or >=41 earlier bar dates
  (40 minimum returns). Reports aggregate counts
  and source hashes, without individual news IDs.
- Reports price-cache ticker missingness and SPY
  date shortfalls separately.

**Security caveat:** It loads *trusted original*
Pandas Pickles, which can execute code and necessarily
loads complete original frames into Python memory.
Use only on files from the previously audited
local research folder, not remote or untrusted Pickles.
The relevant numeric columns are not accessed
in calculations.

**Scientific caveat:** Historical July-5 files may
contain split/dividend adjustments or other
revisions made after the May/June decisions.
Even 100% prior bar-date coverage is NOT proof of
event-time source availability.

### Operator command — no new market return computation

Run from any shell directory:

```bash
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"

curl -fsSL "$BASE/ic_g2_a3_original_validation_date_coverage.py" \
  -o "$AUDIT/ic_g2_a3_original_validation_date_coverage.py"

curl -fsSL "$BASE/test_ic_g2_13_validation_dates_regression.py" \
  -o "$AUDIT/test_ic_g2_13_validation_dates_regression.py"

python3 -m py_compile \
  "$AUDIT/ic_g2_a3_original_validation_date_coverage.py" \
  "$AUDIT/test_ic_g2_13_validation_dates_regression.py"

cd "$AUDIT"
python3 -m unittest test_ic_g2_13_validation_dates_regression.py -v

python3 "$AUDIT/ic_g2_a3_original_validation_date_coverage.py" \
  --original-price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --original-model-rows "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data/legacy_model_rows_2026-05-01.pkl" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12-report "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --trust-original-pickles
```

**Expected result class — not a promised result:**
`G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN`
if all original validation events have 60 prior
dated price closes. If not, expect
`G2_13_A3_V0_VALID_PRICE_DATE_COVERAGE_PARTIAL_COMMON_CASE_REQUIRED`
(exit 2, with full missingness report).
Do not rewrite original cohort or choose a
convenient date range to avoid partial results.

If a model-row schema/count/source SHA check
halts, retain all reports without overwriting.

## After G2.13: single bounded G2 freeze discussion

Even a full validation coverage PASS only establishes
that a validation-only *retrospective* volatility
cutoff is possible in principle.

**Before authorizing G3** we must still (i) decide
honest quote-vintage / corporate-action limitations;
(ii) lock all common-sample, missing close and
adjustment rules and actual provider evidence;
(iii) decide A4 economic replay feasibility and
A6 fixed Top-K grid; (iv) close the 22-point reviewer
audit and adversarial G2 freeze.

Avoid additional low-value inventory steps.
The A3 baseline comparison, if authorized, will
remain explicitly **POST_OUTCOME_EXPLORATORY**,
not an independent prospective 60-day test.

## Superseding G2.13 local operator outcome and immutable report digest (2026-10-28)

The operator subsequently ran **7/7 static regression tests PASS**
and the full source-only date gate. Exact result:
`G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN`.
Original `valid` fold **19,880/19,880** event/ticker pairs,
**167** symbols, oldest original validation event date
`2025-12-24`, newest `2026-01-21`;
zero original price-cache ticker gaps.
Original `legacy_model_rows_2026-05-01.pkl`
retrospective local SHA:
`3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
G2.12 source report SHA:
`e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`.

The operator also SHA256-checked the newly generated
G2.13 report with exact digest:
`e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`.

This supersedes the earlier 'G2.13 not yet run' / missing
digest text above. No volatility, actual return outcomes,
predictor fitting, or G3 comparison was executed. Source
vintage, numeric closing prices and adjustment regime
remain unverified. **G2 unfrozen; G3 blocked.**
