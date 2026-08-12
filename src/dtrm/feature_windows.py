"""Feature horizon definitions for DTRM experiments."""

from datetime import date, datetime, timedelta
from typing import Union


DateLike = Union[str, date, datetime]


def _to_date(value: DateLike) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings ('YYYY-MM-DD'), date or datetime objects."
    )


def trailing_feature_window(
    event_date: DateLike,
    lookback_days: int = 60,
) -> tuple[date, date]:
    """
    Define an ex-ante trailing feature window.

    Feature definition:
        start = event_date - lookback
        end   = event_date

    No information after event_date is allowed.
    """

    event = _to_date(event_date)

    if lookback_days <= 0:
        raise ValueError("lookback_days must be greater than zero.")

    return (
        event - timedelta(days=lookback_days),
        event,
    )