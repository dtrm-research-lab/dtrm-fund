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
