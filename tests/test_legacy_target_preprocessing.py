import pytest

from dtrm.legacy_target_preprocessing import preprocess_legacy_targets


def test_preprocess_legacy_targets():
    result = preprocess_legacy_targets(
        train_tickers=["AAPL", "AAPL", "MSFT"],
        train_targets=[0.0, 2.0, 10.0],
        valid_tickers=["AAPL", "MSFT"],
        valid_targets=[3.0, 20.0],
        test_tickers=["AAPL", "NVDA"],
        test_targets=[-10.0, 5.0],
        lower_quantile=0.0,
        upper_quantile=1.0,
    )

    assert result["clip_lower"] == pytest.approx(0.0)
    assert result["clip_upper"] == pytest.approx(10.0)

    assert result["ticker_means"]["AAPL"] == pytest.approx(1.0)
    assert result["ticker_means"]["MSFT"] == pytest.approx(10.0)

    assert result["train"].tolist() == pytest.approx(
        [-1.0, 1.0, 0.0]
    )

    assert result["valid"].tolist() == pytest.approx(
        [2.0, 0.0]
    )

    # AAPL: -10 clips to 0, then subtracts AAPL train mean 1 -> -1
    # NVDA: unseen ticker, so mean = 0
    assert result["test"].tolist() == pytest.approx(
        [-1.0, 5.0]
    )


def test_valid_and_test_do_not_change_train_derived_parameters():
    first = preprocess_legacy_targets(
        train_tickers=["AAPL", "AAPL"],
        train_targets=[0.0, 2.0],
        valid_tickers=["AAPL"],
        valid_targets=[100.0],
        test_tickers=["AAPL"],
        test_targets=[100.0],
        lower_quantile=0.0,
        upper_quantile=1.0,
    )

    second = preprocess_legacy_targets(
        train_tickers=["AAPL", "AAPL"],
        train_targets=[0.0, 2.0],
        valid_tickers=["AAPL"],
        valid_targets=[-1000.0],
        test_tickers=["AAPL"],
        test_targets=[-1000.0],
        lower_quantile=0.0,
        upper_quantile=1.0,
    )

    assert first["clip_lower"] == second["clip_lower"]
    assert first["clip_upper"] == second["clip_upper"]
    assert first["ticker_means"] == second["ticker_means"]