#!/usr/bin/env python3
"""G2.7 A2 preregistration-source metadata preflight.

No scientific Pickles, prices, forward targets, XGBoost data/models,
validation predictions, source CSV or arrays opened or evaluated.
Only read JSON metadata reports and specification, check original
G2.6 source/P10 controls; this is NOT a scientific G3 run.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

PIN="c7502a690162459cdfb3413573e3133c42efb126"
OLD_G1="7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac"
OLD_G2_5="ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7"
THRESHOLD=-0.16665692627429962
OFFSET=-0.06494169682264328
QS=[0.15,0.25,0.35]
EXPECTED={
  "V2":(4449,444),
  "V3":(2827,282),
  "V4":(40320,4032),
}
SHA_FIELDS=("v2_threshold","v2_features","v2_signals","v3_features",
            "v3_signals","v4_signals","v1_features","v1_signals")
def checksum(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):
            h.update(block)
    return h.hexdigest()
def get_json(path:Path):
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required JSON metadata missing or symlink: "+path.name)
    return json.loads(path.read_text(encoding="utf-8"))
def demand(ok,msg):
    if not ok:raise RuntimeError(msg)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan",required=True)
    p.add_argument("--g2-5-inventory",required=True)
    p.add_argument("--g2-6-binding",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out).expanduser()
    if out.exists():p.error("Refuses overwrite of previous G2.7 report")
    plan_p=Path(a.plan).expanduser()
    inv_p=Path(a.g2_5_inventory).expanduser()
    bind_p=Path(a.g2_6_binding).expanduser()
    plan,inventory,binding=(get_json(z) for z in (plan_p,inv_p,bind_p))
    demand(plan.get("schema_version")=="dtrm.ic.g2.a2_threshold_sensitivity_plan.v1",
           "Plan schema changed")
    demand(plan.get("status")=="G2_A2_PLAN_PRECOMMITTED_DRAFT_NOT_FROZEN",
           "A2 preregistration is not this source-only draft")
    a2=plan["source_anchor"]
    demand(a2["pinned_original_commit"]==PIN and
           a2["historical_dossier_sha256"]==OLD_G1,
           "Plan has unverified historic pin or dossier")
    demand(a2["g2_5_source_inventory_sha256"]==OLD_G2_5
           and checksum(inv_p)==OLD_G2_5,
           "Original G2.5 inventory SHA256 altered")
    demand(inventory.get("schema_version")=="dtrm.ic.g2.historical_analysis_input_inventory.v1"
           and inventory.get("status")=="G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3",
           "Original G2.5 metadata-only inventory not PASS")
    demand(binding.get("schema_version")=="dtrm.ic.g2.validation_source_readiness.v1"
           and binding.get("status")=="G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED",
           "Original operator G2.6 source-only gate not PASS")
    demand(binding.get("frozen_reconstructed_model_source_g1_2k_sha256")==OLD_G1 and
           binding.get("historical_source_git_commit_verified")==PIN,
           "Original G2.6 historical training pin mismatch")
    demand(binding.get("g2_5_candidate_input_hash_reference_sha256")==OLD_G2_5,
           "Original G2.6 G2.5 input reference SHA changed")
    demand(binding.get("historic_g1_12_checks_all_pass") is True
           and binding.get("historic_original_v0_validation_best_p10_iteration")==18
           and binding.get("historic_original_v0_weighted_q25")==THRESHOLD
           and binding.get("historic_original_v0_validation_calibration_offset")==OFFSET,
           "Original V0 q25 cutoff or validation source numeric anchor mismatch")
    demand(binding.get("A2_new_q15_or_q35_computed") is False,
           "Preanalysis source gate cannot have computed alternative thresholds")
    demand(binding.get("g3_scoring_authorized") is False,
           "G3 authorization must remain false")
    demand(all(binding["v0_validation_quantile_routine_token_checks"].values()),
           "Frozen V0 weighted quantile source check failed")
    hashes=binding.get("g2_5_historic_old_cohort_input_sha256",{})
    demand(set(hashes)==set(SHA_FIELDS) and all(
           isinstance(x,str) and len(x)==64 and
           all(c in "0123456789abcdef" for c in x)
           for x in hashes.values()),
           "Eight original old holdout input SHA references missing")
    demand(a2.get("q25_original_validation_cutoff")==THRESHOLD
           and a2.get("calibration_offset")==OFFSET
           and a2.get("original_validation_rows")==19880
           and a2.get("p10_best_iteration")==18,
           "Predeclared original validation anchors incomplete")
    threshold=plan["threshold_spec"]
    demand(threshold["quantile_fractions"]==QS and
           threshold["quantile_method"].find("searchsorted(side=left)")>=0 and
           threshold["calibration_offset_frozen"]==OFFSET and
           threshold["p10_prediction_iteration_range_exclusive_upper"]==19 and
           threshold["q25_failed_to_match_behavior"]=="HALT_ALL_ANALYSES",
           "Predeclared q15/q25/q35 grid, estimator or calibration changed")
    demand(threshold.get("no_calibration_or_cutoff_estimation_on_v2_v3_v4_targets") is True,
           "No estimation with V2/V3/V4 outcomes allowed")
    cohorts=plan["cohorts"]
    demand(len(cohorts)==3 and
           all((x["rows"],x["K_at_0_10"])==EXPECTED[x["id"]]
               and x["original_status"]=="CONSUMED"
               for x in cohorts),
           "Historical cohorts or Top-K capacity incorrectly specified")
    selection=plan["selection"]
    demand(selection["candidate_full_K_required"] is True and
           "floor(0.10*N)" in selection["K_rule"] and
           "INFEASIBLE" in selection["zero_fill_or_insufficient_count"],
           "Fixed full-K selection/feasibility not enforced")
    stats=plan["uncertainty"]
    demand(stats["already_known_outcomes"] is True
           and stats["multiple_9_cells_exploratory_no_pooled_p_value"] is True
           and stats["overlapping_60day_targets_limitation"] is True,
           "Dependence or post-outcome caution missing")
    for kind,seed,cluster in (("news_bootstrap",20260821,"news_id"),
                               ("ticker_bootstrap",20260822,"ticker")):
        c=stats[kind]
        demand(c["cluster"]==cluster and c["replicates"]==10000
               and c["seed"]==seed and c["confidence"]==0.95,
               "Original fixed news/ticker bootstrap design changed")
    flags=plan["implementation_status"]
    demand(flags["original_source_verification_operator_g2_6_pass"] is True
           and flags["g2_overall_frozen"] is False
           and flags["g3_experiment_permitted"] is False,
           "G2.7 may not authorize G3 outcomes")
    result={
      "schema_version":"dtrm.ic.g2.a2_spec_metadata_preflight.v1",
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      "status":"G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN",
      "plan_sha256":checksum(plan_p),
      "g2_5_inventory_sha256":checksum(inv_p),
      "g2_6_operator_binding_sha256":checksum(bind_p),
      "original_model_source_commit":PIN,
      "old_input_sha256_refs":hashes,
      "validation_rows":19880,
      "validation_quantiles_predeclared":QS,
      "cohorts":[x["id"] for x in cohorts],
      "number_of_exploratory_old_cohort_cells":9,
      "G3_new_outcome_computations_authorized":False,
      "G2_full_revision_protocol_frozen":False,
      "note":"Documentation-only gate. Do NOT compute q15/q35 or test outcomes until full G2 closure and signature."
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2.7:",result["status"])
    print("Verified old-cohort input SHA references:",len(hashes))
    print("A2 q-grid:",QS,"; 3 old cohorts x 3 cutoffs =",9,"exploratory comparisons")
    print("Operator G2.6 SHA:",result["g2_6_operator_binding_sha256"])
    print("A2 prereg plan SHA:",result["plan_sha256"])
    print("Report:",out)
    print("G2 NOT FROZEN; G3 NOT AUTHORIZED; no targets or predictions read")
    return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G2.7 halted:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
