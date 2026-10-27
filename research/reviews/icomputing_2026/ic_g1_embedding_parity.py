#!/usr/bin/env python3
"""IC G1.2j — historical V1 embedding parity, strictly source-directed.

Read-only 2026-06-06 V1 signal/feature/manifest, two 2026 embedding
cache families and the original 27-news supplement. Each news_id uses
exactly its declared source, never a closest-vector search. No
prices, financial targets, returns, newer cohort, or model inference.
The old local Pickles MUST be operator-trusted.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pickle
import sys

PIN = "c7502a690162459cdfb3413573e3133c42efb126"
SIGNALS = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
FEATURES = "probabilistic_v1_holdout_features_2026-06-06.npy"
MANIFEST = "probabilistic_v1_embedding_manifest_2026-06-06.pkl"
SUPPLEMENT = "probabilistic_v1_missing_embeddings_2026-06-06.pkl"
SIGNAL_SHA = "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b"
FEATURE_SHA = "a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750"
SOURCE_COUNTS = {"2026-06-06":4764,"2026-05-23":735,"v1_supplement":27}
ROWS, DIM = 40320, 384
TOL = 1e-6

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_file(root: Path, name: str) -> Path:
    path=root/name
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("Required original historical file unavailable: "+name)
    return path

def json_gate(path: Path, schema: str, status: str) -> dict:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version")!=schema or obj.get("status")!=status:
        raise RuntimeError("Original historical predecessor audit not PASS: "+path.name)
    return obj

def load_cache(root: Path, suffix: str, previous: dict):
    import numpy as np
    dat=safe_file(root,f"news_emb_2025-01-01_{suffix}.dat")
    index_file=safe_file(root,f"news_emb_index_2025-01-01_{suffix}.pkl")
    shape_file=safe_file(root,f"news_emb_shape_2025-01-01_{suffix}.pkl")
    original=previous["historical_caches"][suffix]
    for key,path in (("dat",dat),("index",index_file),("shape",shape_file)):
        if sha256(path)!=original["sha256_new_local_anchor"][key]:
            raise RuntimeError("Cache has changed since G1.2h: "+suffix+"/"+key)
    with index_file.open("rb") as f:
        index=pickle.load(f)
    with shape_file.open("rb") as f:
        shape=pickle.load(f)
    if not isinstance(index,dict) or not isinstance(shape,(tuple,list)):
        raise RuntimeError("Original embedding cache index/shape schema mismatch")
    if list(shape)!=original["shape"] or len(index)!=original["index_entries"]:
        raise RuntimeError("Original cache dimensions/index changed")
    if len(shape)!=2 or shape[1]!=DIM or dat.stat().st_size!=int(shape[0])*DIM*4:
        raise RuntimeError("Original cache .dat dimensions invalid")
    import numbers
    if not all(isinstance(k,str) and isinstance(v,numbers.Integral)
               and 0<=int(v)<int(shape[0]) for k,v in index.items()):
        raise RuntimeError("Original source index offsets/IDs malformed")
    if len({int(v) for v in index.values()})!=len(index):
        raise RuntimeError("Original source cache offsets duplicated")
    mem=np.memmap(dat,dtype=np.float32,mode="r",shape=tuple(shape))
    return index,mem

def compare(source_data, original):
    import numpy as np
    x=np.asarray(source_data,dtype=np.float32)
    y=np.asarray(original,dtype=np.float32)
    if x.shape!=y.shape or x.ndim!=2 or x.shape[1]!=DIM:
        raise RuntimeError("Aligned original embedding group dimensions differ")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise RuntimeError("Nonfinite historical vectors")
    abs_diff=np.abs(x.astype(np.float64)-y.astype(np.float64))
    return {
        "rows":int(x.shape[0]),
        "coordinates":int(x.size),
        "max_abs_difference":float(abs_diff.max()),
        "mean_abs_difference":float(abs_diff.mean()),
        "rows_exceeding_1e_6":int(np.count_nonzero(np.any(abs_diff>TOL,axis=1))),
        "coordinates_exceeding_1e_6":int(np.count_nonzero(abs_diff>TOL)),
        "coordinates_bitwise_equal":int(np.count_nonzero(x==y)),
        "tolerance_pass":bool(np.all(abs_diff<=TOL)),
    }

def main():
    import numpy as np
    import pandas as pd

    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-local-data",required=True)
    parser.add_argument("--historical-outputs",required=True)
    parser.add_argument("--embedding-inventory",required=True)
    parser.add_argument("--supplement-schema",required=True)
    parser.add_argument("--beta-provenance",required=True)
    parser.add_argument("--text-provenance",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--trust-historical-pickles",action="store_true")
    args=parser.parse_args()
    if not args.trust_historical_pickles:
        parser.error("Only locally trusted original research Pickles may be loaded")
    out=Path(args.out).expanduser()
    if out.exists():
        parser.error("Refusing to overwrite an existing audit")
    folder=Path(args.historical_local_data).expanduser()
    old=Path(args.historical_outputs).expanduser()
    h=json_gate(Path(args.embedding_inventory).expanduser(),
        "dtrm.ic.g1.embedding_source_inventory.v1",
        "G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED")
    i=json_gate(Path(args.supplement_schema).expanduser(),
        "dtrm.ic.g1.supplement_structure.v1",
        "G1_2I_SUPPLEMENT_NAMED_SCHEMA_READY_FOR_PREDECLARED_MAPPING")
    f=json_gate(Path(args.beta_provenance).expanduser(),
        "dtrm.ic.g1.feature_provenance_structure.v1",
        "HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN")
    g=json_gate(Path(args.text_provenance).expanduser(),
        "dtrm.ic.g1.text_five_provenance.v1",
        "TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN")
    if not f.get("beta_to_feature_column390",{}).get("matching_all_40320"):
        raise RuntimeError("Original keyed beta parity not established")
    if g.get("rows_exceeding_1e_6")!=0 or g.get("max_abs_difference")!=0.0:
        raise RuntimeError("Original five text features did not match exactly")
    if h.get("historical_training_commit")!=PIN:
        raise RuntimeError("Original training commit inconsistent")

    signal_path=safe_file(folder,SIGNALS)
    features_path=safe_file(folder,FEATURES)
    manifest_path=safe_file(folder,MANIFEST)
    supplement_path=safe_file(folder,SUPPLEMENT)
    for name,p,expected in (
        ("signals",signal_path,SIGNAL_SHA),
        ("features",features_path,FEATURE_SHA),
        ("manifest",manifest_path,h["manifest_structure"]["file_sha256_new_local_anchor"]),
        ("supplement",supplement_path,h["historical_supplement_structure"]["file_sha256_new_local_anchor"]),
    ):
        if sha256(p)!=expected:
            raise RuntimeError("Original historical file changed: "+name)
    if i.get("recognized_schema_only_ready") is not True:
        raise RuntimeError("Supplement source mapping was not approved by G1.2i")

    sig=pd.read_pickle(signal_path)
    manifest=pd.read_pickle(manifest_path)
    sup=pd.read_pickle(supplement_path)
    X=np.load(features_path,allow_pickle=False)
    if not isinstance(sig,pd.DataFrame) or not isinstance(manifest,pd.DataFrame):
        raise RuntimeError("Original signal or manifest type invalid")
    if X.shape!=(ROWS,390) or len(sig)!=ROWS or len(manifest)!=5526:
        raise RuntimeError("Original V1 dimension/count commitments missing")
    if not {"news_id","embedding_source","date_dt"}.issubset(manifest.columns):
        raise RuntimeError("Original manifest source fields missing")
    if sig["news_id"].isna().any() or manifest["news_id"].isna().any():
        raise RuntimeError("Original news identifiers null")
    if manifest["news_id"].duplicated().any():
        raise RuntimeError("Original manifest news identifiers duplicated")
    groups=manifest["embedding_source"].value_counts().to_dict()
    if groups!=SOURCE_COUNTS:
        raise RuntimeError("Original 4764/735/27 source labels changed")
    unique_ids=pd.Index(sig["news_id"].unique())
    if len(unique_ids)!=5526 or not unique_ids.isin(manifest["news_id"]).all():
        raise RuntimeError("Original 5526 historic signal identifiers not represented")
    mapping=manifest.set_index("news_id")["embedding_source"]
    labels=mapping.reindex(sig["news_id"]).to_numpy()
    if len(labels)!=ROWS or pd.isna(labels).any():
        raise RuntimeError("Unresolved original row-wise source label mapping")
    if not isinstance(sup,dict) or "news_ids" not in sup or "embeddings" not in sup:
        raise RuntimeError("Original supplement lacks declared ID/vector fields")
    sup_ids=sup["news_ids"]
    sup_vectors=sup["embeddings"]
    if not isinstance(sup_ids,list) or not all(isinstance(z,str) for z in sup_ids):
        raise RuntimeError("Supplement original ID vector keys invalid")
    if not isinstance(sup_vectors,np.ndarray) or sup_vectors.shape!=(27,DIM) or sup_vectors.dtype!=np.float32:
        raise RuntimeError("Supplement vectors not 27×384 float32")
    if len(sup_ids)!=27 or len(set(sup_ids))!=27:
        raise RuntimeError("Supplement source ID cardinality/uniqueness mismatch")
    if set(sup_ids)!=set(manifest.loc[manifest["embedding_source"]=="v1_supplement","news_id"]):
        raise RuntimeError("Supplement news IDs not exactly the manifest source group")
    if sup.get("model")!="all-MiniLM-L6-v2" or sup.get("dtype")!="float32":
        raise RuntimeError("Original supplement embedding model or dtype does not match contract")
    if sup.get("max_chars")!=1600 or sup.get("normalize_embeddings") is not True:
        raise RuntimeError("Original supplement model input normalization contract mismatch")
    if not np.isfinite(sup_vectors).all():
        raise RuntimeError("Nonfinite original supplement vectors")
    sup_pos={key:j for j,key in enumerate(sup_ids)}

    expected=np.asarray(X[:,:DIM],dtype=np.float32)
    rebuilt=np.empty((ROWS,DIM),dtype=np.float32)
    covered=np.zeros(ROWS,dtype=bool)
    by_source={}
    for source in ("2026-06-06","2026-05-23","v1_supplement"):
        selected=np.flatnonzero(labels==source)
        ids=sig["news_id"].iloc[selected].tolist()
        if not len(selected):
            raise RuntimeError("Empty historic source group: "+source)
        if source=="v1_supplement":
            missing=[n for n in ids if n not in sup_pos]
            if missing:
                raise RuntimeError("Supplement source missing historical manifest news")
            indices=np.asarray([sup_pos[n] for n in ids],dtype=np.int64)
            rebuilt[selected]=sup_vectors[indices]
        else:
            index,cache=load_cache(old,source,h)
            missing=[n for n in ids if n not in index]
            if missing:
                raise RuntimeError("Manifest-assigned historic cache has missing event IDs")
            indices=np.asarray([int(index[n]) for n in ids],dtype=np.int64)
            rebuilt[selected]=cache[indices]
        covered[selected]=True
        by_source[source]=compare(rebuilt[selected],expected[selected])
        by_source[source]["unique_manifest_news"]=int(SOURCE_COUNTS[source])
    if not covered.all() or int(covered.sum())!=ROWS:
        raise RuntimeError("Some V1 feature rows were not reconstructed")
    total=compare(rebuilt,expected)
    status=("G1_2J_HISTORICAL_384_EMBEDDING_ROW_PARITY_PASS"
            if total["tolerance_pass"] and all(v["tolerance_pass"] for v in by_source.values())
            else "G1_2J_HISTORICAL_EMBEDDING_VALUES_MISMATCH")
    result={
        "schema_version":"dtrm.ic.g1.embedding_row_parity.v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":status,
        "frozen_training_commit":PIN,
        "source_mapping_rule":"Original V1 manifest embedding_source label only; no nearest-vector search or cache reassignment",
        "manifest_5526_all_news_ids_resolved":True,
        "source_counts_unique_news":SOURCE_COUNTS,
        "historic_signal_rows":ROWS,
        "embedding_dimensions":DIM,
        "historic_precommitted_features_sha256_verified":True,
        "historic_precommitted_signals_sha256_verified":True,
        "local_h_i_f_g_audit_hashes_and_pass_states_verified":True,
        "per_source_row_parity":by_source,
        "all_40320x384_parity":total,
        "full_390_numeric_input_parity_supported_by_prior_f_g":bool(total["tolerance_pass"]),
        "original_filter_rule_recovered":False,
        "unseen_cohort_approved":False,
        "limitations":[
            "Source cache/manifest/supplement hashes were only committed in the current local retrospective audit, unlike original V1 features/signals.",
            "Matching historic matrix is not proof of untouched new temporal performance.",
            "Original raw 265145 vs contract-stated 40320 file-row discrepancy is unresolved.",
            "Exact historical raw→selected filtering algorithm still not independently recovered.",
            "No model trained or inferred, no outcome, target, or forward-price file opened.",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2j:",status)
    print("Original V1 model inputs: ",ROWS,"×",DIM,"embedding coordinates")
    for src,metrics in by_source.items():
        print(src,": rows",metrics["rows"],"max_abs_diff",metrics["max_abs_difference"],
              "rows_outside_1e-6",metrics["rows_exceeding_1e_6"])
    print("ALL:",total)
    print("Report:",out)
    print("No future targets, returns, prices, new news or model inference opened")
    return 0 if total["tolerance_pass"] else 2

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"G1.2j stopped: {type(exc).__name__}: {exc}",file=sys.stderr)
        raise SystemExit(3)
