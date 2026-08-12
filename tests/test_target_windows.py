from datetime import date

import pytest

from dtrm.target_windows import (
    forward_target_window,
    legacy_centered_target_window,
)


def test_legacy_centered_target_window():
    start, end = legacy_centered_target_window("2026-01-15", horizon_days=60)

    assert start == date(2025, 11, 16)
    assert end == date(2026, 3, 16)


def test_forward_target_window():
    start, end = forward_target_window("2026-01-15", horizon_days=60)

    assert start == date(2026, 1, 15)
    assert end == date(2026, 3, 16)


def test_legacy_window_is_centered_around_event():
    event_date = date(2026, 1, 15)

    start, end = legacy_centered_target_window(event_date, horizon_days=60)

    assert (event_date - start).days == 60
    assert (end - event_date).days == 60


def test_forward_window_starts_at_event():
    event_date = date(2026, 1, 15)

    start, end = forward_target_window(event_date, horizon_days=60)

    assert start == event_date
    assert (end - start).days == 60


def test_invalid_horizon_raises_error():
    with pytest.raises(ValueError):
        legacy_centered_target_window("2026-01-15", horizon_days=0)

    with pytest.raises(ValueError):
        forward_target_window("2026-01-15", horizon_days=0)