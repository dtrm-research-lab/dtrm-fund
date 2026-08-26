import numpy as np
import pytest

from dtrm.phase3_mm0_state import (
    P10_CALIBRATION_OFFSET,
    P10_GUARDRAIL_THRESHOLD,
    materialize_mm0_information_state,
)


def test_materialize_mm0_information_state_applies_frozen_phase2_rules():
    baseline = np.array([0.20, 0.50, 0.10], dtype=np.float32)
    raw_p10 = np.array([
        0.00,
        P10_GUARDRAIL_THRESHOLD - P10_CALIBRATION_OFFSET,
        -0.30,
    ])

    state = materialize_mm0_information_state(
        news_id=["n1", "n2", "n3"],
        ticker=["AAA", "BBB", "CCC"],
        date_dt=["2026-01-01", "2026-01-02", "2026-01-03"],
        baseline_point_score=baseline,
        raw_p10=raw_p10,
    )

    assert state.rows == 3
    np.testing.assert_allclose(
        state.calibrated_p10,
        raw_p10 + P10_CALIBRATION_OFFSET,
        rtol=0.0,
        atol=1e-15,
    )
    np.testing.assert_array_equal(
        state.phase2_guardrail_pass,
        np.array([True, True, False]),
    )

    # np.argsort(-baseline) -> [1, 0, 2], therefore ranks attached to
    # the original rows are [1, 0, 2].
    np.testing.assert_array_equal(
        state.baseline_rank,
        np.array([1, 0, 2]),
    )


def test_mm0_rank_reproduces_numpy_argsort_negative_score():
    baseline = np.array([0.4, -0.1, 0.7, 0.2, 0.6])

    state = materialize_mm0_information_state(
        news_id=np.arange(5),
        ticker=["A", "B", "C", "D", "E"],
        date_dt=np.arange(5),
        baseline_point_score=baseline,
        raw_p10=np.zeros(5),
    )

    recovered_order = np.argsort(state.baseline_rank)
    expected_order = np.argsort(-baseline)

    np.testing.assert_array_equal(recovered_order, expected_order)


def test_mm0_state_arrays_are_read_only():
    state = materialize_mm0_information_state(
        news_id=[1],
        ticker=["AAA"],
        date_dt=["2026-01-01"],
        baseline_point_score=[0.1],
        raw_p10=[0.0],
    )

    with pytest.raises(ValueError):
        state.baseline_point_score[0] = 99.0

    with pytest.raises(ValueError):
        state.phase2_guardrail_pass[0] = False


def test_mm0_state_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        materialize_mm0_information_state(
            news_id=[1, 2],
            ticker=["AAA"],
            date_dt=["2026-01-01", "2026-01-02"],
            baseline_point_score=[0.1, 0.2],
            raw_p10=[0.0, 0.1],
        )


def test_mm0_state_rejects_empty_input():
    with pytest.raises(ValueError, match="must not be empty"):
        materialize_mm0_information_state(
            news_id=[],
            ticker=[],
            date_dt=[],
            baseline_point_score=[],
            raw_p10=[],
        )


@pytest.mark.parametrize(
    ("field", "bad_values", "match"),
    [
        ("baseline", [0.1, np.nan], "baseline_point_score"),
        ("p10", [0.1, np.inf], "raw_p10"),
    ],
)
def test_mm0_state_rejects_non_finite_scores(field, bad_values, match):
    baseline = [0.1, 0.2]
    p10 = [0.0, 0.1]

    if field == "baseline":
        baseline = bad_values
    else:
        p10 = bad_values

    with pytest.raises(ValueError, match=match):
        materialize_mm0_information_state(
            news_id=[1, 2],
            ticker=["AAA", "BBB"],
            date_dt=["2026-01-01", "2026-01-02"],
            baseline_point_score=baseline,
            raw_p10=p10,
        )


def test_mm0_state_rejects_non_vector_input():
    with pytest.raises(ValueError, match="one-dimensional"):
        materialize_mm0_information_state(
            news_id=[[1, 2]],
            ticker=["AAA", "BBB"],
            date_dt=["2026-01-01", "2026-01-02"],
            baseline_point_score=[0.1, 0.2],
            raw_p10=[0.0, 0.1],
        )
