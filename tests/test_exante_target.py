import pytest

from dtrm.exante_target import forward_excess_beta_target


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