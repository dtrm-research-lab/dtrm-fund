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


def test_resampled_row_multiplicity_duplicates_all_rows_of_repeated_cluster():
    class FakeRNG:
        def integers(self, low, high, size):
            assert low == 0
            assert high == 3
            assert size == 3
            return np.array([0, 0, 2], dtype=np.int64)

    cluster_codes = np.array([0, 0, 1, 2, 2], dtype=np.int64)
    result = boot.resampled_row_multiplicity(
        cluster_codes,
        n_clusters=3,
        rng=FakeRNG(),
    )

    assert result.tolist() == [2, 2, 0, 1, 1]


def test_resampled_row_indices_remains_exact_expanded_reference():
    class FakeRNG:
        def integers(self, low, high, size):
            return np.array([0, 0, 2], dtype=np.int64)

    cluster_codes = np.array([0, 0, 1, 2, 2], dtype=np.int64)
    result = boot.resampled_row_indices(
        cluster_codes,
        n_clusters=3,
        rng=FakeRNG(),
    )

    assert result.tolist() == [0, 0, 1, 1, 3, 4]


def test_exchangeable_policy_recomputes_k_from_integer_multiplicity():
    frame = _frame(20)
    multiplicity = np.ones(20, dtype=np.int64)
    multiplicity[:2] = 2
    multiplicity[2:4] = 0

    result = boot.evaluate_resampled_policy_exchangeable(frame, multiplicity)

    assert result is not None
    assert result["rows"] == 20
    assert result["K_H"] == 2


def test_exchangeable_policy_returns_none_when_phase2_pool_cannot_fill():
    frame = _frame(20)
    frame["raw_p10"] = -1.0
    multiplicity = np.ones(20, dtype=np.int64)

    assert boot.evaluate_resampled_policy_exchangeable(frame, multiplicity) is None


def test_exchangeable_solver_matches_expanded_frozen_optimizer_on_small_duplicate_sample():
    frame = _frame(20)
    multiplicity = np.array(
        [2, 2, 0, 0] + [1] * 16,
        dtype=np.int64,
    )
    expanded_idx = np.repeat(np.arange(len(frame), dtype=np.int64), multiplicity)

    compact = boot.evaluate_resampled_policy_exchangeable(frame, multiplicity)
    expanded = boot.evaluate_resampled_policy_expanded_reference(frame, expanded_idx)

    assert compact is not None
    assert expanded is not None
    for key in (
        "rows",
        "K_H",
        "phase2_value",
        "MM1_value",
        "delta_topk_mean_target_model_vs_phase2",
        "phase2_hit_rate",
        "MM1_hit_rate",
        "delta_topk_hit_rate",
    ):
        assert compact[key] == pytest.approx(expanded[key], abs=1.0e-12)


def test_copy_label_swap_is_not_a_distinct_quantity_action():
    adjusted = np.array([0.8, 0.8, 0.5], dtype=np.float64)
    original_ids = np.array([0, 0, 1], dtype=np.int64)
    selected = np.array([0], dtype=np.int64)

    # The unselected second copy of row 0 is not a distinct quantity action;
    # the best distinct action must move the unit to original row 1.
    result = boot._best_one_unit_distinct_total(
        unrestricted_total=0.8,
        adjusted=adjusted,
        eligible_original_ids=original_ids,
        selected_local=selected,
        original_rows=2,
    )
    assert result == pytest.approx(0.5)


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

    def fake_evaluate(_frame, multiplicity):
        value = float(np.mean(multiplicity))
        return {
            "delta_topk_mean_target_model_vs_phase2": value,
            "delta_topk_hit_rate": value / 100.0,
        }

    monkeypatch.setattr(boot, "evaluate_resampled_policy_exchangeable", fake_evaluate)

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

    def fake_evaluate(_frame, _multiplicity):
        calls["n"] += 1
        if calls["n"] == 2:
            return None
        return {
            "delta_topk_mean_target_model_vs_phase2": 0.1,
            "delta_topk_hit_rate": 0.2,
        }

    monkeypatch.setattr(boot, "evaluate_resampled_policy_exchangeable", fake_evaluate)
    delta_mean, delta_hit, infeasible = boot.cluster_bootstrap(
        frame,
        rng=np.random.default_rng(1),
        replicates=3,
    )

    assert infeasible == 1
    assert np.isnan(delta_mean[1])
    assert np.isnan(delta_hit[1])


def test_runner_source_uses_exchangeable_exact_amendment_and_contains_no_retuning():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_primary_bootstrap.py"
    ).read_text()

    assert "evaluate_resampled_policy_exchangeable(frame, multiplicity)" in source
    assert "_threshold_primary_optimum(" in source
    assert "DTRM_PHASE3_MM1_V5_BOOTSTRAP_SOLVER_AMENDMENT.yaml" in source
    assert "rng.integers(0, n_clusters, size=n_clusters)" in source
    assert '"rho_retuned": False' in source
    assert '"threshold_retuned": False' in source
