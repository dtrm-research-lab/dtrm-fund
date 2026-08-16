import numpy as np
import pytest

from dtrm.legacy_model_rows import (
    order_selected_legacy_rows,
)


def test_orders_full_dataset_before_selecting_rows():
    full_tickers = [
        "B",
        "A",
        "A",
        "B",
    ]

    full_dates = [
        "2025-01-02",
        "2025-01-02",
        "2025-01-01",
        "2025-01-01",
    ]

    full_keys = [
        ("n0", "B"),
        ("n1", "A"),
        ("n2", "A"),
        ("n3", "B"),
    ]

    selected_keys = [
        ("n0", "B"),
        ("n2", "A"),
        ("n3", "B"),
    ]

    result = order_selected_legacy_rows(
        full_tickers,
        full_dates,
        full_keys,
        selected_keys,
    )

    np.testing.assert_array_equal(
        result,
        np.array([1, 2, 0], dtype=np.int64),
    )


def test_rejects_duplicate_selected_keys():
    with pytest.raises(
        ValueError,
        match="selected_keys must be unique",
    ):
        order_selected_legacy_rows(
            ["A", "A"],
            ["2025-01-01", "2025-01-02"],
            [("n1", "A"), ("n2", "A")],
            [("n1", "A"), ("n1", "A")],
        )


def test_rejects_missing_selected_keys():
    with pytest.raises(
        ValueError,
        match="not all selected_keys were found",
    ):
        order_selected_legacy_rows(
            ["A"],
            ["2025-01-01"],
            [("n1", "A")],
            [("missing", "A")],
        )


def test_rejects_mismatched_full_lengths():
    with pytest.raises(
        ValueError,
        match="must have the same length",
    ):
        order_selected_legacy_rows(
            ["A", "B"],
            ["2025-01-01"],
            [("n1", "A"), ("n2", "B")],
            [("n1", "A")],
        )