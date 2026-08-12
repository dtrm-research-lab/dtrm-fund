"""Rolling beta series construction."""

from datetime import date

from dtrm.beta import legacy_beta_from_returns
from dtrm.return_alignment import DailyReturnSeries, align_daily_returns


def rolling_legacy_beta(
    stock_returns: DailyReturnSeries,
    market_returns: DailyReturnSeries,
    lookback: int = 252,
    min_observations: int = 60,
) -> list[tuple[date, float]]:
    """
    Construct the legacy rolling beta series.

    For each aligned trading date, beta uses the latest
    `lookback` stock/market return observations including
    the current date.
    """

    aligned = align_daily_returns(
        stock_returns,
        market_returns,
    )

    results: list[tuple[date, float]] = []

    for index in range(len(aligned)):
        window_start = max(
            0,
            index - lookback + 1,
        )

        window = aligned[window_start:index + 1]

        stock_window = [
            stock_return
            for _, stock_return, _ in window
        ]

        market_window = [
            market_return
            for _, _, market_return in window
        ]

        beta = legacy_beta_from_returns(
            stock_window,
            market_window,
            lookback=lookback,
            min_observations=min_observations,
        )

        if beta is not None:
            beta_date = aligned[index][0]
            results.append((beta_date, beta))

    return results