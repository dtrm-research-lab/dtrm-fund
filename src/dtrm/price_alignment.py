"""Trading-timestamp price alignment utilities."""

from datetime import date, datetime, time, timedelta
from typing import Sequence, Union


DateLike = Union[str, date, datetime]
Temporal = Union[date, datetime]
PriceSeries = Sequence[tuple[DateLike, float]]


def _to_datetime(value: DateLike) -> datetime:
    """Convert to datetime for precise temporal comparison."""

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings, date or datetime objects."
    )


def _preserve_temporal_type(value: DateLike) -> Temporal:
    """Preserve date-only inputs while retaining full timestamps."""

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


def price_on_or_before(
    prices: PriceSeries,
    target_date: DateLike,
    tolerance_days: int = 5,
) -> tuple[Temporal, float] | None:
    """Return the closest price on or before target_date."""

    target = _to_datetime(target_date)

    candidates = [
        (_to_datetime(price_date), price_date, price)
        for price_date, price in prices
        if _to_datetime(price_date) <= target
    ]

    if not candidates:
        return None

    matched_dt, original_date, price = max(
        candidates,
        key=lambda item: item[0],
    )

    if target - matched_dt > timedelta(days=tolerance_days):
        return None

    return _preserve_temporal_type(original_date), float(price)


def price_on_or_after(
    prices: PriceSeries,
    target_date: DateLike,
    tolerance_days: int = 5,
) -> tuple[Temporal, float] | None:
    """Return the closest price on or after target_date."""

    target = _to_datetime(target_date)

    candidates = [
        (_to_datetime(price_date), price_date, price)
        for price_date, price in prices
        if _to_datetime(price_date) >= target
    ]

    if not candidates:
        return None

    matched_dt, original_date, price = min(
        candidates,
        key=lambda item: item[0],
    )

    if matched_dt - target > timedelta(days=tolerance_days):
        return None

    return _preserve_temporal_type(original_date), float(price)