#!/usr/bin/env python3
"""G0 historical point-estimate replay for Intelligent Computing major revision.

Read-only to raw scientific artifacts. Runs on trusted local .pkl only after
explicit approval. No model fit, no data upload and no bootstrap. Uses the
same frozen selection logic as the 2026-08 original runner.

This script verifies point estimates, NOT full raw-data reconstruction,
training-code reproducibility or inferential CI replication.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

COHORTS = {
    "V2": {
        "signals": "probabilistic_v2_holdout_signals_2026-06-10.pkl",
        "targets": "probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
        "rows": 4449, "k": 444, "pass_rows": 2530,
        "start": "2026-06-07", "end": "2026-06-10",
        "baseline_mean": -0.1949552297592163,
        "candidate_mean": -0.050660423934459686,
        "delta_mean": 0.14429480582475662,
        "baseline_hit": 0.04504504504504504,
        "candidate_hit": 0.6238738738738738,
        "delta_hit": 0.5788288288288288,
    },
    "V3": {
        "signals": "probabilistic_v3_holdout_signals_2026-06-14.pkl",
        "targets": "probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
        "rows": 2827, "k": 282, "pass_rows": 1634,
        "start": "2026-06-11", "end": "2026-06-14",
        "baseline_mean": -0.1790371835231781,
        "candidate_mean": -0.029599694535136223,
        "delta_mean": 0.14943748898804188,
        "baseline_hit": 0.06028368794326241,
        "candidate_hit": 0.6453900709219859,
        "delta_hit": 0.5851063829787234,
    },
    "V4": {
        "signals": "probabilistic_v4_holdout_signals_2026-06-06.pkl",
        "targets": "probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
        "rows": 40320, "k": 4032, "pass_rows": 23348,
        "start": "2026-05-02", "end": "2026-06-06",
        "baseline_mean": -0.05458883196115494,
        "candidate_mean": -0.02702723816037178,
        "delta_mean": 0.027561593800783157,
        "baseline_hit": 0.3864087301587302,
        "candidate_hit": 0.4880952380952381,
        "delta_hit": 0.10168650793650791,
    },
}

TOPK_FRACTION = 0.10
ATOL = 1e-12
PRUNE = {
    ".git", ".Trash", ".venv", "venv", "__pycache__", "node_modules",
    ".cache", ".npm", ".cargo", ".rustup", "Library",
}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def discover(root: Path, names: set[str]) -> dict[str, Path]:
    hits: dict[str, list[Path]] = {name: [] for name in names}
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in PRUNE and not (Path(parent) / d).is_symlink()]
        for name in names.intersection(files):
            candidate = Path(parent) / name
            if candidate.is_file() and not candidate.is_symlink():
                hits[name].append(candidate)
    ambiguous = [name for name, paths in hits.items() if len(paths) != 1]
    if ambiguous:
        raise RuntimeError("Missing or ambiguous local files: " + ", ".join(sorted(ambiguous)))
    return {name: paths[0] for name, paths in hits.items()}

def trusted_paths(root: Path, prior_manifest: Path) -> dict[str, Path]:
    manifest = json.loads(prior_manifest.read_text(encoding="utf-8"))
    names = {
        spec[key] for spec in COHORTS.values()
        for key in ("signals", "targets")
    }
    paths = discover(root, names)
    old = manifest.get("artifacts", {})
    for name, path in paths.items():
        prior = old.get(name, {})
        variants = prior.get("variants", [])
        if prior.get("copies") != 1 or len(variants) != 1:
            raise RuntimeError(f"Discovery manifest lacks unique copy of {name}")
        expected = variants[0].get("sha256")
        if not expected or sha256(path) != expected:
            raise RuntimeError(f"SHA256 differs from discovery manifest: {name}")
        anchored = prior.get("expected_sha256")
        if anchored and (expected != anchored or variants[0].get("integrity") != "MATCH"):
            raise RuntimeError(f"Historical SHA256 mismatch: {name}")
    return paths

def evaluate(df):
    """Identical ordering/capacity convention to frozen primary bootstrap runner."""
    import numpy as np
    pred = df["baseline_prediction"].to_numpy()
    eligible = df["p10_pass"].to_numpy(dtype=bool)
    y = df["target_model"].to_numpy()
    n = len(df)
    k = int(n * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("Empty Top-K")
    order = np.argsort(-pred)
    baseline = order[:k]
    valid = order[eligible[order]]
    if len(valid) < k:
        raise RuntimeError("Guardrail cannot fill Top-K")
    candidate = valid[:k]
    b = float(y[baseline].mean())
    c = float(y[candidate].mean())
    bh = float((y[baseline] > 0).mean())
    ch = float((y[candidate] > 0).mean())
    return {
        "rows": n, "k": k, "pass_rows": int(eligible.sum()),
        "baseline_mean": b, "candidate_mean": c, "delta_mean": c - b,
        "baseline_hit": bh, "candidate_hit": ch, "delta_hit": ch - bh,
    }

def load_pair(signals_path: Path, targets_path: Path):
    import numpy as np
    import pandas as pd
    signals = pd.read_pickle(signals_path)
    targets = pd.read_pickle(targets_path)
    required_signals = {"news_id", "ticker", "date_dt", "baseline_prediction", "p10_pass"}
    required_targets = {"news_id", "ticker", "date_dt", "target_model"}
    if not required_signals.issubset(signals.columns):
        raise ValueError("Required signal columns absent")
    if not required_targets.issubset(targets.columns):
        raise ValueError("Required target columns absent")
    if signals.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicated signal news_id/ticker")
    if targets.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicated target news_id/ticker")
    df = signals.merge(
        targets[["news_id", "ticker", "date_dt", "target_model"]],
        on=["news_id", "ticker"], how="inner",
        validate="one_to_one", sort=False,
        suffixes=("_signal", "_target"),
    )
    if len(df) != len(signals) or len(df) != len(targets):
        raise ValueError("Incomplete one-to-one pair merge")
    sdates = pd.to_datetime(df["date_dt_signal"], utc=True)
    tdates = pd.to_datetime(df["date_dt_target"], utc=True)
    if not sdates.equals(tdates):
        raise ValueError("Signal/target timestamp mismatch")
    for col in ("baseline_prediction", "target_model"):
        if not np.isfinite(df[col].to_numpy()).all():
            raise ValueError("Nonfinite value in " + col)
    pass_values = df["p10_pass"]
    if pass_values.isna().any() or not pass_values.isin([True, False]).all():
        raise ValueError("Nonboolean or missing p10_pass")
    return df, sdates

def run(paths: dict[str, Path]) -> dict:
    import numpy as np
    output = {}
    complete = True
    for name, spec in COHORTS.items():
        df, dates = load_pair(paths[spec["signals"]], paths[spec["targets"]])
        actual = evaluate(df)
        date_min = dates.min().date().isoformat()
        date_max = dates.max().date().isoformat()
        checks = {
            "rows": actual["rows"] == spec["rows"],
            "k": actual["k"] == spec["k"],
            "pass_rows": actual["pass_rows"] == spec["pass_rows"],
            "date_min": date_min == spec["start"],
            "date_max": date_max == spec["end"],
        }
        for field in ("baseline_mean", "candidate_mean", "delta_mean",
                      "baseline_hit", "candidate_hit", "delta_hit"):
            checks[field] = bool(np.isclose(
                actual[field], spec[field], rtol=0, atol=ATOL
            ))
        passed = all(checks.values())
        complete &= passed
        output[name] = {
            "status": "PASS" if passed else "FAIL",
            "checks": checks,
            "observed": actual,
            "signal_date_range": [date_min, date_max],
            "unique_news": int(df["news_id"].nunique()),
            "unique_tickers": int(df["ticker"].nunique()),
        }
        print(f"{name}: {'PASS' if passed else 'FAIL'}; "
              f"rows={actual['rows']}; K={actual['k']}; "
              f"pass_rows={actual['pass_rows']}; "
              f"delta_mean={actual['delta_mean']:+.12f}")
    return {
        "schema_version": "dtrm.ic.g0.point_replay.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "frozen_tag": "dtrm-xgb-probabilistic-phase2-stats",
            "frozen_commit": "c7502a690162459cdfb3413573e3133c42efb126",
            "original_logic": "research/experiments/run_phase2_primary_bootstrap.py",
        },
        "status": "POINT_REPLAY_PASS_NOT_RAW_REPRODUCED"
                  if complete else "POINT_REPLAY_FAIL",
        "cohorts": output,
        "limits": [
            "Only existing historical signals and targets are replayed",
            "No raw news/prices reconstructed; no model inference or fitting",
            "No bootstrap confidence intervals computed",
            "Unanchored artifacts have only same-as-discovery SHA evidence",
        ],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-root", required=True)
    parser.add_argument("--discovery-manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--trust-local-pickles", action="store_true",
        help="Required because loading Python pickle data can execute code; "
             "only use on trusted original local research artifacts."
    )
    args = parser.parse_args()
    if not args.trust_local_pickles:
        parser.error("Explicit --trust-local-pickles is required")
    root = Path(args.search_root).expanduser().resolve()
    prior = Path(args.discovery_manifest).expanduser()
    result = run(trusted_paths(root, prior))
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print("Replay report:", out)
    print("G0:", result["status"])
    return 0 if result["status"] == "POINT_REPLAY_PASS_NOT_RAW_REPRODUCED" else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G0 point replay aborted: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)
