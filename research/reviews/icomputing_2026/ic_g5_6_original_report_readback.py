#!/usr/bin/env python3
"""G5.6 operator report readback ONLY: immutable SHA verification, no Pickles.

Recognizes original G5.6 v0 status-field collision without changing its
historical bytes, records owner-reported TRAIN parity and provenance gaps.
No market/return/ticker-level data access. NO G5.7 old outcome authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ORIGINAL_OWNER_REPORT_SHA="ee6868bf190e4103f1951e53d4b66e34926b3f56f82974f4639b391f7bed963c"
ORIGINAL_STAGE1_SHA="a9a39f0836f490dc2c8a464db224f546883e14e34cc3b6ff3b669cf726c32e2d"
ORIGINAL_OPERATOR_COMMIT="269c8c7a5ccff5273b99bc19c23ffdcdf03afde7"
ORIGINAL_FROZEN_SCIENCE="c7502a690162459cdfb3413573e3133c42efb126"
V0_LEGACY_CORE_STATUS="TRAIN_CENTERS_NUMERIC_PARITY_ONLY"
PROTECTED_G56_STATUS="G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED"
PUBLIC_READBACK_STATUS="G56_OWNER_REPORT_SHA_VERIFIED_TRAIN_PARITY_FULL_ROW_ORIGIN_UNATTESTED"


class ReportReadbackError(ValueError):
    pass


def _require(ok,reason):
    if not ok:raise ReportReadbackError(reason)


def _digest(v,label):
    _require(isinstance(v,str) and len(v)==64 and
             all(x in "0123456789abcdef" for x in v),label+" invalid SHA256")


def interpret(report:dict, owner_sha:str=ORIGINAL_OWNER_REPORT_SHA)->dict:
    """Validate all provenance and scientific no-outcome gates with no raw data."""
    _require(isinstance(report,dict),"G5.6 report not an object")
    status=report.get("status")
    _require(status in (V0_LEGACY_CORE_STATUS,PROTECTED_G56_STATUS),
             "G5.6 status not recognized")
    _require(report.get("schema_version")=="dtrm.ic.g5_6.original_train_only_centers.v0",
             "G5.6 schema changed")
    _require(report.get("approved_protected_runner_commit")==ORIGINAL_OPERATOR_COMMIT
             and report.get("original_source_commit")==ORIGINAL_FROZEN_SCIENCE,
             "Original code commit identity drift")
    _require(report.get("g55_original_local_source_metadata_sha256")==ORIGINAL_STAGE1_SHA,
             "G5.5 source report lineage drift")
    _require(report.get("train_rows")==75828 and report.get("train_tickers")==171,
             "Original TRAIN observation/ticker cardinality drift")
    _require(report.get("original_174_price_files_sha_checked")==174 and
             report.get("original_cohort_files_hashed_not_opened")==6,
             "Original SHA-bound source coverage changed")
    for key,expected in (
       ("train_centered_float32_parity",True),
       ("original_full_rows_historical_sha_bound",False),
       ("original_heldout_v2_v3_v4_target_labels_accessed",False),
       ("validation_or_test_targets_reconstructed",False),
       ("validation_or_test_labels_consumed",False),
       ("v2_v3_v4_targets_consumed",False),
       ("original_price_provider_vintage_verified",False),
       ("original_adjustment_point_in_time_verified",False),
       ("economic_returns_or_trading_pnl_inferred",False),
       ("historical_three_arm_or_policy_attribution_run",False),
       ("no_real_trading_pnl",True),
    ):
        _require(report.get(key) is expected,"G5.6 boolean source/interpretation drift: "+key)
    _require(report.get("scientific_use")==
       "TRAIN_SOURCE_PARITY_ONLY_NOT_YET_INDEPENDENT_HOLDOUT_PROOF",
       "Scientific scope changed")
    for key in ("train_ticker_mean_float32_mapping_sha256",
                "original_train_centered_bytes_sha256",
                "original_full_rows_current_sha256",
                "original_historical_model_rows_sha256"):
        _digest(report.get(key),key)
    _require(report["original_historical_model_rows_sha256"]==
       "3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724",
       "Original model rows SHA drift")
    lower=report.get("clip_lower")
    upper=report.get("clip_upper")
    _require(type(lower) in (int,float) and type(upper) in (int,float)
             and math.isfinite(lower) and math.isfinite(upper) and lower<upper,
             "Invalid recovered TRAIN-only clipping quantiles")
    if status==V0_LEGACY_CORE_STATUS:
        _require("numeric_core_status" not in report,
                 "First-run legacy status must not contain normalized status")
    else:
        _require(report.get("numeric_core_status")==V0_LEGACY_CORE_STATUS,
                 "Corrected protected status missing preserved numeric core status")
    return {
        "schema_version":"dtrm.ic.g5_6.owner_report_readback.v0",
        "status":PUBLIC_READBACK_STATUS,
        "original_owner_g56_report_sha256":owner_sha,
        "original_owner_g56_observed_status":status,
        "protected_operator_status_normalized_for_interpretation":PROTECTED_G56_STATUS,
        "legacy_status_field_collision_present":status==V0_LEGACY_CORE_STATUS,
        "original_owner_code_commit":ORIGINAL_OPERATOR_COMMIT,
        "original_science_commit":ORIGINAL_FROZEN_SCIENCE,
        "g55_source_report_sha256":ORIGINAL_STAGE1_SHA,
        "train_rows":75828,
        "train_tickers":171,
        "train_centered_float32_parity":True,
        "original_train_ticker_center_map_sha256":
            report["train_ticker_mean_float32_mapping_sha256"],
        "old_v2_v3_v4_heldout_targets_read":False,
        "original_full_row_archival_identity_proven":False,
        "original_price_acquisition_vintage_proven":False,
        "original_holdout_target_transform_compatibility_proven":False,
        "old_outcome_access_authorized_by_readback":False,
        "portfolio_pnl_calculated":False,
        "interpretation":"OWNER_PROVIDED_ORIGINAL_G56_REPORT_READBACK_NOT_G57_HISTORICAL_ATTRIBUTION",
    }


def file_readback(path:Path, expected_sha:str=ORIGINAL_OWNER_REPORT_SHA)->dict:
    path=path.expanduser()
    _digest(expected_sha,"expected report")
    _require(path.is_file() and not path.is_symlink(),"Missing/unsafe original report")
    _require(0<path.stat().st_size<50000,"G5.6 report size unexpected")
    raw=path.read_bytes()
    actual=hashlib.sha256(raw).hexdigest()
    _require(actual==expected_sha,"Original first owner report SHA mismatch; refuse substitution")
    try:record=json.loads(raw)
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise ReportReadbackError("Original G5.6 JSON malformed") from exc
    return interpret(record,actual)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--report",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    out=args.out.expanduser()
    _require(not out.exists(),"Refuse overwrite of owner evidence/readback")
    check=file_readback(args.report)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(check,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(check["status"])
    print("ORIGINAL_G56_SHA256="+check["original_owner_g56_report_sha256"])
    print("TRAIN_N="+str(check["train_rows"])+" TRAIN_TICKERS="+str(check["train_tickers"]))
    print("FLOAT32_PARITY=PASS")
    print("LEGACY_STATUS_COLLISION_RECORDED="+str(check["legacy_status_field_collision_present"]))
    print("ORIGINAL_FULL_ROW_ARCHIVE_PROVEN=NO")
    print("V2_V3_V4_OLD_LABEL_ACCESS=NONE")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
