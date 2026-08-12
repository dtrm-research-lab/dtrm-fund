import pytest

from dtrm.legacy_target import legacy_excess_beta_target


def test_legacy_excess_beta_target():
    stock_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 120.0),
    ]

    market_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 110.0),
    ]

    result = legacy_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=1.5,
        event_date="2026-01-15",
        horizon_days=60,
        tolerance_days=5,
    )

    # stock return = 20%
    # market return = 10%
    # excess_beta = 0.20 - 1.5 * 0.10 = 0.05
    assert result == pytest.approx(0.05)


def test_legacy_excess_beta_target_with_zero_beta():
    stock_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 115.0),
    ]

    market_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 130.0),
    ]

    result = legacy_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=0.0,
        event_date="2026-01-15",
    )

    assert result == pytest.approx(0.15)


def test_legacy_excess_beta_target_is_none_if_stock_return_missing():
    stock_prices = [
        ("2025-11-01", 100.0),
        ("2026-03-16", 120.0),
    ]

    market_prices = [
        ("2025-11-14", 100.0),
        ("2026-03-16", 110.0),
    ]

    result = legacy_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=1.0,
        event_date="2026-01-15",
        tolerance_days=5,
    )

    assert result is None