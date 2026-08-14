import pytest

from dtrm.return_construction import legacy_centered_return


def test_legacy_centered_return():
    prices = [
        ("2025-11-14", 100.0),  # before target start: 2025-11-16
        ("2026-03-16", 120.0),  # exact target end
    ]

    result = legacy_centered_return(
        prices,
        event_date="2026-01-15",
        horizon_days=60,
        tolerance_days=5,
    )

    assert result == pytest.approx(0.20)


def test_legacy_return_uses_backward_and_forward_alignment():
    prices = [
        ("2025-11-14", 100.0),  # backward from 2025-11-16
        ("2026-03-17", 121.0),  # forward from 2026-03-16
    ]

    result = legacy_centered_return(
        prices,
        event_date="2026-01-15",
        horizon_days=60,
        tolerance_days=5,
    )

    assert result == pytest.approx(0.21)


def test_legacy_return_is_none_when_price_outside_tolerance():
    prices = [
        ("2025-11-01", 100.0),
        ("2026-03-16", 120.0),
    ]

    result = legacy_centered_return(
        prices,
        event_date="2026-01-15",
        horizon_days=60,
        tolerance_days=5,
    )

    assert result is None

def test_legacy_centered_return_preserves_event_timestamp():
    prices = [
        ("2024-12-13", 447.27),
        ("2024-12-16", 451.59),
        ("2025-04-14", 387.81),
        ("2025-04-15", 385.73),
    ]

    result = legacy_centered_return(
        prices,
        "2025-02-13 22:04:26",
        horizon_days=60,
        tolerance_days=5,
    )

    expected = (385.73 - 447.27) / 447.27

    assert result == expected