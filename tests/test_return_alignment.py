from datetime import date

from dtrm.return_alignment import align_daily_returns


def test_align_daily_returns_keeps_only_common_dates():
    stock_returns = [
        ("2026-01-05", 0.01),
        ("2026-01-06", 0.02),
        ("2026-01-07", 0.03),
    ]

    market_returns = [
        ("2026-01-06", 0.005),
        ("2026-01-07", -0.01),
        ("2026-01-08", 0.02),
    ]

    result = align_daily_returns(
        stock_returns,
        market_returns,
    )

    assert result == [
        (date(2026, 1, 6), 0.02, 0.005),
        (date(2026, 1, 7), 0.03, -0.01),
    ]


def test_align_daily_returns_sorts_by_date():
    stock_returns = [
        ("2026-01-07", 0.03),
        ("2026-01-06", 0.02),
    ]

    market_returns = [
        ("2026-01-07", -0.01),
        ("2026-01-06", 0.005),
    ]

    result = align_daily_returns(
        stock_returns,
        market_returns,
    )

    assert result[0][0] == date(2026, 1, 6)
    assert result[1][0] == date(2026, 1, 7)


def test_align_daily_returns_returns_empty_if_no_common_dates():
    stock_returns = [
        ("2026-01-05", 0.01),
    ]

    market_returns = [
        ("2026-01-06", 0.02),
    ]

    result = align_daily_returns(
        stock_returns,
        market_returns,
    )

    assert result == []