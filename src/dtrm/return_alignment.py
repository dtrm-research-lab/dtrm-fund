"""Daily return alignment utilities."""

from datetime import date, datetime
from typing import Sequence, Union


DateLike = Union[str, date, datetime]
DailyReturnSeries = Sequence[tuple[DateLike, float]]


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


def align_daily_returns(
    stock_returns: DailyReturnSeries,
    market_returns: DailyReturnSeries,
) -> list[tuple[date, float, float]]:
    """
    Align stock and market returns using dates present in both series.

    Equivalent to the legacy inner join by trading date.

    Returns:
        (date, stock_return, market_return)
    """

    stock_by_date = {
        _to_date(return_date): float(value)
        for return_date, value in stock_returns
    }

    market_by_date = {
        _to_date(return_date): float(value)
        for return_date, value in market_returns
    }

    common_dates = sorted(
        set(stock_by_date) & set(market_by_date)
    )

    return [
        (
            return_date,
            stock_by_date[return_date],
            market_by_date[return_date],
        )
        for return_date in common_dates
    ]