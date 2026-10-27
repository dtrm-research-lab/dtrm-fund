# G1.2h — Frozen V1 original embedding-source coverage and cache inventory

Date 2026-10-27. ICOMPUTING-D-26-01069.

## G1.2g operator outcome
Original V1 five-text-feature provenance PASS:
- 40,320/40,320 rows × 5 text columns compared against exact pinned
  `c7502a690162459cdfb3413573e3133c42efb126` source.
- Maximum difference **0.0**, and zero rows outside 1e-6 tolerance.
- Historic June 6 2026 news snapshot: 43,183 rows.
- Historical keyed beta feature already passed with maximum difference 0.0.
- Thus all 6 *non-embedding* features of the 390-feature vector pass.

Historic V1 contract documents 5,526 unique event-news embeddings:
- 4,764 from the `2026-06-06` original embedding cache;
- 735 from the `2026-05-23` original cache;
- 27 from the V1 supplement.

Local inventory indicates the associated cache families are present,
including `news_emb_2025-01-01_2026-06-06.dat` (40,733,184 bytes)
and `news_emb_2025-01-01_2026-05-23.dat` (39,653,376 bytes).
Those byte sizes are not evidence of correct event-ID coverage.

## G1.2h metadata+schema-only next step
The script `ic_g1_embedding_inventory.py` verifies:
- SHA-bound original historical V1 signal artifact and news-ID coverage.
- Exact `(news_id, date_dt, embedding_source)` manifest structure;
  category names, 5,526 rows and source counts without exposing IDs.
- Original `2026-06-06` and `2026-05-23` embedding cache
  index and shape Pickles are deserialized **only from trusted local
  historical sources**. It checks integer index offsets, 384
  dimensions, counts, and byte-size consistency of `.dat` vectors.
- Source-label membership against each cache index, by news_id.
- The supplement Pickle is deserialized to examine type, field names,
  key coverage and shape, **not the numeric vector values**.
- Hashes cache files and the supplement as **new local commitments**;
  these are not independent historical artifact hashes.

No `.dat` numeric embeddings are read as vectors, no trained model
is executed, no target values, prices, news later than June 2026,
or future returns are read. The script deliberately cannot select
a cache based on which vector happens to match the historical
feature matrix: the declared `embedding_source` must determine
that mapping *before* G1.2i numerical comparison.

## Operator command

From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_embedding_inventory.py" \
  -o "$AUDIT/ic_g1_embedding_inventory.py"
python3 -m py_compile "$AUDIT/ic_g1_embedding_inventory.py"

python3 "$AUDIT/ic_g1_embedding_inventory.py" \
  --historical-local-data "$PWD/dtrm-fund/research/local_data" \
  --historical-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_embedding_inventory.json" \
  --trust-historical-pickles
```

Expected successful schema status:
`G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED`.

If the manifest source count multiset differs from `(4764, 735, 27)`,
or more/missing rows exist, report the discrepancy rather than changing
historical data to force compliance.

## Next strictly gated step
G1.2i must:
1. Use *actual original source-label semantics* to select exactly one
   of the two dated caches or the original V1 supplement.
2. Reconstruct the 5,526 distinct 384-float32 embedding vectors in
   original signal row order (40,320×384); no target values or
   outcome labels may be opened.
3. Compare against first 384 columns of original precommitted V1
   feature matrix with fixed 1e-6 tolerance. Report only aggregate
   max abs difference and mismatch count; never try alternate cache
   assignments to optimize the result.
4. Keep any unknown supplement schema, missing event ID, vector
   normalization discrepancy, or suspicious feature mismatch OPEN.
5. Never mark the independent new temporal holdout approved by
   successfully replaying a historic, already-consumed V1 cohort.

The original historical V1 raw pair filename contract discrepancy
(265,145 local rows vs 40,320 claimed in contract) and original raw→V1
selection/filtering chain remain unresolved independently.
