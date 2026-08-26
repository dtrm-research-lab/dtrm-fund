"""Deterministic value adapter for the Phase-3 MM0 experiment."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def _as_index_vector(selected_indices: Sequence[int], *, rows: int) -> np.ndarray:
    indices = np.asarray(selected_indices)

    if indices.ndim != 1:
        raise ValueError("selected_indices must be one-dimensional")

    if indices.size == 0:
        raise ValueError("selected_indices must not be empty")

    if not np.issubdtype(indices.dtype, np.integer):
        raise ValueError("selected_indices must contain integers")

    indices = indices.astype(np.int64, copy=False)

    if (indices < 0).any() or (indices >= rows).any():
        raise ValueError("selected_indices contain out-of-range values")

    if np.unique(indices).size != indices.size:
        raise ValueError("selected_indices must not contain duplicates")

    return indices


def selected_mean_value(
    selected_indices: Sequence[int],
    candidate_value_vector: Sequence[float],
) -> float:
    """
    Return V_H(a,u) or V_H_realized(a) as the arithmetic mean of selected rows.

    ``candidate_value_vector`` must already be expressed in frozen Phase-2
    ``target_model`` units. The adapter deliberately performs no raw-return
    conversion, probability weighting, clipping, re-ranking, or scenario
    generation.
    """

    values = np.asarray(candidate_value_vector, dtype=np.float64)

    if values.ndim != 1:
        raise ValueError("candidate_value_vector must be one-dimensional")

    if values.size == 0:
        raise ValueError("candidate_value_vector must not be empty")

    if not np.isfinite(values).all():
        raise ValueError("candidate_value_vector must contain only finite values")

    indices = _as_index_vector(selected_indices, rows=values.size)

    return float(np.mean(values[indices]))


def incremental_value(
    challenger_indices: Sequence[int],
    champion_indices: Sequence[int],
    candidate_value_vector: Sequence[float],
) -> float:
    """
    Return DeltaV_H(a,u) using one common candidate-level value vector.

    The same ``candidate_value_vector`` is passed to both actions, enforcing
    the Binding-C same-world comparison by construction.
    """

    challenger = np.asarray(challenger_indices)
    champion = np.asarray(champion_indices)

    if challenger.ndim != 1 or champion.ndim != 1:
        raise ValueError("challenger_indices and champion_indices must be one-dimensional")

    if challenger.size != champion.size:
        raise ValueError("challenger and champion must have the same Top-K cardinality")

    challenger_value = selected_mean_value(challenger, candidate_value_vector)
    champion_value = selected_mean_value(champion, candidate_value_vector)

    return float(challenger_value - champion_value)
