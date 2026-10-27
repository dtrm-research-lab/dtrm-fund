#!/usr/bin/env python3
"""IC G1.1: safe structural audit of local JSON model candidates.

This script is strictly a *model structure* audit: it reads JSON candidates,
but never unpickles, runs XGBoost, uses historical inputs or reads returns.
Reports only metadata, never tree node/leaf values or feature weights.

A compatible XGBoost JSON is NOT authenticated as the frozen HDPG model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

MODEL_HINTS = ("trump_score_xgb", "xgb", "quantile", "booster", "ranker")
SKIP_HINTS = ("summary", "policy", "lineage", "manifest", "test_result", "target")
MAX_BYTES = 100_000_000
MAX_FILES = 1000


def safe_obj(obj):
    return obj if isinstance(obj, dict) else {}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_model_header(path: Path) -> dict:
    size = path.stat().st_size
    metadata = {"file_name": path.name, "bytes": size, "sha256": sha256_file(path)}
    if size > MAX_BYTES:
        metadata["classification"] = "SKIPPED_SIZE_LIMIT"
        return metadata

    try:
        with path.open(encoding="utf-8") as f:
            contents = json.load(f)
    except (ValueError, UnicodeDecodeError, OSError) as exc:
        metadata["classification"] = "INVALID_OR_UNREADABLE_JSON"
        metadata["error_type"] = type(exc).__name__
        return metadata

    root = safe_obj(contents)
    learner = safe_obj(root.get("learner"))
    booster = safe_obj(learner.get("gradient_booster"))
    mdl = safe_obj(booster.get("model"))
    if not learner or not booster:
        metadata["classification"] = "NOT_XGBOOST_SAVED_MODEL_SCHEMA"
        metadata["json_root_keys"] = sorted(root)[:12]
        return metadata

    learner_param = safe_obj(learner.get("learner_model_param"))
    objective = safe_obj(learner.get("objective"))
    objective_name = objective.get("name")
    if not isinstance(objective_name, str):
        objective_name = None

    alpha = None
    for subkey in ("quantile_loss_param", "reg_loss_param"):
        sub = safe_obj(objective.get(subkey))
        if "quantile_alpha" in sub:
            alpha = sub.get("quantile_alpha")
            break

    ntrees = None
    trees = mdl.get("trees")
    if isinstance(trees, list):
        ntrees = len(trees)
    else:
        params = safe_obj(mdl.get("gbtree_model_param"))
        ntrees = params.get("num_trees")

    try:
        n_features = int(learner_param.get("num_feature"))
    except (TypeError, ValueError):
        n_features = None

    version = root.get("version")
    if not isinstance(version, list):
        version = None

    is_390 = n_features == 390
    is_baseline = objective_name == "reg:squarederror"
    is_p10 = objective_name == "reg:quantileerror"

    metadata.update({
        "classification": "STRUCTURALLY_VALID_XGBOOST_JSON_CANDIDATE",
        "objective": objective_name,
        "n_features": n_features,
        "trees": ntrees,
        "save_format_version": version,
        "booster_name": booster.get("name"),
        "quantile_alpha_reported": alpha,
        "could_be_390_feature_baseline": bool(is_390 and is_baseline),
        "could_be_390_feature_p10": bool(is_390 and is_p10),
        "identity_confirmed_as_frozen_HDPG": False,
    })
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True,
                        help="Original trusted directory with model JSON files")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    folder = Path(args.directory).expanduser()
    if not folder.is_dir():
        parser.error("Model directory not found")
    report = Path(args.out).expanduser()
    if report.exists():
        parser.error("Refusing to overwrite previous audit report")

    chosen = []
    for p in sorted(folder.rglob("*.json"), key=lambda x: str(x)):
        if p.is_symlink() or not p.is_file():
            continue
        name = p.name.lower()
        if any(h in name for h in MODEL_HINTS) and not any(s in name for s in SKIP_HINTS):
            chosen.append(p)
            if len(chosen) >= MAX_FILES:
                break

    results = [read_model_header(path) for path in chosen]
    summary = {
        "scanned_json_candidates": len(results),
        "saved_booster_candidates": sum(
            x.get("classification") == "STRUCTURALLY_VALID_XGBOOST_JSON_CANDIDATE"
            for x in results
        ),
        "feature390_baseline_candidates": sum(
            x.get("could_be_390_feature_baseline", False) for x in results
        ),
        "feature390_p10_candidates": sum(
            x.get("could_be_390_feature_p10", False) for x in results
        ),
        "historical_HDPG_identity_verified": False,
    }
    payload = {
        "schema_version": "dtrm.ic.g1.booster_json_metadata.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "model_json_candidates": results,
        "safety": {
            "no_market_or_event_data_read": True,
            "no_outcome_values_read": True,
            "no_models_executed": True,
            "no_tree_weights_exported": True,
            "no_raw_paths_reported": True,
        },
        "interpretation": "Structural candidates only: objective/features are not proof of frozen HDPG identity.",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("G1.1 — XGBoost JSON structural audit")
    for row in results:
        print(row["file_name"], "|", row["classification"],
              "| features:", row.get("n_features", "?"),
              "| objective:", row.get("objective", "?"),
              "| trees:", row.get("trees", "?"))
    print("Summary:", summary)
    print("Report:", report)
    print("NO target values, market returns, predictions or model inference inspected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
