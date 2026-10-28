# G2.12 — SHA-bound per-event price bar-date coverage, no outcomes

Manuscript: `ICOMPUTING-D-26-01069`.
Date: 2026-10-28.
Reviewer R1-04: conventional volatility/downside comparator.
**Graph: G2 ACTIVE/UNFROZEN; G3 still BLOCKED.**

## Operator G2.9 and G2.10 source report fingerprints — now pinned

The operator ran `shasum -a 256` over the two original local reports,
and supplied **the exact** source report SHA-256 values:

| Source report | SHA256 |
| --- | --- |
| `IC_G2_9_A3_original_price_cache_inventory.json` | `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb` |
| `IC_G2_10_A3_price_schema_dates.json` | `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3` |

Previously pinned G2.6 report:
`1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`.

Original source commit:
`c7502a690162459cdfb3413573e3133c42efb126`.

G2.10 results on user Mac:
5/5 static tests PASS; 174/174 original July-5
`date`/`close` named columns, strictly prior
calendar-date coverage for 60 daily close-to-close
returns at **only the three earliest original cohort
event dates** (V4 May 2, V2 June 7, V3 June 11).
Nothing about individual May/June news/ticker rows
or original V0 validation has yet been certified.

## G2.12 limited research question

**For each original consumed (news_id,ticker,date_dt) record,
does the ORIGINAL July-5 stock price cache contain at least
61 distinct dated close bars strictly before the individual
event date, permitting in principle up to 60 lagged returns?**

The price values and actual returns are NOT examined.

Inputs, read-only:
- 174 original saved `*_2026-07-05.pkl` stock/SPY
  price-cache sources, each size and SHA-verified against G2.9
  **before** trusted original Pickle deserialization.
- Frozen V1 signals 40,320 pairs (used to represent V4
  time cohort), V2 signals 4,449 pairs, V3 signals
  2,827 pairs, plus original V4 signals 40,320
  as a supplementary key/order/date crosscheck.
  Each signal file is SHA-verified against G2.6 before loading.
- It accesses *only* source price `date` and old
  signal `news_id`, `ticker`, `date_dt`.
  All original financial prediction, target and label
  fields are not used for calculation or output.
- Original `BRK.B→BRK-B` ticker alias is applied
  once; no general ticker-coverage tuning.
- Every original event pair gets a strict UTC
  calendar cutoff, excluding event-day close.
  Counts >=61 dated closes imply 60 *potential*
  trailing close-to-close returns; >=41 imply
  minimum 40. Price quality is not certified.
- V1 vs V4 event/ticker/date **key sets** must agree;
  original source row order is recorded separately
  and does not change price-date feasibility.
  This is NOT a new independent temporal cohort.
- Report **aggregate pair counts per cohort only**:
  full 60-date coverage, 40-date coverage, missing
  cache ticker, SPY deficit, dates outside historic
  windows. No individual news IDs or ticker records
  leave the operator's local machine.

### Run (shell, any current directory)

First download the new source and regression tests to
`$HOME/dtrm-ic-audit`. The script refuses to overwrite
an existing source report; do not delete a previous
evidence artifact to make the command pass.

```bash
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"

curl -fsSL "$BASE/ic_g2_a3_per_event_bar_date_coverage.py" \
  -o "$AUDIT/ic_g2_a3_per_event_bar_date_coverage.py"
curl -fsSL "$BASE/test_ic_g2_12_per_event_date_regression.py" \
  -o "$AUDIT/test_ic_g2_12_per_event_date_regression.py"

python3 -m py_compile \
  "$AUDIT/ic_g2_a3_per_event_bar_date_coverage.py" \
  "$AUDIT/test_ic_g2_12_per_event_date_regression.py"

cd "$AUDIT"
python3 -m unittest test_ic_g2_12_per_event_date_regression.py -v

python3 "$AUDIT/ic_g2_a3_per_event_bar_date_coverage.py" \
  --original-price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --original-local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --trust-original-pickles
```

**Security:** The `--trust-original-pickles` flag
is explicit consent to load the previously audited
LOCAL historical Pandas Pickles. Pickle loading can
execute code, including if the file is malicious.
Never use it on a downloaded/untrusted Pickle.
The script checks original expected SHA-256 of
each Pickle before opening it, but this does not
make Pickle inherently safe. Reading a Pickle
unavoidably materializes its stored dataframe
in memory, including any numeric fields;
those fields are *not accessed* by this procedure.

### Expected result classes, NOT guaranteed outcomes

- `G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN`:
  all original historical event/ticker pairs have
  61 strictly prior dated close bars; original
  V1/V4 event/ticker/date **key sets** match.
  Their row-order agreement is separately reported.
  Provider vintage and price adjustments remain
  **UNVERIFIED**, so no causal independent A3
  result and no G3 authorization.
- `G2_12_A3_PARTIAL_EVENT_PAIR_BAR_DATES_OR_SOURCE_SCHEMA_OPEN`:
  missing prices, shortened bars, date/ticker or
  source schema issue in at least one old cohort.
  All missingness is reported. Do not alter ticker
  rules or exclude inconvenient records post hoc.
  Exit status 2 indicates incomplete source
  readiness, not an investment result.
- `G2.12 HALTED` on input hash mismatch,
  malformed source, or missing original
  trusted file. Preserve the prior evidence,
  diagnose without retuning scientific rules.

V2/V3 original signal file schemas are checked
at runtime. If they lack the expected three
identifier/date fields, the program reports
`SIGNAL_DATE_TICKER_SCHEMA_OPEN` rather than
guessing or retrieving forward target/label files.

## Scientific boundaries after G2.12

Even if all 47,596 distinct original historical
pairs pass (V4 40,320 + V2 4,449 + V3 2,827;
V1/V4 duplicate representation checked separately),
the A3 comparator still needs:
1. Validation V0 event/date/ticker coverage
   for a *validation-only* volatility threshold.
2. Actual historical price **numeric validity**,
   stock split/dividend adjustment regime,
   vendor as-of **acquisition timestamps** and
   anti-leakage design. Original July-5 source
   itself postdates May/June decisions.
3. Exactly fixed common-eligible old cohort
   sample, risk cutpoint, full-K and bootstrap
   methods, before opening any old outcomes.
4. An honest `POST_OUTCOME_EXPLORATORY` label.
5. A4 economic/flat and A6 Top-K disposition,
   complete 22-point reviewer matrix and
   final human G2 scientific signoff.

**G2.12 is PREPARED, NOT OPERATOR EXECUTED.
No model scores, price returns, risk filter,
profitability or future labels are calculated.
G3 remains BLOCKED.**
