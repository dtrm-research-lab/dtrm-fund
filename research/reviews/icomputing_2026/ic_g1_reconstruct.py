#!/usr/bin/env python3
"""G1.2 reproducibility-controlled HDPG model reconstruction.

Requires a detached clone at the exact historical source commit.
Preflight never opens scientific files. --rebuild opens ONLY trusted
historical training inputs and re-executes frozen V0 source functions.
Nothing prospective or from MM1/Phase IV is imported.

Outputs remain UNAPPROVED pending per-row historical prediction parity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
BASE_SOURCE = "research/experiments/run_exante_baseline_v0.py"
QUANT_SOURCE = "research/experiments/run_probabilistic_xgb_v0.py"
RAW_NAMES = [
    "legacy_pairs_enriched_2025-01-01_2026-05-01.pkl",
    "legacy_model_rows_2026-05-01.pkl",
]
EXTERNAL_NAMES = [
    "news_2025-01-01_2026-05-01.pkl",
    "news_emb_2025-01-01_2026-05-01.dat",
    "news_emb_shape_2025-01-01_2026-05-01.pkl",
    "news_emb_index_2025-01-01_2026-05-01.pkl",
]

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def frozen_head(root: Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()

def preflight(root: Path, legacy_data: Path, outputs: Path) -> dict:
    code_head = frozen_head(root)
    if code_head != PIN:
        raise RuntimeError(f"Incorrect frozen source commit: {code_head} (expected {PIN})")
    dirty = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if dirty:
        raise RuntimeError("Frozen source clone has tracked local modifications")
    code_files = {name: root / name for name in (BASE_SOURCE, QUANT_SOURCE)}
    missing_code = [name for name,p in code_files.items() if not p.is_file()]
    if missing_code:
        raise RuntimeError(f"Missing historic code: {missing_code}")
    inputs = {name: legacy_data / name for name in RAW_NAMES}
    inputs.update({name: outputs / name for name in EXTERNAL_NAMES})
    missing = [name for name,p in inputs.items() if not p.is_file()]
    price_cache = outputs / "price_cache_fmp_pickle"
    price_files = sorted(price_cache.glob("*_2026-07-05.pkl")) if price_cache.is_dir() else []
    from importlib.metadata import version, PackageNotFoundError
    environment = {}
    for package in ("numpy", "pandas", "xgboost", "sentence-transformers"):
        try:
            environment[package] = version(package)
        except PackageNotFoundError:
            environment[package] = "NOT_INSTALLED"
    result = {
        "historical_commit_verified": True,
        "environment_package_versions": environment,
        "source_files_sha256": {name: sha256(p) for name,p in code_files.items()},
        "training_inputs": {
            name: {"present": p.is_file(), "bytes": p.stat().st_size if p.is_file() else None}
            for name,p in inputs.items()
        },
        "source_paths": {
            "price_cache_present": price_cache.is_dir(),
            "price_2026_07_05_named_snapshots": len(price_files),
            "news_and_embedding_files_present": all((outputs / n).is_file() for n in EXTERNAL_NAMES),
        },
        "no_scientific_data_contents_inspected": True,
        "can_begin_historical_reconstruction": (
            not missing and len(price_files) == 174
        ),
    }
    return result

def load_frozen_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load source " + name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def close(actual: float, expected: float, atol: float = 1e-6) -> bool:
    import numpy as np
    return bool(np.isclose(float(actual), float(expected), atol=atol, rtol=0))

def historical_rebuild(root: Path, legacy_data: Path, outputs: Path, out: Path) -> dict:
    import numpy as np
    import pandas as pd
    import xgboost as xgb

    # Use old repository source, not a mutable working branch.
    sys.path.insert(0, str(root / "src"))
    base = load_frozen_module("ic_pinned_baseline", root / BASE_SOURCE)
    quant = load_frozen_module("ic_pinned_quantile", root / QUANT_SOURCE)
    for module in (base, quant):
        module.LOCAL_DATA = legacy_data
        module.FULL_ROWS_PATH = legacy_data / RAW_NAMES[0]
        module.MODEL_ROWS_PATH = legacy_data / RAW_NAMES[1]
        module.OUTPUTS = outputs
        module.PRICE_CACHE = outputs / "price_cache_fmp_pickle"
        module.NEWS_PATH = outputs / EXTERNAL_NAMES[0]
        module.EMBEDDING_DAT_PATH = outputs / EXTERNAL_NAMES[1]
        module.EMBEDDING_SHAPE_PATH = outputs / EXTERNAL_NAMES[2]
        module.EMBEDDING_INDEX_PATH = outputs / EXTERNAL_NAMES[3]

    print("Reconstructing original feature matrix from old TRAIN/VALID/TEST inputs")
    _, rows = base.load_ordered_model_rows()
    prices = base.load_exante_price_cache()
    raw_y = base.build_exante_raw_targets(rows, prices)
    X = base.build_exante_feature_matrix(rows)
    if X.ndim != 2 or X.shape[1] != 390:
        raise RuntimeError("Historical feature count mismatch (expected 390)")
    if len(X) != len(rows) or not np.isfinite(X).all():
        raise RuntimeError("Feature rows mismatch or nonfinite feature values")

    masks, targets, weights = base.prepare_training_data(rows, raw_y)
    masks2, targets2, weights2 = quant.prepare_training_data(rows, raw_y)
    for part in ("train","valid","test"):
        if not np.array_equal(masks[part],masks2[part]):
            raise RuntimeError("Baseline/quantile original masks differ")
        if not np.array_equal(targets[part],targets2[part]):
            raise RuntimeError("Baseline/quantile original target transforms differ")
        if not np.array_equal(weights[part],weights2[part]):
            raise RuntimeError("Baseline/quantile original weights differ")

    print("Training original ex-ante point ranker from frozen code")
    ranker, base_matrices, _history = base.train_legacy_model(
        X, rows, masks, targets, weights
    )
    topk = base.select_legacy_topk(ranker, base_matrices, targets)
    print("Training original P10/P50/P90 quantiles from frozen code")
    q_matrices = quant.build_dmatrices(X, masks2, targets2, weights2)
    qmodels, _history_q = quant.train_quantile_models(q_matrices)
    p10 = qmodels["p10"]
    valid_p10_raw = quant.predict_at_iteration(
        p10, q_matrices["valid"], int(p10.best_iteration)
    )
    offset = quant.weighted_quantile(
        targets2["valid"]-valid_p10_raw, weights2["valid"], 0.10
    )
    threshold = quant.weighted_quantile(
        valid_p10_raw + offset, weights2["valid"], 0.25
    )
    observed = {
        "feature_matrix_shape": list(X.shape),
        "split_sizes": {k: int(v.sum()) for k,v in masks.items()},
        "ranker_best_iteration": int(ranker.best_iteration),
        "ranker_best_score": float(ranker.best_score),
        "ranker_selected_topk_iteration": int(topk.iteration),
        "ranker_valid_topk_mean": float(topk.topk_mean),
        "ranker_valid_topk_hit_rate": float(topk.topk_hit_rate),
        "p10_best_iteration": int(p10.best_iteration),
        "p10_best_score": float(p10.best_score),
        "p50_best_iteration": int(qmodels["p50"].best_iteration),
        "p90_best_iteration": int(qmodels["p90"].best_iteration),
        "p10_calibration_offset": offset,
        "relative_veto_threshold": threshold,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "xgboost": xgb.__version__,
    }

    checks = {
        "features_390": observed["feature_matrix_shape"][1] == 390,
        "ranker_best_iteration_6": observed["ranker_best_iteration"] == 6,
        "ranker_rmse": close(observed["ranker_best_score"],0.13148387466227393),
        "ranker_topk_iteration_10": observed["ranker_selected_topk_iteration"] == 10,
        "ranker_valid_mean": close(observed["ranker_valid_topk_mean"],-0.023497406393289566),
        "ranker_valid_hit": close(observed["ranker_valid_topk_hit_rate"],0.2857142857142857),
        "p10_best_iteration_18": observed["p10_best_iteration"] == 18,
        "p10_valid_pinball": close(observed["p10_best_score"],0.02465790502590275),
        "p50_best_iteration_19": observed["p50_best_iteration"] == 19,
        "p90_best_iteration_0": observed["p90_best_iteration"] == 0,
        "p10_calibration": close(offset,-0.06494169682264328),
        "veto_threshold": close(threshold,-0.16665692627429962),
    }
    result = {
        "status": "HISTORICAL_AGGREGATE_PARITY_ONLY"
                  if all(checks.values()) else "HISTORICAL_REBUILD_MISMATCH",
        "observed": observed,
        "checks": checks,
        "scientific_limit": (
            "Aggregate historical metrics are NOT row-level prediction parity. "
            "Model identity remains UNAPPROVED; no new cohort may be scored."
        ),
        "candidate_model_sha256": {},
    }
    # Only save models when the aggregate gates pass. Still label UNAPPROVED.
    if all(checks.values()):
        folder = out / "reconstructed_UNAPPROVED"
        folder.mkdir(parents=True, exist_ok=False)
        for name,model in (("exante_ranker",ranker),
                           ("p10",qmodels["p10"]),
                           ("p50",qmodels["p50"]),
                           ("p90",qmodels["p90"])):
            target = folder / (name+".ubj")
            model.save_model(str(target))
            result["candidate_model_sha256"][target.name] = sha256(target)
    return result

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen-repo",required=True)
    ap.add_argument("--legacy-local-data",required=True)
    ap.add_argument("--legacy-outputs",required=True)
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--mode",choices=["preflight","rebuild"],default="preflight")
    ap.add_argument("--trust-historical-pickles",action="store_true")
    args = ap.parse_args()
    root = Path(args.frozen_repo).expanduser().resolve()
    local = Path(args.legacy_local_data).expanduser().resolve()
    legacy = Path(args.legacy_outputs).expanduser().resolve()
    out = Path(args.out_dir).expanduser()
    out.mkdir(parents=True,exist_ok=True)
    name = "IC_G1_2_"+args.mode+".json"
    report_file = out / name
    if report_file.exists():
        ap.error("Refusing to overwrite prior attempt report "+str(report_file))
    pf = preflight(root,local,legacy)
    report = {
        "schema_version":"dtrm.ic.g1.historical_rebuild.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "mode":args.mode,
        "frozen_source_commit": PIN,
        "preflight":pf,
        "prospective_holdout_opened":False,
        "status":"PRECHECK_ONLY",
    }
    if args.mode == "rebuild":
        if not args.trust_historical_pickles:
            ap.error("Rebuild requires explicit --trust-historical-pickles")
        if not pf["can_begin_historical_reconstruction"]:
            ap.error("Historical inputs not complete; cannot train")
        print("NOTE: Reads trusted historical Pickles, never uninspected prospective data")
        report["reconstruction"] = historical_rebuild(root,local,legacy,out)
        report["status"] = report["reconstruction"]["status"]
    report_file.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2:",report["status"])
    print("Audit report:",report_file)
    if args.mode=="preflight":
        print("Legacy inputs available:",pf["can_begin_historical_reconstruction"])
        print("Original July 5 price files:",pf["source_paths"]["price_2026_07_05_named_snapshots"])
        print("NO Pickle files loaded; no models trained")
    else:
        for k,v in report["reconstruction"]["checks"].items():
            print(k, "PASS" if v else "FAIL")
        print("WARNING: candidate models UNAPPROVED pending row-level prediction parity")
    return 0 if report["status"] in ("PRECHECK_ONLY","HISTORICAL_AGGREGATE_PARITY_ONLY") else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G1.2 aborted: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(3)
