#!/usr/bin/env python3
"""IC G1.2g: reproduce historical 5 text features on frozen V1 rows.

Reads only trusted historical V1 news text, V1 signals and precommitted
V1 feature matrix; imports original pinned text-feature code.
No outcomes, historical targets, prices, future news or model inference.
Does NOT claim the 384 embedding dimensions have been reconstructed.
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
ORIGINAL_CODE = "src/dtrm/text_features.py"
NEWS_NAME = "news_2025-01-01_2026-06-06.pkl"
SIGNAL_NAME = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
FEATURE_NAME = "probabilistic_v1_holdout_features_2026-06-06.npy"
ANCHORED = {
    SIGNAL_NAME: "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b",
    FEATURE_NAME: "a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750",
}
ROWS = 40320

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def git_out(root: Path, *args: str) -> str:
    run=subprocess.run(["git","-C",str(root),*args],
                       check=True,capture_output=True,text=True)
    return run.stdout.strip()

def list_embedding_candidates(*roots: Path) -> dict:
    entries={}
    for root in roots:
        candidates=[]
        if root.is_dir():
            for p in root.iterdir():
                if not p.is_file() or p.is_symlink():
                    continue
                name=p.name.lower()
                if any(x in name for x in ("emb_", "embedding", "mini", "sbert")):
                    candidates.append({"name":p.name,"bytes":p.stat().st_size})
        entries[root.name]={
            "candidates_count":len(candidates),
            "candidate_names_and_sizes":sorted(candidates,key=lambda x:x["name"])[:90],
            "possible_truncation":len(candidates)>90,
        }
    return entries

def main() -> int:
    import numpy as np
    import pandas as pd

    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frozen-repo",required=True)
    ap.add_argument("--v1-local-data",required=True)
    ap.add_argument("--legacy-outputs",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--trust-historical-pickles",action="store_true")
    args=ap.parse_args()
    if not args.trust_historical_pickles:
        ap.error("Requires explicit trust of original local historical Pickles")
    report_path=Path(args.out).expanduser()
    if report_path.exists():
        ap.error("Refusing to overwrite previously generated audit file")

    source=Path(args.frozen_repo).expanduser().resolve()
    local=Path(args.v1_local_data).expanduser().resolve()
    old=Path(args.legacy_outputs).expanduser().resolve()
    if git_out(source,"rev-parse","HEAD")!=PIN:
        raise RuntimeError("Unexpected historical code commit")
    if git_out(source,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("Historic source has modified tracked files")
    code=source/ORIGINAL_CODE
    paths={
        SIGNAL_NAME:local/SIGNAL_NAME,
        FEATURE_NAME:local/FEATURE_NAME,
        NEWS_NAME:old/NEWS_NAME,
    }
    for name,path in paths.items():
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Original historical source unavailable: "+name)
        if name in ANCHORED and sha256(path)!=ANCHORED[name]:
            raise RuntimeError("Original SHA256 commitment mismatch: "+name)

    signals=pd.read_pickle(paths[SIGNAL_NAME])
    X=np.load(paths[FEATURE_NAME],allow_pickle=False)
    news=pd.read_pickle(paths[NEWS_NAME])
    if not isinstance(signals,pd.DataFrame) or X.shape!=(ROWS,390):
        raise RuntimeError("Invalid original V1 signal or feature matrix shape")
    if not isinstance(news,pd.DataFrame):
        raise RuntimeError("Historical news source is not a DataFrame")
    if len(signals)!=ROWS or "news_id" not in signals.columns:
        raise RuntimeError("Frozen original V1 signal IDs unavailable")

    data={
        "schema_version":"dtrm.ic.g1.text_five_provenance.v1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "pinned_training_commit":PIN,
        "original_text_feature_source_sha256":sha256(code),
        "frozen_signals_and_features_sha256_verified":True,
        "historical_news_file_sha256_new_local_anchor":sha256(paths[NEWS_NAME]),
        "historical_news_rows":len(news),
        "frozen_signal_rows":len(signals),
        "feature_layout":"384 embeddings + 5 text features + 1 beta_pre",
        "historical_news_columns":sorted(str(c) for c in news.columns),
        "embedding_file_candidates_metadata_only":list_embedding_candidates(old,local),
        "new_news_or_outcomes_opened":False,
        "future_holdout_approved":False,
    }
    required={"news_id","news_text"}
    if not required.issubset(news.columns):
        data["status"]="TEXT_FEATURE_SOURCE_SCHEMA_UNRESOLVED"
        data["reason"]="Original 2026-06-06 news snapshot has no news_id/news_text columns"
    elif news["news_id"].isna().any() or news["news_id"].duplicated().any():
        data["status"]="TEXT_FEATURE_SOURCE_KEYS_UNRESOLVED"
        data["reason"]="Original news source keys are duplicated or missing"
    else:
        lookup=news.set_index("news_id")["news_text"]
        mapped=signals["news_id"].map(lookup)
        absent=int(mapped.isna().sum())
        # Original legacy feature code itself accepts missing text as empty;
        # but missing event IDs from news snapshot cannot establish lineage.
        if absent:
            data["status"]="TEXT_FEATURE_NEWS_COVERAGE_UNRESOLVED"
            data["missing_news_text_mapped_rows"]=absent
        else:
            spec=importlib.util.spec_from_file_location("pinned_ic_text_features",code)
            if spec is None or spec.loader is None:
                raise RuntimeError("Could not load historical text feature source")
            module=importlib.util.module_from_spec(spec)
            sys.modules["pinned_ic_text_features"]=module
            spec.loader.exec_module(module)
            rebuilt=module.legacy_text_feature_matrix(mapped)
            ref=np.asarray(X[:,384:389],dtype=np.float32)
            if rebuilt.shape!=ref.shape or not np.isfinite(rebuilt).all():
                raise RuntimeError("Historical five-feature output shape/finite mismatch")
            delta=np.abs(np.asarray(rebuilt,dtype=np.float64)-np.asarray(ref,dtype=np.float64))
            per_row=np.max(delta,axis=1)
            data.update({
                "rows_compared":len(ref),
                "text_feature_columns":5,
                "max_abs_difference":float(delta.max()),
                "mean_abs_difference":float(delta.mean()),
                "rows_exceeding_1e_6":int((per_row>1e-6).sum()),
                "feature_columns_exceeding_1e_6":[int((delta[:,j]>1e-6).sum()) for j in range(5)],
                "missing_news_text_mapped_rows":0,
            })
            data["status"]=(
                "TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN"
                if data["rows_exceeding_1e_6"]==0
                else "TEXT_FEATURE_MISMATCH_REQUIRES_LINEAGE_INVESTIGATION"
            )

    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print("G1.2g:",data["status"])
    print("Historic V1 text: features=5, signals=",len(signals),
          "; source news rows=",len(news))
    if "max_abs_difference" in data:
        print("5 text-feature max absolute difference:",data["max_abs_difference"])
        print("Rows exceeding tolerance:",data["rows_exceeding_1e_6"])
        print("Mismatches by text column:",data["feature_columns_exceeding_1e_6"])
    else:
        print("Source issue:",data.get("reason","unknown"))
        print("Historic news columns:",data["historical_news_columns"])
    for label,detail in data["embedding_file_candidates_metadata_only"].items():
        print("Embedding candidates in",label,":",detail["candidates_count"])
        for entry in detail["candidate_names_and_sizes"]:
            print(" ",entry["name"],"bytes",entry["bytes"])
    print("Report:",report_path)
    print("No outcome values, targets, prices, newer news or model inference opened.")
    return 0 if data["status"]=="TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN" else 2

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"G1.2g halted: {type(e).__name__}: {e}",file=sys.stderr)
        raise SystemExit(3)
