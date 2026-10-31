#!/usr/bin/env python3
"""G5.7b strict June target-producer vs consumer source evidence audit.

No private Pickles, notebooks, model targets or financial rows accessed.
Do not treat same-module np.savez_compressed as historical *.pkl producer.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

from ic_g5_7a_target_producer_source_scan import TARGET_FILES

ORIGINAL_G57A_SHA="4c1dc4bb7309e89020c58600fd58166958d74926173e4807bd1235b99c152c19"
EXPECTED={"V2":1,"V3":1,"V4":1}
SOURCE_LIMIT=2_000_000
class SourceLineageFailure(ValueError):pass

def require(value,reason):
    if not value:raise SourceLineageFailure(reason)

def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def _callname(node):
    if not isinstance(node,ast.Call):return ""
    f=node.func
    return f.attr if isinstance(f,ast.Attribute) else (f.id if isinstance(f,ast.Name) else "")

def _strings(node):
    """Literal constants ONLY, no expression evaluation."""
    return [x.value for x in ast.walk(node)
            if isinstance(x,ast.Constant) and isinstance(x.value,str)]

def _direct_target_writer(tree,target_basename):
    """Conservative: only a recognizable write sink with exact output name.

    No producer assertion for dynamic variable-based paths.
    """
    sinks=set()
    for n in ast.walk(tree):
        if not isinstance(n,ast.Call):continue
        name=_callname(n)
        if name=="to_pickle" and n.args and any(
                target_basename in x for x in _strings(n.args[-1])):
            sinks.add("TO_PICKLE_EXACT_ARGUMENT")
        # e.g. Path("EXACT.pkl").write_bytes(bytes)
        if name=="write_bytes" and isinstance(n.func,ast.Attribute):
            if isinstance(n.func.value,ast.Call):
                if target_basename in _strings(n.func.value):
                    sinks.add("PATH_WRITE_BYTES_EXACT_RECEIVER")
        # e.g. open("EXACT.pkl","wb"), only when explicitly write mode
        if name=="open" and len(n.args)>=2 and target_basename in _strings(n.args[0]):
            if any("w" in mode or "a" in mode or "x" in mode
                   for mode in _strings(n.args[1])):
                sinks.add("OPEN_EXACT_TARGET_WRITE_MODE")
    return sorted(sinks)

def _safe_source(root:Path,name:str)->bytes:
    relative=Path(name)
    require(not relative.is_absolute() and ".." not in relative.parts and
            relative.suffix==".py","Unsafe candidate relative Python path")
    source=root/relative
    require(source.is_file() and not source.is_symlink() and
            source.resolve().is_relative_to(root.resolve()),
            "Candidate outside original source root or symlink")
    require(0<source.stat().st_size<=SOURCE_LIMIT,"Candidate source size invalid")
    return source.read_bytes()

def analyze_source_report(source_report:dict,roots:list[Path])->dict:
    require(isinstance(source_report,dict) and source_report.get("schema_version")==
            "dtrm.ic.g5_7a.source_only_target_producer_search.v0",
            "Not original G5.7a source-only schema")
    require(source_report.get("python_files_checked")==38 and
            len(source_report.get("static_source_candidates",[]))==12 and
            source_report.get("exact_target_reference_counts")==EXPECTED,
            "Not original G5.7a bounded source inventory")
    for key,expected in (
        ("notebook_code_cells_scanned",False),
        ("pickle_files_opened",False),
        ("original_old_cohort_targets_read",False),
        ("target_generation_execution_proven",False),
        ("v2_v3_v4_label_transform_compatibility_proven",False),
        ("old_outcome_access_permitted",False)):
        require(source_report.get(key) is expected,"G5.7a safety/claim drift: "+key)
    require(len(roots)==2,"Expect exact two original code roots")
    for root in roots:
        require(root.is_dir() and not root.is_symlink(),
                "Original source scope missing or symlink")
    verified=[]
    for item in source_report["static_source_candidates"]:
        id=item.get("scope_id")
        require(type(id) is int and 1<=id<=2,"Invalid source scope index")
        name=item.get("relative_python_path")
        digest=item.get("python_source_sha256")
        require(isinstance(name,str) and isinstance(digest,str) and
                len(digest)==64,"Invalid original source record")
        raw=_safe_source(roots[id-1],name)
        require(sha(raw)==digest,"Candidate Python source SHA drift: "+name)
        try:tree=ast.parse(raw.decode("utf-8"),filename="original_source.py")
        except (UnicodeError,SyntaxError) as e:
            raise SourceLineageFailure("Cannot parse hash-bound source: "+name) from e
        calls={_callname(n) for n in ast.walk(tree) if isinstance(n,ast.Call)}
        original_ref=item.get("exact_target_filename_references",[])
        require(isinstance(original_ref,list),"G5.7a source filename references corrupted")
        literal_refs=sorted(k for k,f in TARGET_FILES.items() if f in raw.decode("utf-8"))
        require(sorted(original_ref)==literal_refs,
                "G5.7a exact source reference mismatch: "+name)
        writes={k:_direct_target_writer(tree,TARGET_FILES[k])
                for k in literal_refs}
        verified.append({
          "scope_id":id,"relative_python_path":name,
          "original_source_sha256":digest,
          "exact_target_filename_references":literal_refs,
          "same_module_read_pickle_present":"read_pickle" in calls,
          "same_module_nontarget_savez_present":"savez_compressed" in calls or "savez" in calls,
          "direct_exact_archive_write_sinks":writes,
          "is_direct_target_writer_candidate":any(writes.values()),
          "original_producer_execution_proven":False,
          "target_transform_compatibility_proven":False,
        })
    writer=any(x["is_direct_target_writer_candidate"] for x in verified)
    return {
      "schema_version":"dtrm.ic.g5_7b.consumer_writer_source_review.v0",
      "status":("G57B_DIRECT_EXACT_ARCHIVE_WRITE_CANDIDATE_PROVENANCE_OPEN" if writer
                else "G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE"),
      "original_g57a_report_sha256":ORIGINAL_G57A_SHA,
      "original_source_files_rehashed":len(verified),
      "exact_filename_reference_counts":EXPECTED,
      "verified_source_candidates":verified,
      "python_source_only":True,
      "jupyter_notebook_data_access":False,
      "original_v2_v3_v4_pickle_files_opened":False,
      "original_target_producer_execution_proven":False,
      "v2_v3_v4_label_transform_compatibility_proven":False,
      "old_outcome_access_authorized":False,
      "interpretation":"STRICT_STATIC_SOURCE_ONLY_NOT_JUNE_TARGET_GENERATION_PROOF",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--g57a-original-report",type=Path,required=True)
    p.add_argument("--source-root",type=Path,action="append",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    path=a.g57a_original_report.expanduser()
    require(path.is_file() and not path.is_symlink(),"Original G5.7a report unavailable")
    raw=path.read_bytes()
    require(sha(raw)==ORIGINAL_G57A_SHA,
            "Original G5.7a report SHA drift; refuse substitution")
    try:old=json.loads(raw)
    except (UnicodeError,json.JSONDecodeError) as e:
        raise SourceLineageFailure("Cannot decode original G5.7a manifest") from e
    result=analyze_source_report(old,a.source_root)
    out=a.out.expanduser()
    require(not out.exists(),"Refuse existing G5.7b audit overwrite")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(result["status"])
    print("ORIGINAL_G57A_SHA=PASS")
    print("SOURCE_CANDIDATES_REHASHED="+str(result["original_source_files_rehashed"]))
    for c in result["verified_source_candidates"]:
        if c["exact_target_filename_references"]:
            print("REFERENCE_SCOPE="+str(c["scope_id"])+
                  " FILE="+c["relative_python_path"]+
                  " TARGETS="+",".join(c["exact_target_filename_references"])+
                  " DIRECT_WRITE="+str(c["is_direct_target_writer_candidate"])+
                  " READ_PICKLE="+str(c["same_module_read_pickle_present"])+
                  " OTHER_SAVEZ="+str(c["same_module_nontarget_savez_present"]))
    print("TARGET_PRODUCER_EXECUTION_PROVEN=NO")
    print("LABEL_TRANSFORM_COMPATIBILITY=NOT_ESTABLISHED")
    print("OLD_OUTCOME_ACCESS=NONE")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
