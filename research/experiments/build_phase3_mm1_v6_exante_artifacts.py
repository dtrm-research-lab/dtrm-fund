"""Build Phase-3 MM1 V6 ex-ante candidate rows and 390-feature matrix.

V6 is the preregistered prospective replication cohort. This builder is
strictly outcome-blind: it reads only contemporaneous news metadata/text, the
frozen Phase-2 universe, and historical prices on or before each event date
needed to reconstruct beta_pre. It never constructs, loads, or inspects V6
forward targets, target_model, realized forward returns, or a post-event price
path for decision use.

The implementation intentionally reuses the frozen V5 feature semantics without
modifying any V5 artifact or the MM1 optimizer.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

import build_phase3_mm1_v5_exante_artifacts as v5


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"

V6_START = pd.Timestamp("2026-06-26T00:00:00Z")
V6_END = pd.Timestamp("2026-07-06T23:59:59Z")
EXPECTED_FEATURE_COUNT = v5.EXPECTED_FEATURE_COUNT

V6_ROWS_OUTPUT = LOCAL_DATA / "phase3_mm1_v6_candidate_rows_exante.pkl"
V6_FEATURES_OUTPUT = LOCAL_DATA / "phase3_mm1_v6_features_exante.npy"
V6_BUILD_SUMMARY_OUTPUT = LOCAL_DATA / "phase3_mm1_v6_exante_build_summary.json"

MONGO_DATABASE = v5.MONGO_DATABASE
MONGO_COLLECTION = v5.MONGO_COLLECTION
REQUIRED_ROW_COLUMNS = ("news_id", "ticker", "date_dt")


def sha256_file(path: Path) -> str:
    return v5.sha256_file(path)


def validate_v6_inputs(
    rows: pd.DataFrame,
    features: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    missing = set(REQUIRED_ROW_COLUMNS) - set(rows.columns)
    if missing:
        raise ValueError(f"Missing V6 ex-ante row columns: {sorted(missing)}")

    extra = set(rows.columns) - set(REQUIRED_ROW_COLUMNS)
    if extra:
        raise ValueError(
            "V6 candidate-row artifact must contain identity/date fields only; "
            f"unexpected columns: {sorted(extra)}"
        )

    normalized = rows.loc[:, REQUIRED_ROW_COLUMNS].copy()
    normalized["date_dt"] = pd.to_datetime(normalized["date_dt"], utc=True)

    if normalized.empty:
        raise ValueError("V6 candidate-row artifact must not be empty")
    if normalized[["news_id", "ticker"]].isna().any().any():
        raise ValueError("V6 row identities must not contain missing values")
    if normalized["date_dt"].isna().any():
        raise ValueError("V6 dates must be valid timestamps")
    if normalized.duplicated(["news_id", "ticker"]).any():
        raise ValueError("V6 candidate rows contain duplicate (news_id, ticker) keys")
    if (normalized["date_dt"] < V6_START).any() or (normalized["date_dt"] > V6_END).any():
        raise ValueError("V6 candidate rows fall outside the preregistered V6 window")

    X = np.asarray(features)
    if X.ndim != 2:
        raise ValueError("V6 feature matrix must be two-dimensional")
    if X.shape[0] != len(normalized):
        raise ValueError("V6 feature rows must match candidate-row count")
    if X.shape[1] != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"V6 feature matrix must contain exactly {EXPECTED_FEATURE_COUNT} columns"
        )
    if not np.issubdtype(X.dtype, np.number):
        raise ValueError("V6 features must be numeric")
    if not np.isfinite(X).all():
        raise ValueError("V6 features must contain only finite values")

    return normalized.reset_index(drop=True), np.asarray(X, dtype=np.float32)


def extract_v6_news_and_pairs(
    documents: Iterable[Mapping],
    *,
    allowed_tickers: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reproduce frozen V5 row semantics on the preregistered V6 window."""

    news_rows: list[dict] = []
    pair_rows: list[dict] = []

    for document in documents:
        if "_id" not in document:
            raise ValueError("Every V6 source document must contain _id")

        raw_date = document.get("date")
        if raw_date is None:
            continue
        try:
            event_date = pd.to_datetime(str(raw_date)[:10], utc=True)
        except Exception:
            continue

        if pd.isna(event_date) or event_date < V6_START or event_date > V6_END:
            continue

        text = v5.legacy_embedding_text(document.get("text", ""))
        if not text:
            continue

        tickers = v5._extract_matched_tickers(document, allowed_tickers)
        if not tickers:
            continue

        news_id = str(document["_id"])
        news_rows.append(
            {"news_id": news_id, "date_dt": event_date, "news_text": text}
        )
        for ticker in tickers:
            pair_rows.append(
                {"news_id": news_id, "ticker": ticker, "date_dt": event_date}
            )

    news = pd.DataFrame(news_rows, columns=["news_id", "date_dt", "news_text"])
    pairs = pd.DataFrame(pair_rows, columns=["news_id", "ticker", "date_dt"])

    if news.empty or pairs.empty:
        raise RuntimeError("No valid V6 news/pairs were produced from the frozen source query")
    if news.duplicated(["news_id"]).any():
        duplicated = news.loc[news.duplicated(["news_id"], keep=False), "news_id"].unique()
        raise ValueError(f"Duplicate V6 news_id values: {duplicated[:5].tolist()}")
    if pairs.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicate V6 (news_id, ticker) pairs after ticker normalization")

    news = news.sort_values(["date_dt", "news_id"], kind="mergesort").reset_index(drop=True)
    news_position = {nid: i for i, nid in enumerate(news["news_id"].tolist())}
    pairs = pairs.assign(_news_position=pairs["news_id"].map(news_position))
    pairs = (
        pairs.sort_values(["_news_position", "ticker"], kind="mergesort")
        .drop(columns=["_news_position"])
        .reset_index(drop=True)
    )

    ordering_dates = pairs["date_dt"].dt.tz_convert("UTC").dt.tz_localize(None)
    order = v5.legacy_model_row_order(pairs["ticker"], ordering_dates)
    pairs = pairs.iloc[order].reset_index(drop=True)

    merged_dates = pairs[["news_id", "date_dt"]].merge(
        news[["news_id", "date_dt"]],
        on="news_id",
        how="left",
        validate="many_to_one",
        suffixes=("_pair", "_news"),
    )
    if not merged_dates["date_dt_pair"].equals(merged_dates["date_dt_news"]):
        raise ValueError("V6 pair/news event dates are inconsistent")

    return news, pairs


def fetch_v6_documents_from_mongo() -> list[dict]:
    """Read only the projected outcome-free source fields frozen in V5."""

    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError(
            "V6 builder requires the optional 'v5-builder' dependencies; "
            "install with: python -m pip install -e '.[v5-builder]'"
        ) from exc

    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        password = os.getenv("db_password")
        if not password:
            raise RuntimeError("Missing MONGO_URI or db_password for read-only V6 source query")
        mongo_uri = (
            f"mongodb+srv://UrtziFM:{password}@pcmoneytest.qvnkw.mongodb.net/"
            "?retryWrites=true&w=majority&appName=PCMoneyTest"
        )

    client = MongoClient(mongo_uri)
    try:
        collection = client[MONGO_DATABASE][MONGO_COLLECTION]
        documents = list(
            collection.find(
                {
                    "date": {
                        "$gte": V6_START.strftime("%Y-%m-%d"),
                        "$lte": V6_END.strftime("%Y-%m-%d"),
                    }
                },
                {"text": 1, "date": 1, "matched_tickers": 1},
            )
        )
    finally:
        client.close()

    return documents


def require_outputs_absent() -> None:
    existing = [
        path
        for path in (V6_ROWS_OUTPUT, V6_FEATURES_OUTPUT, V6_BUILD_SUMMARY_OUTPUT)
        if path.exists()
    ]
    if existing:
        raise RuntimeError(
            "V6 ex-ante artifact builder refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def main() -> None:
    require_outputs_absent()

    allowed_tickers = v5.load_frozen_phase2_universe()
    documents = fetch_v6_documents_from_mongo()
    source_sha256 = v5.canonical_source_sha256(documents)

    news, pairs = extract_v6_news_and_pairs(
        documents,
        allowed_tickers=allowed_tickers,
    )

    # Exactly the frozen ex-ante price cache and beta implementation used by V5.
    prices = v5.load_exante_price_cache()
    beta_pre = v5.beta_pre_for_pairs(pairs, prices)
    embeddings, sentence_transformers_version = v5.encode_unique_news(news)
    features = v5.build_v5_feature_matrix(
        news,
        pairs,
        beta_pre=beta_pre,
        embeddings=embeddings,
    )

    candidate_rows = pairs[["news_id", "ticker", "date_dt"]].copy()
    candidate_rows, features = validate_v6_inputs(candidate_rows, features)

    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    candidate_rows.to_pickle(V6_ROWS_OUTPUT)
    np.save(V6_FEATURES_OUTPUT, features, allow_pickle=False)

    summary = {
        "stage": "DTRM_PHASE3_MM1_V6_EXANTE_ARTIFACT_BUILDER",
        "status": "built_outcome_blind_pending_provenance_freeze",
        "role": "prospective_temporal_replication",
        "window": {
            "start": V6_START.isoformat(),
            "end": V6_END.isoformat(),
        },
        "source": {
            "database": MONGO_DATABASE,
            "collection": MONGO_COLLECTION,
            "projected_fields": ["_id", "date", "text", "matched_tickers"],
            "raw_documents": int(len(documents)),
            "canonical_source_sha256": source_sha256,
        },
        "frozen_universe_tickers": int(len(allowed_tickers)),
        "news_unique": int(len(news)),
        "pair_rows": int(len(candidate_rows)),
        "canonical_tickers": int(candidate_rows["ticker"].nunique()),
        "duplicate_pairs": int(candidate_rows.duplicated(["news_id", "ticker"]).sum()),
        "features": {
            "dimensions": int(features.shape[1]),
            "dtype": str(features.dtype),
            "layout": "384_sbert_plus_5_legacy_text_plus_1_beta_pre",
            "sbert_model": v5.SBERT_MODEL,
            "sbert_dimensions": v5.SBERT_DIMENSIONS,
            "sbert_normalize": True,
            "sbert_max_chars": v5.SBERT_MAX_CHARS,
            "sentence_transformers_version": sentence_transformers_version,
            "text_feature_count": 5,
            "beta_feature_count": 1,
            "ret_spy_evt_included": False,
        },
        "beta_pre": {
            "lookback": v5.BETA_LOOKBACK,
            "min_observations": v5.BETA_MIN_OBSERVATIONS,
            "tolerance_days": v5.BETA_TOLERANCE_DAYS,
            "information_set": "prices_on_or_before_each_event_date_only",
            "post_event_prices_passed_to_beta": False,
            "missing_or_imputed": 0,
        },
        "price_snapshot_loader": "run_exante_baseline_v0.load_exante_price_cache",
        "information_firewall": {
            "target_model_accessed": False,
            "forward_target_computed": False,
            "realized_forward_returns_accessed": False,
            "V5_results_used_to_change_V6_policy": False,
        },
        "governance": {
            "rho_retuned": False,
            "threshold_retuned": False,
            "model_retrained_for_V6": False,
            "V6_policy_changed_from_frozen_V5": False,
            "evaluation_before_2026_09_04": "forbidden",
        },
        "outputs": {
            "candidate_rows": str(V6_ROWS_OUTPUT.relative_to(REPO_ROOT)),
            "candidate_rows_sha256": sha256_file(V6_ROWS_OUTPUT),
            "features": str(V6_FEATURES_OUTPUT.relative_to(REPO_ROOT)),
            "features_sha256": sha256_file(V6_FEATURES_OUTPUT),
        },
    }

    V6_BUILD_SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V6 EX-ANTE ARTIFACT BUILD")
    print("outcome firewall: PASS")
    print("source documents:", len(documents))
    print("unique news:", len(news))
    print("pair rows:", len(candidate_rows))
    print("canonical tickers:", candidate_rows["ticker"].nunique())
    print("features:", features.shape)
    print("candidate rows sha256:", sha256_file(V6_ROWS_OUTPUT))
    print("feature matrix sha256:", sha256_file(V6_FEATURES_OUTPUT))
    print("candidate rows:", V6_ROWS_OUTPUT)
    print("feature matrix:", V6_FEATURES_OUTPUT)
    print("summary:", V6_BUILD_SUMMARY_OUTPUT)


if __name__ == "__main__":
    main()
