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
THRESHOLD_VALIDATION_TOLERANCE = 1.0e-10


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


def _topk_positions(
    values: np.ndarray,
    *,
    k: int,
    baseline_ranks: np.ndarray,
) -> np.ndarray:
    """Return a deterministic exact top-k set for one additive score vector."""

    scores = np.asarray(values, dtype=np.float64)
    ranks = np.asarray(baseline_ranks)
    n = int(scores.size)

    if scores.ndim != 1 or ranks.ndim != 1 or ranks.size != n:
        raise ValueError("top-k values and baseline ranks must be aligned vectors")
    if k <= 0 or k > n:
        raise ValueError("top-k cardinality is infeasible")
    if not np.isfinite(scores).all():
        raise ValueError("top-k values must be finite")

    if k == n:
        return np.arange(n, dtype=np.int64)

    partition = np.argpartition(scores, n - k)[n - k :]
    cutoff = float(np.min(scores[partition]))

    above = np.flatnonzero(scores > cutoff).astype(np.int64, copy=False)
    tied = np.flatnonzero(scores == cutoff).astype(np.int64, copy=False)
    needed = int(k - above.size)

    if needed < 0 or needed > tied.size:
        raise RuntimeError("deterministic top-k cutoff accounting failed")

    if needed:
        tie_order = np.argsort(ranks[tied], kind="stable")
        selected = np.concatenate([above, tied[tie_order[:needed]]])
    else:
        selected = above

    if selected.size != k:
        raise RuntimeError("deterministic top-k returned wrong cardinality")

    return selected.astype(np.int64, copy=False)


def _theta_candidates(widths: np.ndarray) -> np.ndarray:
    """Exact finite theta set implied by the budgeted-downside robust counterpart."""

    values = np.asarray(widths, dtype=np.float64)
    if values.ndim != 1 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("downside widths must be finite and non-negative")

    return np.unique(np.concatenate([np.array([0.0], dtype=np.float64), values]))


def _adjusted_scores(
    baseline: np.ndarray,
    widths: np.ndarray,
    theta: float,
) -> np.ndarray:
    return baseline - np.maximum(widths - float(theta), 0.0)


def _threshold_primary_optimum(
    baseline: np.ndarray,
    widths: np.ndarray,
    *,
    k: int,
    baseline_ranks: np.ndarray,
) -> tuple[np.ndarray, float, float, int]:
    """
    Solve the MM1 primary robust objective exactly by finite theta enumeration.

    Strong duality gives, for binary selection x and shared theta,

        J(x, theta)
          = sum_i x_i [b_i - max(d_i - theta, 0)] - B * theta.

    For fixed theta, exact-K maximization chooses the K largest adjusted scores.
    Between consecutive downside-width breakpoints d_i, the top-K score sum is
    the maximum of affine functions and is therefore convex; subtracting the
    linear B*theta term preserves convexity. Hence the maximum on every such
    interval is attained at an endpoint. It is therefore exact to enumerate
    theta in {0} union {d_i}.
    """

    b = np.asarray(baseline, dtype=np.float64)
    d = np.asarray(widths, dtype=np.float64)
    ranks = np.asarray(baseline_ranks)
    if b.ndim != 1 or d.ndim != 1 or b.size != d.size:
        raise ValueError("baseline and widths must be aligned vectors")

    budget = float(RHO_MM0 * k)
    thetas = _theta_candidates(d)

    best_total = -np.inf
    best_local: np.ndarray | None = None
    best_theta = 0.0

    for theta in thetas:
        adjusted = _adjusted_scores(b, d, float(theta))
        selected = _topk_positions(adjusted, k=k, baseline_ranks=ranks)
        total = float(np.sum(adjusted[selected], dtype=np.float64) - budget * theta)

        if total > best_total:
            best_total = total
            best_local = selected.copy()
            best_theta = float(theta)

    if best_local is None or not np.isfinite(best_total):
        raise RuntimeError("exact theta enumeration failed to produce an MM1 optimum")

    return best_local, best_total, best_theta, int(thetas.size)


def _best_alternative_total_excluding(
    baseline: np.ndarray,
    widths: np.ndarray,
    *,
    k: int,
    baseline_ranks: np.ndarray,
    excluded_local: np.ndarray,
) -> float:
    """
    Return the exact best robust total among all exact-K sets except one set.

    For each exact theta breakpoint, if the unrestricted additive top-K differs
    from the excluded set it is already the best allowed action. If it equals
    the excluded set, fixed cardinality implies the best distinct action is the
    single least-cost swap: remove the weakest selected adjusted score and add
    the strongest outside adjusted score.
    """

    b = np.asarray(baseline, dtype=np.float64)
    d = np.asarray(widths, dtype=np.float64)
    ranks = np.asarray(baseline_ranks)
    excluded = np.asarray(excluded_local, dtype=np.int64)
    n = int(b.size)

    if excluded.size != k:
        raise ValueError("excluded selection must contain exactly k rows")
    if k == n:
        return -np.inf

    excluded_mask = np.zeros(n, dtype=bool)
    excluded_mask[excluded] = True
    budget = float(RHO_MM0 * k)

    best_alternative = -np.inf
    for theta in _theta_candidates(d):
        adjusted = _adjusted_scores(b, d, float(theta))
        unrestricted = _topk_positions(adjusted, k=k, baseline_ranks=ranks)
        unrestricted_total = float(np.sum(adjusted[unrestricted], dtype=np.float64))

        unrestricted_mask = np.zeros(n, dtype=bool)
        unrestricted_mask[unrestricted] = True

        if not np.array_equal(unrestricted_mask, excluded_mask):
            additive_total = unrestricted_total
        else:
            remove_value = float(np.min(adjusted[excluded]))
            add_value = float(np.max(adjusted[~excluded_mask]))
            additive_total = unrestricted_total - remove_value + add_value

        robust_total = float(additive_total - budget * theta)
        if robust_total > best_alternative:
            best_alternative = robust_total

    return float(best_alternative)


# ---------------------------------------------------------------------------
# Residual exact MILP tie hierarchy.
#
# The pre-V5 scaling amendment changes only the primary computational route.
# If more than one action survives the already-frozen 1e-12 primary robust
# band, the original exact HiGHS hierarchy remains authoritative for levels
# 2-4 (champion overlap, nominal mean, lexicographic baseline rank).
# ---------------------------------------------------------------------------


def _base_problem(
    baseline: np.ndarray,
    widths: np.ndarray,
    *,
    k: int,
) -> tuple[csr_matrix, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    n = int(baseline.size)
    variable_count = 2 * n + 1
    theta_col = n
    p_offset = n + 1
    budget = float(RHO_MM0 * k)

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
    indices = np.asarray(selected_local, dtype=np.int64)
    if indices.size != k:
        raise ValueError("selection exclusion requires exactly k selected positions")
    return _single_row_constraint(
        variable_count,
        indices,
        np.ones(indices.size, dtype=np.float64),
        ub=float(k - 1),
    )


def _milp_primary_reference(
    baseline: np.ndarray,
    widths: np.ndarray,
    *,
    k: int,
) -> tuple[np.ndarray, float]:
    """Small-problem reference implementation of the original exact MILP primary solve."""

    (
        base_matrix,
        base_lb,
        base_ub,
        lower,
        upper,
        integrality,
        budget,
    ) = _base_problem(baseline, widths, k=k)

    n = int(baseline.size)
    theta_col = n
    p_offset = n + 1
    c = np.zeros(2 * n + 1, dtype=np.float64)
    c[:n] = -baseline
    c[theta_col] = budget
    c[p_offset:] = 1.0

    result = _solve(
        c=c,
        base_matrix=base_matrix,
        base_lb=base_lb,
        base_ub=base_ub,
        lower=lower,
        upper=upper,
        integrality=integrality,
    )
    selected = _selected_local_positions(result.x, n=n, k=k)
    gap = float(getattr(result, "mip_gap", np.nan))
    if np.isfinite(gap) and gap > 1.0e-9:
        raise RuntimeError("MM1 MILP reference reported a non-zero MIP gap")
    return selected, gap


def _milp_tie_hierarchy(
    state: MM0InformationState,
    *,
    eligible_indices: np.ndarray,
    champion: np.ndarray,
    baseline: np.ndarray,
    widths: np.ndarray,
    k: int,
    robust_star: float,
) -> tuple[np.ndarray, float]:
    """Apply the frozen tie hierarchy inside the exact primary robust band."""

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

    robust_target_total = float(k * (robust_star - ROBUST_VALUE_TOLERANCE))
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
        fixed: dict[int, int] = {}
        selected_count = 0
        rank_order = np.argsort(state.baseline_rank[eligible_indices])

        for local_position in rank_order:
            local_position = int(local_position)
            if selected_count == k:
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
        raise RuntimeError("MM1 tie hierarchy returned wrong cardinality")

    gaps = [
        float(getattr(overlap_result, "mip_gap", np.nan)),
        float(getattr(nominal_result, "mip_gap", np.nan)),
    ]
    finite_gaps = [gap for gap in gaps if np.isfinite(gap)]
    max_gap = max(finite_gaps, default=0.0)
    if max_gap > 1.0e-9:
        raise RuntimeError("MM1 tie hierarchy reported a non-zero MIP gap")

    return eligible_indices[final_local], float(max_gap)


def optimize_mm1(state: MM0InformationState) -> MM1OptimizationResult:
    """
    Solve the frozen MM1 max-min problem exactly without inspecting outcomes.

    The primary robust optimum uses the exact finite-threshold reformulation
    frozen in the pre-V5 solver amendment. The original exact HiGHS MILP is
    retained only for the residual tie hierarchy if another exact-K action
    survives the 1e-12 robust-value band.
    """

    k = int(state.rows * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("MM1 Top-K is empty for this cohort")

    eligible_indices = np.flatnonzero(state.phase2_guardrail_pass).astype(np.int64)
    if eligible_indices.size < k:
        raise ValueError("Phase-2 eligible pool cannot fill the frozen Top-K")

    champion = _phase2_champion_indices(state, k=k)
    champion_value = robust_value_for_selection(state, champion)

    baseline = np.asarray(
        state.baseline_point_score[eligible_indices],
        dtype=np.float64,
    )
    calibrated_p10 = np.asarray(
        state.calibrated_p10[eligible_indices],
        dtype=np.float64,
    )
    widths = baseline - np.minimum(baseline, calibrated_p10)
    eligible_ranks = np.asarray(state.baseline_rank[eligible_indices])

    primary_local, primary_total, _primary_theta, _threshold_count = (
        _threshold_primary_optimum(
            baseline,
            widths,
            k=k,
            baseline_ranks=eligible_ranks,
        )
    )
    primary_global = eligible_indices[primary_local]
    primary_value = robust_value_for_selection(state, primary_global)

    if abs(primary_total / k - primary_value.robust_value) > THRESHOLD_VALIDATION_TOLERANCE:
        raise RuntimeError(
            "exact threshold objective disagrees with authoritative robust-value adapter"
        )

    solver_status = "optimal_exact_threshold_enumeration"
    solver_gap = 0.0

    if primary_value.robust_value <= champion_value.robust_value + ROBUST_VALUE_TOLERANCE:
        selected = champion
        selected_value = champion_value
        intervention = False
        solver_status = "optimal_exact_threshold_champion_fallback"
    else:
        best_alternative_total = _best_alternative_total_excluding(
            baseline,
            widths,
            k=k,
            baseline_ranks=eligible_ranks,
            excluded_local=primary_local,
        )
        robust_band_floor_total = float(
            k * (primary_value.robust_value - ROBUST_VALUE_TOLERANCE)
        )

        if best_alternative_total < robust_band_floor_total:
            selected = primary_global
            selected_value = primary_value
            intervention = True
            solver_status = "optimal_exact_threshold_unique_primary_band"
        else:
            selected, solver_gap = _milp_tie_hierarchy(
                state,
                eligible_indices=eligible_indices,
                champion=champion,
                baseline=baseline,
                widths=widths,
                k=k,
                robust_star=float(primary_value.robust_value),
            )
            selected_value = robust_value_for_selection(state, selected)
            if (
                selected_value.robust_value
                < primary_value.robust_value - 2.0 * ROBUST_VALUE_TOLERANCE
            ):
                raise RuntimeError("MM1 tie-break left the frozen robust-optimal band")
            intervention = True
            solver_status = "optimal_exact_threshold_plus_milp_tie_hierarchy"

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
        solver_status=solver_status,
        solver_mip_gap=float(solver_gap),
        scipy_version=str(scipy.__version__),
        numpy_version=str(np.__version__),
    )
