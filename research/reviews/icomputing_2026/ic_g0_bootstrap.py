#!/usr/bin/env python3
"""Verify historical G0 bootstrap CIs using byte-exact frozen August 2026 runners.

Never changes original research records. Reads trusted local Pickles only after
--trust-local-pickles and checks them against the earlier discovery manifest.
Writes aggregated summaries/distributions to an audit-only directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

PINNED_COMMIT = "c7502a690162459cdfb3413573e3133c42efb126"
BLOBS = {
    "run_phase2_primary_bootstrap.py": "88b2cb9e76cdfc10f9afab982847aa13c16bbe10",
    "run_phase2_ticker_bootstrap.py": "2fbe7c4a90ee431cf382100c11707d37fa9defb0",
}
NAMES = {
    "V2": (
        "probabilistic_v2_holdout_signals_2026-06-10.pkl",
        "probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
    ),
    "V3": (
        "probabilistic_v3_holdout_signals_2026-06-14.pkl",
        "probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
    ),
    "V4": (
        "probabilistic_v4_holdout_signals_2026-06-06.pkl",
        "probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
    ),
}
EXPECTED_CIS = {
    "news": {
        "V2": {"mean": [0.12422081055119634, 0.1529691657051444],
               "hit": [0.5062970261097139, 0.609375]},
        "V3": {"mean": [0.12443295484408737, 0.16876715365506242],
               "hit": [0.49097472924187735, 0.64102787456446]},
        "V4": {"mean": [0.020819739997386934, 0.032413393817842],
               "hit": [0.08152519907128697, 0.13842317931436227]},
    },
    "ticker": {
        "V2": {"mean": [-0.006220224499702454, 0.19615343257319176],
               "hit": [-0.007422653940288334, 0.7869257290241077]},
        "V3": {"mean": [0.007538507026038135, 0.193316538631916],
               "hit": [0.026547834540091176, 0.79931338028169]},
        "V4": {"mean": [-0.010468163806945084, 0.07181955866981293],
               "hit": [-0.007457728649162368, 0.28585617483056575]},
    },
}
PRUNE = {".git", ".Trash", ".venv", "venv", "__pycache__", "node_modules",
         ".cache", ".npm", ".cargo", ".rustup", "Library"}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def git_blob_sha(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode("ascii") + b"\0" + b).hexdigest()

def find_local(root: Path, names: set[str]) -> dict[str, Path]:
    found: dict[str, list[Path]] = {n: [] for n in names}
    for dirname, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in PRUNE and
                   not (Path(dirname) / d).is_symlink()]
        for n in names.intersection(files):
            p = Path(dirname) / n
            if p.is_file() and not p.is_symlink():
                found[n].append(p)
    bad = sorted(n for n, matches in found.items() if len(matches) != 1)
    if bad:
        raise RuntimeError("Missing or ambiguous local inputs: " + ", ".join(bad))
    return {n: matches[0] for n, matches in found.items()}

def verify_inputs(files: dict[str, Path], discovery_path: Path) -> None:
    manifest = json.loads(discovery_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "dtrm.ic.g0.discovery.v1":
        raise RuntimeError("Unexpected discovery manifest schema")
    for name, path in files.items():
        original = manifest.get("artifacts", {}).get(name, {})
        variants = original.get("variants", [])
        if original.get("copies") != 1 or len(variants) != 1:
            raise RuntimeError(f"Missing unique historical discovery for {name}")
        observed_sha = sha256(path)
        if observed_sha != variants[0].get("sha256"):
            raise RuntimeError(f"Same-file SHA256 gate failed: {name}")
        expected = original.get("expected_sha256")
        if expected and expected != observed_sha:
            raise RuntimeError(f"Historical immutable SHA256 gate failed: {name}")

def load_verified_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load pinned runner: " + path.name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def compare_cis(aggregate: dict, cluster: str):
    checks = {}
    for cohort in ("V2", "V3", "V4"):
        part = aggregate["cohorts"][cohort]
        ci = part["bootstrap"]
        expected = EXPECTED_CIS[cluster][cohort]
        actual = {
            "mean": ci["delta_topk_mean_ci95"],
            "hit": ci["delta_topk_hit_rate_ci95"],
        }
        checks[cohort] = {
            "replicate_count": aggregate.get("replicates") == 10000,
            "infeasible_replicates_zero": ci.get("infeasible_replicates") == 0,
            "delta_topk_mean_ci95_match": all(
                abs(a-b) <= 1e-8 for a, b in zip(actual["mean"], expected["mean"])
            ) and len(actual["mean"]) == 2,
            "delta_topk_hit_rate_ci95_match": all(
                abs(a-b) <= 1e-8 for a, b in zip(actual["hit"], expected["hit"])
            ) and len(actual["hit"]) == 2,
        }
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-root", required=True)
    parser.add_argument("--discovery-manifest", required=True)
    parser.add_argument("--point-replay", required=True)
    parser.add_argument("--frozen-runner-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--cluster", choices=["news", "ticker"], required=True)
    parser.add_argument("--trust-local-pickles", action="store_true")
    args = parser.parse_args()
    if not args.trust_local_pickles:
        parser.error("Loading Pickle data requires explicit --trust-local-pickles")
    point_replay = json.loads(Path(args.point_replay).expanduser().read_text(encoding="utf-8"))
    if point_replay.get("status") != "POINT_REPLAY_PASS_NOT_RAW_REPRODUCED":
        raise RuntimeError("G0.2 point-replay gate is not PASS")
    if any(point_replay.get("cohorts", {}).get(cohort, {}).get("status") != "PASS"
           for cohort in ("V2", "V3", "V4")):
        raise RuntimeError("One or more G0.2 cohort gates are not PASS")
    root = Path(args.search_root).expanduser().resolve()
    paths = find_local(root, {name for pair in NAMES.values() for name in pair})
    verify_inputs(paths, Path(args.discovery_manifest).expanduser())

    runner_dir = Path(args.frozen_runner_dir).expanduser()
    for file_name, expected_blob in BLOBS.items():
        path = runner_dir / file_name
        actual_blob = git_blob_sha(path)
        if actual_blob != expected_blob:
            raise RuntimeError(
                f"Frozen runner differs from historical GitHub blob: {file_name}"
            )

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    aggregate_path = out_dir / f"IC_G0_bootstrap_{args.cluster}_aggregate.json"
    distribution_path = out_dir / f"IC_G0_bootstrap_{args.cluster}_distributions.npz"
    verification_path = out_dir / f"IC_G0_bootstrap_{args.cluster}_verification.json"
    if any(p.exists() for p in (aggregate_path, distribution_path, verification_path)):
        raise RuntimeError("Refusing to overwrite previous audit outputs")

    primary = load_verified_module(
        "run_phase2_primary_bootstrap",
        runner_dir / "run_phase2_primary_bootstrap.py"
    )
    if primary.REPLICATES != 10000 or primary.SEED != 20260821 or primary.TOPK_FRACTION != 0.10:
        raise RuntimeError("Frozen primary constants changed")
    for cohort, (signal, target) in NAMES.items():
        primary.COHORTS[cohort]["signals"] = paths[signal]
        primary.COHORTS[cohort]["targets"] = paths[target]

    if args.cluster == "news":
        runner = primary
    else:
        runner = load_verified_module(
            "run_phase2_ticker_bootstrap",
            runner_dir / "run_phase2_ticker_bootstrap.py"
        )
        if runner.REPLICATES != 10000 or runner.SEED != 20260822 or runner.TOPK_FRACTION != 0.10:
            raise RuntimeError("Frozen ticker constants changed")

    runner.OUTPUT_SUMMARY = aggregate_path
    runner.OUTPUT_DISTRIBUTIONS = distribution_path
    print(f"Running original frozen 10,000-replicate {args.cluster} bootstrap on trusted local data")
    runner.main()
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    checks = compare_cis(aggregate, args.cluster)
    passed = all(all(c.values()) for c in checks.values())
    verification = {
        "schema_version": "dtrm.ic.g0.bootstrap_replay.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_commit": PINNED_COMMIT,
        "cluster": args.cluster,
        "status": ("BOOTSTRAP_REPLAY_PASS" if passed else "BOOTSTRAP_REPLAY_MISMATCH"),
        "checks": checks,
        "aggregate_cis": {
            cohort: {
                "delta_topk_mean_ci95":
                    aggregate["cohorts"][cohort]["bootstrap"]["delta_topk_mean_ci95"],
                "delta_topk_hit_rate_ci95":
                    aggregate["cohorts"][cohort]["bootstrap"]["delta_topk_hit_rate_ci95"],
            } for cohort in ("V2", "V3", "V4")
        },
        "caveat": "Historical bootstrap replay, not a new independent temporal test.",
    }
    verification_path.write_text(
        json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Verification: {verification_path}")
    for cohort, c in checks.items():
        print(f"{cohort}: {'PASS' if all(c.values()) else 'MISMATCH'}")
    print(f"G0 {args.cluster}: {verification['status']}")
    return 0 if passed else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G0 bootstrap aborted: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(3)
