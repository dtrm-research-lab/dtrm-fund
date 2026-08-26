import numpy as np
import pytest

from dtrm.phase3_mm0_action import (
    TOPK_FRACTION,
    finalize_mm0_action,
    phase2_champion_keep_mask,
)
from dtrm.phase3_mm0_state import materialize_mm0_information_state


def _state(rows: int = 20):
    baseline = np.linspace(1.0, 0.0, rows)
    # First 15 pass Phase 2, last 5 fail.
    raw_p10 = np.concatenate([
        np.full(15, 0.0),
        np.full(rows - 15, -1.0),
    ])

    return materialize_mm0_information_state(
        news_id=[f"n{i}" for i in range(rows)],
        ticker=[f"T{i}" for i in range(rows)],
        date_dt=[f"2026-01-{(i % 28) + 1:02d}" for i in range(rows)],
        baseline_point_score=baseline,
        raw_p10=raw_p10,
    )


def test_neutral_mask_reproduces_phase2_champion_selection():
    state = _state()
    keep = phase2_champion_keep_mask(state)

    result = finalize_mm0_action(state, keep)

    expected_k = int(state.rows * TOPK_FRACTION)
    expected_order = np.argsort(state.baseline_rank)
    expected = expected_order[state.phase2_guardrail_pass[expected_order]][:expected_k]

    assert result.k == expected_k
    assert result.rows == expected_k
    np.testing.assert_array_equal(result.selected_indices, expected)


def test_additional_veto_walks_down_same_frozen_ranking():
    state = _state()
    keep = phase2_champion_keep_mask(state).copy()
    keep.setflags(write=True)

    # Neutral champion would select original rows [0, 1]. Veto row 0, so the
    # same frozen order must walk down and select [1, 2].
    keep[0] = False

    result = finalize_mm0_action(state, keep)
    np.testing.assert_array_equal(result.selected_indices, np.array([1, 2]))


def test_action_cannot_rescue_phase2_vetoed_candidate():
    state = _state()
    keep = phase2_champion_keep_mask(state).copy()
    keep.setflags(write=True)
    keep[-1] = True

    with pytest.raises(ValueError, match="cannot rescue"):
        finalize_mm0_action(state, keep)


def test_action_must_leave_enough_candidates_for_full_topk():
    state = _state()
    keep = np.zeros(state.rows, dtype=bool)
    keep[0] = True

    with pytest.raises(ValueError, match="fill Top-K"):
        finalize_mm0_action(state, keep)


def test_action_rejects_length_mismatch():
    state = _state()

    with pytest.raises(ValueError, match="match MM0 state length"):
        finalize_mm0_action(state, np.ones(state.rows - 1, dtype=bool))


def test_action_rejects_non_boolean_mask():
    state = _state()

    with pytest.raises(ValueError, match="booleans"):
        finalize_mm0_action(state, np.ones(state.rows, dtype=np.int64))


def test_action_rejects_non_vector_mask():
    state = _state()

    with pytest.raises(ValueError, match="one-dimensional"):
        finalize_mm0_action(state, np.ones((2, 10), dtype=bool))


def test_selected_indices_are_read_only():
    state = _state()
    result = finalize_mm0_action(state, phase2_champion_keep_mask(state))

    with pytest.raises(ValueError):
        result.selected_indices[0] = 99


def test_action_rejects_cohort_with_empty_topk():
    state = materialize_mm0_information_state(
        news_id=["n1"],
        ticker=["AAA"],
        date_dt=["2026-01-01"],
        baseline_point_score=[0.1],
        raw_p10=[0.0],
    )

    with pytest.raises(ValueError, match="Top-K is empty"):
        finalize_mm0_action(state, np.array([True], dtype=bool))
