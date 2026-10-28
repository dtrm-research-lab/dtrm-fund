#!/usr/bin/env python3
"""G3.1 A2/A6 bounded old-outcome runner — EXPLICIT HUMAN ATTESTATION.

No implicit financial access, A3, model refitting or file overwrites.
This program is permitted to open trusted original V2/V3/V4 old
financial target Pickles ONLY after the operator explicitly:
  --authorize-retrospective-a2-a6-old-outcome-access
  --acknowledge-no-independent-60d-holdout
  --acknowledge-no-realized-tradable-pnl
and SHA-binding this exact program + five pure modules to the
specified IMMUTABLE Git commit, and verifying original G2/G3.0
approval, prior source-only gate report and six original input SHAs.

It first validates V0 validation q25, exact three original historical
q25/K10 outcomes, then computes ALL 18 retrospective point estimates.
--mode full additionally performs every pre-specified 10,000 news and
ticker cluster bootstrap for all FEASIBLE cells.
--mode point is an explicit partial scientific output, NOT completed G3.1.

No raw news IDs, prices, per-row outcomes or model weights are emitted.
Scientific effects are beta-adjusted FORWARD 60d targets, not P&L.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ORIGINAL="c7502a690162459cdfb3413573e3133c42efb126"
G2_FREEZE="3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0"
SOURCE_GATE_SHA="3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8"
G3_0_SHA="a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a"
SCRIPTS=[
  "ic_g3_1_a2_a6_protected_runner.py",
  "ic_g3_1_a2_a6_join_contract.py",
  "ic_g3_1_a2_a6_pure_grid.py",
  "ic_g3_1_a2_validation_only_source.py",
  "ic_g2_g3_exploratory_core.py",
  "test_ic_g3_1_a2_a6_join_contract.py",
  "test_ic_g3_1_a2_a6_pure_grid.py",
  "test_ic_g3_1_a2_validation_only_source.py",
  "test_ic_g3_1_a2_a6_protected_runner.py",
]
FROZEN_PATH="research/reviews/icomputing_2026/"
COHORTS=("V2","V3","V4")
HEX40=re.compile(r"^[0-9a-f]{40}$")

def must(ok,reason):
    if not ok:raise RuntimeError(reason)

def sha(path:Path):
    must(path.is_file() and not path.is_symlink(),
         "Missing or symlinked file: "+path.name)
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda:fp.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def obj(path):
    p=Path(path).expanduser()
    return json.loads(p.read_text(encoding="utf-8")) if (
       p.is_file() and not p.is_symlink()) else must(False,"Missing/unsafe JSON: "+p.name)

def git(repo,*args):
    return subprocess.run(["git","-C",str(repo),*args],
           capture_output=True,check=True).stdout

def make_release_checks(args):
    commit=args.approved_commit.lower()
    must(HEX40.fullmatch(commit),"Full 40-digit candidate Git SHA required")
    repo=Path(args.review_repo).expanduser()
    must(repo.is_dir(),"Review repository missing")
    must(git(repo,"cat-file","-t",commit).strip()==b"commit",
         "Unknown immutable Git commit")
    local=Path(__file__).resolve().parent
    exact={}
    for name in SCRIPTS:
        file=local/name
        actual=sha(file)
        gitblob=git(repo,"show",commit+":"+FROZEN_PATH+name)
        expected=hashlib.sha256(gitblob).hexdigest()
        must(actual==expected,
             "Local reviewed G3.1 scientific code/test differs from frozen Git commit: "+name)
        exact[name]=actual
    sourcepath=Path(args.source_only_report).expanduser()
    must(sha(sourcepath)==SOURCE_GATE_SHA,
         "G3.1 source-only report exact operator SHA mismatch")
    source=obj(sourcepath)
    must(source.get("status")==
         "G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED"
         and source.get("g3_1_outcome_access_authorized") is False
         and source.get("old_financial_targets_deserialized") is False
         and source.get("original_expected_total_pairs")==47596,
         "G3.1 original source pre-authorization was not a clean, locked PASS")
    paritypath=Path(args.g3_0_report).expanduser()
    must(sha(paritypath)==G3_0_SHA,"G3.0 source/model parity SHA changed")
    parity=obj(paritypath)
    must(parity.get("status")==
         "G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED"
         and parity.get("g3_1_financial_comparison_authorized") is False,
         "Frozen G3.0 model parity never authorized G3.1")
    approval=obj(args.g2_freeze_approval)
    must(approval.get("status")==
         "G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY"
         and approval.get("immutable_freeze_commit")==G2_FREEZE
         and approval.get("human_scientific_signoff") is True
         and approval.get("g3_1_old_outcome_access_authorized") is False
         and source.get("g2_owner_freeze_approval_sha256")==
                 sha(Path(args.g2_freeze_approval).expanduser()),
         "G2 operator approval lineage missing/different")
    must(source.get("source_g3_0_sha256")==G3_0_SHA and
         source.get("g2_freeze_commit")==G2_FREEZE,
         "G3.1 source-only source lineage differs")
    originals=Path(args.original_local_data).expanduser()
    must(originals.is_dir() and not originals.is_symlink(),
         "Trusted original local source root missing/unsafe")
    bound={}
    for cohort in COHORTS:
        detail=source["cohorts"][cohort]
        for role in ("signals","targets"):
            rec=detail["files"][role]
            must(rec["source_metadata_status"]=="ORIGINAL_G2_5_MANIFEST_SHA_PASS",
                 "Unbound original source: "+cohort+"/"+role)
            p=originals/rec["basename"]
            must(p.is_file() and not p.is_symlink() and
                 p.stat().st_size==rec["size_bytes"] and
                 sha(p)==rec["sha256_original_g2_5"],
                 "Original input bytes changed since six-file SHA PASS: "+cohort+"/"+role)
            bound[(cohort,role)]=p
    must(source["cohorts"]["V4"]["files"]["targets"]["basename"]==
         "probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
         "Original V4 MUST use original V1 outcome target archive")
    return exact,bound

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review-repo",required=True)
    p.add_argument("--approved-commit",required=True)
    p.add_argument("--source-only-report",required=True)
    p.add_argument("--g3-0-report",required=True)
    p.add_argument("--g2-freeze-approval",required=True)
    p.add_argument("--g1-dossier",required=True)
    p.add_argument("--original-local-data",required=True)
    p.add_argument("--original-frozen-repo",required=True)
    p.add_argument("--legacy-outputs",required=True)
    p.add_argument("--reconstructed-models",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--mode",required=True,choices=("point","full"))
    p.add_argument("--authorize-retrospective-a2-a6-old-outcome-access",
                   action="store_true")
    p.add_argument("--acknowledge-no-independent-60d-holdout",
                   action="store_true")
    p.add_argument("--acknowledge-no-realized-tradable-pnl",
                   action="store_true")
    p.add_argument("--trust-original-audited-pickles",action="store_true")
    a=p.parse_args()
    if not (a.authorize_retrospective_a2_a6_old_outcome_access
            and a.acknowledge_no_independent_60d_holdout
            and a.acknowledge_no_realized_tradable_pnl
            and a.trust_original_audited_pickles):
        p.error("SEPARATE explicit human authorization and three scientific risk/old-Pickle acknowledgements REQUIRED")
    dest=Path(a.out).expanduser()
    must(not dest.exists(),"Refuse overwriting research results or previous scientific checkpoint")
    exact,bound=make_release_checks(a)

    # All source, frozen-code, original-report and operator approval
    # gates have passed before ANY untrusted Pickle deserialization.
    import pandas as pd
    from ic_g3_1_a2_a6_join_contract import source_exact_join,extract_source_arrays
    from ic_g3_1_a2_validation_only_source import reconstruct_valid_p10_only
    from ic_g3_1_a2_a6_pure_grid import analyze_18_cells
    valid_raw,valid_news,valid_check=reconstruct_valid_p10_only(
       frozen_root=a.original_frozen_repo,
       local_data=a.original_local_data,
       old_outputs=a.legacy_outputs,
       reconstructed_models=a.reconstructed_models,
       g1_dossier_path=a.g1_dossier)
    original={}
    for cohort in COHORTS:
        signals=pd.read_pickle(bound[(cohort,"signals")])
        targets=pd.read_pickle(bound[(cohort,"targets")])
        joined=source_exact_join(signals,targets,cohort)
        original[cohort]=extract_source_arrays(joined)
    response=analyze_18_cells(
       original_valid_p10_raw=valid_raw,
       original_valid_news_ids=valid_news,
       old_cohorts=original,
       bootstrap=(a.mode=="full"),
    )
    must(response["cells_expected"]==18 and len(response["cells"])==18,
         "No incomplete G3.1 sensitivity results permitted")
    output={
        "schema_version":"dtrm.ic.g3.1.a2_a6.operator_attested_exploratory.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":"G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY"
                 if a.mode=="full" else
                 "G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN",
        "mode":a.mode,
        "explicit_owner_acknowledgements":{
             "retrospective_old_outcome_access":True,
             "no_independent_nonoverlapping_60d_holdout":True,
             "no_realized_tradable_portfolio_pnl":True,
             "trust_original_audited_pickles":True,
             "old_outcomes_have_already_been_consumed":True,
        },
        "original_g2_freeze_commit":G2_FREEZE,
        "immutable_a2_a6_runner_commit":a.approved_commit.lower(),
        "reviewed_scripts_sha256":exact,
        "original_g3_0_source_report_sha256":G3_0_SHA,
        "six_original_source_report_sha256":SOURCE_GATE_SHA,
        "g2_owner_original_attestation_sha256":
              sha(Path(a.g2_freeze_approval).expanduser()),
        "original_validation_source_check":valid_check,
        "financial_target_definition":"60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",
        "a3_price_volatility_experiment_authorized":False,
        "no_independent_matured_new_60_day_holdout":True,
        "all_old_outcomes_were_previously_consulted":True,
        "results":response,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as fp:
        json.dump(output,fp,indent=2,ensure_ascii=False)
        fp.write("\n")
    print("G3.1:",output["status"])
    print("Original source q25 / K10 parity PASS:",",".join(sorted(original)))
    print("Validation-only calibrated P10 q15/q25/q35:",response["cutoffs_validation_only"])
    print("Old-cohort exploratory cells:",len(response["cells"]))
    if a.mode=="point":
        print("Cluster intervals NOT RUN; point-estimate-only checkpoint.")
    else:
        print("News and ticker clustered uncertainty completed with fixed 10k resamples per feasible cell.")
    print("Report:",dest)
    print("NO independent new temporal cohort, NO tradable account P&L, NO A3 price comparison.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as e:
        print("G3.1 HALTED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(3)
