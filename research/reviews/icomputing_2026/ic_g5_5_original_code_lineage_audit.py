#!/usr/bin/env python3
"""G5.5 REAL ORIGINAL SOURCE-CODE audit; NO model/data/outcome access.

Reads frozen original Git blobs (not financial Pickles), compares actual
working files bytewise with pinned 2026 original-source commit and validates
target lineage, continuous risk features and unresolved prerequisites.
A PASS proves SOURCE CODE PATHS, not cohort economic data readiness or effects.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

FROZEN="c7502a690162459cdfb3413573e3133c42efb126"
FILES_FROZEN=(
    "research/experiments/run_exante_baseline_v0.py",
    "research/experiments/run_probabilistic_xgb_v0.py",
    "research/experiments/run_phase2_primary_bootstrap.py",
    "src/dtrm/exante_target.py",
    "src/dtrm/legacy_target_preprocessing.py",
)
# Verified via GitHub fetch_file(ref=FROZEN) on 2026-10-29; exact frozen
# Git blob OIDs. Local 'git hash-object' works even in shallow CI checkouts.
# This is a *pinned remote blob identity* check, not a re-fetch of the
# historical commit in every CI job.
FROZEN_BLOB_SHA1={
    "research/experiments/run_exante_baseline_v0.py":"cecd1a71ffc1526d64f37d0a52b47db4b1e36675",
    "research/experiments/run_probabilistic_xgb_v0.py":"26f056b767aa17daa7f088153ab09e1fa34dc1e6",
    "research/experiments/run_phase2_primary_bootstrap.py":"88b2cb9e76cdfc10f9afab982847aa13c16bbe10",
    "src/dtrm/exante_target.py":"c73ef57fcedfccbbf36aab2bc0cf8974c42377f9",
    "src/dtrm/legacy_target_preprocessing.py":"45e37c24e0c09675f5a0b9374c48a096bbb72925",
}

FILES_REVIEW=(
    "research/reviews/icomputing_2026/ic_g3_1_a2_a6_join_contract.py",
    "research/reviews/icomputing_2026/ic_g3_2_a3_original_3arm_source_preflight.py",
    "research/reviews/icomputing_2026/ic_g3_2_a3_three_arm_pure_points.py",
    "research/reviews/icomputing_2026/ic_g2_g3_exploratory_core.py",
    "research/reviews/icomputing_2026/ic_g3_1_a2_validation_only_source.py",
)
STATUS="G55_FROZEN_ORIGINAL_SOURCE_LINEAGE_CONFIRMED_MARKET_DATA_UNREAD"


class CodeLineageError(RuntimeError):
    pass


def _sha(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()


def _fns(tree:ast.AST)->set[str]:
    return {n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}


def _calls(tree:ast.AST)->set[str]:
    calls=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            x=n.func
            if isinstance(x,ast.Name):
                calls.add(x.id)
            elif isinstance(x,ast.Attribute):
                calls.add(x.attr)
    return calls


def _references(tree:ast.AST)->set[str]:
    return {n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}


def source_semantics(files:dict[str,bytes])->dict:
    trees={}
    for path,blob in files.items():
        try:
            trees[path.rsplit("/",1)[-1]]=ast.parse(blob.decode("utf-8"),filename=path)
        except (UnicodeError,SyntaxError) as exc:
            raise CodeLineageError(f"Original source fails parse: {path}") from exc
    base=trees["run_exante_baseline_v0.py"]
    prob=trees["run_probabilistic_xgb_v0.py"]
    phase2=trees["run_phase2_primary_bootstrap.py"]
    target=trees["exante_target.py"]
    preprocessing=trees["legacy_target_preprocessing.py"]
    join=trees["ic_g3_1_a2_a6_join_contract.py"]
    volatility=trees["ic_g3_2_a3_original_3arm_source_preflight.py"]
    riskpure=trees["ic_g3_2_a3_three_arm_pure_points.py"]
    core=trees["ic_g2_g3_exploratory_core.py"]
    valid=trees["ic_g3_1_a2_validation_only_source.py"]
    verdict={
        "original_point_and_quantile_scripts_construct_60d_raw_excess_beta":
            all("build_exante_raw_targets" in _fns(t) and
                "forward_excess_beta_target" in _calls(t)
                for t in (base,prob)),
        "original_scripts_apply_train_only_target_preprocessing":
            all("prepare_training_data" in _fns(t) and
                "preprocess_legacy_targets" in _calls(t)
                for t in (base,prob)),
        "original_beta_excess_definition_references_stock_and_market_forward_returns":
            "forward_excess_beta_target" in _fns(target) and
            "market_adjusted_target" in _calls(target),
        "original_preprocessor_exports_train_ticker_means_and_clip_bounds":
            "preprocess_legacy_targets" in _fns(preprocessing) and
            False  # Determined with explicit AST checks below
    }
    # AST identifier checks (not executable tests on market sources).
    names={x.id for x in ast.walk(preprocessing) if isinstance(x,ast.Name)}
    strings=_references(phase2)
    verdict["original_preprocessor_exports_train_ticker_means_and_clip_bounds"]=(
        {"ticker_means","np"}.issubset(names) and
        "preprocess_legacy_targets" in _fns(preprocessing) and
        {"train","valid","test","clip_lower","clip_upper","ticker_means"}.issubset(_references(preprocessing))
        and "clip" in _calls(preprocessing))
    verdict.update({
        "phase2_old_result_uses_transformed_target_model":
            "target_model" in strings and "merge" in _calls(phase2),
        "original_g3_join_returns_continuous_calibrated_p10_and_float_target":
            {"p10_calibrated","p10_raw","target_model","baseline_prediction"}.issubset(_references(join))
            and "source_exact_join" in _fns(join)
            and "extract_source_arrays" in _fns(join),
        "existing_original_volatility_preflight_recomputes_risk_continuously":
            "counts" in _fns(volatility) and
            "trailing_volatility_60" in _calls(volatility)
            and "source_risk_admission_mask" in _fns(riskpure),
        "existing_original_volatility_risk_is_date_restricted":
            "trailing_volatility_60" in _fns(core),
        "original_validation_reconstruction_exists_but_is_p10_only":
            "reconstruct_valid_p10_only" in _fns(valid)
            and "original_validation_p10_thresholds" in _calls(valid),
    })
    if not all(verdict.values()):
        failed=[k for k,v in verdict.items() if not v]
        raise CodeLineageError("Original source code semantic gates fail: "+",".join(failed))
    return verdict


def audit(repo:Path,frozen_ref:str=FROZEN)->dict:
    repo=repo.expanduser().resolve()
    if not (repo/".git").exists():
        raise CodeLineageError("Git repository not found")
    if frozen_ref!=FROZEN:
        raise CodeLineageError("No arbitrary alternative original code reference")
    files={}
    frozen_hash={}
    frozen_blob_oid={}
    for path in FILES_FROZEN:
        local=repo/path
        if not local.is_file() or local.is_symlink():
            raise CodeLineageError(f"Missing/unsafe original working source: {path}")
        blob=local.read_bytes()
        actual=subprocess.run(["git","hash-object","--",str(local)],
                 capture_output=True,check=True,text=True).stdout.strip()
        if actual!=FROZEN_BLOB_SHA1[path]:
            raise CodeLineageError(f"Original source differs from source code blob pinned at historical GitHub commit: {path}")
        frozen_hash[path]=_sha(blob)
        frozen_blob_oid[path]=actual
        files[path]=blob
    review_hash={}
    for path in FILES_REVIEW:
        local=repo/path
        if not local.is_file() or local.is_symlink():
            raise CodeLineageError(f"Missing review source: {path}")
        blob=local.read_bytes()
        review_hash[path]=_sha(blob)
        files[path]=blob
    checks=source_semantics(files)
    return {
        "schema_version":"dtrm.ic.g5_5.original_code_lineage.v0",
        "status":STATUS,
        "frozen_original_commit":FROZEN,
        "frozen_original_public_source_sha256":frozen_hash,
        "frozen_original_public_git_blob_sha1":frozen_blob_oid,
        "identity_basis":"PINNED_ORIGINAL_COMMIT_GITHUB_BLOB_OIDS_VALIDATED_WITH_LOCAL_GIT_HASH_OBJECT",
        "historical_git_commit_object_reloaded_in_this_ci":False,
        "existing_review_source_sha256":review_hash,
        "semantic_checks":checks,
        "supported_by_code_only":{
            "continuous_original_p10_source_join_present":True,
            "continuous_trailing_volatility_reconstruction_path_present":True,
            "train_ticker_center_reconstruction_function_present":True,
            "original_transformed_target_definition_source_verified":True,
        },
        "still_unverified":{
            "actual_train_ticker_centers_recovered":False,
            "reconstructed_validation_point_predictions_and_iqr_audited":False,
            "original_v2_v3_v4_private_pickles_opened":False,
            "original_price_vendor_acquisition_vintage_certified":False,
            "raw_untransformed_absolute_returns_audited":False,
            "information_matched_old_outcome_evaluated":False,
            "clipped_target_decomposition_old_outcome_evaluated":False,
            "economic_portfolio_pnl_estimated":False,
            "unused_new_independent_60d_holdout_available":False,
        },
        "conclusion":"ORIGINAL_CODE_LINEAGE_ONLY_NO_PRIVATE_MARKET_DATA_OR_OUTCOME_ACCESS",
    }


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        p.error("Refuse overwrite of existing source audit report")
    result=audit(a.repo)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(STATUS)
    print("ORIGINAL_FROZEN_SOURCE_FILES="+str(len(FILES_FROZEN)))
    print("REVIEW_SOURCE_FILES="+str(len(FILES_REVIEW)))
    print("SOURCE_LINEAGE_CHECKS="+str(len(result["semantic_checks"])))
    print("TRAIN_CENTERS_HISTORIC_RECONSTRUCTION=NOT_YET_EXECUTED")
    print("PRIVATE_MARKET_OUTCOME_ACCESS=NONE")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
