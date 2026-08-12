"""Daily return construction utilities."""

from datetime import date, datetime

from dtrm.price_alignment import PriceSeries
from dtrm.targets import simple_return


def _to_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings ('YYYY-MM-DD'), date or datetime objects."
    )


def daily_simple_returns(
    prices: PriceSeries,
) -> list[tuple[date, float]]:
    """
    Convert an ordered price history into daily simple returns.

    Each return is assigned to the ending date:

        R_t = (P_t - P_{t-1}) / P_{t-1}
    """

    normalized = sorted(
        [(_to_date(price_date), float(price)) for price_date, price in prices],
        key=lambda item: item[0],
    )

    if len(normalized) < 2:
        return []

    returns = []

    for previous, current in zip(normalized[:-1], normalized[1:]):
        previous_date, previous_price = previous
        current_date, current_price = current

        if current_date == previous_date:
            raise ValueError("Price dates must be unique.")

        returns.append(
            (
                current_date,
                simple_return(previous_price, current_price),
            )
        )

    return returns