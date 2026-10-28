#!/usr/bin/env python3
"""G3.2 A3 original stock-price NUMERIC SOURCE QUALITY; NO outcomes.

This is the FIRST *source-only* step after G3.1 A2/A6 is closed.
On opt-in, SHA-check all 174 original July-5, 2026 locally archived
FMP Pickles BEFORE loading trusted original price source data.
Read original V0 VALID identifiers/date and original V2/V3/V4 old
signal identifiers/date, not their outcomes. For every original pair
evaluate only the frozen EXACT 61 strictly pre-event closes -> 60
non-imputed simple returns -> sample std ddof=1.
No risk cutoff, ranker, P10, targets, comparisons, 10k bootstrap,
new optimal thresholds, live price feeds, portfolio P&L, A4 or A5.

A source row that fails becomes A3 common-sample excluded with an
unaltered reason. Price values and risk scores NEVER leave memory or
get written; only count summaries. SHA-check reports and source
snapshots; a report cannot certify FMP vendor acquisition vintage
or contemporaneous split/dividend-adjustment authenticity.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
G29="65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb"
G210="f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3"
G212="e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f"
G213="e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7"
G26="1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
V0_SHA="3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724"
OLD_SIGNALS={
  "V2":("v2_signals","probabilistic_v2_holdout_signals_2026-06-10.pkl",4449),
  "V3":("v3_signals","probabilistic_v3_holdout_signals_2026-06-14.pkl",2827),
  "V4":("v4_signals","probabilistic_v4_holdout_signals_2026-06-06.pkl",40320),
}
CODE_REL="research/reviews/icomputing_2026/"
CORE_NAME="ic_g2_g3_exploratory_core.py"
REQUIRED_VALID=("news_id","ticker","date_dt","split")
REQUIRED_SIGNAL=("news_id","ticker","date_dt")
N_VALID=19880
N_OLD=47596

def must(test,reason):
    if not test:raise RuntimeError(reason)

def sha(p):
    p=Path(p).expanduser()
    must(p.is_file() and not p.is_symlink(),"Missing/symlinked original: "+p.name)
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def evidence(path,digest):
    p=Path(path).expanduser()
    must(sha(p)==digest,"Archived G2 source report SHA differs: "+p.name)
    out=json.loads(p.read_text(encoding="utf-8"))
    must(isinstance(out,dict),"Archived source JSON not object: "+p.name)
    return out

def canon(symbol):
    return "BRK-B" if str(symbol)=="BRK.B" else str(symbol)

def _code_sha_check(review_repo,code_commit):
    must(len(code_commit)==40 and all(x in "0123456789abcdef" for x in code_commit),
         "Exact 40-character immutable Git revision required")
    root=Path(review_repo).expanduser()
    must(root.is_dir() and not root.is_symlink(),"Source Git repository missing")
    for name in ("ic_g3_2_a3_numeric_source_quality_gate.py",CORE_NAME,
                 "test_ic_g3_2_a3_numeric_source_quality_gate.py"):
        local=Path(__file__).resolve().with_name(name)
        must(local.is_file() and not local.is_symlink(),
             "Pinned code/test file missing: "+name)
        original=subprocess.run(
            ["git","-C",str(root),"show",code_commit+":"+CODE_REL+name],
            capture_output=True,check=True).stdout
        must(hashlib.sha256(original).hexdigest()==sha(local),
             "G3.2 A3 local code/test differs from exact reviewed Git SHA: "+name)

def validation_source_checks(g29,g210,g212,g213,g26):
    must(g29.get("status")==
         "G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN",
         "Original price archive not G2.9 source gate PASS")
    must(g210.get("status")==
         "G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN",
         "G2.10 original dated-bar metadata not PASS")
    must(g212.get("status")==
         "G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN"
         and g212.get("v1_v4_event_pair_key_date_set_agreement") is True,
         "G2.12 original V2/V3/V4 pairs/stock bar-date gate not PASS")
    must(g213.get("status")==
         "G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN",
         "G2.13 V0 validation 19880/19880 bar-date gate not PASS")
    must(g26.get("status")==
         "G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
         "G2.6 original signal sources not SHA bound")
    must(g213.get("original_v0_model_rows_current_sha256")==V0_SHA
         and g213.get("original_valid_split_rows")==N_VALID
         and g213.get("original_price_cache_files_sha_checked")==174
         and g213.get("original_g2_12_sha256")==G212
         and g212.get("source_cache_files_checked")==174
         and g212.get("original_g2_9_report_sha256")==G29
         and g212.get("original_g2_10_report_sha256")==G210,
         "Previous original SHA-bound row/date count or ancestry drift")
    manifest=g29.get("watched_historical_filenames",{}).get("2026-07-05",[])
    must(isinstance(manifest,list) and len(manifest)==174,
         "G2.9 original July-5 cache does not contain 174 price file SHA entries")
    return manifest

def inspect_series(event_days,symbols,prices,volatility):
    """Aggregate only, memoize repeated original (symbol,event day)."""
    must(len(event_days)==len(symbols),"Pair date and ticker lengths disagree")
    seen={}
    counts=Counter()
    for symbol,day in zip(symbols,event_days):
        if symbol not in prices:
            status="MISSING_ORIGINAL_PRICE_SYMBOL"
        else:
            key=(symbol,day)
            if key not in seen:
                bars,close=prices[symbol]
                risk,reason=volatility(bars,close,day)
                must((risk is None)==(reason!="OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED"),
                     "A3 numeric volatility reason/value invariant violated")
                status=reason
                seen[key]=status
            status=seen[key]
        counts[status]+=1
    must(sum(counts.values())==len(symbols),"A3 numeric quality count incomplete")
    return dict(sorted(counts.items()))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review-repo",required=True)
    p.add_argument("--code-commit",required=True)
    p.add_argument("--original-price-cache",required=True)
    p.add_argument("--original-local-data",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--g2-9-report",required=True)
    p.add_argument("--g2-10-report",required=True)
    p.add_argument("--g2-12-report",required=True)
    p.add_argument("--g2-13-report",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--authorize-a3-price-numeric-source-quality-only",action="store_true")
    p.add_argument("--trust-original-audited-pickles",action="store_true")
    p.add_argument("--acknowledge-price-provider-vintage-unverified",action="store_true")
    args=p.parse_args()
    if not(args.authorize_a3_price_numeric_source_quality_only
           and args.trust_original_audited_pickles
           and args.acknowledge_price_provider_vintage_unverified):
        p.error("A3 ONLY: explicit consent to trusted original price Pickles and unverified vintage is REQUIRED")
    dest=Path(args.out).expanduser()
    must(not dest.exists(),"Never overwrite previous original source evidence")
    _code_sha_check(args.review_repo,args.code_commit.lower())
    g29=evidence(args.g2_9_report,G29)
    g210=evidence(args.g2_10_report,G210)
    g212=evidence(args.g2_12_report,G212)
    g213=evidence(args.g2_13_report,G213)
    g26=evidence(args.g2_6_binding,G26)
    manifest=validation_source_checks(g29,g210,g212,g213,g26)
    cache=Path(args.original_price_cache).expanduser()
    local=Path(args.original_local_data).expanduser()
    must(cache.is_dir() and not cache.is_symlink() and
         local.is_dir() and not local.is_symlink(),
         "Original historical source roots missing/unsafe")
    orig_rows=local/"legacy_model_rows_2026-05-01.pkl"
    must(sha(orig_rows)==V0_SHA,"Original V0 training/VALID row source SHA mismatch")
    for cohort,(source_key,filename,n) in OLD_SIGNALS.items():
        pth=local/filename
        must(pth.name==filename and
             sha(pth)==g26["g2_5_historic_old_cohort_input_sha256"][source_key],
             "Original old signal SHA drift: "+cohort)
    # SHA-check EVERY original price archive before deserializing ANY Pickle.
    guarded_prices={}
    for record in manifest:
        filename=record.get("filename","")
        must(isinstance(filename,str) and filename.endswith("_2026-07-05.pkl")
             and "/" not in filename and "\\" not in filename,
             "Price cache filename not a direct original July-5 file")
        name=canon(filename.split("_",1)[0])
        pth=cache/filename
        must(name not in guarded_prices,
             "Duplicate original symbol or alias: "+name)
        must(pth.stat().st_size==record.get("bytes") and
             sha(pth)==record.get("sha256_new_local_commitment"),
             "Original price source fingerprint changed: "+name)
        guarded_prices[name]=pth
    must(len(guarded_prices)==174 and "SPY" in guarded_prices,
         "Expected exact 173 original stocks plus SPY")
    # Import and trusted old Pickle reading occur only AFTER all hashes.
    import pandas as pd
    from ic_g2_g3_exploratory_core import trailing_volatility_60
    dated_prices={}
    for symbol,path in guarded_prices.items():
        frame=pd.read_pickle(path)
        must(isinstance(frame,pd.DataFrame) and
             {"date","close"}.issubset(frame.columns),
             "Original price source columns invalid")
        dates=pd.to_datetime(frame["date"],utc=True,errors="coerce")
        must(not dates.isna().any(),"Unparseable original price bar dates")
        bar_days=dates.dt.date.tolist()
        must(len(bar_days)==len(set(bar_days)),
             "Duplicate original daily bar dates for "+symbol)
        must(len(bar_days)>=61,"Original bar source has <61 daily prices: "+symbol)
        dated_prices[symbol]=(bar_days,frame["close"].tolist())
        del frame
    validated=pd.read_pickle(orig_rows)
    must(isinstance(validated,pd.DataFrame) and
         set(REQUIRED_VALID).issubset(validated.columns),
         "Original V0 model rows split/keys/date source invalid")
    valid=validated.loc[validated["split"].eq("valid"),list(REQUIRED_VALID)]
    must(len(valid)==N_VALID and
         not valid.duplicated(["news_id","ticker"]).any(),
         "Original V0 VALID pair count/key uniqueness drift")
    dt=pd.to_datetime(valid["date_dt"],utc=True,errors="coerce")
    must(not dt.isna().any(),"Original V0 event dates invalid")
    valid_counts=inspect_series(dt.dt.date.tolist(),
         [canon(v) for v in valid["ticker"].tolist()],
         dated_prices,trailing_volatility_60)
    cohorts={}
    total=0
    for cohort,(source_key,filename,n) in OLD_SIGNALS.items():
        original=pd.read_pickle(local/filename)
        must(isinstance(original,pd.DataFrame) and
             set(REQUIRED_SIGNAL).issubset(original.columns)
             and len(original)==n and
             not original.duplicated(["news_id","ticker"]).any(),
             "Original "+cohort+" source schema/count/key changed")
        when=pd.to_datetime(original["date_dt"],utc=True,errors="coerce")
        must(not when.isna().any(),"Original "+cohort+" event date invalid")
        scores=inspect_series(when.dt.date.tolist(),
             [canon(v) for v in original["ticker"].tolist()],
             dated_prices,trailing_volatility_60)
        cohorts[cohort]={
           "original_pairs":n,
           "numeric_quality_reasons":scores,
           "common_quality_eligible_pairs":
              scores.get("OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED",0),
        }
        total+=n
    must(total==N_OLD,"Frozen 47596 original historical pairs drift")
    valid_ok=valid_counts.get("OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED",0)
    all_ok=sum(v["common_quality_eligible_pairs"] for v in cohorts.values())
    status=("G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED"
         if valid_ok==N_VALID and all_ok==N_OLD else
         "G3_2_A3_NUMERIC_CLOSE_SOURCE_PARTIAL_COMMON_SAMPLE_REQUIRED_VINTAGE_UNVERIFIED")
    result={
      "schema_version":"dtrm.ic.g3.2.a3_original_numeric_source_quality.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":status,"original_source_commit":PIN,
      "immutable_source_quality_code_commit":args.code_commit.lower(),
      "source_report_sha256":{"g2_6":G26,"g2_9":G29,
          "g2_10":G210,"g2_12":G212,"g2_13":G213},
      "original_price_snapshot_suffix":"2026-07-05",
      "price_files_sha_checked_before_pickle":174,
      "original_validation_pairs":N_VALID,
      "validation_numeric_quality_reasons":valid_counts,
      "validation_common_quality_eligible_pairs":valid_ok,
      "original_old_total_pairs":total,
      "old_common_quality_eligible_pairs":all_ok,
      "cohorts":cohorts,
      "numeric_source_policy":{
        "prior_bars":61,"prior_returns":60,
        "pre_event_utc_calendar_cutoff":True,
        "standard_deviation_ddof":1,
        "source_missing_close_imputation":False,
        "forty_return_fallback":False,
      },
      "price_close_values_accessed_for_quality":True,
      "numeric_volatility_scores_ever_serialized":False,
      "predictive_model_or_p10_scores_accessed":False,
      "forward_outcome_labels_targets_or_returns_accessed":False,
      "validation_risk_cutoff_computed":False,
      "A3_baseline_p10_risk_outcome_comparison_executed":False,
      "A3_bootstraps_executed":False,
      "original_provider_vintage_verified":False,
      "price_adjustments_point_in_time_verified":False,
      "scientific_scope":"RETROSPECTIVE_SOURCE_DATE_RESTRICTED_ONLY_NOT_PROSPECTIVE",
      "no_new_60day_independent_holdout":True,
      "g3_2_a3_outcome_execution_authorized":False,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as fp:
        json.dump(result,fp,indent=2,ensure_ascii=False)
        fp.write("\n")
    print("G3.2 A3 SOURCE NUMERIC QUALITY:",status)
    print("Price files SHA checked:",174)
    print("Validation eligible:",valid_ok,"/",N_VALID,
          "reasons:",valid_counts)
    for key,v in cohorts.items():
        print(key,"eligible:",v["common_quality_eligible_pairs"],
              "/",v["original_pairs"],"reasons:",v["numeric_quality_reasons"])
    print("Original old total eligible:",all_ok,"/",N_OLD)
    print("Report:",dest)
    print("No risk threshold, no P10 scores, no old target/labels, no new comparisons.")
    print("Price provider acquisition and adjusted corporate-action vintage: UNVERIFIED.")
    return 0 if all_ok==N_OLD and valid_ok==N_VALID else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.2 A3 SOURCE QUALITY HALTED:",
              type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
