#!/usr/bin/env python3
"""G5.7c bounded streaming notebook CODE ONLY provenance inventory.

Explicit owner authorization required. No notebook execution, Pickles or data
inputs. Raw notebook text is read to skip cells/outputs but output content is
NEVER JSON-decoded, accumulated, displayed or included in reports.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
from ic_g5_7a_target_producer_source_scan import TARGET_FILES
from ic_g5_7b_direct_writer_disambiguation import _direct_target_writer

G57B_SHA="b8d0d10eef98fe57a85cd1ddc65262aaa905d01f53c3733f397389a2cf73e308"
MAX_NOTEBOOKS=400
MAX_BYTES_PER_NOTEBOOK=16_000_000
MAX_TOTAL_NOTEBOOK_BYTES=128_000_000
MAX_CELLS=1200
MAX_SOURCE_CHARS_PER_FILE=2_000_000
class NotebookGateError(ValueError):pass

def require(ok,msg):
    if not ok:raise NotebookGateError(msg)

class StreamingNotebook:
    """Small bounded tokenizer; *only* JSON-decodes keys and code-cell source."""
    def __init__(self,f):
        self.f=f
        self.hold=None
    def peek(self):
        if self.hold is None:self.hold=self.f.read(1)
        return self.hold
    def take(self):
        x=self.peek();self.hold=None
        if not x:raise NotebookGateError("Truncated notebook JSON")
        return x
    def ws(self):
        while self.peek() and self.peek().isspace():self.take()
    def expect(self,c):
        self.ws()
        if self.take()!=c:raise NotebookGateError("Malformed notebook JSON structure")
    def string(self):
        self.ws()
        if self.take()!='"':raise NotebookGateError("Expected JSON string")
        buf=['"']
        while True:
            c=self.take()
            buf.append(c)
            if c=="\\":
                buf.append(self.take())
            elif c=='"':break
            if len(buf)>MAX_SOURCE_CHARS_PER_FILE+100:
                raise NotebookGateError("Overlong JSON key/source fragment")
        try:return json.loads(''.join(buf))
        except json.JSONDecodeError as e:raise NotebookGateError("Malformed JSON string") from e
    def skip_string(self):
        if self.take()!='"':raise NotebookGateError("Invalid JSON string")
        while True:
            c=self.take()
            if c=="\\":self.take()
            elif c=='"':break
    def skip_value(self):
        """Skip arbitrary JSON value without decoding payloads/outputs."""
        self.ws()
        c=self.peek()
        if c=='"':self.skip_string();return
        if c in "{[":
            stack=[self.take()]
            while stack:
                c=self.peek()
                if not c:raise NotebookGateError("Truncated JSON output")
                if c=='"':self.skip_string()
                elif c in "{[":stack.append(self.take())
                elif c in "}]":
                    last=stack.pop()
                    if (last,c) not in (("{","}"),("[","]")):
                        raise NotebookGateError("Unbalanced notebook JSON")
                    self.take()
                else:self.take()
                if len(stack)>100:raise NotebookGateError("Notebook nesting too deep")
            return
        if not c:raise NotebookGateError("Truncated JSON primitive")
        count=0
        while self.peek() and self.peek() not in ",]}\n\r\t ":
            self.take();count+=1
            if count>100:raise NotebookGateError("Malformed JSON primitive")
    def source(self):
        self.ws()
        if self.peek()=='"':return self.string()
        self.expect("[")
        fragments=[]
        while True:
            self.ws()
            if self.peek()=="]":self.take();break
            fragments.append(self.string())
            require(sum(map(len,fragments))<=MAX_SOURCE_CHARS_PER_FILE,
                    "Notebook code cell source too large")
            self.ws()
            c=self.take()
            if c=="]":break
            if c!=",":raise NotebookGateError("Malformed source array")
        return ''.join(fragments)
    def code_cells(self):
        self.expect("{")
        found=False
        sources=[]
        while True:
            self.ws()
            if self.peek()=="}":self.take();break
            key=self.string();self.expect(":")
            if key=="cells":
                require(not found,"Duplicate top-level cells")
                found=True
                self.expect("[")
                while True:
                    self.ws()
                    if self.peek()=="]":self.take();break
                    self.expect("{")
                    cell_type=None
                    src=""
                    while True:
                        self.ws()
                        if self.peek()=="}":self.take();break
                        key=self.string();self.expect(":")
                        if key=="cell_type":cell_type=self.string()
                        elif key=="source":src=self.source()
                        else:self.skip_value()
                        self.ws()
                        sep=self.take()
                        if sep=="}":break
                        if sep!=",":raise NotebookGateError("Malformed cell object")
                    if cell_type=="code":sources.append(src)
                    require(len(sources)<=MAX_CELLS,"Too many notebook code cells")
                    self.ws()
                    sep=self.take()
                    if sep=="]":break
                    if sep!=",":raise NotebookGateError("Malformed cells array")
            else:self.skip_value()
            self.ws()
            sep=self.take()
            if sep=="}":break
            if sep!=",":raise NotebookGateError("Malformed notebook top-level object")
        require(found,"Not a notebook with cells")
        self.ws()
        require(self.peek()=="","Notebook trailing payload")
        return sources

def _get_call_names(tree):
    out=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            f=n.func
            out.add(f.attr if isinstance(f,ast.Attribute) else f.id if isinstance(f,ast.Name) else "")
    return out

def inspect_notebook(file:Path)->dict:
    # SHA streams raw bytes; does not deserialize any notebook output.
    h=hashlib.sha256()
    with file.open("rb") as f:
        while True:
            part=f.read(1024*1024)
            if not part:break
            h.update(part)
    with file.open("r",encoding="utf-8") as f:
        code=StreamingNotebook(f).code_cells()
    target_counts={k:0 for k in TARGET_FILES}
    direct={k:0 for k in TARGET_FILES}
    dynamic=0
    target_related=0
    for cell in code:
        if len(cell)>MAX_SOURCE_CHARS_PER_FILE:
            raise NotebookGateError("Notebook cell source too large")
        named=[k for k,filename in TARGET_FILES.items() if filename in cell]
        for name in named:target_counts[name]+=1
        target_related+=int(bool(named))
        if not cell.strip():continue
        try:tree=ast.parse(cell)
        except SyntaxError:continue
        calls=_get_call_names(tree)
        for name in named:
            if _direct_target_writer(tree,TARGET_FILES[name]):direct[name]+=1
        if ("target_model" in cell or "holdout" in cell or "probabilistic" in cell):
            if ({"to_pickle","dump","save"} & calls) and not any(direct.values()):
                dynamic+=1
    return {
      "notebook_sha256":h.hexdigest(),
      "code_cells_scanned":len(code),
      "exact_target_filename_code_cell_counts":target_counts,
      "direct_exact_target_write_code_cell_counts":direct,
      "possible_dynamic_target_writer_cells":dynamic,
      "target_filename_code_cells":target_related,
      "no_original_target_values_read_by_code":True,
      "notebook_outputs_json_decoded":False,
      "original_archive_producer_execution_proven":False,
      "train_transform_compatibility_proven":False,
    }

def scan(root:Path)->dict:
    require(root.is_dir() and not root.is_symlink(),"Original notebook root missing/unsafe")
    entries=[]
    total=0
    size_sum=0
    skipped=0
    excluded={".git",".venv","venv","__pycache__","node_modules","Outputs","output",
              "outputs","results","Results","local_data","price_cache_fmp_pickle"}
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[z for z in sorted(dirs) if z not in excluded and
                 not z.startswith(".") and not (Path(base)/z).is_symlink()]
        for name in sorted(files):
            if not name.endswith(".ipynb"):continue
            p=Path(base)/name
            if not p.is_file() or p.is_symlink():continue
            total+=1
            require(total<=MAX_NOTEBOOKS,"Notebook count exceeds bounded scope")
            size=p.stat().st_size
            if size>MAX_BYTES_PER_NOTEBOOK:
                skipped+=1;continue
            size_sum+=size
            require(size_sum<=MAX_TOTAL_NOTEBOOK_BYTES,"Original notebook byte cap exceeded")
            item=inspect_notebook(p)
            item["relative_notebook_path"]=p.relative_to(root).as_posix()
            entries.append(item)
    direct=sum(sum(x["direct_exact_target_write_code_cell_counts"].values()) for x in entries)
    dynamic=sum(x["possible_dynamic_target_writer_cells"] for x in entries)
    references=sum(sum(x["exact_target_filename_code_cell_counts"].values()) for x in entries)
    status=("G57C_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY" if direct
            else "G57C_NOTEBOOK_DYNAMIC_WRITER_LEADS_ONLY" if dynamic
            else "G57C_NOTEBOOK_TARGET_REFERENCES_ONLY" if references
            else "G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS")
    return {
        "schema_version":"dtrm.ic.g5_7c.notebook_code_streaming_source.v0",
        "status":status,
        "original_g57b_sha256":G57B_SHA,
        "notebooks_enumerated":total,
        "notebooks_scanned":len(entries),
        "oversize_skipped":skipped,
        "scanned_bytes":size_sum,
        "notebooks":entries,
        "code_only_notebook_inspection_authorized":True,
        "notebook_execution":False,
        "outputs_deserialized_or_saved":False,
        "financial_pickle_or_csv_opened":False,
        "june_target_producer_execution_proven":False,
        "train_transform_compatibility_proven":False,
        "old_v2_v3_v4_target_outcome_access_authorized":False,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--g57b-original-report",type=Path,required=True)
    p.add_argument("--original-notebooks-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--authorize-notebook-code-inspection",action="store_true")
    a=p.parse_args()
    require(a.authorize_notebook_code_inspection,
            "Explicit owner approval for opening original notebook JSON code cells required")
    old=a.g57b_original_report.expanduser()
    require(old.is_file() and not old.is_symlink(),"G5.7b original report missing/unsafe")
    digest=hashlib.sha256(old.read_bytes()).hexdigest()
    require(digest==G57B_SHA,"Original G5.7b report SHA mismatch")
    data=json.loads(old.read_text(encoding="utf-8"))
    require(data.get("status")=="G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE"
        and data.get("original_v2_v3_v4_pickle_files_opened") is False
        and data.get("v2_v3_v4_label_transform_compatibility_proven") is False,
        "G5.7b original no-outcome safety state drift")
    out=a.out.expanduser()
    require(not out.exists(),"Never overwrite historical lineage report")
    report=scan(a.original_notebooks_root.expanduser())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(report["status"])
    print("NOTEBOOKS_SCANNED="+str(report["notebooks_scanned"]))
    print("OVERSIZE_SKIPPED="+str(report["oversize_skipped"]))
    print("NOTEBOOK_CODE_EXECUTED=NO")
    print("NOTEBOOK_OUTPUTS_DESERIALIZED=NO")
    print("OLD_V2_V3_V4_TARGET_PICKLES_ACCESSED=NO")
    for z in report["notebooks"]:
        if (sum(z["exact_target_filename_code_cell_counts"].values()) or
            z["possible_dynamic_target_writer_cells"]):
            print("CODE_LEAD="+z["relative_notebook_path"]+
                " EXACT_WRITES="+str(sum(z["direct_exact_target_write_code_cell_counts"].values()))+
                " DYNAMIC_WRITER_CELLS="+str(z["possible_dynamic_target_writer_cells"])+
                " EXACT_REFERENCES="+str(sum(z["exact_target_filename_code_cell_counts"].values())))
    print("LABEL_TRANSFORM_COMPATIBILITY=NOT_ESTABLISHED")

if __name__=="__main__":
    main()
