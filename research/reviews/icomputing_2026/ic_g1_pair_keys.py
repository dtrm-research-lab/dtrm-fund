#!/usr/bin/env python3
"""G1.2d original V1 pair key-order audit; no outcomes or new holdout.

Reads only trusted 2026 source pairs/signals. No predictions, prices,
model fitting, or return labels. File-path names are never reported.
"""
import argparse
import hashlib
import json
from pathlib import Path

SIGNALS="probabilistic_v1_holdout_signals_2026-06-06.pkl"
PAIRS="pairs_raw_2025-01-01_2026-06-06.pkl"
SIGNALS_SHA="dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b"

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def main():
    import pandas as pd
    p=argparse.ArgumentParser()
    p.add_argument("--local-data",required=True)
    p.add_argument("--original-outputs",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--trust-original-pickles",action="store_true")
    args=p.parse_args()
    if not args.trust_original_pickles:
        p.error("Requires explicit trust of the original local Pickles")
    sig_path=Path(args.local_data).expanduser()/SIGNALS
    pairs_path=Path(args.original_outputs).expanduser()/PAIRS
    if not sig_path.is_file() or not pairs_path.is_file():
        raise RuntimeError("Original V1 signal or pair file not found at given roots")
    if digest(sig_path)!=SIGNALS_SHA:
        raise RuntimeError("Original V1 signal SHA256 did not match 2026 contract")
    out=Path(args.out).expanduser()
    if out.exists():
        p.error("Refusing to overwrite prior report")
    sig=pd.read_pickle(sig_path)
    raw=pd.read_pickle(pairs_path)
    if not isinstance(sig,pd.DataFrame) or not isinstance(raw,pd.DataFrame):
        raise RuntimeError("Original pair inputs not both dataframes")
    required={"news_id","ticker"}
    if not required.issubset(sig.columns) or not required.issubset(raw.columns):
        raise RuntimeError("Original pairs or signals lack explicit (news_id,ticker)")
    sk=pd.MultiIndex.from_frame(sig[["news_id","ticker"]])
    rk=pd.MultiIndex.from_frame(raw[["news_id","ticker"]])
    unique=bool(sk.is_unique and rk.is_unique)
    equal_set=bool(unique and len(sk)==len(rk) and len(sk.intersection(rk))==len(sk))
    same_order=bool(equal_set and sk.equals(rk))
    date_match=None
    if equal_set and "date_dt" in sig and "date_dt" in raw:
        s=pd.to_datetime(sig["date_dt"],utc=True)
        dates=pd.Series(pd.to_datetime(raw["date_dt"],utc=True).values,index=rk)
        matched=pd.to_datetime(dates.reindex(sk).to_numpy(),utc=True)
        date_match=bool((s.array==matched).all())
    state=("V1_SOURCE_PAIR_KEYS_AND_ORDER_MATCH"
           if same_order and date_match is not False
           else "V1_SOURCE_PAIR_KEYS_MATCH_ORDER_DIFFERENT"
           if equal_set and date_match is not False
           else "V1_SOURCE_PAIRS_MISMATCH_OR_UNKNOWN")
    report={
        "schema_version":"dtrm.ic.g1.source_keys.v1",
        "status":state,
        "signals_sha256_original_anchor_verified":True,
        "source_pairs_sha256_new_local_anchor":digest(pairs_path),
        "signals_rows":len(sig),
        "pairs_rows":len(raw),
        "unique_pair_keys":unique,
        "key_sets_identical":equal_set,
        "key_order_identical":same_order,
        "dates_match_by_key":date_match,
        "source_pair_columns":sorted(str(c) for c in raw.columns),
        "feature_row_alignment_certified":False,
        "holdout_scored":False,
        "limitations":[
            "Raw source pairs lack an independently checked 2026 SHA commitment.",
            "Matching pair order is not by itself proof of 390-feature matrix alignment.",
            "News embeddings and beta feature provenance still require verification.",
        ],
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2d:",state)
    print("raw pairs:",len(raw),"; signals:",len(sig))
    print("same key set:",equal_set,"; same order:",same_order,"; dates match:",date_match)
    print("Original source columns:",report["source_pair_columns"])
    print("Report:",out)
    print("No new outcomes or post-June data opened.")
    return 0 if equal_set and date_match is not False else 2

if __name__=="__main__":
    raise SystemExit(main())
