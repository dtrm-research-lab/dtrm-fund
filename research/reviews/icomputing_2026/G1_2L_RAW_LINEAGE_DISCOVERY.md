# G1.2l — Read-only historical V1 raw/selected sample provenance discovery

2026-10-27. Paper: ICOMPUTING-D-26-01069.

## Context and bounded objective
Original G1.2k historical reconstruction evidence is sealed:
9 JSON reports, 4 locally hashed rebuilt XGBoost boosters,
40,320 × 390 features numerically reproduced.
Final **local dossier SHA256**:
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
This reference is immutable for this checkpoint.

The historical V1 YAML names the raw file
`pairs_raw_2025-01-01_2026-06-06.pkl` with **40,320 rows**
but the operator's local file with that exact basename has
**265,145**. All scored 40,320 news/ticker pair keys form an
ordered subsequence after the frozen BRK.B→BRK-B normalization.
Numerical feature/score parity does not resolve whether this
was an unrecorded upstream raw dataset, overwritten snapshot,
or another original preprocessing step.

The original frozen `dtrm-fund` repository contains training
row ordering helpers but does not document an original
V1 265,145→40,320 dataset generation pipeline. To avoid
inventing an algorithm after seeing its results, examine
historical **source-code reference evidence** first.

## Tool: code-only local inventory
`ic_g1_raw_lineage_discovery.py` scans only `.py`, `.sh`,
`.md`, `.yaml`, `.yml`, `.toml`, `.sql` files under
the specified local folders, limited to 2 MB per source file.
It matches relevant names/numeric cardinalities and source
operations; records file relative paths, SHA256 and line
numbers of matching references. It never prints source lines,
IDs or potential credentials.

`.ipynb` filenames and sizes may be inventoried, but **notebook
contents are not opened**. Nor are Pickles, market data files,
embeddings, saved model binaries, targets, journal results,
or original scientific outcome records. This does not run
source code or imports. No exploratory scanning of returns.

From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_raw_lineage_discovery.py" \
  -o "$AUDIT/ic_g1_raw_lineage_discovery.py"

python3 -m py_compile "$AUDIT/ic_g1_raw_lineage_discovery.py"

python3 "$AUDIT/ic_g1_raw_lineage_discovery.py" \
  --search-root "$PWD/dtrm-fund" \
  --search-root "$HOME/Desktop/Play4Fun/PCDoMoney_Backend" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_raw_lineage_sources.json"
```

Expected completion:
`G1.2l: SOURCE_LINEAGE_REFERENCE_INVENTORY_ONLY`.
This is not a scientific pass; the operator must review source
references in historical chronology before a derivation claim
may be made. The script's reported SHA256 pertains to local
source-code files and is not evidence those sources are
historically dated/authored contemporaneously with V1.
Evaluate git commits, file modification timestamps and
notebook provenance separately; do not claim dates from
filesystem timestamps without corroboration.

## Next after source inventory
- Locate the exact source expression that applied original
  event window, filtering, exclusion, canonical ticker
  names and ordering to generate the historical 40,320 signals.
  Reproduce original counts WITHOUT reading any return labels,
  and compare against frozen original key sets and order.
- If the exact rule is only present in notebook source,
  design a separate *code-cell-only* extraction with outputs
  suppressed. Do not execute notebooks, inspect historical
  target/results cells or upload original private notebooks.
- If no authentic source is recovered, publish a transparent
  qualified discrepancy in supplementary methods; do not
  retrofit old YAML contract.
- Separately, draft the next independent 60-calendar-day
  evaluation protocol: see `G1_3_INDEPENDENT_TEMPORAL_PREREG_DRAFT.md`.
  That draft is **not frozen** and target data cannot be opened.

**Status: HISTORICAL_REPRODUCTION_PASS; V1_FILTERING_LINEAGE_OPEN.**
