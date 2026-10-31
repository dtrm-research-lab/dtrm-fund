#!/usr/bin/env python3
"""G5.7a: bounded SOURCE-ONLY search for historical target-producing Python code.

Never opens original target files or notebooks (whose outputs can embed data).
Never serializes source snippets, secrets, row identifiers or absolute paths.
Static source candidate does NOT prove actual June label production.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

TARGET_FILES={
 "V2":"probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
 "V3":"probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
 "V4":"probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
}
MAX_FILES=2000
MAX_FILE_BYTES=2_000_000
MAX_SOURCE_BYTES=32_000_000

class SourceScanError(ValueError):
    pass

def _regular(path:Path)->bool:
    return path.is_file() and not path.is_symlink()

def _callnames(tree)->set[str]:
    values=set()
    for x in ast.walk(tree):
        if isinstance(x,ast.Call):
            func=x.func
            if isinstance(func,ast.Name):
                values.add(func.id)
            elif isinstance(func,ast.Attribute):
                values.add(func.attr)
    return values

def _iter_files(root:Path):
    """No symlink traversal; skip dot dirs, caches, envs, output dirs."""
    exclude={".git",".venv","venv","env","__pycache__","node_modules",
             "Outputs","outputs","results","Results","data","local_data",
             "price_cache_fmp_pickle","artifacts",".mypy_cache"}
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=sorted(z for z in dirs if z not in exclude
                       and not z.startswith(".")
                       and not (Path(base)/z).is_symlink())
        for file in sorted(files):
            if file.endswith(".py"):
                p=Path(base)/file
                if _regular(p):yield p

def scan(roots:list[Path])->dict:
    if not roots or len(roots)>4:
        raise SourceScanError("Need 1-4 explicitly named original code roots")
    allhits=[]
    total=0
    bytes_checked=0
    skipped_oversize=0
    roots_checked=[]
    for i,path in enumerate(roots):
        root=path.expanduser().resolve()
        if (not root.is_dir() or path.expanduser().is_symlink()
            or root.is_symlink()):
            raise SourceScanError("Original code scope missing/unsafe: scope "+str(i+1))
        roots_checked.append({"scope_id":i+1,"exists":True,"scope_kind":"PY_SOURCE_ONLY"})
        for f in _iter_files(root):
            total+=1
            if total>MAX_FILES:
                raise SourceScanError("Bounded scan source file count exceeded")
            sz=f.stat().st_size
            if sz>MAX_FILE_BYTES:
                skipped_oversize+=1
                continue
            bytes_checked+=sz
            if bytes_checked>MAX_SOURCE_BYTES:
                raise SourceScanError("Bounded scan total source bytes exceeded")
            data=f.read_bytes()
            try: src=data.decode("utf-8")
            except UnicodeDecodeError:continue
            hits={name:basename in src for name,basename in TARGET_FILES.items()}
            has_target=any(hits.values())
            has_generic=("target_model" in src and
                         ("to_pickle" in src or "pickle.dump" in src
                          or "save" in src))
            if not has_target and not has_generic:
                continue
            try:
                tree=ast.parse(src,filename="source_candidate.py")
                calls=_callnames(tree)
                parses=True
            except SyntaxError:
                calls=set()
                parses=False
            write_calls=sorted(calls.intersection({
                "to_pickle","dump","dumps","save","savez","savez_compressed"}))
            # 'dump' and 'save' may be unrelated; never classify as genuine writer.
            candidate=bool(write_calls and has_target)
            allhits.append({
              "scope_id":i+1,
              "relative_python_path":f.relative_to(root).as_posix(),
              "python_source_sha256":hashlib.sha256(data).hexdigest(),
              "exact_target_filename_references":sorted(k for k,v in hits.items() if v),
              "same_module_static_write_call_names":write_calls,
              "same_module_target_model_identifier_text":("target_model" in src),
              "same_module_train_preprocess_reference":("preprocess_legacy_targets" in src),
              "python_ast_parsed":parses,
              "static_writer_candidate_not_execution_proof":candidate,
              "generic_target_writer_candidate_only":has_generic and not has_target,
            })
    writers=[x for x in allhits if x["static_writer_candidate_not_execution_proof"]]
    if writers:status="G57A_SOURCE_WRITER_CANDIDATE_ONLY_PROVENANCE_OPEN"
    elif any(x["exact_target_filename_references"] for x in allhits):
        status="G57A_TARGET_REFERENCES_ONLY_NO_PRODUCER_PROOF"
    else:status="G57A_NO_EXACT_TARGET_SOURCE_IN_BOUNDED_PY_SCOPE"
    counts={k:sum(k in x["exact_target_filename_references"] for x in allhits)
            for k in TARGET_FILES}
    return {
      "schema_version":"dtrm.ic.g5_7a.source_only_target_producer_search.v0",
      "status":status,
      "scopes":roots_checked,
      "python_files_checked":total,
      "source_bytes_checked":bytes_checked,
      "oversized_python_files_skipped":skipped_oversize,
      "exact_target_reference_counts":counts,
      "static_source_candidates":allhits,
      "notebook_code_cells_scanned":False,
      "pickle_files_opened":False,
      "original_old_cohort_targets_read":False,
      "target_generation_execution_proven":False,
      "identical_v0_training_clip_and_ticker_means_proven":False,
      "v2_v3_v4_label_transform_compatibility_proven":False,
      "old_outcome_access_permitted":False,
      "note":"Source-only static inventory, not actual artifact-generation or point-in-time proof.",
    }

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root",required=True,type=Path,action="append")
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    out=args.out.expanduser()
    if out.exists():ap.error("Refusing overwrite of prior source inventory")
    result=scan(args.source_root)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(result["status"])
    print("PYTHON_FILES_CHECKED="+str(result["python_files_checked"]))
    print("STATIC_SOURCE_CANDIDATES="+str(len(result["static_source_candidates"])))
    for k,v in result["exact_target_reference_counts"].items():
        print(k+"_EXACT_FILENAME_REFERENCES="+str(v))
    print("NOTEBOOK_OUTPUTS_READ=NO")
    print("OLD_V2_V3_V4_TARGET_DATA_ACCESS=NONE")
    print("LABEL_TRANSFORMATION_COMPATIBILITY=NOT_ESTABLISHED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
