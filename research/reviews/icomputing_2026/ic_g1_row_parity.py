#!/usr/bin/env python3
"""IC G1.2b: historical frozen holdout row-level prediction parity.

Uses ONLY original V1/V4 historical features and signals with V4 SHA256
anchors plus locally rebuilt UNAPPROVED booster files. No new holdout,
no raw news, no target outcomes, no retraining or live inference.

Preserves no individual predictions in report; all checks are aggregate.
In absence of numerical historic calibrated P10 signal, gates cannot
fully approve P10 rowwise numerical parity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

FEATURE_NAME = "probabilistic_v1_holdout_features_2026-06-06.npy"
SIGNALS_NAME = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
EXPECTED_HASHES = {
    FEATURE_NAME: "a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750",
    SIGNALS_NAME: "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b",
}
PIN = "c7502a690162459cdfb3413573e3133c42efb126"
OFFSET = -0.06494169682264328
THRESHOLD = -0.16665692627429962
P10_NUMERIC_MAP = {
    "p10_calibrated": "calibrated",
    "calibrated_p10": "calibrated",
    "p10_calibrated_prediction": "calibrated",
    "p10_prediction_calibrated": "calibrated",
    "calibrated_p10_prediction": "calibrated",
    "p10_raw": "raw",
    "p10_raw_prediction": "raw",
    "raw_p10_prediction": "raw",
    "p10_prediction": "unknown", # never infer raw vs calibrated from ambiguous name
}
PRUNE = {".git", ".Trash", ".venv", "venv", "node_modules",
         "__pycache__", ".cache", ".npm", ".cargo", ".rustup", "Library"}

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def locate(root, names):
    found = {x: [] for x in names}
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [x for x in dirs if x not in PRUNE
                   and not (Path(parent) / x).is_symlink()]
        for n in names.intersection(files):
            p = Path(parent)/n
            if p.is_file() and not p.is_symlink():
                found[n].append(p)
    duplicates = [name for name, hits in found.items() if len(hits) != 1]
    if duplicates:
        raise RuntimeError("Original historical artifacts absent or ambiguous: "
                           + ", ".join(sorted(duplicates)))
    result = {n: found[n][0] for n in names}
    for name,p in result.items():
        if digest(p) != EXPECTED_HASHES[name]:
            raise RuntimeError("Historical original SHA256 mismatch: "+name)
    return result

def stats(actual, expected, tolerance):
    import numpy as np
    arr = np.asarray(actual, dtype=np.float64)
    ref = np.asarray(expected, dtype=np.float64)
    if arr.ndim != 1 or ref.ndim != 1 or len(arr) != len(ref):
        raise ValueError("Prediction length mismatch")
    if not np.isfinite(arr).all() or not np.isfinite(ref).all():
        raise ValueError("Nonfinite numeric predictions")
    diff = np.abs(arr-ref)
    mask = diff <= tolerance
    return {
        "rows": len(arr), "tolerance": tolerance,
        "max_abs_difference": float(diff.max()),
        "mean_abs_difference": float(diff.mean()),
        "exceeding_tolerance": int((~mask).sum()),
        "within_tolerance": bool(mask.all()),
    }

def run(root, report_json, model_folder):
    import numpy as np
    import pandas as pd
    import xgboost as xgb

    evidence = json.loads(report_json.read_text(encoding="utf-8"))
    if evidence.get("status") != "HISTORICAL_AGGREGATE_PARITY_ONLY":
        raise RuntimeError("G1.2 historical aggregate gate not passed")
    if evidence.get("frozen_source_commit") != PIN:
        raise RuntimeError("G1.2 pinned original source not matching")
    if not all(evidence.get("reconstruction",{}).get("checks",{}).values()):
        raise RuntimeError("Incomplete G1.2 historical reconstruction checks")
    model_sha = evidence.get("reconstruction",{}).get("candidate_model_sha256",{})
    if "exante_ranker.ubj" not in model_sha or "p10.ubj" not in model_sha:
        raise RuntimeError("G1.2 candidate model SHA evidence is missing")
    for filename in ("exante_ranker.ubj","p10.ubj"):
        p = model_folder / filename
        if not p.is_file() or digest(p) != model_sha[filename]:
            raise RuntimeError("Saved reconstructed model SHA mismatch: "+filename)

    files = locate(root, set(EXPECTED_HASHES))
    X = np.load(files[FEATURE_NAME], allow_pickle=False)
    if X.ndim != 2 or X.shape != (40320,390):
        raise RuntimeError(f"Historical feature shape unexpected: {X.shape}")
    if not np.issubdtype(X.dtype, np.number) or not np.isfinite(X).all():
        raise RuntimeError("Historical features missing or nonfinite")
    signals = pd.read_pickle(files[SIGNALS_NAME])
    if not isinstance(signals, pd.DataFrame) or len(signals) != len(X):
        raise RuntimeError("Original frozen signals not 1:1 with feature matrix")
    if not {"news_id","ticker","date_dt","baseline_prediction","p10_pass"}.issubset(signals.columns):
        raise RuntimeError("Frozen original signals missing required columns")
    if signals.duplicated(["news_id","ticker"]).any():
        raise RuntimeError("Original signal pair identifiers are duplicated")
    if signals["p10_pass"].isna().any() or not signals["p10_pass"].isin([True,False]).all():
        raise RuntimeError("Original p10_pass is not a valid Boolean field")

    matrix = xgb.DMatrix(X)
    base = xgb.Booster()
    base.load_model(str(model_folder / "exante_ranker.ubj"))
    p10 = xgb.Booster()
    p10.load_model(str(model_folder / "p10.ubj"))

    rank = base.predict(matrix, iteration_range=(0,11))
    baseline = stats(rank, signals["baseline_prediction"].to_numpy(), 1e-6)

    p10_raw = p10.predict(matrix, iteration_range=(0,19))
    p10_calibrated = p10_raw + OFFSET
    admitted = p10_calibrated >= THRESHOLD
    expected_admitted = signals["p10_pass"].to_numpy(dtype=bool)
    decisions = {
        "rows": len(admitted),
        "reconstructed_pass": int(admitted.sum()),
        "original_pass": int(expected_admitted.sum()),
        "disagreements": int((admitted != expected_admitted).sum()),
        "exact_pass_match": bool(np.array_equal(admitted, expected_admitted)),
    }
    p10_matches = {}
    for column, convention in P10_NUMERIC_MAP.items():
        if column not in signals.columns:
            continue
        if convention == "unknown":
            p10_matches[column] = {
                "status":"AMBIGUOUS_RAW_OR_CALIBRATED_COLUMN_NOT_EVALUATED",
            }
            continue
        values = signals[column]
        if not pd.api.types.is_numeric_dtype(values):
            p10_matches[column] = {"status":"NONNUMERIC_REFERENCE"}
            continue
        reference = values.to_numpy()
        predicted = p10_calibrated if convention=="calibrated" else p10_raw
        p10_matches[column] = stats(predicted, reference, 1e-6)
    recognized = [
        v for v in p10_matches.values()
        if isinstance(v,dict) and "within_tolerance" in v
    ]
    numeric_pass = any(v["within_tolerance"] for v in recognized)
    base_pass = baseline["within_tolerance"]
    decisions_pass = decisions["exact_pass_match"]
    if not base_pass or not decisions_pass:
        status = "HISTORICAL_ROW_PARITY_FAIL"
    elif numeric_pass:
        status = "HISTORICAL_NUMERIC_PARITY_PASS_PROVENANCE_PENDING"
    else:
        status = "PARTIAL_BASELINE_AND_P10_VETO_PARITY_ONLY"
    return {
        "schema_version": "dtrm.ic.g1.rowlevel_parity.v1",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "source_pin": PIN,
        "status":status,
        "frozen_rows":len(signals),
        "frozen_features":X.shape[1],
        "original_signal_columns": sorted(str(x) for x in signals.columns),
        "original_artifacts_sha256_verified":True,
        "reconstructed_model_sha256_verified":True,
        "baseline_numeric_parity":baseline,
        "p10_veto_parity":decisions,
        "p10_numeric_parity_candidates":p10_matches,
        "p10_numeric_full_parity_verified": numeric_pass,
        "row_keys_identified": True,
        "feature_to_signal_row_provenance_certified": False,
        "warning": (
            "Rowwise prediction match supports ordered linkage but the stored "
            "feature matrix lacks embedded pair IDs. Original feature construction "
            "and mapping provenance must be corroborated separately. No prospective "
            "cohort has been opened, and no trading-return validation is claimed."
        )
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--search-root", required=True)
    p.add_argument("--rebuild-report", required=True)
    p.add_argument("--models-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--trust-original-pickles",action="store_true")
    args=p.parse_args()
    if not args.trust_original_pickles:
        p.error("Requires explicit --trust-original-pickles for trusted historic local data")
    outfile=Path(args.out).expanduser()
    if outfile.exists():
        p.error("Refusing to overwrite existing parity output")
    result=run(
        Path(args.search_root).expanduser(),
        Path(args.rebuild_report).expanduser(),
        Path(args.models_dir).expanduser(),
    )
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                       encoding="utf-8")
    print("G1.2b:",result["status"])
    for key in ("baseline_numeric_parity","p10_veto_parity"):
        print(key,result[key])
    print("P10 numeric candidate columns:", list(result["p10_numeric_parity_candidates"]))
    print("Historical signal columns:",result["original_signal_columns"])
    print("Audit:",outfile)
    print("NO prospective outcome data opened; models remain UNAPPROVED.")
    return 2 if result["status"]=="HISTORICAL_ROW_PARITY_FAIL" else 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G1.2b halted: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(3)
