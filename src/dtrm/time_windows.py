"""Temporal window construction for DTRM experiments."""

from datetime import date, datetime, timedelta
from typing import Union


DateLike = Union[str, date, datetime]


def _to_date(value: DateLike) -> date:
    """Convert an ISO date string, date or datetime into a date."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings ('YYYY-MM-DD'), date or datetime objects."
    )


def build_time_windows(
    as_of_date: DateLike,
    cohort_start: DateLike = "2025-01-01",
    horizon_days: int = 60,
    asof_tolerance_days: int = 5,
    embargo_extra_days: int = 5,
    valid_days: int = 30,
    test_days: int = 30,
) -> dict[str, date | int]:
    """
    Build reproducible temporal windows for the DTRM model.

    The function intentionally requires an explicit `as_of_date`.
    It must never depend on the current system date.

    Timeline:

        TRAIN ---- embargo ---- VALID ---- embargo ---- TEST

    The latest trainable cohort date is:

        as_of_date - horizon_days - asof_tolerance_days

    Returns
    -------
    dict
        Temporal boundaries and embargo configuration.
    """

    as_of = _to_date(as_of_date)
    cohort_start_date = _to_date(cohort_start)

    if horizon_days <= 0:
        raise ValueError("horizon_days must be greater than zero.")

    if valid_days <= 0 or test_days <= 0:
        raise ValueError("valid_days and test_days must be greater than zero.")

    if asof_tolerance_days < 0 or embargo_extra_days < 0:
        raise ValueError("Tolerance and embargo values cannot be negative.")

    embargo_days = (
        horizon_days
        + asof_tolerance_days
        + embargo_extra_days
    )

    cohort_end = as_of - timedelta(
        days=horizon_days + asof_tolerance_days
    )

    test_end = cohort_end
    test_start = test_end - timedelta(days=test_days - 1)

    valid_end = test_start - timedelta(days=embargo_days)
    valid_start = valid_end - timedelta(days=valid_days - 1)

    train_end = valid_start - timedelta(days=embargo_days)

    if train_end < cohort_start_date:
        raise ValueError(
            "The calculated training window ends before cohort_start."
        )

    return {
        "as_of_date": as_of,
        "cohort_start": cohort_start_date,
        "cohort_end": cohort_end,
        "train_end": train_end,
        "valid_start": valid_start,
        "valid_end": valid_end,
        "test_start": test_start,
        "test_end": test_end,
        "embargo_days": embargo_days,
    }