"""Temporal split assignment for DTRM experiments."""

from datetime import date, datetime, time
from typing import Union


DateLike = Union[str, date, datetime]


def _to_datetime(value: DateLike) -> datetime:
    """Convert temporal values to datetime, preserving timestamps."""

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError(
        "Date values must be ISO strings, date or datetime objects."
    )


def assign_temporal_split(
    event_date: DateLike,
    windows: dict,
) -> str | None:
    """
    Assign an event to train, valid or test.

    Date-only window boundaries are interpreted at midnight,
    reproducing the legacy pandas Timestamp comparisons.
    """

    event = _to_datetime(event_date)

    cohort_start = _to_datetime(windows["cohort_start"])
    train_end = _to_datetime(windows["train_end"])
    valid_start = _to_datetime(windows["valid_start"])
    valid_end = _to_datetime(windows["valid_end"])
    test_start = _to_datetime(windows["test_start"])
    test_end = _to_datetime(windows["test_end"])

    if cohort_start <= event <= train_end:
        return "train"

    if valid_start <= event <= valid_end:
        return "valid"

    if test_start <= event <= test_end:
        return "test"

    return None