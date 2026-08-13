import pytest

from dtrm.legacy_target import legacy_excess_beta_target_from_prices


def test_legacy_excess_beta_target_from_prices():
    market_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 101.0),          # +1%
        ("2026-01-03", 103.02),         # +2%
        ("2026-01-04", 101.9898),       # -1%
        ("2026-01-05", 105.049494),     # +3%
        ("2026-01-06", 109.0),
        ("2026-01-07", 113.322),        # +10% vs Jan 3
    ]

    stock_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),          # +2%
        ("2026-01-03", 106.08),         # +4%
        ("2026-01-04", 103.9584),       # -2%
        ("2026-01-05", 110.195904),     # +6%
        ("2026-01-06", 121.0),
        ("2026-01-07", 132.6),          # +25% vs Jan 3
    ]

    result = legacy_excess_beta_target_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date="2026-01-05",
        horizon_days=2,
        price_tolerance_days=0,
        beta_lookback=3,
        beta_min_observations=3,
        beta_tolerance_days=20,
    )

    # beta_pre = 2
    # stock centered return = 25%
    # market centered return = 10%
    #
    # excess_beta = 0.25 - 2 * 0.10 = 0.05

    assert result == pytest.approx(0.05)