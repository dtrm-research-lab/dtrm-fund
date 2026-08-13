import pytest

from dtrm.legacy_beta_pre import legacy_beta_pre_from_prices


def test_legacy_beta_pre_from_prices_equals_two():
    market_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 101.0),       # +1%
        ("2026-01-03", 103.02),      # +2%
        ("2026-01-04", 101.9898),    # -1%
    ]

    stock_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),       # +2%
        ("2026-01-03", 106.08),      # +4%
        ("2026-01-04", 103.9584),    # -2%
    ]

    result = legacy_beta_pre_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date="2026-01-05",
        lookback=3,
        min_observations=3,
        tolerance_days=20,
    )

    assert result == pytest.approx(2.0)


def test_legacy_beta_pre_requires_minimum_observations():
    market_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 101.0),
        ("2026-01-03", 103.02),
        ("2026-01-04", 101.9898),
    ]

    stock_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),
        ("2026-01-03", 106.08),
        ("2026-01-04", 103.9584),
    ]

    result = legacy_beta_pre_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date="2026-01-05",
        lookback=4,
        min_observations=4,
        tolerance_days=20,
    )

    assert result is None


def test_legacy_beta_pre_respects_event_tolerance():
    market_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 101.0),
        ("2026-01-03", 103.02),
        ("2026-01-04", 101.9898),
    ]

    stock_prices = [
        ("2026-01-01", 100.0),
        ("2026-01-02", 102.0),
        ("2026-01-03", 106.08),
        ("2026-01-04", 103.9584),
    ]

    result = legacy_beta_pre_from_prices(
        stock_prices=stock_prices,
        market_prices=market_prices,
        event_date="2026-01-30",
        lookback=3,
        min_observations=3,
        tolerance_days=20,
    )

    assert result is None