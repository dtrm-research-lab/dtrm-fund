import pytest

from dtrm.daily_returns import daily_simple_returns


def test_daily_simple_returns():
    prices = [
        ("2026-01-05", 100.0),
        ("2026-01-06", 110.0),
        ("2026-01-07", 99.0),
    ]

    result = daily_simple_returns(prices)

    assert result[0][1] == pytest.approx(0.10)
    assert result[1][1] == pytest.approx(-0.10)


def test_daily_returns_are_assigned_to_end_date():
    prices = [
        ("2026-01-05", 100.0),
        ("2026-01-06", 105.0),
    ]

    result = daily_simple_returns(prices)

    assert result[0][0].isoformat() == "2026-01-06"


def test_daily_returns_sort_prices_by_date():
    prices = [
        ("2026-01-07", 121.0),
        ("2026-01-05", 100.0),
        ("2026-01-06", 110.0),
    ]

    result = daily_simple_returns(prices)

    assert result[0][1] == pytest.approx(0.10)
    assert result[1][1] == pytest.approx(0.10)


def test_daily_returns_requires_two_prices():
    result = daily_simple_returns(
        [("2026-01-05", 100.0)]
    )

    assert result == []


def test_daily_returns_rejects_duplicate_dates():
    prices = [
        ("2026-01-05", 100.0),
        ("2026-01-05", 101.0),
    ]

    with pytest.raises(ValueError):
        daily_simple_returns(prices)