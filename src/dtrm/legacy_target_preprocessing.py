"""Legacy target preprocessing pipeline."""

from typing import Sequence

import numpy as np

from dtrm.target_clipping import (
    clip_targets,
    train_only_clip_bounds,
)
from dtrm.target_demeaning import (
    demean_targets,
    train_only_ticker_means,
)


def preprocess_legacy_targets(
    train_tickers: Sequence[str],
    train_targets: Sequence[float],
    valid_tickers: Sequence[str],
    valid_targets: Sequence[float],
    test_tickers: Sequence[str],
    test_targets: Sequence[float],
    lower_quantile: float = 0.01,
    upper_quantile: float = 0.99,
) -> dict:
    """
    Reproduce legacy target preprocessing.

    1. Calculate clipping bounds from TRAIN only.
    2. Apply those same bounds to train, valid and test.
    3. Calculate ticker means from clipped TRAIN only.
    4. Apply those train-derived means to all splits.
    """

    lower, upper = train_only_clip_bounds(
        train_targets,
        lower_quantile=lower_quantile,
        upper_quantile=upper_quantile,
    )

    train_clipped = clip_targets(train_targets, lower, upper)
    valid_clipped = clip_targets(valid_targets, lower, upper)
    test_clipped = clip_targets(test_targets, lower, upper)

    ticker_means = train_only_ticker_means(
        train_tickers,
        train_clipped,
    )

    return {
        "clip_lower": lower,
        "clip_upper": upper,
        "ticker_means": ticker_means,
        "train": demean_targets(
            train_tickers,
            train_clipped,
            ticker_means,
        ),
        "valid": demean_targets(
            valid_tickers,
            valid_clipped,
            ticker_means,
        ),
        "test": demean_targets(
            test_tickers,
            test_clipped,
            ticker_means,
        ),
    }