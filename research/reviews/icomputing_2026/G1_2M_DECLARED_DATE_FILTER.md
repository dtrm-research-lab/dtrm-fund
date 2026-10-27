# G1.2m — Validate the *historically declared* V1 event-window hypothesis (outcome blind)

Date: 2026-10-27, manuscript ICOMPUTING-D-26-01069.

## What was established at G1.2l
The operator ran the source-code-only inventory
`ic_g1_raw_lineage_discovery.py`:
- **301** original code/documentation files examined.
- **5** potentially related historical references, but no direct
  source generation rule was identified in them; historic V1
  and V4 YAML and Phase II bootstrap/report references dominate.
- **33** original notebook *filenames* identified but contents
  deliberately not inspected.
- No source notebooks, Pickles, forward target outcomes or
  market prices opened by G1.2l.

Historical 2026 V1 contract names:
- Cohort event dates **2026-05-02** through **2026-06-06**.
- News snapshot `news_2025-01-01_2026-06-06.pkl`.
- A pair snapshot basename `pairs_raw_2025-01-01_2026-06-06.pkl`
  with a declared 40,320 selected rows.
- Only historically declared ticker alias `BRK.B → BRK-B`.

Locally, the file under that exact raw basename has **265,145**
rows; the already SHA256-frozen V1 signals have **40,320**.
The 40,320 V1 keys are an ordered subset of the raw 265,145
after the historically documented ticker alias. Existing evidence
has not established *why* those 40,320 were selected.

## ONE preregistered structural hypothesis, never optimized

The name `pairs_raw_2025-01-01_2026-06-06.pkl` may describe an
upstream, full-date-range candidate universe, and selecting rows
whose original `news_id` maps to news with
**2026-05-02 ≤ date_dt < 2026-06-07 UTC** may independently
recover exactly the 40,320 V1 scored pairs.

This is the **only** tested date window (from original frozen V1
contract). No scanning alternative date ranges, tickers, returns,
or exclusion policies to maximize agreement.

`ic_g1_declared_date_filter.py` reads three *trusted historical*
source Pickles: the 265,145 source candidate `(news_id,ticker)`
pairs, the June 6 original news snapshot (news_id and date_dt),
and the already SHA256-anchored 40,320 V1 signals.
The original prior G1.2e raw pair and G1.2g news SHA256 hashes
must also match; it does NOT open target returns, label files,
future prices, model boosters or recent events. No notebooks
are executed or opened.

It then compares filtered canonical pair **key set, raw-order
subsequence, and historical news event timestamp agreement**.
Only aggregate counts and hashes are written; no individual IDs
or original article text are written to output.

An exact set/order match supports a very specific original
*observational equivalence of declared date-only filtering*.
It does **not** establish that the original V1 script actually
implemented this rule, nor does it resolve the historical
40,320-vs-265,145 file-label/documentation conflict.

## Run from DTRM_Lab

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_declared_date_filter.py" \
  -o "$AUDIT/ic_g1_declared_date_filter.py"

python3 -m py_compile "$AUDIT/ic_g1_declared_date_filter.py"

python3 "$AUDIT/ic_g1_declared_date_filter.py" \
  --historical-local-data "$PWD/dtrm-fund/research/local_data" \
  --historical-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --source-subset-report "$AUDIT/g1-reconstruction/IC_G1_2_source_subset.json" \
  --text-provenance-report "$AUDIT/g1-reconstruction/IC_G1_2_text_provenance.json" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_declared_date_filter.json" \
  --trust-historical-pickles
```

## Interpretation

- `V1_DECLARED_DATE_FILTER_EXACT_KEY_SET_AND_ORDER_PASS_SOURCE_CODE_OPEN`:
  all 40,320 keys and original source order obtained using
  **only the frozen date window and ticker alias**. Historical
  generator file identity and implementation source remain OPEN.
- `V1_DECLARED_DATE_FILTER_KEY_SET_PASS_ORDER_OR_DATES_OPEN`:
  complete source key membership with ordering or
  event-timestamp differences needing explanation.
- `V1_DECLARED_DATE_FILTER_INCOMPLETE_ADDITIONAL_SELECTION_RULE_UNKNOWN`:
  date-only filtering is insufficient. Do not invent further
  filters to fit observed V1 rows. Investigate original notebooks'
  **code cells only** in a separately audited step.
- `V1_DECLARED_DATE_FILTER_SOURCE_NEWS_SCHEMA_OPEN`:
  original news does not have expected `news_id,date_dt`.
  Investigate original source lineage, not an estimated date field.

## Distinct outstanding gates
1. Original source code/observational inclusion-rule chronology
   and source file copy lineage are not established by numeric
   recreation of a date filter.
2. Prior G1.2k historic reproduction dossier remains unchanged
   SHA256 `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
3. G1.3 new-outcome validation is **NOT frozen nor authorized**.
   A genuinely new late October 60-calendar-day prospective cohort
   cannot yield completed outcomes before Nov 25 deadline.

## Operator outcome recorded 2026-10-27 — STRUCTURAL PARITY PASS

The previously declared **single** historical event-date-window
hypothesis was tested without examining price outcomes or alternative
filters. CLI state:
`V1_DECLARED_DATE_FILTER_EXACT_KEY_SET_AND_ORDER_PASS_SOURCE_CODE_OPEN`.

Observed original June 6 news-ID coverage 100% (unmatched 0);
date-filtered original raw candidates **40,320**, historical V1
signal pairs **40,320**; key sets identical; row order identical;
every signal event timestamp matches original news event timestamp.
There are **zero** missing/extra pairs. The ticker alias is the
previously documented BRK.B→BRK-B normalization.

**Selection provenance now split into evidence grades:**
- **Structural reconstruction PASS:** original predeclared V1
  UTC date-only selection explains exact 265,145→40,320
  cardinality, canonical keys, row order and event dates.
- **Authentic original historical generator / snapshot label
  unresolved:** pinned YAML `pairs_snapshot.file` labels
  the same local raw filename as containing 40,320 rows.
  We do not yet have a contemporaneous code/notebook or
  copy manifest authenticating which physical version the
  label referred to. Preserve old YAML verbatim.
- **Historic numeric reproducibility PASS**: sealed separate
  G1.2k dossier SHA256
  `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`;
  do not edit the sealed output to inject this supplementary
  G1.2m finding.
- **New prospective evidence NOT YET RUN**: no independent
  results may be inferred from this exact historical match.

Reviewer-safe conclusion: The retained raw pair candidate
snapshot, filtered by the originally specified cohort dates
and ticker alias, reproduces the frozen 40,320-row V1
`(news_id,ticker,date)` sequence exactly. We retain an
explicit file-label/provenance caveat.
