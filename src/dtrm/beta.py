"""Beta estimation utilities for DTRM experiments."""

from math import isfinite
from typing import Sequence


def legacy_beta_from_returns(
    stock_returns: Sequence[float],
    market_returns: Sequence[float],
    lookback: int = 252,
    min_observations: int = 60,
) -> float | None:
    """
    Reproduce the mathematical core of the legacy rolling beta.

    beta = cov(stock, market) / (var(market) + 1e-12)

    Only the latest `lookback` aligned observations are used.
    """

    if len(stock_returns) != len(market_returns):
        raise ValueError(
            "stock_returns and market_returns must have the same length."
        )

    if lookback <= 1:
        raise ValueError("lookback must be greater than one.")

    if min_observations <= 1:
        raise ValueError("min_observations must be greater than one.")

    aligned = [
        (float(stock), float(market))
        for stock, market in zip(stock_returns, market_returns)
        if isfinite(float(stock)) and isfinite(float(market))
    ]

    aligned = aligned[-lookback:]

    if len(aligned) < min_observations:
        return None

    stock = [item[0] for item in aligned]
    market = [item[1] for item in aligned]

    n = len(aligned)

    stock_mean = sum(stock) / n
    market_mean = sum(market) / n

    covariance = sum(
        (s - stock_mean) * (m - market_mean)
        for s, m in zip(stock, market)
    ) / (n - 1)

    market_variance = sum(
        (m - market_mean) ** 2
        for m in market
    ) / (n - 1)

    return covariance / (market_variance + 1e-12)