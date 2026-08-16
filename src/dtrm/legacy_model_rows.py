"""Legacy model-row ordering utilities."""

import numpy as np

from dtrm.legacy_row_order import legacy_model_row_order


def order_selected_legacy_rows(
    full_tickers,
    full_dates,
    full_keys,
    selected_keys,
) -> np.ndarray:
    """
    Return selected-row indices in exact legacy model order.

    Legacy semantics:
    1. order the full pre-filter dataset;
    2. only then retain model-selected rows.
    """

    if (
        len(full_tickers) != len(full_dates)
        or len(full_tickers) != len(full_keys)
    ):
        raise ValueError(
            "full_tickers, full_dates and full_keys "
            "must have the same length."
        )

    selected_lookup = {
        key: index
        for index, key in enumerate(selected_keys)
    }

    if len(selected_lookup) != len(selected_keys):
        raise ValueError(
            "selected_keys must be unique."
        )

    full_order = legacy_model_row_order(
        full_tickers,
        full_dates,
    )

    result = []

    for index in full_order:
        key = full_keys[index]

        if key in selected_lookup:
            result.append(
                selected_lookup[key]
            )

    if len(result) != len(selected_keys):
        raise ValueError(
            "not all selected_keys were found "
            "in the full dataset."
        )

    return np.asarray(
        result,
        dtype=np.int64,
    )