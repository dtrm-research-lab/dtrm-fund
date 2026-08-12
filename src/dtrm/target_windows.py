"""Target horizon definitions for DTRM experiments."""

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


def legacy_centered_target_window(
    event_date: DateLike,
    horizon_days: int = 60,
) -> tuple[date, date]:
    """
    Reproduce the legacy DTRM target window.

    Legacy definition:
        start = event_date - horizon
        end   = event_date + horizon
    """

    event = _to_date(event_date)

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    return (
        event - timedelta(days=horizon_days),
        event + timedelta(days=horizon_days),
    )


def forward_target_window(
    event_date: DateLike,
    horizon_days: int = 60,
) -> tuple[date, date]:
    """
    Define an ex-ante forward target window.

    Forward definition:
        start = event_date
        end   = event_date + horizon
    """

    event = _to_date(event_date)

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    return (
        event,
        event + timedelta(days=horizon_days),
    )