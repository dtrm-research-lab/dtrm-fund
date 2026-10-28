#!/usr/bin/env python3
"""G2.12: outcome-blind original per-event pre-date price coverage.

Opt-in, verified TRUSTED original Pandas Pickles:
- 174 G2.9 original stock/SPY price snapshots: use ONLY bar date.
- V1/V2/V3/V4 historical signals: use ONLY news_id,ticker,date_dt.
- Compare 60 strictly earlier daily date intervals to each event;
  never evaluate price close, model scores, risk, labels, or returns.
- The 2026-07-05 retrospectively saved data is NOT a certified
  historical acquisition-time/vintage source. G3 remains blocked.

Pickle can run arbitrary code. Use only on the previously audited
trusted LOCAL original research files, never downloaded/untrusted files.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
BIND_SHA = "1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
G29_SHA = "65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb"
G210_SHA = "f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3"

FILES = {
    "V4_original_V1_signals": ("v1_signals", "probabilistic_v1_holdout_signals_2026-06-06.pkl", 40320, "2026-05-02", "2026-06-06"),
    "V2": ("v2_signals", "probabilistic_v2_holdout_signals_2026-06-10.pkl", 4449, "2026-06-07", "2026-06-10"),
    "V3": ("v3_signals", "probabilistic_v3_holdout_signals_2026-06-14.pkl", 2827, "2026-06-11", "2026-06-14"),
    "V4_original_V4_signals": ("v4_signals", "probabilistic_v4_holdout_signals_2026-06-06.pkl", 40320, "2026-05-02", "2026-06-06"),
}
RETURNS_FULL = 60
RETURNS_MIN = 40
SOURCE_COLUMNS = ("news_id", "ticker", "date_dt")
HASH_RE = re.compile(r"^[a-f0-9]{64}$")

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def read_json(path: Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required local report absent/unsafe: " + path.name)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected source metadata JSON object")
    return value

def check(valid: bool, reason: str):
    if not valid:
        raise RuntimeError(reason)

def canonical(name: str) -> str:
    if name == "BRK.B":
        return "BRK-B"
    return name

def utc_days(values, pd):
    parsed = pd.to_datetime(values, utc=True, errors="coerce")
    check(not parsed.isna().any(), "Historical source contains unparseable event/bar dates")
    return parsed.dt.date

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-price-cache", required=True)
    p.add_argument("--original-local-data", required=True)
    p.add_argument("--g2-6-binding", required=True)
    p.add_argument("--g2-9-report", required=True)
    p.add_argument("--g2-10-report", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--trust-original-pickles", action="store_true",
                   help="Explicit trust in preexisting LOCAL research Pickles; loading can execute code")
    a = p.parse_args()
    if not a.trust_original_pickles:
        p.error("Trusted original Pickle loading requires --trust-original-pickles")
    out = Path(a.out).expanduser()
    if out.exists():
        p.error("Refuse overwrite of prior G2.12 report")
    binding_path = Path(a.g2_6_binding).expanduser()
    g29_path = Path(a.g2_9_report).expanduser()
    g210_path = Path(a.g2_10_report).expanduser()
    check(sha(binding_path) == BIND_SHA, "G2.6 sealed report SHA mismatch")
    check(sha(g29_path) == G29_SHA, "G2.9 sealed report SHA mismatch")
    check(sha(g210_path) == G210_SHA, "G2.10 sealed report SHA mismatch")
    binding, g29, g210 = (read_json(x) for x in (binding_path,g29_path,g210_path))
    check(binding.get("status") == "G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
          "G2.6 original historic source gate not PASS")
    check(g29.get("status") == "G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN",
          "G2.9 price-cache filename gate not PASS")
    check(g210.get("status") == "G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN",
          "G2.10 date-only original price gate not PASS")
    check(g210.get("source_historical_git_commit") == PIN and
          g210.get("g2_9_metadata_inventory_sha256") == G29_SHA and
          g210.get("source_files_checked") == 174 and
          g210.get("g3_scoring_authorized") is False,
          "G2.10 original report lineage or G3 lock not verified")
    check(g210.get("trusted_original_pickles_deserialized") is True and
          g210.get("numeric_price_values_used_in_any_calculation") is False,
          "G2.10 original price-only metadata contract missing")
    inventory = g29.get("watched_historical_filenames", {}).get("2026-07-05", [])
    check(len(inventory) == 174, "G2.9 original July-5 source snapshot not complete")
    g210_tickers = {
        v.get("ticker_from_filename") for v in g210.get("per_symbol_date_metadata_only", [])
    }
    check(len(g210_tickers) == 174, "G2.10 original ticker inventory not 174 unique names")
    source_sha = binding.get("g2_5_historic_old_cohort_input_sha256", {})
    check(isinstance(source_sha, dict), "G2.6 old source SHA references missing")

    cache_root = Path(a.original_price_cache).expanduser()
    src_root = Path(a.original_local_data).expanduser()
    check(cache_root.is_dir() and not cache_root.is_symlink(),
          "Original FMP price cache path not a local directory")
    check(src_root.is_dir() and not src_root.is_symlink(),
          "Original scientific local_data path not a local directory")
    import pandas as pd

    dates = {}
    for v in inventory:
        filename = v.get("filename","")
        check(isinstance(filename,str) and filename.endswith("_2026-07-05.pkl"),
              "Unexpected original price-cache filename")
        symbol = filename.split("_",1)[0]
        symbol = canonical(symbol)
        check(symbol not in dates and symbol in g210_tickers,
              "Duplicate or unpaired original price ticker: "+symbol)
        path = cache_root/filename
        check(path.is_file() and not path.is_symlink(),"Missing/unsafe original price file")
        check(path.stat().st_size == v.get("bytes"),"Original price file size changed")
        expected = v.get("sha256_new_local_commitment")
        check(isinstance(expected,str) and bool(HASH_RE.fullmatch(expected)),
              "Original source price hash missing")
        check(sha(path) == expected,"Original price file changed since G2.9")
        price = pd.read_pickle(path)
        check(isinstance(price,pd.DataFrame) and {"date","close"}.issubset(price.columns),
              "Original price snapshot shape changed")
        obs = utc_days(price["date"], pd)
        dateset = sorted(set(obs.tolist()))
        check(len(dateset) == len(obs), "Original price bar date duplicates found")
        check(len(dateset) >= 61, "Original price series insufficient for 60 historical dates")
        dates[symbol] = dateset
        del price
    check(len(dates) == 174 and "SPY" in dates,
          "FMP stock/SPY original cache coverage no longer 174")

    result = {
        "schema_version":"dtrm.ic.g2.a3_per_event_bar_date_coverage.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "original_code_commit":PIN,
        "original_g2_6_report_sha256":BIND_SHA,
        "original_g2_9_report_sha256":G29_SHA,
        "original_g2_10_report_sha256":G210_SHA,
        "source_snapshot_suffix":"2026-07-05",
        "source_cache_files_checked":174,
        "cohorts":{},
        "v1_v4_event_pair_key_order_and_date_agreement":None,
        "original_validation_pair_date_coverage_checked":False,
        "price_close_column_values_loaded_in_memory_by_pickle":True,
        "price_close_values_accessed_for_calculation":False,
        "model_predictions_accessed_for_calculation":False,
        "forward_targets_or_returns_accessed_for_calculation":False,
        "volatility_or_economic_metrics_calculated":False,
        "provider_acquisition_vintage_verified":False,
        "corporate_action_adjustments_point_in_time_verified":False,
        "g2_revision_protocol_frozen":False,
        "g3_scoring_authorized":False,
        "caveats":[
            "SOURCE_DATE coverage is strictly before event UTC calendar date only, without reading any close values.",
            "Late 2026-07-05 price-cache file cannot authenticate its price revisions or adjustments at earlier May/June event times.",
            "The V0 validation set and its date/ticker coverage are not certified by this source-only step.",
            "Every V2/V3/V4 outcome was previously consumed; any later A3 results must be labeled POST_OUTCOME_EXPLORATORY.",
            "No source of September/October new 60-calendar-day independent holdout was identified in previous G1.3 scans."
        ]
    }
    row_keys = {}
    all_good = True
    for cohort, (key, filename, expected_n, low, high) in FILES.items():
        path = src_root/filename
        check(path.is_file() and not path.is_symlink(),
              "Missing original old frozen signals: "+filename)
        exp_hash = source_sha.get(key)
        check(isinstance(exp_hash,str) and HASH_RE.fullmatch(exp_hash),
              "Original G2.6 old signal SHA key unavailable: "+key)
        check(sha(path) == exp_hash, "Original frozen signal SHA mismatch: "+key)
        signals = pd.read_pickle(path)
        observed = {"original_signal_rows":len(signals) if hasattr(signals,"__len__") else None,
                    "expected_rows":expected_n,
                    "source_sha256":exp_hash,
                    "required_source_columns_present":False,
                    "scope_start":low,"scope_end":high}
        if not isinstance(signals,pd.DataFrame) or not set(SOURCE_COLUMNS).issubset(signals.columns):
            observed["status"]="SIGNAL_DATE_TICKER_SCHEMA_OPEN"
            observed["reported_column_names"] = ([str(x) for x in signals.columns]
                                                  if isinstance(signals,pd.DataFrame) else [])
            all_good = False
            result["cohorts"][cohort] = observed
            continue
        check(len(signals) == expected_n,
              "Frozen signal row count drift in "+cohort)
        keys=signals[list(SOURCE_COLUMNS)].copy()
        keys["ticker"] = keys["ticker"].astype(str).map(canonical)
        keys["date_dt"] = pd.to_datetime(keys["date_dt"],utc=True,errors="coerce")
        check(not keys["date_dt"].isna().any(),"Frozen event datetime unparseable")
        check(not keys.duplicated(["news_id","ticker"]).any(),
              "Original news/ticker repeated, cannot count independent pairs")
        cutoff=keys["date_dt"].dt.date.tolist()
        check(min(cutoff).isoformat()>=low and max(cutoff).isoformat()<=high,
              "Frozen event source outside original declared cohort dates")
        ticker=keys["ticker"].tolist()
        observed.update({
          "status":"STRUCTURAL_DATE_COVERAGE_CHECKED",
          "required_source_columns_present":True,
          "distinct_tickers":len(set(ticker)),
          "earliest_event_date":min(cutoff).isoformat(),
          "last_event_date":max(cutoff).isoformat(),
          "missing_original_price_cache_ticker_pairs":0,
          "full_60_prior_return_date_coverage_pairs":0,
          "min_40_prior_return_date_coverage_pairs":0,
          "shorter_than_40_prior_return_date_coverage_pairs":0,
          "missing_market_reference_prior_60_date_count":0,
          "source_event_days_after_price_snapshot":0,
          "utc_calendar_event_day_bar_included":False
        })
        for symbol,event_date in zip(ticker,cutoff):
            d=dates.get(symbol)
            if d is None:
                observed["missing_original_price_cache_ticker_pairs"]+=1
                continue
            count=bisect_left(d,event_date)
            spy_count=bisect_left(dates["SPY"],event_date)
            if spy_count<61:
                observed["missing_market_reference_prior_60_date_count"]+=1
            if count>=61:
                observed["full_60_prior_return_date_coverage_pairs"]+=1
            elif count>=41:
                observed["min_40_prior_return_date_coverage_pairs"]+=1
            else:
                observed["shorter_than_40_prior_return_date_coverage_pairs"]+=1
        observed["all_pairs_have_60_prior_return_date_coverage"] = (
            observed["full_60_prior_return_date_coverage_pairs"]==expected_n
            and observed["missing_original_price_cache_ticker_pairs"]==0
            and observed["missing_market_reference_prior_60_date_count"]==0
        )
        if not observed["all_pairs_have_60_prior_return_date_coverage"]:
            all_good=False
        row_keys[cohort]=[(str(x),y,z.isoformat()) for x,y,z in
                         zip(keys["news_id"],ticker,cutoff)]
        result["cohorts"][cohort]=observed
        del signals,keys
    if ("V4_original_V1_signals" in row_keys
        and "V4_original_V4_signals" in row_keys):
        result["v1_v4_event_pair_key_order_and_date_agreement"]=(
            row_keys["V4_original_V1_signals"]==
            row_keys["V4_original_V4_signals"]
        )
        if result["v1_v4_event_pair_key_order_and_date_agreement"] is not True:
            all_good=False
    else:
        all_good=False

    state=("G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN"
           if all_good else "G2_12_A3_PARTIAL_EVENT_PAIR_BAR_DATES_OR_SOURCE_SCHEMA_OPEN")
    result["status"]=state
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.12:",state)
    print("Original source price cache files:",len(dates),
          "; provider vintage verified:",False)
    for cohort,v in result["cohorts"].items():
        print(cohort,"rows",v["original_signal_rows"],
              "schema",v["status"],
              "full_60_prior_return_date_coverage_pairs",
              v.get("full_60_prior_return_date_coverage_pairs"),
              "missing_ticker_pairs",
              v.get("missing_original_price_cache_ticker_pairs"))
    print("V1 vs V4 event ID/ticker/date order agreed:",
          result["v1_v4_event_pair_key_order_and_date_agreement"])
    print("Report:",out)
    print("No close prices accessed in calculations, no returns, volatility, labels, model inference or portfolio P&L.")
    print("G2 UNFROZEN; G3 BLOCKED.")
    return 0 if all_good else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G2.12 HALTED:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
