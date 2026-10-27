#!/usr/bin/env python3
"""IC G1.2i — original V1 supplement schema audit only.

Trusted historical source metadata inspection, no vector values used or
printed, no predictions, no targets/prices/returns/new observations.
Run only with explicitly trusted original local 2026 research Pickles.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

MANIFEST = "probabilistic_v1_embedding_manifest_2026-06-06.pkl"
SUPPLEMENT = "probabilistic_v1_missing_embeddings_2026-06-06.pkl"
MANIFEST_SHA = "3c74994a08384ea009af36b4cf3bcef592c95a06daf2d9889b3eaef79b24e52e"
SUPPLEMENT_SHA = "1697fc009800b673edda43ede18373f96916934d05cc03f50d16363b19d118d3"
NEWS_ID_FIELD_NAMES = {"news_ids", "missing_news_ids", "ids", "missing_ids"}
VECTOR_FIELD_NAMES = {"embeddings", "vectors", "missing_embeddings", "missing_vectors"}
EXPECTED_SUPPLEMENT_ROWS = 27

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for piece in iter(lambda:handle.read(1024*1024), b""):
            h.update(piece)
    return h.hexdigest()

def describe(name, value):
    import numpy as np
    r={"name":name, "python_type":type(value).__name__}
    if isinstance(value,np.ndarray):
        r.update({"shape":list(value.shape), "dtype":str(value.dtype),
                  "ndim":int(value.ndim)})
    elif isinstance(value,(tuple,list)):
        r["length"]=len(value)
        r["element_python_type_counts"]=dict(sorted(Counter(
            type(x).__name__ for x in value
        ).items()))
        if len(value):
            first=value[0]
            if isinstance(first,np.ndarray):
                r["first_element_shape"]=list(first.shape)
                r["first_element_dtype"]=str(first.dtype)
    elif isinstance(value,str):
        r["string_length"]=len(value)
    # Explicitly do not output any values, IDs, text, or vector elements.
    return r

def main():
    import pandas as pd
    import numpy as np

    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-local-data",required=True)
    parser.add_argument("--embedding-inventory",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--trust-historical-pickles",action="store_true")
    args=parser.parse_args()
    if not args.trust_historical_pickles:
        parser.error("Requires explicit trust of original historical local Pickles")
    out=Path(args.out).expanduser()
    if out.exists():
        parser.error("Refusing to overwrite existing supplement audit")
    previous=json.loads(Path(args.embedding_inventory).expanduser().read_text(encoding="utf-8"))
    if previous.get("schema_version")!="dtrm.ic.g1.embedding_source_inventory.v1":
        raise RuntimeError("G1.2h report schema mismatch")
    if previous.get("status")!="G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED":
        raise RuntimeError("G1.2h did not reach source inventory PASS")
    root=Path(args.historical_local_data).expanduser()
    manifest_path=root/MANIFEST
    supplement_path=root/SUPPLEMENT
    for path,oldhash in ((manifest_path,MANIFEST_SHA),(supplement_path,SUPPLEMENT_SHA)):
        if path.is_symlink() or not path.is_file() or digest(path)!=oldhash:
            raise RuntimeError("Historical artifact absent or different from G1.2h SHA: "+path.name)
    manifest=pd.read_pickle(manifest_path)
    obj=pd.read_pickle(supplement_path)
    if not isinstance(manifest,pd.DataFrame):
        raise RuntimeError("Original historical embedding manifest not DataFrame")
    if not {"news_id","embedding_source"}.issubset(manifest.columns):
        raise RuntimeError("Original manifest news/source columns missing")
    if manifest["news_id"].isna().any() or manifest["news_id"].duplicated().any():
        raise RuntimeError("Original manifest invalid news identifiers")
    target=manifest.loc[manifest["embedding_source"]=="v1_supplement","news_id"]
    if len(target)!=EXPECTED_SUPPLEMENT_ROWS:
        raise RuntimeError("Historic V1 supplement label count mismatch")
    if not isinstance(obj,dict) or not all(isinstance(k,str) for k in obj):
        raise RuntimeError("Historic V1 supplement expected dictionary with str keys")
    fields=[describe(k,v) for k,v in sorted(obj.items())]
    candidate_ids=[]
    for key,value in sorted(obj.items()):
        if key.lower() not in NEWS_ID_FIELD_NAMES:
            continue
        if not isinstance(value,(tuple,list,np.ndarray)):
            continue
        seq=list(value)
        if not all(isinstance(x,str) for x in seq):
            continue
        idx=pd.Index(seq)
        candidate_ids.append({
            "field":key,
            "identifier_count":len(seq),
            "unique_identifiers":int(idx.nunique()),
            "manifest_supplement_set_equal":bool(
                len(seq)==EXPECTED_SUPPLEMENT_ROWS
                and idx.is_unique and
                len(idx.intersection(pd.Index(target)))==EXPECTED_SUPPLEMENT_ROWS
            ),
        })
    vector_fields=[]
    for key,value in sorted(obj.items()):
        if key.lower() in VECTOR_FIELD_NAMES and isinstance(value,np.ndarray):
            vector_fields.append({
                "field":key, "shape":list(value.shape),
                "dtype":str(value.dtype),
                "shape_27_by_384":list(value.shape)==[27,384],
            })
    could_proceed=any(q["manifest_supplement_set_equal"] for q in candidate_ids) and any(
        q["shape_27_by_384"] for q in vector_fields)
    status=("G1_2I_SUPPLEMENT_NAMED_SCHEMA_READY_FOR_PREDECLARED_MAPPING"
            if could_proceed else "G1_2I_SUPPLEMENT_SCHEMA_NEEDS_EXPLICIT_MAPPING")
    result={
        "schema_version":"dtrm.ic.g1.supplement_structure.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":status,
        "supplement_sha256_matches_prior":True,
        "manifest_sha256_matches_prior":True,
        "supplement_record_type":type(obj).__name__,
        "supplement_fields":fields,
        "manifest_supplement_news_count":len(target),
        "explicitly_named_id_fields":candidate_ids,
        "explicitly_named_vector_fields":vector_fields,
        "recognized_schema_only_ready":bool(could_proceed),
        "vector_values_inspected_or_compared":False,
        "historical_features_reconstructed":False,
        "unseen_holdout_approved":False,
        "warnings":[
            "Six supplement dictionary keys are metadata fields, not six news events.",
            "Supplement must have deterministic explicit news-ID to row mapping.",
            "Historical label chooses cache/supplement, never a similarity search.",
            "Original raw-pair V1 contract 40320 vs local 265145 rows remains unresolved.",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2i:",status)
    print("Manifest news for supplement:",len(target))
    for field in fields:
        print(" Supplement field:",field)
    print(" Explicit ID mapping candidates:",candidate_ids)
    print(" Explicit vector field candidates:",vector_fields)
    print("Report:",out)
    print("No embeddings compared, outcomes/targets/prices or new cohorts opened")
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G1.2i stopped: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(3)
