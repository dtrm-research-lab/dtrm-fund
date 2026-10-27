# G2.10 — Original FMP price-cache SCHEMA + DATE-only feasibility, not volatility analysis

Date: 2026-10-27
Editorial case: `ICOMPUTING-D-26-01069`
Reviewer point: R1-04 conventional volatility/downside benchmark.
Gate: G2 ACTIVE/UNFROZEN; G3 BLOCKED.

## Verified G2.9 operator evidence

The operator ran `ic_g2_a3_price_cache_directory_inventory.py` on
the original FMP saved cache and obtained exactly
`G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN`.

- **3,649** original price-cache PKL files by filename.
- **174** `*_2026-07-05.pkl` original historic price
  snapshot files: **173 distinct equities + SPY**.
- Another 174 `*_2026-08-10.pkl` files.
- Zero watched files omitted from SHA256 cap.
- Exact report path:
  `~/dtrm-ic-audit/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json`.
  This locally generated report is protected by G2.10's
  computed SHA256, not a SHA manually invented in GitHub.

This corrects the G2.8 **basename-only candidate search false
negative**, without changing the earlier G2.5/G2.8 sealed
reports or any original experimental results.

## Scope of G2.10: original historical dates ONLY

Original frozen reader at
`c7502a690162459cdfb3413573e3133c42efb126`
uses `pd.read_pickle` and columns `date`, `close`,
which were historically used to construct returns.

New `ic_g2_a3_original_price_schema_dates.py`:
- Opt-in **only for locally trusted original Pickles**;
  `pandas.read_pickle` can execute arbitrary code, so do
  not use this on untrusted or downloaded Pickle files.
- Validates each of the 174 original July-5 file SHA256
  against the G2.9 metadata report **before** loading it.
- Checks DataFrame type and **column-name presence**
  `date` and `close`. Does NOT access `close` values
  or examine their numeric content. The original
  DataFrame is necessarily loaded into Python memory
  by the trusted-Pickle parser; do not claim that
  numerical prices were not read into memory.
- Checks only `date` parseability, uniqueness, min/max,
  nulls and any rows dated after the filename snapshot.
- For the earliest dated original V4/V2/V3 events,
  May 2 / June 7 / June 11, checks per ticker whether
  there are 41 dates before each event for minimum
  40 close-to-close returns and 61 dates for a full
  60 trailing trading-return lookback.
- SPY is included in the same metadata audit. No
  original V2/V3/V4 result arrays, labels, market
  returns, volatility values, XGBoost inference,
  finance targets or new event/news cohort are opened.
- Refuses to overwrite the prior audit output.
- Outputs date coverage counts per ticker and
  original source SHA references.

**Important limitation:** These are cohort *first-event
date* coverage checks, not event-by-event verification
for every row nor the entire V0 training/validation
population. Even if 174/174 pass the dates, as-of
ingestion/provider vintage, corporate actions,
historical adjusted prices and ticker mappings
remain **UNVERIFIED**. A July-5 snapshot was
saved **after** May/June events. Past bar dates
in a retrospective snapshot are necessary for
a no-future-bar risk statistic but insufficient
to prove its original pre-event source vintage.

### Command (Mac, from `~/Desktop/DTRM_Lab`)

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_a3_original_price_schema_dates.py" \
  -o "$AUDIT/ic_g2_a3_original_price_schema_dates.py"

python3 -m py_compile "$AUDIT/ic_g2_a3_original_price_schema_dates.py"

python3 "$AUDIT/ic_g2_a3_original_price_schema_dates.py" \
  --price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-7-preflight "$AUDIT/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json" \
  --g2-7-plan "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --trust-original-price-pickles
```

Possible result statuses:

- `G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`:
  All 174 original saved frames have `date`/`close`
  named columns and sufficient uniquely dated historical
  bars before the three earliest event dates, **without
  assessing close values**. This is **NOT** a point-in-time
  provider-vintage certification or a performance comparison.
- `G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PARTIAL_OR_SCHEMA_OPEN`:
  One or more files lack date/column shape, contain
  duplicate/invalid dates, or have insufficient
  historical dates. Preserve all failures; do not
  silently reduce tickers or fabricate missing bars.

If the operator does not explicitly trust the
historical local Pickles, **do not run G2.10**;
choose a safer export from a known trusted
original code path. Original source files were
used earlier in G1.2 trusted reconstructions,
but this does not remove Pickle security risk.

### Scientific next actions if date-level feasibility passes

1. Fix actual original V0 validation time and ticker
   population, and row-for-row V2/V3/V4 news dates
   and ticker overlap without opening forward labels.
2. Record adjustment regime, market as-of vintage
   and strictly pre-event daily closing-price
   availability, with limitations if contemporary
   snapshots cannot be authenticated.
3. Predeclare a conventional trailing realized-volatility
   risk veto: 60 previous daily close-to-close
   returns (min 40), strictly pre-event; validation-only
   high-risk rejection cutoff set to match the
   original weighted P10 admission budget; same
   ranker, Top-K and full-K feasibility.
4. Label any old-cohort A3 comparison
   `POST_OUTCOME_EXPLORATORY`; record original
   negative and wide ticker-cluster intervals
   and all comparator failures.
5. Only after A3/A4/A6 dispositions, full-G2
   adversarial science review and signoff, freeze
   the revision protocol. No G3 now.

**Status G2.10 PREPARED / NOT YET RUN. G3 BLOCKED.**

## 2026-10-27 G2.10 first operator attempt HALTED — bug fixed, NOT a scientific failure

Operator command returned:
`G2.10 HALTED: NameError: name 'G2_5' is not defined`.

**Root cause:** the G2.10 output dictionary referenced
undefined variables `G2_5`, `G2_6`, and `G2_A2`,
while the SHA anchors defined in the module were
`G2_5_SHA`, `G2_6_SHA`, and `G2_A2_SHA`.
The fix changes **only the output JSON metadata dictionary
value references** to the defined sealed constants:
- `g2_5_source_inventory_sha256: G2_5_SHA`
- `g2_6_source_binding_sha256: G2_6_SHA`
- `g2_7_a2_plan_sha256: G2_A2_SHA`

The error occurs *after the loop that hash-checks and loads
the 174 opt-in original historical price frames*, during
final JSON result construction. Thus the first attempt
probably completed its date-only inspection but **did
not write a report or issue PASS/PARTIAL**. It did not
compute volatility, financial returns, risk filter
comparison or model inference. This is an **audit tool
runtime defect**, not missing price data or a failed
point-in-time statistical test.

The code has been fixed directly on the same review
branch; original historical Git pin, input files and
G2.5–G2.9 SHA evidence were not changed.
Added `test_ic_g2_10_schema_dates_regression.py`
with five static-only regression cases checking the
original JSON SHA names, syntax, close-values exclusion,
trusted-Pickle opt-in and G3 gate. **No user-machine
regression test execution is asserted.**

### Safe repair / verify / retry from the original DTRM_Lab directory

```bash
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"

curl -fsSL "$BASE/ic_g2_a3_original_price_schema_dates.py" \
  -o "$AUDIT/ic_g2_a3_original_price_schema_dates.py"
curl -fsSL "$BASE/test_ic_g2_10_schema_dates_regression.py" \
  -o "$AUDIT/test_ic_g2_10_schema_dates_regression.py"

python3 -m py_compile \
  "$AUDIT/ic_g2_a3_original_price_schema_dates.py" \
  "$AUDIT/test_ic_g2_10_schema_dates_regression.py"

cd "$AUDIT"
python3 -m unittest test_ic_g2_10_schema_dates_regression.py -v

python3 "$AUDIT/ic_g2_a3_original_price_schema_dates.py" \
  --price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-7-preflight "$AUDIT/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json" \
  --g2-7-plan "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --trust-original-price-pickles
```

Reusing the same output path is valid **only if it did
not exist before this rerun**; G2.10 deliberately
refuses overwrites. If the path already exists for
any reason, use a new path and preserve previous
artifacts without deleting them.

**G2.10 scientific status remains NOT EVALUATED pending
fresh user execution of the corrected script. G3 BLOCKED.**

## 2026-10-27 G2.10 corrected operator retest — PASS

The operator subsequently executed the corrected source
after the 3-undefined-SHA-symbol bug and ran the five
static regression tests: **5/5 PASS**.

Actual G2.10 local terminal:
`G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`
with `DATE_STRUCTURE_OK: 174`, `173` equity
symbols and `1` SPY file. All 174 original
price frames have at least 61 distinct dated
closes strictly before each of the three
original V4/V2/V3 first-event dates, sufficient
dates for 60 close-to-close returns.
Local report at
`~/dtrm-ic-audit/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json`.
Its SHA256 is not yet in the GitHub audit.

**Supersedes the earlier 'HALTED/RETEST PENDING' label
above.** No financial close series values were used
in computations, no target or P&L outcomes opened,
and G3 was NOT authorized. Trusted original Pickles
were unpickled in memory with operator opt-in.
Source vintage, adjustments and all event-pair
coverage remain open. Next
`G2_11_A3_A4_A6_CONTROLLED_HANDOFF.md`.
