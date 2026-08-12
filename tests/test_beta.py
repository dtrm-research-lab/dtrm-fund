import pytest

from dtrm.beta import legacy_beta_from_returns


def test_beta_equals_one_for_identical_returns():
    market_returns = [0.01, 0.02, -0.01, 0.03, 0.00]
    stock_returns = market_returns.copy()

    result = legacy_beta_from_returns(
        stock_returns,
        market_returns,
        lookback=5,
        min_observations=5,
    )

    assert result == pytest.approx(1.0)


def test_beta_equals_two_for_double_market_returns():
    market_returns = [0.01, 0.02, -0.01, 0.03, 0.00]
    stock_returns = [2 * value for value in market_returns]

    result = legacy_beta_from_returns(
        stock_returns,
        market_returns,
        lookback=5,
        min_observations=5,
    )

    assert result == pytest.approx(2.0)


def test_beta_requires_minimum_observations():
    result = legacy_beta_from_returns(
        stock_returns=[0.01, 0.02, 0.03],
        market_returns=[0.01, 0.02, 0.03],
        lookback=252,
        min_observations=4,
    )

    assert result is None


def test_beta_uses_only_latest_lookback_observations():
    market_returns = [
        0.50,
        -0.40,
        0.01,
        0.02,
        -0.01,
        0.03,
    ]

    stock_returns = [
        -0.80,
        0.90,
        0.02,
        0.04,
        -0.02,
        0.06,
    ]

    result = legacy_beta_from_returns(
        stock_returns,
        market_returns,
        lookback=4,
        min_observations=4,
    )

    assert result == pytest.approx(2.0)


def test_beta_rejects_misaligned_series():
    with pytest.raises(ValueError):
        legacy_beta_from_returns(
            stock_returns=[0.01, 0.02],
            market_returns=[0.01],
        )