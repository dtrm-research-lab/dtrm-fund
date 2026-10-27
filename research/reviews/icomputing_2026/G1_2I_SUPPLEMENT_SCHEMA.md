# G1.2i — Six-field V1 supplement schema, before numerical embedding replay

Date: 2026-10-27. Paper ICOMPUTING-D-26-01069.

## Completed G1.2h
Operator-run schema/source audit status:
`G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED`.

- 5,526 unique original V1 signal news; 5,526 manifest entries,
  zero missing or extra.
- 4,764 assigned to `2026-06-06` cache, all 4,764 present in
  June index. 2,467 of those IDs also occur in older May cache:
  keep **manifest source labels authoritative**.
- 735 assigned to `2026-05-23`, all in May index; zero
  observed in June index.
- 27 assigned to `v1_supplement`; these IDs are absent from
  both cache indices as expected for the V1 supplement.
- Original June cache: 26,519×384 float32; original May
  cache: 25,816×384 float32. Sizes, shapes and unique string
  index rows checked; actual embeddings still UNTESTED.
- The 42,446-byte original V1 supplement has SHA256
  `1697fc009800b673edda43ede18373f96916934d05cc03f50d16363b19d118d3`.
  It is a **six-key dictionary**, with list (one), ndarray (one),
  str (two), bool (one), int (one). G1.2h's supplementary
  structural-ID check matched zero because it looked at
  **metadata field names**, not at the internal news IDs.
  This is **not** evidence of missing 27 source news IDs.

## G1.2i scope and run command
Audit script: `ic_g1_supplement_schema.py`.
Requires G1.2h PASS and both original manifest/supplement SHA256
matches. Reads only the **trusted historical V1** supplement
and manifest Pickles, inspects:
- six dictionary field names/types, list cardinality,
  ndarray shape/dtype, without printing ID lists, content, or vectors;
- whether an explicitly named list field (`news_ids`,
  `missing_news_ids`, `ids`, `missing_ids`) has **exactly
  the 27 manifest supplementary IDs**, with zero duplicates;
- whether an explicitly named array field (`embeddings`,
  `vectors`, `missing_embeddings`, `missing_vectors`)
  is a 27×384 array (no element values inspected).
A nonrecognized schema remains OPEN for next review. Never infer
news IDs from dictionary keys; do not select source cache based
on vector similarity or target data.

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_supplement_schema.py" \
  -o "$AUDIT/ic_g1_supplement_schema.py"

python3 -m py_compile "$AUDIT/ic_g1_supplement_schema.py"

python3 "$AUDIT/ic_g1_supplement_schema.py" \
  --historical-local-data "$PWD/dtrm-fund/research/local_data" \
  --embedding-inventory "$AUDIT/g1-reconstruction/IC_G1_2_embedding_inventory.json" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_supplement_schema.json" \
  --trust-historical-pickles
```

Expected possible states:
- `G1_2I_SUPPLEMENT_NAMED_SCHEMA_READY_FOR_PREDECLARED_MAPPING`:
  explicit metadata field names permit deterministic ID→row
  mapping for future G1.2j numerical comparison; actual vector
  values remain UNTESTED.
- `G1_2I_SUPPLEMENT_SCHEMA_NEEDS_EXPLICIT_MAPPING`:
  inspect the schema and write a human-reviewed mapping with
  known field meanings before considering vector comparison.
  No adjusting vectors or searching cache assignments.

## G1.2j gate (NOT yet executed)
Once the exact historical supplement ID/vector structure is
validated, reconstruct the **384** embedding columns from the
two predeclared caches and supplement using the source manifest.
Compare numerically to original 40,320×384 historical
feature block with SHA-bound file checks and fixed tolerance 1e-6.
Never select embeddings based on proximity to frozen features.
The six non-embedding columns have already passed at max error 0.

Even full 390-feature historical parity does not prove that a new
independent 60-day holdout is feasible. Source contract basename
row-count discrepancy (265,145 local raw vs 40,320 in original
YAML) and original selection rules remain open.
