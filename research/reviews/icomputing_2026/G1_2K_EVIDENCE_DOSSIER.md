# G1.2k — Historical model + complete 390-feature reproduction evidence dossier

Date: 2026-10-27. ICOMPUTING-D-26-01069.
Code/source anchor: `c7502a690162459cdfb3413573e3133c42efb126`.

## Operator-reported G1.2j PASS

After independent original V1 source, numeric ranker, P10, beta,
text and embedding provenance checks, the operator produced:
`G1_2J_HISTORICAL_384_EMBEDDING_ROW_PARITY_PASS`.

For the 40,320 original V1 ticker–news observations, source-directed
embedding reconstruction performed 15,482,880 comparisons:
- June 2026 cache: **35,358 rows**, max numerical difference 0.0.
- May 2026 cache: **4,753 rows**, max numerical difference 0.0.
- V1 27-news supplement: **209 rows**, max numerical difference 0.0.
- Total: **40,320 × 384**, max/mean absolute error **0.0**,
  zero mismatched rows/coordinates.
- G1.2j reported `coordinates_bitwise_equal=15482880`, but the
  checker calculates this field using NumPy **numeric equality
  (`x == y`)**, not a bytewise check (`view(uint32)`). Thus
  the scientifically precise claim is **exact numerical float32
  equality at every embedding coordinate**, not byte-for-byte
  identity of original source files.
- G1.2g demonstrated exact zero-difference reproduction of
  the five original text features on all 40,320 rows.
- G1.2f demonstrated exact zero-difference keyed `beta_pre`
  at the 390th feature on all 40,320 rows.
- G1.2c original **ranker predictions** max absolute difference 0,
  original **raw P10** max absolute difference 0, original
  **calibrated P10** max 7.450580596923828e-09; both old
  V1 and V4 P10 veto masks match with zero disagreements.
- The reconstructed boosters are **not** original preexisting
  serialized weights. They are reconstructed and independently
  compared numerically against frozen historical signals.

This supports historical reconstruction of all
40,320 × 390 = **15,724,800 feature coordinates**.

## What G1.2k does

`ic_g1_seal_dossier.py` creates a small, locally hashed, path-redacted
JSON dossier. It strictly verifies the expected statuses/content of
nine previous audit reports:
`preflight`, `rebuild`, `row_parity`, `source_subset`,
`feature_provenance`, `text_provenance`,
`embedding_inventory`, `supplement_schema`, and
`embedding_parity`.

It re-hashes the four **UNAPPROVED** reconstructed historical XGBoost
`.ubj` candidates and compares the hashes to the original
G1.2 reconstruction report. It records original V1 feature/signal/
beta SHA256 hashes independently committed in the V4 contract.

It does **not** open Pickles, embeddings, news, 60-day return targets,
prices or later cohort files; it does not run inference or retraining,
or publish per-row values. Output explicitly states:
`HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN`.

This is a *retrospective research dossier* and never represents
an independent new prospective accuracy evaluation.

## Run locally from DTRM_Lab

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_seal_dossier.py" \
  -o "$AUDIT/ic_g1_seal_dossier.py"

python3 -m py_compile "$AUDIT/ic_g1_seal_dossier.py"

python3 "$AUDIT/ic_g1_seal_dossier.py" \
  --reports-dir "$AUDIT/g1-reconstruction" \
  --models-dir "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json"
```

The operator should retain the reported dossier SHA256 and, after
review, may share **only that final dossier JSON** as a safe
metadata-only appendix. Do not upload original private source data,
models or raw per-news predictions.

## Outstanding scientific gates — explicitly NOT cleared

**Source-chain provenance:** Historical V1 contract associates
`pairs_raw_2025-01-01_2026-06-06.pkl` with 40,320 rows,
whereas the original local raw candidate file under that same
basename now holds **265,145**. The 40,320 scored pairs were shown to
form a normalized ordered subsequence, but neither their full
historical filter inclusion rule nor the raw-file copy/derivation
history is documented. Don't modify original frozen YAML to
reinterpret it post hoc; record source discrepancy.

**Independent efficacy:** All G0–G1.2 verification reuses known
historical V1/V4 outcomes. Before any G1.3 run, establish a
pre-registered **new temporally independent** cohort, date and
observation windows, 60-day horizon maturity, target definition,
source coverage, original frozen model hash, veto threshold,
required sample size and Top-K sizing, leakage embargo, and
news_id/ticker dependence-aware uncertainty design.
Never tune a policy based on newer targets before preregistration.
Keep the separate Phase IV STAMP/MM1 experiments unrelated.

**Statistical limitations:** Prior V2/V4 ticker-cluster 95% CIs for
incremental Top-K mean cross zero; don't describe the result as
uniformly robust, absolute profitability or an observed trade P&L.
