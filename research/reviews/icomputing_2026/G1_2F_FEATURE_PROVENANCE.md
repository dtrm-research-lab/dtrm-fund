# G1.2f — Canonical row order, beta feature, embedding manifest (historical only)

Date: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.

## Evidence established before this gate

- Frozen ex-ante point ranker reconstructed on original trusted historical
  data, 12/12 aggregate checks PASS.
- Original V1 40,320-row baseline signal had 0.0 maximum per-row
  prediction difference against reconstructed frozen booster.
- P10 raw signal per-row maximum difference 0.0; calibrated P10 maximum
  7.450580596923828e-09, tolerance 1e-6; both veto masks exact.
- G1.2e membership confirms **40,320/40,320** signal pairs appear in
  the raw 265,145-row historical universe after historical
  `BRK.B` → `BRK-B` canonicalization. Raw duplicate pairs 0,
  signals duplicates 0; 33 aliases did not match literally.
- Signal date range 2026-05-02T03:06:00Z to
  2026-06-06T22:22:29Z, inside historical V1 window.
- The frozen V1 contract assigns 40,320 rows to the exact raw pair
  filename, whereas the found local file has 265,145. This discrepancy
  remains **open** and must not be silently rewritten.

## Audit and scientific limits

Script `ic_g1_feature_provenance.py` verifies three frozen artifact
SHA256 values documented prior to V4 outcome inspection, the locally
generated G1.2e raw-input SHA, and canonicalized key membership. It
computes whether V1 selected keys form an ordered subsequence of the
raw candidate pairs **after** canonicalization, provided aliases do
not create duplicate raw keys.

The ex-ante feature design from pinned source is
384 embedding features + 5 text features + 1 beta_pre = 390.
For the historically saved V1 features it inspects only column 390
(the beta_pre field). If the original beta artifact has a recognized
numeric schema, it compares all 40,320 values at original float32
precision. Where the original beta source has explicit news_id/ticker
keys, the join is keyed; otherwise any numeric match is described as
*positional*, not proof of provenance. It also reports only type,
column names and shape for the historical embedding manifest.
No raw news text, model weights, news identifiers or per-row values
are exported.

This test is a source-provenance **corroboration**, never a substitute
for re-running the original selection and feature engineering scripts.
A non-monotonic source subsequence order may simply indicate historic
intentional sorting and is NOT automatically a fail. All G1.2f
outcomes preserve `prospective_model_approval: false`.

## Run from DTRM_Lab

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_feature_provenance.py" \
  -o "$AUDIT/ic_g1_feature_provenance.py"
python3 -m py_compile "$AUDIT/ic_g1_feature_provenance.py"

python3 "$AUDIT/ic_g1_feature_provenance.py" \
  --signals-root "$PWD/dtrm-fund/research/local_data" \
  --raw-root "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --source-subset-report "$AUDIT/g1-reconstruction/IC_G1_2_source_subset.json" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_feature_provenance.json" \
  --trust-historical-pickles
```

The script opens **trusted original 2026 data Pickles only**:
raw candidate news/ticker keys; V1 historical signals; V1 beta_pre;
optionally historic V1 embedding manifest; and original V1 feature
matrix. It never reads old or new target outcomes, market returns, or
2026-08+ prospective news/prices. Do not upload these scientific
inputs to GitHub.

## Gate meanings

- `HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN`:
  SHA-bound historic source membership and recognized beta column
  parity passed. Full 389 remaining features and selection lineage
  are still uncertified.
- `HISTORICAL_CANONICAL_PAIR_MEMBERSHIP_PASS_BETA_SCHEMA_OPEN`:
  beta serialization needs further schema-specific investigation;
  canonical membership remains corroborated.
- `HISTORICAL_BETA_FEATURE_MISMATCH` or
  `CANONICAL_PAIR_LINEAGE_MISMATCH`: stop promotion and investigate.
- No possible result of this control represents a fresh, temporally
  disjoint holdout. Independent G1.3 remains CLOSED.

## Subsequent work
1. Reconstruct the exact frozen inclusion/ordering and complete
   384-embedding + 5-text + beta matrix from original V1 source,
   matching its pre-committed SHA256, or document precisely the
   residual row-provenance limitation.
2. Identify why the raw candidate filename described in the 2026
   V1 contract now has a different row cardinality.
3. Treat the reconstructed XGBoost models as historically numerically
   equivalent, but not literally original saved boosters. Keep
   per-model SHA and a provenance bundle.
4. Acquire authorized newly timestamped independent news and forward
   price data without peeking at outcomes; pre-register temporal
   cutoff and embargo before the next empirical test.
