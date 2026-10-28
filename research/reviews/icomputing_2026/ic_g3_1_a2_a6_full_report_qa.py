#!/usr/bin/env python3
"""Read-only QA of already computed G3.1 A2/A6 point/full reports.

This file reads ONLY locally published aggregate JSON result reports,
never the original per-row price/news/Pickle/target/model files.
It cannot authorize or rerun experiments.

Output: source digests, 18 fixed point cell preservation,
36 aggregate cluster bootstrap statuses, CI withheld when a
single resampled draw is infeasible, and unadjusted descriptive
95% intervals only. NOT independent prospective confirmation,
familywise multiple-testing significance or realized strategy P&L.

Original scientific runner is frozen separately at 0c5e433f...
This is a NEW post-run independent AUDIT reader, not a
modification of the frozen scientific calculation code.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

POINT_SHA="8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb"
FULL_SHA="53c4618f86f46a80a5a783c3449a8d120379f26c8d459c8e740dd4fb63697968"
CODE_SHA="0c5e433f10ce742bc129b666dfc4551f4b2fd21b"
G3_0_SHA="a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a"
SOURCES_SHA="3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8"
G2_FREEZE="3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0"
VALIDATION_THRESHOLDS={"0.15":-0.17323055863380432,
                       "0.25":-0.16665692627429962,
                       "0.35":-0.16293590515851974}
EXPECTED={(arm,cohort,setting) for arm,vals in
          (("A2",(.15,.25,.35)),("A6",(.05,.1,.15)))
          for cohort in ("V2","V3","V4") for setting in vals}
ROWS={"V2":4449,"V3":2827,"V4":40320}
POINT_FIELDS=("n_original_pairs","k_required","admitted_pairs",
              "admitted_rate","full_k_feasible",
              "baseline_mean_forward_excess_beta",
              "veto_mean_forward_excess_beta",
              "delta_mean_forward_excess_beta",
              "baseline_hit_rate","veto_hit_rate",
              "delta_hit_rate","inferential_scope")
CLUSTERS=(("news","news_cluster_bootstrap",20260821),
          ("ticker","ticker_cluster_bootstrap",20260822))

def must(ok,msg):
    if not ok:raise ValueError(msg)

def _sha(path:Path)->str:
    must(path.is_file() and not path.is_symlink(),
         "Missing/unsafe report: "+str(path))
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for buf in iter(lambda:fp.read(1024*1024),b""):
            h.update(buf)
    return h.hexdigest()

def _load(path,expected):
    p=Path(path).expanduser()
    must(_sha(p)==expected,
         "Exact operator-attested report SHA mismatch: "+str(p))
    with p.open("r",encoding="utf-8") as fp:
        obj=json.load(fp)
    must(isinstance(obj,dict),"Expected JSON object: "+str(p))
    return obj

def _safe_int(x,low,high):
    return type(x) is int and low<=x<=high

def qa(point,full):
    """Strict structural and numerical QA, no saved original datasets."""
    must(point.get("status")==
         "G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN",
         "Original point-only state invalid")
    must(full.get("status")==
         "G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY",
         "Original full state invalid")
    must(point.get("mode")=="point" and full.get("mode")=="full",
         "Expected distinct original point/full modes")
    for label,r in (("point",point),("full",full)):
        must(r.get("immutable_a2_a6_runner_commit")==CODE_SHA,
             label+" calculation commit differs from 71-test frozen source")
        must(r.get("original_g2_freeze_commit")==G2_FREEZE,
             label+" original G2 scientific protocol drift")
        must(r.get("original_g3_0_source_report_sha256")==G3_0_SHA,
             label+" G3.0 original P10/ranker report drift")
        must(r.get("six_original_source_report_sha256")==SOURCES_SHA,
             label+" original six-file SHA validation report drift")
        must(r.get("a3_price_volatility_experiment_authorized") is False,
             label+" unexpected A3 permission")
        must(r.get("no_independent_matured_new_60_day_holdout") is True,
             label+" misleading independent holdout attestation")
        must(r.get("all_old_outcomes_were_previously_consulted") is True,
             label+" missing retrospective post-outcome disclosure")
        must(r.get("financial_target_definition")==
             "60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",
             label+" target meaning drift")
        res=r.get("results")
        must(isinstance(res,dict) and
             res.get("cells_expected")==18 and
             res.get("cutoffs_validation_only")==VALIDATION_THRESHOLDS and
             res.get("frozen_q25")==VALIDATION_THRESHOLDS["0.25"],
             label+" validation cutoffs or expected cell count changed")
        must(res.get("target_is_tradable_portfolio_profit") is False and
             res.get("independent_new_60_day_holdout") is False and
             res.get("g3_1_execution_authorized_by_this_module") is False,
             label+" result interpretation/permission contract drift")
    pr=point["results"]["cells"];fr=full["results"]["cells"]
    must(isinstance(pr,list) and isinstance(fr,list) and
         len(pr)==len(fr)==18,"Not exactly 18 point and 18 full result rows")
    must(full["results"]["replicates_per_news_or_ticker_cell"]==10000 and
         point["results"]["replicates_per_news_or_ticker_cell"]==0,
         "Full/point bootstrap count claim differs from protocol")
    keys=set()
    record={}
    withheld=0;valid=0;both_exclude_zero=0;both_intervals_valid=0
    for n,(p,f) in enumerate(zip(pr,fr)):
        key=(f.get("work_package"),f.get("cohort"),f.get("setting"))
        must(key==(p.get("work_package"),p.get("cohort"),p.get("setting")),
             "Original point/full row order or key changed")
        must(key in EXPECTED and key not in keys,
             "Non-prespecified or duplicate q/K/cohort: "+str(key))
        keys.add(key)
        must(f.get("n_original_pairs")==ROWS[key[1]],
             "Unexpected original cohort size: "+str(key))
        must(f.get("full_k_feasible") is True,
             "Original 18/18 sample feasibility changed: "+str(key))
        must(p.get("news_cluster_bootstrap") is None and
             p.get("ticker_cluster_bootstrap") is None,
             "Original point report secretly contains cluster intervals")
        for field in POINT_FIELDS:
            must(p.get(field)==f.get(field),
                 "Original point estimate changed in full: "+
                 str(key)+" "+field)
        record[key]={}
        for which,field,seed in CLUSTERS:
            x=f.get(field)
            must(isinstance(x,dict) and
                 x.get("method")=="cluster_bootstrap" and
                 x.get("seed")==seed and
                 x.get("replicates")==10000 and
                 x.get("interpretation")==
                      "POST_OUTCOME_EXPLORATORY_NOT_INDEPENDENT_CONFIRMATION",
                 "Missing or changed fixed original bootstrap: "+
                 str(key)+" "+which)
            bad=x.get("infeasible_replicates")
            must(_safe_int(bad,0,10000),
                 "Noninteger/invalid infeasibility count: "+str(key))
            mean=x.get("ci95_delta_topk_mean")
            hit=x.get("ci95_delta_topk_hit_rate")
            if bad:
                must(mean is None and hit is None,
                     "Invalid interval published despite infeasible K: "+
                     str(key)+" "+which)
                withheld+=1
                status="WITHHELD"
                exclude_zero=None
            else:
                for interval,metric in ((mean,"mean"),(hit,"hit")):
                    must(isinstance(interval,list) and len(interval)==2 and
                         all(type(z) in (float,int) and
                             math.isfinite(z) for z in interval) and
                         interval[0]<=interval[1],
                         "Missing/nonfinite/unordered "+metric+
                         " CI for "+str(key)+" "+which)
                valid+=1
                status="VALID"
                exclude_zero=bool(mean[0]>0 or mean[1]<0)
            record[key][which]={
                "status":status,"infeasible_replicates":bad,
                "mean_ci95":mean,"hit_ci95":hit,
                "mean_ci95_excludes_zero_unadjusted":exclude_zero
            }
        if all(record[key][c]["status"]=="VALID" for c in ("news","ticker")):
            both_intervals_valid+=1
            if all(record[key][c]["mean_ci95_excludes_zero_unadjusted"]
                   for c in ("news","ticker")):
                both_exclude_zero+=1
    must(keys==EXPECTED,"Missing prespecified original grid cells")
    # At fixed q25/K10 A2 and fixed K10 A6, the same seed and original
    # data must produce identical intervals and point effects.
    for cohort in ROWS:
        a=record[("A2",cohort,.25)]
        b=record[("A6",cohort,.10)]
        must(a==b,
             "Duplicated q25/K10 policy bootstrap no longer deterministic: "+cohort)
    must(valid+withheld==36,"Wrong number of news/ticker CI blocks")
    return {
      "status":"G3_1_A2_A6_FULL_36_CLUSTER_BLOCKS_REPORT_QA_PASS",
      "original_fixed_cells":18,
      "expected_cluster_blocks":36,
      "valid_cluster_blocks":valid,
      "withheld_cluster_blocks":withheld,
      "cells_with_both_news_and_ticker_intervals_valid":both_intervals_valid,
      "cells_both_unadjusted_mean_cis_exclude_zero":both_exclude_zero,
      "cluster_results":record,
      "independent_holdout":False,
      "familywise_multiple_testing_adjusted":False,
      "target_is_realized_portfolio_pnl":False,
      "interpretation":"POST_OUTCOME_EXPLORATORY_NOT_INDEPENDENT_CONFIRMATION"
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--point",required=True)
    p.add_argument("--full",required=True)
    args=p.parse_args()
    point=_load(args.point,POINT_SHA)
    full=_load(args.full,FULL_SHA)
    summary=qa(point,full)
    print("G3.1 FULL JSON REVIEW:",summary["status"])
    print("Point report SHA256:",POINT_SHA)
    print("Full report SHA256:",FULL_SHA)
    print("Fixed original point cells:",summary["original_fixed_cells"])
    print("Cluster blocks:",summary["expected_cluster_blocks"])
    print("Valid CI blocks:",summary["valid_cluster_blocks"])
    print("Withheld CI blocks:",summary["withheld_cluster_blocks"])
    print("Cells with both news and ticker valid CI:",
          summary["cells_with_both_news_and_ticker_intervals_valid"])
    print("Cells with BOTH unadjusted mean CIs excluding zero:",
          summary["cells_both_unadjusted_mean_cis_exclude_zero"])
    for (arm,cohort,setting),entry in summary["cluster_results"].items():
        for name,d in entry.items():
            print(arm,cohort,setting,name,
                  "status",d["status"],
                  "infeasible",d["infeasible_replicates"],
                  "mean_CI95",d["mean_ci95"],
                  "hit_CI95",d["hit_ci95"])
    print("Inference: POST_OUTCOME_EXPLORATORY only; "
          "multiple testing NOT adjusted; no new holdout; NO actual portfolio P&L")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as e:
        print("G3.1 FULL REPORT QA HALTED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(2)
