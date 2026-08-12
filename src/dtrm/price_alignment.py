"""Trading-date price alignment utilities."""

from datetime import date, datetime
from typing import Sequence, Union


DateLike = Union[str, date, datetime]
PriceSeries = Sequence[tuple[DateLike, float]]


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


def price_on_or_before(
    prices: PriceSeries,
    target_date: DateLike,
    tolerance_days: int = 5,
) -> tuple[date, float] | None:
    """Return the closest price on or before target_date."""

    target = _to_date(target_date)

    candidates = [
        (_to_date(price_date), price)
        for price_date, price in prices
        if _to_date(price_date) <= target
    ]

    if not candidates:
        return None

    price_date, price = max(candidates, key=lambda item: item[0])

    if (target - price_date).days > tolerance_days:
        return None

    return price_date, float(price)


def price_on_or_after(
    prices: PriceSeries,
    target_date: DateLike,
    tolerance_days: int = 5,
) -> tuple[date, float] | None:
    """Return the closest price on or after target_date."""

    target = _to_date(target_date)

    candidates = [
        (_to_date(price_date), price)
        for price_date, price in prices
        if _to_date(price_date) >= target
    ]

    if not candidates:
        return None

    price_date, price = min(candidates, key=lambda item: item[0])

    if (price_date - target).days > tolerance_days:
        return None

    return price_date, float(price)