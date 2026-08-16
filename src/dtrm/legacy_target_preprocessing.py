"""Legacy target preprocessing pipeline."""

from typing import Sequence

import numpy as np

from dtrm.target_clipping import train_only_clip_bounds

def _kahan_mean_float32(values) -> np.float32:
    values = np.asarray(
        values,
        dtype=np.float32,
    )

    total = np.float32(0.0)
    compensation = np.float32(0.0)

    for value in values:
        adjusted = np.float32(
            value - compensation
        )

        updated = np.float32(
            total + adjusted
        )

        compensation = np.float32(
            (updated - total) - adjusted
        )

        total = updated

    return np.float32(
        total / np.float32(len(values))
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
    """Reproduce legacy clipping and ticker de-meaning semantics."""

    lower, upper = train_only_clip_bounds(
        train_targets,
        lower_quantile=lower_quantile,
        upper_quantile=upper_quantile,
    )

    train_clipped = np.clip(
        np.asarray(train_targets, dtype=np.float32),
        lower,
        upper,
    ).astype(np.float32)

    valid_clipped = np.clip(
        np.asarray(valid_targets, dtype=np.float32),
        lower,
        upper,
    ).astype(np.float32)

    test_clipped = np.clip(
        np.asarray(test_targets, dtype=np.float32),
        lower,
        upper,
    ).astype(np.float32)

    grouped: dict[str, list[np.float32]] = {}

    for ticker, target in zip(train_tickers, train_clipped):
        grouped.setdefault(str(ticker), []).append(target)

    ticker_means = {
        ticker: _kahan_mean_float32(values)
        for ticker, values in grouped.items()
    }

    def demean(tickers, targets):
        means = np.asarray(
            [
                ticker_means.get(
                    str(ticker),
                    np.float32(0.0),
                )
                for ticker in tickers
            ],
            dtype=np.float32,
        )

        return (
            np.asarray(
                targets,
                dtype=np.float32,
            )
            - means
        ).astype(np.float32)

    return {
        "clip_lower": lower,
        "clip_upper": upper,
        "ticker_means": ticker_means,
        "train": demean(
            train_tickers,
            train_clipped,
        ),
        "valid": demean(
            valid_tickers,
            valid_clipped,
        ),
        "test": demean(
            test_tickers,
            test_clipped,
        ),
    }