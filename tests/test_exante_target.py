import pytest

from dtrm.exante_target import (
    forward_excess_beta_target,
    forward_excess_beta_target_from_prices,
)


def test_forward_excess_beta_target():
    stock_prices = [
        ("2026-01-16", 100.0),
        ("2026-03-17", 120.0),
    ]

    market_prices = [
        ("2026-01-16", 200.0),
        ("2026-03-17", 210.0),
    ]

    result = forward_excess_beta_target(
        stock_prices=stock_prices,
        market_prices=market_prices,
        beta=1.2,
        event_date="2026-01-15 12:00:00",
        horizon_days=60,
        tolerance_days=5,
    )

    # 20% - 1.2 * 5% = 14%
    assert result == pytest.approx(0.14)

def test_forward_excess_beta_target_from_prices():
    market_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 101.0),
        ("2026-01-03", 103.02),
        ("2026-01-04", 101.9898),
        ("2026-01-06", 200.0),
        ("2026-01-08", 210.0),
    ]

    stock_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),
        ("2026-01-03", 106.08),
        ("2026-01-04", 103.9584),
        ("2026-01-06", 100.0),
        ("2026-01-08", 120.0),
    ]

    result = forward_excess_beta_target_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date="2026-01-05",
        horizon_days=2,
        price_tolerance_days=2,
        beta_lookback=3,
        beta_min_observations=3,
        beta_tolerance_days=20,
    )

    # beta_pre = 2
    # stock forward return = 20%
    # market forward return = 5%
    # target = 20% - 2 * 5% = 10%
    assert result == pytest.approx(0.10)