import numpy as np
import pytest

from dtrm.legacy_row_order import legacy_model_row_order


def test_legacy_model_row_order():
    tickers = [
        "MSFT",
        "AAPL",
        "AAPL",
        "MSFT",
        "AAPL",
    ]

    dates = [
        "2025-01-02",
        "2025-01-02",
        "2025-01-02",
        "2025-01-01",
        "2025-01-01",
    ]

    order = legacy_model_row_order(
        tickers,
        dates,
    )

    assert order.dtype == np.int64

    assert order.tolist() == [
        4,  # AAPL 2025-01-01
        1,  # AAPL 2025-01-02
        2,  # AAPL 2025-01-02
        3,  # MSFT 2025-01-01
        0,  # MSFT 2025-01-02
    ]


def test_equal_ticker_date_preserves_source_order():
    tickers = [
        "AAPL",
        "AAPL",
        "AAPL",
    ]

    dates = [
        "2025-01-01",
        "2025-01-01",
        "2025-01-01",
    ]

    order = legacy_model_row_order(
        tickers,
        dates,
    )

    assert order.tolist() == [0, 1, 2]


def test_legacy_model_row_order_rejects_length_mismatch():
    with pytest.raises(
        ValueError,
        match="same length",
    ):
        legacy_model_row_order(
            ["AAPL", "MSFT"],
            ["2025-01-01"],
        )