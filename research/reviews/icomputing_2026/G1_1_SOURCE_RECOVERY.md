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

## 2026-10-27 operator result — legacy PCDoMoney source FOUND

Exact original notebook outputs root:
`~/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs`

Operator-reported read-only source existence and sizes:
- `news_2025-01-01_2026-05-01.pkl`: 12,973,286 bytes, present.
- `news_emb_2025-01-01_2026-05-01.dat`: 34,352,640 bytes, present.
- `news_emb_shape_2025-01-01_2026-05-01.pkl`: 20 bytes, present.
- `news_emb_index_2025-01-01_2026-05-01.pkl`: 670,844 bytes, present.
- `price_cache_fmp_pickle/`: present with 174 files ending `_2026-07-05.pkl`.
- Initial legacy Outputs G1.0 inventory: 3,717 files visited; 3,706 classified;
  3,649 price snapshots, 688 price filenames dated Aug or later, last date token 2026-08-15;
  news filenames <=2026-06-06; no news filenames dated Aug+.
- **Caveat**: `price` filename dates may reflect snapshot/export dates, not the last underlying stock trading date; the Aug 15 snapshot cannot be presumed to support target maturities through Oct 2026.
- No prospective news or target values were read during this inventory; this is availability evidence only.
- The first G1.0 broad catalog omitted `.dat` by extension, but direct operator check verifies the essential original embedding binary is present.

### Frozen scientific issues still to resolve
1. Identify actual fitted XGBoost point and quantile booster weights, rather than training files or model metadata.
2. Verify historical legacy input completeness, deterministic dependencies and original selected-iteration predictions.
3. Locate or acquire *newly sourced* post-August-18 news and post-October realized prices from authorized, versioned sources, outcome-blind before any inference.
4. Pre-register a sufficiently powered independent cohort; separation from prior 60-day targets must be checked on real trading-price intervals, not filename snapshots.
5. If old model weights cannot be found, reconstruct using only historical train/valid; demonstrate agreement with historic predictions before any new holdout inference.

### G1.1 targeted non-content lineage probe
Script: `ic_g1_lineage_probe.py`. Uses filenames and filesystem metadata only,
including possible XGBoost model binary names and distribution of price cache
filename snapshot dates. Classifications do not establish binary contents.

## 2026-10-27 G1.1 targeted model-candidate probe: operator-reported

Metadata-only terminal results:
- `Outputs`: 3,717 files visited; 0 likely serialized XGBoost `.ubj/.model/.bst/.joblib/.xgb` binaries, 14 filename-based possible JSON/pickle model candidates. Sample: `trump_score_xgb_excess_beta.json`, `trump_score_xgb_reg_excess_beta.json`, `trump_score_xgb_v1.json`. No prospective news filenames dated August+.
- `PCDoMoney_Backend`: 3,792 files visited; 0 known binary candidates, 15 unverified serialization candidates (overlap with Outputs).
- `dtrm-fund/research/local_data`: 51 files visited; no model candidates.
- Price cache has 3,649 historical files. Largest named snapshot date 2026-08-15, with 344 file names on that date. This is NOT evidence of underlying October 2026 price coverage.
- **No candidate has been inspected for actual booster structure or identity.** The filenames mostly indicate earlier Trump scoring models and may be incompatible with the 390-feature ex-ante ranker and quantile P10.
- **Frozen training source audit:** `run_exante_baseline_v0.py` trains an XGBoost point model with `reg:squarederror` and 390 features, selected ranking iteration 10. `run_probabilistic_xgb_v0.py` trains a separate `reg:quantileerror` P10 model (alpha 0.10, best iteration 18); no `save_model` instructions observed in either script.

### Next model identification gate
`research/reviews/icomputing_2026/ic_g1_booster_audit.py` may read ONLY JSON model candidate structures and report:
objective, feature count, tree count, version and SHA256.
It never runs model inference, inspects holdout targets or exports tree weights.
Any matching XGBoost schema is **a candidate, not proof** of model lineage.
If no exact weights exist, deterministic reconstruction must pass historical
validation and frozen predictions parity before independent replay.

Temporal holdout: **NOT AUTHORIZED**. G1.1 remains open.
