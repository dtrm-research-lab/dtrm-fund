# G1.2e — Source subset and 2026 pair snapshot provenance

Date: 2026-10-27. ICOMPUTING-D-26-01069.

## Completed independent checkpoint
- The local reconstructed point XGBoost predictions matched the frozen
  40,320-row original V1 baseline signal **exactly**: max abs diff 0.
- Both original P10 numeric series passed at 1e-6:
  `p10_raw` max abs diff 0;
  `p10_calibrated` max abs diff 7.450580596923828e-09.
- V1 absolute-zero P10 veto and V4 frozen relative-P25 veto had **zero**
  row-level disagreements.
- No prospective outcomes inspected in G1.2.

## Why G1.2d returned UNKNOWN
The simple G1.2d checker assumed a source raw candidate file and frozen
V1 signals must have the **same** pair count and ordering. Actual local
historical sources are:
- `pairs_raw_2025-01-01_2026-06-06.pkl`: **265,145** rows;
  columns `news_id`, `ticker`.
- `probabilistic_v1_holdout_signals_2026-06-06.pkl`: **40,320** rows.

Different counts *may* be expected for an upstream raw candidate universe
and selected scored cohort; G1.2d cannot resolve it. Do not interpret
`V1_SOURCE_PAIRS_MISMATCH_OR_UNKNOWN` as disproof of the reproduced
XGBoost model or as proof the source is correct.

**Scientific contract discrepancy:** historical
`DTRM_XGB_PROBABILISTIC_V1.yaml` describes the raw pairs basename
`pairs_raw_2025-01-01_2026-06-06.pkl` and `rows: 40320`.
Yet the local file with that exact name has 265,145 rows. Its origin
and whether a later selection/pipeline overwrote an earlier copy remain
unresolved. Record this explicitly in journal revision; don't edit the
historical contract or invent an original filtering rule.

## Outcome-blind corrected test

From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_source_subset.py" \
  -o "$AUDIT/ic_g1_source_subset.py"
python3 -m py_compile "$AUDIT/ic_g1_source_subset.py"
python3 "$AUDIT/ic_g1_source_subset.py" \
  --signals-root "$PWD/dtrm-fund/research/local_data" \
  --raw-root "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_source_subset.json" \
  --trust-original-pickles
```

Reads **only** two original trusted historical pickle dataframes; no new
holdout predictions or targets/returns. Generates an aggregate, path-redacted
JSON report with raw/selected pair counts, exact source-key membership, known
BRK.B→BRK-B normalization sensitivity, raw duplicate count, subset order if
source keys are unique, original V1 event date bounds, current SHA of raw
file (not pre-committed), and an explicit historic contract cardinality warning.

### Interpretation
- `RAW_SOURCE_SUBSET_MEMBERSHIP_CONFIRMED_DERIVATION_PENDING`:
  Every V1 selected signal pair appears in raw input (not proof how selected).
- `CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING`:
  Only the predeclared BRK.B→BRK-B transform ensures membership.
- `RAW_SOURCE_PAIR_LINKAGE_UNRESOLVED`: one or more V1 keys still cannot
  be linked to the claimed raw source; block promotion, trace lineage.

Even a full match is **not** a complete provenance certificate: independent
row-to-390-feature construction and the original raw→selected filtering
pipeline must still be documented. Prospective scoring remains closed.
