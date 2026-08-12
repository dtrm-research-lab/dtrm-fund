from datetime import date

import pytest

from dtrm.time_windows import build_time_windows


def test_legacy_time_windows_july_2026():
    """
    Reproduce the temporal windows observed in the legacy
    trumpDataModel_v4 notebook for 2026-07-05.
    """

    windows = build_time_windows("2026-07-05")

    assert windows["as_of_date"] == date(2026, 7, 5)

    assert windows["cohort_start"] == date(2025, 1, 1)
    assert windows["cohort_end"] == date(2026, 5, 1)

    assert windows["train_end"] == date(2025, 10, 15)

    assert windows["valid_start"] == date(2025, 12, 24)
    assert windows["valid_end"] == date(2026, 1, 22)

    assert windows["test_start"] == date(2026, 4, 2)
    assert windows["test_end"] == date(2026, 5, 1)

    assert windows["embargo_days"] == 70


def test_embargo_is_derived_from_model_parameters():
    windows = build_time_windows(
        "2026-07-05",
        horizon_days=60,
        asof_tolerance_days=5,
        embargo_extra_days=5,
    )

    assert windows["embargo_days"] == 70


def test_different_as_of_date_changes_windows():
    first = build_time_windows("2026-07-05")
    second = build_time_windows("2026-07-06")

    assert second["cohort_end"] > first["cohort_end"]
    assert second["test_end"] > first["test_end"]


def test_invalid_horizon_raises_error():
    with pytest.raises(ValueError):
        build_time_windows(
            "2026-07-05",
            horizon_days=0,
        )


def test_invalid_date_type_raises_error():
    with pytest.raises(TypeError):
        build_time_windows(12345)