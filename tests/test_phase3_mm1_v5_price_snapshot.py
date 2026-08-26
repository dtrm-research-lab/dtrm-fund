from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import build_phase3_mm1_v5_price_snapshot as snap


def _signals() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": ["n1", "n2"],
            "ticker": ["AAA", "BBB"],
            "date_dt": pd.to_datetime(["2026-06-15", "2026-06-16"], utc=True),
            "baseline_point_score": [0.2, 0.1],
            "baseline_rank": [0, 1],
            "raw_p10": [-0.1, -0.2],
            "calibrated_p10": [-0.16, -0.26],
            "phase2_guardrail_pass": [True, False],
        }
    )


def _prices() -> pd.DataFrame:
    rows = []
    for ticker in ("AAA", "BBB", "SPY"):
        rows.extend(
            [
                {"ticker": ticker, "date": "2026-06-15", "close": 100.0},
                {"ticker": ticker, "date": "2026-08-24", "close": 110.0},
                {"ticker": ticker, "date": "2026-08-26", "close": 111.0},
            ]
        )
    return pd.DataFrame(rows, columns=["ticker", "date", "close"])


def test_required_tickers_include_spy_and_are_sorted():
    assert snap.required_tickers_from_signals(_signals()) == ("AAA", "BBB", "SPY")


def test_validate_price_snapshot_accepts_complete_exact_schema():
    result = snap.validate_price_snapshot(
        _prices(),
        required_tickers=("AAA", "BBB", "SPY"),
    )

    assert list(result.columns) == ["ticker", "date", "close"]
    assert len(result) == 9
    assert result["date"].max() == pd.Timestamp("2026-08-26")


def test_validate_price_snapshot_rejects_missing_required_ticker():
    prices = _prices().query("ticker != 'BBB'")
    with pytest.raises(ValueError, match="missing required tickers"):
        snap.validate_price_snapshot(
            prices,
            required_tickers=("AAA", "BBB", "SPY"),
        )


def test_validate_price_snapshot_rejects_unexpected_ticker():
    prices = pd.concat(
        [
            _prices(),
            pd.DataFrame(
                [{"ticker": "ZZZ", "date": "2026-08-24", "close": 1.0}]
            ),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="unexpected tickers"):
        snap.validate_price_snapshot(
            prices,
            required_tickers=("AAA", "BBB", "SPY"),
        )


def test_validate_price_snapshot_rejects_duplicate_ticker_date():
    prices = pd.concat([_prices(), _prices().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        snap.validate_price_snapshot(
            prices,
            required_tickers=("AAA", "BBB", "SPY"),
        )


def test_validate_price_snapshot_rejects_stale_ticker():
    prices = _prices()
    prices = prices[
        ~((prices["ticker"] == "BBB") & (prices["date"] != "2026-06-15"))
    ].copy()
    with pytest.raises(ValueError, match="required V5 market date"):
        snap.validate_price_snapshot(
            prices,
            required_tickers=("AAA", "BBB", "SPY"),
        )


def test_fetch_ticker_prices_uses_params_without_embedding_api_key_in_url():
    payload = {
        "historical": [
            {"date": "2026-08-24", "close": 123.0},
        ]
    }

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    class Session:
        def __init__(self):
            self.url = None
            self.params = None

        def get(self, url, params, timeout):
            self.url = url
            self.params = params
            assert timeout == 30
            return Response()

    session = Session()
    result = snap.fetch_ticker_prices(
        session,
        api_key="SECRET",
        ticker="AAA",
        retries=1,
    )

    assert "SECRET" not in session.url
    assert session.params["apikey"] == "SECRET"
    assert result.loc[0, "ticker"] == "AAA"


def test_sha256_file_matches_known_digest(tmp_path):
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"abc")
    assert snap.sha256_file(path) == hashlib.sha256(b"abc").hexdigest()


def test_builder_source_does_not_compute_realized_comparison_or_reoptimize():
    source = (
        EXPERIMENTS / "build_phase3_mm1_v5_price_snapshot.py"
    ).read_text()

    forbidden = (
        "optimize_mm1(",
        "target_model =",
        "realized_delta",
        "PROMOTED_POINT",
        "NOT_PROMOTED_REALIZED",
    )
    for token in forbidden:
        assert token not in source
