#!/usr/bin/env python3
"""G2.8 A3—metadata-only original price-source feasibility triage.

Reads SHA-sealed G2.5 filename/size/hash inventory, G2.6/G2.7 JSON
source-only reports, and pinned *source code*; it NEVER opens scientific
price data, returns, news, targets, Pickles, NPY, or model binaries.
Candidate filenames cannot prove point-in-time daily price coverage.
It never authorizes G3 risk-filter comparisons.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
G2_5_SHA = "ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7"
G2_6_SHA = "1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
G2_A2_SHA = "5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8"
SOURCE = ("src/dtrm/price_alignment.py", "src/dtrm/return_construction.py")
SCHEMA = "dtrm.ic.g2.a3_original_price_source_triage.v1"

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as s:
        for b in iter(lambda:s.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def load(path:Path)->dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required original metadata report missing/unsafe: "+path.name)
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise RuntimeError("Metadata report must be a JSON object")
    return obj

def demand(condition:bool,msg:str):
    if not condition:
        raise RuntimeError(msg)

def classify(filename:str)->str:
    name=filename.lower()
    # Earlier labels/targets must never be misidentified as
    # observational price series for a pre-event filter.
    if any(k in name for k in (
        "holdout","target","label","model_target","evaluation",
        "forward","bootstrap","excess_beta","phase3","phase4"
    )):
        return "EXCLUDED_OUTCOME_OR_TEST_ARTIFACT"
    if any(k in name for k in (
        "price","prices","ohlc","ohlcv","adjusted_close",
        "adj_close","historical_daily","stock_daily"
    )):
        return "POSSIBLE_PRICE_SOURCE_ASOF_UNVERIFIED"
    if any(k in name for k in ("volatility","volatil","realized_vol")):
        return "POSSIBLE_RISK_PROXY_ASOF_UNVERIFIED"
    if any(k in name for k in ("beta_pre","beta","spy","market")):
        return "BETA_OR_MARKET_CONTEXT_NOT_STOCK_PRICE_SOURCE"
    return "OTHER_FILE_NAME"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--g2-5-inventory",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--g2-7-preflight",required=True)
    p.add_argument("--g2-7-plan",required=True)
    p.add_argument("--frozen-repo",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out).expanduser()
    if out.exists():
        p.error("Refusing overwrite of original G2.8 report")
    invpath=Path(a.g2_5_inventory).expanduser()
    bindingpath=Path(a.g2_6_binding).expanduser()
    planpath=Path(a.g2_7_plan).expanduser()
    inventory,binding,pre,plan=(load(Path(q).expanduser()) for q in (
        a.g2_5_inventory,a.g2_6_binding,a.g2_7_preflight,a.g2_7_plan))
    demand(sha(invpath)==G2_5_SHA,"Original G2.5 SHA is not pinned")
    demand(sha(bindingpath)==G2_6_SHA,"Original G2.6 SHA is not pinned")
    demand(sha(planpath)==G2_A2_SHA,"Original G2.7 A2 plan SHA is not pinned")
    demand(inventory.get("status")==
        "G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3",
        "G2.5 historical file scan not metadata-only PASS")
    demand(binding.get("status")==
        "G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
        "G2.6 historical original calibration preflight not PASS")
    demand(pre.get("status")==
        "G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN",
        "G2.7 source-and-method preflight not PASS")
    demand(pre.get("plan_sha256")==G2_A2_SHA and
           pre.get("g2_5_inventory_sha256")==G2_5_SHA and
           pre.get("g2_6_operator_binding_sha256")==G2_6_SHA,
           "G2.7 does not bind the original metadata evidence")
    demand(pre.get("G3_new_outcome_computations_authorized") is False and
           plan.get("implementation_status",{}).get("g3_experiment_permitted") is False,
           "G3 authorization illegally promoted before A3 source review")

    frozen=Path(a.frozen_repo).expanduser()
    result=subprocess.run(["git","-C",str(frozen),"rev-parse","HEAD"],
        check=True,capture_output=True,text=True)
    demand(result.stdout.strip()==PIN,"Not original frozen historical Git source HEAD")
    dirty=subprocess.run(["git","-C",str(frozen),"status","--porcelain",
        "--untracked-files=no"],check=True,capture_output=True,text=True)
    demand(not dirty.stdout.strip(),"Original historical source tracked files modified")
    source_checks={}
    for name in SOURCE:
        src=frozen/name
        demand(src.is_file() and not src.is_symlink(),
               "Pinned historical source code missing: "+name)
        content=src.read_text(encoding="utf-8")
        source_checks[name]={
          "sha256_original_source_code":sha(src),
          "has_historical_on_or_before":("price_on_or_before" in content),
          "has_historical_on_or_after":("price_on_or_after" in content),
          "has_historical_forward_return":("forward_return" in content),
          "note":"Code inspection only; does not imply a local price dataset exists."
        }
    demand(source_checks[SOURCE[0]]["has_historical_on_or_before"],
           "Frozen historical price alignment code is missing on-or-before rule")
    demand(source_checks[SOURCE[1]]["has_historical_forward_return"],
           "Frozen historical forward target construction missing")

    catalog=inventory.get("candidate_files",[])
    demand(isinstance(catalog,list) and len(catalog)==92,
           "Expected exactly 92 original G2.5 metadata entries")
    counts=Counter()
    records=[]
    for item in catalog:
        name=Path(item["relative_path"]).name
        label=classify(name)
        counts[label]+=1
        if label not in (
            "POSSIBLE_PRICE_SOURCE_ASOF_UNVERIFIED",
            "POSSIBLE_RISK_PROXY_ASOF_UNVERIFIED",
            "BETA_OR_MARKET_CONTEXT_NOT_STOCK_PRICE_SOURCE"
        ):
            continue
        digest=item.get("sha256_new_local_commitment")
        demand(item.get("hash_status")=="SHA256_STREAMED_WITHOUT_DESERIALIZATION",
               "Unhashable old candidate was not verified by G2.5")
        demand(isinstance(digest,str) and re.fullmatch(r"[0-9a-f]{64}",digest),
               "Missing old source local SHA commitment")
        records.append({
            "relative_path":item["relative_path"],
            "root_ordinal":item["root_ordinal"],
            "bytes":item["size_bytes"],
            "sha256_existing_g2_5_local_commitment":digest,
            "filename_only_classification":label,
            "proven_asof_stock_price_dataset":False,
        })
    candidates=sum(counts[k] for k in (
        "POSSIBLE_PRICE_SOURCE_ASOF_UNVERIFIED",
        "POSSIBLE_RISK_PROXY_ASOF_UNVERIFIED"
    ))
    state=("G2_8_A3_POTENTIAL_SOURCE_NAMES_FOUND_PRICE_VALUES_UNREAD"
        if candidates else
        "G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY")
    report={
        "schema_version":SCHEMA,
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":state,
        "historic_source_commit":PIN,
        "source_code_checks":source_checks,
        "original_g2_5_inventory_sha256":G2_5_SHA,
        "original_g2_6_binding_sha256":G2_6_SHA,
        "original_g2_7_plan_sha256":G2_A2_SHA,
        "g2_7_operator_source_gate_status":pre["status"],
        "candidate_file_name_category_counts":dict(sorted(counts.items())),
        "plausible_old_source_candidates":records,
        "candidate_is_not_proof_of_asof_availability":True,
        "A3_historical_point_in_time_daily_stock_prices_verified":False,
        "A3_historical_universe_ticker_coverage_verified":False,
        "A3_original_adjustment_provider_time_verified":False,
        "A3_conventional_volatility_comparison_executed":False,
        "A4_realized_trading_returns_or_costs_analyzed":False,
        "g2_frozen":False,
        "g3_authorized":False,
        "next_condition":"Named source must be authentic daily adjusted historical prices with strictly pre-event as-of dates for all old cohorts and validation. Verify schema/coverage without targets, then separately freeze original-risk matched comparator.",
        "limits":[
            "G2.5 filename filter may omit price datasets with generic names; no negative global existence claim.",
            "Raw event-time stock market prices, including original chart adjustments and provider timestamps, were NOT opened or certified.",
            "Target prices used for 60-day outcome construction are NOT automatically valid historical volatility features.",
            "A post hoc risk-control benchmark is exploratory on already consumed V2/V3/V4 outcomes.",
            "No source data or old/new outcomes read; no G3 financial performance computed."
        ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.8:",state)
    print("G2.5 filename categories:",report["candidate_file_name_category_counts"])
    print("Potential price/risk filenames:",candidates)
    for q in records[:30]:
        print(" ",q["filename_only_classification"],"root",q["root_ordinal"],
              q["relative_path"],"bytes",q["bytes"])
    print("Original historic source code rules:",list(source_checks))
    print("Report:",out)
    print("No price contents, forward outcomes, Pickles, models, or new observations opened. G3 BLOCKED.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print(f"G2.8 halted: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
