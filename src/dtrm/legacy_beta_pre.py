"""Legacy beta_pre reconstruction."""

from dtrm.beta_alignment import beta_on_or_before
from dtrm.daily_returns import daily_simple_returns
from dtrm.price_alignment import PriceSeries
from dtrm.rolling_beta import rolling_legacy_beta
from dtrm.target_windows import DateLike


def legacy_beta_pre_from_prices(
    stock_prices: PriceSeries,
    market_prices: PriceSeries,
    event_date: DateLike,
    lookback: int = 252,
    min_observations: int = 60,
    tolerance_days: int = 20,
) -> float | None:
    """
    Reproduce legacy beta_pre from stock and market prices.

    prices
        -> daily returns
        -> aligned rolling beta
        -> latest beta on or before event_date
    """

    stock_returns = daily_simple_returns(stock_prices)
    market_returns = daily_simple_returns(market_prices)

    beta_series = rolling_legacy_beta(
        stock_returns,
        market_returns,
        lookback=lookback,
        min_observations=min_observations,
    )

    beta_match = beta_on_or_before(
        beta_series,
        event_date,
        tolerance_days=tolerance_days,
    )

    if beta_match is None:
        return None

    _, beta = beta_match

    return beta