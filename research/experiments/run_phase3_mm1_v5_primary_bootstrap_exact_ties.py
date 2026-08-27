"""Exact V5 news_id bootstrap with exchangeable-copy tie hierarchy.

This runner is the operational implementation of the frozen bootstrap solver
and tie amendments. It preserves the preregistered resampling law and frozen
MM1 policy. Bootstrap copies of one original V5 row are represented as bounded
integer quantities; when the primary robust band is non-unique, the original
MM1 tie hierarchy is solved exactly over the union of finite theta witnesses.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

import run_phase3_mm1_v5_primary_bootstrap as base
from dtrm.phase3_mm1_optimizer import (
    ROBUST_VALUE_TOLERANCE,
    _adjusted_scores,
    _theta_candidates,
    _topk_positions,
)
from dtrm.phase3_mm1_robust_value import RHO_MM0, robust_value_for_selection


REPO_ROOT = base.REPO_ROOT
LOCAL_DATA = base.LOCAL_DATA
REPORTS = base.REPORTS
DECISION_MANIFEST_PATH = base.DECISION_MANIFEST_PATH
POINT_RESULT_PATH = base.POINT_RESULT_PATH
SIGNALS_PATH = base.SIGNALS_PATH
TARGET_PATH = base.TARGET_PATH
BOOTSTRAP_AMENDMENT_PATH = base.BOOTSTRAP_AMENDMENT_PATH
TIE_AMENDMENT_PATH = (
    REPO_ROOT
    / "research"
    / "contracts"
    / "DTRM_PHASE3_MM1_V5_BOOTSTRAP_TIE_AMENDMENT.yaml"
)
OUTPUT_SUMMARY = base.OUTPUT_SUMMARY
OUTPUT_DISTRIBUTIONS = base.OUTPUT_DISTRIBUTIONS

REPLICATES = 10_000
SEED = 20260827
TOPK_FRACTION = 0.10
CONFIDENCE_LEVEL = 0.95
BOUNDARY_NUMERICAL_PADDING = 1.0e-10
SOLVER_GAP_TOLERANCE = 1.0e-9


@dataclass(frozen=True)
class ThetaWitness:
    theta: float
    boundary_rows: np.ndarray
    capacities: np.ndarray
    champion_capacities: np.ndarray
    adjusted: np.ndarray
    baseline: np.ndarray
    ranks: np.ndarray
    remaining_k: int
    adjusted_required: float
    fixed_quantity: np.ndarray
    fixed_overlap: int
    fixed_nominal_total: float
    max_overlap: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_committed_bytes(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    relative = str(path.relative_to(REPO_ROOT))
    try:
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"],
            cwd=REPO_ROOT,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Required bootstrap amendment is not committed: {relative}") from exc
    if committed != path.read_bytes():
        raise RuntimeError(f"Local amendment differs from committed Git bytes: {relative}")


def _solve_boundary(
    *,
    capacities: np.ndarray,
    champion_capacities: np.ndarray,
    adjusted: np.ndarray,
    baseline: np.ndarray,
    remaining_k: int,
    adjusted_required: float,
    objective: str,
    overlap_required: int | None = None,
    nominal_required: float | None = None,
    quantity_index: int | None = None,
    fixed_quantities: dict[int, int] | None = None,
):
    cap = np.asarray(capacities, dtype=np.int64)
    champ = np.asarray(champion_capacities, dtype=np.int64)
    a = np.asarray(adjusted, dtype=np.float64)
    b = np.asarray(baseline, dtype=np.float64)
    m = int(cap.size)

    if not (champ.size == a.size == b.size == m):
        raise ValueError("Residual tie arrays must be aligned")
    if (cap < 0).any() or (champ < 0).any() or (champ > cap).any():
        raise ValueError("Invalid residual capacities")
    if remaining_k < 0 or remaining_k > int(np.sum(cap)):
        return None

    # q_c are units overlapping the Phase-2 champion; q_n are all other units.
    variable_count = 2 * m
    upper = np.concatenate([champ, cap - champ]).astype(np.float64)
    lower = np.zeros(variable_count, dtype=np.float64)
    integrality = np.ones(variable_count, dtype=np.int8)

    rows: list[np.ndarray] = []
    lbs: list[float] = []
    ubs: list[float] = []

    cardinality = np.ones(variable_count, dtype=np.float64)
    rows.append(cardinality)
    lbs.append(float(remaining_k))
    ubs.append(float(remaining_k))

    adjusted_row = np.concatenate([a, a])
    rows.append(adjusted_row)
    lbs.append(float(adjusted_required))
    ubs.append(np.inf)

    if overlap_required is not None:
        overlap_row = np.concatenate([np.ones(m), np.zeros(m)])
        rows.append(overlap_row)
        lbs.append(float(overlap_required))
        ubs.append(float(overlap_required))

    if nominal_required is not None:
        nominal_row = np.concatenate([b, b])
        rows.append(nominal_row)
        lbs.append(float(nominal_required))
        ubs.append(np.inf)

    if fixed_quantities:
        for index, value in sorted(fixed_quantities.items()):
            if index < 0 or index >= m:
                raise ValueError("Fixed residual quantity index out of range")
            row = np.zeros(variable_count, dtype=np.float64)
            row[index] = 1.0
            row[m + index] = 1.0
            rows.append(row)
            lbs.append(float(value))
            ubs.append(float(value))

    matrix = np.vstack(rows)
    constraints = LinearConstraint(
        matrix,
        lb=np.asarray(lbs, dtype=np.float64),
        ub=np.asarray(ubs, dtype=np.float64),
    )

    c = np.zeros(variable_count, dtype=np.float64)
    if objective == "overlap":
        c[:m] = -1.0
    elif objective == "nominal":
        c[:m] = -b
        c[m:] = -b
    elif objective == "quantity":
        if quantity_index is None:
            raise ValueError("quantity objective requires quantity_index")
        c[quantity_index] = -1.0
        c[m + quantity_index] = -1.0
    elif objective != "feasibility":
        raise ValueError(f"Unknown residual objective: {objective}")

    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lower, upper),
        constraints=constraints,
        options={"presolve": True, "mip_rel_gap": 0.0},
    )

    if not bool(result.success) or int(result.status) != 0:
        if int(result.status) == 2:
            return None
        raise RuntimeError(f"Residual exchangeable MILP failed: {result.message}")

    gap = float(getattr(result, "mip_gap", np.nan))
    if np.isfinite(gap) and gap > SOLVER_GAP_TOLERANCE:
        raise RuntimeError("Residual exchangeable MILP returned non-zero gap")

    x = np.asarray(result.x, dtype=np.float64)
    qc = np.rint(x[:m]).astype(np.int64)
    qn = np.rint(x[m:]).astype(np.int64)
    if np.max(np.abs(x[:m] - qc), initial=0.0) > 1.0e-7:
        raise RuntimeError("Residual champion quantities are not integral")
    if np.max(np.abs(x[m:] - qn), initial=0.0) > 1.0e-7:
        raise RuntimeError("Residual non-champion quantities are not integral")
    quantity = qc + qn

    return {
        "quantity": quantity,
        "champion_quantity": qc,
        "overlap": int(np.sum(qc)),
        "nominal_total": float(np.dot(b, quantity)),
        "adjusted_total": float(np.dot(a, quantity)),
    }


def _unique_row_data(
    frame: pd.DataFrame,
    *,
    state,
    expanded_idx: np.ndarray,
    eligible_indices: np.ndarray,
    champion: np.ndarray,
    baseline_expanded: np.ndarray,
    widths_expanded: np.ndarray,
    ranks_expanded: np.ndarray,
):
    original_ids = expanded_idx[eligible_indices]
    row_ids, first = np.unique(original_ids, return_index=True)

    capacities_all = np.bincount(original_ids, minlength=len(frame)).astype(np.int64)
    champion_all = np.bincount(
        expanded_idx[champion], minlength=len(frame)
    ).astype(np.int64)

    rank_min = np.full(len(frame), np.iinfo(np.int64).max, dtype=np.int64)
    np.minimum.at(rank_min, original_ids, ranks_expanded)

    return {
        "row_ids": row_ids.astype(np.int64, copy=False),
        "capacities": capacities_all[row_ids],
        "champion_capacities": champion_all[row_ids],
        "baseline": baseline_expanded[first],
        "widths": widths_expanded[first],
        "ranks": rank_min[row_ids],
    }


def _build_theta_witnesses(
    *,
    row_data: dict,
    baseline_expanded: np.ndarray,
    widths_expanded: np.ndarray,
    ranks_expanded: np.ndarray,
    k: int,
    primary_total: float,
) -> list[ThetaWitness]:
    row_ids = row_data["row_ids"]
    capacities = row_data["capacities"]
    champion_capacities = row_data["champion_capacities"]
    baseline = row_data["baseline"]
    widths = row_data["widths"]
    ranks = row_data["ranks"]

    robust_target_total = float(primary_total - k * ROBUST_VALUE_TOLERANCE)
    budget = float(RHO_MM0 * k)
    witnesses: list[ThetaWitness] = []

    for theta in _theta_candidates(widths_expanded):
        theta = float(theta)
        adjusted_expanded = _adjusted_scores(
            baseline_expanded, widths_expanded, theta
        )
        topk = _topk_positions(
            adjusted_expanded,
            k=k,
            baseline_ranks=ranks_expanded,
        )
        max_adjusted_total = float(
            np.sum(adjusted_expanded[topk], dtype=np.float64)
        )
        required_adjusted_total = float(robust_target_total + budget * theta)
        slack = float(max_adjusted_total - required_adjusted_total)
        if slack < -BOUNDARY_NUMERICAL_PADDING:
            continue
        slack = max(slack, 0.0)
        cutoff = float(np.min(adjusted_expanded[topk]))

        adjusted = _adjusted_scores(baseline, widths, theta)
        high = adjusted > cutoff + slack + BOUNDARY_NUMERICAL_PADDING
        low = adjusted < cutoff - slack - BOUNDARY_NUMERICAL_PADDING
        boundary = ~(high | low)

        fixed_quantity = np.zeros(row_ids.size, dtype=np.int64)
        fixed_quantity[high] = capacities[high]
        fixed_count = int(np.sum(fixed_quantity))
        remaining_k = int(k - fixed_count)
        if remaining_k < 0:
            raise RuntimeError("Boundary reduction forced more than K units")

        fixed_adjusted = float(np.dot(adjusted, fixed_quantity))
        adjusted_required = float(required_adjusted_total - fixed_adjusted)
        fixed_overlap = int(
            np.sum(np.minimum(fixed_quantity, champion_capacities))
        )
        fixed_nominal = float(np.dot(baseline, fixed_quantity))

        boundary_rows = np.flatnonzero(boundary).astype(np.int64, copy=False)
        if remaining_k > int(np.sum(capacities[boundary_rows])):
            raise RuntimeError("Boundary reduction removed a potentially feasible unit")

        if boundary_rows.size == 0:
            if remaining_k != 0 or fixed_adjusted + BOUNDARY_NUMERICAL_PADDING < required_adjusted_total:
                continue
            max_overlap = fixed_overlap
        else:
            overlap = _solve_boundary(
                capacities=capacities[boundary_rows],
                champion_capacities=champion_capacities[boundary_rows],
                adjusted=adjusted[boundary_rows],
                baseline=baseline[boundary_rows],
                remaining_k=remaining_k,
                adjusted_required=adjusted_required,
                objective="overlap",
            )
            if overlap is None:
                continue
            max_overlap = int(fixed_overlap + overlap["overlap"])

        witnesses.append(
            ThetaWitness(
                theta=theta,
                boundary_rows=boundary_rows,
                capacities=capacities,
                champion_capacities=champion_capacities,
                adjusted=adjusted,
                baseline=baseline,
                ranks=ranks,
                remaining_k=remaining_k,
                adjusted_required=adjusted_required,
                fixed_quantity=fixed_quantity,
                fixed_overlap=fixed_overlap,
                fixed_nominal_total=fixed_nominal,
                max_overlap=max_overlap,
            )
        )

    if not witnesses:
        raise RuntimeError("No theta witness survives the frozen robust band")
    return witnesses


def _nominal_solution(witness: ThetaWitness, *, overlap_star: int):
    rows = witness.boundary_rows
    needed_overlap = int(overlap_star - witness.fixed_overlap)
    if needed_overlap < 0:
        return None
    if rows.size == 0:
        if witness.remaining_k == 0 and needed_overlap == 0:
            return {
                "quantity": np.empty(0, dtype=np.int64),
                "nominal_total": 0.0,
            }
        return None

    return _solve_boundary(
        capacities=witness.capacities[rows],
        champion_capacities=witness.champion_capacities[rows],
        adjusted=witness.adjusted[rows],
        baseline=witness.baseline[rows],
        remaining_k=witness.remaining_k,
        adjusted_required=witness.adjusted_required,
        overlap_required=needed_overlap,
        objective="nominal",
    )


def _lex_solution(
    witness: ThetaWitness,
    *,
    overlap_star: int,
    nominal_star_total: float,
) -> np.ndarray | None:
    rows = witness.boundary_rows
    needed_overlap = int(overlap_star - witness.fixed_overlap)
    nominal_required = float(
        nominal_star_total
        - witness.fixed_nominal_total
        - ROBUST_VALUE_TOLERANCE * int(np.sum(witness.fixed_quantity) + witness.remaining_k)
    )

    if rows.size == 0:
        if witness.remaining_k != 0 or needed_overlap != 0:
            return None
        quantity = witness.fixed_quantity.copy()
        if float(np.dot(witness.baseline, quantity)) + BOUNDARY_NUMERICAL_PADDING < nominal_star_total - ROBUST_VALUE_TOLERANCE * int(np.sum(quantity)):
            return None
        return quantity

    fixed: dict[int, int] = {}
    local_order = np.argsort(witness.ranks[rows], kind="stable")
    last_result = None

    for local_index in local_order:
        local_index = int(local_index)
        trial = _solve_boundary(
            capacities=witness.capacities[rows],
            champion_capacities=witness.champion_capacities[rows],
            adjusted=witness.adjusted[rows],
            baseline=witness.baseline[rows],
            remaining_k=witness.remaining_k,
            adjusted_required=witness.adjusted_required,
            overlap_required=needed_overlap,
            nominal_required=nominal_required,
            objective="quantity",
            quantity_index=local_index,
            fixed_quantities=fixed,
        )
        if trial is None:
            return None
        value = int(trial["quantity"][local_index])
        fixed[local_index] = value
        last_result = trial

    final = _solve_boundary(
        capacities=witness.capacities[rows],
        champion_capacities=witness.champion_capacities[rows],
        adjusted=witness.adjusted[rows],
        baseline=witness.baseline[rows],
        remaining_k=witness.remaining_k,
        adjusted_required=witness.adjusted_required,
        overlap_required=needed_overlap,
        nominal_required=nominal_required,
        objective="feasibility",
        fixed_quantities=fixed,
    )
    if final is None:
        return None

    quantity = witness.fixed_quantity.copy()
    quantity[rows] = final["quantity"]
    return quantity


def _lex_tuple(quantity: np.ndarray, ranks: np.ndarray) -> tuple[int, ...]:
    order = np.argsort(ranks, kind="stable")
    return tuple(
        int(rank)
        for index in order
        for rank in [ranks[index]] * int(quantity[index])
    )


def _selected_positions_from_quantity(
    *,
    eligible_indices: np.ndarray,
    eligible_original_ids: np.ndarray,
    row_ids: np.ndarray,
    quantity: np.ndarray,
) -> np.ndarray:
    selected: list[int] = []
    for row_id, count in zip(row_ids, quantity, strict=True):
        count = int(count)
        if count <= 0:
            continue
        positions = eligible_indices[eligible_original_ids == int(row_id)]
        if positions.size < count:
            raise RuntimeError("Quantity exceeds exchangeable expanded capacity")
        selected.extend(int(x) for x in positions[:count])
    return np.asarray(selected, dtype=np.int64)


def resolve_exact_tie_quantity(
    frame: pd.DataFrame,
    *,
    state,
    expanded_idx: np.ndarray,
    eligible_indices: np.ndarray,
    champion: np.ndarray,
    baseline_expanded: np.ndarray,
    widths_expanded: np.ndarray,
    ranks_expanded: np.ndarray,
    k: int,
    primary_total: float,
) -> tuple[np.ndarray, dict]:
    row_data = _unique_row_data(
        frame,
        state=state,
        expanded_idx=expanded_idx,
        eligible_indices=eligible_indices,
        champion=champion,
        baseline_expanded=baseline_expanded,
        widths_expanded=widths_expanded,
        ranks_expanded=ranks_expanded,
    )
    witnesses = _build_theta_witnesses(
        row_data=row_data,
        baseline_expanded=baseline_expanded,
        widths_expanded=widths_expanded,
        ranks_expanded=ranks_expanded,
        k=k,
        primary_total=primary_total,
    )

    overlap_star = max(w.max_overlap for w in witnesses)

    nominal_candidates: list[tuple[ThetaWitness, dict, float]] = []
    nominal_star_total = -np.inf
    for witness in witnesses:
        if witness.max_overlap != overlap_star:
            continue
        solution = _nominal_solution(witness, overlap_star=overlap_star)
        if solution is None:
            continue
        total = float(witness.fixed_nominal_total + solution["nominal_total"])
        nominal_candidates.append((witness, solution, total))
        nominal_star_total = max(nominal_star_total, total)

    if not np.isfinite(nominal_star_total):
        raise RuntimeError("Residual hierarchy could not reproduce maximum overlap")

    best_quantity = None
    best_witness = None
    best_lex = None
    for witness, _solution, nominal_total in nominal_candidates:
        if nominal_total < nominal_star_total - k * ROBUST_VALUE_TOLERANCE - BOUNDARY_NUMERICAL_PADDING:
            continue
        quantity = _lex_solution(
            witness,
            overlap_star=overlap_star,
            nominal_star_total=nominal_star_total,
        )
        if quantity is None:
            continue
        lex = _lex_tuple(quantity, witness.ranks)
        if best_lex is None or lex < best_lex:
            best_lex = lex
            best_quantity = quantity
            best_witness = witness

    if best_quantity is None or best_witness is None:
        raise RuntimeError("Residual hierarchy failed at lexicographic level")

    row_ids = row_data["row_ids"]
    full_quantity = np.zeros(len(frame), dtype=np.int64)
    full_quantity[row_ids] = best_quantity
    if int(np.sum(full_quantity)) != k:
        raise RuntimeError("Residual hierarchy returned wrong cardinality")

    eligible_original_ids = expanded_idx[eligible_indices]
    selected = _selected_positions_from_quantity(
        eligible_indices=eligible_indices,
        eligible_original_ids=eligible_original_ids,
        row_ids=row_ids,
        quantity=best_quantity,
    )
    robust = robust_value_for_selection(state, selected)
    primary_mean = float(primary_total / k)
    if robust.robust_value < primary_mean - ROBUST_VALUE_TOLERANCE - 1.0e-10:
        raise RuntimeError("Residual hierarchy returned action outside robust band")

    champion_quantity = np.bincount(
        expanded_idx[champion], minlength=len(frame)
    ).astype(np.int64)
    overlap = int(np.sum(np.minimum(full_quantity, champion_quantity)))
    if overlap != overlap_star:
        raise RuntimeError("Residual hierarchy overlap does not reproduce optimum")

    nominal_total = float(np.dot(row_data["baseline"], best_quantity))
    if nominal_total < nominal_star_total - k * ROBUST_VALUE_TOLERANCE - 1.0e-10:
        raise RuntimeError("Residual hierarchy nominal level does not reproduce optimum")

    return full_quantity, {
        "theta_witnesses": int(len(witnesses)),
        "overlap_star": int(overlap_star),
        "nominal_star_total": float(nominal_star_total),
        "selected_theta": float(best_witness.theta),
        "selected_boundary_rows": int(best_witness.boundary_rows.size),
    }


def evaluate_resampled_policy_exact(
    frame: pd.DataFrame,
    multiplicity: np.ndarray,
) -> dict[str, float | int] | None:
    state, expanded_idx = base._expanded_state(frame, multiplicity)
    n = int(state.rows)
    k = int(n * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("Bootstrap replicate Top-K is empty")

    rank_order = np.argsort(state.baseline_rank)
    eligible_order = rank_order[state.phase2_guardrail_pass[rank_order]]
    if eligible_order.size < k:
        return None
    champion = eligible_order[:k].astype(np.int64, copy=False)

    eligible_indices = np.flatnonzero(state.phase2_guardrail_pass).astype(np.int64)
    if eligible_indices.size < k:
        return None

    baseline = np.asarray(state.baseline_point_score[eligible_indices], dtype=np.float64)
    calibrated_p10 = np.asarray(state.calibrated_p10[eligible_indices], dtype=np.float64)
    widths = baseline - np.minimum(baseline, calibrated_p10)
    ranks = np.asarray(state.baseline_rank[eligible_indices], dtype=np.int64)

    selected_local, primary_total, _theta, _count = base._threshold_primary_optimum(
        baseline, widths, k=k, baseline_ranks=ranks
    )
    selected = eligible_indices[selected_local]

    selected_robust = robust_value_for_selection(state, selected)
    champion_robust = robust_value_for_selection(state, champion)
    primary_mean = float(primary_total / k)
    if not np.isclose(selected_robust.robust_value, primary_mean, rtol=0.0, atol=1.0e-10):
        raise RuntimeError("Primary threshold theorem does not reproduce robust value")

    champion_quantity = np.bincount(
        expanded_idx[champion], minlength=len(frame)
    ).astype(np.int64)

    if primary_mean <= champion_robust.robust_value + ROBUST_VALUE_TOLERANCE:
        selected_quantity = champion_quantity.copy()
        hierarchy = "champion_fallback"
    else:
        eligible_original_ids = expanded_idx[eligible_indices]
        selected_quantity_fast = base._quantity_vector(
            eligible_original_ids,
            selected_local,
            original_rows=len(frame),
        )
        alternative_total = base._best_distinct_quantity_robust_total(
            baseline,
            widths,
            k=k,
            baseline_ranks=ranks,
            eligible_original_ids=eligible_original_ids,
            excluded_quantity=selected_quantity_fast,
            original_rows=len(frame),
        )
        alternative_mean = float(alternative_total / k)

        if alternative_mean < primary_mean - ROBUST_VALUE_TOLERANCE:
            selected_quantity = selected_quantity_fast
            hierarchy = "unique_primary_band"
        else:
            selected_quantity, _diagnostics = resolve_exact_tie_quantity(
                frame,
                state=state,
                expanded_idx=expanded_idx,
                eligible_indices=eligible_indices,
                champion=champion,
                baseline_expanded=baseline,
                widths_expanded=widths,
                ranks_expanded=ranks,
                k=k,
                primary_total=primary_total,
            )
            hierarchy = "exact_exchangeable_tie_hierarchy"

    target = frame["target_model"].to_numpy(dtype=np.float64)
    phase2_value, phase2_hit = base._weighted_metrics(
        target, champion_quantity, k=k
    )
    mm1_value, mm1_hit = base._weighted_metrics(
        target, selected_quantity, k=k
    )

    return {
        "rows": n,
        "K_H": k,
        "phase2_value": phase2_value,
        "MM1_value": mm1_value,
        "delta_topk_mean_target_model_vs_phase2": float(mm1_value - phase2_value),
        "phase2_hit_rate": phase2_hit,
        "MM1_hit_rate": mm1_hit,
        "delta_topk_hit_rate": float(mm1_hit - phase2_hit),
        "hierarchy": hierarchy,
    }


def cluster_bootstrap_exact(
    frame: pd.DataFrame,
    *,
    rng: np.random.Generator,
    replicates: int = REPLICATES,
) -> tuple[np.ndarray, np.ndarray, int, dict[str, int]]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")

    cluster_codes, cluster_labels = pd.factorize(frame["news_id"], sort=False)
    n_clusters = int(len(cluster_labels))
    if n_clusters <= 0:
        raise ValueError("V5 bootstrap requires at least one news_id cluster")

    delta_mean = np.full(replicates, np.nan, dtype=np.float64)
    delta_hit = np.full(replicates, np.nan, dtype=np.float64)
    infeasible = 0
    hierarchy_counts: dict[str, int] = {}

    for replicate in range(replicates):
        multiplicity = base.resampled_row_multiplicity(
            cluster_codes,
            n_clusters=n_clusters,
            rng=rng,
        )
        result = evaluate_resampled_policy_exact(frame, multiplicity)
        if result is None:
            infeasible += 1
        else:
            delta_mean[replicate] = float(
                result["delta_topk_mean_target_model_vs_phase2"]
            )
            delta_hit[replicate] = float(result["delta_topk_hit_rate"])
            label = str(result["hierarchy"])
            hierarchy_counts[label] = hierarchy_counts.get(label, 0) + 1

        if replicates == REPLICATES and (replicate + 1) % 1000 == 0:
            print(f"bootstrap {replicate + 1}/{REPLICATES}", flush=True)

    return delta_mean, delta_hit, infeasible, hierarchy_counts


def main() -> None:
    base.require_outputs_absent()
    base.require_clean_tracked_worktree()
    require_committed_bytes(BOOTSTRAP_AMENDMENT_PATH)
    require_committed_bytes(TIE_AMENDMENT_PATH)

    decision_manifest = base.require_committed_json(
        DECISION_MANIFEST_PATH,
        expected_status="decision_frozen_pending_git_commit",
    )
    point_result = base.require_committed_json(
        POINT_RESULT_PATH,
        expected_status="realized_point_evaluation_complete_pending_commit",
    )
    if point_result["decision_manifest"]["sha256"] != sha256_file(DECISION_MANIFEST_PATH):
        raise RuntimeError("V5 point result is bound to a different decision manifest")
    if point_result["point_evaluation"]["classification"] != "PROMOTED_POINT":
        raise RuntimeError("V5 primary bootstrap expected frozen PROMOTED_POINT")

    frame = base.load_bootstrap_frame(decision_manifest, point_result)
    point = base.reproduce_frozen_point(frame, decision_manifest)
    expected_point = point_result["point_evaluation"]
    for key in (
        "phase2_value",
        "MM1_value",
        "delta_topk_mean_target_model_vs_phase2",
        "phase2_hit_rate",
        "MM1_hit_rate",
        "delta_topk_hit_rate",
    ):
        if not np.isclose(point[key], float(expected_point[key]), rtol=0.0, atol=1.0e-12):
            raise RuntimeError(f"Frozen V5 point result does not reproduce: {key}")

    print("DTRM PHASE 3 MM1 V5 PRIMARY NEWS_ID BOOTSTRAP")
    print("point result reproduction: PASS")
    print("exchangeable tie amendment: PASS")
    print("rows:", len(frame))
    print("news_id clusters:", frame["news_id"].nunique())
    print("replicates:", REPLICATES)
    print("seed:", SEED)

    delta_mean, delta_hit, infeasible, hierarchy_counts = cluster_bootstrap_exact(
        frame,
        rng=np.random.default_rng(SEED),
    )

    REPORTS.mkdir(parents=True, exist_ok=True)
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT_DISTRIBUTIONS,
        delta_topk_mean_target_model_vs_phase2=delta_mean,
        delta_topk_hit_rate=delta_hit,
    )
    distributions_sha = sha256_file(OUTPUT_DISTRIBUTIONS)

    if infeasible == 0:
        mean_ci = base.percentile_interval(delta_mean)
        hit_ci = base.percentile_interval(delta_hit)
        evidence_label = (
            "PRIMARY_NEWS_CLUSTER_CI_SUPPORTS_POSITIVE_INCREMENT"
            if mean_ci[0] > 0.0
            else "POINT_RESULT_NOT_CONFIRMED_BY_NEWS_CLUSTER_CI"
        )
    else:
        mean_ci = None
        hit_ci = None
        evidence_label = "PRIMARY_NEWS_CLUSTER_CI_INFEASIBLE"

    summary = {
        "stage": "DTRM_PHASE3_MM1_V5_PRIMARY_BOOTSTRAP",
        "status": "primary_bootstrap_complete_pending_commit",
        "method": "news_id_cluster_bootstrap",
        "replicates": REPLICATES,
        "random_seed": SEED,
        "confidence_level": CONFIDENCE_LEVEL,
        "interval": "percentile",
        "quantile_method": "linear",
        "implementation": "exchangeable_integer_quantities_exact_residual_tie_hierarchy",
        "resampling": {
            "unit": "news_id",
            "draw_count": int(frame["news_id"].nunique()),
            "sampling": "uniform_with_replacement",
            "include_all_rows_per_cluster_draw": True,
            "repeated_draws_duplicate_all_cluster_rows": True,
            "policy_recomputation_inside_each_replicate": True,
            "recompute_n_and_K": True,
            "rerun_exact_frozen_MM1_optimizer": True,
        },
        "provenance": {
            "decision_manifest_sha256": sha256_file(DECISION_MANIFEST_PATH),
            "point_result_sha256": sha256_file(POINT_RESULT_PATH),
            "signals_sha256": sha256_file(SIGNALS_PATH),
            "target_model_sha256": sha256_file(TARGET_PATH),
            "bootstrap_solver_amendment_sha256": sha256_file(BOOTSTRAP_AMENDMENT_PATH),
            "bootstrap_tie_amendment_sha256": sha256_file(TIE_AMENDMENT_PATH),
        },
        "observed": {
            "rows": int(len(frame)),
            "news_id_clusters": int(frame["news_id"].nunique()),
            "point_delta_topk_mean_target_model_vs_phase2": float(
                point["delta_topk_mean_target_model_vs_phase2"]
            ),
            "point_delta_topk_hit_rate": float(point["delta_topk_hit_rate"]),
        },
        "bootstrap": {
            "infeasible_replicates": int(infeasible),
            "zero_infeasible_required_for_confirmatory_CI": True,
            "delta_topk_mean_target_model_vs_phase2_ci95": mean_ci,
            "delta_topk_hit_rate_ci95": hit_ci,
            "hierarchy_counts": hierarchy_counts,
            "evidence_label": evidence_label,
        },
        "distributions": {
            "path": str(OUTPUT_DISTRIBUTIONS.relative_to(REPO_ROOT)),
            "sha256": distributions_sha,
        },
        "governance": {
            "rho_retuned": False,
            "threshold_retuned": False,
            "V5_policy_changed": False,
            "promotion_role": "supportive_not_required_for_point_promotion",
            "V6_policy_change_permitted_from_V5": False,
        },
    }
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")

    print("infeasible replicates:", infeasible)
    print("hierarchy counts:", hierarchy_counts)
    print("delta mean CI95:", mean_ci)
    print("delta hit-rate CI95:", hit_ci)
    print("evidence:", evidence_label)
    print("summary:", OUTPUT_SUMMARY)
    print("distributions:", OUTPUT_DISTRIBUTIONS)

    if infeasible != 0:
        raise RuntimeError(
            "Primary bootstrap produced infeasible replicates; confirmatory CI is not valid"
        )


if __name__ == "__main__":
    main()
