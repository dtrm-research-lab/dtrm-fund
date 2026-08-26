from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import build_phase3_mm1_v5_exante_artifacts as builder


def _documents():
    return [
        {
            "_id": "n2",
            "date": "2026-06-20",
            "text": " Second\nheadline ",
            "matched_tickers": [
                {"ticker": "BRK.B"},
                {"ticker": "ZZZ"},
            ],
        },
        {
            "_id": "n1",
            "date": "2026-06-15",
            "text": " First headline ",
            "matched_tickers": [
                {"ticker": "AAPL"},
                {"ticker": "BRK.B"},
            ],
        },
    ]


def test_legacy_embedding_text_matches_frozen_normalization():
    raw = "  Hello\nWORLD  " + ("x" * 2000)
    normalized = builder.legacy_embedding_text(raw)

    assert normalized.startswith("Hello WORLD")
    assert "\n" not in normalized
    assert len(normalized) == builder.SBERT_MAX_CHARS


def test_extract_v5_news_pairs_filters_universe_normalizes_ticker_and_orders():
    news, pairs = builder.extract_v5_news_and_pairs(
        _documents(),
        allowed_tickers={"AAPL", "BRK-B"},
    )

    assert news["news_id"].tolist() == ["n1", "n2"]
    assert news["news_text"].tolist() == ["First headline", "Second headline"]
    assert set(pairs["ticker"]) == {"AAPL", "BRK-B"}
    assert "ZZZ" not in set(pairs["ticker"])
    assert not pairs.duplicated(["news_id", "ticker"]).any()
    assert pairs["ticker"].tolist() == sorted(pairs["ticker"].tolist())


def test_extract_v5_news_pairs_ignores_outside_window_and_empty_text():
    documents = [
        {
            "_id": "old",
            "date": "2026-06-14",
            "text": "outside",
            "matched_tickers": [{"ticker": "AAPL"}],
        },
        {
            "_id": "empty",
            "date": "2026-06-15",
            "text": "   ",
            "matched_tickers": [{"ticker": "AAPL"}],
        },
    ]

    with pytest.raises(RuntimeError, match="No valid V5"):
        builder.extract_v5_news_and_pairs(
            documents,
            allowed_tickers={"AAPL"},
        )


def test_extract_v5_news_pairs_rejects_duplicate_news_ids():
    documents = [_documents()[0], dict(_documents()[0])]

    with pytest.raises(ValueError, match="Duplicate V5 news_id"):
        builder.extract_v5_news_and_pairs(
            documents,
            allowed_tickers={"BRK-B"},
        )


def test_price_history_is_cut_off_at_event_date():
    prices = [
        ("2026-06-14", 10.0),
        ("2026-06-15", 11.0),
        ("2026-06-16", 999.0),
    ]

    result = builder.price_history_on_or_before(prices, "2026-06-15T12:00:00Z")

    assert result == prices[:2]


def test_beta_pre_uses_only_event_time_history_and_caches_same_ticker_day(monkeypatch):
    pairs = pd.DataFrame(
        {
            "news_id": ["n1", "n2"],
            "ticker": ["AAA", "AAA"],
            "date_dt": pd.to_datetime(
                ["2026-06-15T00:00:00Z", "2026-06-15T00:00:00Z"],
                utc=True,
            ),
        }
    )
    prices = {
        "AAA": [("2026-06-14", 10.0), ("2026-06-15", 11.0), ("2026-06-16", 999.0)],
        "SPY": [("2026-06-14", 20.0), ("2026-06-15", 21.0), ("2026-06-16", 999.0)],
    }
    calls = []

    def fake_beta(**kwargs):
        calls.append(kwargs)
        assert max(pd.Timestamp(d) for d, _ in kwargs["stock_prices"]) <= pd.Timestamp("2026-06-15")
        assert max(pd.Timestamp(d) for d, _ in kwargs["market_prices"]) <= pd.Timestamp("2026-06-15")
        assert kwargs["lookback"] == 252
        assert kwargs["min_observations"] == 60
        assert kwargs["tolerance_days"] == 20
        return 1.25

    monkeypatch.setattr(builder, "legacy_beta_pre_from_prices", fake_beta)

    values = builder.beta_pre_for_pairs(pairs, prices)

    assert np.allclose(values, [1.25, 1.25])
    assert len(calls) == 1


def test_beta_pre_rejects_missing_ticker_price_cache():
    pairs = pd.DataFrame(
        {
            "news_id": ["n1"],
            "ticker": ["AAA"],
            "date_dt": pd.to_datetime(["2026-06-15"], utc=True),
        }
    )

    with pytest.raises(RuntimeError, match="missing ticker AAA"):
        builder.beta_pre_for_pairs(pairs, {"SPY": [("2026-06-15", 1.0)]})


class _FakeEncoder:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((list(texts), dict(kwargs)))
        result = np.zeros((len(texts), 384), dtype=np.float32)
        for row in range(len(texts)):
            result[row, row] = 1.0
        return result


def test_encode_unique_news_freezes_model_call_semantics():
    news = pd.DataFrame(
        {
            "news_id": ["n1", "n2"],
            "date_dt": pd.to_datetime(["2026-06-15", "2026-06-16"], utc=True),
            "news_text": ["hello", "world"],
        }
    )
    encoder = _FakeEncoder()

    embeddings, version = builder.encode_unique_news(news, encoder=encoder)

    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32
    assert version == "provided_encoder"
    texts, kwargs = encoder.calls[0]
    assert texts == ["hello", "world"]
    assert kwargs["batch_size"] == 16
    assert kwargs["normalize_embeddings"] is True


def test_encode_unique_news_rejects_non_unit_embeddings():
    news = pd.DataFrame(
        {
            "news_id": ["n1"],
            "date_dt": pd.to_datetime(["2026-06-15"], utc=True),
            "news_text": ["hello"],
        }
    )

    class BadEncoder:
        def encode(self, texts, **kwargs):
            return np.ones((1, 384), dtype=np.float32)

    with pytest.raises(RuntimeError, match="not unit-normalized"):
        builder.encode_unique_news(news, encoder=BadEncoder())


def test_build_feature_matrix_is_exact_390_and_pair_aligned():
    news = pd.DataFrame(
        {
            "news_id": ["n1", "n2"],
            "date_dt": pd.to_datetime(["2026-06-15", "2026-06-16"], utc=True),
            "news_text": ["AAA!", "BBB?"],
        }
    )
    pairs = pd.DataFrame(
        {
            "news_id": ["n2", "n1"],
            "ticker": ["BBB", "AAA"],
            "date_dt": pd.to_datetime(["2026-06-16", "2026-06-15"], utc=True),
        }
    )
    embeddings = np.zeros((2, 384), dtype=np.float32)
    embeddings[0, 0] = 1.0
    embeddings[1, 1] = 1.0
    beta = np.array([2.0, 3.0])

    X = builder.build_v5_feature_matrix(
        news,
        pairs,
        beta_pre=beta,
        embeddings=embeddings,
    )

    assert X.shape == (2, 390)
    assert X.dtype == np.float32
    assert X[0, 1] == 1.0
    assert X[1, 0] == 1.0
    assert X[0, -1] == 2.0
    assert X[1, -1] == 3.0


def test_canonical_source_hash_is_document_order_independent():
    docs = _documents()
    forward = builder.canonical_source_sha256(docs)
    reverse = builder.canonical_source_sha256(list(reversed(docs)))

    assert forward == reverse
    assert len(forward) == 64
    int(forward, 16)


def test_sha256_file_matches_known_digest(tmp_path):
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"abc")

    assert builder.sha256_file(path) == hashlib.sha256(b"abc").hexdigest()


def test_builder_source_has_no_v5_outcome_construction_or_artifact_path():
    source = (
        EXPERIMENTS / "build_phase3_mm1_v5_exante_artifacts.py"
    ).read_text()

    forbidden = (
        "from dtrm.exante_target import",
        "forward_excess_beta_target(",
        "phase3_mm1_v5_target",
        "phase3_mm1_v5_model_target",
        "target_model.pkl",
    )
    for token in forbidden:
        assert token not in source
