"""Exact robust-value adapter for the Phase-3 MM1 experiment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from dtrm.phase3_mm0_action import TOPK_FRACTION
from dtrm.phase3_mm0_state import MM0InformationState


RHO_MM0 = 0.4378501384944031


@dataclass(frozen=True)
class MM1RobustValue:
    """Exact worst-case value diagnostics for one admissible MM1 action."""

    robust_value: float
    nominal_mean: float
    adversarial_penalty_mean: float
    stress_budget: float
    fully_stressed_rows: int
    fractional_stress: float


def _as_admissible_selection(
    state: MM0InformationState,
    selected_indices: Sequence[int],
) -> np.ndarray:
    indices = np.asarray(selected_indices)

    if indices.ndim != 1:
        raise ValueError("selected_indices must be one-dimensional")

    if not np.issubdtype(indices.dtype, np.integer):
        raise ValueError("selected_indices must contain integers")

    indices = indices.astype(np.int64, copy=False)

    expected_k = int(state.rows * TOPK_FRACTION)
    if expected_k <= 0:
        raise ValueError("MM1 Top-K is empty for this cohort")

    if indices.size != expected_k:
        raise ValueError("MM1 selection must contain exactly the frozen Top-K size")

    if (indices < 0).any() or (indices >= state.rows).any():
        raise ValueError("selected_indices contain out-of-range values")

    if np.unique(indices).size != indices.size:
        raise ValueError("selected_indices must not contain duplicates")

    if not np.all(state.phase2_guardrail_pass[indices]):
        raise ValueError("MM1 selection may contain only Phase-2-eligible candidates")

    return indices


def _budgeted_downside_penalty(
    downside_widths: np.ndarray,
    *,
    stress_budget: float,
) -> tuple[float, int, float]:
    """Return the exact fractional-knapsack downside penalty."""

    widths = np.asarray(downside_widths, dtype=np.float64)

    if widths.ndim != 1:
        raise ValueError("downside_widths must be one-dimensional")

    if not np.isfinite(widths).all():
        raise ValueError("downside_widths must contain only finite values")

    if (widths < 0).any():
        raise ValueError("downside_widths must be non-negative")

    if not np.isfinite(stress_budget) or stress_budget < 0:
        raise ValueError("stress_budget must be finite and non-negative")

    if widths.size == 0 or stress_budget == 0:
        return 0.0, 0, 0.0

    budget = min(float(stress_budget), float(widths.size))
    fully_stressed = min(int(np.floor(budget)), int(widths.size))
    fractional = float(budget - fully_stressed)

    ordered = np.sort(widths)[::-1]
    penalty = float(np.sum(ordered[:fully_stressed], dtype=np.float64))

    if fully_stressed < widths.size and fractional > 0.0:
        penalty += fractional * float(ordered[fully_stressed])

    return penalty, fully_stressed, fractional


def robust_value_for_selection(
    state: MM0InformationState,
    selected_indices: Sequence[int],
) -> MM1RobustValue:
    """
    Compute the exact MM1 worst-case value W_H(S) for one admissible action.

    MM1 uses the frozen budgeted-downside uncertainty family

        y_i(z) = b_i - z_i d_i,
        0 <= z_i <= 1,
        sum_i z_i <= rho * K,

    with ``rho = 0.4378501384944031``. For a fixed selected set the inner
    adversary is a fractional-knapsack problem: it allocates stress first to
    selected rows with the largest downside widths ``d_i``.
    """

    indices = _as_admissible_selection(state, selected_indices)
    k = int(indices.size)

    baseline = np.asarray(state.baseline_point_score[indices], dtype=np.float64)
    calibrated_p10 = np.asarray(state.calibrated_p10[indices], dtype=np.float64)

    downside_floor = np.minimum(baseline, calibrated_p10)
    downside_widths = baseline - downside_floor

    stress_budget = float(RHO_MM0 * k)
    penalty_total, fully_stressed, fractional = _budgeted_downside_penalty(
        downside_widths,
        stress_budget=stress_budget,
    )

    nominal_mean = float(np.mean(baseline))
    penalty_mean = float(penalty_total / k)
    robust_value = float(nominal_mean - penalty_mean)

    return MM1RobustValue(
        robust_value=robust_value,
        nominal_mean=nominal_mean,
        adversarial_penalty_mean=penalty_mean,
        stress_budget=stress_budget,
        fully_stressed_rows=fully_stressed,
        fractional_stress=fractional,
    )
