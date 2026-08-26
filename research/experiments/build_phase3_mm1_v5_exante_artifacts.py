"""Build Phase-3 MM1 V5 ex-ante candidate rows and 390-feature matrix.

This builder is intentionally outcome-blind. It reads only contemporaneous
news metadata/text, the frozen Phase-2 universe, and historical prices needed
to reconstruct beta_pre on or before each event date. It never constructs or
loads V5 forward targets, realized returns, or target_model.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from dtrm.feature_matrix import assemble_exante_feature_matrix
from dtrm.legacy_beta_pre import legacy_beta_pre_from_prices
from dtrm.legacy_row_order import legacy_model_row_order
from dtrm.text_features import legacy_text_feature_matrix

from run_exante_baseline_v0 import (
    load_exante_price_cache,
    load_ordered_model_rows,
)
from run_phase3_mm1_v5_decision_freeze import validate_v5_inputs


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"

V5_START = pd.Timestamp("2026-06-15T00:00:00Z")
V5_END = pd.Timestamp("2026-06-25T23:59:59Z")

SBERT_MODEL = "all-MiniLM-L6-v2"
SBERT_DIMENSIONS = 384
SBERT_MAX_CHARS = 1600
SBERT_BATCH_SIZE = 16
EXPECTED_FEATURE_COUNT = 390

BETA_LOOKBACK = 252
BETA_MIN_OBSERVATIONS = 60
BETA_TOLERANCE_DAYS = 20

TICKER_NORMALIZATION = {
    "BRK.B": "BRK-B",
}

V5_ROWS_OUTPUT = LOCAL_DATA / "phase3_mm1_v5_candidate_rows_exante.pkl"
V5_FEATURES_OUTPUT = LOCAL_DATA / "phase3_mm1_v5_features_exante.npy"
V5_BUILD_SUMMARY_OUTPUT = LOCAL_DATA / "phase3_mm1_v5_exante_build_summary.json"

MONGO_DATABASE = "trumpMinMax"
MONGO_COLLECTION = "trumpNews"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_ticker(value) -> str:
    ticker = str(value).strip().upper()
    return TICKER_NORMALIZATION.get(ticker, ticker)


def legacy_embedding_text(value) -> str:
    """Reproduce the legacy scorer's text normalization for SBERT."""

    if not isinstance(value, str):
        value = "" if value is None else str(value)
    value = value.replace("\n", " ").replace("\r", " ").strip()
    return value[:SBERT_MAX_CHARS] if len(value) > SBERT_MAX_CHARS else value


def load_frozen_phase2_universe() -> set[str]:
    """Return the canonical ticker universe represented by frozen model rows."""

    _, ordered_rows = load_ordered_model_rows()
    universe = {
        _canonical_ticker(ticker)
        for ticker in ordered_rows["ticker"].tolist()
    }
    universe.discard("")
    if not universe:
        raise RuntimeError("Frozen Phase-2 universe is empty")
    return universe


def _extract_matched_tickers(document: Mapping, allowed_tickers: set[str]) -> list[str]:
    result = set()
    for match in document.get("matched_tickers", []):
        ticker = match.get("ticker") if isinstance(match, Mapping) else None
        if not ticker:
            continue
        canonical = _canonical_ticker(ticker)
        if canonical in allowed_tickers:
            result.add(canonical)
    return sorted(result)


def extract_v5_news_and_pairs(
    documents: Iterable[Mapping],
    *,
    allowed_tickers: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normalize projected Mongo news documents into deterministic V5 rows."""

    news_rows = []
    pair_rows = []

    for document in documents:
        if "_id" not in document:
            raise ValueError("Every V5 source document must contain _id")

        raw_date = document.get("date")
        if raw_date is None:
            continue

        try:
            event_date = pd.to_datetime(str(raw_date)[:10], utc=True)
        except Exception:
            continue

        if pd.isna(event_date) or event_date < V5_START or event_date > V5_END:
            continue

        text = legacy_embedding_text(document.get("text", ""))
        if not text:
            continue

        tickers = _extract_matched_tickers(document, allowed_tickers)
        if not tickers:
            continue

        news_id = str(document["_id"])
        news_rows.append(
            {
                "news_id": news_id,
                "date_dt": event_date,
                "news_text": text,
            }
        )
        for ticker in tickers:
            pair_rows.append(
                {
                    "news_id": news_id,
                    "ticker": ticker,
                    "date_dt": event_date,
                }
            )

    news = pd.DataFrame(news_rows, columns=["news_id", "date_dt", "news_text"])
    pairs = pd.DataFrame(pair_rows, columns=["news_id", "ticker", "date_dt"])

    if news.empty or pairs.empty:
        raise RuntimeError("No valid V5 news/pairs were produced from the frozen source query")

    if news.duplicated(["news_id"]).any():
        duplicated = news.loc[news.duplicated(["news_id"], keep=False), "news_id"].unique()
        raise ValueError(f"Duplicate V5 news_id values: {duplicated[:5].tolist()}")

    if pairs.duplicated(["news_id", "ticker"]).any():
        raise ValueError("Duplicate V5 (news_id, ticker) pairs after ticker normalization")

    news = news.sort_values(["date_dt", "news_id"], kind="mergesort").reset_index(drop=True)

    # Reproduce the frozen legacy model-row ordering semantics while giving
    # same-ticker/same-date ties a deterministic source order from the sorted
    # news snapshot above.
    news_position = {nid: i for i, nid in enumerate(news["news_id"].tolist())}
    pairs = pairs.assign(_news_position=pairs["news_id"].map(news_position))
    pairs = pairs.sort_values(
        ["_news_position", "ticker"],
        kind="mergesort",
    ).drop(columns=["_news_position"]).reset_index(drop=True)

    ordering_dates = pairs["date_dt"].dt.tz_convert("UTC").dt.tz_localize(None)
    order = legacy_model_row_order(pairs["ticker"], ordering_dates)
    pairs = pairs.iloc[order].reset_index(drop=True)

    merged_dates = pairs[["news_id", "date_dt"]].merge(
        news[["news_id", "date_dt"]],
        on="news_id",
        how="left",
        validate="many_to_one",
        suffixes=("_pair", "_news"),
    )
    if not merged_dates["date_dt_pair"].equals(merged_dates["date_dt_news"]):
        raise ValueError("V5 pair/news event dates are inconsistent")

    return news, pairs


def _naive_utc(value) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert("UTC").tz_localize(None)
    return timestamp


def price_history_on_or_before(price_series: Sequence, event_date) -> list:
    """Return a price history explicitly cut off at the event timestamp."""

    cutoff = _naive_utc(event_date)
    result = []
    for date, price in price_series:
        if _naive_utc(date) <= cutoff:
            result.append((date, price))
    return result


def beta_pre_for_pairs(
    pairs: pd.DataFrame,
    prices: Mapping[str, Sequence],
) -> np.ndarray:
    """Reconstruct frozen beta_pre with no post-event price observations."""

    if "SPY" not in prices:
        raise RuntimeError("Frozen price cache is missing SPY")

    beta_cache: dict[tuple[str, str], float] = {}
    values = np.empty(len(pairs), dtype=np.float64)

    for position, row in enumerate(pairs.itertuples(index=False)):
        ticker = _canonical_ticker(row.ticker)
        if ticker not in prices:
            raise RuntimeError(f"Frozen price cache is missing ticker {ticker}")

        event_date = pd.Timestamp(row.date_dt)
        day_key = event_date.strftime("%Y-%m-%d")
        key = (ticker, day_key)

        if key not in beta_cache:
            stock_history = price_history_on_or_before(prices[ticker], event_date)
            market_history = price_history_on_or_before(prices["SPY"], event_date)

            beta = legacy_beta_pre_from_prices(
                stock_prices=stock_history,
                market_prices=market_history,
                event_date=event_date,
                lookback=BETA_LOOKBACK,
                min_observations=BETA_MIN_OBSERVATIONS,
                tolerance_days=BETA_TOLERANCE_DAYS,
            )
            if beta is None or not np.isfinite(beta):
                raise RuntimeError(
                    f"Missing frozen beta_pre for {ticker} at {day_key}; imputation is forbidden"
                )
            beta_cache[key] = float(beta)

        values[position] = beta_cache[key]

    return values


def encode_unique_news(news: pd.DataFrame, *, encoder=None) -> tuple[np.ndarray, str]:
    """Encode one normalized SBERT vector per unique news_id."""

    version = "provided_encoder"
    if encoder is None:
        try:
            import sentence_transformers
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "V5 builder requires the optional 'v5-builder' dependencies; "
                "install with: python -m pip install -e '.[v5-builder]'"
            ) from exc
        version = str(sentence_transformers.__version__)
        encoder = SentenceTransformer(SBERT_MODEL)

    texts = [legacy_embedding_text(text) for text in news["news_text"].tolist()]
    embeddings = encoder.encode(
        texts,
        batch_size=SBERT_BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.shape != (len(news), SBERT_DIMENSIONS):
        raise RuntimeError(
            f"SBERT output shape {embeddings.shape} != ({len(news)}, {SBERT_DIMENSIONS})"
        )
    if not np.isfinite(embeddings).all():
        raise RuntimeError("SBERT produced non-finite embeddings")

    norms = np.linalg.norm(embeddings.astype(np.float64), axis=1)
    if not np.allclose(norms, 1.0, rtol=0.0, atol=1.0e-4):
        raise RuntimeError("SBERT embeddings are not unit-normalized as frozen by Phase 2")

    return np.ascontiguousarray(embeddings, dtype=np.float32), version


def build_v5_feature_matrix(
    news: pd.DataFrame,
    pairs: pd.DataFrame,
    *,
    beta_pre: np.ndarray,
    embeddings: np.ndarray,
) -> np.ndarray:
    """Assemble 384 SBERT + 5 text + 1 beta_pre in pair-row order."""

    if len(beta_pre) != len(pairs):
        raise ValueError("beta_pre row count must equal V5 pair count")
    if embeddings.shape != (len(news), SBERT_DIMENSIONS):
        raise ValueError("embeddings must align one-to-one with V5 news rows")

    text_features = legacy_text_feature_matrix(news["news_text"].tolist())
    news_index = {nid: i for i, nid in enumerate(news["news_id"].tolist())}

    try:
        pair_news_index = np.fromiter(
            (news_index[nid] for nid in pairs["news_id"].tolist()),
            dtype=np.int64,
            count=len(pairs),
        )
    except KeyError as exc:
        raise ValueError(f"V5 pair references unknown news_id: {exc}") from exc

    X = assemble_exante_feature_matrix(
        embeddings[pair_news_index],
        text_features[pair_news_index],
        beta_pre,
    )

    if X.shape != (len(pairs), EXPECTED_FEATURE_COUNT):
        raise RuntimeError("V5 ex-ante matrix does not contain exactly 390 features")
    if X.dtype != np.float32 or not np.isfinite(X).all():
        raise RuntimeError("V5 ex-ante matrix must be finite float32")

    return X


def fetch_v5_documents_from_mongo() -> list[dict]:
    """Read only the projected outcome-free fields used by the legacy scorer."""

    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError(
            "V5 builder requires the optional 'v5-builder' dependencies; "
            "install with: python -m pip install -e '.[v5-builder]'"
        ) from exc

    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        password = os.getenv("db_password")
        if not password:
            raise RuntimeError("Missing MONGO_URI or db_password for read-only V5 source query")
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
                        "$gte": V5_START.strftime("%Y-%m-%d"),
                        "$lte": V5_END.strftime("%Y-%m-%d"),
                    }
                },
                {
                    "text": 1,
                    "date": 1,
                    "matched_tickers": 1,
                },
            )
        )
    finally:
        client.close()

    return documents


def canonical_source_sha256(documents: Iterable[Mapping]) -> str:
    """Hash the projected Mongo snapshot without serializing credentials."""

    canonical = []
    for doc in documents:
        matches = []
        for match in doc.get("matched_tickers", []):
            if isinstance(match, Mapping) and match.get("ticker"):
                matches.append(_canonical_ticker(match["ticker"]))
        canonical.append(
            {
                "news_id": str(doc.get("_id", "")),
                "date": str(doc.get("date", "")),
                "text": str(doc.get("text", "")),
                "matched_tickers": sorted(set(matches)),
            }
        )
    canonical.sort(key=lambda item: (item["date"], item["news_id"]))
    payload = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def require_outputs_absent() -> None:
    existing = [
        path
        for path in (V5_ROWS_OUTPUT, V5_FEATURES_OUTPUT, V5_BUILD_SUMMARY_OUTPUT)
        if path.exists()
    ]
    if existing:
        raise RuntimeError(
            "V5 ex-ante artifact builder refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def main() -> None:
    require_outputs_absent()

    allowed_tickers = load_frozen_phase2_universe()
    documents = fetch_v5_documents_from_mongo()
    source_sha256 = canonical_source_sha256(documents)

    news, pairs = extract_v5_news_and_pairs(
        documents,
        allowed_tickers=allowed_tickers,
    )

    prices = load_exante_price_cache()
    beta_pre = beta_pre_for_pairs(pairs, prices)
    embeddings, sentence_transformers_version = encode_unique_news(news)
    features = build_v5_feature_matrix(
        news,
        pairs,
        beta_pre=beta_pre,
        embeddings=embeddings,
    )

    candidate_rows = pairs[["news_id", "ticker", "date_dt"]].copy()
    candidate_rows, features = validate_v5_inputs(candidate_rows, features)

    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    candidate_rows.to_pickle(V5_ROWS_OUTPUT)
    np.save(V5_FEATURES_OUTPUT, features, allow_pickle=False)

    summary = {
        "stage": "DTRM_PHASE3_MM1_V5_EXANTE_ARTIFACT_BUILDER",
        "status": "built_outcome_blind_pending_decision_freeze",
        "window": {
            "start": V5_START.isoformat(),
            "end": V5_END.isoformat(),
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
            "sbert_model": SBERT_MODEL,
            "sbert_dimensions": SBERT_DIMENSIONS,
            "sbert_normalize": True,
            "sbert_max_chars": SBERT_MAX_CHARS,
            "sentence_transformers_version": sentence_transformers_version,
            "text_feature_count": 5,
            "beta_feature_count": 1,
            "ret_spy_evt_included": False,
        },
        "beta_pre": {
            "lookback": BETA_LOOKBACK,
            "min_observations": BETA_MIN_OBSERVATIONS,
            "tolerance_days": BETA_TOLERANCE_DAYS,
            "post_event_prices_passed_to_beta": False,
            "missing_or_imputed": 0,
        },
        "price_snapshot_loader": "run_exante_baseline_v0.load_exante_price_cache",
        "information_firewall": {
            "target_model_accessed": False,
            "forward_target_computed": False,
            "realized_forward_returns_accessed": False,
        },
        "outputs": {
            "candidate_rows": str(V5_ROWS_OUTPUT.relative_to(REPO_ROOT)),
            "candidate_rows_sha256": sha256_file(V5_ROWS_OUTPUT),
            "features": str(V5_FEATURES_OUTPUT.relative_to(REPO_ROOT)),
            "features_sha256": sha256_file(V5_FEATURES_OUTPUT),
        },
    }

    V5_BUILD_SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V5 EX-ANTE ARTIFACT BUILD")
    print("outcome firewall: PASS")
    print("source documents:", len(documents))
    print("unique news:", len(news))
    print("pair rows:", len(candidate_rows))
    print("canonical tickers:", candidate_rows["ticker"].nunique())
    print("features:", features.shape)
    print("candidate rows:", V5_ROWS_OUTPUT)
    print("feature matrix:", V5_FEATURES_OUTPUT)
    print("summary:", V5_BUILD_SUMMARY_OUTPUT)


if __name__ == "__main__":
    main()
