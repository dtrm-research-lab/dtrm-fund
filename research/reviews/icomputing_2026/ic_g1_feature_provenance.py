#!/usr/bin/env python3
"""G1.2f read-only historical canonical order and beta/embedding provenance.

Reads only explicitly trusted original V1 historical pair/signal/beta/
feature/embedding-manifest artifacts. Does not read any targets, prices,
returns, later news, or new holdout data. Never fits or executes models.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

NAMES = {
    "signals": "probabilistic_v1_holdout_signals_2026-06-06.pkl",
    "raw": "pairs_raw_2025-01-01_2026-06-06.pkl",
    "beta": "probabilistic_v1_holdout_beta_pre_2026-06-06.pkl",
    "features": "probabilistic_v1_holdout_features_2026-06-06.npy",
    "embed_manifest": "probabilistic_v1_embedding_manifest_2026-06-06.pkl",
}
ANCHORED = {
    "signals": "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b",
    "beta": "e39896db92f1bb7c8334f61a6eee7bc71f8acbd6b6e87504c388ae0b8b1463d8",
    "features": "a75af139bab4768740eb2e96c8656e51910ce0eb240babd357c7e96150b9d750",
}
ROWS = 40320
FEATURES = 390

def digest(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def keys(df, pd):
    if not {"news_id","ticker"}.issubset(df.columns):
        raise RuntimeError("No (news_id, ticker) pair key in historic source")
    if df[["news_id","ticker"]].isna().any().any():
        raise RuntimeError("Pair keys contain nulls")
    normalized = df[["news_id","ticker"]].copy()
    normalized["ticker"] = normalized["ticker"].replace({"BRK.B":"BRK-B"})
    return pd.MultiIndex.from_frame(normalized)

def describe_pickle(path, pd):
    if path is None or not path.is_file():
        return None, {"present":False}
    obj = pd.read_pickle(path)
    summary = {"present":True, "type":type(obj).__name__,
               "bytes":path.stat().st_size, "sha256_new_local_anchor":digest(path)}
    if isinstance(obj,(pd.DataFrame,pd.Series)):
        summary["shape"] = list(obj.shape)
        if isinstance(obj,pd.DataFrame):
            summary["column_names"] = sorted(str(x) for x in obj.columns)
    elif hasattr(obj,"shape"):
        try:
            summary["shape"] = list(obj.shape)
        except Exception:
            pass
    elif hasattr(obj,"__len__"):
        summary["length"] = len(obj)
    return obj,summary

def check_beta(obj, sig, X, pd, np):
    result = {"alignment_type":"NOT_DETERMINED", "recognized_numeric":False,
              "max_absolute_difference":None,"matching_all_40320":None,
              "notes":"This checks consistency with feature 390 only, not all feature columns."}
    if obj is None:
        return result
    candidates = None
    if isinstance(obj,pd.DataFrame):
        if {"news_id","ticker","beta_pre"}.issubset(obj.columns):
            source_index = keys(obj,pd)
            signal_index = keys(sig,pd)
            if not source_index.is_unique:
                result["alignment_type"]="DUPLICATE_NORMALIZED_BETA_KEYS"
                return result
            series = pd.Series(obj["beta_pre"].to_numpy(),index=source_index)
            matched = series.reindex(signal_index)
            if matched.notna().all():
                candidates = matched.to_numpy()
                result["alignment_type"]="KEYED_BY_NEWS_AND_CANONICAL_TICKER"
            else:
                result["alignment_type"]="KEYED_BUT_MISSING_SIGNAL_PAIRS"
        elif len(obj)==ROWS and "beta_pre" in obj.columns:
            candidates = obj["beta_pre"].to_numpy()
            result["alignment_type"]="POSITIONAL_DATAFRAME_NO_VERIFIED_KEYS"
    elif isinstance(obj,pd.Series) and len(obj)==ROWS:
        candidates = obj.to_numpy()
        result["alignment_type"]="POSITIONAL_SERIES_NO_VERIFIED_KEYS"
    elif isinstance(obj,np.ndarray):
        if obj.shape == (ROWS,):
            candidates = obj
            result["alignment_type"]="POSITIONAL_VECTOR_NO_VERIFIED_KEYS"
        elif obj.shape == (ROWS,1):
            candidates = obj[:,0]
            result["alignment_type"]="POSITIONAL_COLUMN_NO_VERIFIED_KEYS"
    if candidates is None:
        return result
    try:
        values = np.asarray(candidates,dtype=np.float64)
    except (TypeError, ValueError):
        result["alignment_type"]="NON_NUMERIC_BETA_CANDIDATE"
        return result
    if values.shape!=(ROWS,) or not np.isfinite(values).all():
        result["alignment_type"]="INVALID_NUMERIC_BETA_SHAPE_OR_VALUES"
        return result
    feature_beta = np.asarray(X[:,-1],dtype=np.float64)
    # Features are historically stored as float32: compare at same precision.
    delta = np.abs(feature_beta - values.astype(np.float32).astype(np.float64))
    result["recognized_numeric"]=True
    result["max_absolute_difference"]=float(delta.max())
    result["matching_all_40320"]=bool((delta<=1e-6).all())
    return result

def main():
    import numpy as np
    import pandas as pd
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signals-root",required=True)
    parser.add_argument("--raw-root",required=True)
    parser.add_argument("--embedding-manifest-root",default=None)
    parser.add_argument("--source-subset-report",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--trust-historical-pickles",action="store_true")
    args=parser.parse_args()
    if not args.trust_historical_pickles:
        parser.error("Explicit local trust required for original historic Pickles")
    subset=json.loads(Path(args.source_subset_report).expanduser().read_text(encoding="utf-8"))
    if subset.get("schema_version")!="dtrm.ic.g1.raw_source_subset.v1" or subset.get("status") not in (
        "CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING",
        "RAW_SOURCE_SUBSET_MEMBERSHIP_CONFIRMED_DERIVATION_PENDING"):
        raise RuntimeError("G1.2e source membership gate missing or not passed")
    out=Path(args.out).expanduser()
    if out.exists():
        parser.error("Refusing to overwrite previous audit")
    source=Path(args.signals_root).expanduser()
    old=Path(args.raw_root).expanduser()
    paths={
        "signals":source/NAMES["signals"],
        "raw":old/NAMES["raw"],
        "beta":source/NAMES["beta"],
        "features":source/NAMES["features"],
    }
    missing=[name for name,path in paths.items() if not path.is_file()]
    if missing:
        raise RuntimeError("Required original artifacts not found at specified root: "+", ".join(missing))
    for name,expected in ANCHORED.items():
        if digest(paths[name])!=expected:
            raise RuntimeError("Original historical SHA256 mismatch: "+NAMES[name])
    if digest(paths["raw"])!=subset.get("raw_candidate_sha256_new_anchor_only"):
        raise RuntimeError("Raw input changed since G1.2e membership check")
    sig=pd.read_pickle(paths["signals"])
    raw=pd.read_pickle(paths["raw"])
    if not isinstance(sig,pd.DataFrame) or not isinstance(raw,pd.DataFrame):
        raise RuntimeError("Expected original pair and signal tables")
    if len(sig)!=ROWS:
        raise RuntimeError("Historic V1 signals row count changed")
    sig_idx=keys(sig,pd)
    raw_idx=keys(raw,pd)
    raw_dup=int(len(raw_idx)-len(raw_idx.unique()))
    signal_dup=int(len(sig_idx)-len(sig_idx.unique()))
    if raw_dup==0 and signal_dup==0:
        positions=pd.Series(np.arange(len(raw_idx),dtype=np.int64),index=raw_idx).reindex(sig_idx)
        if positions.isna().any():
            membership=False
            ordered=None
        else:
            membership=True
            ordered=bool(np.all(np.diff(positions.to_numpy(dtype=np.int64))>0))
    else:
        membership=bool(sig_idx.isin(raw_idx.unique()).all())
        ordered=None
    X=np.load(paths["features"],allow_pickle=False)
    if X.shape!=(ROWS,FEATURES) or not np.issubdtype(X.dtype,np.number) or not np.isfinite(X).all():
        raise RuntimeError("Original pinned V1 feature matrix shape invalid")
    beta,beta_structure=describe_pickle(paths["beta"],pd)
    beta_check=check_beta(beta,sig,X,pd,np)
    embed_path=None
    if args.embedding_manifest_root:
        candidate=Path(args.embedding_manifest_root).expanduser()/NAMES["embed_manifest"]
        if candidate.is_file():
            embed_path=candidate
    if embed_path is None:
        for folder in (source,old):
            candidate=folder/NAMES["embed_manifest"]
            if candidate.is_file():
                embed_path=candidate
                break
    _,emb_structure=describe_pickle(embed_path,pd)
    result={
        "schema_version":"dtrm.ic.g1.feature_provenance_structure.v1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "historical_anchored_sha_verification":True,
        "raw_sha_unchanged_since_g1_2e":True,
        "row_counts":{"raw_candidate_pairs":len(raw),"frozen_V1_signals":len(sig)},
        "canonical_pair_membership_all":membership,
        "canonical_raw_pair_duplicate_rows":raw_dup,
        "canonical_signal_duplicate_rows":signal_dup,
        "canonical_signal_order_is_raw_subsequence":ordered,
        "feature_shape":list(X.shape),
        "beta_source_structure":beta_structure,
        "beta_to_feature_column390":beta_check,
        "embedding_manifest_structure":emb_structure,
        "remaining_limitations":[
            "Pair-subsequence order is not required if the source was explicitly resorted.",
            "Even a last-column beta match is not proof of all 384 embedding + 5 text fields.",
            "The local raw pair file and V1 contract differ in file row count (265145 vs 40320).",
            "Original raw-to-selected filtering and feature construction source pipeline remains unverified.",
            "No new temporal event cohort or realized returns may be scored on this report alone.",
        ],
        "new_holdout_evaluated":False,
        "prospective_model_approval":False,
    }
    if not membership or signal_dup:
        result["status"]="CANONICAL_PAIR_LINEAGE_MISMATCH"
    elif beta_check["recognized_numeric"] and not beta_check["matching_all_40320"]:
        result["status"]="HISTORICAL_BETA_FEATURE_MISMATCH"
    elif beta_check["matching_all_40320"]:
        result["status"]="HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN"
    else:
        result["status"]="HISTORICAL_CANONICAL_PAIR_MEMBERSHIP_PASS_BETA_SCHEMA_OPEN"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2f:",result["status"])
    print("Raw/selected:",len(raw),"/",len(sig))
    print("Normalized raw duplicate rows:",raw_dup)
    print("Normalized membership all:",membership)
    print("Selected pair order is source subsequence:",ordered)
    print("Historic features shape:",X.shape)
    print("Beta schema:",beta_structure)
    print("Beta to last feature:",beta_check)
    print("Embedding manifest schema:",emb_structure)
    print("Report:",out)
    print("No targets/returns/new cohorts or model inference accessed")
    return 2 if result["status"] in (
        "CANONICAL_PAIR_LINEAGE_MISMATCH","HISTORICAL_BETA_FEATURE_MISMATCH") else 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"G1.2f halted: {type(e).__name__}: {e}",file=sys.stderr)
        sys.exit(3)
