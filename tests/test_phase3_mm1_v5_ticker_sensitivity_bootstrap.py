from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import run_phase3_mm1_v5_ticker_sensitivity_bootstrap as ticker_boot


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": [f"n{i}" for i in range(8)],
            "ticker": ["A", "A", "B", "B", "C", "C", "D", "D"],
            "date_dt_signal": pd.to_datetime(["2026-06-15"] * 8, utc=True),
            "baseline_point_score": np.linspace(1.0, 0.2, 8),
            "raw_p10": np.linspace(0.8, 0.1, 8),
            "target_model": np.linspace(-0.2, 0.3, 8),
        }
    )


def test_ticker_sensitivity_constants_are_preregistered():
    assert ticker_boot.REPLICATES == 10_000
    assert ticker_boot.SEED == 20260828
    assert ticker_boot.TOPK_FRACTION == 0.10
    assert ticker_boot.CONFIDENCE_LEVEL == 0.95


def test_ticker_bootstrap_resamples_ticker_clusters(monkeypatch):
    frame = _frame()
    observed = []

    def fake_eval(_frame, multiplicity):
        observed.append(np.asarray(multiplicity, dtype=np.int64).copy())
        return {
            "delta_topk_mean_target_model_vs_phase2": 0.1,
            "delta_topk_hit_rate": 0.2,
            "hierarchy": "unique_primary_band",
        }

    monkeypatch.setattr(ticker_boot.exact, "evaluate_resampled_policy_exact", fake_eval)
    result = ticker_boot.cluster_bootstrap_ticker_exact(
        frame,
        rng=np.random.default_rng(123),
        replicates=3,
    )

    assert len(observed) == 3
    for multiplicity in observed:
        assert multiplicity[0] == multiplicity[1]
        assert multiplicity[2] == multiplicity[3]
        assert multiplicity[4] == multiplicity[5]
        assert multiplicity[6] == multiplicity[7]
    assert result[2] == 0
    assert result[3] == {"unique_primary_band": 3}


def test_ticker_bootstrap_is_deterministic_for_same_seed(monkeypatch):
    frame = _frame()

    def fake_eval(_frame, multiplicity):
        value = float(np.mean(multiplicity))
        return {
            "delta_topk_mean_target_model_vs_phase2": value,
            "delta_topk_hit_rate": value / 10.0,
            "hierarchy": "exact_exchangeable_tie_hierarchy",
        }

    monkeypatch.setattr(ticker_boot.exact, "evaluate_resampled_policy_exact", fake_eval)
    first = ticker_boot.cluster_bootstrap_ticker_exact(
        frame,
        rng=np.random.default_rng(77),
        replicates=5,
    )
    second = ticker_boot.cluster_bootstrap_ticker_exact(
        frame,
        rng=np.random.default_rng(77),
        replicates=5,
    )

    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(first[1], second[1])
    assert first[2:] == second[2:]


def test_ticker_bootstrap_reports_infeasible_replicates(monkeypatch):
    frame = _frame()
    calls = {"n": 0}

    def fake_eval(_frame, _multiplicity):
        calls["n"] += 1
        if calls["n"] == 2:
            return None
        return {
            "delta_topk_mean_target_model_vs_phase2": 0.1,
            "delta_topk_hit_rate": 0.2,
            "hierarchy": "unique_primary_band",
        }

    monkeypatch.setattr(ticker_boot.exact, "evaluate_resampled_policy_exact", fake_eval)
    delta_mean, delta_hit, infeasible, hierarchy = (
        ticker_boot.cluster_bootstrap_ticker_exact(
            frame,
            rng=np.random.default_rng(1),
            replicates=3,
        )
    )

    assert infeasible == 1
    assert np.isnan(delta_mean[1])
    assert np.isnan(delta_hit[1])
    assert hierarchy == {"unique_primary_band": 2}


def test_ticker_runner_source_preserves_sensitivity_only_governance():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_ticker_sensitivity_bootstrap.py"
    ).read_text()

    assert 'frame["ticker"]' in source
    assert "SEED = 20260828" in source
    assert '"role": "sensitivity_only"' in source
    assert '"promotion_role": "none"' in source
    assert '"V5_policy_changed": False' in source
    assert '"V6_policy_change_permitted_from_V5": False' in source
