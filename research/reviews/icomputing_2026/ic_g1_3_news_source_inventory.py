#!/usr/bin/env python3
"""IC G1.3a: metadata-only inventory of candidate news/event-time inputs.

Do NOT open any file contents, deserialize a dataset, read prices,
targets or returns, or execute a scientific model. Directory entries
and filenames are NOT proof of usable event-time datasets.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

CANDIDATE_EXT = {".pkl",".pickle",".parquet",".json",".jsonl",".csv",".dat",".npy",".ndjson"}
SKIP_DIR = {".git", "node_modules",".venv","venv","Library","Downloads",".next",
            "__pycache__",".cache",".Trash",".npm","build","dist"}
# Explicitly avoid examining any numeric/label/outcome data even as filenames
# in reported results; they are ignored as positive source candidates.
FORBIDDEN_WORDS = (
    "target","return","price","profit","outcome","label","pnl",
    "performance","beta_pre","model_targets","bootstrap","metrics"
)
EVENT_WORDS = ("news","article","event","headline")
EMBED_WORDS = ("emb","sbert","minilm")
PAIR_WORDS = ("pair","ticker_news")
DATE_TOKEN = re.compile(r"20(?:25|26)-\d{2}-\d{2}")
MAX_DISPLAY = 80
START_DATE = "2026-06-15"

def kind(filename: str):
    name=filename.lower()
    if any(x in name for x in FORBIDDEN_WORDS):
        return None
    if any(x in name for x in EMBED_WORDS):
        return "embedding_candidate"
    if any(x in name for x in EVENT_WORDS):
        return "news_event_candidate"
    if any(x in name for x in PAIR_WORDS):
        return "pairs_candidate"
    return None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--search-root",action="append",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out).expanduser()
    if out.exists():
        ap.error("Refusing to overwrite previously produced G1.3a report")
    seen=set()
    records=[]
    all_counts=Counter()
    dated_counts=Counter()
    roots=[Path(p).expanduser().resolve() for p in args.search_root]
    for i,root in enumerate(roots):
        if not root.is_dir():
            all_counts["missing_search_roots"]+=1
            continue
        for directory,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=[x for x in dirs if x not in SKIP_DIR and
                     not (Path(directory)/x).is_symlink()]
            for filename in files:
                file=Path(directory)/filename
                if file.suffix.lower() not in CANDIDATE_EXT:
                    continue
                group=kind(filename)
                if group is None:
                    continue
                if file.is_symlink() or not file.is_file():
                    continue
                try:
                    st=file.stat()
                except OSError:
                    all_counts["stat_failed"]+=1
                    continue
                identity=(st.st_dev,st.st_ino)
                if identity in seen:
                    continue
                seen.add(identity)
                all_counts[group]+=1
                # Only look at dates IN THE FILENAME (NOT in source contents).
                tokens=DATE_TOKEN.findall(filename)
                latest=max(tokens) if tokens else None
                if latest is None:
                    date_bucket="NO_DATE_IN_FILENAME"
                elif latest >= START_DATE:
                    date_bucket="AFTER_CONSUMED_HOLDOUT_FAMILY"
                else:
                    date_bucket="HISTORIC_OR_CONSUMED"
                dated_counts[group+"/"+date_bucket]+=1
                if date_bucket=="AFTER_CONSUMED_HOLDOUT_FAMILY" or latest is None:
                    records.append({
                        "root_ordinal":i+1,
                        "relative_path":str(file.relative_to(root)),
                        "category":group,
                        "bytes":int(st.st_size),
                        "filename_date_tokens":tokens,
                        "note":"Filename metadata only. No content or event timestamps verified.",
                    })
    records.sort(key=lambda x:(x["category"], x["filename_date_tokens"],x["relative_path"]))
    report={
        "schema_version":"dtrm.ic.g1_3.news_source_metadata_inventory.v1",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "status":"G1_3A_FILENAMES_ONLY_AVAILABLE_NEWS_NOT_YET_VERIFIED",
        "search_roots":[{"ordinal":i+1,"exists":r.is_dir()} for i,r in enumerate(roots)],
        "source_candidate_counts":dict(sorted(all_counts.items())),
        "filename_date_buckets":dict(sorted(dated_counts.items())),
        "candidate_entries":records[:MAX_DISPLAY],
        "candidate_entry_truncation_count":max(0,len(records)-MAX_DISPLAY),
        "no_file_contents_accessed":True,
        "no_outcome_label_or_price_data_accessed":True,
        "cohort_not_frozen":True,
        "models_not_authorized_for_new_inference":True,
        "limitations":[
            "Filename dates are not validated event dates, nor evidence of point-in-time news availability.",
            "Files named after the test period may still contain duplicates, labels or prior reused samples.",
            "Before any new empirical test, separately verify event-time news and embeddings, disjoint event IDs, original price maturity and outcome-blindness.",
            "Original V1 period and August 2026 60-day outcome overlap require independently fixed temporal embargo.",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.3a:",report["status"])
    print("Candidate filename date buckets:",report["filename_date_buckets"])
    print("Newer or undated candidate files:",len(records),"(shown",min(len(records),MAX_DISPLAY),")")
    for record in records[:MAX_DISPLAY]:
        print(" root",record["root_ordinal"],record["category"],
              record["relative_path"],"size",record["bytes"])
    print("Report:",out)
    print("No file content, targets, market price values, model weights, or inference accessed.")
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("G1.3a stopped:",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(3)
