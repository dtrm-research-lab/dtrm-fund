from dtrm.split_assignment import assign_temporal_split
from dtrm.time_windows import build_time_windows


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