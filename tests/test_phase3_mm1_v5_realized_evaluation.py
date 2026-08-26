from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import run_phase3_mm1_v5_realized_evaluation as realized


def _signals() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3", "n4"],
            "ticker": ["AAA", "BBB", "CCC", "DDD"],
            "date_dt": pd.to_datetime(
                ["2026-06-15", "2026-06-16", "2026-06-17", "2026-06-18"],
                utc=True,
            ),
        }
    )


def _identity(signals: pd.DataFrame, position: int) -> dict:
    row = signals.iloc[position]
    return {
        "news_id": row["news_id"],
        "ticker": row["ticker"],
        "date_dt": pd.Timestamp(row["date_dt"]).isoformat(),
        "baseline_rank": position,
    }


def test_selection_positions_maps_frozen_identities_exactly():
    signals = _signals()
    identities = [_identity(signals, 2), _identity(signals, 0)]

    positions = realized.selection_positions(signals, identities, k=2)

    np.testing.assert_array_equal(positions, np.array([2, 0]))


def test_selection_positions_rejects_missing_identity():
    signals = _signals()
    missing = _identity(signals, 0)
    missing["news_id"] = "missing"

    with pytest.raises(RuntimeError, match="absent"):
        realized.selection_positions(signals, [missing], k=1)


def test_price_series_by_ticker_is_ordered_and_date_only():
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "SPY", "SPY"],
            "date": ["2026-06-16", "2026-06-15", "2026-06-16", "2026-06-15"],
            "close": [101.0, 100.0, 202.0, 200.0],
        }
    )

    result = realized.price_series_by_ticker(prices)

    assert [item[1] for item in result["AAA"]] == [100.0, 101.0]
    assert result["AAA"][0][0].isoformat() == "2026-06-15"


def test_build_v5_raw_targets_uses_frozen_beta_and_forward_window():
    signals = pd.DataFrame(
        {
            "news_id": ["n1"],
            "ticker": ["AAA"],
            "date_dt": pd.to_datetime(["2026-06-15"], utc=True),
        }
    )
    beta = np.array([2.0], dtype=np.float64)
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA", "SPY", "SPY"],
            "date": ["2026-06-15", "2026-08-14", "2026-06-15", "2026-08-14"],
            "close": [100.0, 120.0, 200.0, 210.0],
        }
    )

    raw = realized.build_v5_raw_targets(signals, beta, prices)

    # Stock +20%; SPY +5%; beta=2 => excess-beta target +10%.
    assert raw[0] == pytest.approx(0.10, abs=1e-12)


def test_build_v5_raw_targets_refuses_incomplete_target():
    signals = pd.DataFrame(
        {
            "news_id": ["n1"],
            "ticker": ["AAA"],
            "date_dt": pd.to_datetime(["2026-06-15"], utc=True),
        }
    )
    beta = np.array([1.0], dtype=np.float64)
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "SPY"],
            "date": ["2026-06-15", "2026-06-15"],
            "close": [100.0, 200.0],
        }
    )

    with pytest.raises(RuntimeError, match="INFEASIBLE"):
        realized.build_v5_raw_targets(signals, beta, prices)


def _manifest(signals: pd.DataFrame, *, intervention: bool = True, lift: float = 0.01):
    return {
        "cohort_structure": {"K_H": 2},
        "decision": {
            "phase2_champion_row_identities": [
                _identity(signals, 0),
                _identity(signals, 1),
            ],
            "MM1_selected_row_identities": [
                _identity(signals, 0),
                _identity(signals, 2),
            ],
            "intervention": intervention,
            "robust_lift": lift,
        },
    }


def test_evaluate_frozen_actions_promotes_positive_realized_delta():
    signals = _signals()
    target = np.array([0.10, -0.10, 0.30, 0.0], dtype=np.float32)

    result = realized.evaluate_frozen_actions(signals, target, _manifest(signals))

    assert result["phase2_value"] == pytest.approx(0.0, abs=1e-12)
    assert result["MM1_value"] == pytest.approx(0.20, abs=1e-8)
    assert result["delta_topk_mean_target_model_vs_phase2"] > 0.0
    assert result["classification"] == "PROMOTED_POINT"
    assert result["promoted"] is True


def test_evaluate_frozen_actions_rejects_nonpositive_realized_delta():
    signals = _signals()
    target = np.array([0.10, 0.20, -0.30, 0.0], dtype=np.float32)

    result = realized.evaluate_frozen_actions(signals, target, _manifest(signals))

    assert result["delta_topk_mean_target_model_vs_phase2"] < 0.0
    assert result["classification"] == "NOT_PROMOTED_REALIZED"
    assert result["promoted"] is False


def test_evaluate_frozen_actions_no_incremental_action_is_exact_zero():
    signals = _signals()
    manifest = _manifest(signals, intervention=False, lift=0.0)
    manifest["decision"]["MM1_selected_row_identities"] = list(
        manifest["decision"]["phase2_champion_row_identities"]
    )
    target = np.array([0.10, -0.20, 0.30, 0.0], dtype=np.float32)

    result = realized.evaluate_frozen_actions(signals, target, manifest)

    assert result["same_action"] is True
    assert result["delta_topk_mean_target_model_vs_phase2"] == 0.0
    assert result["delta_topk_hit_rate"] == 0.0
    assert result["classification"] == "NO_INCREMENTAL_ACTION"
    assert result["promoted"] is False


def test_evaluate_frozen_actions_requires_strict_exante_lift_for_intervention():
    signals = _signals()
    target = np.array([0.10, -0.10, 0.30, 0.0], dtype=np.float32)

    with pytest.raises(RuntimeError, match="strict robust lift"):
        realized.evaluate_frozen_actions(
            signals,
            target,
            _manifest(signals, intervention=True, lift=1e-13),
        )


def test_runner_source_never_calls_optimizer():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_realized_evaluation.py"
    ).read_text()

    assert "optimize_mm1" not in source
    assert "phase3_mm1_optimizer" not in source


def test_runner_binds_beta_to_frozen_feature_column():
    assert realized.EXPECTED_FEATURE_COUNT == 390
    assert realized.BETA_FEATURE_INDEX == 389
