from datetime import date

import pytest

from dtrm.feature_windows import trailing_feature_window


def test_trailing_feature_window():
    start, end = trailing_feature_window(
        "2026-01-15",
        lookback_days=60,
    )

    assert start == date(2025, 11, 16)
    assert end == date(2026, 1, 15)


def test_feature_window_ends_at_event_date():
    event_date = date(2026, 1, 15)

    start, end = trailing_feature_window(
        event_date,
        lookback_days=60,
    )

    assert end == event_date
    assert (end - start).days == 60


def test_feature_window_never_uses_future_information():
    event_date = date(2026, 1, 15)

    _, end = trailing_feature_window(
        event_date,
        lookback_days=60,
    )

    assert end <= event_date


def test_invalid_lookback_raises_error():
    with pytest.raises(ValueError):
        trailing_feature_window(
            "2026-01-15",
            lookback_days=0,
        )