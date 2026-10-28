#!/usr/bin/env python3
"""G3.2 A3: original 10k news/ticker PAIRED cluster bootstrap, scoped consent.

Previously consumed historic 60d forward-excess-beta target Pickles
are opened ONLY under new, explicit human authorization AFTER
checking exact original reports, original G2/G3.1 science source/tests
and 6 signal+target and 174 original price SHA checks.
Run all three policy arms (baseline/q25 P10/V0 risk) on the SAME
resampled original rows and K=floor(.1*N). No parameter retuning.
No raw user IDs/scores/price rows or original targets serialized.
Missing full K in any bootstrap replicate WITHHOLDS all 6 intervals
(mean/hit x 3 comparisons) for that news/ticker cluster scheme.
Quotes were collected in July 2026; point-in-time vendor price
adjustment vintages are unverified. No new holdout / tradable P&L.
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
from ic_g3_1_a2_a6_join_contract import source_exact_join,extract_source_arrays
from ic_g3_2_a3_original_3arm_source_preflight import (
    check_code,counts as source_counts,EXPECTED,CUTOFF
)
from ic_g3_2_a3_numeric_source_quality_gate import (
    G26,G29,G210,G212,G213,evidence,validation_source_checks,sha,must
)
from ic_g3_2_a3_valid_only_cutoff import recheck_all_historical_price_hashes
from ic_g3_2_a3_three_arm_point_runner import (
    validate_aggregate_checkpoints,check_point_against_original,
    verify_local_runner_code,QUALITY_SHA,VALID_CUTOFF_SHA,
    SOURCE_PREFLIGHT_SHA,G31_ORIGINAL_POINT_SHA,ORIGINAL_P10,
)
from ic_g3_2_a3_three_arm_pure_points import (
    source_risk_admission_mask,three_arm_point_effects
)
from ic_g3_2_a3_paired_cluster_bootstrap import (
    original_paired_a3_cluster_bootstrap
)

A3_PRIOR_POINT_SHA="b5b94f09d57d8bb3336ea01eb469f5ef703743a1217422be7e0f4b98484b4087"
PATH="research/reviews/icomputing_2026/"
CODE_FILES=(
    "ic_g3_2_a3_paired_bootstrap_runner.py",
    "test_ic_g3_2_a3_paired_bootstrap_runner.py",
    "ic_g3_2_a3_paired_cluster_bootstrap.py",
    "test_ic_g3_2_a3_paired_cluster_bootstrap.py",
)

def verify_new_source(repo,commit):
    must(len(commit)==40 and all(x in "0123456789abcdef" for x in commit),
         "Exact immutable 40-digit code commit required")
    folder=Path(__file__).resolve().parent
    for name in CODE_FILES:
        local=folder/name
        must(local.is_file() and not local.is_symlink(),
             "New paired source/test file missing: "+name)
        original=subprocess.run(
            ["git","-C",str(Path(repo).expanduser()),"show",commit+":"+PATH+name],
            capture_output=True,check=True).stdout
        must(hashlib.sha256(original).hexdigest()==sha(local),
             "Paired A3 new code/test Git SHA drift: "+name)

def verify_prior_point_rows(prior,actual):
    must(prior.get("status")==
         "G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY"
         and prior.get("news_id_cluster_bootstrap_completed") is False
         and prior.get("ticker_cluster_bootstrap_completed") is False
         and prior.get("original_price_vendor_asof_vintage_verified") is False
         and prior.get("original_parity_q25_k10_rechecked") is True
         and len(prior.get("cohorts",[]))==3,
         "Prior exact original A3 point report status/limits invalid")
    old=[v for v in prior["cohorts"] if v.get("cohort")==actual["cohort"]]
    must(len(old)==1,"Prior A3 original point cohort missing/duplicate")
    for key,value in actual.items():
        must(key in old[0] and old[0][key]==value,
             "Old original point effect or source metadata drift: "+
             actual["cohort"]+"/"+key)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("review-repo","approved-commit",
                "source-only-report","g3-0-report","g2-freeze-approval",
                "g1-dossier","original-local-data","original-frozen-repo",
                "legacy-outputs","reconstructed-models",
                "g2-6-binding","g2-9-report","g2-10-report",
                "g2-12-report","g2-13-report","original-price-cache",
                "g3-2-numeric-quality-report","g3-2-valid-cutoff-report",
                "g3-2-three-arm-source-preflight-report",
                "g3-1-original-point-report","g3-2-original-3arm-point-report","out"):
        p.add_argument("--"+arg,required=True)
    p.add_argument("--authorize-a3-old-outcomes-paired-news-ticker-bootstrap",
                   action="store_true")
    p.add_argument("--acknowledge-no-independent-60d-holdout",action="store_true")
    p.add_argument("--acknowledge-retrospective-price-vintage-unverified",
                   action="store_true")
    p.add_argument("--acknowledge-no-realized-tradable-pnl",action="store_true")
    p.add_argument("--trust-original-audited-pickles",action="store_true")
    a=p.parse_args()
    if not(a.authorize_a3_old_outcomes_paired_news_ticker_bootstrap
           and a.acknowledge_no_independent_60d_holdout
           and a.acknowledge_retrospective_price_vintage_unverified
           and a.acknowledge_no_realized_tradable_pnl
           and a.trust_original_audited_pickles):
        p.error("New explicit A3 original-target 10k PAIRED bootstrap scope consent required")
    output_file=Path(a.out).expanduser()
    must(not output_file.exists(),"Never overwrite prior A3 report")
    commit=a.approved_commit.lower()
    # No original Pickle access before ALL source, old target, new code
    # and independent experimental checkpoint fingerprints match.
    verify_new_source(a.review_repo,commit)
    verify_local_runner_code(a.review_repo,commit)
    check_code(a.review_repo,commit)
    _,original_inputs=make_release_checks(a)
    quality=evidence(a.g3_2_numeric_quality_report,QUALITY_SHA)
    calibration=evidence(a.g3_2_valid_cutoff_report,VALID_CUTOFF_SHA)
    preflight=evidence(a.g3_2_three_arm_source_preflight_report,
                       SOURCE_PREFLIGHT_SHA)
    old_g31=evidence(a.g3_1_original_point_report,G31_ORIGINAL_POINT_SHA)
    original_a3=evidence(a.g3_2_original_3arm_point_report,A3_PRIOR_POINT_SHA)
    validate_aggregate_checkpoints(preflight,old_g31,calibration,quality)
    g26=evidence(a.g2_6_binding,G26)
    g29=evidence(a.g2_9_report,G29)
    g210=evidence(a.g2_10_report,G210)
    g212=evidence(a.g2_12_report,G212)
    g213=evidence(a.g2_13_report,G213)
    manifest=validation_source_checks(g29,g210,g212,g213,g26)
    price_files=recheck_all_historical_price_hashes(
        manifest,a.original_price_cache)
    # Full original SHA checks completed BEFORE first trusted Pickle.
    import pandas as pd
    historic_prices={}
    for symbol,path in price_files.items():
        b=pd.read_pickle(path)
        must(isinstance(b,pd.DataFrame) and
             {"date","close"}.issubset(b.columns),
             "Original saved stock price schema drift: "+symbol)
        d=pd.to_datetime(b["date"],utc=True,errors="coerce")
        must(not d.isna().any(),"Original saved stock price invalid bar date")
        dates=d.dt.date.tolist()
        must(len(dates)==len(set(dates)),
             "Original saved stock price duplicate bar date")
        historic_prices[symbol]=(dates,b["close"].tolist())
        del b
    cells=[]
    for cohort in ("V2","V3","V4"):
        signals=pd.read_pickle(original_inputs[(cohort,"signals")])
        source=source_counts(signals,historic_prices,cohort)
        former=preflight["cohorts"][cohort]
        for key in (
            "old_original_pairs","common_source_quality_eligible_pairs",
            "k_floor_10_percent","p10_original_q25_admitted_pairs",
            "volatility_v0_cutoff_admitted_pairs","both_vetoes_admitted_pairs",
            "top_k_overlap_baseline_p10","top_k_overlap_baseline_volatility",
            "top_k_overlap_p10_volatility","three_arms_all_full_k_feasible"
        ):
            must(source[key]==former[key],
                 "Source-only preflight mutated before paired outcome: "+
                 cohort+"/"+key)
        risk=source_risk_admission_mask(signals,historic_prices,cohort)
        targets=pd.read_pickle(original_inputs[(cohort,"targets")])
        joined=source_exact_join(signals,targets,cohort)
        arrays=extract_source_arrays(joined)
        observed=three_arm_point_effects(
            cohort,arrays["prediction"],arrays["target"],
            arrays["original_q25_pass"],risk)
        check_point_against_original(observed,source,old_g31)
        verify_prior_point_rows(original_a3,observed)
        observed["paired_news_cluster_ci"]=original_paired_a3_cluster_bootstrap(
            cohort,arrays["prediction"],arrays["target"],
            arrays["original_q25_pass"],risk,
            arrays["news_id"],scheme="news_id")
        observed["paired_ticker_cluster_ci"]=original_paired_a3_cluster_bootstrap(
            cohort,arrays["prediction"],arrays["target"],
            arrays["original_q25_pass"],risk,
            arrays["ticker"],scheme="ticker")
        cells.append(observed)
        del signals,targets,joined,arrays,risk
    must(len(cells)==3 and
         {v["cohort"] for v in cells}==set(EXPECTED),
         "Incomplete original paired A3 bootstrap cohort grid")
    result={
       "schema_version":"dtrm.ic.g3.2.a3_three_arm_paired_bootstrap.v1",
       "generated_at_utc":datetime.now(timezone.utc).isoformat(),
       "status":"G3_2_A3_ORIGINAL_3ARM_PAIRED_NEWS_TICKER_10K_COMPLETED_POST_OUTCOME_EXPLORATORY",
       "immutable_paired_bootstrap_code_commit":commit,
       "sha256_original_a3_point_report":A3_PRIOR_POINT_SHA,
       "sha256_original_a3_preflight":SOURCE_PREFLIGHT_SHA,
       "sha256_original_a3_v0_cutoff":VALID_CUTOFF_SHA,
       "sha256_original_a3_numeric_quality":QUALITY_SHA,
       "sha256_original_g31_point_report":G31_ORIGINAL_POINT_SHA,
       "cohorts":cells,
       "expected_cohorts":3,
       "replicates_per_cluster_per_cohort":10000,
       "total_news_and_ticker_resamples":60000,
       "all_CIs_withheld_per_cluster_scheme_if_any_K_infeasible":True,
       "all_original_phase_ii_q25_k10_effect_parity_checked":True,
       "original_60d_forward_target_deserialized_with_new_owner_consent":True,
       "old_60day_outcomes_previously_consulted":True,
       "no_new_independent_matured_60day_holdout":True,
       "price_provider_vintage_verified":False,
       "point_in_time_corporate_actions_verified":False,
       "realized_tradable_account_pnl":False,
       "familywise_multiple_comparisons_controlled":False,
       "scientific_interpretation":"DATE_RESTRICTED_UNADJUSTED_POST_OUTCOME_EXPLORATORY_NO_PROSPECTIVE_CLAIM",
    }
    output_file.parent.mkdir(parents=True,exist_ok=True)
    with output_file.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,indent=2,ensure_ascii=False)
        stream.write("\n")
    print("G3.2 A3:",result["status"])
    for row in cells:
        nc=row["paired_news_cluster_ci"]
        tc=row["paired_ticker_cluster_ci"]
        print(row["cohort"],
              "P10-risk point",row["p10_minus_risk_paired_delta_mean"],
              "news bad",nc["infeasible_replicates"],
              "ticker bad",tc["infeasible_replicates"],
              "news CI",nc["comparison_intervals"]["p10_minus_risk"]["ci95_delta_mean"],
              "ticker CI",tc["comparison_intervals"]["p10_minus_risk"]["ci95_delta_mean"])
    print("Report:",output_file)
    print("All CIs nominal/unadjusted, old post-outcome and price-vintage unverified.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.2 A3 PAIRED BOOTSTRAP HALTED:",
              type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
