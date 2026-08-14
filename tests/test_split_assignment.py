from dtrm.split_assignment import assign_temporal_split
from dtrm.time_windows import build_time_windows
from datetime import date, datetime


WINDOWS = build_time_windows(
    as_of_date="2026-07-05",
)


def test_assigns_train_split():
    assert assign_temporal_split(
        "2025-10-15",
        WINDOWS,
    ) == "train"


def test_assigns_valid_split():
    assert assign_temporal_split(
        "2025-12-24",
        WINDOWS,
    ) == "valid"


def test_assigns_test_split():
    assert assign_temporal_split(
        "2026-04-02",
        WINDOWS,
    ) == "test"


def test_embargo_between_train_and_valid_is_unassigned():
    assert assign_temporal_split(
        "2025-11-15",
        WINDOWS,
    ) is None


def test_embargo_between_valid_and_test_is_unassigned():
    assert assign_temporal_split(
        "2026-02-15",
        WINDOWS,
    ) is None


def test_date_after_test_window_is_unassigned():
    assert assign_temporal_split(
        "2026-05-15",
        WINDOWS,
    ) is None

def test_end_date_after_midnight_is_unassigned():
    windows = {
        "cohort_start": date(2025, 1, 1),
        "train_end": date(2025, 10, 15),
        "valid_start": date(2025, 12, 24),
        "valid_end": date(2026, 1, 22),
        "test_start": date(2026, 4, 2),
        "test_end": date(2026, 5, 1),
    }

    assert (
        assign_temporal_split(
            datetime(2025, 10, 15, 12, 0, 0),
            windows,
        )
        is None
    )