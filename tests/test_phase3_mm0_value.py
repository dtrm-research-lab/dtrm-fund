import numpy as np
import pytest

from dtrm.phase3_mm0_value import (
    incremental_value,
    selected_mean_value,
)


def test_selected_mean_value_matches_numpy_mean():
    values = np.array([0.1, -0.2, 0.4, 0.8], dtype=np.float32)
    selected = np.array([3, 0], dtype=np.int64)

    result = selected_mean_value(selected, values)

    assert result == pytest.approx(float(np.mean(values[selected])))


def test_incremental_value_uses_same_world_vector():
    values = np.array([0.5, 0.1, -0.2, 0.9], dtype=np.float64)
    challenger = [0, 3]
    champion = [0, 1]

    result = incremental_value(challenger, champion, values)

    expected = float(np.mean(values[challenger]) - np.mean(values[champion]))
    assert result == pytest.approx(expected)


def test_incremental_value_neutral_action_is_zero():
    values = np.array([0.2, -0.1, 0.3], dtype=np.float64)
    selected = [2, 0]

    assert incremental_value(selected, selected, values) == pytest.approx(0.0)


def test_incremental_value_requires_same_topk_cardinality():
    with pytest.raises(ValueError, match="same Top-K cardinality"):
        incremental_value([0, 1], [0], [0.2, 0.1])


def test_selected_mean_value_rejects_empty_selection():
    with pytest.raises(ValueError, match="must not be empty"):
        selected_mean_value([], [0.1, 0.2])


def test_selected_mean_value_rejects_duplicate_indices():
    with pytest.raises(ValueError, match="duplicates"):
        selected_mean_value([0, 0], [0.1, 0.2])


def test_selected_mean_value_rejects_out_of_range_indices():
    with pytest.raises(ValueError, match="out-of-range"):
        selected_mean_value([2], [0.1, 0.2])


def test_selected_mean_value_rejects_non_integer_indices():
    with pytest.raises(ValueError, match="integers"):
        selected_mean_value([0.0], [0.1])


def test_selected_mean_value_rejects_non_finite_values():
    with pytest.raises(ValueError, match="finite"):
        selected_mean_value([0], [np.nan])


def test_selected_mean_value_rejects_non_vector_values():
    with pytest.raises(ValueError, match="one-dimensional"):
        selected_mean_value([0], [[0.1]])


def test_incremental_value_is_directional_challenger_minus_champion():
    values = np.array([1.0, 0.0, -1.0], dtype=np.float64)

    forward = incremental_value([0], [2], values)
    reverse = incremental_value([2], [0], values)

    assert forward == pytest.approx(2.0)
    assert reverse == pytest.approx(-2.0)
