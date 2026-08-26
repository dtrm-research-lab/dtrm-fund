"""Exact deterministic outer optimizer for the Phase-3 MM1 experiment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import scipy
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, csr_matrix

from dtrm.phase3_mm0_action import TOPK_FRACTION
from dtrm.phase3_mm0_state import MM0InformationState
from dtrm.phase3_mm1_robust_value import RHO_MM0, robust_value_for_selection


ROBUST_VALUE_TOLERANCE = 1.0e-12


@dataclass(frozen=True)
class MM1OptimizationResult:
    """Frozen ex-ante output of the exact MM1 robust optimizer."""

    selected_indices: np.ndarray
    champion_indices: np.ndarray
    k: int
    eligible_rows: int
    robust_value_selected: float
    robust_value_champion: float
    robust_lift: float
    nominal_mean_selected: float
    nominal_mean_champion: float
    overlap_with_champion: int
    intervention: bool
    solver_status: str
    solver_mip_gap: float
    scipy_version: str
    numpy_version: str


def _readonly_indices(values: Sequence[int]) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64).copy()
    array.setflags(write=False)
    return array


def _phase2_champion_indices(state: MM0InformationState, *, k: int) -> np.ndarray:
    order = np.argsort(state.baseline_rank)
    eligible_order = order[state.phase2_guardrail_pass[order]]
    if eligible_order.size < k:
        raise ValueError("Phase-2 eligible pool cannot fill the frozen Top-K")
    return eligible_order[:k].astype(np.int64, copy=False)


def _base_problem(
    baseline: np.ndarray,
    widths: np.ndarray,
    *,
    k: int,
) -> tuple[csr_matrix, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Build the exact robust-counterpart variables, bounds, and base constraints."""

    n = int(baseline.size)
    variable_count = 2 * n + 1
    theta_col = n
    p_offset = n + 1
    budget = float(RHO_MM0 * k)

    # Row 0: exact cardinality. Rows 1..n: theta + p_i - d_i*x_i >= 0.
    cardinality_rows = np.zeros(n, dtype=np.int64)
    cardinality_cols = np.arange(n, dtype=np.int64)
    cardinality_data = np.ones(n, dtype=np.float64)

    candidate_rows = np.repeat(np.arange(1, n + 1, dtype=np.int64), 3)
    candidate_cols = np.empty(3 * n, dtype=np.int64)
    candidate_cols[0::3] = np.arange(n, dtype=np.int64)
    candidate_cols[1::3] = theta_col
    candidate_cols[2::3] = p_offset + np.arange(n, dtype=np.int64)
    candidate_data = np.empty(3 * n, dtype=np.float64)
    candidate_data[0::3] = -widths
    candidate_data[1::3] = 1.0
    candidate_data[2::3] = 1.0

    rows = np.concatenate([cardinality_rows, candidate_rows])
    cols = np.concatenate([cardinality_cols, candidate_cols])
    data = np.concatenate([cardinality_data, candidate_data])
    matrix = coo_matrix(
        (data, (rows, cols)),
        shape=(n + 1, variable_count),
        dtype=np.float64,
    ).tocsr()

    constraint_lb = np.concatenate([[float(k)], np.zeros(n, dtype=np.float64)])
    constraint_ub = np.concatenate([[float(k)], np.full(n, np.inf, dtype=np.float64)])

    lower = np.zeros(variable_count, dtype=np.float64)
    upper = np.full(variable_count, np.inf, dtype=np.float64)
    upper[:n] = 1.0
    max_width = float(np.max(widths)) if n else 0.0
    upper[theta_col] = max_width
    upper[p_offset:] = widths

    integrality = np.zeros(variable_count, dtype=np.int8)
    integrality[:n] = 1

    primary_c = np.zeros(variable_count, dtype=np.float64)
    primary_c[:n] = -baseline
    primary_c[theta_col] = budget
    primary_c[p_offset:] = 1.0

    return matrix, constraint_lb, constraint_ub, lower, upper, integrality, budget


def _single_row_constraint(
    variable_count: int,
    indices: np.ndarray,
    values: np.ndarray,
    *,
    lb: float = -np.inf,
    ub: float = np.inf,
) -> LinearConstraint:
    row = csr_matrix(
        (values.astype(np.float64), (np.zeros(indices.size, dtype=np.int64), indices)),
        shape=(1, variable_count),
        dtype=np.float64,
    )
    return LinearConstraint(row, lb=np.array([lb]), ub=np.array([ub]))


def _solve(
    *,
    c: np.ndarray,
    base_matrix: csr_matrix,
    base_lb: np.ndarray,
    base_ub: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    integrality: np.ndarray,
    extra_constraints: Sequence[LinearConstraint] = (),
    fixed_x: Mapping[int, int] | None = None,
    require_optimal: bool = True,
):
    lb = lower.copy()
    ub = upper.copy()

    if fixed_x:
        for position, value in fixed_x.items():
            if value not in (0, 1):
                raise ValueError("fixed binary values must be 0 or 1")
            lb[position] = float(value)
            ub[position] = float(value)

    constraints = [LinearConstraint(base_matrix, lb=base_lb, ub=base_ub)]
    constraints.extend(extra_constraints)

    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=constraints,
        options={
            "presolve": True,
            "mip_rel_gap": 0.0,
        },
    )

    if require_optimal and (not bool(result.success) or int(result.status) != 0):
        raise RuntimeError(f"MM1 MILP did not reach an optimal solution: {result.message}")

    return result


def _selected_local_positions(solution: np.ndarray, *, n: int, k: int) -> np.ndarray:
    selected = np.flatnonzero(np.asarray(solution[:n], dtype=np.float64) >= 0.5)
    if selected.size != k:
        raise RuntimeError("MM1 MILP returned a non-integral or wrong-cardinality selection")
    return selected.astype(np.int64, copy=False)


def _selection_exclusion_constraint(
    variable_count: int,
    selected_local: np.ndarray,
    *,
    k: int,
) -> LinearConstraint:
    """Exclude exactly one cardinality-k binary selection with a no-good cut."""

    indices = np.asarray(selected_local, dtype=np.int64)
    if indices.size != k:
        raise ValueError("selection exclusion requires exactly k selected positions")
    return _single_row_constraint(
        variable_count,
        indices,
        np.ones(indices.size, dtype=np.float64),
        ub=float(k - 1),
    )


def optimize_mm1(state: MM0InformationState) -> MM1OptimizationResult:
    """
    Solve the preregistered MM1 max-min problem exactly with a MILP robust counterpart.

    Only rows already passing the frozen Phase-2 guardrail enter the decision
    variables. Realized outcomes are not accepted by this interface.
    """

    k = int(state.rows * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("MM1 Top-K is empty for this cohort")

    eligible_indices = np.flatnonzero(state.phase2_guardrail_pass).astype(np.int64)
    if eligible_indices.size < k:
        raise ValueError("Phase-2 eligible pool cannot fill the frozen Top-K")

    champion = _phase2_champion_indices(state, k=k)
    champion_value = robust_value_for_selection(state, champion)

    baseline = np.asarray(state.baseline_point_score[eligible_indices], dtype=np.float64)
    calibrated_p10 = np.asarray(state.calibrated_p10[eligible_indices], dtype=np.float64)
    widths = baseline - np.minimum(baseline, calibrated_p10)

    (
        base_matrix,
        base_lb,
        base_ub,
        lower,
        upper,
        integrality,
        budget,
    ) = _base_problem(baseline, widths, k=k)

    n = int(eligible_indices.size)
    variable_count = int(2 * n + 1)
    theta_col = n
    p_offset = n + 1

    # Primary exact robust optimum.
    primary_c = np.zeros(variable_count, dtype=np.float64)
    primary_c[:n] = -baseline
    primary_c[theta_col] = budget
    primary_c[p_offset:] = 1.0
    primary = _solve(
        c=primary_c,
        base_matrix=base_matrix,
        base_lb=base_lb,
        base_ub=base_ub,
        lower=lower,
        upper=upper,
        integrality=integrality,
    )

    primary_local = _selected_local_positions(primary.x, n=n, k=k)
    primary_global = eligible_indices[primary_local]
    primary_value = robust_value_for_selection(state, primary_global)

    mip_gap = float(getattr(primary, "mip_gap", np.nan))
    if np.isfinite(mip_gap) and mip_gap > 1.0e-9:
        raise RuntimeError("MM1 MILP reported a non-zero MIP gap")

    # Frozen fallback: Phase 2 remains the action unless robust lift is strict.
    if primary_value.robust_value <= champion_value.robust_value + ROBUST_VALUE_TOLERANCE:
        selected = champion
        selected_value = champion_value
        intervention = False
    else:
        robust_target_total = float(k * (primary_value.robust_value - ROBUST_VALUE_TOLERANCE))
        robust_indices = np.concatenate(
            [
                np.arange(n, dtype=np.int64),
                np.array([theta_col], dtype=np.int64),
                p_offset + np.arange(n, dtype=np.int64),
            ]
        )
        robust_coefficients = np.concatenate(
            [
                baseline,
                np.array([-budget], dtype=np.float64),
                -np.ones(n, dtype=np.float64),
            ]
        )
        robust_band = _single_row_constraint(
            variable_count,
            robust_indices,
            robust_coefficients,
            lb=robust_target_total,
        )

        champion_members = np.isin(eligible_indices, champion).astype(np.float64)

        # Tie level 2: maximize overlap with the frozen Phase-2 champion.
        overlap_c = np.zeros(variable_count, dtype=np.float64)
        overlap_c[:n] = -champion_members
        overlap_result = _solve(
            c=overlap_c,
            base_matrix=base_matrix,
            base_lb=base_lb,
            base_ub=base_ub,
            lower=lower,
            upper=upper,
            integrality=integrality,
            extra_constraints=(robust_band,),
        )
        overlap_local = _selected_local_positions(overlap_result.x, n=n, k=k)
        overlap_star = int(np.sum(champion_members[overlap_local]))
        overlap_constraint = _single_row_constraint(
            variable_count,
            np.arange(n, dtype=np.int64),
            champion_members,
            lb=float(overlap_star),
            ub=float(overlap_star),
        )

        # Tie level 3: maximize nominal mean with robust band and overlap fixed.
        nominal_c = np.zeros(variable_count, dtype=np.float64)
        nominal_c[:n] = -baseline
        nominal_result = _solve(
            c=nominal_c,
            base_matrix=base_matrix,
            base_lb=base_lb,
            base_ub=base_ub,
            lower=lower,
            upper=upper,
            integrality=integrality,
            extra_constraints=(robust_band, overlap_constraint),
        )
        nominal_local = _selected_local_positions(nominal_result.x, n=n, k=k)
        nominal_star_total = float(np.sum(baseline[nominal_local], dtype=np.float64))
        nominal_band = _single_row_constraint(
            variable_count,
            np.arange(n, dtype=np.int64),
            baseline,
            lb=float(nominal_star_total - k * ROBUST_VALUE_TOLERANCE),
        )

        # Tie level 4 remains exactly the preregistered lexicographic rule. Before
        # starting the potentially long greedy feasibility scan, prove whether the
        # level-1/2/3 winner is already unique inside the frozen tolerance bands.
        # The no-good cut excludes only nominal_local because cardinality is fixed.
        # If that cut makes the problem infeasible, no lexicographic comparison is
        # needed and nominal_local is necessarily the exact level-4 winner.
        zero_c = np.zeros(variable_count, dtype=np.float64)
        tie_constraints = (robust_band, overlap_constraint, nominal_band)
        exclusion = _selection_exclusion_constraint(
            variable_count,
            nominal_local,
            k=k,
        )
        alternative = _solve(
            c=zero_c,
            base_matrix=base_matrix,
            base_lb=base_lb,
            base_ub=base_ub,
            lower=lower,
            upper=upper,
            integrality=integrality,
            extra_constraints=tie_constraints + (exclusion,),
            require_optimal=False,
        )

        if not bool(alternative.success) or int(alternative.status) != 0:
            if int(alternative.status) != 2:
                raise RuntimeError(
                    "MM1 uniqueness check ended without an optimal or infeasible status: "
                    f"{alternative.message}"
                )
            final_local = nominal_local
        else:
            # Multiple selections remain in the frozen robust/overlap/nominal bands.
            # Fall back to the original exact greedy lexicographic feasibility scan.
            fixed: dict[int, int] = {}
            selected_count = 0
            rank_order = np.argsort(state.baseline_rank[eligible_indices])

            for local_position in rank_order:
                local_position = int(local_position)
                remaining_needed = k - selected_count
                if remaining_needed == 0:
                    fixed[local_position] = 0
                    continue

                trial_fixed = dict(fixed)
                trial_fixed[local_position] = 1
                trial = _solve(
                    c=zero_c,
                    base_matrix=base_matrix,
                    base_lb=base_lb,
                    base_ub=base_ub,
                    lower=lower,
                    upper=upper,
                    integrality=integrality,
                    extra_constraints=tie_constraints,
                    fixed_x=trial_fixed,
                    require_optimal=False,
                )

                if bool(trial.success) and int(trial.status) == 0:
                    fixed[local_position] = 1
                    selected_count += 1
                else:
                    fixed[local_position] = 0

            if selected_count != k:
                raise RuntimeError("MM1 lexicographic tie-break failed to construct a full Top-K")

            final_local = np.array(
                sorted(position for position, value in fixed.items() if value == 1),
                dtype=np.int64,
            )
            if final_local.size != k:
                raise RuntimeError("MM1 lexicographic tie-break returned wrong cardinality")

        selected = eligible_indices[final_local]
        selected_value = robust_value_for_selection(state, selected)
        if selected_value.robust_value < primary_value.robust_value - 2.0 * ROBUST_VALUE_TOLERANCE:
            raise RuntimeError("MM1 tie-break left the frozen robust-optimal band")
        intervention = True

    if not np.all(state.phase2_guardrail_pass[selected]):
        raise RuntimeError("MM1 optimizer selected a Phase-2-vetoed candidate")
    if np.unique(selected).size != k:
        raise RuntimeError("MM1 optimizer returned duplicate or wrong-cardinality rows")

    selected_set = set(int(i) for i in selected)
    overlap = int(sum(int(i) in selected_set for i in champion))

    return MM1OptimizationResult(
        selected_indices=_readonly_indices(selected),
        champion_indices=_readonly_indices(champion),
        k=k,
        eligible_rows=int(eligible_indices.size),
        robust_value_selected=float(selected_value.robust_value),
        robust_value_champion=float(champion_value.robust_value),
        robust_lift=float(selected_value.robust_value - champion_value.robust_value),
        nominal_mean_selected=float(selected_value.nominal_mean),
        nominal_mean_champion=float(champion_value.nominal_mean),
        overlap_with_champion=overlap,
        intervention=bool(intervention),
        solver_status="optimal",
        solver_mip_gap=mip_gap,
        scipy_version=str(scipy.__version__),
        numpy_version=str(np.__version__),
    )
