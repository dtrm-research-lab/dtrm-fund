#!/usr/bin/env python3
"""G3.1 original q25/K10 parity FAILURE TRIAGE, not new analysis.

Read-only, old baseline data only. Uses the exact original frozen
Phase II evaluation function and the separately approved A2/A6
join/core implementation on original SHA-verified cohort files.
Compares ONLY already-published V2/V3/V4 q25/K10 point estimates.
NO q15/q35; NO K5/K15; NO bootstrap; NO A3 prices; NO target fitting;
NO 18-cell new outcome estimands. Never exposes row-level targets.

OPERATOR MUST CONSENT to reading original locally SHA-bound trusted
Pickles. Source integrity is checked before opening any input Pickle.
A diagnostic source Git SHA separate from previously approved runner
must be supplied, and both sources must match immutable commits.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

FROZEN_ORIGINAL="c7502a690162459cdfb3413573e3133c42efb126"
APPROVED_G31="5cf62c854643576ee6059ac44f55a805b8ff3137"
REL="research/reviews/icomputing_2026/ic_g3_1_original_q25_parity_diagnostic.py"
OLD="research/experiments/run_phase2_primary_bootstrap.py"
TOL=1e-12

def must(ok,msg):
    if not ok:raise RuntimeError(msg)

def sha(file):
    h=hashlib.sha256()
    path=Path(file).expanduser()
    must(path.is_file() and not path.is_symlink(),"Missing/unsafe original local evidence: "+path.name)
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def git(repo,*args):
    return subprocess.run(["git","-C",str(repo),*args],
                          check=True,capture_output=True).stdout

def frozen_source(path,name,repo,commit):
    contents=git(repo,"show",commit+":"+name)
    must(path.is_file() and not path.is_symlink() and
         hashlib.sha256(contents).hexdigest()==sha(path),
         "Frozen original executable source differs from immutable Git: "+name)

def original_module(file:Path):
    spec=importlib.util.spec_from_file_location("ic_original_phase2_q25_no_main",file)
    must(spec is not None and spec.loader is not None,"Cannot inspect frozen Phase II method")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

def one_diagnostic(original,cohort,files,join_fn,arrays_fn,protected_fn):
    import numpy as np
    import pandas as pd
    config=original.COHORTS[cohort]
    # The ORIGINAL untouched code controls base pairing and selection.
    old_frame=original.load_cohort(files[(cohort,"signals")],files[(cohort,"targets")])
    old_eval=original.evaluate_selection(
        old_frame["baseline_prediction"].to_numpy(),
        old_frame["p10_pass"].to_numpy(dtype=bool),
        old_frame["target_model"].to_numpy()
    )
    must(old_eval is not None,"Original Phase II q25/K10 selection is infeasible: "+cohort)
    old_sources={
        "signals":pd.read_pickle(files[(cohort,"signals")]),
        "targets":pd.read_pickle(files[(cohort,"targets")]),
    }
    guarded=join_fn(old_sources["signals"],old_sources["targets"],cohort)
    data=arrays_fn(guarded)
    prot=protected_fn(data["prediction"],data["target"],data["original_q25_pass"],.10)
    must(prot.feasible,"Protected q25/K10 selection infeasible: "+cohort)
    orig={
        "topk_rows":int(old_eval["topk_rows"]),
        "baseline_mean":float(old_eval["baseline_topk_mean"]),
        "candidate_mean":float(old_eval["candidate_topk_mean"]),
        "delta_mean":float(old_eval["delta_topk_mean"]),
        "baseline_hit_rate":float(old_eval["baseline_topk_hit_rate"]),
        "candidate_hit_rate":float(old_eval["candidate_topk_hit_rate"]),
        "delta_hit_rate":float(old_eval["delta_topk_hit_rate"]),
    }
    new={
        "topk_rows":prot.k,
        "baseline_mean":prot.baseline_mean,
        "candidate_mean":prot.candidate_mean,
        "delta_mean":prot.delta_mean,
        "baseline_hit_rate":prot.baseline_hit_rate,
        "candidate_hit_rate":prot.candidate_hit_rate,
        "delta_hit_rate":prot.delta_hit_rate,
    }
    # THREE SEPARATE DIFFERENCES: old method vs original expected,
    # our guarded new method vs original expected, and method vs method.
    expected={"delta_mean":float(config["expected_delta_mean"]),
              "delta_hit_rate":float(config["expected_delta_hit"])}
    diffs={
        "original_vs_expected_delta_mean":orig["delta_mean"]-expected["delta_mean"],
        "original_vs_expected_delta_hit_rate":orig["delta_hit_rate"]-expected["delta_hit_rate"],
        "protected_vs_expected_delta_mean":new["delta_mean"]-expected["delta_mean"],
        "protected_vs_expected_delta_hit_rate":new["delta_hit_rate"]-expected["delta_hit_rate"],
        "protected_minus_original_delta_mean":new["delta_mean"]-orig["delta_mean"],
        "protected_minus_original_delta_hit_rate":new["delta_hit_rate"]-orig["delta_hit_rate"],
    }
    original_ok=(abs(diffs["original_vs_expected_delta_mean"])<=TOL and
                 abs(diffs["original_vs_expected_delta_hit_rate"])<=TOL)
    protected_ok=(abs(diffs["protected_vs_expected_delta_mean"])<=TOL and
                  abs(diffs["protected_vs_expected_delta_hit_rate"])<=TOL)
    method_ok=(all(abs(new[k]-orig[k])<=TOL for k in orig if k!="topk_rows")
               and orig["topk_rows"]==new["topk_rows"])
    if original_ok and protected_ok and method_ok:
        status="ORIGINAL_AND_PROTECTED_Q25_K10_PARITY_PASS"
    elif not original_ok and method_ok:
        status="ORIGINAL_SOURCE_VS_FROZEN_EXPECTED_MISMATCH_METHODS_AGREE"
    elif original_ok and not method_ok:
        status="NEW_JOIN_OR_SELECTION_REGRESSION_ORIGINAL_IS_PASS"
    else:
        status="BOTH_REFERENCE_AND_IMPLEMENTATION_MISMATCH_INVESTIGATE"
    return {
        "cohort":cohort,"rows":int(len(old_frame)),
        "old_join_rows":int(len(old_frame)),"new_join_rows":int(len(guarded)),
        "original_p10_pass_count":int(old_frame["p10_pass"].sum()),
        "protected_p10_pass_count":int(np.sum(data["original_q25_pass"])),
        "old_phase2_expected":expected,
        "original_exact_phase2_method":orig,
        "new_protected_original_only_method":new,
        "differences":diffs,
        "original_point_parity_pass":original_ok,
        "protected_point_parity_pass":protected_ok,
        "two_implementations_agree":method_ok,
        "classification":status,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review-repo",required=True)
    p.add_argument("--diagnostic-code-commit",required=True)
    p.add_argument("--original-frozen-repo",required=True)
    p.add_argument("--source-only-report",required=True)
    p.add_argument("--g3-0-report",required=True)
    p.add_argument("--g2-freeze-approval",required=True)
    p.add_argument("--original-local-data",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--authorize-original-q25-parity-diagnostic-only",
                   action="store_true")
    p.add_argument("--trust-previously-sha-audited-original-pickles",
                   action="store_true")
    a=p.parse_args()
    if not (a.authorize_original_q25_parity_diagnostic_only
            and a.trust_previously_sha_audited_original_pickles):
        p.error("Explicit operator consent to original-only point-estimate diagnostic and trusted local Pickles required")
    dest=Path(a.out).expanduser()
    must(not dest.exists(),"Refuse to overwrite historical audit/result reports")
    review=Path(a.review_repo).expanduser()
    diagnostic_commit=a.diagnostic_code_commit.lower()
    must(len(diagnostic_commit)==40 and
         all(c in "0123456789abcdef" for c in diagnostic_commit),
         "Diagnostic source requires immutable 40-hex Git SHA")
    frozen_source(Path(__file__).resolve(),REL,review,diagnostic_commit)
    original_root=Path(a.original_frozen_repo).expanduser()
    must(git(original_root,"rev-parse","HEAD").decode().strip()==FROZEN_ORIGINAL,
         "Original Phase II reference checkout not frozen")
    must(not git(original_root,"status","--porcelain","--untracked-files=no").strip(),
         "Original Phase II reference checkout modified")
    original_path=original_root/OLD
    frozen_source(original_path,OLD,original_root,FROZEN_ORIGINAL)
    # Import of the previously approved and code-SHA-checked runner
    # does NOT execute main or open any original files.
    from ic_g3_1_a2_a6_protected_runner import make_release_checks
    from ic_g3_1_a2_a6_join_contract import source_exact_join,extract_source_arrays
    from ic_g2_g3_exploratory_core import select_topk
    a.approved_commit=APPROVED_G31
    exact,bound=make_release_checks(a)
    must(len(bound)==6,"Expected exactly six original source input files")
    original=original_module(original_path)
    details={}
    for c in ("V2","V3","V4"):
        details[c]=one_diagnostic(original,c,bound,
                                  source_exact_join,extract_source_arrays,select_topk)
    overall=("G3_1_ORIGINAL_Q25_K10_ALL_3_PARITY_PASS_INVESTIGATE_PRIOR_FAILURE"
             if all(v["classification"]=="ORIGINAL_AND_PROTECTED_Q25_K10_PARITY_PASS"
                    for v in details.values()) else
             "G3_1_ORIGINAL_Q25_K10_PARITY_DISCREPANCY_LOCALIZED_G3_1_RESULTS_BLOCKED")
    output={
        "schema_version":"dtrm.ic.g3.1.original_q25_only_failure_triage.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":overall,"original_scientific_commit":FROZEN_ORIGINAL,
        "prior_approved_g31_code_commit":APPROVED_G31,
        "new_diagnostic_code_commit":diagnostic_commit,
        "source_only_report_sha256":sha(a.source_only_report),
        "g3_0_report_sha256":sha(a.g3_0_report),
        "g2_freeze_attestation_sha256":sha(a.g2_freeze_approval),
        "original_files_sha_verified":6,
        "cohorts":details,
        "allowed_reconstruction":"ONLY original published q25/K10 point statistics",
        "any_q15_q35_or_k5_k15_sensitivity_executed":False,
        "any_bootstrap_executed":False,
        "any_new_a2_a6_18_cell_result_executed":False,
        "financial_outcome_values_present_only_locally":True,
        "g3_1_18_cell_results_authorized_by_diagnostic":False,
        "target_not_realized_portfolio_pnl":True,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as fp:
        json.dump(output,fp,ensure_ascii=False,indent=2)
        fp.write("\n")
    print("G3.1 ORIGINAL PARITY DIAGNOSTIC:",overall)
    for key,d in details.items():
        print(key,"N",d["rows"],"K",d["original_exact_phase2_method"]["topk_rows"],
              "original_mean",format(d["original_exact_phase2_method"]["delta_mean"],".17g"),
              "expected_mean",format(d["old_phase2_expected"]["delta_mean"],".17g"),
              "protected_mean",format(d["new_protected_original_only_method"]["delta_mean"],".17g"),
              "original_hit",format(d["original_exact_phase2_method"]["delta_hit_rate"],".17g"),
              "expected_hit",format(d["old_phase2_expected"]["delta_hit_rate"],".17g"),
              "protected_hit",format(d["new_protected_original_only_method"]["delta_hit_rate"],".17g"),
              "STATUS",d["classification"])
    print("Local report:",dest)
    print("NO A2/A6 18-cells, NO new q/K, NO bootstrap, NO A3, NO portfolio P&L.")
    return 0 if overall.startswith("G3_1_ORIGINAL_Q25_K10_ALL_3") else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G3.1 ORIGINAL PARITY DIAGNOSTIC HALTED:",
              type(exc).__name__,str(exc),file=sys.stderr)
        raise SystemExit(3)
