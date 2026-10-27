#!/usr/bin/env python3
"""G2.10 A3: trusted ORIGINAL price-cache DataFrame schema and bar-DATE check.

Opt-in trusted Pickle deserialization: this inspects ONLY DATE column,
column NAMES, row counts, duplicate date counts, and coverage of 60
prior trading returns at three fixed earliest historical event dates.
The close column's *presence* is checked; close VALUES are never used,
converted, printed, analyzed or copied into the output. No returns,
volatility, financial targets, labels, or ML model are computed.

Important: 2026-07-05 source files were saved AFTER May/June events.
Past-dated bars in these files DO NOT prove vintage/as-of timestamps,
quote adjustments or pre-event availability. G3 remains BLOCKED.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
G2_5_SHA = "ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7"
G2_6_SHA = "1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
G2_A2_SHA = "5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8"
SNAPSHOT_SUFFIX = "2026-07-05"
CUTS = {
  "V4_first_event_2026_05_02":"2026-05-02",
  "V2_first_event_2026_06_07":"2026-06-07",
  "V3_first_event_2026_06_11":"2026-06-11",
}
WINDOW_RETURNS = 60
MIN_RETURNS = 40
FMT = re.compile(r"^[A-Za-z0-9.\-]+_\d{4}-\d{2}-\d{2}_2026-07-05\.pkl$")
NAME = re.compile(r"^(?P<ticker>[A-Za-z0-9.\-]+)_\d{4}-\d{2}-\d{2}_2026-07-05\.pkl$")

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as s:
        for chunk in iter(lambda:s.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def read_meta(path:Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required local G2 metadata missing or symbolic link: "+path.name)
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise RuntimeError("Expected JSON object: "+path.name)
    return value

def check(value,reason):
    if not value: raise RuntimeError(reason)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--price-cache",required=True)
    p.add_argument("--g2-9-report",required=True)
    p.add_argument("--g2-5-inventory",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--g2-7-preflight",required=True)
    p.add_argument("--g2-7-plan",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--trust-original-price-pickles",action="store_true",
                   help="Required explicit trust in saved local historical Pandas Pickles; never use on untrusted files")
    args=p.parse_args()
    if not args.trust_original_price_pickles:
        p.error("Explicit --trust-original-price-pickles required. Pickle loading can execute code.")
    out=Path(args.out).expanduser()
    if out.exists():
        p.error("Refusing overwrite of preexisting G2.10 report")
    root=Path(args.price_cache).expanduser()
    check(root.is_dir() and not root.is_symlink(),
          "Specified historical price-cache directory missing or symlink")
    report9=read_meta(Path(args.g2_9_report).expanduser())
    i5=Path(args.g2_5_inventory).expanduser()
    i6=Path(args.g2_6_binding).expanduser()
    pl=Path(args.g2_7_plan).expanduser()
    p7=Path(args.g2_7_preflight).expanduser()
    check(sha(i5)==G2_5_SHA and sha(i6)==G2_6_SHA and sha(pl)==G2_A2_SHA,
          "Earlier frozen source metadata SHA mismatch")
    check(report9.get("schema_version")=="dtrm.ic.g2.a3_direct_original_price_cache_inventory.v1"
          and report9.get("status")=="G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN"
          and report9.get("historically_original_2026_07_05_count")==174
          and report9.get("historically_original_2026_07_05_excluding_SPY")==173
          and report9.get("pickles_deserialized") is False
          and report9.get("g3_scoring_authorized") is False,
          "Original G2.9 not an intact source-only price cache PASS")
    x7=read_meta(p7)
    check(x7.get("status")=="G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN"
          and x7.get("G3_new_outcome_computations_authorized") is False,
          "Original G2.7 G3 safety gate missing")
    binding=read_meta(i6)
    check(binding.get("status")=="G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
          "Historical original q25 source binding missing")
    items=report9.get("watched_historical_filenames",{}).get(SNAPSHOT_SUFFIX,[])
    check(isinstance(items,list) and len(items)==174,
          "G2.9 original July-5 source records must be 174")
    seen=set()
    for item in items:
        filename=item.get("filename")
        check(isinstance(filename,str) and bool(FMT.fullmatch(filename)),
              "Original price-cache entry has invalid filename")
        check(filename not in seen,"Duplicate filename in G2.9 metadata")
        seen.add(filename)
        check(item.get("hash_state")=="SHA256_STREAMED_WITHOUT_DESERIALIZATION"
              and isinstance(item.get("sha256_new_local_commitment"),str)
              and len(item["sha256_new_local_commitment"])==64,
              "Original price cache file must be SHA-recorded without deserializing")
    # Loading the original local trusted Pickles needs pandas, but no
    # financial column is accessed. Pandas pickle parsing inherently loads
    # the whole DataFrame into memory, including any close values.
    # We inspect only date and column-name METADATA and never write
    # any numerical prices to the output.
    import pandas as pd
    earliest=sorted(set(CUTS.values()))
    summary=Counter()
    buckets={label:Counter() for label in CUTS}
    rows=[]
    min_required_prior_bars=MIN_RETURNS+1
    full_prior_bars=WINDOW_RETURNS+1
    for item in sorted(items,key=lambda x:x["filename"]):
        filename=item["filename"]
        path=root/filename
        check(path.is_file() and not path.is_symlink(),"Price file missing/unsafe: "+filename)
        check(path.stat().st_size==item.get("bytes"),"Byte length mismatch: "+filename)
        check(sha(path)==item["sha256_new_local_commitment"],
              "File mutated after original G2.9 snapshot: "+filename)
        frame=pd.read_pickle(path)
        if not isinstance(frame,pd.DataFrame):
            summary["not_dataframe"]+=1
            rows.append({"file":filename,"status":"INVALID_NOT_DATAFRAME"})
            continue
        column_names=[str(x) for x in frame.columns]
        has_date="date" in column_names
        has_close="close" in column_names
        if not (has_date and has_close):
            summary["missing_date_or_close_column"]+=1
            rows.append({"file":filename,"status":"INVALID_MISSING_REQUIRED_COLUMNS",
                         "has_date":has_date,"has_close":has_close})
            continue
        # Read ONLY the date column; never access numerical close values here or
        # compute mathematical returns from any market value.
        parsed=pd.to_datetime(frame["date"],utc=True,errors="coerce")
        good=parsed.dropna()
        naive_good=good.dt.tz_convert("UTC").dt.date
        duplicated=int(naive_good.duplicated().sum())
        nat=int(parsed.isna().sum())
        unique=sorted(set(naive_good.tolist()))
        valid=int(len(unique))
        first=str(unique[0]) if unique else None
        last=str(unique[-1]) if unique else None
        count_future=int(sum(d>datetime(2026,7,5).date() for d in unique))
        entry={
          "file":filename,
          "ticker_from_filename":NAME.fullmatch(filename)["ticker"],
          "status":"DATE_STRUCTURE_OK" if valid and not nat and not duplicated and not count_future else "DATE_STRUCTURE_NEEDS_REVIEW",
          "date_column_present":True,
          "close_column_name_present_values_uninspected":True,
          "date_rows":len(frame),
          "distinct_utc_calendar_dates":valid,
          "null_or_unparseable_dates":nat,
          "duplicate_calendar_dates":duplicated,
          "first_date_metadata":first,
          "last_date_metadata":last,
          "dates_after_filename_snapshot_day":count_future,
          "prior_event_date_coverage":{},
        }
        for label,iso in CUTS.items():
            event_date=datetime.strptime(iso,"%Y-%m-%d").date()
            strictly_prior=sum(d<event_date for d in unique)
            is_min=strictly_prior>=min_required_prior_bars
            is_full=strictly_prior>=full_prior_bars
            entry["prior_event_date_coverage"][label]={
               "event_date":iso,
               "unique_prior_trading_bar_dates":strictly_prior,
               "enough_for_min_40_return_observations":is_min,
               "enough_for_full_60_return_observations":is_full,
               "price_values_or_returns_examined":False
            }
            if is_min:buckets[label]["min_40_return_date_coverage"]+=1
            if is_full:buckets[label]["full_60_return_date_coverage"]+=1
            if not is_min:buckets[label]["insufficient_40_date_coverage"]+=1
        summary[entry["status"]]+=1
        if entry["ticker_from_filename"]=="SPY":
            summary["market_reference_SPY"]+=1
        else:
            summary["non_SPY_named_tickers"]+=1
        rows.append(entry)
        # Do not retain an original dataframe across iterations.
        del frame
    if len(rows)!=174:
        raise RuntimeError("Internal price source summary truncated")
    if summary["DATE_STRUCTURE_OK"]==174 and all(
            buckets[x]["full_60_return_date_coverage"]==174 for x in CUTS):
        status="G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN"
    else:
        status="G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PARTIAL_OR_SCHEMA_OPEN"
    result={
      "schema_version":"dtrm.ic.g2.a3_original_price_bar_date_check.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":status,
      "source_historical_git_commit":PIN,
      "original_snapshot_last_date_in_filename":"2026-07-05",
      "g2_9_metadata_inventory_sha256":sha(Path(args.g2_9_report).expanduser()),
      "g2_5_source_inventory_sha256":G2_5,
      "g2_6_source_binding_sha256":G2_6,
      "g2_7_a2_plan_sha256":G2_A2,
      "g2_7_preflight_sha256":sha(p7),
      "source_files_checked":174,
      "structural_counts":dict(summary),
      "fixed_bar_date_coverage_rule":"Every close for volatility would require a strictly earlier calendar trading date than each event; 61 closes for 60 returns, min 41 closes for 40 returns.",
      "min_returns":MIN_RETURNS,
      "full_returns":WINDOW_RETURNS,
      "pre_event_date_buckets":{k:dict(v) for k,v in buckets.items()},
      "per_symbol_date_metadata_only":rows,
      "trusted_original_pickles_deserialized":True,
      "numeric_price_values_loaded_into_memory_by_pandas_pickle":True,
      "numeric_price_values_used_in_any_calculation":False,
      "numeric_price_values_exported_or_printed":False,
      "no_future_target_or_return_outcomes_inspected":True,
      "no_market_volatility_or_comparator_computed":True,
      "historical_provider_asof_acquisition_times_verified":False,
      "point_in_time_price_adjustments_verified":False,
      "all_original_validation_event_date_coverage_verified":False,
      "all_historical_old_news_ticker_pairs_coverage_verified":False,
      "g2_full_revision_protocol_frozen":False,
      "g3_scoring_authorized":False,
      "scientific_caveats":[
        "The 2026-07-05 file snapshot is later than May/June decision dates; earlier quote dates do not by themselves prove point-in-time data vintage or absence of corporate-action revisions.",
        "Only each cohort first event calendar date tested. This does NOT verify all individual news dates or the entire original validation window.",
        "Each file's close column name is checked but no close values, missing prices, numeric precision, adjustment regime, actual tradable prices or returns assessed.",
        "A3 volatility-veto comparator must still predeclare and freeze original validation-only threshold, 60 prior trading-return formula, ticker/news eligibility, missingness, clusters and no tuning.",
        "New analyses on V2/V3/V4 outcomes are inherently post-outcome exploratory, and no 60-day nonoverlapping independent holdout has been added."
      ]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.10:",status)
    print("Original 2026-07-05 historic price snapshots:",len(rows))
    print("Date/column structural counts:",dict(summary))
    for label in CUTS:
        print("Earliest-event date:",CUTS[label],
              "full 60 prior returns date coverage:",
              buckets[label]["full_60_return_date_coverage"],
              "min 40 prior returns date coverage:",
              buckets[label]["min_40_return_date_coverage"],
              "out of 174 snapshot files")
    print("Report:",out)
    print("No close values, returns, risk, benchmark, target outcomes or models evaluated.")
    print("Historical as-of acquisition/price vintage unverified; G3 remains BLOCKED.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print(f"G2.10 HALTED: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
