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

import dtrm.phase3_mm1_optimizer as frozen_optimizer
from dtrm.phase3_mm0_state import (
    P10_CALIBRATION_OFFSET,
    materialize_mm0_information_state,
)
import run_phase3_mm1_v6_decision_freeze_exact_ties as v6x


def _state(baseline, calibrated_p10):
    baseline = np.asarray(baseline, dtype=np.float64)
    calibrated_p10 = np.asarray(calibrated_p10, dtype=np.float64)
    rows = baseline.size
    return materialize_mm0_information_state(
        news_id=np.arange(rows),
        ticker=[f"T{i:04d}" for i in range(rows)],
        date_dt=np.arange(rows),
        baseline_point_score=baseline,
        raw_p10=calibrated_p10 - P10_CALIBRATION_OFFSET,
    )


def _frame(state):
    return pd.DataFrame({"row_id": np.arange(state.rows, dtype=np.int64)})


def _tie_state():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    baseline[2:5] = 0.80
    calibrated[0:2] = 0.00
    calibrated[2:5] = 0.79
    calibrated[5] = 0.50
    return _state(baseline, calibrated)


def _unique_state():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[0:2] = 0.0
    calibrated[2] = baseline[2] - 0.01
    calibrated[3] = baseline[3] - 0.02
    calibrated[4] = baseline[4] - 0.10
    return _state(baseline, calibrated)


def _fallback_state():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[:6] = baseline[:6]
    return _state(baseline, calibrated)


def test_reduced_tie_wrapper_matches_frozen_global_milp_tie_hierarchy():
    state = _tie_state()
    expected = frozen_optimizer.optimize_mm1(state)
    assert expected.solver_status == "optimal_exact_threshold_plus_milp_tie_hierarchy"

    actual, diagnostics = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))

    np.testing.assert_array_equal(actual.selected_indices, expected.selected_indices)
    np.testing.assert_array_equal(actual.champion_indices, expected.champion_indices)
    assert actual.robust_value_selected == pytest.approx(expected.robust_value_selected, abs=1e-12)
    assert actual.nominal_mean_selected == pytest.approx(expected.nominal_mean_selected, abs=1e-12)
    assert actual.overlap_with_champion == expected.overlap_with_champion
    assert actual.intervention is True
    assert actual.solver_status == "optimal_exact_threshold_plus_reduced_residual_tie_hierarchy"
    assert diagnostics["residual_route"] == "exact_reduced_residual_tie_hierarchy"


def test_unique_primary_band_is_identical_to_frozen_optimizer():
    state = _unique_state()
    expected = frozen_optimizer.optimize_mm1(state)
    actual, diagnostics = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))

    np.testing.assert_array_equal(actual.selected_indices, expected.selected_indices)
    assert actual.robust_value_selected == pytest.approx(expected.robust_value_selected, abs=1e-12)
    assert actual.robust_lift == pytest.approx(expected.robust_lift, abs=1e-12)
    assert actual.solver_status == expected.solver_status
    assert diagnostics["residual_route"] == "unique_primary_band"


def test_champion_fallback_is_identical_to_frozen_optimizer():
    state = _fallback_state()
    expected = frozen_optimizer.optimize_mm1(state)
    actual, diagnostics = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))

    np.testing.assert_array_equal(actual.selected_indices, expected.selected_indices)
    assert actual.intervention is False
    assert actual.robust_lift == pytest.approx(0.0, abs=1e-12)
    assert actual.solver_status == "optimal_exact_threshold_champion_fallback"
    assert diagnostics["residual_route"] == "champion_fallback"


def test_reduced_tie_wrapper_is_deterministic():
    state = _tie_state()
    first, first_diag = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))
    second, second_diag = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))

    np.testing.assert_array_equal(first.selected_indices, second.selected_indices)
    assert first.robust_value_selected == second.robust_value_selected
    assert first.nominal_mean_selected == second.nominal_mean_selected
    assert first_diag == second_diag


def test_reduced_tie_wrapper_preserves_exact_k_and_guardrail():
    state = _tie_state()
    result, _ = v6x.optimize_v6_exact_reduced_ties(state, _frame(state))

    assert len(result.selected_indices) == int(state.rows * 0.10)
    assert len(np.unique(result.selected_indices)) == len(result.selected_indices)
    assert np.all(state.phase2_guardrail_pass[result.selected_indices])


def test_amendment_is_present_and_source_remains_outcome_blind():
    assert v6x.AMENDMENT_PATH.exists()
    source = (EXPERIMENTS / "run_phase3_mm1_v6_decision_freeze_exact_ties.py").read_text()
    forbidden = (
        "phase3_mm1_v6_target_model",
        "phase3_mm1_v6_price_snapshot",
        "realized_forward_return",
        "delta_topk_mean_target_model_vs_phase2",
    )
    for token in forbidden:
        assert token not in source


def test_wrapper_does_not_modify_frozen_policy_blob_expectations():
    observed = v6x.base.require_frozen_v5_policy_code()
    assert observed == v6x.base.FROZEN_V5_POLICY_BLOBS
