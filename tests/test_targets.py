import pytest

from dtrm.targets import market_adjusted_target, simple_return


def test_simple_return_positive():
    result = simple_return(100.0, 110.0)

    assert result == pytest.approx(0.10)


def test_simple_return_negative():
    result = simple_return(100.0, 90.0)

    assert result == pytest.approx(-0.10)


def test_simple_return_rejects_non_positive_start_price():
    with pytest.raises(ValueError):
        simple_return(0.0, 100.0)


def test_market_adjusted_target():
    result = market_adjusted_target(
        stock_return=0.12,
        beta=1.2,
        market_return=0.05,
    )

    assert result == pytest.approx(0.06)


def test_market_adjusted_target_with_negative_market():
    result = market_adjusted_target(
        stock_return=0.02,
        beta=1.0,
        market_return=-0.03,
    )

    assert result == pytest.approx(0.05)