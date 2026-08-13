"""Train-only ticker de-meaning utilities."""

from typing import Sequence

import numpy as np # type: ignore


def train_only_ticker_means(
    tickers: Sequence[str],
    train_targets: Sequence[float],
) -> dict[str, float]:
    """
    Calculate per-ticker target means using training data only.
    """

    if len(tickers) != len(train_targets):
        raise ValueError(
            "tickers and train_targets must have the same length."
        )

    if len(tickers) == 0:
        raise ValueError("Training data cannot be empty.")

    grouped: dict[str, list[float]] = {}

    for ticker, target in zip(tickers, train_targets):
        grouped.setdefault(str(ticker), []).append(float(target))

    return {
        ticker: float(np.mean(values))
        for ticker, values in grouped.items()
    }


def demean_targets(
    tickers: Sequence[str],
    targets: Sequence[float],
    ticker_means: dict[str, float],
) -> np.ndarray:
    """
    Subtract train-derived ticker means from target values.

    Unseen tickers use a mean of zero, matching legacy behavior.
    """

    if len(tickers) != len(targets):
        raise ValueError(
            "tickers and targets must have the same length."
        )

    return np.asarray(
        [
            float(target) - ticker_means.get(str(ticker), 0.0)
            for ticker, target in zip(tickers, targets)
        ],
        dtype=float,
    )