import numpy as np
import pytest

from dtrm.topk_selection import (
    select_topk_iteration,
    topk_metrics,
)


def test_topk_metrics_selects_highest_predictions():
    y_true = np.array(
        [-1.0, 2.0, 3.0, -2.0],
        dtype=np.float32,
    )

    y_pred = np.array(
        [0.1, 0.9, 0.8, 0.2],
        dtype=np.float32,
    )

    mean, hit = topk_metrics(
        y_true,
        y_pred,
        fraction=0.50,
    )

    assert mean == pytest.approx(2.5)
    assert hit == pytest.approx(1.0)


def test_select_topk_iteration_uses_max_mean():
    result = select_topk_iteration(
        [
            (0, 0.01, 0.60),
            (10, 0.05, 0.65),
            (20, 0.03, 0.90),
        ]
    )

    assert result.iteration == 10
    assert result.topk_mean == pytest.approx(0.05)
    assert result.topk_hit_rate == pytest.approx(0.65)


def test_select_topk_iteration_uses_hit_rate_as_tiebreaker():
    result = select_topk_iteration(
        [
            (40, 0.10, 0.70),
            (50, 0.10, 0.73),
        ]
    )

    assert result.iteration == 50
    assert result.topk_hit_rate == pytest.approx(0.73)


def test_topk_metrics_rejects_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        topk_metrics(
            [1.0, 2.0],
            [0.5],
        )


def test_select_topk_iteration_rejects_empty_input():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        select_topk_iteration([])
        