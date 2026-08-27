"""Run the preregistered V5 ticker-cluster sensitivity bootstrap for MM1.

This sensitivity analysis reuses the exact exchangeable-copy MM1 bootstrap
implementation frozen for the primary news_id analysis. The only inferential
changes are the preregistered resampling unit (ticker) and random seed
(20260828). It has no promotion role and cannot change the frozen V5/V6 policy.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_phase3_mm1_v5_primary_bootstrap_exact_ties as exact


REPO_ROOT = exact.REPO_ROOT
LOCAL_DATA = exact.LOCAL_DATA
REPORTS = exact.REPORTS
DECISION_MANIFEST_PATH = exact.DECISION_MANIFEST_PATH
POINT_RESULT_PATH = exact.POINT_RESULT_PATH
SIGNALS_PATH = exact.SIGNALS_PATH
TARGET_PATH = exact.TARGET_PATH
BOOTSTRAP_AMENDMENT_PATH = exact.BOOTSTRAP_AMENDMENT_PATH
TIE_AMENDMENT_PATH = exact.TIE_AMENDMENT_PATH
PRIMARY_BOOTSTRAP_PATH = REPORTS / "DTRM_PHASE3_MM1_V5_PRIMARY_BOOTSTRAP.json"

OUTPUT_SUMMARY = REPORTS / "DTRM_PHASE3_MM1_V5_TICKER_SENSITIVITY_BOOTSTRAP.json"
OUTPUT_DISTRIBUTIONS = (
    LOCAL_DATA / "phase3_mm1_v5_ticker_sensitivity_bootstrap_distributions.npz"
)

REPLICATES = 10_000
SEED = 20260828
TOPK_FRACTION = 0.10
CONFIDENCE_LEVEL = 0.95


def sha256_file(path: Path) -> str:
    return exact.sha256_file(path)


def require_outputs_absent() -> None:
    existing = [path for path in (OUTPUT_SUMMARY, OUTPUT_DISTRIBUTIONS) if path.exists()]
    if existing:
        raise RuntimeError(
            "V5 ticker sensitivity bootstrap refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def cluster_bootstrap_ticker_exact(
    frame: pd.DataFrame,
    *,
    rng: np.random.Generator,
    replicates: int = REPLICATES,
) -> tuple[np.ndarray, np.ndarray, int, dict[str, int]]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")

    cluster_codes, cluster_labels = pd.factorize(frame["ticker"], sort=False)
    n_clusters = int(len(cluster_labels))
    if n_clusters <= 0:
        raise ValueError("V5 ticker bootstrap requires at least one ticker cluster")

    delta_mean = np.full(replicates, np.nan, dtype=np.float64)
    delta_hit = np.full(replicates, np.nan, dtype=np.float64)
    infeasible = 0
    hierarchy_counts: dict[str, int] = {}

    for replicate in range(replicates):
        multiplicity = exact.base.resampled_row_multiplicity(
            cluster_codes,
            n_clusters=n_clusters,
            rng=rng,
        )
        result = exact.evaluate_resampled_policy_exact(frame, multiplicity)
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
    require_outputs_absent()
    exact.base.require_clean_tracked_worktree()
    exact.require_committed_bytes(BOOTSTRAP_AMENDMENT_PATH)
    exact.require_committed_bytes(TIE_AMENDMENT_PATH)
    exact.require_committed_bytes(PRIMARY_BOOTSTRAP_PATH)

    decision_manifest = exact.base.require_committed_json(
        DECISION_MANIFEST_PATH,
        expected_status="decision_frozen_pending_git_commit",
    )
    point_result = exact.base.require_committed_json(
        POINT_RESULT_PATH,
        expected_status="realized_point_evaluation_complete_pending_commit",
    )
    primary_bootstrap = exact.base.require_committed_json(
        PRIMARY_BOOTSTRAP_PATH,
        expected_status="primary_bootstrap_complete_pending_commit",
    )

    if point_result["decision_manifest"]["sha256"] != sha256_file(DECISION_MANIFEST_PATH):
        raise RuntimeError("V5 point result is bound to a different decision manifest")
    if point_result["point_evaluation"]["classification"] != "PROMOTED_POINT":
        raise RuntimeError("V5 ticker sensitivity expected frozen PROMOTED_POINT")
    if primary_bootstrap["bootstrap"]["infeasible_replicates"] != 0:
        raise RuntimeError("Committed primary bootstrap is not a valid complete reference")

    frame = exact.base.load_bootstrap_frame(decision_manifest, point_result)
    point = exact.base.reproduce_frozen_point(frame, decision_manifest)
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

    print("DTRM PHASE 3 MM1 V5 TICKER-CLUSTER SENSITIVITY BOOTSTRAP")
    print("point result reproduction: PASS")
    print("primary news_id bootstrap committed: PASS")
    print("exchangeable tie amendment: PASS")
    print("rows:", len(frame))
    print("ticker clusters:", frame["ticker"].nunique())
    print("replicates:", REPLICATES)
    print("seed:", SEED)

    delta_mean, delta_hit, infeasible, hierarchy_counts = cluster_bootstrap_ticker_exact(
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
        mean_ci = exact.base.percentile_interval(delta_mean)
        hit_ci = exact.base.percentile_interval(delta_hit)
        evidence_label = (
            "TICKER_CLUSTER_SENSITIVITY_SUPPORTS_POSITIVE_INCREMENT"
            if mean_ci[0] > 0.0
            else "TICKER_CLUSTER_SENSITIVITY_CI_INCLUDES_ZERO"
        )
    else:
        mean_ci = None
        hit_ci = None
        evidence_label = "TICKER_CLUSTER_SENSITIVITY_INFEASIBLE"

    summary = {
        "stage": "DTRM_PHASE3_MM1_V5_TICKER_SENSITIVITY_BOOTSTRAP",
        "status": "ticker_sensitivity_complete_pending_commit",
        "method": "ticker_cluster_bootstrap",
        "replicates": REPLICATES,
        "random_seed": SEED,
        "confidence_level": CONFIDENCE_LEVEL,
        "interval": "percentile",
        "quantile_method": "linear",
        "implementation": "exchangeable_integer_quantities_exact_residual_tie_hierarchy",
        "resampling": {
            "unit": "ticker",
            "draw_count": int(frame["ticker"].nunique()),
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
            "primary_bootstrap_sha256": sha256_file(PRIMARY_BOOTSTRAP_PATH),
            "signals_sha256": sha256_file(SIGNALS_PATH),
            "target_model_sha256": sha256_file(TARGET_PATH),
            "bootstrap_solver_amendment_sha256": sha256_file(BOOTSTRAP_AMENDMENT_PATH),
            "bootstrap_tie_amendment_sha256": sha256_file(TIE_AMENDMENT_PATH),
        },
        "observed": {
            "rows": int(len(frame)),
            "ticker_clusters": int(frame["ticker"].nunique()),
            "point_delta_topk_mean_target_model_vs_phase2": float(
                point["delta_topk_mean_target_model_vs_phase2"]
            ),
            "point_delta_topk_hit_rate": float(point["delta_topk_hit_rate"]),
        },
        "bootstrap": {
            "infeasible_replicates": int(infeasible),
            "same_feasibility_rule_as_primary": True,
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
            "role": "sensitivity_only",
            "promotion_role": "none",
            "rho_retuned": False,
            "threshold_retuned": False,
            "V5_policy_changed": False,
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
            "Ticker sensitivity bootstrap produced infeasible replicates; sensitivity CI is not valid"
        )


if __name__ == "__main__":
    main()
