#!/usr/bin/env python3
"""IC G1.2e: read-only original-source subset membership audit.

Compares an original *raw candidate universe* to frozen V1 signals.
A source of 265145 raw candidate pairs need not have 40320 selected
V1 signal rows. The test establishes membership and (if possible) order,
NOT the provenance of the historical filtering policy or feature rows.

Read only explicitly trusted local historical Pickle inputs.
Never load targets, future data, prices, or model inference.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ORIGINAL_SIGNALS = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
RAW_CANDIDATES = "pairs_raw_2025-01-01_2026-06-06.pkl"
ORIGINAL_SIGNALS_SHA = "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b"
STAGE = "DTRM_XGB_PROBABILISTIC_V1"
DECLARED_PAIRS = 40320
DECLARED_NEWS = 5526
DECLARED_TICKERS = 171

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def pair_index(df, pd):
    if not {"news_id","ticker"}.issubset(df.columns):
        raise RuntimeError("Input lacks news_id/ticker pair keys")
    if df[["news_id","ticker"]].isna().any().any():
        raise RuntimeError("Input has null pair identifiers")
    return pd.MultiIndex.from_frame(df[["news_id","ticker"]])

def tally(signal_keys, raw_keys, pd):
    # Conservative exact-key membership with no guesses.
    uniq_raw=raw_keys.unique()
    uniq_sig=signal_keys.unique()
    yes=signal_keys.isin(uniq_raw)
    missing=int((~yes).sum())
    raw_duplicate=int(len(raw_keys)-len(uniq_raw))
    order=None
    if bool(uniq_raw.is_unique) and raw_duplicate==0 and missing==0:
        # Every source pair has a unique original row position.
        index_to_position=pd.Series(range(len(raw_keys)),index=raw_keys)
        positions=index_to_position.reindex(signal_keys).to_numpy()
        import numpy as np
        order=bool(np.all(np.diff(positions)>0))
    return {
        "original_raw_candidates":len(raw_keys),
        "raw_distinct_keys":len(uniq_raw),
        "raw_duplicate_key_rows":raw_duplicate,
        "selected_signal_rows":len(signal_keys),
        "selected_distinct_keys":len(uniq_sig),
        "signal_duplicate_key_rows":len(signal_keys)-len(uniq_sig),
        "selected_keys_present_in_raw":int(yes.sum()),
        "selected_keys_missing_in_raw":missing,
        "raw_to_selected_subset_membership_complete": bool(missing==0),
        "selected_order_is_raw_subsequence_if_raw_unique": order,
    }

def main() -> int:
    import pandas as pd
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--signals-root",required=True)
    ap.add_argument("--raw-root",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--trust-original-pickles",action="store_true")
    args=ap.parse_args()
    if not args.trust_original_pickles:
        ap.error("Only explicit trusted historic Pickles permitted")
    sig_path=Path(args.signals_root).expanduser()/ORIGINAL_SIGNALS
    raw_path=Path(args.raw_root).expanduser()/RAW_CANDIDATES
    out=Path(args.out).expanduser()
    if out.exists():
        ap.error("Refusing to overwrite prior report")
    if not sig_path.is_file() or not raw_path.is_file():
        raise RuntimeError("Historic signals or raw pair input missing")
    if sha(sig_path)!=ORIGINAL_SIGNALS_SHA:
        raise RuntimeError("Original V1 signals historical SHA mismatch")
    raw_sha=sha(raw_path)
    sig=pd.read_pickle(sig_path)
    raw=pd.read_pickle(raw_path)
    if not isinstance(sig,pd.DataFrame) or not isinstance(raw,pd.DataFrame):
        raise RuntimeError("Expected pandas DataFrame sources")
    if len(sig)!=DECLARED_PAIRS:
        raise RuntimeError("Historic signals no longer have original V1 row count")
    sk=pair_index(sig,pd)
    rk=pair_index(raw,pd)
    exact=tally(sk,rk,pd)
    canonical=tally(
        pair_index(sig.assign(ticker=sig["ticker"].replace({"BRK.B":"BRK-B"})),pd),
        pair_index(raw.assign(ticker=raw["ticker"].replace({"BRK.B":"BRK-B"})),pd),
        pd,
    )
    dates=None
    if "date_dt" in sig.columns:
        ds=pd.to_datetime(sig["date_dt"],utc=True,errors="raise")
        dates={
            "minimum_event_date_utc":ds.min().isoformat(),
            "maximum_event_date_utc":ds.max().isoformat(),
            "within_declared_V1_date_window":bool(
                (ds >= pd.Timestamp("2026-05-02",tz="UTC")).all()
                and (ds < pd.Timestamp("2026-06-07",tz="UTC")).all()
            ),
        }
    props={
        "signals_news_count":int(sig["news_id"].nunique()),
        "signals_ticker_count":int(sig["ticker"].nunique()),
        "signals_duplicate_pairs":int(exact["signal_duplicate_key_rows"]),
        "expected_contract_news":DECLARED_NEWS,
        "expected_contract_tickers":DECLARED_TICKERS,
    }
    contract_file_name_reused_with_other_cardinality = len(raw)!=DECLARED_PAIRS
    if exact["raw_to_selected_subset_membership_complete"] and exact["signal_duplicate_key_rows"]==0:
        status="RAW_SOURCE_SUBSET_MEMBERSHIP_CONFIRMED_DERIVATION_PENDING"
    elif canonical["raw_to_selected_subset_membership_complete"] and canonical["signal_duplicate_key_rows"]==0:
        status="CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING"
    else:
        status="RAW_SOURCE_PAIR_LINKAGE_UNRESOLVED"
    report={
        "schema_version":"dtrm.ic.g1.raw_source_subset.v1",
        "stage":STAGE,
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "status":status,
        "signals_historical_sha256_anchor_verified":True,
        "raw_candidate_sha256_new_anchor_only":raw_sha,
        "exact_key_membership":exact,
        "BRK_B_canonicalized_membership":canonical,
        "event_date_range":dates,
        "selected_signal_properties":props,
        "contract_name_cardinality_discrepancy":{
            "contract_lists_raw_filename":RAW_CANDIDATES,
            "contract_rows_for_name":DECLARED_PAIRS,
            "local_files_rows":len(raw),
            "mismatch":contract_file_name_reused_with_other_cardinality,
            "interpretation":"Open provenance discrepancy; investigate raw-to-selected filtering or file provenance. Not automatically data corruption.",
        },
        "not_verified":[
            "Exact original inclusion/exclusion rule for mapping raw candidate pairs into selected 40320 rows",
            "Original full 390-feature vector alignment to each (news_id,ticker)",
            "Full original embedding, beta and text feature construction chain",
            "Model transport to unseen August/September 2026 news",
        ],
        "no_return_values_or_new_holdout_read":True,
        "model_inference_approved":False,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2e:",status)
    print("Raw candidate rows:",len(raw),"; V1 selected rows:",len(sig))
    print("Exact member hits:",exact["selected_keys_present_in_raw"],"; missing:",exact["selected_keys_missing_in_raw"])
    print("Canonical BRK.B -> BRK-B member hits:",canonical["selected_keys_present_in_raw"],
          "; missing:",canonical["selected_keys_missing_in_raw"])
    print("Raw duplicates:",exact["raw_duplicate_key_rows"],
          "; V1 signal duplicates:",exact["signal_duplicate_key_rows"])
    print("Original raw-order subsequence:",exact["selected_order_is_raw_subsequence_if_raw_unique"])
    print("Contract filename cardinality discrepancy:",contract_file_name_reused_with_other_cardinality)
    print("Original V1 events:",dates)
    print("Report:",out)
    print("No prospective news, price returns, targets, or models opened.")
    return 2 if status=="RAW_SOURCE_PAIR_LINKAGE_UNRESOLVED" else 0

if __name__=="__main__":
    sys.exit(main())
