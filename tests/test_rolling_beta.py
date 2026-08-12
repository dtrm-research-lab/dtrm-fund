import pytest

from dtrm.rolling_beta import rolling_legacy_beta


def test_rolling_beta_starts_after_minimum_observations():
    market_returns = [
        ("2026-01-01", 0.01),
        ("2026-01-02", 0.02),
        ("2026-01-03", -0.01),
        ("2026-01-04", 0.03),
    ]

    stock_returns = [
        ("2026-01-01", 0.02),
        ("2026-01-02", 0.04),
        ("2026-01-03", -0.02),
        ("2026-01-04", 0.06),
    ]

    result = rolling_legacy_beta(
        stock_returns,
        market_returns,
        lookback=4,
        min_observations=3,
    )

    assert len(result) == 2
    assert result[0][0].isoformat() == "2026-01-03"
    assert result[1][0].isoformat() == "2026-01-04"


def test_rolling_beta_equals_two():
    market_returns = [
        ("2026-01-01", 0.01),
        ("2026-01-02", 0.02),
        ("2026-01-03", -0.01),
        ("2026-01-04", 0.03),
    ]

    stock_returns = [
        (date, 2 * value)
        for date, value in market_returns
    ]

    result = rolling_legacy_beta(
        stock_returns,
        market_returns,
        lookback=4,
        min_observations=3,
    )

    assert result[0][1] == pytest.approx(2.0)
    assert result[1][1] == pytest.approx(2.0)


def test_rolling_beta_respects_lookback():
    market_returns = [
        ("2026-01-01", 0.50),
        ("2026-01-02", -0.40),
        ("2026-01-03", 0.01),
        ("2026-01-04", 0.02),
        ("2026-01-05", -0.01),
        ("2026-01-06", 0.03),
    ]

    stock_returns = [
        ("2026-01-01", -0.80),
        ("2026-01-02", 0.90),
        ("2026-01-03", 0.02),
        ("2026-01-04", 0.04),
        ("2026-01-05", -0.02),
        ("2026-01-06", 0.06),
    ]

    result = rolling_legacy_beta(
        stock_returns,
        market_returns,
        lookback=4,
        min_observations=4,
    )

    assert result[-1][1] == pytest.approx(2.0)