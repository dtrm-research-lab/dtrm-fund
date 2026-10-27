#!/usr/bin/env python3
"""G2.9 A3 — scoped inventory of original FMP price-cache filename metadata.

Only file names, file sizes, and bounded streaming SHA-256 are used;
never deserialize a Pickle, inspect actual prices/date series, open
target values, or execute models. The filename's last YYYY-MM-DD
is not evidence of provider acquisition time or an event-time
point-in-time snapshot. G3 risk comparator remains BLOCKED.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
G2_5="ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7"
G2_6="1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
G2_A2="5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8"
SPEC_RE=re.compile(r"^(?P<ticker>[A-Za-z0-9.\-]+)_(?P<first>\d{4}-\d{2}-\d{2})_(?P<last>\d{4}-\d{2}-\d{2})\.pkl$")
WATCH={"2026-07-05","2026-08-10"}
MAX_SCAN=25000
MAX_LIST_PER_SNAPSHOT=240

def file_hash(path):
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def metadata(path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing or symbolic metadata report: "+str(path))
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise RuntimeError("JSON metadata report must be an object")
    return obj

def ok(condition,message):
    if not condition:raise RuntimeError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--price-cache",required=True,
       help="The ORIGINAL historical Notebooks/Outputs/price_cache_fmp_pickle folder")
    p.add_argument("--frozen-repo",required=True)
    p.add_argument("--g2-5-inventory",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--g2-7-preflight",required=True)
    p.add_argument("--g2-7-plan",required=True)
    p.add_argument("--g2-8-report",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--max-hash-mb",type=int,default=25)
    args=p.parse_args()

    out=Path(args.out).expanduser()
    if out.exists():p.error("Refusing overwrite of existing G2.9 evidence")
    if not 1<=args.max_hash_mb<=100:p.error("hash cap must be 1..100 MiB")
    inv=Path(args.g2_5_inventory).expanduser()
    bnd=Path(args.g2_6_binding).expanduser()
    plan=Path(args.g2_7_plan).expanduser()
    previous=Path(args.g2_8_report).expanduser()
    g25=metadata(inv)
    g26=metadata(bnd)
    g27=metadata(Path(args.g2_7_preflight).expanduser())
    g28=metadata(previous)
    originalplan=metadata(plan)
    ok(file_hash(inv)==G2_5,"G2.5 original SHA mismatch")
    ok(file_hash(bnd)==G2_6,"G2.6 original SHA mismatch")
    ok(file_hash(plan)==G2_A2,"G2.7 original A2 plan SHA mismatch")
    ok(g25.get("status")=="G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3",
       "G2.5 not a metadata-only PASS")
    ok(g26.get("status")=="G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
       "G2.6 source-only original P10 binding not PASS")
    ok(g27.get("status")=="G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN",
       "G2.7 documented A2 preflight not PASS")
    ok(g27.get("plan_sha256")==G2_A2 and g27.get("g2_6_operator_binding_sha256")==G2_6,
       "G2.7 binds different original inputs")
    ok(g28.get("status")=="G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY"
        and g28.get("g3_authorized") is False,
       "Unexpected original G2.8 bounded/negative filename-only result")
    ok(originalplan.get("implementation_status",{}).get("g3_experiment_permitted") is False,
       "Unfrozen scientific G3 input permission unexpectedly changed")

    frozen=Path(args.frozen_repo).expanduser()
    rev=subprocess.run(["git","-C",str(frozen),"rev-parse","HEAD"],
                       capture_output=True,text=True,check=True).stdout.strip()
    ok(rev==PIN,"Historical source must match original commit")
    dirty=subprocess.run(["git","-C",str(frozen),"status","--porcelain",
       "--untracked-files=no"],capture_output=True,text=True,check=True).stdout.strip()
    ok(not dirty,"Original historical source tree modified")
    original_source=frozen/"research/experiments/run_exante_baseline_v0.py"
    ok(original_source.is_file() and not original_source.is_symlink(),
       "Pinned V0 price-cache reader original source missing")
    source=original_source.read_text(encoding="utf-8")
    for keyword in ("price_cache_fmp_pickle","*_2026-07-05.pkl",
                    'frame["date"]','frame["close"]'):
        ok(keyword in source,"Historical price source structure unexpectedly changed: "+keyword)

    root=Path(args.price_cache).expanduser()
    ok(root.is_dir() and not root.is_symlink(),"No direct safe historical FMP price cache directory")
    # One exact directory, no recursive search; do not look into news/targets.
    names=[]
    with os.scandir(root) as scan:
        for entry in scan:
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                continue
            if len(names)>=MAX_SCAN:
                raise RuntimeError("Historical cache exceeds bounded max file count")
            names.append(entry.name)
    names.sort()

    all_counts=Counter()
    tickers=defaultdict(set)
    per_group=defaultdict(list)
    examples=[]
    totalbytes=0
    unsafe=0
    for filename in names:
        m=SPEC_RE.fullmatch(filename)
        if not m:
            all_counts["UNRECOGNIZED_FILENAME_PATTERN"]+=1
            if len(examples)<8:examples.append(filename)
            continue
        ticker=m["ticker"];last=m["last"];first=m["first"]
        try:
            d0=datetime.strptime(first,"%Y-%m-%d").date()
            d1=datetime.strptime(last,"%Y-%m-%d").date()
            if d1<d0:raise ValueError("last date before first date")
        except ValueError:
            all_counts["UNRECOGNIZED_DATE_RANGE"]+=1
            continue
        all_counts[last]+=1
        tickers[last].add(ticker)
        path=root/filename
        stat=path.stat()
        totalbytes+=stat.st_size
        if last not in WATCH:continue
        rec={
            "ticker_in_filename":ticker,
            "filename":filename,
            "filename_first_date":first,
            "filename_last_date":last,
            "bytes":stat.st_size,
            "sha256_new_local_commitment":None,
            "asof_provider_timestamp_proven":False,
            "daily_close_schema_proven":False,
            "actual_pre_event_coverage_proven":False,
        }
        if stat.st_size<=args.max_hash_mb*1024*1024:
            rec["sha256_new_local_commitment"]=file_hash(path)
            rec["hash_state"]="SHA256_STREAMED_WITHOUT_DESERIALIZATION"
        else:
            rec["hash_state"]="EXCEEDS_HASH_LIMIT"
            unsafe+=1
        per_group[last].append(rec)
    historic_grp=per_group.get("2026-07-05",[])
    historic=bool(
        len(historic_grp)>=2 and
        len({z["ticker_in_filename"] for z in historic_grp if z["ticker_in_filename"]!="SPY"})>=1
    )
    state=("G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN"
           if historic else
           "G2_9_A3_NO_MULTITICKER_ORIGINAL_PRICE_CACHE_SNAPSHOT_IDENTIFIED")

    report={
      "schema_version":"dtrm.ic.g2.a3_direct_original_price_cache_inventory.v1",
      "created_utc":datetime.now(timezone.utc).isoformat(),
      "status":state,
      "original_historical_code_commit":PIN,
      "original_reader_source_sha256":file_hash(original_source),
      "g2_5_input_report_sha256":G2_5,
      "g2_6_binding_report_sha256":G2_6,
      "g2_7_a2_plan_sha256":G2_A2,
      "g2_7_a2_gate_sha256":file_hash(Path(args.g2_7_preflight).expanduser()),
      "previous_g2_8_triage_sha256":file_hash(previous),
      "previous_g2_8_result_gated_scope":"ONLY_G2_5_BASENAME_KEYWORD_MATCHES_NO_FULL_PRICE_CACHE",
      "cache_exists":True,
      "files_in_original_price_cache":len(names),
      "recognized_suffix_counts":dict(sorted(all_counts.items())),
      "ticker_counts_by_filename_suffix":{x:len(z) for x,z in sorted(tickers.items())},
      "total_recognized_price_cache_bytes":totalbytes,
      "historically_original_2026_07_05_count":len(historic_grp),
      "historically_original_2026_07_05_excluding_SPY":
          len({z["ticker_in_filename"] for z in historic_grp if z["ticker_in_filename"]!="SPY"}),
      "sha256_max_file_mb":args.max_hash_mb,
      "files_exceeding_hash_limit_in_watched_groups":unsafe,
      "watched_historical_filenames":{k:sorted(v,key=lambda x:x["filename"])[:MAX_LIST_PER_SNAPSHOT]
                                     for k,v in sorted(per_group.items())},
      "ignored_unrecognized_filename_examples":examples,
      "metadata_only":True,
      "pickles_deserialized":False,
      "financial_values_or_return_outcomes_read":False,
      "provider_acquisition_timestamps_verified":False,
      "historical_date_columns_or_daily_price_schema_verified":False,
      "point_in_time_adjusted_prices_verified":False,
      "validation_coverage_and_event_prehistory_verified":False,
      "conventional_volatility_baseline_tested":False,
      "g2_frozen":False,"g3_scoring_authorized":False,
      "note":"File suffixes such as 2026-07-05 and 2026-08-10 describe filename snapshot coordinates, NOT provable acquisition time or pre-event history quality. The stored post-event file could still contain earlier dated prices and corporate-action revisions; neither is proven by this inventory."
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.9:",state)
    print("Original price cache named .pkl files:",len(names))
    print("Source reader pinned:",PIN)
    print("Historical 2026-07-05 files:",len(historic_grp),
          "; non-SPY distinct tickers:",report["historically_original_2026_07_05_excluding_SPY"])
    print("Other suffix group counts:",{k:v for k,v in sorted(all_counts.items()) if k!="2026-07-05"})
    print("Hash limit omissions in watched groups:",unsafe)
    print("Report:",out)
    print("No Pickles deserialized, price values/returns read, or G3 tests run. Point-in-time certification OPEN.")
    return 0
if __name__=="__main__":
    try:sys.exit(main())
    except Exception as exc:
        print(f"G2.9 HALTED: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(3)
