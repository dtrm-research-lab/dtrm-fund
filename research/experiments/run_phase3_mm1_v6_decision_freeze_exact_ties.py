"""Freeze V6 MM1 using the frozen policy plus exact reduced residual ties.

This is the operational implementation of
DTRM_PHASE3_MM1_V6_RESIDUAL_TIE_SOLVER_AMENDMENT. It does not modify the
byte-frozen V5 policy modules. The finite-threshold primary solve, champion
fallback, robust tolerance, and tie hierarchy are unchanged; only the residual
tie computational route is reduced to exact theta-boundary subproblems.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

import run_phase3_mm1_v6_decision_freeze as base
import run_phase3_mm1_v5_primary_bootstrap_exact_ties as exact_ties
from dtrm.phase3_mm1_optimizer import (
    MM1OptimizationResult,
    ROBUST_VALUE_TOLERANCE,
    _best_alternative_total_excluding,
    _phase2_champion_indices,
    _threshold_primary_optimum,
)
from dtrm.phase3_mm1_robust_value import robust_value_for_selection


REPO_ROOT = base.REPO_ROOT
AMENDMENT_PATH = (
    REPO_ROOT
    / "research"
    / "contracts"
    / "DTRM_PHASE3_MM1_V6_RESIDUAL_TIE_SOLVER_AMENDMENT.yaml"
)


def require_committed_bytes(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    relative = str(path.relative_to(REPO_ROOT))
    committed = subprocess.check_output(
        ["git", "show", f"HEAD:{relative}"],
        cwd=REPO_ROOT,
    )
    if committed != path.read_bytes():
        raise RuntimeError(f"Local amendment differs from committed Git bytes: {relative}")


def optimize_v6_exact_reduced_ties(state, frame) -> tuple[MM1OptimizationResult, dict]:
    """Apply the frozen MM1 policy with an exact reduced residual tie route."""

    k = int(state.rows * 0.10)
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
    ranks = np.asarray(state.baseline_rank[eligible_indices], dtype=np.int64)

    primary_local, primary_total, primary_theta, threshold_count = _threshold_primary_optimum(
        baseline,
        widths,
        k=k,
        baseline_ranks=ranks,
    )
    primary_global = eligible_indices[primary_local]
    primary_value = robust_value_for_selection(state, primary_global)
    primary_mean = float(primary_total / k)
    if not np.isclose(
        primary_mean,
        primary_value.robust_value,
        rtol=0.0,
        atol=1.0e-10,
    ):
        raise RuntimeError("Exact threshold objective disagrees with robust-value adapter")

    diagnostics = {
        "primary_theta": float(primary_theta),
        "threshold_count": int(threshold_count),
        "residual_route": "not_required",
    }

    if primary_value.robust_value <= champion_value.robust_value + ROBUST_VALUE_TOLERANCE:
        selected = champion
        selected_value = champion_value
        intervention = False
        solver_status = "optimal_exact_threshold_champion_fallback"
        diagnostics["residual_route"] = "champion_fallback"
    else:
        best_alternative_total = _best_alternative_total_excluding(
            baseline,
            widths,
            k=k,
            baseline_ranks=ranks,
            excluded_local=primary_local,
        )
        robust_band_floor_total = float(
            k * (primary_value.robust_value - ROBUST_VALUE_TOLERANCE)
        )
        diagnostics["best_alternative_total"] = float(best_alternative_total)
        diagnostics["robust_band_floor_total"] = float(robust_band_floor_total)

        if best_alternative_total < robust_band_floor_total:
            selected = primary_global
            selected_value = primary_value
            intervention = True
            solver_status = "optimal_exact_threshold_unique_primary_band"
            diagnostics["residual_route"] = "unique_primary_band"
        else:
            # Unit-capacity specialization of the already-tested exchangeable
            # exact residual hierarchy: expanded row identity is the original
            # V6 row identity, so all capacities are exactly one.
            expanded_idx = np.arange(state.rows, dtype=np.int64)
            quantity, tie_diag = exact_ties.resolve_exact_tie_quantity(
                frame,
                state=state,
                expanded_idx=expanded_idx,
                eligible_indices=eligible_indices,
                champion=champion,
                baseline_expanded=baseline,
                widths_expanded=widths,
                ranks_expanded=ranks,
                k=k,
                primary_total=float(primary_total),
            )
            if quantity.shape != (state.rows,):
                raise RuntimeError("Reduced residual hierarchy returned wrong quantity shape")
            if not np.isin(quantity, [0, 1]).all():
                raise RuntimeError("V6 unit-capacity residual hierarchy returned non-binary quantity")
            selected = np.flatnonzero(quantity == 1).astype(np.int64)
            if selected.size != k:
                raise RuntimeError("Reduced residual hierarchy returned wrong cardinality")
            selected_value = robust_value_for_selection(state, selected)
            if (
                selected_value.robust_value
                < primary_value.robust_value - ROBUST_VALUE_TOLERANCE - 1.0e-10
            ):
                raise RuntimeError("Reduced residual hierarchy left frozen robust band")
            intervention = True
            solver_status = "optimal_exact_threshold_plus_reduced_residual_tie_hierarchy"
            diagnostics["residual_route"] = "exact_reduced_residual_tie_hierarchy"
            diagnostics["tie"] = tie_diag

    if not np.all(state.phase2_guardrail_pass[selected]):
        raise RuntimeError("MM1 optimizer selected a Phase-2-vetoed candidate")
    if np.unique(selected).size != k:
        raise RuntimeError("MM1 optimizer returned duplicate or wrong-cardinality rows")

    selected_set = set(int(i) for i in selected)
    overlap = int(sum(int(i) in selected_set for i in champion))

    result = MM1OptimizationResult(
        selected_indices=np.asarray(selected, dtype=np.int64),
        champion_indices=np.asarray(champion, dtype=np.int64),
        k=int(k),
        eligible_rows=int(eligible_indices.size),
        robust_value_selected=float(selected_value.robust_value),
        robust_value_champion=float(champion_value.robust_value),
        robust_lift=float(selected_value.robust_value - champion_value.robust_value),
        nominal_mean_selected=float(selected_value.nominal_mean),
        nominal_mean_champion=float(champion_value.nominal_mean),
        overlap_with_champion=int(overlap),
        intervention=bool(intervention),
        solver_status=solver_status,
        solver_mip_gap=0.0,
        scipy_version=str(exact_ties.base.scipy.__version__) if hasattr(exact_ties.base, "scipy") else "exact_reduced",
        numpy_version=str(np.__version__),
    )
    return result, diagnostics


def main() -> None:
    if base.V6_MANIFEST_PATH.exists():
        raise RuntimeError("V6 decision manifest already exists; refusing to overwrite freeze artifact")

    base.require_clean_tracked_worktree()
    require_committed_bytes(AMENDMENT_PATH)
    source_head = base.git_head()
    source_branch = base.git_branch()
    policy_blobs = base.require_frozen_v5_policy_code()

    provenance = base.load_frozen_v6_provenance()
    provenance_sha256 = base.sha256_file(base.V6_PROVENANCE_PATH)
    rows_sha256 = base.sha256_file(base.V6_ROWS_PATH)
    features_sha256 = base.sha256_file(base.V6_FEATURES_PATH)
    base.require_frozen_input_hashes(
        provenance,
        rows_sha256=rows_sha256,
        features_sha256=features_sha256,
    )
    rows, features = base.load_v6_inputs()

    (
        baseline_model,
        p10_model,
        offset_reproduced,
        threshold_reproduced,
    ) = base.reproduce_frozen_phase2_models()

    if not np.isclose(
        offset_reproduced,
        base.P10_CALIBRATION_OFFSET,
        rtol=0.0,
        atol=1.0e-15,
    ):
        raise RuntimeError("Frozen Phase-2 P10 calibration offset did not reproduce")
    if not np.isclose(
        threshold_reproduced,
        base.P10_GUARDRAIL_THRESHOLD,
        rtol=0.0,
        atol=1.0e-15,
    ):
        raise RuntimeError("Frozen Phase-2 P10 threshold did not reproduce")

    state, raw_p10 = base.score_v6(rows, features, baseline_model, p10_model)
    signals = base.signal_frame(rows, state, raw_p10)
    base.V6_SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    signals.to_pickle(base.V6_SIGNALS_PATH)
    signals_sha256 = base.sha256_file(base.V6_SIGNALS_PATH)

    optimization, solver_diagnostics = optimize_v6_exact_reduced_ties(state, signals)

    manifest = base.build_manifest(
        signals=signals,
        optimization=optimization,
        rows_sha256=rows_sha256,
        features_sha256=features_sha256,
        signals_sha256=signals_sha256,
        provenance_sha256=provenance_sha256,
        source_head=source_head,
        source_branch=source_branch,
        offset_reproduced=offset_reproduced,
        threshold_reproduced=threshold_reproduced,
        baseline_best_iteration=int(baseline_model.best_iteration),
        p10_best_iteration=int(p10_model.best_iteration),
        policy_blobs=policy_blobs,
    )
    manifest["residual_tie_solver_amendment"] = {
        "path": str(AMENDMENT_PATH.relative_to(REPO_ROOT)),
        "sha256": base.sha256_file(AMENDMENT_PATH),
        "role": "computational_only",
        "scientific_policy_changed": False,
    }
    manifest["decision"]["solver_diagnostics"] = solver_diagnostics
    manifest["information_firewall"]["V6_realized_outcomes_accessed"] = False
    manifest["information_firewall"]["realized_evaluation_before_2026_09_04"] = "forbidden"

    base.V6_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V6 DECISION FREEZE - EXACT REDUCED TIES")
    print("frozen provenance: PASS")
    print("frozen V5 policy code: PASS")
    print("V6 residual tie amendment: PASS")
    print("outcome firewall: PASS")
    print("rows:", len(signals))
    print("unique news:", signals["news_id"].nunique())
    print("canonical tickers:", signals["ticker"].nunique())
    print("K_H:", optimization.k)
    print("Phase-2 eligible rows:", optimization.eligible_rows)
    print("robust value MM1:", optimization.robust_value_selected)
    print("robust value Phase 2:", optimization.robust_value_champion)
    print("robust lift:", optimization.robust_lift)
    print("overlap with Phase 2:", optimization.overlap_with_champion)
    print("intervention:", optimization.intervention)
    print("solver status:", optimization.solver_status)
    print("residual route:", solver_diagnostics.get("residual_route"))
    print("signals sha256:", signals_sha256)
    print("signals:", base.V6_SIGNALS_PATH)
    print("manifest:", base.V6_MANIFEST_PATH)
    print()
    print("NEXT REQUIRED ACTION: commit the V6 decision manifest before any realized evaluation.")
    print("V6 REALIZED EVALUATION REMAINS FORBIDDEN BEFORE 2026-09-04.")


if __name__ == "__main__":
    main()
