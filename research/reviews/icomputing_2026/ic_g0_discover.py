#!/usr/bin/env python3
"""Read-only local artifact discovery for IC major revision G0.

This script never executes or unpickles recovered artifacts and never uploads data.
It only hashes named files and writes a small, path-redacted JSON manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_HASHES = {
    "probabilistic_v1_holdout_beta_pre_2026-06-06.pkl":
        "e39896db92f1bb7c8334f61a6eee7bc71f8acbd6b6e87504c388ae0b8b1463d8",
    "probabilistic_v1_holdout_features_2026-06-06.npy":
        "a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750",
    "probabilistic_v1_holdout_signals_2026-06-06.pkl":
        "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b",
    "probabilistic_v1_holdout_targets_2026-06-06.pkl":
        "a48dc970761d0474e4bb856fed892b5ffa5a908afec4d54f938ea5ab4ed89cdf",
    "probabilistic_v1_holdout_model_targets_2026-06-06.pkl":
        "8c1ad175aa9c54a81134109f0a6459ee892d365f77f6489f379d49941b262121",
}

REQUIRED = [
    "probabilistic_v2_holdout_signals_2026-06-10.pkl",
    "probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
    "probabilistic_v3_holdout_signals_2026-06-14.pkl",
    "probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
    "probabilistic_v4_holdout_signals_2026-06-06.pkl",
    *EXPECTED_HASHES,
]

PRUNED_DIRS = {
    ".git", ".Trash", ".venv", "venv", "__pycache__", "node_modules",
    ".cache", ".npm", ".cargo", ".rustup", "Library",
}

def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def discover(roots: list[Path]) -> dict[str, list[Path]]:
    wanted = set(REQUIRED)
    found = {name: [] for name in REQUIRED}
    seen = set()
    for root in roots:
        if not root.is_dir():
            print(f"WARNING: search root unavailable: {root}")
            continue
        for parent, dirs, files in os.walk(root, topdown=True, followlinks=False):
            dirs[:] = [d for d in dirs
                       if d not in PRUNED_DIRS
                       and not (Path(parent) / d).is_symlink()]
            for name in files:
                if name not in wanted:
                    continue
                candidate = Path(parent) / name
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                try:
                    key = (candidate.stat().st_dev, candidate.stat().st_ino)
                except OSError:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                found[name].append(candidate)
    return found

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-root", action="append", required=True,
                        help="Directory to scan; repeat for multiple locations")
    parser.add_argument("--out", default="IC_G0_discovery_manifest.json",
                        help="Small path-redacted JSON report, or '-' for stdout")
    parser.add_argument("--show-paths", action="store_true",
                        help="Show paths locally in terminal (not saved to JSON)")
    args = parser.parse_args()
    roots = [Path(p).expanduser().resolve() for p in args.search_root]
    found = discover(roots)
    report = {
        "schema_version": "dtrm.ic.g0.discovery.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "read-only artifact presence and SHA-256, not scientific reproduction",
        "roots_scanned": len(roots),
        "artifacts": {},
    }
    total_found = 0
    failed_hashes = []
    ambiguous = []
    missing = []
    for name in REQUIRED:
        paths = found[name]
        if not paths:
            missing.append(name)
        if len(paths) > 1:
            ambiguous.append(name)
        variants = []
        for path in paths:
            try:
                stat = path.stat()
                sha = digest_file(path)
                expected = EXPECTED_HASHES.get(name)
                integrity = ("MATCH" if sha == expected else "MISMATCH") if expected else "NO_ANCHOR"
                if integrity == "MISMATCH":
                    failed_hashes.append(name)
                variants.append({
                    "bytes": stat.st_size,
                    "sha256": sha,
                    "integrity": integrity,
                })
                total_found += 1
                if args.show_paths:
                    print(f"LOCAL PATH: {name}: {path}")
            except OSError as exc:
                variants.append({"integrity": "READ_ERROR", "error_type": type(exc).__name__})
                failed_hashes.append(name)
        report["artifacts"][name] = {
            "copies": len(paths),
            "expected_sha256": EXPECTED_HASHES.get(name),
            "variants": variants,
        }
    report["summary"] = {
        "required_names": len(REQUIRED),
        "found_names": len(REQUIRED) - len(missing),
        "files_checked": total_found,
        "missing_names": missing,
        "ambiguous_names": ambiguous,
        "hash_errors": sorted(set(failed_hashes)),
        "g0_status": "NEEDS_FOLLOW_UP" if missing or ambiguous or failed_hashes
                     else "PRESENCE_AND_ANCHOR_HASHES_OK_NOT_REPRODUCED",
    }
    serialized = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out == "-":
        print(serialized)
    else:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
        print(f"Manifest written: {out}")
    print(f"Required files located: {len(REQUIRED)-len(missing)}/{len(REQUIRED)}")
    print(f"Hash integrity errors: {len(set(failed_hashes))}; duplicates: {len(ambiguous)}")
    print(f"Status: {report['summary']['g0_status']}")
    print("No .pkl files were loaded, no models executed, and no data uploaded.")
    return 0 if not failed_hashes else 2

if __name__ == "__main__":
    raise SystemExit(main())
