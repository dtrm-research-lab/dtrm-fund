#!/usr/bin/env python3
"""G1.2h: historical V1 embedding-cache provenance/coverage inventory.

Read-only trusted *historical* manifest, V1 signals, cache shape/index
Pickles, and supplement schema. The float32 embedding .dat bytes are only
hashed and size-checked; NO embedding values, targets, prices, returns,
newer news, or model predictions are inspected.

The report has aggregate counts, source labels and SHA256 values only.
This is a schema preflight; it never authorizes a new experiment.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import numbers
from pathlib import Path
import pickle
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
MANIFEST_NAME = "probabilistic_v1_embedding_manifest_2026-06-06.pkl"
SIGNALS_NAME = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
SUPPLEMENT_NAME = "probabilistic_v1_missing_embeddings_2026-06-06.pkl"
ORIGINAL_SIGNALS_SHA = "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b"
REQUIRED_LABEL_COUNTS = sorted((4764,735,27))
CACHE_DATES = ("2026-06-06","2026-05-23")
CACHE_PREFIX = "news_emb"
MAX_GROUPS = 20

def sha256(path: Path) -> str:
    dig=hashlib.sha256()
    with path.open("rb") as reader:
        for block in iter(lambda: reader.read(1024*1024), b""):
            dig.update(block)
    return dig.hexdigest()

def structural_pickle(path: Path):
    import pandas as pd
    # Explicit user authorization and trusted local research source only.
    obj=pd.read_pickle(path)
    structure={
        "pickle_type":type(obj).__name__,
        "file_bytes":path.stat().st_size,
        "file_sha256_new_local_anchor":sha256(path),
    }
    ids=None
    if isinstance(obj,pd.DataFrame):
        structure["rows"]=len(obj)
        structure["columns"]=[str(x) for x in obj.columns]
        if "news_id" in obj:
            ids=pd.Index(obj["news_id"])
            structure["news_id_present"]=True
            structure["distinct_news_ids"]=int(ids.nunique())
            structure["duplicate_news_ids"]=int(ids.duplicated().sum())
            structure["news_id_dtype"]=str(ids.dtype)
        else:
            structure["news_id_present"]=False
        for name in obj.columns:
            if "embed" in str(name).lower():
                structure.setdefault("embedding_column_types",{})[str(name)]=str(obj[name].dtype)
    elif isinstance(obj,pd.Series):
        structure["rows"]=len(obj)
        structure["index_type"]=type(obj.index).__name__
        if obj.index.is_unique:
            ids=obj.index
            structure["news_id_possible_index"]=True
    elif isinstance(obj,dict):
        structure["entries"]=len(obj)
        structure["key_type_counts"]=dict(Counter(type(x).__name__ for x in obj))
        ids=pd.Index(list(obj))
        structure["news_id_possible_dictionary_keys"]=True
        structure["value_type_counts"]=dict(Counter(type(x).__name__ for x in obj.values()))
    else:
        structure["shape"]=list(obj.shape) if hasattr(obj,"shape") else None
    return obj, structure, ids

def load_index(path: Path, shape_path: Path, binary: Path):
    with path.open("rb") as index_pickle:
        idx=pickle.load(index_pickle)
    with shape_path.open("rb") as shape_pickle:
        shape=pickle.load(shape_pickle)
    if not isinstance(idx,dict):
        raise RuntimeError("Historical cache index is not a dictionary")
    if not isinstance(shape,(tuple,list)) or len(shape)!=2:
        raise RuntimeError("Historical cache shape is invalid")
    dim=list(shape)
    if dim[1]!=384 or dim[0]<=0:
        raise RuntimeError("Historical cache is not a positive Nx384 matrix")
    if binary.stat().st_size != dim[0]*384*4:
        raise RuntimeError("Historical embedding binary byte size != Nx384×float32")
    indices=list(idx.values())
    if not all(isinstance(x,numbers.Integral) and 0<=x<dim[0] for x in indices):
        raise RuntimeError("Historical cache indices not zero-based integer row offsets")
    if len(set(indices))!=len(indices):
        raise RuntimeError("Historical cache index has duplicated row offsets")
    record={
        "shape":dim,
        "index_entries":len(idx),
        "index_key_type_counts":dict(Counter(type(x).__name__ for x in idx)),
        "bytes":binary.stat().st_size,
        "sha256_new_local_anchor":{
            "dat":sha256(binary), "index":sha256(path), "shape":sha256(shape_path)
        }
    }
    return idx,record

def main() -> int:
    import pandas as pd
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-local-data",required=True)
    parser.add_argument("--historical-outputs",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--trust-historical-pickles",action="store_true")
    args=parser.parse_args()
    if not args.trust_historical_pickles:
        parser.error("Requires explicit trust for original historical local Pickles")
    out=Path(args.out).expanduser()
    if out.exists():
        parser.error("Refusing to overwrite a previous G1.2h audit")
    root=Path(args.historical_local_data).expanduser()
    outputs=Path(args.historical_outputs).expanduser()
    sig_path=root/SIGNALS_NAME
    manifest_path=root/MANIFEST_NAME
    supplement_path=root/SUPPLEMENT_NAME
    for p in (sig_path,manifest_path,supplement_path):
        if not p.is_file() or p.is_symlink():
            raise RuntimeError("Historical V1 artifact unavailable: "+p.name)
    if sha256(sig_path)!=ORIGINAL_SIGNALS_SHA:
        raise RuntimeError("Historical V1 signal hash mismatch")

    signals=pd.read_pickle(sig_path)
    manifest,manifest_info,_=structural_pickle(manifest_path)
    supplement,supplement_info,supplement_ids=structural_pickle(supplement_path)
    if not isinstance(signals,pd.DataFrame) or len(signals)!=40320:
        raise RuntimeError("Historic signal pairs no longer match 40320")
    if not isinstance(manifest,pd.DataFrame):
        raise RuntimeError("Historic source manifest is not a DataFrame")
    cols={"news_id","embedding_source","date_dt"}
    if not cols.issubset(manifest.columns):
        raise RuntimeError("Original embedding manifest required columns missing")
    if manifest["news_id"].isna().any() or manifest["news_id"].duplicated().any():
        raise RuntimeError("Original manifest news identifiers are null or duplicate")
    news=pd.Index(signals["news_id"].unique())
    manifest_ids=pd.Index(manifest["news_id"])
    if news.isna().any():
        raise RuntimeError("Original signals missing news identifiers")
    missing=int((~news.isin(manifest_ids)).sum())
    additional=int((~manifest_ids.isin(news)).sum())
    if manifest["embedding_source"].isna().any():
        raise RuntimeError("Original manifest source label missing")
    count_map={
        str(x):int(n)
        for x,n in manifest["embedding_source"].value_counts(dropna=False).items()
    }
    if len(count_map)>MAX_GROUPS:
        raise RuntimeError("Original manifest unexpectedly many source labels")
    cache_records={}
    cache_indices={}
    for suffix in CACHE_DATES:
        dat=outputs/f"{CACHE_PREFIX}_2025-01-01_{suffix}.dat"
        idx=outputs/f"{CACHE_PREFIX}_index_2025-01-01_{suffix}.pkl"
        shape=outputs/f"{CACHE_PREFIX}_shape_2025-01-01_{suffix}.pkl"
        for p in (dat,idx,shape):
            if not p.is_file() or p.is_symlink():
                raise RuntimeError("Original embedding cache component missing: "+p.name)
        cache_indices[suffix],cache_records[suffix]=load_index(idx,shape,dat)

    overlap={}
    for label,group in manifest.groupby("embedding_source",sort=True):
        ids=list(group["news_id"])
        membership={
            suffix:int(sum(x in cache_indices[suffix] for x in ids))
            for suffix in CACHE_DATES
        }
        if supplement_ids is not None:
            lookup=set(supplement_ids)
            membership["supplement_structural_id_matches"]=int(sum(x in lookup for x in ids))
        overlap[str(label)]={
            "manifest_news":len(ids),
            "membership_counts_by_cache":membership,
        }

    contract_groups_valid=sorted(count_map.values())==REQUIRED_LABEL_COUNTS
    manifest_count=len(manifest)==5526
    source_rows_match=missing==0 and additional==0
    status=(
        "G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED"
        if manifest_count and contract_groups_valid and source_rows_match
        else "G1_2H_MANIFEST_COVERAGE_OR_LABEL_COUNTS_UNRESOLVED"
    )
    result={
        "schema_version":"dtrm.ic.g1.embedding_source_inventory.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "historical_training_commit":PIN,
        "status":status,
        "frozen_signals_sha256_verified":True,
        "frozen_signal_rows":len(signals),
        "unique_signal_news_ids":len(news),
        "manifest_structure":manifest_info,
        "manifest_missing_signal_news":missing,
        "manifest_additional_news":additional,
        "manifest_exact_labels_and_counts":count_map,
        "original_contract_count_multiset_matches":contract_groups_valid,
        "historical_caches":cache_records,
        "manifest_source_overlap_with_caches":overlap,
        "historical_supplement_structure":supplement_info,
        "all_384_embedding_feature_coordinates_reproduced":False,
        "frozen_feature_row_mapping_certified":False,
        "independent_temporal_evaluation_approved":False,
        "limitations":[
            "The source labels must explicitly determine the source cache, not best matching vectors.",
            "The supplement representation and mapping are not assumed from its filename.",
            "Original cache hashes are newly observed local commitments, not independent historical precommits.",
            "The V1 raw-pair filename/40320-vs-265145 contract discrepancy remains unresolved.",
            "No model inference, financial outcomes or prospective news/returns accessed.",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2h:",status)
    print("Original signal news:",len(news),"; manifest:",len(manifest))
    print("Manifest misses:",missing,"; additions:",additional)
    print("Source labels and counts:",count_map)
    for suffix,info in cache_records.items():
        print("Embedding cache",suffix,":",info["shape"],"; index entries",info["index_entries"],
              "; key types:",info["index_key_type_counts"])
    print("Supplement:",supplement_info)
    print("Manifest source coverage in original caches:")
    for label,info in overlap.items():
        print(" ",label,info)
    print("Report:",out)
    print("No embedding vectors, model predictions, financial targets or returns inspected")
    return 0 if status.startswith("G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS") else 2

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G1.2h stopped: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
