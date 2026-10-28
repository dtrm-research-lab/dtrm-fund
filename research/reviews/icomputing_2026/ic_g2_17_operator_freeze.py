#!/usr/bin/env python3
"""G2.17: operator-attested release for G3.0 ONLY, fail-closed.

This script does not authorize G3.1 or access financial data/models.
Human approval is explicit CLI action, NOT a cryptographic signature.
It independently verifies that immutable Git commit contains the exact
methods, source reader, traceability and reviewer protocol that passed
the operator's *latest* 31-test G2.16 gate, and invokes the legacy
22-requirement reviewer gate on the approval-specific matrix copy.
No source files, original model/price/target Pickles, scores or returns
are opened. Does NOT fabricate a signature or a Git commit.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT="research/reviews/icomputing_2026/"
ORIG="c7502a690162459cdfb3413573e3133c42efb126"
G2_GATE="G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING"
LOCKED_IDS={*(f"E-{i:02}" for i in range(1,8)),
            *(f"R1-{i:02}" for i in range(1,8)),
            *(f"R2-{i:02}" for i in range(1,9))}
FILES={
 "spec":"G2_16_EXPLORATORY_SCOPE_CANDIDATE.json",
 "engine":"ic_g2_g3_exploratory_core.py",
 "stage0":"ic_g3_0_original_model_row_parity.py",
 "matrix":"G2_17_REVIEWER_TRACEABILITY_FREEZE_CANDIDATE.json",
 "protocol":"G2_17_FINAL_PROTOCOL_FREEZE_CANDIDATE.md",
 "legacy":"ic_g2_freeze_preflight.py",
 "freezer":"ic_g2_17_operator_freeze.py"
}

def fail(condition,message):
    if not condition:raise RuntimeError(message)
def digest(content):
    return hashlib.sha256(content).hexdigest()
def sha(path:Path):
    fail(path.is_file() and not path.is_symlink(),"Missing or unsafe local source: "+path.name)
    return digest(path.read_bytes())
def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))
def git(repo,*cmd):
    proc=subprocess.run(["git","-C",str(repo),*cmd],
                       text=False,capture_output=True,check=True)
    return proc.stdout

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review-branch-repo",required=True)
    p.add_argument("--freeze-commit",required=True)
    p.add_argument("--latest-g2-16-pass",required=True)
    p.add_argument("--inputs-dir",required=True,
                   help="Same locally downloaded research source files as G2.16 PASS")
    p.add_argument("--out",required=True)
    p.add_argument("--matrix-out",required=True)
    p.add_argument("--editor-review-gate-out",required=True)
    p.add_argument("--approve-g3-0-source-parity-only",action="store_true",
                   help="Explicit operator attestation of science/vintage/no-independent-holdout limitations")
    p.add_argument("--acknowledge-retrospective-data-vintage-risk",action="store_true")
    p.add_argument("--acknowledge-no-independent-60day-holdout",action="store_true")
    a=p.parse_args()
    if not (a.approve_g3_0_source_parity_only
            and a.acknowledge_retrospective_data_vintage_risk
            and a.acknowledge_no_independent_60day_holdout):
        p.error("Explicit three-part operator scientific approval REQUIRED; no automated signoff")
    repo=Path(a.review_branch_repo).expanduser().resolve()
    srcdir=Path(a.inputs_dir).expanduser().resolve()
    out=Path(a.out).expanduser()
    mout=Path(a.matrix_out).expanduser()
    gout=Path(a.editor_review_gate_out).expanduser()
    fail(len({str(out),str(mout),str(gout)})==3,
         "Output paths must be distinct")
    for path in (out,mout,gout):
        fail(not path.exists(),"Refuse overwrite of existing G2 freeze document")
    commit=a.freeze_commit.lower()
    fail(len(commit)==40 and all(c in "0123456789abcdef" for c in commit),
         "Freeze commit must be a fully qualified 40-character Git SHA")
    fail(git(repo,"cat-file","-t",commit).decode().strip()=="commit",
         "Frozen Git SHA is not an existing commit")
    # The versioned source is the real commit; do not treat current
    # mutable branch or untracked local files as the frozen authority.
    contents={}
    for key,base in FILES.items():
        content=git(repo,"show",commit+":"+ROOT+base)
        local=srcdir/base
        fail(sha(local)==digest(content),
             "Downloaded candidate does not match actual immutable Git commit: "+base)
        contents[key]=content
    report_path=Path(a.latest_g2_16_pass).expanduser()
    result=read_json(report_path)
    fail(result.get("status")==G2_GATE and
         result.get("tests_successful") is True and
         result.get("tests_run",0)>=36 and
         result.get("reviewer_editor_requirements_traced")==22,
         "Latest G2.16 31-test source/reviewer PASS not proven")
    fail(result.get("original_code_commit")==ORIG and
         result.get("g3_1_financial_comparison_authorized") is False,
         "Original source changed or G3.1 gate opened")
    for key,resultkey in (
        ("spec","scientific_spec_sha256"),
        ("engine","pure_core_sha256"),
        ("stage0","protected_g3_0_source_sha256"),
        ("matrix","reviewer_traceability_sha256")
    ):
        # G2.16 checks the reviewer matrix passed as its argument.
        # It must be the EXACT reconciled G2.17 candidate, not an
        # earlier provisional version that happens to have 22 IDs.
        fail(digest(contents[key])==result.get(resultkey),
             "Latest G2.16 PASS not bound to this exact "+key)
    fail(digest(contents["freezer"])==sha(Path(__file__).resolve())
         and result.get("operator_freeze_builder_sha256")==digest(contents["freezer"]),
         "Executing G2 freeze builder does not match exact G2.16 tested and immutable Git-committed source")
    # The canonical final protocol is separately immutable in commit.
    matrix=json.loads(contents["matrix"])
    protocol=contents["protocol"].decode("utf-8")
    fail(matrix.get("status")=="G2_17_22_REQUIREMENTS_EXPLORATORY_DESIGNS_BOUND_MANUAL_FREEZE_PENDING",
         "Wrong final reviewer candidate stage")
    fail(matrix.get("revision_protocol_freeze_commit") is None and
         matrix.get("human_scientific_signoff") is False and
         matrix.get("g3_1_historic_financial_target_access_authorized") is False and
         matrix.get("all_g3_analyses_specified") is True,
         "G2.17 candidate must be honestly pending (never pre-sign)")
    fail({x["id"] for x in matrix.get("actual_reviewer_comments",[])}==LOCKED_IDS,
         "Not all 22 editor and reviewer requirements covered")
    matrix["revision_protocol_freeze_commit"]=commit
    matrix["human_scientific_signoff"]=True
    matrix["g3_0_parity_authorized"]=True
    matrix["g3_1_historic_financial_target_access_authorized"]=False
    matrix["g2_16_current_source_code_test_pass"]=True
    matrix["g2_16_operator_gate_report_sha256"]=sha(report_path)
    matrix["status"]="G2_FROZEN_G3_0_SOURCE_PARITY_ONLY_G3_1_BLOCKED"
    # Validates all 22 original reviewer comments and exact
    # scientific limitation fields, not just counted IDs.
    sys.path.insert(0,str(srcdir))
    import ic_g2_freeze_preflight
    problems,notes=ic_g2_freeze_preflight.verify(matrix,protocol)
    fail(not problems,"Original full G2 reviewer gate blocked: "+", ".join(problems))
    serialized=(json.dumps(matrix,indent=2,ensure_ascii=False)+"\n").encode()
    source_gate_digest=sha(report_path)
    approval={
       "schema_version":"dtrm.ic.g2.operator_attested_science_freeze.v1",
       "generated_at_utc":datetime.now(timezone.utc).isoformat(),
       "status":"G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY",
       "editorial_case":"ICOMPUTING-D-26-01069",
       "original_code_commit":ORIG,
       "immutable_freeze_commit":commit,
       "source_gate_report_sha256":source_gate_digest,
       "human_scientific_signoff":True,
       "human_signoff_basis":"Explicit operator command-line attestation; NOT a cryptographic signature",
       "reviewed_retrospective_price_vendor_vintage_limitations":True,
       "reviewed_original_v2_v4_ticker_ci_cross_zero":True,
       "reviewed_60_calendar_day_overlap":True,
       "reviewed_no_independent_nonoverlapping_60d_holdout":True,
       "g3_0_source_parity_only_authorized":True,
       "g3_1_old_outcome_access_authorized":False,
       "protected_g3_0_source_sha256":digest(contents["stage0"]),
       "scientific_core_sha256":digest(contents["engine"]),
       "scientific_spec_sha256":digest(contents["spec"]),
       "reviewer_matrix_sha256":digest(serialized),
       "canonical_protocol_sha256":digest(contents["protocol"]),
       "reviewer_editor_items":22,
       "local_original_economic_outcomes_accessed":False,
       "original_historic_model_weight_precommit_recovered":False,
       "no_model_training_or_scoring_performed":True,
       "limitations":[
           "The historical V2/V3/V4 outcomes were previously consumed; additional analyses are POST_OUTCOME_EXPLORATORY.",
           "Original July-5 price archive is a later snapshot, not verified at contemporaneous historical provider vintage.",
           "Original V2 and V4 ticker-cluster confidence intervals include zero.",
           "Reconstructed model weights are not original pretrained serialized weights.",
           "No independent new matured nonoverlapping 60-day 2026 cohort has been certified.",
           "G3.1 financial metrics and new target labels remain BLOCKED, even if G3.0 signal parity succeeds."
       ]
    }
    check={
       "schema_version":"dtrm.ic.g2.reviewer_freeze_check.operator_attested.v1",
       "checked_at_utc":approval["generated_at_utc"],
       "status":"G2_22_EDITOR_REVIEWER_ITEMS_AND_SCIENTIFIC_POLICY_PASS_AFTER_OPERATOR_ATTESTATION",
       "matrix_sha256":digest(serialized),
       "protocol_sha256":digest(contents["protocol"]),
       "blocking_codes":[],
       "reviewer_items_listed":22,
       "operator_attestation_present":True,
       "g3_0_only":True,
       "g3_1_authorized":False,
       "notes":notes
    }
    for path,contents_bytes in (
        (mout,serialized),
        (gout,(json.dumps(check,indent=2)+"\n").encode()),
        (out,(json.dumps(approval,indent=2)+"\n").encode()),
    ):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("xb") as fp:fp.write(contents_bytes)
    print("G2.17: G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY")
    print("G2.16 latest tests:",result["tests_run"],"reviewer/editor requirements:",22)
    print("Frozen Git commit:",commit)
    print("Operator source-gate report SHA256:",source_gate_digest)
    print("Operator approval manifest:",out)
    print("G3.0 original V2/V3 model-signal parity: AUTHORIZED; NOT EXECUTED.")
    print("G3.1 old forward targets, returns or profits: BLOCKED.")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G2.17 HALTED:",type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
