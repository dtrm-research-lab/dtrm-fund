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

import run_phase3_mm1_v5_primary_bootstrap as boot


def _frame(n: int = 20) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": [f"n{i // 2}" for i in range(n)],
            "ticker": [f"T{i}" for i in range(n)],
            "date_dt_signal": pd.to_datetime(
                ["2026-06-15"] * n,
                utc=True,
            ),
            "baseline_point_score": np.linspace(1.0, 0.1, n),
            "raw_p10": np.full(n, 0.1),
            "target_model": np.linspace(-0.2, 0.3, n),
        }
    )


def test_frozen_primary_bootstrap_constants():
    assert boot.REPLICATES == 10_000
    assert boot.SEED == 20260827
    assert boot.TOPK_FRACTION == 0.10
    assert boot.CONFIDENCE_LEVEL == 0.95


def test_resampled_row_indices_duplicate_all_rows_of_repeated_cluster():
    class FakeRNG:
        def integers(self, low, high, size):
            assert low == 0
            assert high == 3
            assert size == 3
            return np.array([0, 0, 2], dtype=np.int64)

    cluster_codes = np.array([0, 0, 1, 2, 2], dtype=np.int64)
    result = boot.resampled_row_indices(
        cluster_codes,
        n_clusters=3,
        rng=FakeRNG(),
    )

    assert result.tolist() == [0, 0, 1, 1, 3, 4]


def test_evaluate_resampled_policy_recomputes_k_and_calls_optimizer(monkeypatch):
    frame = _frame(20)
    observed = {}

    def fake_optimize(state):
        observed["rows"] = state.rows
        observed["k"] = int(state.rows * 0.10)
        return SimpleNamespace(
            k=2,
            champion_indices=np.array([0, 1], dtype=np.int64),
            selected_indices=np.array([18, 19], dtype=np.int64),
        )

    monkeypatch.setattr(boot, "optimize_mm1", fake_optimize)
    result = boot.evaluate_resampled_policy(frame, np.arange(20, dtype=np.int64))

    assert observed == {"rows": 20, "k": 2}
    assert result["K_H"] == 2
    assert result["delta_topk_mean_target_model_vs_phase2"] > 0.0
    assert result["delta_topk_hit_rate"] > 0.0


def test_evaluate_resampled_policy_returns_none_when_frozen_policy_is_infeasible(monkeypatch):
    frame = _frame(20)

    def fake_optimize(_state):
        raise ValueError("Phase-2 eligible pool cannot fill the frozen Top-K")

    monkeypatch.setattr(boot, "optimize_mm1", fake_optimize)
    assert boot.evaluate_resampled_policy(frame, np.arange(20, dtype=np.int64)) is None


def test_evaluate_resampled_policy_propagates_unrelated_optimizer_errors(monkeypatch):
    frame = _frame(20)

    def fake_optimize(_state):
        raise ValueError("different failure")

    monkeypatch.setattr(boot, "optimize_mm1", fake_optimize)
    with pytest.raises(ValueError, match="different failure"):
        boot.evaluate_resampled_policy(frame, np.arange(20, dtype=np.int64))


def test_reproduce_frozen_point_uses_only_manifest_identities():
    frame = _frame(4)
    manifest = {
        "cohort_structure": {"K_H": 2},
        "decision": {
            "phase2_champion_row_identities": [
                {
                    "news_id": "n0",
                    "ticker": "T0",
                    "date_dt": "2026-06-15T00:00:00+00:00",
                },
                {
                    "news_id": "n0",
                    "ticker": "T1",
                    "date_dt": "2026-06-15T00:00:00+00:00",
                },
            ],
            "MM1_selected_row_identities": [
                {
                    "news_id": "n1",
                    "ticker": "T2",
                    "date_dt": "2026-06-15T00:00:00+00:00",
                },
                {
                    "news_id": "n1",
                    "ticker": "T3",
                    "date_dt": "2026-06-15T00:00:00+00:00",
                },
            ],
        },
    }

    result = boot.reproduce_frozen_point(frame, manifest)
    expected_phase2 = float(frame.loc[[0, 1], "target_model"].mean())
    expected_mm1 = float(frame.loc[[2, 3], "target_model"].mean())

    assert result["phase2_value"] == pytest.approx(expected_phase2)
    assert result["MM1_value"] == pytest.approx(expected_mm1)
    assert result["delta_topk_mean_target_model_vs_phase2"] == pytest.approx(
        expected_mm1 - expected_phase2
    )


def test_percentile_interval_uses_linear_95_percent_interval():
    values = np.arange(100, dtype=np.float64)
    result = boot.percentile_interval(values)
    expected = [
        float(np.quantile(values, 0.025, method="linear")),
        float(np.quantile(values, 0.975, method="linear")),
    ]
    assert result == expected


def test_percentile_interval_rejects_nan_values():
    with pytest.raises(ValueError, match="finite"):
        boot.percentile_interval(np.array([0.0, np.nan, 1.0]))


def test_cluster_bootstrap_is_deterministic_for_same_seed(monkeypatch):
    frame = _frame(20)

    def fake_evaluate(_frame, idx):
        value = float(np.mean(idx))
        return {
            "delta_topk_mean_target_model_vs_phase2": value,
            "delta_topk_hit_rate": value / 100.0,
        }

    monkeypatch.setattr(boot, "evaluate_resampled_policy", fake_evaluate)

    first = boot.cluster_bootstrap(
        frame,
        rng=np.random.default_rng(123),
        replicates=5,
    )
    second = boot.cluster_bootstrap(
        frame,
        rng=np.random.default_rng(123),
        replicates=5,
    )

    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(first[1], second[1])
    assert first[2] == second[2] == 0


def test_cluster_bootstrap_reports_infeasible_replicates(monkeypatch):
    frame = _frame(20)
    calls = {"n": 0}

    def fake_evaluate(_frame, _idx):
        calls["n"] += 1
        if calls["n"] == 2:
            return None
        return {
            "delta_topk_mean_target_model_vs_phase2": 0.1,
            "delta_topk_hit_rate": 0.2,
        }

    monkeypatch.setattr(boot, "evaluate_resampled_policy", fake_evaluate)
    delta_mean, delta_hit, infeasible = boot.cluster_bootstrap(
        frame,
        rng=np.random.default_rng(1),
        replicates=3,
    )

    assert infeasible == 1
    assert np.isnan(delta_mean[1])
    assert np.isnan(delta_hit[1])


def test_runner_source_recomputes_policy_and_contains_no_retuning():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_primary_bootstrap.py"
    ).read_text()

    assert "optimize_mm1(state)" in source
    assert "rng.integers(0, n_clusters, size=n_clusters)" in source
    assert '"rho_retuned": False' in source
    assert '"threshold_retuned": False' in source
