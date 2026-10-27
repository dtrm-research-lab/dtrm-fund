#!/usr/bin/env python3
"""G2.5: hash-only inventory of ALREADY-CONSUMED historical analysis inputs.

For G2 science-spec setup. Does not deserialize/examine market data,
target labels, returns, embeddings, prices or fitted models. Filenames
and size are recorded. Candidate files <= --hash-limit-mb are SHA256
streamed without decoding; all hashes are NEW local commitments.
Does NOT authorize G3 analysis or reveal any market values.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ALLOW={".pkl",".pickle",".npy",".npz",".csv",".parquet",".dat",".json"}
SKIP={".git",".venv","venv","node_modules","__pycache__", ".cache","dist","build",".next"}
KEYWORDS={
 "validation_quantiles":re.compile(r"val(id|idation)?|p10|quantile|weight|calibr",re.I),
 "historical_cohorts":re.compile(r"probabilistic_v[0-4]|holdout|xgb|signal",re.I),
 "price_beta_history":re.compile(r"price|spy|market|beta|daily|return|quote|volatil",re.I),
 "features":re.compile(r"features|embedding_manifest|exante",re.I),
}
MAX_RESULTS=180

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",action="append",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--hash-limit-mb",type=int,default=200)
    args=ap.parse_args()
    out=Path(args.out).expanduser()
    if out.exists():ap.error("Will not overwrite prior source inventory")
    if args.hash_limit_mb<1 or args.hash_limit_mb>200:
        ap.error("Hash limit must be 1–200 MB")
    roots=[Path(x).expanduser().resolve() for x in args.root]
    maxbytes=args.hash_limit_mb*1024*1024
    report={
      "schema_version":"dtrm.ic.g2.historical_analysis_input_inventory.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":"G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3",
      "roots":[{"ordinal":i+1,"exists":p.is_dir()} for i,p in enumerate(roots)],
      "counts_by_type":{}, "candidate_files":[], "skipped_large":0,
      "candidate_truncated":0, "source_file_errors":0,
      "scientific_file_contents_deserialized":False,
      "new_cohort_accessed":False,
      "g3_execution_authorized":False,
      "warnings":[
        "All candidate data source hashes are NEW LOCAL commitments, not original independent precommits",
        "Original V2/V3/V4 outcomes already observed; any new analyses are post-outcome exploratory",
        "Candidate file names are NOT validation/market dataset proof: source schema and timestamp need independent review before G2 freeze",
        "Do not upload original private datasets to public GitHub",
      ],
    }
    seen=set(); records=[]; counter=Counter()
    for j,root in enumerate(roots):
        if not root.is_dir():continue
        for base,dirs,filenames in os.walk(root,followlinks=False):
            dirs[:]=[x for x in dirs if x not in SKIP and not (Path(base)/x).is_symlink()]
            for filename in filenames:
                path=Path(base)/filename
                if path.suffix.lower() not in ALLOW or path.is_symlink() or not path.is_file():
                    continue
                cats=[name for name,pat in KEYWORDS.items() if pat.search(filename)]
                if not cats:continue
                try:st=path.stat()
                except OSError:
                    report["source_file_errors"]+=1;continue
                ident=(st.st_dev,st.st_ino)
                if ident in seen:continue
                seen.add(ident)
                for cat in cats:counter[cat]+=1
                records.append({
                    "root_ordinal":j+1,
                    "relative_path":str(path.relative_to(root)),
                    "size_bytes":int(st.st_size),
                    "candidate_categories":cats,
                    "_absolute_path":str(path)
                })
    records.sort(key=lambda r:(
        "validation_quantiles" not in r["candidate_categories"],
        "historical_cohorts" not in r["candidate_categories"],
        "price_beta_history" not in r["candidate_categories"],
        r["relative_path"]
    ))
    report["candidate_truncated"]=max(0,len(records)-MAX_RESULTS)
    for rec in records[:MAX_RESULTS]:
        path=Path(rec.pop("_absolute_path"))
        if rec["size_bytes"]>maxbytes:
            rec["sha256_new_local_commitment"]=None
            rec["hash_status"]="NOT_HASHED_EXCEEDS_LIMIT"
            report["skipped_large"]+=1
        else:
            try:
                rec["sha256_new_local_commitment"]=digest(path)
                rec["hash_status"]="SHA256_STREAMED_WITHOUT_DESERIALIZATION"
            except OSError:
                rec["sha256_new_local_commitment"]=None
                rec["hash_status"]="FILE_IO_ERROR"
                report["source_file_errors"]+=1
        report["candidate_files"].append(rec)
    report["counts_by_type"]=dict(sorted(counter.items()))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.5:",report["status"])
    print("Candidate groups:",report["counts_by_type"],"; files:",len(records))
    print("Source entries written:",len(report["candidate_files"]),
          "; file sizes > hash cap:",report["skipped_large"])
    for rec in report["candidate_files"][:40]:
        print(" root",rec["root_ordinal"],rec["relative_path"],
              "bytes",rec["size_bytes"],
              "hash",rec["hash_status"])
    print("Report:",out)
    print("No source data deserialized; no new cohorts, targets inspected or models executed")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G2.5 stopped:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
