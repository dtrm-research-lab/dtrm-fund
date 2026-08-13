import pytest

from dtrm.target_clipping import (
    clip_targets,
    train_only_clip_bounds,
)


def test_train_only_clip_bounds():
    targets = [0.0, 1.0, 2.0, 3.0, 4.0]

    lower, upper = train_only_clip_bounds(
        targets,
        lower_quantile=0.25,
        upper_quantile=0.75,
    )

    assert lower == pytest.approx(1.0)
    assert upper == pytest.approx(3.0)


def test_clip_targets_uses_precomputed_bounds():
    clipped = clip_targets(
        [-2.0, 0.5, 5.0],
        lower=0.0,
        upper=2.0,
    )

    assert clipped.tolist() == pytest.approx(
        [0.0, 0.5, 2.0]
    )


def test_empty_train_targets_are_rejected():
    with pytest.raises(ValueError):
        train_only_clip_bounds([])


def test_invalid_quantiles_are_rejected():
    with pytest.raises(ValueError):
        train_only_clip_bounds(
            [1.0, 2.0],
            lower_quantile=0.9,
            upper_quantile=0.1,
        )


def test_invalid_clip_bounds_are_rejected():
    with pytest.raises(ValueError):
        clip_targets(
            [1.0, 2.0],
            lower=3.0,
            upper=1.0,
        )