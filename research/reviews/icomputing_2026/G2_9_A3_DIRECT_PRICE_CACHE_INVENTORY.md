# G2.9 — Correction of G2.8 risk-comparator source search (scope false-negative)

Date: 2026-10-27
Manuscript: `ICOMPUTING-D-26-01069`
Reviewer: R1-04 (volatility-based control).
Graph: G2 ACTIVE/UNFROZEN; G3 BLOCKED.

## Operator finding at G2.8

G2.8 operator result:
`G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY`.

The actual 92-candidate earlier source scan classified:
- 28 `BETA_OR_MARKET_CONTEXT_NOT_STOCK_PRICE_SOURCE`;
- 43 `EXCLUDED_OUTCOME_OR_TEST_ARTIFACT`;
- 21 `OTHER_FILE_NAME`;
- 0 `POSSIBLE_PRICE_SOURCE`.

**Critical scope correction:** these zero candidates do **NOT**
justify concluding that original stock-level historical prices
are absent. The G2.5 inventory used case-insensitive patterns
on the individual **basename only**:
`price|spy|market|beta|daily|return|quote|volatil`.
Consequently, files such as
`price_cache_fmp_pickle/MSFT_2024-02-16_2026-07-05.pkl`
would not be included, despite their residence in the
original FMP price cache. However, `SPY_...` paths
would be included merely due to 'SPY' in the basename;
the user observed 28 such original SPY cache files.
The named MSFT path here is **hypothetical example only,
not a confirmed local file**.

The original historic V0
`run_exante_baseline_v0.py` at pinned commit
`c7502a690162459cdfb3413573e3133c42efb126`
has:
- `PRICE_CACHE=OUTPUTS/"price_cache_fmp_pickle"`;
- `glob("*_2026-07-05.pkl")`;
- ticker parsed from filename;
- `frame["date"]` and `frame["close"]`
  for original forward-outcome price construction.
The already completed historic G1.2 preflight reported
174 original `*_2026-07-05.pkl` files as its source
feasibility requirement. **This is previously reported
historical metadata, not independently revalidated in G2.9.**

### Source boundaries and caution

Having a July 5 2026 **filename** does not demonstrate
that the price series was collected before a May/June
2026 event, that corporate-action-adjusted close existed
then, that risk could be computed without future data,
or that all 60 prior observations exist for validation
and test dates. In particular the original price source
uses the `close` column rather than an independently
proven point-in-time `adj_close` field.

The original G2.8 state is therefore retained verbatim
as an **accurate bounded result about G2.5's narrow
candidate catalog**, but scientific decision
`A3_NOT_EXECUTABLE` is **NOT** authorized on its basis.

## New G2.9 audit (never open prices)

Script:
`ic_g2_a3_price_cache_directory_inventory.py`.

Bounded new operation:
1. Reuse cryptographically pinned old G2.5 inventory
   SHA256 `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`,
   original G2.6 binding SHA256
   `1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`
   and A2 plan SHA256
   `5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8`.
2. Check actual G2.7 PASS and G2.8 limited negative report,
   pinned unchanged original Git `HEAD`.
3. Examine only original folder
   `PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle`
   (not another research source root).
4. Classify filenames shaped
   `<ticker>_<first-date>_<last-date>.pkl` and count
   per filename last-date suffix.
5. Hash at most 25 MiB per file for the original
   `2026-07-05` and `2026-08-10` file-date groups,
   streaming bytes without decoding/executing any
   Pickle. Collect ticker names/count, file sizes and
   hashes, no numerical price data.
6. Refuse to overwrite the source report or silently
   include symlinks. Do not alter G1/G2.8 artifacts.

### Operator command — from `~/Desktop/DTRM_Lab`

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_a3_price_cache_directory_inventory.py" \
  -o "$AUDIT/ic_g2_a3_price_cache_directory_inventory.py"

python3 -m py_compile "$AUDIT/ic_g2_a3_price_cache_directory_inventory.py"

python3 "$AUDIT/ic_g2_a3_price_cache_directory_inventory.py" \
  --price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-7-preflight "$AUDIT/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json" \
  --g2-7-plan "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  --g2-8-report "$AUDIT/g1-reconstruction/IC_G2_8_A3_price_source_triage.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json"
```

Possible metadata-only statuses:

`G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN`:
a source directory with multiple distinct original stock
snapshot filenames exists; **schema, actual dates, historical
as-of adjustments, daily stock volatility and eligibility
are NOT proven.** Before computing A3, create a separate
consented historical schema/date-only verification of
trusted original file content with no future results;
freeze deterministic missingness rules and fair validation
risk-veto cutoff in G2.

`G2_9_A3_NO_MULTITICKER_ORIGINAL_PRICE_CACHE_SNAPSHOT_IDENTIFIED`:
the specified folder does not show sufficient distinct
recognized original historic-price filenames.
Do not improvise a comparator on `beta_pre`,
or rely on unproven generic price files.

**G2.9 not yet operator-run. G2 not frozen; G3 blocked.**

## G2.9 operator execution result — PASS (2026-10-27)

The operator subsequently executed the original
G2.9 script and obtained
`G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN`.

File counts: **3,649** original cache entries,
**174** `*_2026-07-05.pkl` (173 distinct
non-SPY symbols + SPY); another **174**
`*_2026-08-10.pkl`. Zero hashed
watched-file cap omissions. All file
contents remain unopened by G2.9.
This supersedes this runbook's original
`G2.9 not yet operator-run` historical footer.

A3 source barcode/schema/date verification
remains open. Next G2.10 is separately gated
`G2_10_A3_PRICE_DATE_SCHEMA_GATE.md`.
No new investment comparison has been executed.
