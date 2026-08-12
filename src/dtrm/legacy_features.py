"""Legacy feature reconstruction for DTRM experiments."""

from dtrm.price_alignment import PriceSeries
from dtrm.return_construction import legacy_centered_return
from dtrm.target_windows import DateLike


def legacy_ret_spy_evt_feature(
    market_prices: PriceSeries,
    event_date: DateLike,
    horizon_days: int = 60,
    tolerance_days: int = 5,
) -> float | None:
    """
    Reproduce the legacy ret_spy_evt model feature.

    WARNING
    -------
    This feature uses a centered market return:

        event_date - horizon -> event_date + horizon

    Therefore it includes information occurring after event_date
    and must not be used in an ex-ante prediction model.
    """

    return legacy_centered_return(
        market_prices,
        event_date,
        horizon_days=horizon_days,
        tolerance_days=tolerance_days,
    )