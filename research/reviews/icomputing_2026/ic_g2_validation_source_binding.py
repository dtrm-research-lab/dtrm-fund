#!/usr/bin/env python3
"""G2.6 — bind frozen V0 P10 validation replay to G2.5 metadata only.

Reads: G1.2k seal JSON, G1.2 preflight+rebuild JSON, G2.5 source
inventory JSON, pinned historical .py *source code* and git HEAD.
Does not open Pickles, .npy, market prices, trading outcomes, news,
XGBoost booster binaries, or calculate validation/test predictions.
Does not authorize G3 or freeze the secondary analysis plan.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
G1_SEAL="7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac"
V2_THRESH="-0.16665692627429962"
BASE="research/experiments/run_exante_baseline_v0.py"
QUANT="research/experiments/run_probabilistic_xgb_v0.py"
NAMES={
  "v2_threshold":"probabilistic_v2_frozen_p10_threshold.pkl",
  "v2_features":"probabilistic_v2_holdout_features_2026-06-10.npy",
  "v2_signals":"probabilistic_v2_holdout_signals_2026-06-10.pkl",
  "v3_features":"probabilistic_v3_holdout_features_2026-06-14.npy",
  "v3_signals":"probabilistic_v3_holdout_signals_2026-06-14.pkl",
  "v4_signals":"probabilistic_v4_holdout_signals_2026-06-06.pkl",
  "v1_features":"probabilistic_v1_holdout_features_2026-06-06.npy",
  "v1_signals":"probabilistic_v1_holdout_signals_2026-06-06.pkl",
}
CHECKS={
 "v0_quantile_weighted_quantile_defined":"def weighted_quantile(",
 "v0_quantile_sort_values":"np.argsort(values)",
 "v0_quantile_cumulative_weights":"np.cumsum(weights)",
 "v0_quantile_first_cumulative_hit":"side=\"left\"",
 "v0_legacy_news_weights":"legacy_news_weights(",
 "g1_replay_valid_predictions":"valid_p10_raw = quant.predict_at_iteration(",
 "g1_replay_validation_q25":"weights2[\"valid\"], 0.25",
 "g1_replay_weights_explicit":"weights2[\"valid\"]",
 "g1_replay_valid_only_calibration":"targets2[\"valid\"]-valid_p10_raw",
}

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def load(path:Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Missing/unsafe report: "+path.name)
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen-repo",required=True)
    p.add_argument("--g1-sealed",required=True)
    p.add_argument("--g1-preflight",required=True)
    p.add_argument("--g1-rebuild",required=True)
    p.add_argument("--g1-reconstruction-code",required=True)
    p.add_argument("--g2-inventory",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out).expanduser()
    if out.exists():p.error("Refusing overwrite of G2.6 evidence")
    frozen=Path(args.frozen_repo).expanduser()
    reports={n:Path(getattr(args,n)).expanduser() for n in (
       "g1_sealed","g1_preflight","g1_rebuild","g2_inventory")}
    g1=load(reports["g1_sealed"])
    pf=load(reports["g1_preflight"])
    rebuild=load(reports["g1_rebuild"])
    g2=load(reports["g2_inventory"])
    if sha(reports["g1_sealed"])!=G1_SEAL:
        raise RuntimeError("Historical G1.2k dossier changed since seal")
    if g1.get("status")!="HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN":
        raise RuntimeError("G1.2k historical source seal not PASS")
    if g1.get("source_commit")!=PIN:
        raise RuntimeError("Original historical source commit mismatch")
    if pf.get("preflight",{}).get("historical_commit_verified") is not True or pf.get("preflight",{}).get("can_begin_historical_reconstruction") is not True:
        raise RuntimeError("Original historical preflight did not PASS")
    rec=rebuild.get("reconstruction",{})
    if rebuild.get("frozen_source_commit")!=PIN or rec.get("status")!="HISTORICAL_AGGREGATE_PARITY_ONLY":
        raise RuntimeError("Historical model numerical reconstruction not pinned")
    checks=rec.get("checks",{})
    if len(checks)!=12 or not all(v is True for v in checks.values()):
        raise RuntimeError("Original 12/12 model reconstruction numeric checks not PASS")
    orig=rec.get("observed",{})
    if orig.get("p10_best_iteration")!=18 or abs(float(orig.get("relative_veto_threshold",1.0))-float(V2_THRESH))>1e-6:
        raise RuntimeError("Historic q25 validation cutoff/iteration not reproduced")
    if abs(float(orig.get("p10_calibration_offset",1.0))+0.06494169682264328)>1e-6:
        raise RuntimeError("Historic P10 calibration offset mismatch")
    if g2.get("schema_version")!="dtrm.ic.g2.historical_analysis_input_inventory.v1" or g2.get("status")!="G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3":
        raise RuntimeError("G2.5 scan not in expected metadata-only state")
    files=g2.get("candidate_files",[])
    if not isinstance(files,list):
        raise RuntimeError("G2.5 candidate records invalid")
    hashes={}
    for key,basename in NAMES.items():
        matches=[entry for entry in files if Path(entry.get("relative_path","")).name==basename and entry.get("root_ordinal")==1]
        if len(matches)!=1 or matches[0].get("hash_status")!="SHA256_STREAMED_WITHOUT_DESERIALIZATION":
            raise RuntimeError("Missing or non-uniquely SHA-recorded original cohort artifact: "+basename)
        hs=matches[0].get("sha256_new_local_commitment")
        if not isinstance(hs,str) or len(hs)!=64:
            raise RuntimeError("Invalid G2.5 SHA256 reference for "+basename)
        hashes[key]=hs
    # Source files are code, never scientific datasets. Pin exact original
    # commit and guard against tracked worktree edits.
    git=subprocess.run(["git","-C",str(frozen),"rev-parse","HEAD"],capture_output=True,text=True,check=True)
    if git.stdout.strip()!=PIN:
        raise RuntimeError("Frozen source git HEAD diverges from original V0")
    dirty=subprocess.run(["git","-C",str(frozen),"status","--porcelain","--untracked-files=no"],capture_output=True,text=True,check=True)
    if dirty.stdout.strip():
        raise RuntimeError("Original frozen tracked source modified")
    origcode={}
    for name in (BASE,QUANT):
        source=frozen/name
        if not source.is_file() or source.is_symlink():
            raise RuntimeError("Original frozen source .py unavailable: "+name)
        origcode[name]={"sha256_source_code":sha(source)}
    reconpath=Path(args.g1_reconstruction_code).expanduser()
    if not reconpath.is_file():
        raise RuntimeError("Original G1.2 reconstruction source absent")
    oldr=reconpath.read_text(encoding="utf-8")
    oldq=(frozen/QUANT).read_text(encoding="utf-8")
    text_checks={}
    for key,token in CHECKS.items():
        text_checks[key]=token in (oldq if key.startswith("v0_") else oldr)
    ready=bool(all(text_checks.values()) and
               len(g1.get("reconstructed_unapproved_model_sha256",{}))==4)
    state=("G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED"
           if ready else "G2_6_A2_ORIGINAL_VALIDATION_PROCEDURE_NEEDS_SOURCE_REVIEW")
    result={
      "schema_version":"dtrm.ic.g2.validation_source_readiness.v1",
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "status":state,
      "historical_source_git_commit_verified":PIN,
      "frozen_reconstructed_model_source_g1_2k_sha256":G1_SEAL,
      "historic_g1_12_checks_all_pass":True,
      "historic_original_v0_validation_best_p10_iteration":18,
      "historic_original_v0_validation_calibration_offset":float(orig["p10_calibration_offset"]),
      "historic_original_v0_weighted_q25":float(orig["relative_veto_threshold"]),
      "historic_v0_quantile_source_hashes":origcode,
      "g1_reconstruction_source_sha256":sha(reconpath),
      "v0_validation_quantile_routine_token_checks":text_checks,
      "g2_5_candidate_input_hash_reference_sha256":sha(reports["g2_inventory"]),
      "g2_5_historic_old_cohort_input_sha256":hashes,
      "A2_validation_predictions_and_weights_stored_as_standalone_artifacts":None,
      "A2_validation_predictions_recreatable_via_existing_original_code":ready,
      "A2_new_q15_or_q35_computed":False,
      "A3_pre_event_volatility_source_certified":False,
      "A4_tradable_portfolio_pnl_certified":False,
      "A6_topk_sensitivity_executed":False,
      "g2_protocol_frozen":False,
      "g3_scoring_authorized":False,
      "limitations":[
         "Source route is original, previously reproduced G1 train/valid/test replay, not a retained preexisting validation prediction vector.",
         "Inspect source logic and sign fixed q15/q25/q35 estimator and holdout analysis before any sensitivity calculation.",
         "Some G2.5 price-like filenames may be target/evaluation files. Source metadata does not establish pre-event price provenance.",
         "Original existing V2/V3/V4 outcomes are already consumed, so new threshold sensitivities remain post-outcome exploratory.",
         "The original V1 file copy/label discrepancy and new independent holdout limitation remain open.",
      ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.6:",state)
    print("Original pinned V0 validation-P10 source:",PIN)
    print("Original q25 reproduced:",result["historic_original_v0_weighted_q25"])
    print("Original source token checks:",text_checks)
    print("Original old-cohort files hash-referenced:",len(hashes))
    print("G2.5 metadata report SHA256:",sha(reports["g2_inventory"]))
    print("Report:",out)
    print("No original Pickle, prices, financial targets, new cohort or model predictions accessed.")
    return 0 if ready else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print(f"G2.6 stopped: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
