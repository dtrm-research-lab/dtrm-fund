import itertools

import numpy as np
import pytest

from dtrm.phase3_mm0_state import (
    P10_CALIBRATION_OFFSET,
    P10_GUARDRAIL_THRESHOLD,
    materialize_mm0_information_state,
)
from dtrm.phase3_mm1_robust_value import (
    RHO_MM0,
    robust_value_for_selection,
)


def _make_state(
    *,
    rows=30,
    baseline=None,
    calibrated_p10=None,
):
    if baseline is None:
        baseline = np.linspace(0.50, 0.01, rows)
    else:
        baseline = np.asarray(baseline, dtype=np.float64)

    if calibrated_p10 is None:
        calibrated_p10 = np.full(rows, 0.0, dtype=np.float64)
    else:
        calibrated_p10 = np.asarray(calibrated_p10, dtype=np.float64)

    raw_p10 = calibrated_p10 - P10_CALIBRATION_OFFSET

    return materialize_mm0_information_state(
        news_id=[f"n{i}" for i in range(rows)],
        ticker=[f"T{i}" for i in range(rows)],
        date_dt=[f"2026-01-{(i % 28) + 1:02d}" for i in range(rows)],
        baseline_point_score=baseline,
        raw_p10=raw_p10,
    )


def test_mm1_robust_value_matches_closed_form_fractional_knapsack():
    baseline = np.linspace(0.20, 0.01, 30)
    baseline[:3] = [0.50, 0.40, 0.30]

    calibrated = np.zeros(30)
    calibrated[:3] = [0.10, 0.35, 0.25]

    state = _make_state(baseline=baseline, calibrated_p10=calibrated)
    result = robust_value_for_selection(state, [0, 1, 2])

    budget = RHO_MM0 * 3
    fractional = budget - 1.0
    expected_penalty_total = 0.40 + fractional * 0.05
    expected_nominal = 0.40
    expected_robust = expected_nominal - expected_penalty_total / 3.0

    assert result.stress_budget == pytest.approx(budget)
    assert result.fully_stressed_rows == 1
    assert result.fractional_stress == pytest.approx(fractional)
    assert result.nominal_mean == pytest.approx(expected_nominal)
    assert result.adversarial_penalty_mean == pytest.approx(expected_penalty_total / 3.0)
    assert result.robust_value == pytest.approx(expected_robust)


def test_mm1_robust_value_equals_exhaustive_extreme_point_search():
    baseline = np.linspace(0.20, 0.01, 30)
    baseline[:3] = [0.55, 0.42, 0.31]

    calibrated = np.zeros(30)
    calibrated[:3] = [0.05, 0.22, 0.26]

    state = _make_state(baseline=baseline, calibrated_p10=calibrated)
    selected = np.array([0, 1, 2])
    result = robust_value_for_selection(state, selected)

    b = state.baseline_point_score[selected]
    d = b - np.minimum(b, state.calibrated_p10[selected])
    budget = RHO_MM0 * selected.size
    fractional = budget - np.floor(budget)

    candidate_levels = [0.0, float(fractional), 1.0]
    direct_values = []
    for z_tuple in itertools.product(candidate_levels, repeat=selected.size):
        z = np.asarray(z_tuple, dtype=np.float64)
        if z.sum() <= budget + 1e-12:
            direct_values.append(float(np.mean(b - z * d)))

    assert direct_values
    assert result.robust_value == pytest.approx(min(direct_values), abs=1e-12)


def test_mm1_downside_width_is_zero_when_calibrated_p10_exceeds_baseline():
    baseline = np.linspace(0.20, 0.01, 30)
    baseline[:3] = [0.20, 0.19, 0.18]

    calibrated = np.zeros(30)
    calibrated[:3] = [0.30, 0.29, 0.28]

    state = _make_state(baseline=baseline, calibrated_p10=calibrated)
    result = robust_value_for_selection(state, [0, 1, 2])

    assert result.adversarial_penalty_mean == pytest.approx(0.0)
    assert result.robust_value == pytest.approx(np.mean(baseline[:3]))


def test_mm1_robust_value_is_invariant_to_selected_index_order():
    state = _make_state()

    a = robust_value_for_selection(state, [0, 1, 2])
    b = robust_value_for_selection(state, [2, 0, 1])

    assert a.robust_value == pytest.approx(b.robust_value)
    assert a.nominal_mean == pytest.approx(b.nominal_mean)
    assert a.adversarial_penalty_mean == pytest.approx(b.adversarial_penalty_mean)


def test_mm1_robust_value_rejects_wrong_topk_cardinality():
    state = _make_state()

    with pytest.raises(ValueError, match="exactly the frozen Top-K size"):
        robust_value_for_selection(state, [0, 1])


def test_mm1_robust_value_rejects_phase2_ineligible_candidate():
    calibrated = np.zeros(30)
    calibrated[2] = P10_GUARDRAIL_THRESHOLD - 0.01
    state = _make_state(calibrated_p10=calibrated)

    with pytest.raises(ValueError, match="Phase-2-eligible"):
        robust_value_for_selection(state, [0, 1, 2])


def test_mm1_robust_value_rejects_duplicate_indices():
    state = _make_state()

    with pytest.raises(ValueError, match="duplicates"):
        robust_value_for_selection(state, [0, 0, 1])


def test_mm1_robust_value_rejects_out_of_range_indices():
    state = _make_state()

    with pytest.raises(ValueError, match="out-of-range"):
        robust_value_for_selection(state, [0, 1, 30])


def test_mm1_robust_value_rejects_noninteger_indices():
    state = _make_state()

    with pytest.raises(ValueError, match="integers"):
        robust_value_for_selection(state, [0.0, 1.0, 2.0])
