#!/usr/bin/env python3
"""IC G1.2m: ONE declared historical V1 date-window raw-pair hypothesis.

Read-only comparison of frozen 2026 historical candidate news/ticker keys
against the historically documented V1 event window. The ONLY proposed
filter is 2026-05-02 <= event UTC day <= 2026-06-06, using event dates
from the original June 6 news snapshot. No rule optimization or data
labels/targets/prices, no new holdout and no model inference.

Even an exact match is retrospective *structural corroboration*, NOT
independent provenance of original generating code or file identity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

SIGNALS = "probabilistic_v1_holdout_signals_2026-06-06.pkl"
RAW = "pairs_raw_2025-01-01_2026-06-06.pkl"
NEWS = "news_2025-01-01_2026-06-06.pkl"
SIGNAL_SHA = "dc6f2c7ce6e794c271864526c94e9709c2837129b4776f298a9487641a8ea76b"
DATE_START = "2026-05-02"
DATE_END_EXCLUSIVE = "2026-06-07"
EXPECTED = 40320

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def identity(df,pd):
    if not {"news_id","ticker"}.issubset(df.columns):
        raise RuntimeError("Historical pair inputs lack explicit news/ticker keys")
    a=df[["news_id","ticker"]].copy()
    if a.isna().any().any():
        raise RuntimeError("Null historical source keys")
    a["ticker"]=a["ticker"].replace({"BRK.B":"BRK-B"})
    return pd.MultiIndex.from_frame(a)

def main():
    import pandas as pd

    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--historical-local-data",required=True)
    p.add_argument("--historical-outputs",required=True)
    p.add_argument("--source-subset-report",required=True)
    p.add_argument("--text-provenance-report",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--trust-historical-pickles",action="store_true")
    args=p.parse_args()
    if not args.trust_historical_pickles:
        p.error("Explicit --trust-historical-pickles required for local original Pickles")
    out=Path(args.out).expanduser()
    if out.exists():
        p.error("Refusing to overwrite a previous G1.2m evidence report")
    local=Path(args.historical_local_data).expanduser()
    old=Path(args.historical_outputs).expanduser()
    sources={
        "original_signals":local/SIGNALS,
        "raw_candidate_pairs":old/RAW,
        "original_news":old/NEWS,
    }
    for name,path in sources.items():
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Original historic source missing/unsafe: "+name)

    subset=json.loads(Path(args.source_subset_report).expanduser().read_text(encoding="utf-8"))
    text=json.loads(Path(args.text_provenance_report).expanduser().read_text(encoding="utf-8"))
    if subset.get("schema_version")!="dtrm.ic.g1.raw_source_subset.v1" or subset.get("status") not in (
        "CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING",
        "RAW_SOURCE_SUBSET_MEMBERSHIP_CONFIRMED_DERIVATION_PENDING"):
        raise RuntimeError("Original G1.2e canonicalized membership gate missing")
    if text.get("status")!="TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN":
        raise RuntimeError("Original G1.2g news-source gate missing")
    if sha(sources["original_signals"])!=SIGNAL_SHA:
        raise RuntimeError("Historical V1 signal SHA256 does not match V4 commitment")
    raw_sha=sha(sources["raw_candidate_pairs"])
    news_sha=sha(sources["original_news"])
    if raw_sha!=subset.get("raw_candidate_sha256_new_anchor_only"):
        raise RuntimeError("Original raw pair file differs from G1.2e")
    if news_sha!=text.get("historical_news_file_sha256_new_local_anchor"):
        raise RuntimeError("Original 2026 June news source differs from G1.2g")

    signals=pd.read_pickle(sources["original_signals"])
    raw=pd.read_pickle(sources["raw_candidate_pairs"])
    news=pd.read_pickle(sources["original_news"])
    if not all(isinstance(df,pd.DataFrame) for df in (signals,raw,news)):
        raise RuntimeError("Historical sources not all DataFrames")
    if len(signals)!=EXPECTED or len(raw)!=265145:
        raise RuntimeError("Unexpected original 40320/265145 source cardinalities")
    if not {"news_id","date_dt"}.issubset(news.columns):
        # No date-column speculation. Report only code-safe column metadata.
        status="V1_DECLARED_DATE_FILTER_SOURCE_NEWS_SCHEMA_OPEN"
        report={
            "schema_version":"dtrm.ic.g1.declared_date_filter.v1",
            "status":status,
            "source_news_columns":sorted(str(x) for x in news.columns),
            "original_news_rows":len(news),
            "date_window_start":DATE_START,
            "date_window_end_exclusive":DATE_END_EXCLUSIVE,
            "no_return_targets_or_new_cohorts_opened":True,
            "original_selection_source_verified":False,
        }
    else:
        if news["news_id"].isna().any() or news["news_id"].duplicated().any():
            raise RuntimeError("Original news snapshot has duplicate/missing news keys")
        news_dates=pd.to_datetime(news["date_dt"],utc=True,errors="raise")
        if news_dates.isna().any():
            raise RuntimeError("Historical original news event date missing")
        lookups=pd.Series(news_dates.to_numpy(),index=news["news_id"])
        old_dates=pd.to_datetime(raw["news_id"].map(lookups),utc=True)
        missing=int(old_dates.isna().sum())
        within=((old_dates >= pd.Timestamp(DATE_START,tz="UTC")) &
                (old_dates < pd.Timestamp(DATE_END_EXCLUSIVE,tz="UTC")))
        filtered=raw.loc[within].copy()
        filter_keys=identity(filtered,pd)
        signal_keys=identity(signals,pd)
        unique_original=bool(filter_keys.is_unique)
        unique_selected=bool(signal_keys.is_unique)
        matching_set=bool(
            unique_original and unique_selected
            and len(filter_keys)==len(signal_keys)
            and filter_keys.isin(signal_keys).all()
            and signal_keys.isin(filter_keys).all())
        matching_order=bool(matching_set and filter_keys.equals(signal_keys))
        original_dates_match=None
        if matching_set and "date_dt" in signals.columns:
            event_dates=pd.to_datetime(signals["date_dt"],utc=True,errors="raise")
            candidates=pd.Series(
                old_dates.loc[within].to_numpy(),
                index=filter_keys,
            )
            synced=pd.to_datetime(candidates.reindex(signal_keys),utc=True)
            original_dates_match=bool((event_dates.array==synced.array).all())
        missed_pairs=int((~signal_keys.isin(filter_keys)).sum())
        extra_pairs=int((~filter_keys.isin(signal_keys)).sum())
        if matching_set and matching_order and original_dates_match is not False:
            status="V1_DECLARED_DATE_FILTER_EXACT_KEY_SET_AND_ORDER_PASS_SOURCE_CODE_OPEN"
        elif matching_set:
            status="V1_DECLARED_DATE_FILTER_KEY_SET_PASS_ORDER_OR_DATES_OPEN"
        else:
            status="V1_DECLARED_DATE_FILTER_INCOMPLETE_ADDITIONAL_SELECTION_RULE_UNKNOWN"
        report={
            "schema_version":"dtrm.ic.g1.declared_date_filter.v1",
            "status":status,
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "source_date_rule":"Only historically declared V1 [2026-05-02,2026-06-06] in UTC (end-exclusive 2026-06-07); no fitted filters",
            "source_raw_pairs":len(raw),
            "original_historical_news_rows":len(news),
            "historically_frozen_v1_signals":len(signals),
            "source_news_ids_unmatched":missing,
            "window_filtered_candidate_pairs":len(filtered),
            "filtered_unique_pairs":unique_original,
            "selected_unique_pairs":unique_selected,
            "selected_pairs_not_in_window":missed_pairs,
            "window_pairs_not_in_selected_signals":extra_pairs,
            "same_pair_key_set":matching_set,
            "same_pair_order":matching_order,
            "event_timestamps_agree_by_id":original_dates_match,
            "original_v1_signals_historical_SHA256_verified":True,
            "raw_source_SHA256_new_local_anchor":raw_sha,
            "historical_news_SHA256_new_local_anchor":news_sha,
            "original_selection_source_verified":False,
            "contract_pair_filename_and_row_count_reconciled":False,
            "no_return_targets_or_new_cohorts_opened":True,
            "scientific_limits":[
                "Even complete date-window matching does NOT identify or authenticate the original historical V1 generator implementation.",
                "The local raw candidate basename has 265145 rows while historical contract lists the same basename with 40320.",
                "Only the previously documented V1 window and BRK.B alias were tested; no alternative interval or optimization applied.",
                "No news prices, labels, forward-return targets or newer observations opened.",
            ],
        }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G1.2m:",report["status"])
    for name in (
        "source_news_ids_unmatched","window_filtered_candidate_pairs",
        "historically_frozen_v1_signals","selected_pairs_not_in_window",
        "window_pairs_not_in_selected_signals","same_pair_key_set",
        "same_pair_order","event_timestamps_agree_by_id"):
        if name in report:
            print(name,":",report[name])
    if "source_news_columns" in report:
        print("source_news_columns:",report["source_news_columns"])
    print("Report:",out)
    print("No financial targets/prices, model inference, future cohort or new selection filters read.")
    return 0 if report["status"]=="V1_DECLARED_DATE_FILTER_EXACT_KEY_SET_AND_ORDER_PASS_SOURCE_CODE_OPEN" else 2

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"G1.2m stopped: {type(exc).__name__}: {exc}",file=sys.stderr)
        sys.exit(3)
