# G1.1 — Additional input provenance and frozen-model existence audit

Date: 2026-10-27. ICOMPUTING-D-26-01069.
No prospective holdout has been approved. All steps are **metadata only**.

## Why G1.1 is needed
Initial G1.0 scanned `dtrm-fund` (497 visited/41 relevant) and
`theresistance-back` (450 visited/7 relevant); no filenames with
post-2026-07 date tokens were seen. That says nothing conclusive
about file internals, alternative local roots, or later data availability.

The original source `run_exante_baseline_v0.py` and
`run_probabilistic_xgb_v0.py` call `xgb.train` and have no direct
`save_model`/checkpoint call. Having saved cohort predictions and full
bootstrap reproduction does NOT demonstrate frozen model weights exist
for independent new inference. Find genuine model weight objects or
reconstruct and prove prediction-equivalence using old TRAIN/VALID and
historical replay before claiming "same frozen ranker."

## Additional operator-only local scan
From `~/Desktop/DTRM_Lab`, where these directories exist:
```bash
python3 "$HOME/dtrm-ic-audit/ic_g1_inventory.py" \
  --root "$PWD/theresistance" \
  --root "$PWD/theresistance-back-phase4-readback" \
  --root "$PWD/theresistance-back-g7-readback" \
  --out "$HOME/dtrm-ic-audit/IC_G1_additional_metadata_inventory.json"
```
If new snapshots are still not found, a separate, *optional*
metadata-only scan of `Phase4_offline_private` may identify
source provenance; this is not consent to read its confidential
contents or merge its experiments with the IC cohort.

## Show relevant file name samples from G1.0 only
```bash
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / "dtrm-ic-audit/IC_G1_metadata_inventory.json"
x = json.loads(p.read_text())
for alias, root in x["root_results"].items():
    for category in ("frozen_models_or_model_metadata", "news_snapshots", "price_snapshots"):
        cat = root.get("categories", {}).get(category)
        if cat:
            print(alias, category, cat.get("sample_filenames", []))
PY
```

## Gate decisions
- Confirm what is a **genuine saved model file** rather than a training
  dataset with "model" in its name; verify source and before/after timestamps.
- Confirm actual August/September event news, eligible tickers, price
  history, text-embedding dimensionality and fixed features. File name
  dates alone are insufficient.
- If no mature untouched cohort exists, design independent historical
  ingestion with licensed source, outcome-blind preregistration, and
  a feasible deadline; never opportunistically reuse evaluated cohorts.
- Keep Phase IV/STAMP/MM1 research scientifically separate from HDPG.
- Reviewer response must acknowledge any unavoidable reconstruction of
  model weights, retrospective news ingestion, non-independence or
  short test window.

Status: G1.1 **PENDING**. No new performance results.

## 2026-10-27 update: additional operator inventory and recovered exact legacy input path

Additional operator metadata-only inventory:
- `theresistance`: visited 751, 0 categorized matches.
- `theresistance-back-phase4-readback`: visited 402, 7 matches, no dated Aug+ filenames.
- `theresistance-back-g7-readback`: visited 480, 7 matches, no dated Aug+ filenames.
- No scientific target/return data opened.
- Existing `dtrm-fund` catalog's `legacy_model_rows_2026-05-01.pkl` is a MODEL ROWS DATASET not proof of an XGBoost model binary; `probabilistic_v2_frozen_p10_threshold.pkl` is a threshold artifact, not evidence of trained booster weights.
- `phase3_mm1_v5_price_snapshot.pkl` and `phase3_mm1_v6_price_snapshot.pkl` are MM1 evidence and require separate provenance and scientific isolation; do not silently substitute into the HDPG study.
- Backend `model_environment_v1.json`, `model_acceptance_policy_v1.json`, `ranking_model_policy_v1.json`, `research_model_lineage_v1.json` are metadata/policy filenames, not confirmed XGBoost booster weights.

**Source-code discovery:** both frozen `research/experiments/run_exante_baseline_v0.py`
and `research/experiments/run_probabilistic_xgb_v0.py` define:
```
OUTPUTS = ~/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs
PRICE_CACHE = OUTPUTS/price_cache_fmp_pickle
NEWS_PATH = OUTPUTS/news_2025-01-01_2026-05-01.pkl
EMBEDDING_DAT_PATH = OUTPUTS/news_emb_2025-01-01_2026-05-01.dat
EMBEDDING_SHAPE_PATH = OUTPUTS/news_emb_shape_2025-01-01_2026-05-01.pkl
EMBEDDING_INDEX_PATH = OUTPUTS/news_emb_index_2025-01-01_2026-05-01.pkl
```
These external historical paths were NOT included in initial G1.0 scans.
They are a priority: *verify existence* before discussing fresh ingestion.

### Next operator command (file metadata ONLY)

```bash
SRC="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs"
python3 "$HOME/dtrm-ic-audit/ic_g1_inventory.py" \
  --root "$SRC" \
  --out "$HOME/dtrm-ic-audit/IC_G1_legacy_outputs_metadata_inventory.json"

python3 - <<'PY'
from pathlib import Path
root = Path.home() / 'Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs'
print('ORIGINAL_OUTPUTS_EXISTS:', root.is_dir())
names = [
  'news_2025-01-01_2026-05-01.pkl',
  'news_emb_2025-01-01_2026-05-01.dat',
  'news_emb_shape_2025-01-01_2026-05-01.pkl',
  'news_emb_index_2025-01-01_2026-05-01.pkl',
]
for n in names:
    p = root / n
    print('INPUT', n, 'exists=', p.is_file(),
          'bytes=', p.stat().st_size if p.is_file() else None)
cache = root / 'price_cache_fmp_pickle'
print('PRICE_CACHE_EXISTS:', cache.is_dir())
if cache.is_dir():
    print('HISTORICAL_2026_07_05_PRICE_FILES:', len(list(cache.glob('*_2026-07-05.pkl'))))
PY
```
This command does not deserialize data or inspect price values, score values,
outcome labels or individual news records. The inventory may provide dated file
names only, not actual event-date distributions.

**G1.1 still OPEN** until the operator returns source metadata and genuine
frozen XGBoost weights (or a rigorously validated reconstruction route).
