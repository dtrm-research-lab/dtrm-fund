#!/usr/bin/env python3
"""G2.16: fail-closed synthetic-science and 22-item traceability preflight.

Only JSON metadata, Python source, and synthetic unittest test cases.
Reads NO original Pickles, prices, models, embeddings, targets, outcomes,
prediction arrays, or new cohorts. DOES NOT AUTHORIZE G3.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib,io,json,re,subprocess,sys
from pathlib import Path
import unittest

EXPECTED={
 "g2_13":"e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7",
 "g2_12":"e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f",
 "g2_10":"f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3",
 "g2_9":"65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb"
}
PIN="c7502a690162459cdfb3413573e3133c42efb126"

def fail(ok,reason):
    if not ok:raise RuntimeError(reason)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()
def obj(path):
    fail(path.is_file() and not path.is_symlink(),
         "Missing/unsafe metadata: "+path.name)
    result=json.loads(path.read_text(encoding="utf-8"))
    fail(isinstance(result,dict),"Not JSON object: "+path.name)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec",required=True)
    p.add_argument("--engine",required=True)
    p.add_argument("--tests",required=True)
    p.add_argument("--g3-0-source",required=True)
    p.add_argument("--g3-0-tests",required=True)
    p.add_argument("--freeze-builder",required=True)
    p.add_argument("--freeze-builder-tests",required=True)
    p.add_argument("--reviewer-matrix",required=True)
    p.add_argument("--g2-9",required=True)
    p.add_argument("--g2-10",required=True)
    p.add_argument("--g2-12",required=True)
    p.add_argument("--g2-13",required=True)
    p.add_argument("--frozen-repo",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out).expanduser()
    if out.exists():p.error("Refusing overwrite of G2.16 gate")
    sp=Path(a.spec).expanduser()
    eng=Path(a.engine).expanduser()
    tests=Path(a.tests).expanduser()
    stage0=Path(a.g3_0_source).expanduser()
    stage0_tests=Path(a.g3_0_tests).expanduser()
    freezer=Path(a.freeze_builder).expanduser()
    freezer_tests=Path(a.freeze_builder_tests).expanduser()
    mat=Path(a.reviewer_matrix).expanduser()
    fail(all(x.is_file() and not x.is_symlink()
             for x in (eng,tests,stage0,stage0_tests,freezer,freezer_tests)),
         "Missing/symlinked pure Python modules")
    spec=obj(sp);review=obj(mat)
    original={}
    for key,attr in (("g2_9","g2_9"),("g2_10","g2_10"),
                     ("g2_12","g2_12"),("g2_13","g2_13")):
        path=Path(getattr(a,attr)).expanduser()
        fail(sha(path)==EXPECTED[key],key+" original report SHA mismatched")
        original[key]=obj(path)

    repo=Path(a.frozen_repo).expanduser()
    head=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],
        check=True,capture_output=True,text=True).stdout.strip()
    fail(head==PIN,"Wrong source pin")
    dirty=subprocess.run(["git","-C",str(repo),"status","--porcelain",
        "--untracked-files=no"],check=True,capture_output=True,text=True)
    fail(not dirty.stdout.strip(),"Frozen source modified")
    fail(spec.get("schema_version")=="dtrm.ic.g2.final_analysis_scope_candidate.v1",
         "Scientific candidate protocol changed")
    fail(spec.get("status")=="G2_16_EXECUTION_SPEC_COMPLETE_TESTS_AND_OPERATOR_SIGNOFF_PENDING",
         "Wrong G2.16 protocol stage")
    fail(spec["original_code_commit"]==PIN,
         "Original source commit changed")
    fail(spec["original_evidence"]["g2_13_validation_pair_dates_sha256"]==EXPECTED["g2_13"],
         "G2.13 original validation report not in candidate")
    fail(spec["original_evidence"]["g2_12_holdout_pair_dates_sha256"]==EXPECTED["g2_12"],
         "G2.12 original holdout report not in candidate")
    fail(original["g2_13"].get("status")==
         "G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN" and
         original["g2_13"].get("original_valid_split_rows")==19880,
         "Original validation full date coverage is not PASS")
    fail(original["g2_12"].get("status")==
         "G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN" and
         original["g2_12"].get("v1_v4_event_pair_key_date_set_agreement") is True,
         "Original holdout dated source parity not PASS")

    runs=spec["executions"]
    fail(runs["G3_0"]["no_forward_targets_or_comparative_outcomes_accessed"] is True,
         "G3_0 must restrict to historic source/parity")
    fail(runs["G3_1_A2"]["validation_thresholds"]==[.15,.25,.35],
         "A2 fixed validation grid changed")
    fail(runs["G3_1_A6"]["fractions"]==[.05,.10,.15],
         "A6 fixed capacity grid changed")
    a3=runs["G3_1_A3"]
    fail(a3["minimum_returns"]==60 and
         a3["optional_40_return_fallback"] is False,
         "A3 primary must require exactly 60 valid past daily returns")
    fail("later" in a3["point_in_time_disclosure"].lower() or
         "postdates" in a3["point_in_time_disclosure"].lower(),
         "A3 retrospective provenance disclosure omitted")
    for v in runs.values():
        fail(v["classification"] in (
            "SOURCE_AND_MODEL_LINEAGE_PARITY_ONLY",
            "POST_OUTCOME_EXPLORATORY",
            "RETROSPECTIVE_POST_OUTCOME_EXPLORATORY"),
            "Undisclosed G3 inferential category")
    fail(spec["uncertainty_policy"]["old_V2_and_V4_ticker_CIs_include_zero"] is True,
         "Negative ticker-cluster limitation lost")
    flags=spec["protections"]
    fail(flags["conditional_g3_experiments_authorized"] is False and
         flags["complete_g2_protocol_frozen"] is False and
         flags["G3_0_model_lineage"]=="NOT YET OPERATOR VERIFIED" and
         flags["reviewer_22_item_freeze_pass"] is False,
         "G3 gate illegally promoted to authorized")
    fail(flags["source_reader_entrypoint"].startswith("NOT IMPLEMENTED"),
         "Do not certify unimplemented G3 loader")
    fail(review.get("case_id")=="ICOMPUTING-D-26-01069" and
         review.get("actual_reviewer_comment_count")==22,
         "Review map count/case mismatch")
    reviewers=review.get("actual_reviewer_comments",[])
    identifiers=[e["id"] for e in reviewers]
    expected_ids={
        *(f"E-{i:02}" for i in range(1,8)),
        *(f"R1-{i:02}" for i in range(1,8)),
        *(f"R2-{i:02}" for i in range(1,9))
    }
    fail(len(identifiers)==22 and set(identifiers)==expected_ids,
         "Reviewer/editor IDs not exactly 22")
    fail(all(r.get("g2_action_id") and r.get("g5_section")
             and r.get("g6_response_id") for r in reviewers),
         "Reviewer trace/action/response anchor incomplete")

    # A parser test alone is not sufficient; execute ALL synthetic tests.
    for script in (eng,tests,stage0,stage0_tests,freezer,freezer_tests):
        compile(script.read_text(encoding="utf-8"),str(script),"exec")
    sys.path.insert(0,str(eng.parent))
    test_suite=unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(tests.stem),
        unittest.defaultTestLoader.loadTestsFromName(stage0_tests.stem),
        unittest.defaultTestLoader.loadTestsFromName(freezer_tests.stem)
    ))
    fail(test_suite.countTestCases()>=36,
         "Expected 22 synthetic core, nine protected G3.0, and five freeze-builder tests")
    sink=io.StringIO()
    result=unittest.TextTestRunner(stream=sink,verbosity=1).run(test_suite)
    fail(result.wasSuccessful(),
         "Synthetic tests FAIL: "+sink.getvalue()[-3500:])
    packet={
       "schema_version":"dtrm.ic.g2.synthetic_scientific_freeze_gate.v1",
       "checked_at_utc":datetime.now(timezone.utc).isoformat(),
       "status":"G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING",
       "scientific_spec_sha256":sha(sp),
       "pure_core_sha256":sha(eng),
       "synthetic_test_module_sha256":sha(tests),
       "protected_g3_0_source_sha256":sha(stage0),
       "protected_g3_0_test_sha256":sha(stage0_tests),
       "operator_freeze_builder_sha256":sha(freezer),
       "operator_freeze_builder_test_sha256":sha(freezer_tests),
       "reviewer_traceability_sha256":sha(mat),
       "tests_run":result.testsRun,
       "tests_successful":True,
       "reviewer_editor_requirements_traced":22,
       "original_local_metadata_sha256":EXPECTED,
       "original_code_commit":PIN,
       "model_rowwise_numeric_parity_complete":False,
       "g2_global_freeze_committed":False,
       "g3_0_source_parity_executed":False,
       "g3_1_financial_comparison_authorized":False,
       "human_signoff_pending":True,
       "note":"Pure synthetic and metadata preflight only; original model-row prediction parity and frozen runner source not yet authenticated."
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(packet,indent=2)+"\n",encoding="utf-8")
    print("G2.16:",packet["status"])
    print("Synthetic tests PASS:",result.testsRun)
    print("Reviewer/editor anchors:",22)
    print("Core SHA:",packet["pure_core_sha256"])
    print("Spec SHA:",packet["scientific_spec_sha256"])
    print("Report:",out)
    print("NO original prices/models/targets or G3 analyses inspected.")
    print("G2 NOT FROZEN, G3_0 MODEL PARITY PENDING, G3_1 BLOCKED.")
    return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as e:
        print("G2.16 HALTED:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(3)
