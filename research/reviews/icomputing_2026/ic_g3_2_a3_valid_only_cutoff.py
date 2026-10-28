#!/usr/bin/env python3
"""G3.2 A3 — frozen V0 VALID-only volatility veto cutoff; NO old outcomes.

After numeric 66,476-pair source-only quality PASS, this consented
VALIDATION-ONLY step recomputes P10-calibrated old q25 admissions on the
original 19,880 V0 VALID rows and calibrates the conventional
trailing-volatility veto to the identical inverse-news weighted
admission on the SAME original source-common eligible rows.

Original 2026-07-05 price-source Pickles are SHA-verified before any
deserialization. Historical saved quote vintage and corporate action
adjustments remain UNKNOWN (retrospective only). No V2/V3/V4 signals,
targets, predictions, returns, bootstrap or performance compared.
No per-row predictions, risk scores, prices, IDs or ticker outputs.
This cannot authorize an A3 old-outcome comparison.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime,timezone

from ic_g3_2_a3_numeric_source_quality_gate import (
    evidence,validation_source_checks,sha,canon, must,
    G26,G29,G210,G212,G213,V0_SHA,N_VALID
)

CORE_COMMIT="0c5e433f10ce742bc129b666dfc4551f4b2fd21b"
G3_2_QUALITY_SHA="91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a"
ORIGINAL_Q25=-0.16665692627429962
OFFSET=-0.06494169682264328
REL="research/reviews/icomputing_2026/"
PINNED_FILES=(
    "ic_g3_2_a3_valid_only_cutoff.py",
    "test_ic_g3_2_a3_valid_only_cutoff.py",
    "ic_g3_2_a3_numeric_source_quality_gate.py",
    "test_ic_g3_2_a3_numeric_source_quality_gate.py",
    "ic_g3_1_a2_validation_only_source.py",
    "test_ic_g3_1_a2_validation_only_source.py",
    "ic_g2_g3_exploratory_core.py",
    "test_ic_g2_g3_exploratory_core.py",
)

def reviewed_commit_check(repo,commit):
    must(len(commit)==40 and all(x in "0123456789abcdef" for x in commit),
         "Need full immutable Git SHA")
    repo=Path(repo).expanduser()
    must(repo.is_dir() and not repo.is_symlink(),
         "Audited review Git directory not available")
    here=Path(__file__).resolve().parent
    for name in PINNED_FILES:
        path=here/name
        must(path.is_file() and not path.is_symlink(),
             "Required pinned source/test missing: "+name)
        blob=subprocess.run(
            ["git","-C",str(repo),"show",commit+":"+REL+name],
            capture_output=True,check=True).stdout
        must(hashlib.sha256(blob).hexdigest()==sha(path),
             "Unreviewed local code/test version: "+name)

def recheck_all_historical_price_hashes(manifest,price_cache):
    """Return symbols->path; ALL original source bytes checked before Pickles."""
    cache=Path(price_cache).expanduser()
    must(cache.is_dir() and not cache.is_symlink(),
         "No original trusted price archive directory")
    result={}
    for item in manifest:
        filename=item.get("filename","")
        must(isinstance(filename,str) and filename.endswith("_2026-07-05.pkl")
             and "/" not in filename and "\\" not in filename,
             "Unexpected original price source file name")
        symbol=canon(filename.split("_",1)[0])
        file=cache/filename
        must(symbol not in result and file.stat().st_size==item.get("bytes")
             and sha(file)==item.get("sha256_new_local_commitment"),
             "Original July-5 price cache SHA or size drift: "+symbol)
        result[symbol]=file
    must(len(result)==174 and "SPY" in result,
         "Expected 174 original stocks/SPY source SHA fingerprints")
    return result

def same_order_valid_and_calibrated_p10(row_news,rebuilt_news,p10_raw,quantiles):
    """Exact original V0 VALID order alignment and frozen q25 mask."""
    import numpy as np
    from ic_g2_g3_exploratory_core import (
        original_validation_p10_thresholds,Q25_FROZEN,P10_OFFSET
    )
    source=np.asarray(row_news,dtype=object)
    replay=np.asarray(rebuilt_news,dtype=object)
    raw=np.asarray(p10_raw,dtype=np.float64)
    must(len(source)==N_VALID and len(replay)==N_VALID
         and len(raw)==N_VALID
         and np.array_equal(source,replay),
         "Original P10 VALID rows do not match model-row order; no silent join")
    must(np.isfinite(raw).all() and
         Q25_FROZEN==ORIGINAL_Q25 and P10_OFFSET==OFFSET,
         "Nonfinite original scores or P10 constants changed")
    expected=original_validation_p10_thresholds(raw,replay)
    must(all(abs(float(expected[str(q)])-
                 float(quantiles[str(q)]))<1e-12
             for q in (.15,.25,.35)),
         "Original G3.1 validation cutoff replay drift")
    must(abs(expected[str(.25)]-ORIGINAL_Q25)<=1e-12,
         "Original q25 fails exact frozen validation reproduction")
    calibrated=raw+OFFSET
    return calibrated>=ORIGINAL_Q25

def matched_threshold(vol,news,original_mask):
    """Frozen pure method, all V0 validation observations eligible."""
    import numpy as np
    from ic_g2_g3_exploratory_core import (
       validation_only_volatility_cutoff, legacy_news_weights
    )
    risk=np.asarray(vol,dtype=np.float64)
    admitted=np.asarray(original_mask,dtype=bool)
    must(risk.shape==(N_VALID,) and
         np.isfinite(risk).all() and np.all(risk>=0)
         and admitted.shape==(N_VALID,),
         "A3 19880 original VALID numeric source completeness drift")
    result=validation_only_volatility_cutoff(risk,admitted,news)
    must(result["common_validation_pairs"]==N_VALID and
         result["vintage_status"]=="UNVERIFIED_LATER_SNAPSHOT",
         "Original full validation common-sample or vintage contract drift")
    weights=legacy_news_weights(news)
    mask=(risk<=result["cutoff"])
    expected=float(np.average(mask,weights=weights))
    must(abs(expected-result["volatility_weighted_admission"])<1e-12,
         "Volatility admission source tie-count difference unaccounted")
    return result,mask

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ("review-repo","code-commit","original-price-cache",
                 "original-local-data","original-frozen-repo",
                 "g1-dossier","legacy-outputs","reconstructed-models",
                 "g2-6-binding","g2-9-report","g2-10-report","g2-12-report",
                 "g2-13-report","g3-2-numeric-quality-report","out"):
        ap.add_argument("--"+flag,required=True)
    ap.add_argument("--authorize-a3-validation-only-volatility-calibration",
                    action="store_true")
    ap.add_argument("--trust-original-audited-pickles",action="store_true")
    ap.add_argument("--acknowledge-price-provider-vintage-unverified",
                    action="store_true")
    a=ap.parse_args()
    if not(a.authorize_a3_validation_only_volatility_calibration
           and a.trust_original_audited_pickles
           and a.acknowledge_price_provider_vintage_unverified):
        ap.error("New explicit authorization for VALID ONLY price/P10 source replay REQUIRED")
    dest=Path(a.out).expanduser()
    must(not dest.exists(),"Refuse original A3 report overwrite")
    reviewed_commit_check(a.review_repo,a.code_commit.lower())
    r29=evidence(a.g2_9_report,G29)
    r210=evidence(a.g2_10_report,G210)
    r212=evidence(a.g2_12_report,G212)
    r213=evidence(a.g2_13_report,G213)
    r26=evidence(a.g2_6_binding,G26)
    quality=evidence(a.g3_2_numeric_quality_report,G3_2_QUALITY_SHA)
    manifest=validation_source_checks(r29,r210,r212,r213,r26)
    must(quality.get("status")==
         "G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED"
         and quality.get("validation_common_quality_eligible_pairs")==N_VALID
         and quality.get("old_common_quality_eligible_pairs")==47596
         and quality.get("price_files_sha_checked_before_pickle")==174
         and quality.get("original_provider_vintage_verified") is False
         and quality.get("price_adjustments_point_in_time_verified") is False
         and quality.get("forward_outcome_labels_targets_or_returns_accessed") is False,
         "Original G3.2 numeric-quality report source/known vintage does not PASS")
    prices=recheck_all_historical_price_hashes(
        manifest,a.original_price_cache)
    local=Path(a.original_local_data).expanduser()
    must(local.is_dir() and not local.is_symlink(),
         "Original local research data dir missing or symlink")
    orig_model_rows=local/"legacy_model_rows_2026-05-01.pkl"
    must(sha(orig_model_rows)==V0_SHA,
         "Original 19,880 VALID model-row SHA changed")
    # All price source/validation source report SHAs have passed
    # BEFORE a single trusted original Pandas Pickle is opened.
    import pandas as pd
    from ic_g2_g3_exploratory_core import trailing_volatility_60
    from ic_g3_1_a2_validation_only_source import reconstruct_valid_p10_only
    quotes={}
    for symbol,file in prices.items():
        df=pd.read_pickle(file)
        must(isinstance(df,pd.DataFrame) and
             {"date","close"}.issubset(df.columns),
             "Original archived price data schema drift")
        dat=pd.to_datetime(df["date"],utc=True,errors="coerce")
        must(not dat.isna().any(),"Original price bar date invalid")
        days=dat.dt.date.tolist()
        must(len(days)==len(set(days)),"Original bar dates duplicated")
        quotes[symbol]=(days,df["close"].tolist())
        del df
    original=pd.read_pickle(orig_model_rows)
    must(isinstance(original,pd.DataFrame) and
         {"split","news_id","ticker","date_dt"}.issubset(original.columns),
         "Original V0 VALID model-row schema drift")
    rows=original.loc[original["split"].eq("valid"),
        ["news_id","ticker","date_dt"]].copy()
    must(len(rows)==N_VALID and
         not rows.duplicated(["news_id","ticker"]).any(),
         "Original model row uniqueness / V0 VALID count drift")
    event=pd.to_datetime(rows["date_dt"],utc=True,errors="coerce")
    must(not event.isna().any(),"Original V0 VALID UTC dates invalid")
    ids=rows["news_id"].to_numpy()
    raw,model_news,proof=reconstruct_valid_p10_only(
        frozen_root=a.original_frozen_repo,
        local_data=a.original_local_data,
        old_outputs=a.legacy_outputs,
        reconstructed_models=a.reconstructed_models,
        g1_dossier_path=a.g1_dossier)
    p10_admitted=same_order_valid_and_calibrated_p10(
        ids,model_news,raw,proof["thresholds_validation_only"])
    memo={}
    risks=[]
    for symbol,day in zip(rows["ticker"].tolist(),event.dt.date.tolist()):
        key=(canon(symbol),day)
        if key not in memo:
            must(key[0] in quotes,"V0 historic source stock ticker missing")
            risk,reason=trailing_volatility_60(*quotes[key[0]],day)
            must(reason=="OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED"
                 and risk is not None,
                 "V0 SOURCE QUALITY no longer 19880/19880 eligible: "+reason)
            memo[key]=risk
        risks.append(memo[key])
    # No old V2/V3/V4 outcomes, signals or targets are opened.
    result,mask=matched_threshold(risks,ids,p10_admitted)
    count_p10=int(p10_admitted.sum())
    count_vol=int(mask.sum())
    output={
        "schema_version":"dtrm.ic.g3.2.a3_v0_valid_only_cutoff.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":"G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED",
        "immutable_calibration_code_commit":a.code_commit.lower(),
        "immutable_historical_source_commit":"c7502a690162459cdfb3413573e3133c42efb126",
        "original_g3_2_numeric_quality_report_sha256":G3_2_QUALITY_SHA,
        "original_source_report_sha256":{
            "g2_6":G26,"g2_9":G29,"g2_10":G210,
            "g2_12":G212,"g2_13":G213},
        "original_validation_source_check":{
            "pairs":N_VALID,
            "price_files_sha256_verified":174,
            "numeric_complete_case_pairs":N_VALID,
            "source_p10_q25_frozen":ORIGINAL_Q25,
            "source_p10_calibration_offset":OFFSET,
            "original_validation_p10_source_replay":proof,
        },
        "original_p10_admitted_unweighted_pairs":count_p10,
        "risk_admitted_unweighted_pairs":count_vol,
        "original_p10_admitted_weighted_fraction":
            result["original_p10_weighted_admission"],
        "volatility_admitted_weighted_fraction":
            result["volatility_weighted_admission"],
        "weighted_admission_discrepancy_due_to_ties":
            result["volatility_weighted_admission"]-
            result["original_p10_weighted_admission"],
        "retrospective_stock_volatility_cutoff_daily_std_ddof1":
            result["cutoff"],
        "risk_threshold_uses_validation_only":True,
        "original_v2_v3_v4_signals_opened":False,
        "old_forward_targets_opened":False,
        "v2_v3_v4_model_outcome_comparisons_executed":False,
        "any_bootstrap_executed":False,
        "volatility_values_or_original_row_ids_serialized":False,
        "original_price_vendor_acquisition_vintage_verified":False,
        "original_price_point_in_time_adjustments_verified":False,
        "no_new_independent_60day_holdout":True,
        "inference_scope":"RETROSPECTIVE_VALIDATION_ONLY_PRICE_VINTAGE_UNVERIFIED",
        "a3_old_outcome_access_authorized":False,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as fp:
        json.dump(output,fp,ensure_ascii=False,indent=2)
        fp.write("\n")
    print("G3.2 A3 VALID-ONLY:",output["status"])
    print("Original VALID rows:",N_VALID,"original P10 q25:",ORIGINAL_Q25)
    print("P10 weighted admission:",result["original_p10_weighted_admission"],
          "number:",count_p10)
    print("Matched volatility cutoff (daily std ddof=1):",result["cutoff"])
    print("Volatility weighted admission:",result["volatility_weighted_admission"],
          "number:",count_vol,"tie discrepancy:",
          output["weighted_admission_discrepancy_due_to_ties"])
    print("Original historical outcomes not accessed; no bootstrap.")
    print("Provider price vintage and adjustments: UNVERIFIED.")
    print("Report:",dest)
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.2 A3 VALID-ONLY HALTED:",
              type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
