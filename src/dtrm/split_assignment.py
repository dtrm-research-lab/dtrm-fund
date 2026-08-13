"""Temporal split assignment for DTRM experiments."""

from datetime import date, datetime
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


def assign_temporal_split(
    event_date: DateLike,
    windows: dict,
) -> str | None:
    """
    Assign an event to train, valid or test.

    Dates inside embargo gaps, or outside the experiment
    cohort range, are intentionally left unassigned.
    """

    event = _to_date(event_date)

    if windows["cohort_start"] <= event <= windows["train_end"]:
        return "train"

    if windows["valid_start"] <= event <= windows["valid_end"]:
        return "valid"

    if windows["test_start"] <= event <= windows["test_end"]:
        return "test"

    return None