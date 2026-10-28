#!/usr/bin/env python3
"""G2.13 — old V0 VALID split versus 60 prior price BAR DATES only.

Loads SHA-checked, trusted LOCAL original 2026-07-05 price Pickles and
trusted original legacy_model_rows_2026-05-01.pkl. Deserialization
necessarily materializes full original frames in memory, but we use
only price['date'] and model-row['split','news_id','ticker','date_dt'].
No price['close'], beta, prediction, target, volatility, profit or ML
inference is examined or calculated. This cannot prove price vintage.
"""
from __future__ import annotations
import argparse
from bisect import bisect_left
from datetime import datetime, timezone, date
import hashlib, json, re, sys
from pathlib import Path
from collections import Counter

G29_SHA="65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb"
G210_SHA="f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3"
PIN="c7502a690162459cdfb3413573e3133c42efb126"
SOURCE_NAME="legacy_model_rows_2026-05-01.pkl"
MODEL_FIELDS=("news_id","ticker","date_dt","split")
N_VALID=19880

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for data in iter(lambda:fp.read(1024*1024),b""):
            h.update(data)
    return h.hexdigest()

def load_json(path:Path)->dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing/symlinked earlier source report: "+path.name)
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):raise RuntimeError("Expected JSON source report object")
    return obj

def must(ok:bool,reason:str):
    if not ok:raise RuntimeError(reason)

def canon(x:str)->str:
    return "BRK-B" if x=="BRK.B" else x

def date_series(values,pd):
    out=pd.to_datetime(values,utc=True,errors="coerce")
    must(not out.isna().any(),"Unparseable price/event time metadata")
    return out.dt.date

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-price-cache",required=True)
    p.add_argument("--original-model-rows",required=True)
    p.add_argument("--g2-9-report",required=True)
    p.add_argument("--g2-10-report",required=True)
    p.add_argument("--g2-12-report",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--trust-original-pickles",action="store_true")
    a=p.parse_args()
    if not a.trust_original_pickles:
        p.error("Explicit trust in original LOCAL Pickles required: they can execute code")
    out=Path(a.out).expanduser()
    if out.exists():p.error("Refusing to overwrite an earlier G2.13 report")
    m9=Path(a.g2_9_report).expanduser()
    m10=Path(a.g2_10_report).expanduser()
    m12=Path(a.g2_12_report).expanduser()
    must(sha(m9)==G29_SHA and sha(m10)==G210_SHA,
         "G2.9/10 originally sealed report SHA mismatch")
    old9,old10,old12=load_json(m9),load_json(m10),load_json(m12)
    must(old9.get("status")=="G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN",
         "Original G2.9 not source identification PASS")
    must(old10.get("status")=="G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN",
         "Original G2.10 date schema not PASS")
    must(old12.get("status")=="G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN",
         "Original G2.12 old-cohort pair-date coverage not PASS")
    must(old12.get("original_g2_9_report_sha256")==G29_SHA and
         old12.get("original_g2_10_report_sha256")==G210_SHA and
         old12.get("original_code_commit")==PIN and
         old12.get("g3_scoring_authorized") is False,
         "G2.12 original ancestry or G3 gate not intact")
    historical_checks=old12.get("cohorts",{})
    for name,n in (("V4_original_V1_signals",40320),("V2",4449),
                   ("V3",2827),("V4_original_V4_signals",40320)):
        item=historical_checks.get(name,{})
        must(item.get("full_60_prior_return_date_coverage_pairs")==n and
             item.get("missing_original_price_cache_ticker_pairs")==0,
             "Previous G2.12 source pair date proof incomplete: "+name)
    must(old12.get("v1_v4_event_pair_key_date_set_agreement") is True,
         "Original V1/V4 historical event pair set differs")
    orig=Path(a.original_model_rows).expanduser()
    must(orig.is_file() and not orig.is_symlink()
         and orig.name==SOURCE_NAME,
         "Expected exact original frozen V0 row source basename")
    cache=Path(a.original_price_cache).expanduser()
    must(cache.is_dir() and not cache.is_symlink(),
         "Expected original price cache directory")
    import pandas as pd
    # SHA every original July5 snapshot before trusted Pickle load.
    item9=old9.get("watched_historical_filenames",{}).get("2026-07-05",[])
    must(len(item9)==174,"Original 174-source manifest incomplete")
    date_by_ticker={}
    for item in item9:
        file=item["filename"]
        path=cache/file
        must(path.is_file() and not path.is_symlink(),
             "Original price cache file missing or symlinked")
        must(path.stat().st_size==item.get("bytes") and
             sha(path)==item.get("sha256_new_local_commitment"),
             "Original price file changed since G2.9 SHA inventory")
        sym=canon(file.split("_",1)[0])
        must(sym not in date_by_ticker,"Duplicate normalized symbol "+sym)
        price=pd.read_pickle(path)
        must(isinstance(price,pd.DataFrame) and
             "date" in price.columns and "close" in price.columns,
             "Original historical price source columns changed")
        dates=date_series(price["date"],pd).tolist()
        must(len(dates)==len(set(dates)),"Duplicate dated closing bars")
        date_by_ticker[sym]=sorted(dates)
        del price
    must(len(date_by_ticker)==174 and "SPY" in date_by_ticker,
         "Original historical stock cache no longer 174 including SPY")
    # Model row SHA commitment is retrospective; G1 pinned source
    # reconstruction already verified the 19,880 validation count.
    model_sha=sha(orig)
    rows=pd.read_pickle(orig)
    must(isinstance(rows,pd.DataFrame) and
         set(MODEL_FIELDS).issubset(rows.columns),
         "Original model-row training source schema invalid")
    fold=rows.loc[rows["split"].eq("valid"),list(MODEL_FIELDS)].copy()
    must(len(fold)==N_VALID,"Frozen V0 VALID split count differs from 19,880")
    fold["ticker"]=fold["ticker"].astype(str).map(canon)
    must(not fold.duplicated(["news_id","ticker"]).any(),
         "Duplicate validation news/ticker keys")
    event=date_series(fold["date_dt"],pd).tolist()
    must(all(v<=date(2026,5,1) for v in event),
         "Original VALID event date extends beyond 2026-05-01 frozen split")
    counts=Counter()
    unique=Counter()
    for sym,when in zip(fold["ticker"].tolist(),event):
        arr=date_by_ticker.get(sym)
        if arr is None:
            counts["missing_stock_price_ticker_pairs"]+=1
            continue
        n=bisect_left(arr,when)
        s=bisect_left(date_by_ticker["SPY"],when)
        if s<61:counts["spy_insufficient_60_prior_close_dates_pairs"]+=1
        if n>=61:
            counts["full_60_prior_close_date_pairs"]+=1
        elif n>=41:
            counts["min_40_but_not_full_60_prior_close_date_pairs"]+=1
        else:
            counts["less_than_40_prior_close_date_pairs"]+=1
        unique[sym]+=1
    has_full=(counts["full_60_prior_close_date_pairs"]==N_VALID
          and counts["spy_insufficient_60_prior_close_dates_pairs"]==0
          and counts["missing_stock_price_ticker_pairs"]==0)
    status=("G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN"
        if has_full else
        "G2_13_A3_V0_VALID_PRICE_DATE_COVERAGE_PARTIAL_COMMON_CASE_REQUIRED")
    result={
      "schema_version":"dtrm.ic.g2.a3_v0_validation_bar_date_source_check.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":status,
      "historical_original_source_commit":PIN,
      "original_g2_9_sha256":G29_SHA,"original_g2_10_sha256":G210_SHA,
      "original_g2_12_sha256":sha(m12),
      "original_v0_model_rows_basename":SOURCE_NAME,
      "original_v0_model_rows_current_sha256":model_sha,
      "model_rows_commit_is_retrospective_not_original_preoutcome_hash":True,
      "original_valid_split_rows":N_VALID,
      "original_valid_split_distinct_tickers":len(unique),
      "original_valid_first_date":min(event).isoformat(),
      "original_valid_last_date":max(event).isoformat(),
      "original_price_cache_files_sha_checked":174,
      "valid_pair_date_coverage_aggregates":dict(counts),
      "min_return_observations":40,
      "full_return_observations":60,
      "requires_61_distinct_bars_strictly_before_each_validation_date":True,
      "validation_news_weights_or_predictions_inspected":False,
      "price_close_numeric_values_used":False,
      "forward_return_labels_or_targets_used":False,
      "volatility_computed":False,
      "vendor_asof_acquisition_time_verified":False,
      "corporate_action_adjustments_verified":False,
      "original_complete_case_volatility_cutoff_calculated":False,
      "g2_frozen":False,"g3_authorized":False,
      "notes":[
        "Validation fold is selected solely by original 'valid' flag from legacy_model_rows; no labels, beta, ranker or prediction values are used.",
        "Input Pickles are unpickled into memory and may contain numeric price/target columns, but only dates, ticker, news ID and split columns are accessed.",
        "Original July-5 price cache is retrospective relative to historic decisions; date-only coverage does not prove point-in-time-vintage availability or corporate-action adjustment regime.",
        "If coverage is partial, use a separately frozen common-validation complete-case admission comparison; never silently claim 19,880 fully covered.",
        "No 60-day non-overlapping new prospective event cohort was used. G3 is blocked."
      ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.13:",status)
    print("Original V0 VALID rows:",N_VALID,"distinct symbols:",len(unique))
    print("VALID first/last dated event:",min(event),max(event))
    print("Original common-source coverage:",dict(counts))
    print("V0 model rows retrospective SHA:",model_sha)
    print("G2.12 operator report SHA:",sha(m12))
    print("Report:",out)
    print("No numerical prices, returns, volatility, outcomes, scores or model predictions computed.")
    print("Provider vintage UNVERIFIED; G2 UNFROZEN; G3 BLOCKED.")
    return 0 if has_full else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print(f"G2.13 HALTED: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
