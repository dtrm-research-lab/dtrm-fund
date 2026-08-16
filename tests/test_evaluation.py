import numpy as np
import pytest

from dtrm.evaluation import regression_topk_metrics


def test_regression_topk_metrics_basic():
    y_true = np.array(
        [1.0, -1.0, 2.0, 0.0],
        dtype=np.float32,
    )

    y_pred = np.array(
        [0.8, 0.1, 0.9, 0.2],
        dtype=np.float32,
    )

    result = regression_topk_metrics(
        y_true,
        y_pred,
        topk_fraction=0.50,
    )

    assert result.rows == 4
    assert result.topk_rows == 2
    assert result.topk_mean == pytest.approx(1.5)
    assert result.topk_hit_rate == pytest.approx(1.0)
    assert result.hit_rate == pytest.approx(0.5)


def test_regression_topk_metrics_rejects_shape_mismatch():
    with pytest.raises(
        ValueError,
        match="same shape",
    ):
        regression_topk_metrics(
            [1.0, 2.0],
            [0.1],
        )


def test_regression_topk_metrics_rejects_empty_input():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        regression_topk_metrics(
            [],
            [],
        )


def test_regression_topk_metrics_rejects_invalid_fraction():
    with pytest.raises(
        ValueError,
        match="topk_fraction",
    ):
        regression_topk_metrics(
            [1.0],
            [0.5],
            topk_fraction=0.0,
        )