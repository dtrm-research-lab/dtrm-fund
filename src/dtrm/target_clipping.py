"""Target clipping utilities for DTRM experiments."""

from typing import Sequence

import numpy as np


def train_only_clip_bounds(
    train_targets: Sequence[float],
    lower_quantile: float = 0.01,
    upper_quantile: float = 0.99,
) -> tuple[float, float]:
    """
    Calculate clipping bounds using training targets only.
    """

    if not 0 <= lower_quantile < upper_quantile <= 1:
        raise ValueError(
            "Quantiles must satisfy 0 <= lower < upper <= 1."
        )

    values = np.asarray(train_targets, dtype=float)

    if values.size == 0:
        raise ValueError("train_targets cannot be empty.")

    lower = float(np.quantile(values, lower_quantile))
    upper = float(np.quantile(values, upper_quantile))

    return lower, upper


def clip_targets(
    targets: Sequence[float],
    lower: float,
    upper: float,
) -> np.ndarray:
    """
    Clip target values using precomputed bounds.
    """

    if lower > upper:
        raise ValueError("lower cannot be greater than upper.")

    return np.clip(
        np.asarray(targets, dtype=float),
        lower,
        upper,
    )