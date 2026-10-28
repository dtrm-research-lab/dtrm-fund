#!/usr/bin/env python3
"""G3.2 A3 original baseline/P10/volatility SOURCE-ONLY preflight.

No access to original V2/V3/V4 forward targets or financial labels.
No retraining. Preserves the original q25/K10 legacy ranker, V0-only
calibrated daily-volatility cutoff and original 61 prior source closes.
Every original price and signal file is SHA-verified before trusted
local Pandas Pickle deserialization. Emits ONLY aggregated counts, not
news IDs, row scores, risk array, sampled dates, labels or prices.
Point-in-time vendor quote vintage and adjustments NOT authenticated.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from ic_g3_2_a3_numeric_source_quality_gate import (
    G26,G29,G210,G212,G213,V0_SHA,OLD_SIGNALS,canon,
    evidence,validation_source_checks,sha,must,
)
from ic_g3_2_a3_valid_only_cutoff import (
    recheck_all_historical_price_hashes,
    ORIGINAL_Q25,OFFSET
)

CUTOFF_SHA="f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21"
QUALITY_SHA="91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a"
ORIGINAL_HISTORICAL="c7502a690162459cdfb3413573e3133c42efb126"
CODE_PATH="research/reviews/icomputing_2026/"
SCRIPTS=(
 "ic_g3_2_a3_original_3arm_source_preflight.py",
 "test_ic_g3_2_a3_original_3arm_source_preflight.py",
 "ic_g3_2_a3_valid_only_cutoff.py",
 "test_ic_g3_2_a3_valid_only_cutoff.py",
 "ic_g3_2_a3_numeric_source_quality_gate.py",
 "test_ic_g3_2_a3_numeric_source_quality_gate.py",
 "ic_g2_g3_exploratory_core.py",
 "test_ic_g2_g3_exploratory_core.py",
)
EXPECTED={"V2":4449,"V3":2827,"V4":40320}
CUTOFF=0.020823002555902668

def check_code(repo,commit):
    must(len(commit)==40 and all(x in "0123456789abcdef" for x in commit),
         "Exact 40-digit immutable Git code commit required")
    root=Path(repo).expanduser()
    must(root.is_dir() and not root.is_symlink(),"Missing original review repo")
    for name in SCRIPTS:
        local=Path(__file__).resolve().with_name(name)
        must(local.is_file() and not local.is_symlink(),"Missing bound code/test: "+name)
        original=subprocess.run(
            ["git","-C",str(root),"show",commit+":"+CODE_PATH+name],
            check=True,capture_output=True).stdout
        must(hashlib.sha256(original).hexdigest()==sha(local),
             "Unreviewed A3 source preflight code/test: "+name)

def counts(signals,prices,cohort,risk_cutoff=CUTOFF):
    """Strict original signal/q25/order and no-outcome admission checker."""
    import pandas as pd
    import numpy as np
    from ic_g2_g3_exploratory_core import trailing_volatility_60
    must(cohort in EXPECTED and len(signals)==EXPECTED[cohort],
         "Unexpected original old sample or cohort")
    required={"news_id","ticker","date_dt","baseline_prediction",
              "p10_raw","p10_calibrated","p10_pass"}
    must(isinstance(signals,pd.DataFrame) and required.issubset(signals.columns),
         "Original old signal source schema changed")
    must(not signals[["news_id","ticker","date_dt"]].isna().any().any()
         and not signals.duplicated(["news_id","ticker"]).any(),
         "Null or duplicated original sample identity")
    when=pd.to_datetime(signals["date_dt"],utc=True,errors="coerce")
    must(not when.isna().any(),"Unparseable original event datetime")
    score=signals["baseline_prediction"].to_numpy(dtype=np.float64)
    raw=signals["p10_raw"].to_numpy(dtype=np.float64)
    p10=signals["p10_calibrated"].to_numpy(dtype=np.float64)
    original=signals["p10_pass"]
    must(np.isfinite(score).all() and np.isfinite(raw).all() and
         np.isfinite(p10).all(),
         "Nonfinite original baseline or P10 score")
    must(bool(np.allclose(p10,raw+OFFSET,rtol=0,atol=1e-6)),
         "Original frozen calibrated-P10 offset drift")
    must(original.isin([True,False]).all() and
         all(isinstance(x,(bool,np.bool_)) for x in original.tolist()),
         "Original P10 admission flags not strictly boolean")
    pmask=np.asarray(original.to_numpy(),dtype=bool)
    must(np.array_equal(pmask,p10>=ORIGINAL_Q25),
         "Original q25 veto mask differs from original source flags")
    risk=[]
    memo={}
    for stock,event in zip(signals["ticker"].tolist(),when.dt.date.tolist()):
        key=(canon(stock),event)
        if key not in memo:
            must(key[0] in prices,"Original source-price ticker missing")
            days,close=prices[key[0]]
            vol,reason=trailing_volatility_60(days,close,event)
            must(reason=="OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED"
                 and vol is not None,
                 "Original source common-case numeric quality drift: "+reason)
            memo[key]=vol
        risk.append(memo[key])
    rmask=np.asarray(risk,dtype=np.float64)<=risk_cutoff
    n=len(score);k=int(.1*n)
    must(k>0,"Original Top-K capacity empty")
    ranking=np.argsort(-score)
    pselected=ranking[pmask[ranking]][:k]
    rselected=ranking[rmask[ranking]][:k]
    no_veto=ranking[:k]
    both_full=len(pselected)==len(rselected)==k
    def count_selected_overlap(a,b):
        return len(set(a.tolist()).intersection(b.tolist()))
    return {
      "old_original_pairs":n,
      "common_source_quality_eligible_pairs":n,
      "k_floor_10_percent":k,
      "baseline_admitted_pairs":n,
      "p10_original_q25_admitted_pairs":int(pmask.sum()),
      "volatility_v0_cutoff_admitted_pairs":int(rmask.sum()),
      "both_vetoes_admitted_pairs":int((pmask&rmask).sum()),
      "p10_original_full_k_feasible":bool(len(pselected)==k),
      "volatility_original_full_k_feasible":bool(len(rselected)==k),
      "three_arms_all_full_k_feasible":bool(both_full),
      "top_k_overlap_baseline_p10":count_selected_overlap(no_veto,pselected),
      "top_k_overlap_baseline_volatility":count_selected_overlap(no_veto,rselected),
      "top_k_overlap_p10_volatility":count_selected_overlap(pselected,rselected),
      "saved_risk_cutoff":risk_cutoff,
      "original_q25_cutoff":ORIGINAL_Q25,
      "price_vintage_verified":False,
      "old_target_labels_opened":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("review-repo","code-commit","original-price-cache",
                "original-local-data","g2-6-binding","g2-9-report",
                "g2-10-report","g2-12-report","g2-13-report",
                "g3-2-numeric-quality-report","g3-2-valid-cutoff-report",
                "out"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--authorize-original-a3-three-arm-source-only-preflight",
                   action="store_true")
    p.add_argument("--trust-original-audited-pickles",action="store_true")
    p.add_argument("--acknowledge-vintage-unverified",action="store_true")
    a=p.parse_args()
    if not(a.authorize_original_a3_three_arm_source_only_preflight
           and a.trust_original_audited_pickles
           and a.acknowledge_vintage_unverified):
        p.error("New consent needed for source-only A3 original signal and price access")
    out=Path(a.out).expanduser()
    must(not out.exists(),"Refuse to overwrite any previous A3 report")
    check_code(a.review_repo,a.code_commit.lower())
    g26=evidence(a.g2_6_binding,G26)
    g29=evidence(a.g2_9_report,G29)
    g210=evidence(a.g2_10_report,G210)
    g212=evidence(a.g2_12_report,G212)
    g213=evidence(a.g2_13_report,G213)
    quality=evidence(a.g3_2_numeric_quality_report,QUALITY_SHA)
    cutoff=evidence(a.g3_2_valid_cutoff_report,CUTOFF_SHA)
    manifest=validation_source_checks(g29,g210,g212,g213,g26)
    must(quality.get("status")==
         "G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED"
         and quality.get("old_common_quality_eligible_pairs")==47596
         and quality.get("validation_common_quality_eligible_pairs")==19880
         and quality.get("forward_outcome_labels_targets_or_returns_accessed") is False,
         "Original G3.2 price numeric sample quality not PASS")
    must(cutoff.get("status")==
         "G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED"
         and cutoff.get("original_g3_2_numeric_quality_report_sha256")==QUALITY_SHA
         and cutoff.get("original_validation_source_check",{}).get("pairs")==19880
         and cutoff.get("risk_threshold_uses_validation_only") is True
         and cutoff.get("old_forward_targets_opened") is False
         and cutoff.get("v2_v3_v4_model_outcome_comparisons_executed") is False
         and cutoff.get("original_price_vendor_acquisition_vintage_verified") is False
         and cutoff.get("original_price_point_in_time_adjustments_verified") is False
         and cutoff.get("a3_old_outcome_access_authorized") is False,
         "Original V0-only risk cutoff report lineage not approved")
    # NO adjustment or tolerance relaxation; report exact source floats.
    must(cutoff.get("retrospective_stock_volatility_cutoff_daily_std_ddof1")==CUTOFF
         and cutoff.get("original_validation_source_check",{}).get("source_p10_q25_frozen")==ORIGINAL_Q25,
         "Original precommitted validation-only risk/P10 cutoffs changed")
    root=Path(a.original_local_data).expanduser()
    must(root.is_dir() and not root.is_symlink(),"Original cohort signal directory unsafe")
    bound={}
    for cohort,(key,filename,n) in OLD_SIGNALS.items():
        file=root/filename
        must(file.is_file() and not file.is_symlink() and
             file.stat().st_size>0 and sha(file)==
                g26["g2_5_historic_old_cohort_input_sha256"][key],
             "Original SHA-bound cohort signal changed: "+cohort)
        bound[cohort]=file
    files=recheck_all_historical_price_hashes(
        manifest,a.original_price_cache)
    # Old signals and ALL 174 saved price Pickles SHA-audited before
    # deserializing any of them. NO target, label or outcome source.
    import pandas as pd
    prices={}
    for symbol,file in files.items():
        frame=pd.read_pickle(file)
        must(isinstance(frame,pd.DataFrame) and
             {"date","close"}.issubset(frame.columns),
             "Original saved price schema invalid: "+symbol)
        dates=pd.to_datetime(frame["date"],utc=True,errors="coerce")
        must(not dates.isna().any(),"Original saved daily bar date invalid")
        days=dates.dt.date.tolist()
        must(len(days)==len(set(days)),"Duplicate original stock bar dates")
        prices[symbol]=(days,frame["close"].tolist())
        del frame
    cohorts={}
    for cohort,signal_file in bound.items():
        signals=pd.read_pickle(signal_file)
        cohorts[cohort]=counts(signals,prices,cohort)
        del signals
    total=sum(v["old_original_pairs"] for v in cohorts.values())
    must(total==47596,"Original old pair N unexpectedly changed")
    state=("G3_2_A3_3_ARM_ORIGINAL_SOURCE_ONLY_K10_FEASIBILITY_PASS_OUTCOMES_BLOCKED"
           if all(v["three_arms_all_full_k_feasible"] for v in cohorts.values())
           else "G3_2_A3_3_ARM_ORIGINAL_SOURCE_ONLY_K10_INFEASIBILITY_DOCUMENTED_OUTCOMES_BLOCKED")
    response={
      "schema_version":"dtrm.ic.g3.2.a3_original_3arm_source_preflight.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":state,
      "immutable_source_code_commit":a.code_commit.lower(),
      "original_science_source_commit":ORIGINAL_HISTORICAL,
      "original_price_snapshot_suffix":"2026-07-05",
      "original_g3_2_numeric_source_quality_sha256":QUALITY_SHA,
      "original_validation_only_cutoff_report_sha256":CUTOFF_SHA,
      "original_g2_report_sha256":{
        "g2_6":G26,"g2_9":G29,"g2_10":G210,
        "g2_12":G212,"g2_13":G213,
      },
      "original_historical_pairs":total,
      "full_k_policy":"K=floor(0.10*N) on original common eligible sample",
      "original_historical_quality_common_sample_full":True,
      "cohorts":cohorts,
      "any_forward_target_or_old_outcome_opened":False,
      "a3_comparison_or_bootstrap_executed":False,
      "a3_old_outcome_comparison_authorized":False,
      "no_independent_new_60_day_holdout":True,
      "vendor_asof_acquisition_verified":False,
      "point_in_time_corporate_action_adjustment_verified":False,
      "scientific_scope":"DATE_RESTRICTED_POST_OUTCOME_EXPLORATORY_NOT_REALIZED_PNL",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as stream:
        json.dump(response,stream,indent=2,ensure_ascii=False)
        stream.write("\n")
    print("G3.2 A3 ORIGINAL 3-ARM PREFLIGHT:",state)
    for cohort,d in cohorts.items():
        print(cohort,"N",d["old_original_pairs"],"K",d["k_floor_10_percent"],
              "P10 admitted",d["p10_original_q25_admitted_pairs"],
              "risk admitted",d["volatility_v0_cutoff_admitted_pairs"],
              "both",d["both_vetoes_admitted_pairs"],
              "both feasible",d["three_arms_all_full_k_feasible"],
              "Top-K P10-risk overlap",d["top_k_overlap_p10_volatility"])
    print("Report:",out)
    print("No original financial outcomes/targets/labels accessed. No risk-policy effects or bootstrap.")
    print("Original quote vintage/adjustments UNVERIFIED; A3 outcome comparison BLOCKED.")
    return 0 if state.endswith("FEASIBILITY_PASS_OUTCOMES_BLOCKED") else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.2 A3 SOURCE PREFLIGHT HALTED:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
