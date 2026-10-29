#!/usr/bin/env python3
"""G5.7d: precisely ONE previously skipped oversize notebook, source-only.

Stage 1 'metadata' reads SHA-only file bytes and sizes; stage 2 'code'
requires distinct affirmative owner flag and exact metadata-report SHA,
then streams ONLY this one notebook's CODE cell text (skip all outputs).
Nothing is executed. No historical target Pickle is ever opened.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from ic_g5_7c_notebook_code_source_scan import (
    MAX_BYTES_PER_NOTEBOOK, inspect_notebook, NotebookGateError,
)

ORIGINAL_G57C_SHA="e9b45fda73c8668caa5ae983cfa9dc542a084f8618055cff791c4a5ad82dab8f"
MAX_ONE_NOTEBOOK_BYTES=128_000_000
EXCLUDE={".git",".venv","venv","__pycache__","node_modules","Outputs","output",
         "outputs","results","Results","local_data","price_cache_fmp_pickle"}
class OmittedNotebookError(ValueError): pass

def need(ok,reason):
    if not ok:raise OmittedNotebookError(reason)

def hash_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def load_original(path:Path)->dict:
    need(path.is_file() and not path.is_symlink(),"Original G5.7c report missing/unsafe")
    need(hash_file(path)==ORIGINAL_G57C_SHA,"Original G5.7c SHA mismatch")
    x=json.loads(path.read_text(encoding="utf-8"))
    need(x.get("status")=="G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS"
         and x.get("schema_version")=="dtrm.ic.g5_7c.notebook_code_streaming_source.v0"
         and x.get("notebooks_enumerated")==15
         and x.get("notebooks_scanned")==14
         and x.get("oversize_skipped")==1
         and x.get("notebook_execution") is False
         and x.get("outputs_deserialized_or_saved") is False
         and x.get("financial_pickle_or_csv_opened") is False
         and x.get("train_transform_compatibility_proven") is False
         and x.get("old_v2_v3_v4_target_outcome_access_authorized") is False,
         "Original G5.7c original empirical status does not match")
    return x

def list_notebooks(root:Path)->dict[str,Path]:
    need(root.is_dir() and not root.is_symlink(),"Original notebook root missing/symlink")
    found={}
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[z for z in sorted(dirs) if z not in EXCLUDE
                 and not z.startswith(".") and not (Path(base)/z).is_symlink()]
        for name in sorted(files):
            if not name.endswith(".ipynb"):continue
            p=Path(base)/name
            if p.is_symlink() or not p.is_file():continue
            key=p.relative_to(root).as_posix()
            need(key not in found,"Repeated notebook path")
            found[key]=p
            need(len(found)<=400,"Too many notebooks; original scope drift")
    return found

def metadata_only(original:dict,root:Path)->dict:
    candidates=list_notebooks(root)
    need(len(candidates)==15,"Original 15-notebook scope changed")
    original_rows=original.get("notebooks")
    need(isinstance(original_rows,list) and len(original_rows)==14,
         "Original 14 notebook records absent")
    visited=set()
    for item in original_rows:
        key=item.get("relative_notebook_path")
        expected=item.get("notebook_sha256")
        need(isinstance(key,str) and key in candidates and key not in visited
             and isinstance(expected,str),"Original included path/hash mismatch")
        p=candidates[key]
        need(p.stat().st_size<=MAX_BYTES_PER_NOTEBOOK,"Previously scanned file now oversize")
        need(hash_file(p)==expected,"One of 14 scanned source SHA values drifted")
        visited.add(key)
    skipped=set(candidates)-visited
    need(len(skipped)==1,"Exactly one formerly omitted notebook required")
    key=next(iter(skipped))
    p=candidates[key]
    size=p.stat().st_size
    need(size>MAX_BYTES_PER_NOTEBOOK,"Formerly skipped notebook no longer oversized")
    current_sha=hash_file(p)
    status=("G57D_ONE_OMITTED_NOTEBOOK_PINNED_AND_CODE_READ_CAPABLE"
            if size<=MAX_ONE_NOTEBOOK_BYTES
            else "G57D_ONE_OMITTED_NOTEBOOK_TOO_LARGE_FINITE_SOURCE_STOP")
    return {
        "schema_version":"dtrm.ic.g5_7d.one_omitted_notebook.v0",
        "status":status,
        "source_g57c_original_sha256":ORIGINAL_G57C_SHA,
        "original_14_scanned_notebooks_sha_verified":14,
        "original_notebook_scope_count":15,
        "one_omitted_relative_path":key,
        "one_omitted_current_sha256":current_sha,
        "one_omitted_size_bytes":size,
        "omitted_historical_june_archival_sha_proven":False,
        "max_authorized_code_scan_bytes":MAX_ONE_NOTEBOOK_BYTES,
        "omitted_notebook_code_inspected":False,
        "notebook_outputs_decoded":False,
        "notebook_cells_executed":False,
        "old_v2_v3_v4_financial_labels_opened":False,
        "original_target_producer_executed_proven":False,
        "original_v0_train_transform_compatible_with_june_targets_proven":False,
    }

def code_only(meta:dict,original:dict,root:Path)->dict:
    need(meta.get("schema_version")=="dtrm.ic.g5_7d.one_omitted_notebook.v0"
         and meta.get("status")=="G57D_ONE_OMITTED_NOTEBOOK_PINNED_AND_CODE_READ_CAPABLE",
         "Missing acceptable metadata-only preflight")
    current=metadata_only(original,root)
    for field in ("one_omitted_relative_path","one_omitted_current_sha256",
                  "one_omitted_size_bytes","original_14_scanned_notebooks_sha_verified"):
        need(current[field]==meta.get(field),"Omitted source drift after preflight: "+field)
    name=meta["one_omitted_relative_path"]
    path=(root/name)
    need(path.is_file() and not path.is_symlink()
         and path.resolve().is_relative_to(root.resolve()),"Unsafe notebook target path")
    need(path.stat().st_size<=MAX_ONE_NOTEBOOK_BYTES,"Above bounded notebook file cap")
    try:rows=inspect_notebook(path)
    except (NotebookGateError,UnicodeError,OSError) as e:
        raise OmittedNotebookError("Omitted notebook code-cell parser cannot verify source") from e
    need(rows["notebook_sha256"]==meta["one_omitted_current_sha256"],
         "Notebook source SHA changed during reading")
    direct=sum(rows["direct_exact_target_write_code_cell_counts"].values())
    dynamic=rows["possible_dynamic_target_writer_cells"]
    refs=sum(rows["exact_target_filename_code_cell_counts"].values())
    state=("G57D_OMITTED_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY" if direct else
           "G57D_OMITTED_NOTEBOOK_DYNAMIC_WRITER_LEADS_ONLY" if dynamic else
           "G57D_OMITTED_NOTEBOOK_EXACT_INPUT_REFERENCES_ONLY" if refs else
           "G57D_NO_TARGET_WRITER_IDENTIFIED_IN_LAST_BOUNDED_NOTEBOOK")
    return {**meta,
        "status":state,
        "one_omitted_notebook_source_only_readout":rows,
        "omitted_notebook_code_inspected":True,
        "notebook_outputs_decoded":False,
        "notebook_cells_executed":False,
        "old_v2_v3_v4_financial_labels_opened":False,
        "original_target_producer_executed_proven":False,
        "original_v0_train_transform_compatible_with_june_targets_proven":False,
        "decision":"STATIC_CODE_LEAD_ONLY_NO_PROVEN_HISTORICAL_GENERATION",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-g57c-report",required=True,type=Path)
    p.add_argument("--original-notebooks-root",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--inspect-omitted-code",action="store_true")
    p.add_argument("--authorize-inspect-omitted-notebook-code",action="store_true")
    p.add_argument("--verified-metadata-report",type=Path)
    p.add_argument("--verified-metadata-sha256")
    a=p.parse_args()
    out=a.out.expanduser()
    need(not out.exists(),"Refuse previous evidence overwrite")
    original=load_original(a.original_g57c_report.expanduser())
    root=a.original_notebooks_root.expanduser()
    if not a.inspect_omitted_code:
        need(not a.authorize_inspect_omitted_notebook_code
             and a.verified_metadata_report is None,
             "Metadata-only stage must not include inspection authorization")
        r=metadata_only(original,root)
    else:
        need(a.authorize_inspect_omitted_notebook_code,
             "Explicit owner authorization for omitted notebook CODE required")
        need(a.verified_metadata_report is not None
             and isinstance(a.verified_metadata_sha256,str)
             and len(a.verified_metadata_sha256)==64,
             "Exact SHA-verified metadata report required before code inspection")
        mp=a.verified_metadata_report.expanduser()
        need(mp.is_file() and not mp.is_symlink()
             and hash_file(mp)==a.verified_metadata_sha256,
             "G5.7d source metadata report SHA drift")
        meta=json.loads(mp.read_text(encoding="utf-8"))
        r=code_only(meta,original,root)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(r["status"])
    print("ORIGINAL_G57C_SHA=PASS")
    print("ORIGINAL_14_SCANNED_NOTEBOOK_SHA=PASS")
    print("OMITTED_SOURCE="+r["one_omitted_relative_path"])
    print("OMITTED_BYTES="+str(r["one_omitted_size_bytes"]))
    print("OMITTED_CURRENT_SHA256="+r["one_omitted_current_sha256"])
    print("NOTEBOOK_CODE_INSPECTED="+str(r["omitted_notebook_code_inspected"]))
    print("JUNE_TARGET_PRODUCER_EXECUTION_PROVEN=NO")
    print("V2_V3_V4_LABEL_TRANSFORM_COMPATIBILITY=NOT_ESTABLISHED")
    print("FINANCIAL_TARGET_FILES_OPENED=NONE")

if __name__=="__main__":
    main()
