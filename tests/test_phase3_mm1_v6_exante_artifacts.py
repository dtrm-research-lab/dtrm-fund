from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import build_phase3_mm1_v6_exante_artifacts as v6


def _rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": [
                "2026-06-26T00:00:00Z",
                "2026-07-01T12:00:00Z",
                "2026-07-06T23:59:59Z",
            ],
        }
    )


def _features(rows: int = 3, columns: int = 390) -> np.ndarray:
    return np.zeros((rows, columns), dtype=np.float32)


def test_v6_window_matches_preregistered_replication_contract():
    assert v6.V6_START == pd.Timestamp("2026-06-26T00:00:00Z")
    assert v6.V6_END == pd.Timestamp("2026-07-06T23:59:59Z")
    assert v6.EXPECTED_FEATURE_COUNT == 390


def test_validate_v6_inputs_accepts_exact_outcome_blind_schema():
    rows, features = v6.validate_v6_inputs(_rows(), _features())
    assert list(rows.columns) == ["news_id", "ticker", "date_dt"]
    assert features.shape == (3, 390)
    assert features.dtype == np.float32
    assert str(rows["date_dt"].dt.tz) == "UTC"


def test_validate_v6_inputs_rejects_extra_columns():
    rows = _rows()
    rows["target_model"] = 0.0
    with pytest.raises(ValueError, match="unexpected columns"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_duplicate_pairs():
    rows = _rows()
    rows.loc[1, ["news_id", "ticker"]] = rows.loc[0, ["news_id", "ticker"]]
    with pytest.raises(ValueError, match="duplicate"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_outside_preregistered_window():
    rows = _rows()
    rows.loc[0, "date_dt"] = "2026-06-25T23:59:59Z"
    with pytest.raises(ValueError, match="outside"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_wrong_feature_width():
    with pytest.raises(ValueError, match="exactly 390"):
        v6.validate_v6_inputs(_rows(), _features(columns=389))


def test_extract_v6_news_and_pairs_filters_window_and_universe():
    documents = [
        {
            "_id": "before",
            "date": "2026-06-25",
            "text": "before",
            "matched_tickers": [{"ticker": "AAA"}],
        },
        {
            "_id": "keep1",
            "date": "2026-06-26",
            "text": "hello",
            "matched_tickers": [{"ticker": "BBB"}, {"ticker": "AAA"}],
        },
        {
            "_id": "keep2",
            "date": "2026-07-06",
            "text": "world",
            "matched_tickers": [{"ticker": "CCC"}, {"ticker": "ZZZ"}],
        },
        {
            "_id": "after",
            "date": "2026-07-07",
            "text": "after",
            "matched_tickers": [{"ticker": "AAA"}],
        },
    ]

    news, pairs = v6.extract_v6_news_and_pairs(
        documents,
        allowed_tickers={"AAA", "BBB", "CCC"},
    )

    assert set(news["news_id"]) == {"keep1", "keep2"}
    assert set(zip(pairs["news_id"], pairs["ticker"])) == {
        ("keep1", "AAA"),
        ("keep1", "BBB"),
        ("keep2", "CCC"),
    }
    assert not pairs.duplicated(["news_id", "ticker"]).any()


def test_extract_v6_normalizes_brk_dot_b_like_v5():
    documents = [
        {
            "_id": "n1",
            "date": "2026-07-01",
            "text": "Berkshire news",
            "matched_tickers": [{"ticker": "BRK.B"}],
        }
    ]
    _, pairs = v6.extract_v6_news_and_pairs(
        documents,
        allowed_tickers={"BRK-B"},
    )
    assert pairs["ticker"].tolist() == ["BRK-B"]


def test_builder_source_contains_no_v6_realized_target_or_price_output_path():
    source = (
        EXPERIMENTS / "build_phase3_mm1_v6_exante_artifacts.py"
    ).read_text()

    forbidden = (
        "phase3_mm1_v6_target_model.pkl",
        "phase3_mm1_v6_target.pkl",
        "phase3_mm1_v6_price_snapshot.pkl",
        "forward_excess_beta_target",
    )
    for token in forbidden:
        assert token not in source


def test_builder_explicitly_preserves_v5_policy_and_outcome_firewall():
    source = (
        EXPERIMENTS / "build_phase3_mm1_v6_exante_artifacts.py"
    ).read_text()
    assert '"V5_results_used_to_change_V6_policy": False' in source
    assert '"V6_policy_changed_from_frozen_V5": False' in source
    assert '"evaluation_before_2026_09_04": "forbidden"' in source
