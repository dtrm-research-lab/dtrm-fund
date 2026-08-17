"""Ex-ante target construction for DTRM experiments."""

from dtrm.return_construction import forward_return
from dtrm.target_windows import DateLike
from dtrm.targets import market_adjusted_target
from dtrm.price_alignment import PriceSeries


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