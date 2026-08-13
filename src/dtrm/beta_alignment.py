"""Legacy beta-to-event alignment."""

from datetime import date, datetime
from typing import Sequence, Union


DateLike = Union[str, date, datetime]
BetaSeries = Sequence[tuple[DateLike, float]]


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


def beta_on_or_before(
    betas: BetaSeries,
    event_date: DateLike,
    tolerance_days: int = 20,
) -> tuple[date, float] | None:
    """
    Return the latest beta on or before event_date.

    Reproduces the legacy backward as-of alignment used
    to construct beta_pre.
    """

    event = _to_date(event_date)

    candidates = [
        (_to_date(beta_date), float(beta))
        for beta_date, beta in betas
        if _to_date(beta_date) <= event
    ]

    if not candidates:
        return None

    beta_date, beta = max(
        candidates,
        key=lambda item: item[0],
    )

    if (event - beta_date).days > tolerance_days:
        return None

    return beta_date, beta