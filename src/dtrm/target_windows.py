"""Target horizon definitions for DTRM experiments."""

from datetime import date, datetime, timedelta
from typing import Union


DateLike = Union[str, date, datetime]
Temporal = Union[date, datetime]


def _to_temporal(value: DateLike) -> Temporal:
    """Preserve timestamp information when it exists."""

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        if "T" in value or " " in value:
            return datetime.fromisoformat(value)
        return date.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings, date or datetime objects."
    )


def legacy_centered_target_window(
    event_date: DateLike,
    horizon_days: int = 60,
) -> tuple[Temporal, Temporal]:
    """
    Reproduce the legacy DTRM target window.

    Legacy definition:
        start = event_date - horizon
        end   = event_date + horizon

    Timestamp information is preserved because the legacy notebook
    performs merge_asof against the full event timestamp.
    """

    event = _to_temporal(event_date)

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    return (
        event - timedelta(days=horizon_days),
        event + timedelta(days=horizon_days),
    )


def forward_target_window(
    event_date: DateLike,
    horizon_days: int = 60,
) -> tuple[Temporal, Temporal]:
    """
    Define an ex-ante forward target window.

    Forward definition:
        start = event_date
        end   = event_date + horizon
    """

    event = _to_temporal(event_date)

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    return (
        event,
        event + timedelta(days=horizon_days),
    )