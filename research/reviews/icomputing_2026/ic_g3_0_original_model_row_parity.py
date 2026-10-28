#!/usr/bin/env python3
"""Protected G3.0 original V2/V3 ranker/P10 source parity ONLY.

Requires G2.16 synthetic science PRE-FREEZE PASS. No original
financial target labels, return series, price caches or bootstrap are
opened. Validates original local V2/V3 features/signals against the
retrospectively reconstructed XGB model; this DOES NOT authenticate the
original model's pre-event serialized weight or upstream source vintage.

Security: only trusted local previously SHA-manifested original Pickles
are allowed. External Pickles are untrusted and can execute code.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path

G1_SHA="7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac"
G26_SHA="1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2"
THRESH=-0.16665692627429962
OFFSET=-0.06494169682264328
COHORTS={
 "V2":("probabilistic_v2_holdout_features_2026-06-10.npy",
       "probabilistic_v2_holdout_signals_2026-06-10.pkl",4449),
 "V3":("probabilistic_v3_holdout_features_2026-06-14.npy",
       "probabilistic_v3_holdout_signals_2026-06-14.pkl",2827)
}

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()
def obj(path):
    if not path.is_file() or path.is_symlink():raise RuntimeError("Missing/unsafe original source: "+path.name)
    return json.loads(path.read_text(encoding="utf-8"))
def must(x,s):
    if not x:raise RuntimeError(s)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--g2-16-synthetic-gate",required=True)
    p.add_argument("--g2-freeze-approval",required=True,help="Human-signed and SHA-bound immutable G2 freeze manifest authorizing G3.0 ONLY")
    p.add_argument("--g1-sealed-dossier",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--models-dir",required=True)
    p.add_argument("--original-local-data",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--trust-original-pickles",action="store_true")
    a=p.parse_args()
    if not a.trust_original_pickles:
        p.error("Requires explicit trusted LOCAL source Pickle opt-in")
    target=Path(a.out).expanduser()
    if target.exists():p.error("Refuse overwrite of original G3.0 parity evidence")
    gate_path=Path(a.g2_16_synthetic_gate).expanduser()
    gate=obj(gate_path)
    must(gate.get("status")=="G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING" and
         gate.get("tests_successful") is True and gate.get("tests_run",0)>=19 and
         gate.get("g3_1_financial_comparison_authorized") is False,
         "Protected synthetic source methodology preflight not PASS")
    freeze=obj(Path(a.g2_freeze_approval).expanduser())
    must(freeze.get("status")=="G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY" and
         freeze.get("source_gate_report_sha256")==sha(gate_path) and
         freeze.get("human_scientific_signoff") is True and
         freeze.get("g3_1_old_outcome_access_authorized") is False and
         isinstance(freeze.get("immutable_freeze_commit"),str) and
         len(freeze["immutable_freeze_commit"])==40,
         "No real operator-hash and human-approved G2 freeze for G3.0; HALT")
    dossierpath=Path(a.g1_sealed_dossier).expanduser()
    bindpath=Path(a.g2_6_binding).expanduser()
    must(sha(dossierpath)==G1_SHA and sha(bindpath)==G26_SHA,
         "Historic original SHA lineage failed")
    g1=obj(dossierpath);g26=obj(bindpath)
    must(g1.get("status")=="HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN",
         "G1.2 historic source dossier not PASS")
    must(g26.get("status")=="G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
         "G2.6 original model validation binding missing")
    hashes=g26["g2_5_historic_old_cohort_input_sha256"]
    model_hashes=g1.get("reconstructed_unapproved_model_sha256",{})
    local=Path(a.original_local_data).expanduser()
    modelroot=Path(a.models_dir).expanduser()
    must(local.is_dir() and modelroot.is_dir() and
         not local.is_symlink() and not modelroot.is_symlink(),
         "Missing original trust-bounded model/source dirs")
    import numpy as np
    import pandas as pd
    import xgboost as xgb
    loaded={}
    for name in ("exante_ranker.ubj","p10.ubj"):
        file=modelroot/name
        must(file.is_file() and not file.is_symlink(),"Reconstructed model missing")
        must(sha(file)==model_hashes.get(name),
             "Reconstructed booster has different weights from G1.2K dossier")
        booster=xgb.Booster()
        booster.load_model(str(file))
        loaded[name]=booster
    out={
        "schema_version":"dtrm.ic.g3.0.historic_original_model_pair_parity.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":"G3_0_PENDING",
        "source_g1_sealed_sha256":G1_SHA,
        "source_g2_6_binding_sha256":G26_SHA,
        "g2_16_source_gate_sha256":sha(gate_path),
        "g2_freeze_approval_sha256":sha(Path(a.g2_freeze_approval).expanduser()),
        "reconstructed_original_weights_not_preexisting":True,
        "original_source_provenance_open":True,
        "comparative_old_targets_opened":False,
        "old_cohort_risk_or_returns_computed":False,
        "g3_1_financial_comparison_authorized":False,
        "cohorts":{},
    }
    all_ok=True
    for cohort,(featname,sigfilename,n) in COHORTS.items():
        for k,filename in (("features",featname),("signals",sigfilename)):
            f=local/filename
            expected=hashes["v2_"+k if cohort=="V2" else "v3_"+k]
            must(f.is_file() and not f.is_symlink() and sha(f)==expected,
                 cohort+" source file has changed SHA: "+filename)
        X=np.load(local/featname,allow_pickle=False)
        signals=pd.read_pickle(local/sigfilename)
        must(X.shape==(n,390) and np.isfinite(X).all(),
             cohort+" original features not 390 finite dimensions")
        req={"news_id","ticker","date_dt","baseline_prediction","p10_pass"}
        must(isinstance(signals,pd.DataFrame) and len(signals)==n and
             req.issubset(signals.columns),
             cohort+" signal row source invalid")
        must(not signals.duplicated(["news_id","ticker"]).any(),
             cohort+" old original event/ticker keys duplicate")
        dm=xgb.DMatrix(X)
        predicted=loaded["exante_ranker.ubj"].predict(dm,iteration_range=(0,11))
        raw=loaded["p10.ubj"].predict(dm,iteration_range=(0,19))
        calibrated=raw+OFFSET
        origpred=signals["baseline_prediction"].to_numpy(dtype=float)
        origveto=signals["p10_pass"].to_numpy(dtype=bool)
        wrong_orig_veto=signals["p10_pass"].isna().sum()
        numeric_drift=np.abs(predicted-origpred)
        rank_bad=int(np.sum(~np.isfinite(numeric_drift)|(numeric_drift>1e-6)))
        veto_bad=int(np.sum((calibrated>=THRESH)!=origveto))
        p10_numeric_reference={}
        # Only explicitly named numerical original fields are
        # compared. Ambiguous fields are never guessed as raw.
        for name,pred in (("p10_raw",raw),("p10_calibrated",calibrated)):
            if name in signals.columns:
                ref=signals[name].to_numpy(dtype=float)
                delta=np.abs(pred-ref)
                p10_numeric_reference[name]={
                    "nonfinite_or_mismatched_rows":int(np.sum(~np.isfinite(delta)|(delta>1e-6))),
                    "max_absolute_difference":float(np.max(delta)) if np.isfinite(delta).all() else None
                }
        status=("ROW_PARITY_PASS" if not rank_bad and not veto_bad and
                wrong_orig_veto==0 and
                all(v["nonfinite_or_mismatched_rows"]==0
                    for v in p10_numeric_reference.values()) else
                "ORIGINAL_SIGNAL_ROW_NUMERIC_PARITY_FAILED")
        if status!="ROW_PARITY_PASS":all_ok=False
        out["cohorts"][cohort]={
            "rows":n,"frozen_score_columns_checked":["baseline_prediction","p10_pass"],
            "max_ranker_abs_error":float(np.max(numeric_drift)) if np.isfinite(numeric_drift).all() else None,
            "ranker_rows_exceeding_1e_6":rank_bad,
            "original_p10_veto_mask_disagreements":veto_bad,
            "original_p10_veto_missing_values":int(wrong_orig_veto),
            "original_p10_numeric_reference":p10_numeric_reference,
            "source_rows_and_feature_alignment_assumption":"Persisted feature and signal index order; not an independent source-copy timestamp proof",
            "status":status
        }
    out["status"]=("G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED"
                   if all_ok else "G3_0_HISTORICAL_ROW_PARITY_FAILED_G3_1_BLOCKED")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("G3.0:",out["status"])
    for k,v in out["cohorts"].items():
        print(k,v["status"],"ranker mismatches",v["ranker_rows_exceeding_1e_6"],
              "veto mask disagreements",v["original_p10_veto_mask_disagreements"])
    print("Report:",target)
    print("No old forward-target/outcome values opened; G3.1 still BLOCKED.")
    return 0 if all_ok else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as e:
        print("G3.0 HALTED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(3)
