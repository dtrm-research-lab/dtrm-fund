from itertools import combinations

import numpy as np
import pytest

import dtrm.phase3_mm1_optimizer as optimizer
from dtrm.phase3_mm0_state import (
    P10_CALIBRATION_OFFSET,
    materialize_mm0_information_state,
)
from dtrm.phase3_mm1_optimizer import ROBUST_VALUE_TOLERANCE, optimize_mm1
from dtrm.phase3_mm1_robust_value import robust_value_for_selection


def _build_state(baseline, calibrated_p10):
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


def _champion(state, k):
    order = np.argsort(state.baseline_rank)
    eligible_order = order[state.phase2_guardrail_pass[order]]
    return eligible_order[:k]


def _exhaustive_mm1(state):
    k = int(state.rows * 0.10)
    eligible = np.flatnonzero(state.phase2_guardrail_pass)
    champion = _champion(state, k)
    champion_set = set(int(i) for i in champion)
    champion_value = robust_value_for_selection(state, champion)

    records = []
    for combo in combinations(eligible.tolist(), k):
        indices = np.asarray(combo, dtype=np.int64)
        value = robust_value_for_selection(state, indices)
        records.append(
            {
                "indices": indices,
                "robust": value.robust_value,
                "nominal": value.nominal_mean,
                "overlap": sum(int(i) in champion_set for i in indices),
                "rank_tuple": tuple(
                    sorted(int(state.baseline_rank[i]) for i in indices)
                ),
            }
        )

    robust_star = max(record["robust"] for record in records)
    if robust_star <= champion_value.robust_value + ROBUST_VALUE_TOLERANCE:
        return champion, champion_value.robust_value, False

    candidates = [
        record
        for record in records
        if record["robust"] >= robust_star - ROBUST_VALUE_TOLERANCE
    ]
    overlap_star = max(record["overlap"] for record in candidates)
    candidates = [
        record for record in candidates if record["overlap"] == overlap_star
    ]

    nominal_star = max(record["nominal"] for record in candidates)
    candidates = [
        record
        for record in candidates
        if record["nominal"] >= nominal_star - ROBUST_VALUE_TOLERANCE
    ]

    winner = min(candidates, key=lambda record: record["rank_tuple"])
    return winner["indices"], robust_star, True


def _nontrivial_state():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[:6] = np.array([0.00, 0.00, 0.87, 0.83, 0.79, 0.75])
    return _build_state(baseline, calibrated)


def _eligible_arrays(state):
    eligible = np.flatnonzero(state.phase2_guardrail_pass).astype(np.int64)
    baseline = np.asarray(state.baseline_point_score[eligible], dtype=np.float64)
    calibrated = np.asarray(state.calibrated_p10[eligible], dtype=np.float64)
    widths = baseline - np.minimum(baseline, calibrated)
    ranks = np.asarray(state.baseline_rank[eligible])
    return eligible, baseline, widths, ranks


def test_mm1_optimizer_matches_exhaustive_nontrivial_problem():
    state = _nontrivial_state()
    expected, expected_robust, expected_intervention = _exhaustive_mm1(state)

    result = optimize_mm1(state)

    assert set(result.selected_indices.tolist()) == set(expected.tolist())
    assert result.robust_value_selected == pytest.approx(expected_robust, abs=1e-12)
    assert result.intervention is expected_intervention
    assert result.robust_value_selected >= result.robust_value_champion


@pytest.mark.parametrize("seed", [20260826, 20260827, 20260828])
def test_mm1_optimizer_matches_exhaustive_random_small_problems(seed):
    rng = np.random.default_rng(seed)
    rows = 30
    baseline = np.linspace(1.10, 0.10, rows)
    calibrated = np.full(rows, -1.0)

    eligible_count = 7
    widths = rng.uniform(0.01, 0.35, size=eligible_count)
    calibrated[:eligible_count] = baseline[:eligible_count] - widths

    state = _build_state(baseline, calibrated)
    expected, expected_robust, expected_intervention = _exhaustive_mm1(state)

    result = optimize_mm1(state)

    assert set(result.selected_indices.tolist()) == set(expected.tolist())
    assert result.robust_value_selected == pytest.approx(expected_robust, abs=1e-11)
    assert result.intervention is expected_intervention


@pytest.mark.parametrize("seed", [20260829, 20260830, 20260831])
def test_exact_threshold_primary_matches_original_milp_on_small_problems(seed):
    rng = np.random.default_rng(seed)
    rows = 40
    baseline = np.linspace(1.20, 0.05, rows)
    calibrated = np.full(rows, -1.0)
    eligible_count = 11
    widths = rng.uniform(0.001, 0.50, size=eligible_count)
    calibrated[:eligible_count] = baseline[:eligible_count] - widths
    state = _build_state(baseline, calibrated)

    eligible, b, d, ranks = _eligible_arrays(state)
    k = int(state.rows * 0.10)

    threshold_local, threshold_total, _, _ = optimizer._threshold_primary_optimum(
        b,
        d,
        k=k,
        baseline_ranks=ranks,
    )
    milp_local, milp_gap = optimizer._milp_primary_reference(b, d, k=k)

    threshold_value = robust_value_for_selection(
        state,
        eligible[threshold_local],
    ).robust_value
    milp_value = robust_value_for_selection(
        state,
        eligible[milp_local],
    ).robust_value

    assert threshold_total / k == pytest.approx(threshold_value, abs=1e-11)
    assert threshold_value == pytest.approx(milp_value, abs=1e-11)
    assert milp_gap == pytest.approx(0.0, abs=1e-12)


def test_mm1_optimizer_falls_back_to_phase2_when_widths_are_zero():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[:6] = baseline[:6]
    state = _build_state(baseline, calibrated)

    result = optimize_mm1(state)

    expected_champion = _champion(state, result.k)
    np.testing.assert_array_equal(result.selected_indices, expected_champion)
    assert result.intervention is False
    assert result.robust_lift == pytest.approx(0.0, abs=1e-12)
    assert result.solver_status == "optimal_exact_threshold_champion_fallback"


def test_mm1_optimizer_never_selects_phase2_vetoed_high_nominal_row():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    baseline[0] = 5.0
    calibrated = np.full(rows, -1.0)
    calibrated[0] = -2.0
    calibrated[1:7] = baseline[1:7] - np.array(
        [0.5, 0.4, 0.05, 0.05, 0.05, 0.05]
    )
    state = _build_state(baseline, calibrated)

    assert state.phase2_guardrail_pass[0] is np.False_ or not bool(
        state.phase2_guardrail_pass[0]
    )

    result = optimize_mm1(state)

    assert 0 not in result.selected_indices
    assert np.all(state.phase2_guardrail_pass[result.selected_indices])


def test_mm1_optimizer_applies_lexicographic_rank_tie_break():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)

    baseline[2:5] = 0.80
    calibrated[0:2] = 0.00
    calibrated[2:5] = 0.79
    calibrated[5] = 0.50
    state = _build_state(baseline, calibrated)

    expected, expected_robust, expected_intervention = _exhaustive_mm1(state)
    result = optimize_mm1(state)

    assert expected_intervention is True
    assert result.intervention is True
    assert set(result.selected_indices.tolist()) == set(expected.tolist())
    assert result.robust_value_selected == pytest.approx(expected_robust, abs=1e-12)
    assert result.solver_status == "optimal_exact_threshold_plus_milp_tie_hierarchy"


def test_unique_primary_band_does_not_call_milp(monkeypatch):
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[0:2] = 0.0
    calibrated[2] = baseline[2] - 0.01
    calibrated[3] = baseline[3] - 0.02
    calibrated[4] = baseline[4] - 0.10
    state = _build_state(baseline, calibrated)

    def forbidden_solve(**kwargs):
        raise AssertionError("MILP must not run for a unique primary robust band")

    monkeypatch.setattr(optimizer, "_solve", forbidden_solve)
    result = optimizer.optimize_mm1(state)

    assert result.intervention is True
    assert result.solver_status == "optimal_exact_threshold_unique_primary_band"
    assert result.solver_mip_gap == 0.0


def test_exact_threshold_solver_scales_without_milp_on_large_unique_state(monkeypatch):
    rng = np.random.default_rng(20260826)
    rows = 1000
    baseline = np.linspace(1.20, 0.20, rows)
    widths = rng.uniform(0.001, 0.20, size=rows)
    calibrated = baseline - widths
    state = _build_state(baseline, calibrated)

    def forbidden_solve(**kwargs):
        raise AssertionError("large unique state must not invoke HiGHS")

    monkeypatch.setattr(optimizer, "_solve", forbidden_solve)
    result = optimizer.optimize_mm1(state)

    assert result.k == 100
    assert result.eligible_rows == 1000
    assert result.solver_status.startswith("optimal_exact_threshold")
    assert result.solver_mip_gap == 0.0
    assert len(result.selected_indices) == 100


def test_mm1_optimizer_is_deterministic():
    state = _nontrivial_state()

    first = optimize_mm1(state)
    second = optimize_mm1(state)

    np.testing.assert_array_equal(first.selected_indices, second.selected_indices)
    assert first.robust_value_selected == second.robust_value_selected
    assert first.intervention == second.intervention
    assert first.solver_status == second.solver_status


def test_mm1_optimizer_rejects_infeasible_eligible_pool():
    rows = 20
    baseline = np.linspace(1.00, 0.20, rows)
    calibrated = np.full(rows, -1.0)
    calibrated[0] = 0.0
    state = _build_state(baseline, calibrated)

    with pytest.raises(ValueError, match="cannot fill"):
        optimize_mm1(state)


def test_mm1_optimizer_result_indices_are_read_only():
    state = _nontrivial_state()
    result = optimize_mm1(state)

    with pytest.raises(ValueError):
        result.selected_indices[0] = 99

    with pytest.raises(ValueError):
        result.champion_indices[0] = 99
