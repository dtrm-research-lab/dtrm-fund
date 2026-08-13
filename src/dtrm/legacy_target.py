"""Legacy DTRM target reconstruction."""

from dtrm.legacy_beta_pre import legacy_beta_pre_from_prices
from dtrm.price_alignment import PriceSeries
from dtrm.return_construction import legacy_centered_return
from dtrm.target_windows import DateLike
from dtrm.targets import market_adjusted_target


def legacy_excess_beta_target(
    stock_prices: PriceSeries,
    market_prices: PriceSeries,
    beta: float,
    event_date: DateLike,
    horizon_days: int = 60,
    tolerance_days: int = 5,
) -> float | None:
    """
    Reproduce the legacy DTRM excess-beta target.

    Y = stock_centered_return - beta * market_centered_return
    """

    stock_return = legacy_centered_return(
        stock_prices,
        event_date,
        horizon_days=horizon_days,
        tolerance_days=tolerance_days,
    )

    market_return = legacy_centered_return(
        market_prices,
        event_date,
        horizon_days=horizon_days,
        tolerance_days=tolerance_days,
    )

    if stock_return is None or market_return is None:
        return None

    return market_adjusted_target(
        stock_return=stock_return,
        beta=beta,
        market_return=market_return,
    )


def legacy_excess_beta_target_from_prices(
    stock_prices: PriceSeries,
    market_prices: PriceSeries,
    event_date: DateLike,
    horizon_days: int = 60,
    price_tolerance_days: int = 5,
    beta_lookback: int = 252,
    beta_min_observations: int = 60,
    beta_tolerance_days: int = 20,
) -> float | None:
    """
    Reconstruct the complete legacy excess-beta target from prices.
    """

    beta = legacy_beta_pre_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date=event_date,
        lookback=beta_lookback,
        min_observations=beta_min_observations,
        tolerance_days=beta_tolerance_days,
    )

    if beta is None:
        return None

    return legacy_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=beta,
        event_date=event_date,
        horizon_days=horizon_days,
        tolerance_days=price_tolerance_days,
    )