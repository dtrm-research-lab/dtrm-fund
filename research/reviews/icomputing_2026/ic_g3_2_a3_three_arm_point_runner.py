#!/usr/bin/env python3
"""G3.2 A3 — BOUNDED, OWNER-CONSENTED original 3-arm POINT ONLY.

This module opens previously known 60d old V2/V3/V4 forward-excess-beta
target Pickles ONLY after a new explicit operator authorization, exact
reviewed Git SHA for this and all dependency/tests, original G2/G3.0/G3.1
source + model parity/checks, original 174 price-source SHA, original
V0 calibration report and G3.2 source-only preflight report.

Old target labels have already been seen during G3.1: A3 is secondary
POST_OUTCOME_EXPLORATORY. The original July-5 2026 saved adjusted
stock closes have unverified point-in-time provider acquisition vintage.
This is NOT a realized trading P&L, nor a new matured holdout.
No fitting, threshold tuning, raw targets/IDs or bootstrap in this step.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from ic_g3_1_a2_a6_protected_runner import make_release_checks
from ic_g3_2_a3_original_3arm_source_preflight import (
    check_code,counts as source_counts,EXPECTED,CUTOFF,
)
from ic_g3_2_a3_numeric_source_quality_gate import (
    G26,G29,G210,G212,G213,sha,must,evidence,validation_source_checks,
)
from ic_g3_2_a3_valid_only_cutoff import recheck_all_historical_price_hashes
from ic_g3_2_a3_three_arm_pure_points import (
    three_arm_point_effects,source_risk_admission_mask,
)

SOURCE_PREFLIGHT_SHA="9c03f925be0429b9b70407018d59f1df801682a9e7a821a6bb9c6d3ef80fe317"
VALID_CUTOFF_SHA="f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21"
QUALITY_SHA="91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a"
G31_ORIGINAL_POINT_SHA="8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb"
ORIGINAL_P10=-0.16665692627429962
PATH="research/reviews/icomputing_2026/"
MY_SCRIPTS=(
 "ic_g3_2_a3_three_arm_point_runner.py",
 "test_ic_g3_2_a3_three_arm_point_runner.py",
 "ic_g3_2_a3_three_arm_pure_points.py",
 "test_ic_g3_2_a3_three_arm_pure_points.py",
)

def verify_local_runner_code(review_repo,commit):
    must(len(commit)==40 and all(c in "0123456789abcdef" for c in commit),
         "Full immutable 40-character code SHA needed")
    root=Path(review_repo).expanduser()
    must(root.is_dir() and not root.is_symlink(),"Review repository unsafe")
    for filename in MY_SCRIPTS:
        local=Path(__file__).resolve().with_name(filename)
        must(local.is_file() and not local.is_symlink(),
             "Required original code/test missing: "+filename)
        archived=subprocess.run(
            ["git","-C",str(root),"show",commit+":"+PATH+filename],
            check=True,capture_output=True).stdout
        must(hashlib.sha256(archived).hexdigest()==sha(local),
             "A3 three-arm science code/test not SHA-pinned: "+filename)

def validate_aggregate_checkpoints(pre,point,cal,quality):
    must(pre.get("status")==
         "G3_2_A3_3_ARM_ORIGINAL_SOURCE_ONLY_K10_FEASIBILITY_PASS_OUTCOMES_BLOCKED"
         and pre.get("original_historical_pairs")==47596
         and pre.get("any_forward_target_or_old_outcome_opened") is False
         and pre.get("a3_comparison_or_bootstrap_executed") is False
         and pre.get("a3_old_outcome_comparison_authorized") is False
         and pre.get("original_historical_quality_common_sample_full") is True
         and pre.get("original_validation_only_cutoff_report_sha256")==VALID_CUTOFF_SHA
         and pre.get("original_g3_2_numeric_source_quality_sha256")==QUALITY_SHA
         and pre.get("vendor_asof_acquisition_verified") is False,
         "Original three-arm source-only K10 preflight not a SHA-authenticated PASS")
    must(point.get("status")==
         "G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN"
         and point.get("mode")=="point"
         and point.get("no_independent_matured_new_60_day_holdout") is True
         and point.get("financial_target_definition")==
             "60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",
         "Original G3.1 Phase-II original q25/K10 exact point evidence drift")
    must(cal.get("status")==
         "G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED"
         and cal.get("retrospective_stock_volatility_cutoff_daily_std_ddof1")==CUTOFF
         and cal.get("original_validation_source_check",{}).get("source_p10_q25_frozen")==ORIGINAL_P10
         and cal.get("risk_threshold_uses_validation_only") is True
         and cal.get("old_forward_targets_opened") is False
         and cal.get("a3_old_outcome_access_authorized") is False
         and cal.get("original_price_vendor_acquisition_vintage_verified") is False,
         "Original original VALID-only calibrated risk cutoff changed or unapproved")
    must(quality.get("status")==
         "G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED"
         and quality.get("validation_common_quality_eligible_pairs")==19880
         and quality.get("old_common_quality_eligible_pairs")==47596
         and quality.get("forward_outcome_labels_targets_or_returns_accessed") is False,
         "Original numeric quality/source common-sample not PASS")
    must(set(pre.get("cohorts",{}))==set(EXPECTED),
         "G3.2 source preflight omitted an original cohort")
    for cohort,n in EXPECTED.items():
        prev=pre["cohorts"][cohort]
        must(prev.get("old_original_pairs")==n
             and prev.get("common_source_quality_eligible_pairs")==n
             and prev.get("k_floor_10_percent")==int(.10*n)
             and prev.get("three_arms_all_full_k_feasible") is True
             and prev.get("saved_risk_cutoff")==CUTOFF
             and prev.get("original_q25_cutoff")==ORIGINAL_P10,
             "Original 3-arm K10 source preflight evidence drift: "+cohort)
        original=[r for r in point["results"]["cells"]
                  if r.get("work_package")=="A2"
                  and r.get("cohort")==cohort
                  and r.get("setting")==.25]
        must(len(original)==1
             and original[0].get("full_k_feasible") is True,
             "Original G3.1 point q25/K10 cell missing: "+cohort)

def check_point_against_original(new,source,original_point):
    cohort=new["cohort"]
    actual=[x for x in original_point["results"]["cells"]
            if x.get("work_package")=="A2"
            and x.get("cohort")==cohort
            and x.get("setting")==.25][0]
    for key,expected in (
        ("common_original_pairs",source["old_original_pairs"]),
        ("K_floor_10_percent",source["k_floor_10_percent"]),
        ("p10_admitted_pairs",source["p10_original_q25_admitted_pairs"]),
        ("risk_admitted_pairs",source["volatility_v0_cutoff_admitted_pairs"]),
        ("topk_overlap_p10_risk",source["top_k_overlap_p10_volatility"]),
    ):
        must(new[key]==expected,
             "New A3 point source-only count drift: "+cohort+"/"+key)
    for old_key,new_key in (
        ("baseline_mean_forward_excess_beta",
         "original_baseline_topk_mean_forward_excess_beta"),
        ("veto_mean_forward_excess_beta",
         "original_p10_q25_topk_mean_forward_excess_beta"),
        ("delta_mean_forward_excess_beta",
         "p10_minus_baseline_delta_mean"),
        ("baseline_hit_rate",
         "original_baseline_topk_hit_rate"),
        ("veto_hit_rate","original_p10_topk_hit_rate"),
        ("delta_hit_rate","p10_minus_baseline_delta_hit"),
    ):
        must(abs(actual[old_key]-new[new_key])<=1e-12,
             "Old original G3.1 published q25/K10 point changed: "+
             cohort+"/"+old_key)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ("review-repo","approved-commit",
                "source-only-report","g3-0-report","g2-freeze-approval",
                "g1-dossier","original-local-data","original-frozen-repo",
                "legacy-outputs","reconstructed-models",
                "g2-6-binding","g2-9-report","g2-10-report",
                "g2-12-report","g2-13-report","original-price-cache",
                "g3-2-numeric-quality-report","g3-2-valid-cutoff-report",
                "g3-2-three-arm-source-preflight-report",
                "g3-1-original-point-report","out"):
        parser.add_argument("--"+arg,required=True)
    parser.add_argument("--authorize-a3-retrospective-old-outcome-point-only",
                        action="store_true")
    parser.add_argument("--acknowledge-no-independent-60d-holdout",
                        action="store_true")
    parser.add_argument("--acknowledge-retrospective-price-vintage-unverified",
                        action="store_true")
    parser.add_argument("--acknowledge-no-realized-tradable-pnl",
                        action="store_true")
    parser.add_argument("--trust-original-audited-pickles",
                        action="store_true")
    args=parser.parse_args()
    if not (
        args.authorize_a3_retrospective_old_outcome_point_only
        and args.acknowledge_no_independent_60d_holdout
        and args.acknowledge_retrospective_price_vintage_unverified
        and args.acknowledge_no_realized_tradable_pnl
        and args.trust_original_audited_pickles
    ):
        parser.error("Separate explicit owner A3 original-outcome POINT ONLY access consent and all scientific caveats required")
    out=Path(args.out).expanduser()
    must(not out.exists(),"Refuse original or prior scientific report overwrite")
    commit=args.approved_commit.lower()
    verify_local_runner_code(args.review_repo,commit)
    # Original G3.1 gate independently checks the frozen historical G2,
    # G3.0 and 6 original signal/target source file SHA256 and exact
    # original 9 source/test programs bound to this immutable Git commit.
    _,original_paths=make_release_checks(args)
    # Original G3.2 source-only program checks 8 more immutable
    # source/test files. No source snapshot can silently change.
    check_code(args.review_repo,commit)
    quality=evidence(args.g3_2_numeric_quality_report,QUALITY_SHA)
    cal=evidence(args.g3_2_valid_cutoff_report,VALID_CUTOFF_SHA)
    pre=evidence(args.g3_2_three_arm_source_preflight_report,SOURCE_PREFLIGHT_SHA)
    original=evidence(args.g3_1_original_point_report,G31_ORIGINAL_POINT_SHA)
    validate_aggregate_checkpoints(pre,original,cal,quality)
    original_g26=evidence(args.g2_6_binding,G26)
    g29=evidence(args.g2_9_report,G29)
    g210=evidence(args.g2_10_report,G210)
    g212=evidence(args.g2_12_report,G212)
    g213=evidence(args.g2_13_report,G213)
    manifest=validation_source_checks(g29,g210,g212,g213,original_g26)
    prices_bound=recheck_all_historical_price_hashes(
        manifest,args.original_price_cache)
    # From here all exact original price+signal+target Pickles are
    # SHA-verified and all original reports/code/test immutably bound,
    # and new A3 old outcome access was explicitly authorized.
    import pandas as pd
    from ic_g3_1_a2_a6_join_contract import (
        source_exact_join,extract_source_arrays
    )
    price_arrays={}
    for ticker,p in prices_bound.items():
        bar=pd.read_pickle(p)
        must(isinstance(bar,pd.DataFrame) and
             {"date","close"}.issubset(bar.columns),
             "A3 original saved price schema drift")
        bar_dates=pd.to_datetime(bar["date"],utc=True,errors="coerce")
        must(not bar_dates.isna().any(),
             "A3 source price dates unparseable")
        dates=bar_dates.dt.date.tolist()
        must(len(dates)==len(set(dates)),
             "A3 original saved price daily date duplicate")
        price_arrays[ticker]=(dates,bar["close"].tolist())
        del bar
    rows=[]
    for cohort in ("V2","V3","V4"):
        signals=pd.read_pickle(original_paths[(cohort,"signals")])
        # Independently recalculate full SOURCE-ONLY preflight values
        # with unchanged cutoff, score and same signal order BEFORE
        # joining any original target label.
        source=source_counts(signals,price_arrays,cohort)
        previous=pre["cohorts"][cohort]
        for k in (
            "old_original_pairs","common_source_quality_eligible_pairs",
            "k_floor_10_percent","p10_original_q25_admitted_pairs",
            "volatility_v0_cutoff_admitted_pairs","both_vetoes_admitted_pairs",
            "top_k_overlap_baseline_p10",
            "top_k_overlap_baseline_volatility",
            "top_k_overlap_p10_volatility","three_arms_all_full_k_feasible"
        ):
            must(source[k]==previous[k],
                 "Original source-only preflight drift before A3 labels: "+
                 cohort+"/"+k)
        risk=source_risk_admission_mask(signals,price_arrays,cohort)
        # Original target bytes have passed 6-file SHA binding at
        # make_release_checks; no fit or new forward labeling.
        targets=pd.read_pickle(original_paths[(cohort,"targets")])
        joined=source_exact_join(signals,targets,cohort)
        a=extract_source_arrays(joined)
        outcome=three_arm_point_effects(
            cohort,a["prediction"],a["target"],a["original_q25_pass"],risk)
        check_point_against_original(outcome,source,original)
        rows.append(outcome)
        del signals,targets,joined,a,risk
    must(len(rows)==3 and
         {r["cohort"] for r in rows}==set(EXPECTED),
         "A3 original 3-arm complete cohort comparison did not finish")
    output={
      "schema_version":"dtrm.ic.g3.2.a3_original_3arm_point_only.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":"G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY",
      "immutable_point_science_code_commit":commit,
      "source_original_g31_six_input_report_sha256":
          "3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8",
      "source_original_g31_point_report_sha256":G31_ORIGINAL_POINT_SHA,
      "source_A3_V0_validation_only_cutoff_sha256":VALID_CUTOFF_SHA,
      "source_A3_numeric_source_quality_sha256":QUALITY_SHA,
      "source_A3_3arm_original_preflight_sha256":SOURCE_PREFLIGHT_SHA,
      "original_price_snapshot_suffix":"2026-07-05",
      "original_p10_q25":ORIGINAL_P10,
      "validated_only_volatility_daily_cutoff":CUTOFF,
      "cohorts":rows,
      "old_forward_excess_beta_targets_deserialized":True,
      "original_parity_q25_k10_rechecked":True,
      "same_common_pairs_prediction_and_K_in_all_arms":True,
      "news_id_cluster_bootstrap_completed":False,
      "ticker_cluster_bootstrap_completed":False,
      "original_price_vendor_asof_vintage_verified":False,
      "original_price_point_in_time_adjustments_verified":False,
      "independent_new_matured_holdout":False,
      "is_realized_trading_pnl":False,
      "interpretation":"DATE_RESTRICTED_POST_OUTCOME_EXPLORATORY_POINT_ONLY_NOT_STATISTICALLY_CONFIRMED",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as fp:
        json.dump(output,fp,ensure_ascii=False,indent=2)
        fp.write("\n")
    print("G3.2 A3:",output["status"])
    for r in rows:
        print(r["cohort"],"N",r["common_original_pairs"],
              "K",r["K_floor_10_percent"],
              "Δ P10-baseline",r["p10_minus_baseline_delta_mean"],
              "Δ risk-baseline",r["risk_minus_baseline_delta_mean"],
              "Δ P10-risk",r["p10_minus_risk_paired_delta_mean"],
              "hit Δ P10-risk",r["p10_minus_risk_paired_delta_hit"])
    print("Report:",out)
    print("NO confidence intervals or new independent holdout. Price vintage UNVERIFIED.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as e:
        print("G3.2 A3 POINT HALTED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(3)
