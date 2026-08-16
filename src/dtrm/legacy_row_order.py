"""Legacy row-order reconstruction utilities."""

from typing import Sequence

import numpy as np


def legacy_model_row_order(
    tickers: Sequence[str],
    dates: Sequence,
) -> np.ndarray:
    """
    Return row indices reproducing the legacy ordering sequence.

    Legacy trumpDataModel_v4 behavior:

    1. Sort all rows by ticker and date.
    2. Group by ticker preserving ticker-group order.
    3. Sort each ticker block again by date.

    The second single-column sort matters for rows sharing the same
    ticker/date timestamp because XGBoost subsampling is row-order
    sensitive.
    """

    if len(tickers) != len(dates):
        raise ValueError(
            "tickers and dates must have the same length."
        )

    if len(tickers) == 0:
        return np.empty(0, dtype=np.int64)

    ticker_values = np.asarray(
        [str(ticker) for ticker in tickers],
        dtype=object,
    )

    date_values = np.asarray(
        dates,
        dtype="datetime64[ns]",
    ).astype(np.int64)

    # Equivalent to the initial:
    # sort_values(["ticker", "date_dt"])
    initial_order = np.lexsort(
        (date_values, ticker_values)
    )

    ordered_tickers = ticker_values[initial_order]
    ordered_dates = date_values[initial_order]

    result = []

    start = 0
    n_rows = len(initial_order)

    while start < n_rows:
        ticker = ordered_tickers[start]

        end = start + 1

        while (
            end < n_rows
            and ordered_tickers[end] == ticker
        ):
            end += 1

        block_order = np.argsort(
            ordered_dates[start:end],
            kind="quicksort",
        )

        result.extend(
            initial_order[start:end][block_order]
        )

        start = end

    return np.asarray(
        result,
        dtype=np.int64,
    )