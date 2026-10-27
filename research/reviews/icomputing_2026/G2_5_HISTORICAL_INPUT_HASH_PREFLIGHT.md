# G2.5 — Historical input-hash preflight (NOT G3 execution)

Date: 2026-10-27. Case ICOMPUTING-D-26-01069.
Stage: G2 active draft; G3 blocked.

The 22 editorial/reviewer requirements are now mapped.
Before freezing additional analysis rules, identify existing
historical validation P10 predictions and weights, V2/V3/V4
old cohort materials, and contemporaneous price/beta sources.

The file `ic_g2_historic_analysis_inputs.py` only lists
candidate names/sizes and bounded streaming SHA256 of
original local files. It does not decode NumPy or Pickle
datasets or inspect financial observations, future
return labels, model predictions, or outcomes.

### Run from DTRM_Lab on Mac

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_historic_analysis_inputs.py" \
  -o "$AUDIT/ic_g2_historic_analysis_inputs.py"

python3 -m py_compile "$AUDIT/ic_g2_historic_analysis_inputs.py"

python3 "$AUDIT/ic_g2_historic_analysis_inputs.py" \
  --root "$PWD/dtrm-fund/research/local_data" \
  --root "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --root "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Outputs" \
  --out "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json"
```

Expected success state:
`G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3`.

This is a hash-and-metadata-only checkpoint; no analysis on
previously known V2/V3/V4 returns is permitted. All new
candidate SHA fingerprints are retrospective local
commitments and must not be called pre-outcome hashes.

### Interpretation / next G2 tasks

- Validation source: original calibrated P10 and legacy
  per-event weights must be found and tied to the
  historically frozen original V0 validation process.
  Sensitivity compares *validation percentile cutoffs*
  q=0.15/0.25/0.35 of fixed P10, not new P15/25/35
  prediction models.
- Volatility comparator: verify an authentic price
  history before event timestamp, fixed lookback
  and common eligible set with frozen P10.
- Economic interpretation: verify price entry/exit
  timestamps, adjustment regime and capital/exposure
  assumptions. Otherwise no tradable P&L claim.
- K sensitivity: same old cohorts, fixed fractions,
  all failures disclosed as exploratory.
- After source inspection (distinct later operator
  gate), freeze full fixed formulas/data SHA/CIs/seeds
  or classify as non-executable.
- Preserve historical G1.2k and G1.2m original
  evidence, with original experiment tags unchanged.

**Scientific state: G2 OPEN / G3 BLOCKED.**
