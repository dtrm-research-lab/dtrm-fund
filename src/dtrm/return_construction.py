"""Return construction for DTRM experiments."""

from dtrm.price_alignment import (
    PriceSeries,
    price_on_or_after,
    price_on_or_before,
)
from dtrm.target_windows import (
    DateLike,
    forward_target_window,
    legacy_centered_target_window,
)
from dtrm.targets import simple_return

def legacy_centered_return(
    prices: PriceSeries,
    event_date: DateLike,
    horizon_days: int = 60,
    tolerance_days: int = 5,
) -> float | None:
    """
    Reproduce the legacy DTRM centered return.

    Window:
        event_date - horizon -> event_date + horizon

    Price alignment:
        start -> closest price on or before
        end   -> closest price on or after
    """

    target_start, target_end = legacy_centered_target_window(
        event_date,
        horizon_days=horizon_days,
    )

    start_match = price_on_or_before(
        prices,
        target_start,
        tolerance_days=tolerance_days,
    )

    end_match = price_on_or_after(
        prices,
        target_end,
        tolerance_days=tolerance_days,
    )

    if start_match is None or end_match is None:
        return None

    _, start_price = start_match
    _, end_price = end_match

    return simple_return(start_price, end_price)

def forward_return(
    prices: PriceSeries,
    event_date: DateLike,
    horizon_days: int = 60,
    tolerance_days: int = 5,
) -> float | None:
    """
    Construct a genuinely ex-ante forward return.

    Window:
        event_date -> event_date + horizon

    Both prices must be observable on or after
    their respective target timestamps.
    """

    target_start, target_end = forward_target_window(
        event_date,
        horizon_days=horizon_days,
    )

    start_match = price_on_or_after(
        prices,
        target_start,
        tolerance_days=tolerance_days,
    )

    end_match = price_on_or_after(
        prices,
        target_end,
        tolerance_days=tolerance_days,
    )

    if start_match is None or end_match is None:
        return None

    _, start_price = start_match
    _, end_price = end_match

    return simple_return(
        start_price,
        end_price,
    )