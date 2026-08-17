"""Ex-ante target construction for DTRM experiments."""

from dtrm.return_construction import forward_return
from dtrm.target_windows import DateLike
from dtrm.targets import market_adjusted_target
from dtrm.price_alignment import PriceSeries
from dtrm.legacy_beta_pre import legacy_beta_pre_from_prices


def forward_excess_beta_target(
    stock_prices: PriceSeries,
    market_prices: PriceSeries,
    beta: float,
    event_date: DateLike,
    horizon_days: int = 60,
    tolerance_days: int = 5,
) -> float | None:
    """
    Construct the ex-ante excess-beta target.

    Y = stock_forward_return - beta * market_forward_return
    """

    stock_return = forward_return(
        stock_prices,
        event_date,
        horizon_days=horizon_days,
        tolerance_days=tolerance_days,
    )

    market_return = forward_return(
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

def forward_excess_beta_target_from_prices(
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
    Construct the complete ex-ante excess-beta target from prices.

    beta_pre uses only information available on or before event_date.
    The target uses the forward event_date -> event_date + horizon window.
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

    return forward_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=beta,
        event_date=event_date,
        horizon_days=horizon_days,
        tolerance_days=price_tolerance_days,
    )