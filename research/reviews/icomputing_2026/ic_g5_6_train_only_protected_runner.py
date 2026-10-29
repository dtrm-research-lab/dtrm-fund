#!/usr/bin/env python3
"""G5.6 operator-approved ORIGINAL TRAIN-only ticker-centering reconstruction.

Never reads V2/V3/V4 cohort data; no validation/test target generation.
Trust original Pickle sources ONLY after every prior report/source hash check.
Reports aggregated training statistics and digest, not ticker means or returns.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

from ic_g5_5_private_source_metadata_gate import (
    audit_source_manifest,inspect_training_metadata,sourcefile_sha,
    ORIGINAL_G31_SOURCE_REPORT_SHA,ORIGINAL_ROWS_SHA,
)
from ic_g5_5_original_code_lineage_audit import audit as audit_frozen_code
from ic_g3_2_a3_numeric_source_quality_gate import (
    G26,G29,G210,G212,G213,validation_source_checks,evidence,
)
from ic_g3_2_a3_valid_only_cutoff import recheck_all_historical_price_hashes
from ic_g5_6_train_only_core import centers_from_train

EXPECTED_VALID=19880
EXPECTED_PRICES=174


class TrainReconstructionGate(RuntimeError):
    pass


def must(flag:bool,reason:str)->None:
    if not flag:raise TrainReconstructionGate(reason)


def code_approval(repo:Path,commit:str)->None:
    """Check exact committed reviewed code; reject working source mutations."""
    must(len(commit)==40 and all(x in "0123456789abcdef" for x in commit),
         "Immutable full reviewed commit required")
    head=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],
        check=True,capture_output=True,text=True).stdout.strip()
    must(head==commit,"Operator approved commit differs from checked-out HEAD")
    for p in ("ic_g5_6_train_only_protected_runner.py",
              "ic_g5_6_train_only_core.py",
              "ic_g5_5_private_source_metadata_gate.py",
              "ic_g5_5_original_code_lineage_audit.py"):
        local=Path(__file__).resolve().with_name(p)
        relative="research/reviews/icomputing_2026/"+p
        git_blob=subprocess.run(["git","-C",str(repo),"show",
                    commit+":"+relative],check=True,capture_output=True).stdout
        must(local.read_bytes()==git_blob,"Locally modified/unreviewed protected code: "+p)
    proof=audit_frozen_code(repo)
    must(all(proof["semantic_checks"].values()),"Original code semantic SHA/AST audit failed")


def validate_stage1_metadata_report(report:dict, root:Path, outs:Path,
                                    price_cache:Path)->dict:
    must(report.get("status")==
         "G55_ORIGINAL_LOCAL_SOURCE_HASHES_AND_TRAIN_INPUT_NAMES_PASS_NO_TARGET_VALUES"
         and report.get("private_market_values_loaded") is False
         and report.get("read_or_compute_train_ticker_means") is False
         and report.get("original_v2_v3_v4_outcome_access_authorized") is False,
         "Original G5.5 source-only report not authentic safety state")
    train=inspect_training_metadata(root,outs,price_cache)
    must(train["training_source_metadata"]==
         report.get("training_source_metadata"),
         "Original TRAIN metadata changed after G5.5 source-only preflight")
    must(train["price_cache_snapshot_named_candidates"]==EXPECTED_PRICES,
         "Expected 174 original price filenames")
    return train


def complete_source_preflight(args)->dict:
    """ALL source hashes before unpickling TRAIN rows or quoted prices."""
    repo=args.repo.expanduser()
    root=args.original_local_data.expanduser()
    outs=args.legacy_outputs.expanduser()
    cache=args.original_price_cache.expanduser()
    must(repo.is_dir() and not repo.is_symlink(),"Reviewed repo missing/unsafe")
    must(not args.out.exists(),"Never overwrite a previous original G5.6 audit")
    code_approval(repo,args.approved_code_commit)
    must(sourcefile_sha(args.g31_source_only_report)==
         ORIGINAL_G31_SOURCE_REPORT_SHA,"Original six-source G3.1 digest drift")
    g31=json.loads(args.g31_source_only_report.read_text(encoding="utf-8"))
    # We only hash original old cohort files; they are NOT deserialized here or below.
    old=audit_source_manifest(g31,root)
    must(sum(len(x) for x in old.values())==6,
         "Original six cohort source fingerprints not all bounded")

    must(len(args.g55_metadata_sha256)==64 and
         sourcefile_sha(args.g55_metadata_report)==args.g55_metadata_sha256,
         "Operator approved G5.5 metadata digest does not match")
    stage1=json.loads(args.g55_metadata_report.read_text(encoding="utf-8"))
    check=validate_stage1_metadata_report(stage1,root,outs,cache)
    must(stage1.get("g31_report_sha256")==ORIGINAL_G31_SOURCE_REPORT_SHA,
         "G55 source report lineage drift")

    def load_old_report(file,digest):
        return evidence(file,digest)
    a29=load_old_report(args.g2_9_report,G29)
    a210=load_old_report(args.g2_10_report,G210)
    a212=load_old_report(args.g2_12_report,G212)
    a213=load_old_report(args.g2_13_report,G213)
    a26=load_old_report(args.g2_6_report,G26)
    manifest=validation_source_checks(a29,a210,a212,a213,a26)
    bound=recheck_all_historical_price_hashes(manifest,cache)
    must(len(bound)==EXPECTED_PRICES and "SPY" in bound,
         "Original July 5 prices not completely fingerprinted")
    must(sourcefile_sha(root/"legacy_model_rows_2026-05-01.pkl")==
         ORIGINAL_ROWS_SHA,"Original selected model row SHA changed")

    # The original FULL-row source was not proven historically SHA-bound by
    # this chain. Do not mislabel reconstruction as archival fact.
    full=root/"legacy_pairs_enriched_2025-01-01_2026-05-01.pkl"
    full_now=sourcefile_sha(full)
    must(args.acknowledge_original_full_row_provenance_unbound,
         "Explicit acknowledgement of original full-row source gap required")
    return {"bounded_prices":bound,"full_source_digest":full_now,
            "training_metadata":check,"original_cohort_hash_only_count":6,
            "source_price_files_hash_checked_before_pickle":EXPECTED_PRICES,
            "full_row_archive_original_historical_sha_attested":False}


def reconstruct_original_train_only(args)->dict:
    must(args.authorize_train_only_numeric_reconstruction,
         "New explicit owner approval required for TRAIN-only values")
    must(args.trust_original_audited_pickles,
         "Pandas Pickle can execute code; explicit source trust required")
    must(args.acknowledge_price_vendor_vintage_unverified,
         "2026-07-05 price vendor vintage is NOT point-in-time authenticated")
    must(args.acknowledge_no_old_holdout_outcomes,
         "This code is NOT approved to load old V2/V3/V4 outcomes")
    must(args.acknowledge_original_full_row_provenance_unbound,
         "Historical full-row archive SHA not independently attested")
    proof=complete_source_preflight(args)

    # Only after every checksum and every explicit operator acknowledgement:
    import numpy as np
    import pandas as pd
    root=args.original_local_data.expanduser()
    repo=args.repo.expanduser()
    sys.path.insert(0,str(repo/"src"))
    from dtrm.legacy_model_rows import order_selected_legacy_rows
    from dtrm.exante_target import forward_excess_beta_target

    full=pd.read_pickle(root/"legacy_pairs_enriched_2025-01-01_2026-05-01.pkl")
    selected=pd.read_pickle(root/"legacy_model_rows_2026-05-01.pkl")
    required={"ticker","news_id","date_dt"}
    must(isinstance(full,pd.DataFrame) and
         isinstance(selected,pd.DataFrame) and
         required.issubset(full.columns) and (required|{"split","beta_pre"}).issubset(selected.columns),
         "Original full/model row schema missing required source values")
    fullkeys=list(zip(full["news_id"],full["ticker"]))
    selectedkeys=list(zip(selected["news_id"],selected["ticker"]))
    must(len(set(fullkeys))==len(fullkeys) and
         len(set(selectedkeys))==len(selectedkeys),
         "Original source duplicate identities")
    order=order_selected_legacy_rows(full["ticker"],full["date_dt"],fullkeys,selectedkeys)
    orig=selected.iloc[order].reset_index(drop=True)
    must(len(orig)==len(selected),"Frozen original model ordered row cardinality drift")
    for split in ("train","valid","test"):
        must(split in set(orig["split"]),"Original split membership not found")
    nvalid=int(orig["split"].eq("valid").sum())
    must(nvalid==EXPECTED_VALID,"Original 19,880 VALID count drift")
    train=orig.loc[orig["split"].eq("train"),["ticker","date_dt","beta_pre"]].copy()
    must(len(train)>0 and train.notna().all().all(),"Empty or null TRAIN rows")
    must(pd.to_datetime(train["date_dt"],utc=True,errors="coerce").notna().all(),
         "Invalid original TRAIN event date")
    must(np.isfinite(train["beta_pre"].to_numpy(dtype=np.float64)).all(),
         "Original TRAIN beta nonfinite")

    stock_tickers=set(train["ticker"].tolist())
    must(all(isinstance(t,str) and t in proof["bounded_prices"] for t in stock_tickers),
         "Missing original SHA-bound TRAIN stock")
    used_symbols={"SPY"}|stock_tickers
    # Load ONLY TRAIN-needed original price pickles after ALL 174 are SHA-bound.
    prices={}
    for ticker in sorted(used_symbols):
        frame=pd.read_pickle(proof["bounded_prices"][ticker])
        must(isinstance(frame,pd.DataFrame) and
             {"date","close"}.issubset(frame.columns),
             "Original trusted TRAIN price schema invalid")
        stamp=pd.to_datetime(frame["date"],utc=True,errors="coerce")
        close=np.asarray(frame["close"],dtype=float)
        must(len(close)>60 and stamp.notna().all() and np.isfinite(close).all()
             and (close>0).all() and not stamp.duplicated().any(),
             "Original TRAIN stock price numerical/date quality invalid")
        # Preserve original frozen implementation's date and close value types.
        prices[ticker]=list(zip(frame["date"],frame["close"]))
    sp=prices["SPY"]

    raw=[]
    for row in train.itertuples(index=False):
        value=forward_excess_beta_target(
            stock_prices=prices[row.ticker],market_prices=sp,
            beta=float(row.beta_pre),event_date=row.date_dt,
            horizon_days=60,tolerance_days=5)
        must(value is not None and math.isfinite(value),
             "Original TRAIN raw 60-day beta-excess target missing or nonfinite")
        raw.append(value)
    fitted=centers_from_train(ticker=train["ticker"].tolist(),raw_targets=raw)
    must(fitted["train_rows"]==len(train) and fitted["train_centered_float32_parity"],
         "Exact frozen TRAIN preprocessing parity mismatch")
    del raw,prices,train,full,selected,orig
    return {
        "schema_version":"dtrm.ic.g5_6.original_train_only_centers.v0",
        "status":"G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED",
        "original_source_commit":"c7502a690162459cdfb3413573e3133c42efb126",
        "approved_protected_runner_commit":args.approved_code_commit,
        "g55_original_local_source_metadata_sha256":args.g55_metadata_sha256,
        "original_historical_model_rows_sha256":ORIGINAL_ROWS_SHA,
        "original_full_rows_current_sha256":proof["full_source_digest"],
        "original_full_rows_historical_sha_bound":False,
        "original_174_price_files_sha_checked":EXPECTED_PRICES,
        "original_cohort_files_hashed_not_opened":6,
        **fitted,
        # Deliberately set the protected-reader status AFTER the numerical core.
        # G5.6 operator's original 2026-10-29 report used the core status
        # TRAIN_CENTERS_NUMERIC_PARITY_ONLY because of merge precedence.
        # Keep its original report and SHA untouched; interpret it through a
        # separate versioned readback rather than rewriting history.
        "numeric_core_status":fitted["status"],
        "status":"G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED",
        "original_heldout_v2_v3_v4_target_labels_accessed":False,
        "validation_or_test_targets_reconstructed":False,
        "original_price_provider_vintage_verified":False,
        "original_adjustment_point_in_time_verified":False,
        "historical_three_arm_or_policy_attribution_run":False,
        "no_real_trading_pnl":True,
        "scientific_use":"TRAIN_SOURCE_PARITY_ONLY_NOT_YET_INDEPENDENT_HOLDOUT_PROOF",
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    for x in ("repo","approved-code-commit","original-local-data","legacy-outputs",
              "original-price-cache","g31-source-only-report","g55-metadata-report",
              "g55-metadata-sha256","g2-6-report","g2-9-report",
              "g2-10-report","g2-12-report","g2-13-report","out"):
        parser.add_argument("--"+x,required=True,
            type=Path if x not in ("approved-code-commit","g55-metadata-sha256") else str)
    for x in ("authorize-train-only-numeric-reconstruction",
              "trust-original-audited-pickles",
              "acknowledge-price-vendor-vintage-unverified",
              "acknowledge-original-full-row-provenance-unbound",
              "acknowledge-no-old-holdout-outcomes"):
        parser.add_argument("--"+x,action="store_true")
    args=parser.parse_args()
    if not all((args.authorize_train_only_numeric_reconstruction,
                args.trust_original_audited_pickles,
                args.acknowledge_price_vendor_vintage_unverified,
                args.acknowledge_original_full_row_provenance_unbound,
                args.acknowledge_no_old_holdout_outcomes)):
        parser.error("Explicit TRAIN-only owner authorization, trusted original Pickles and all caveats required")
    args.out=args.out.expanduser()
    if args.out.exists():parser.error("Refuse overwriting original audit result")
    report=reconstruct_original_train_only(args)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    print(report["status"])
    print("TRAIN_N="+str(report["train_rows"])+" TRAIN_TICKERS="+str(report["train_tickers"]))
    print("TRAIN_FLOAT32_CENTER_PARITY=PASS")
    print("ORIGINAL_FULL_ROW_HISTORICAL_SHA=UNATTESTED")
    print("OLD_V2_V3_V4_LABEL_ACCESS=NONE")
    print("ECONOMIC_PNL=NOT_ESTIMATED")
    print("REPORT_SHA256="+sourcefile_sha(args.out))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
