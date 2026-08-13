import pytest

from dtrm.target_demeaning import (
    demean_targets,
    train_only_ticker_means,
)


def test_train_only_ticker_means():
    means = train_only_ticker_means(
        ["AAPL", "AAPL", "MSFT"],
        [1.0, 3.0, 10.0],
    )

    assert means["AAPL"] == pytest.approx(2.0)
    assert means["MSFT"] == pytest.approx(10.0)


def test_demean_targets_uses_train_means():
    means = {
        "AAPL": 2.0,
        "MSFT": 10.0,
    }

    result = demean_targets(
        ["AAPL", "MSFT"],
        [5.0, 12.0],
        means,
    )

    assert result.tolist() == pytest.approx(
        [3.0, 2.0]
    )


def test_unseen_ticker_uses_zero_mean():
    result = demean_targets(
        ["NVDA"],
        [7.5],
        {"AAPL": 2.0},
    )

    assert result.tolist() == pytest.approx(
        [7.5]
    )


def test_train_lengths_must_match():
    with pytest.raises(ValueError):
        train_only_ticker_means(
            ["AAPL"],
            [1.0, 2.0],
        )


def test_demean_lengths_must_match():
    with pytest.raises(ValueError):
        demean_targets(
            ["AAPL"],
            [1.0, 2.0],
            {"AAPL": 1.0},
        )


def test_empty_training_data_is_rejected():
    with pytest.raises(ValueError):
        train_only_ticker_means([], [])