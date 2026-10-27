# G1.2g — Historical five-text-feature row parity, embedding inventory

Date: 2026-10-27. Manuscript ICOMPUTING-D-26-01069.

## Already observed by operator

G1.2f status:
`HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN`.
- 265,145 raw pairs → 40,320 frozen V1 scored pairs.
- 40,320/40,320 normalized pair membership PASS and raw-subsequence
  original pair ordering PASS.
- V1 input features matrix 40,320×390, SHA-bound to the historically
  precommitted matrix.
- Original `beta_pre` table 40,320×4 keyed by news_id, ticker;
  all 40,320 values exactly agree with final model column
  (maximum deviation **0.0**, not positional coincidence).
- Embedding manifest `probabilistic_v1_embedding_manifest_2026-06-06.pkl`
  exists (5,526 rows, fields: date_dt, embedding_source, news_id)
  and has a **newly observed local** SHA256, not independent historic
  commitment.
- G1.2c independently verified original ranking and both quantile
  P10 numerical row signals in 40,320/40,320 samples.

## Historical 390-feature layout

Pinned original source at commit
`c7502a690162459cdfb3413573e3133c42efb126`:
- columns 1–384: `all-MiniLM-L6-v2` embedding, normalised,
  dimension 384, event-specific;
- columns 385–389: `dtrm.text_features.legacy_text_feature_matrix`
  (log count of characters, words, !, ?, uppercase ratio);
- column 390: `beta_pre`, already independently verified against
  an SHA-anchored historical keyed table.

The script `ic_g1_text_provenance.py` uses the exact pinned
`src/dtrm/text_features.py`, not a new approximation. It attempts
to reconstruct all 5 text columns on the V1 frozen signal row order
from the **old 2026-06-06 news snapshot**. Only if full 40,320-row
news_id text lookup exists and is unambiguous does it declare PASS.

The script also inventories original embedding cache filenames/sizes
in original PCDoMoney Outputs and historical `research/local_data`.
It does **not load** those embedding files or assume an embedding cache
format. It does not inspect financial outcomes or new historical prices.
If news schema/coverage is incompatible it returns an explicit
`UNRESOLVED` status, not forced matching or invented news entries.

## Operator command

From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_text_provenance.py" \
  -o "$AUDIT/ic_g1_text_provenance.py"
python3 -m py_compile "$AUDIT/ic_g1_text_provenance.py"

python3 "$AUDIT/ic_g1_text_provenance.py" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --v1-local-data "$PWD/dtrm-fund/research/local_data" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_text_provenance.json" \
  --trust-historical-pickles
```

## Interpretation

- `TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN`:
  all five text fields can be reproduced row-for-row from frozen
  original text and source code. 384 embedding coordinates still OPEN.
- `TEXT_FEATURE_SOURCE_SCHEMA_UNRESOLVED`: V1 news snapshot has a
  different schema; locate the exact source/pipeline and do not
  rewrite the news file.
- `TEXT_FEATURE_SOURCE_KEYS_UNRESOLVED` or
  `TEXT_FEATURE_NEWS_COVERAGE_UNRESOLVED`: original text news-ID
  cardinality/coverage is incomplete or ambiguous.
- `TEXT_FEATURE_MISMATCH_REQUIRES_LINEAGE_INVESTIGATION`: stop,
  assess original text normalization/code/image/encoding provenance.
  Do not tune an approximate text processor against holdout features.

Even a full PASS is **only historical input provenance**. The
384 embedding dimensions must be matched against their original
precommitted sources or the limitation must be disclosed.
Separately, the V1 contract says 40,320 rows under the original raw
pair basename, whereas local raw input file holds 265,145. This
filename-to-cardinality inconsistency remains OPEN.

**No G1.3 fresh temporal holdout, new prediction, or return
evaluation is authorized by G1.2g.**
