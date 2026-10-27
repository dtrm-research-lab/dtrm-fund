#!/usr/bin/env python3
"""G1.1 targeted input/provenance audit (metadata only).

Never opens files, unpickles data, reads returns, computes predictions,
accesses network, or alters experimental source files. Candidate model
classification is from filenames only and does NOT verify trained weights.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone, date
import json
import os
from pathlib import Path
import re

DT = re.compile(r"(?<!\d)(20\d{2})[-_](\d{2})[-_](\d{2})(?!\d)")
PRUNE = {".git", ".Trash", ".venv", "venv", "node_modules", "__pycache__",
         ".cache", ".npm", ".cargo", ".rustup", "Library"}
WEIGHT_EXTS = {".ubj", ".model", ".joblib", ".bst", ".xgb"}
CANDIDATE_EXTS = WEIGHT_EXTS | {".json", ".pkl", ".pickle", ".bin", ".txt"}
MODEL_WORDS = ("xgb", "booster", "ranker", "quantile", "checkpoint",
               "trained_model", "model_p10", "model_p50", "model_p90")
EXCLUDE_WORDS = ("model_rows", "model_targets", "threshold", "policy",
                 "lineage", "manifest", "summary", "reference",
                 "metrics", "predictions", "test_results", "distribution")
NEWS_WORDS = ("news", "article", "headline", "trump", "fmp")
EXACT_INPUTS = (
    "news_2025-01-01_2026-05-01.pkl",
    "news_emb_2025-01-01_2026-05-01.dat",
    "news_emb_shape_2025-01-01_2026-05-01.pkl",
    "news_emb_index_2025-01-01_2026-05-01.pkl",
)
MAX_MATCHES = 30

def named_dates(filename: str) -> list[str]:
    found = set()
    for match in DT.finditer(filename):
        try:
            found.add(date(*map(int, match.groups())).isoformat())
        except ValueError:
            pass
    return sorted(found)

def model_category(filename: str) -> str | None:
    f = filename.lower()
    suffix = Path(f).suffix
    if suffix not in CANDIDATE_EXTS:
        return None
    if any(w in f for w in EXCLUDE_WORDS):
        return None
    if suffix in WEIGHT_EXTS:
        return "possible_model_binary"
    if any(w in f for w in MODEL_WORDS):
        return "possible_model_serialization_unverified"
    return None

def inspect(root: Path) -> dict:
    entry: dict = {
        "exists": root.is_dir(), "visited": 0, "files_by_model_class": {},
        "dated_news_names": {}, "dated_news_after_july_2026": 0,
        "latest_news_filename_date": None, "price_cache": {},
        "exact_legacy_inputs": {},
    }
    if not root.is_dir():
        return entry
    model = {kind: [] for kind in
             ("possible_model_binary", "possible_model_serialization_unverified")}
    news_count: Counter = Counter()
    latest_date = None
    for parent, dirs, filenames in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d not in PRUNE
                   and not (Path(parent) / d).is_symlink()]
        for fn in filenames:
            entry["visited"] += 1
            p = Path(parent) / fn
            if p.is_symlink() or not p.is_file():
                continue
            kind = model_category(fn)
            if kind:
                model[kind].append(fn)
            if any(word in fn.lower() for word in NEWS_WORDS):
                dates = named_dates(fn)
                if dates:
                    most_recent = max(dates)
                    news_count[most_recent[:7]] += 1
                    if most_recent >= "2026-08-01":
                        entry["dated_news_after_july_2026"] += 1
                    if latest_date is None or most_recent > latest_date:
                        latest_date = most_recent
    entry["files_by_model_class"] = {
        kind: {"count": len(files), "sample_names": sorted(set(files))[:MAX_MATCHES]}
        for kind, files in model.items()
    }
    entry["latest_news_filename_date"] = latest_date
    entry["dated_news_names"] = dict(sorted(news_count.items()))
    if root.name == "Outputs":
        entry["exact_legacy_inputs"] = {
            name: {
                "exists": (root / name).is_file(),
                "bytes": (root / name).stat().st_size if (root / name).is_file() else None,
            } for name in EXACT_INPUTS
        }
        cache = root / "price_cache_fmp_pickle"
        by_date = Counter()
        undated = 0
        total = 0
        if cache.is_dir():
            for p in cache.glob("*.pkl"):
                if not p.is_file() or p.is_symlink():
                    continue
                total += 1
                matches = named_dates(p.name)
                if matches:
                    by_date[matches[-1]] += 1
                else:
                    undated += 1
        entry["price_cache"] = {
            "exists": cache.is_dir(), "pickle_files": total,
            "dated_snapshots": dict(sorted(by_date.items())),
            "undated_pickle_files": undated,
            "latest_snapshot_filename_date": max(by_date) if by_date else None,
            "caution": "Filename snapshot date is not latest underlying trading date.",
        }
    return entry

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", action="append", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    roots = [Path(x).expanduser().resolve() for x in args.root]
    if len({r.name for r in roots}) != len(roots):
        p.error("Root folder names must be distinct for a path-redacted report")
    out = Path(args.out).expanduser()
    if out.exists():
        p.error("Audit file already exists; refusing to overwrite")
    results = {root.name: inspect(root) for root in roots}
    payload = {
        "schema_version": "dtrm.ic.g1.input_provenance_metadata.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "status": "METADATA_ONLY_NO_MODEL_OR_NEW_HOLDOUT_APPROVAL",
        "scientific_limits": [
            "Never read file contents or outcome values.",
            "Possible model binaries inferred from filename, not verified weights.",
            "Filename dates do not establish source event date or price coverage.",
            "Conserving historical inputs does not reconstruct exact fitted boosters.",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    for name, data in results.items():
        print(f"{name}: exists={data['exists']}; visited={data['visited']}; "
              f"news filenames Aug+={data['dated_news_after_july_2026']}")
        for kind, items in data["files_by_model_class"].items():
            print(f"  {kind}: {items['count']}  sample={items['sample_names'][:10]}")
        if data["price_cache"]:
            cache = data["price_cache"]
            print(f"  price_cache snapshots: {cache['pickle_files']}; "
                  f"last filename snapshot: {cache['latest_snapshot_filename_date']}")
            print("  snapshot counts by date:", cache["dated_snapshots"])
    print("G1.1 report:", out)
    print("No scientific data files opened. No outcomes inspected.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
