#!/usr/bin/env python3
"""G1.0 availability-only inventory for IC major revision.

Scans file *names and metadata only*, never opens any scientific artifact.
Never loads Pickle, reads returns, scores, targets or file contents; never
runs inference, calls a network service, or modifies existing datasets.

Intended as a conservative input-availability survey, NOT holdout approval.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

EXTENSIONS = {
    ".pkl", ".pickle", ".parquet", ".csv", ".json", ".jsonl",
    ".npy", ".npz", ".joblib", ".ubj", ".model", ".zip", ".sqlite", ".db",
}
PRUNE = {
    ".git", ".Trash", ".venv", "venv", "__pycache__", "node_modules",
    ".cache", ".npm", ".cargo", ".rustup", ".tox", "site-packages",
}
ISO_DATE = re.compile(r"(?<!\d)(20\d{2})[-_](\d{2})[-_](\d{2})(?!\d)")
COMPACT_DATE = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")
FOCUS_FROM = date(2026, 8, 1)
SAMPLE_MAX = 8
MAX_TOTAL_ITEMS = 180000


def dates_in_basename(name: str) -> list[date]:
    found: set[date] = set()
    for pattern in (ISO_DATE, COMPACT_DATE):
        for match in pattern.finditer(name):
            try:
                found.add(date(*(int(group) for group in match.groups())))
            except ValueError:
                pass
    return sorted(found)


def categorize(relative_parts: tuple[str, ...], filename: str) -> str | None:
    parent = "/".join(relative_parts[:-1]).lower()
    n = filename.lower()
    path = parent + "/" + n
    if any(w in n for w in ("target", "return", "excess_beta", "label")):
        return "targets_metadata_only"
    if "price_cache" in parent or any(w in n for w in ("price", "ohlc", "quote", "market_history")):
        return "price_snapshots"
    if "news" in n or "news_cache" in parent:
        return "news_snapshots"
    if "pair" in n or "event_ticker" in n:
        return "event_ticker_pairs"
    if "embedding" in path or "emb_" in n or "feature" in n:
        return "features_and_embeddings"
    if "signal" in n or "prediction" in n or "inference" in n:
        return "signals_and_predictions"
    if any(w in n for w in ("xgb", "quantile", "p10", "p50", "p90", "baseline", "ranker", "model")):
        return "frozen_models_or_model_metadata"
    if ("local_data" in parent or "outputs" in parent) and dates_in_basename(n):
        return "other_dated_research_artifacts"
    return None


def scan_root(root: Path, aliases: dict[str, dict]) -> None:
    alias = root.name
    result = {
        "root_alias": alias,
        "exists": root.is_dir(),
        "matched_files": 0,
        "visited_files": 0,
        "stopped_at_limit": False,
        "categories": {},
    }
    aliases[alias] = result
    if not root.is_dir():
        return
    grouped = defaultdict(lambda: {
        "count": 0, "latest_dated_filename": None,
        "date_months": Counter(), "sample_filenames": [],
        "dated_files_from_aug_2026": 0,
        "dated_sample_filenames": [],
    })
    for parent, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(
            d for d in dirs
            if d not in PRUNE and not (Path(parent) / d).is_symlink()
        )
        for filename in sorted(files):
            result["visited_files"] += 1
            if result["visited_files"] >= MAX_TOTAL_ITEMS:
                result["stopped_at_limit"] = True
                break
            p = Path(parent) / filename
            if p.is_symlink() or p.suffix.lower() not in EXTENSIONS:
                continue
            try:
                relative_parts = p.relative_to(root).parts
            except ValueError:
                continue
            category = categorize(relative_parts, filename)
            if category is None:
                continue
            try:
                if not p.is_file():
                    continue
                # Metadata only; no file opens.
                p.stat()
            except OSError:
                continue
            result["matched_files"] += 1
            data = grouped[category]
            data["count"] += 1
            if len(data["sample_filenames"]) < SAMPLE_MAX:
                data["sample_filenames"].append(filename)
            dates = dates_in_basename(filename)
            if dates:
                last = dates[-1]
                stamp = last.isoformat()
                if data["latest_dated_filename"] is None or stamp > data["latest_dated_filename"]:
                    data["latest_dated_filename"] = stamp
                data["date_months"][last.strftime("%Y-%m")] += 1
                if last >= FOCUS_FROM:
                    data["dated_files_from_aug_2026"] += 1
                    if len(data["dated_sample_filenames"]) < SAMPLE_MAX:
                        data["dated_sample_filenames"].append(filename)
        if result["stopped_at_limit"]:
            break
    result["categories"] = {
        kind: {
            "count": d["count"],
            "latest_dated_filename": d["latest_dated_filename"],
            "date_months": dict(sorted(d["date_months"].items())),
            "dated_files_from_aug_2026": d["dated_files_from_aug_2026"],
            "sample_filenames": d["sample_filenames"],
            "dated_sample_filenames": d["dated_sample_filenames"],
        }
        for kind, d in sorted(grouped.items())
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True,
                        help="Local research directory to inventory; repeatable")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    roots = [Path(x).expanduser().resolve() for x in args.root]
    if len({r.name for r in roots}) != len(roots):
        parser.error("Root directory basenames must be distinct for path-redacted report")
    output = Path(args.out).expanduser()
    if output.exists():
        parser.error("Refusing to overwrite an existing G1 inventory")
    results: dict[str, dict] = {}
    for root in roots:
        scan_root(root, results)
    candidate_inputs = 0
    for entry in results.values():
        for cat in ("news_snapshots", "event_ticker_pairs", "price_snapshots",
                    "features_and_embeddings", "signals_and_predictions",
                    "frozen_models_or_model_metadata"):
            candidate_inputs += entry["categories"].get(cat, {}).get(
                "dated_files_from_aug_2026", 0
            )
    payload = {
        "schema_version": "dtrm.ic.g1.metadata_only_inventory.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "read_policy": "metadata only: scientific file contents never opened",
        "outcome_values_inspected": False,
        "temporal_holdout_approved": False,
        "scope_notes": [
            "File names are not evidence of per-row event dates or market data coverage.",
            "The catalog does not establish outcome maturity or prior exposure.",
            "Post-August artifacts may be unrelated to the frozen HDPG models.",
            "Raw file paths and scientific records are not included in this report.",
            "Candidate cohort selection must be preregistered before reading targets.",
        ],
        "root_results": results,
        "summary": {
            "roots_requested": len(roots),
            "roots_available": sum(x["exists"] for x in results.values()),
            "candidate_post_july_dated_input_files": candidate_inputs,
            "file_scan_truncated": any(x["stopped_at_limit"] for x in results.values()),
            "status": "METADATA_INVENTORY_ONLY_NO_NEW_RESULTS",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("G1.0 — Metadata-only, outcome-blind availability audit")
    for alias, result in results.items():
        print(f"  {alias}: exists={result['exists']}; visited={result['visited_files']}; "
              f"matched={result['matched_files']}; truncated={result['stopped_at_limit']}")
        for category, data in result["categories"].items():
            print(f"    {category}: files={data['count']}; "
                  f"with Aug+ dated names={data['dated_files_from_aug_2026']}; "
                  f"latest filename date={data['latest_dated_filename'] or 'none'}")
    print("Report:", output)
    print("G1:", payload["summary"]["status"])
    print("NO target values, signal scores, file bytes or portfolio returns were read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
