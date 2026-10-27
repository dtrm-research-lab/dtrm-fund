#!/usr/bin/env python3
"""IC G1.2l historical raw-to-selected lineage, SOURCE FILES ONLY.

Scans local existing source-code and metadata text files for references
to original 2026-06-06 265145/40320 pair pipeline; never loads
Pickles, CSV data, notebook contents, outcomes, prices, embeddings,
or any model. Reports only relative source path, reference category,
line numbers and source SHA256; never reports source lines or secrets.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

MATCH = {
    "raw_pair_exact_filename": re.compile(r"pairs_raw_2025-01-01_2026-06-06", re.I),
    "raw_pair_generic": re.compile(r"pairs_raw|raw_pairs|raw_pair", re.I),
    "v1_holdout_identifiers": re.compile(r"probabilistic_v1_holdout|probabilistic_v1_embedding_manifest", re.I),
    "old_news_snapshot": re.compile(r"news_2025-01-01_2026-06-06", re.I),
    "explicit_V1_sample_size": re.compile(r"\b40320\b|40,320|40_320", re.I),
    "raw_candidate_sample_size": re.compile(r"\b265145\b|265,145|265_145", re.I),
    "pair_generation_ops": re.compile(r"explode\(|merge\(|join\(|groupby\(|drop_duplicates\(|isin\(|pairs\.append|pair_rows", re.I),
}
CODE_EXT = {".py",".sh",".md",".yaml",".yml",".toml",".sql"}
PRUNE = {".git",".venv","venv","node_modules","__pycache__",".pytest_cache",
         ".mypy_cache",".cache","dist","build","site-packages",
         ".next","Library","Downloads",".Trash"}
MAX_TEXT_BYTES=2_000_000
MAX_HITS_PER_CATEGORY=1000

def digest(p: Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--search-root",action="append",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out).expanduser()
    if out.exists():
        ap.error("Refusing to overwrite existing lineage-discovery report")
    roots=[Path(x).expanduser().resolve() for x in args.search_root]
    report={
        "schema_version":"dtrm.ic.g1.raw_source_lineage_search.v1",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "scope":"Source-only reference search; no scientific data or notebooks read",
        "search_roots":[{"ordinal":i+1,"exists":root.is_dir()} for i,root in enumerate(roots)],
        "text_code_files_scanned":0,
        "notebook_file_names_only":[],
        "references":[],
        "file_errors":0,
        "large_code_files_skipped":0,
        "match_counts":{x:0 for x in MATCH},
        "raw_data_opened":False,
        "notebook_contents_read":False,
        "outcome_targets_inspected":False,
        "new_holdout_authorized":False,
    }
    seen=set()
    for j,root in enumerate(roots):
        if not root.is_dir():
            continue
        for base,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=[d for d in dirs if d not in PRUNE and
                     not (Path(base)/d).is_symlink()]
            for filename in files:
                path=Path(base)/filename
                if path.is_symlink() or not path.is_file():
                    continue
                try:
                    st=path.stat()
                except OSError:
                    report["file_errors"]+=1
                    continue
                identity=(st.st_dev,st.st_ino)
                if identity in seen:
                    continue
                seen.add(identity)
                if path.suffix.lower()==".ipynb":
                    if len(report["notebook_file_names_only"])<150:
                        report["notebook_file_names_only"].append({
                            "root_ordinal":j+1,
                            "relative_path":str(path.relative_to(root)),
                            "bytes":st.st_size,
                        })
                    continue
                if path.suffix.lower() not in CODE_EXT:
                    continue
                if st.st_size>MAX_TEXT_BYTES:
                    report["large_code_files_skipped"]+=1
                    continue
                try:
                    lines=path.read_text(encoding="utf-8").splitlines()
                except (OSError,UnicodeError):
                    report["file_errors"]+=1
                    continue
                report["text_code_files_scanned"]+=1
                matched={}
                for line_number,line in enumerate(lines,1):
                    for key,pattern in MATCH.items():
                        if pattern.search(line):
                            report["match_counts"][key]+=1
                            if len(matched.get(key,[]))<20:
                                matched.setdefault(key,[]).append(line_number)
                # Keep a code file if it contains a named historical
                # V1 event/source reference. Generic pair ops alone
                # would produce overwhelming irrelevant results.
                strong=(set(matched)-
                        {"pair_generation_ops","raw_pair_generic"})
                if strong or ("raw_pair_generic" in matched and
                              "pair_generation_ops" in matched):
                    report["references"].append({
                        "root_ordinal":j+1,
                        "relative_source_file":str(path.relative_to(root)),
                        "sha256_source_code_only":digest(path),
                        "matched_reference_categories":matched,
                    })
    report["references"].sort(key=lambda row:(
        not ("raw_pair_exact_filename" in row["matched_reference_categories"]),
        not ("v1_holdout_identifiers" in row["matched_reference_categories"]),
        row["root_ordinal"],row["relative_source_file"],
    ))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2l: SOURCE_LINEAGE_REFERENCE_INVENTORY_ONLY")
    print("Source/text files scanned:",report["text_code_files_scanned"])
    print("Potential historical lineage source files:",len(report["references"]))
    print("Notebook filenames inventoried, not opened:",len(report["notebook_file_names_only"]))
    for row in report["references"][:35]:
        print(f" root{row['root_ordinal']}:{row['relative_source_file']}",
              "refs:",{k:v for k,v in row["matched_reference_categories"].items()
                       if k!="pair_generation_ops"})
    print("Report:",out)
    print("No model inference; no scientific data/news/pickle/notebook content or outcomes opened.")
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"G1.2l halted: {type(e).__name__}: {e}",file=sys.stderr)
        sys.exit(3)
