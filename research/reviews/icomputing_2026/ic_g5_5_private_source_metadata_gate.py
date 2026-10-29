#!/usr/bin/env python3
"""Original TRAIN-source availability + six old cohort SHA checks (METADATA ONLY).

This script NEVER imports pandas, unpickles anything, executes a model, reads
financial row values, or authorizes old outcome inspection. SHA256 reads bytes.
Report omits absolute local paths. Avoid public release of private manifests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ORIGINAL_G31_SOURCE_REPORT_SHA="3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8"
ORIGINAL_ROWS_SHA="3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724"
EXPECTED={"V2":4449,"V3":2827,"V4":40320}
TRAIN_FILES=("legacy_model_rows_2026-05-01.pkl",
             "legacy_pairs_enriched_2025-01-01_2026-05-01.pkl")
OUTPUT_FILES=("news_2025-01-01_2026-05-01.pkl",
              "news_emb_2025-01-01_2026-05-01.dat",
              "news_emb_shape_2025-01-01_2026-05-01.pkl",
              "news_emb_index_2025-01-01_2026-05-01.pkl")


class SourceGateError(ValueError):
    pass


def sourcefile_sha(path:Path)->str:
    if not path.is_file() or path.is_symlink():
        raise SourceGateError("Missing/unsafe source: "+path.name)
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def _is_regular(path:Path)->bool:
    return path.is_file() and not path.is_symlink()


def audit_source_manifest(source_report:dict,root:Path)->dict:
    """Checks original immutable six-file bound report against local *bytes*."""
    if (not isinstance(source_report,dict) or
        source_report.get("status")!="G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED"
        or source_report.get("original_expected_total_pairs")!=47596
        or source_report.get("g3_1_outcome_access_authorized") is not False
        or source_report.get("old_financial_targets_deserialized") is not False):
        raise SourceGateError("Unapproved or incorrect source-only G3.1 report")
    if not root.is_dir() or root.is_symlink():
        raise SourceGateError("Original cohort root missing or unsafe")
    verified={}
    for cohort,n in EXPECTED.items():
        c=source_report.get("cohorts",{}).get(cohort,{})
        if c.get("expected_rows")!=n:
            raise SourceGateError("Original cohort cardinality drift: "+cohort)
        verified[cohort]={}
        for role in ("signals","targets"):
            x=c.get("files",{}).get(role,{})
            basename=x.get("basename")
            digest=x.get("sha256_original_g2_5")
            if (x.get("source_metadata_status")!="ORIGINAL_G2_5_MANIFEST_SHA_PASS"
                or not isinstance(basename,str) or basename!=Path(basename).name
                or not isinstance(digest,str) or len(digest)!=64):
                raise SourceGateError("Unbound original source: "+cohort+"/"+role)
            path=root/basename
            if sourcefile_sha(path)!=digest or path.stat().st_size!=x.get("size_bytes"):
                raise SourceGateError("Original source SHA/size drift: "+cohort+"/"+role)
            verified[cohort][role]={"file":basename,"source_sha256":digest,
                                    "bytes":path.stat().st_size,"lineage":"EXACT_G2_5_SHA_PASS"}
    return verified


def inspect_training_metadata(original_local_data:Path,outputs:Path,
                               price_cache:Path)->dict:
    """Training-file existence and exact original model-rows HASH, NO values."""
    if not original_local_data.is_dir() or original_local_data.is_symlink():
        raise SourceGateError("Original local train root missing/unsafe")
    if not outputs.is_dir() or outputs.is_symlink():
        raise SourceGateError("Original notebook Outputs missing/unsafe")
    train_record={}
    for name in TRAIN_FILES:
        p=original_local_data/name
        if not _is_regular(p):
            raise SourceGateError("Missing/unsafe original train input: "+name)
        if name==TRAIN_FILES[0]:
            digest=sourcefile_sha(p)
            if digest!=ORIGINAL_ROWS_SHA:
                raise SourceGateError("Original train model rows SHA drift")
            train_record[name]={"exists":True,"sha256":digest,"status":"ORIGINAL_ROWS_HASH_PASS"}
        else:
            train_record[name]={"exists":True,"bytes":p.stat().st_size,
                                "status":"EXISTS_BUT_HASH_UNBOUND_BY_THIS_GATE"}
    for name in OUTPUT_FILES:
        p=outputs/name
        if not _is_regular(p):
            raise SourceGateError("Missing/unsafe frozen train input: "+name)
        train_record[name]={"exists":True,"bytes":p.stat().st_size,
                            "status":"EXISTS_BUT_HASH_UNBOUND_BY_THIS_GATE"}
    if not price_cache.is_dir() or price_cache.is_symlink():
        raise SourceGateError("Original price directory missing/unsafe")
    candidates=[p for p in price_cache.glob("*_2026-07-05.pkl") if _is_regular(p)]
    return {
        "training_source_metadata":train_record,
        "price_cache_snapshot_named_candidates":len(candidates),
        "price_source_status":"NAMES_ONLY_NO_ACQUISITION_VINTAGE_OR_CORPORATE_ACTIONS_VERIFIED",
        "original_train_ticker_means_read":False,
        "original_clipping_quantiles_read":False,
        "raw_gross_stock_returns_read":False,
        "heldout_target_file_values_read":False,
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    for a in ("source-only-report","original-local-data","legacy-outputs",
              "original-price-cache","out"):
        parser.add_argument("--"+a,required=True)
    args=parser.parse_args()
    output=Path(args.out).expanduser()
    if output.exists():parser.error("No overwrite of original source audits")
    report_path=Path(args.source_only_report).expanduser()
    if sourcefile_sha(report_path)!=ORIGINAL_G31_SOURCE_REPORT_SHA:
        raise SourceGateError("Original G3.1 source-only report SHA not authenticated")
    info=json.loads(report_path.read_text(encoding="utf-8"))
    cohort_files=audit_source_manifest(info,Path(args.original_local_data).expanduser())
    training=inspect_training_metadata(Path(args.original_local_data).expanduser(),
                Path(args.legacy_outputs).expanduser(),
                Path(args.original_price_cache).expanduser())
    payload={
        "status":"G55_ORIGINAL_LOCAL_SOURCE_HASHES_AND_TRAIN_INPUT_NAMES_PASS_NO_TARGET_VALUES",
        "g31_report_sha256":ORIGINAL_G31_SOURCE_REPORT_SHA,
        "original_cohort_files":cohort_files,
        **training,
        "private_market_values_loaded":False,
        "read_or_compute_train_ticker_means":False,
        "original_v2_v3_v4_outcome_access_authorized":False,
        "economic_utility_results":"NOT_ESTIMABLE_FROM_METADATA_ONLY",
        "next_gate":"RECONSTRUCT_TRAIN_ONLY_CENTERS_AFTER_SEPARATE_SOURCE_AND_OPERATOR_APPROVAL"
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(payload["status"])
    print("COHORTS_SHA_VERIFIED="+str(len(cohort_files))+" FILES=6")
    print("ORIGINAL_TRAIN_ROWS_SHA=PASS")
    print("PRIVATE_FINANCIAL_VALUE_ACCESS=NONE")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
