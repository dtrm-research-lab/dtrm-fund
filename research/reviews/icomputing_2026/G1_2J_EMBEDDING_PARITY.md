# G1.2j — Source-directed 40,320 × 384 historical embedding parity

Date: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.
Frozen original source: `c7502a690162459cdfb3413573e3133c42efb126`.

## Historical evidence before this gate

The operator has established:
- Ranker, raw P10, calibrated P10 numerical 40,320-row parity
  against frozen original V1 predictions (max differences 0,
  0 and 7.450580596923828e-09 respectively), and exact
  historic V1 absolute and V4 relative veto masks.
- Original 40,320 V1 pair keys are an ordered subsequence of
  a 265,145-row raw candidate file after the historically documented
  `BRK.B` → `BRK-B` mapping. No duplicate keys.
- Historical keyed `beta_pre` matches the original final
  feature matrix column in all 40,320 rows (max abs error 0).
- All five text features generated from original pinned code
  and original June 6 news match the original feature columns
  385–389 for 40,320 rows (max abs error 0).
- G1.2h manifest 5,526 event IDs equals the 5,526 source-news IDs
  in the original frozen V1 signals (zero missing/extra):
  June cache = 4,764; May cache = 735; V1 supplement = 27.
- G1.2i verifies `probabilistic_v1_missing_embeddings_2026-06-06.pkl`
  is a metadata dict with `news_ids` as 27 unique strings and
  `embeddings` as a 27×384 float32 ndarray, with the **same 27
  event ID set** as the original V1 manifest `v1_supplement` label.
  The other fields are `dtype`, `max_chars`, `model`, and
  `normalize_embeddings`; values of the vectors have not yet
  been inspected or compared.
- A given news ID can exist in multiple caches, but the original
  manifest source label — NEVER whichever vector matches — is
  authoritative. In particular, 2,467 of the 4,764 June-assigned
  event IDs also occur in the May cache.

## Fixed numeric replay protocol

Script `ic_g1_embedding_parity.py` first verifies G1.2f/g/h/i
local predecessor JSON statuses, the historically precommitted
original V1 feature and signal hashes, and the local audit hashes
of the original manifest, two cache binary files and their
index/shape metadata, and the V1 supplement.

It then maps each original V1 signal news_id to `embedding_source`
in the original 5,526-news manifest:
1. `2026-06-06` — original June 6 float32 `.dat`, using
   original June index/shape.
2. `2026-05-23` — original May 23 float32 `.dat`, using
   original May index/shape.
3. `v1_supplement` — original explicitly aligned
   `news_ids[j]` ↔ `embeddings[j]` from historical dict.

No embeddings are regenerated with a new model, no cache is chosen
based on similarity to frozen features, and no labels/scores/returns
are used to select source vectors.

The script compares all 40,320 × 384 float32 coordinates against
columns 1–384 of the precommitted frozen V1 `npy` matrix,
with hard-coded absolute threshold **1e-6** and zero relative tolerance.
It reports total/per-source max/mean error, count of mismatching
rows/coordinates and number of exactly equal coordinates.
Only aggregate metadata and error counts enter local JSON. No
raw text, news IDs, per-row embeddings, trading returns or
serialized source models are uploaded.

## Execute from DTRM_Lab

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_embedding_parity.py" \
  -o "$AUDIT/ic_g1_embedding_parity.py"

python3 -m py_compile "$AUDIT/ic_g1_embedding_parity.py"

python3 "$AUDIT/ic_g1_embedding_parity.py" \
  --historical-local-data "$PWD/dtrm-fund/research/local_data" \
  --historical-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --embedding-inventory "$AUDIT/g1-reconstruction/IC_G1_2_embedding_inventory.json" \
  --supplement-schema "$AUDIT/g1-reconstruction/IC_G1_2_supplement_schema.json" \
  --beta-provenance "$AUDIT/g1-reconstruction/IC_G1_2_feature_provenance.json" \
  --text-provenance "$AUDIT/g1-reconstruction/IC_G1_2_text_provenance.json" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_embedding_parity.json" \
  --trust-historical-pickles
```

## Gate semantics

- `G1_2J_HISTORICAL_384_EMBEDDING_ROW_PARITY_PASS`:
  all original 15,482,880 embedding coordinates match at
  fixed absolute tolerance 1e-6; previous text/beta tests
  establish six more columns, totaling **390 original historic
  input features** in all 40,320 rows.
- `G1_2J_HISTORICAL_EMBEDDING_VALUES_MISMATCH`:
  stop, preserve per-source mismatch statistics and diagnose
  original provenance, dtype/memmap assumptions or source
  lineage. No retry with alternative cache, normalization or
  vector nearest matching.
- Any hash/schema/ID missing: HALT rather than artificially
  adapting the original source.

**Limits:** historic source-cache hashes are retrospective local
commitments. Only the original frozen V1 feature and signal
artifacts have independent V4 historical hashes. The V1 raw
pair file has 265,145 local rows but the historical V1 contract
states 40,320 under the same name; that original selection/contract
discrepancy remains unresolved. No untouched post-August 2026
cohort or independent 60-day gain is demonstrated by historic
reproduction. G1.3 prospective validation remains BLOCKED.
