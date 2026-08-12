from datetime import date

from dtrm.price_alignment import (
    price_on_or_after,
    price_on_or_before,
)


PRICES = [
    ("2026-01-09", 100.0),  # Friday
    ("2026-01-12", 102.0),  # Monday
    ("2026-01-13", 103.0),
]


def test_price_on_or_before_exact_date():
    result = price_on_or_before(
        PRICES,
        "2026-01-12",
        tolerance_days=5,
    )

    assert result == (date(2026, 1, 12), 102.0)


def test_price_on_or_before_weekend():
    result = price_on_or_before(
        PRICES,
        "2026-01-11",  # Sunday
        tolerance_days=5,
    )

    assert result == (date(2026, 1, 9), 100.0)


def test_price_on_or_after_weekend():
    result = price_on_or_after(
        PRICES,
        "2026-01-11",  # Sunday
        tolerance_days=5,
    )

    assert result == (date(2026, 1, 12), 102.0)


def test_price_before_respects_tolerance():
    result = price_on_or_before(
        [("2026-01-01", 100.0)],
        "2026-01-10",
        tolerance_days=5,
    )

    assert result is None


def test_price_after_respects_tolerance():
    result = price_on_or_after(
        [("2026-01-20", 100.0)],
        "2026-01-10",
        tolerance_days=5,
    )

    assert result is None


def test_price_alignment_returns_float_price():
    result = price_on_or_before(
        [("2026-01-12", 100)],
        "2026-01-12",
    )

    assert result == (date(2026, 1, 12), 100.0)