#!/usr/bin/env python3
"""G3.1 A2/A6 ORIGINAL SOURCE-ONLY READINESS — NO FINANCIAL VALUES.

Checks archived original source-commit, frozen G2.17 human approval,
G3.0 operator report SHA, and original phase-II news+ticker/date target
file names/sizes/SHA versus preexisting G2.5 inventory. Does NOT
deserialize a Pickle, read numerical targets, calculate predictions,
open FMP price caches or authorize G3.1 outcome access.

If an authentic original G2.5 SHA is missing, reports SOURCE_SHA_UNBOUND,
not a fabricated original fingerprint; never modify original G2.5.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
G2_FREEZE="3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0"
G3_0_SHA="a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a"
G2_5_SHA="ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7"
G2_6_SHA="1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
G2_16_SHA="5232f42bd84e8b9a16d32d906b638bfd9f0f4a35234fa8440bc1f708d32f2946"
HEXDIGEST=re.compile("^[0-9a-f]{64}$")
FROZEN={
 "V2":{
   "signals":"probabilistic_v2_holdout_signals_2026-06-10.pkl",
   "targets":"probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
   "expected_rows":4449,"signals_g26_key":"v2_signals",
 },
 "V3":{
   "signals":"probabilistic_v3_holdout_signals_2026-06-14.pkl",
   "targets":"probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
   "expected_rows":2827,"signals_g26_key":"v3_signals",
 },
 "V4":{
   "signals":"probabilistic_v4_holdout_signals_2026-06-06.pkl",
   "targets":"probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
   "expected_rows":40320,"signals_g26_key":"v4_signals",
 }
}

def must(ok,reason):
    if not ok: raise RuntimeError(reason)
def sha(path:Path):
    must(path.is_file() and not path.is_symlink(),"Missing or symlinked source: "+path.name)
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda:fp.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
def obj(path:Path):
    must(path.is_file() and not path.is_symlink(),"Missing/unsafe audit JSON: "+path.name)
    result=json.loads(path.read_text(encoding="utf-8"))
    must(isinstance(result,dict),"Expected object JSON: "+path.name)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-local-data",required=True)
    p.add_argument("--g2-5-inventory",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--g2-16-source-gate",required=True)
    p.add_argument("--g2-freeze-approval",required=True)
    p.add_argument("--g3-0-report",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    dest=Path(a.out).expanduser()
    if dest.exists():p.error("Never overwrite an earlier G3.1 readiness report")
    root=Path(a.original_local_data).expanduser()
    must(root.is_dir() and not root.is_symlink(),"Original scientific data root unavailable")
    report_paths={name:Path(getattr(a,name)).expanduser()
       for name in ("g2_5_inventory","g2_6_binding","g2_16_source_gate",
                    "g2_freeze_approval","g3_0_report")}
    for key,expected in (("g2_5_inventory",G2_5_SHA),("g2_6_binding",G2_6_SHA),
                         ("g2_16_source_gate",G2_16_SHA),("g3_0_report",G3_0_SHA)):
        must(sha(report_paths[key])==expected,
             "Archived report local digest mismatch: "+key)
    old5=obj(report_paths["g2_5_inventory"])
    old6=obj(report_paths["g2_6_binding"])
    synth=obj(report_paths["g2_16_source_gate"])
    freeze=obj(report_paths["g2_freeze_approval"])
    parity=obj(report_paths["g3_0_report"])
    must(old6.get("status")=="G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
         "Old original source manifest binding status changed")
    must(synth.get("status")==
         "G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING"
         and synth.get("tests_run",0)>=36 and synth.get("tests_successful") is True
         and synth.get("g3_1_financial_comparison_authorized") is False,
         "Source gate not final 36 PASS with outcomes prohibited")
    must(freeze.get("status")=="G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY"
         and freeze.get("immutable_freeze_commit")==G2_FREEZE
         and freeze.get("source_gate_report_sha256")==G2_16_SHA
         and freeze.get("human_scientific_signoff") is True
         and freeze.get("g3_1_old_outcome_access_authorized") is False,
         "Bound G2 owner attestation does NOT authorize old outcome access")
    must(parity.get("status")=="G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED"
         and parity.get("g3_1_financial_comparison_authorized") is False
         and parity.get("g2_freeze_approval_sha256")==sha(report_paths["g2_freeze_approval"]),
         "G3.0 archived source parity or G2 freeze lineage drift")
    cohort_parity=parity.get("cohorts",{})
    for cohort,n in (("V2",4449),("V3",2827)):
        row=cohort_parity.get(cohort,{})
        must(row.get("rows")==n and row.get("status")=="ROW_PARITY_PASS"
             and row.get("ranker_rows_exceeding_1e_6")==0
             and row.get("original_p10_veto_mask_disagreements")==0
             and row.get("original_p10_numeric_reference_available") is True
             and row.get("p10_numeric_parity_independent_of_boolean_veto") is True,
             "Original V2/V3 P10 numerical and ranker parity not independently PASS: "+cohort)
        must({"p10_raw","p10_calibrated"}.issubset(
             row.get("original_p10_numeric_reference",{})),
             "Original P10 raw/calibrated numerical references absent: "+cohort)
    records=old5.get("candidate_files",[])
    must(isinstance(records,list),"G2.5 original inventory lacks candidate files")
    g26=old6.get("g2_5_historic_old_cohort_input_sha256",{})
    result={
      "schema_version":"dtrm.ic.g3.1.a2_a6_original_source_only_gate.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":"G3_1_A2_A6_SOURCE_READINESS_UNDETERMINED",
      "original_code_commit":PIN,"g2_freeze_commit":G2_FREEZE,
      "source_g2_5_sha256":G2_5_SHA,
      "source_g2_6_sha256":G2_6_SHA,
      "source_g2_16_sha256":G2_16_SHA,
      "source_g3_0_sha256":G3_0_SHA,
      "g2_owner_freeze_approval_sha256":sha(report_paths["g2_freeze_approval"]),
      "cohorts":{},
      "original_expected_total_pairs":47596,
      "old_financial_targets_read":False,
      "old_financial_targets_deserialized":False,
      "original_closes_or_returns_read":False,
      "models_or_embeddings_executed":False,
      "g3_1_execution_authorized":False,
      "g3_1_outcome_access_authorized":False,
      "risk_and_inference_classification":"POST_OUTCOME_EXPLORATORY_NOT_PROSPECTIVE",
      "source_vintage_limitations_preserved":True,
    }
    all_bound=True
    for cohort,config in FROZEN.items():
        detail={"expected_rows":config["expected_rows"],"files":{},
                "join_policy":"Original PhaseII exact news_id+ticker one-to-one and exact date_dt; verify AFTER separate authorization of target deserialization."}
        for kind in ("signals","targets"):
            name=config[kind]
            path=root/name
            must(path.is_file() and not path.is_symlink(),
                 "Original local old cohort input missing: "+name)
            hits=[v for v in records if
                Path(v.get("relative_path","")).name==name and
                v.get("root_ordinal")==1]
            must(len(hits)<=1,"Ambiguous original source inventory record: "+name)
            entry=hits[0] if hits else None
            supplied=(entry or {}).get("sha256_new_local_commitment")
            verified=bool(isinstance(supplied,str)
                         and HEXDIGEST.fullmatch(supplied))
            actual_size=path.stat().st_size
            status="ORIGINAL_G2_5_MANIFEST_SHA_PASS" if verified else "ORIGINAL_G2_5_SOURCE_SHA_NOT_BOUND"
            if entry and entry.get("size_bytes")!=actual_size:
                status="ORIGINAL_G2_5_SIZE_MISMATCH"
            if verified and sha(path)!=supplied:
                status="ORIGINAL_G2_5_SHA_MISMATCH"
            if kind=="signals" and verified and g26.get(config["signals_g26_key"])!=supplied:
                status="G2_6_SIGNAL_SHA_LINEAGE_MISMATCH"
            if status!="ORIGINAL_G2_5_MANIFEST_SHA_PASS":
                all_bound=False
            detail["files"][kind]={
               "basename":name,"size_bytes":actual_size,
               "original_inventory_records":len(hits),
               "sha256_original_g2_5":supplied,
               "source_metadata_status":status
            }
        result["cohorts"][cohort]=detail
    result["status"]=(
       "G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED"
       if all_bound else
       "G3_1_A2_A6_SOURCE_SHA_OR_LINEAGE_GAPS_OUTCOMES_STILL_BLOCKED")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G3.1 A2/A6 source-only:",result["status"])
    for cohort,entry in result["cohorts"].items():
        print(cohort,"N",entry["expected_rows"],
              "signals:",entry["files"]["signals"]["source_metadata_status"],
              "targets:",entry["files"]["targets"]["source_metadata_status"])
    print("Report:",dest)
    print("No targets deserialized, no returns, no model calculations; G3.1 outcomes remain BLOCKED.")
    return 0 if all_bound else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.1 source gate HALTED:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
