"""Freeze the prospective Phase-3 MM1 V6 decision before any V6 outcome access."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

from dtrm.phase3_mm0_state import (
    BASELINE_SELECTED_ITERATION,
    P10_BEST_ITERATION,
    P10_CALIBRATION_OFFSET,
    P10_GUARDRAIL_THRESHOLD,
    materialize_mm0_information_state,
)
from dtrm.phase3_mm1_optimizer import optimize_mm1
from dtrm.phase3_mm1_robust_value import RHO_MM0

from run_phase3_mm1_v5_decision_freeze import (
    reproduce_frozen_phase2_models,
    selection_identities,
    signal_frame,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"
CONTRACTS = REPO_ROOT / "research" / "contracts"

V6_START = pd.Timestamp("2026-06-26T00:00:00Z")
V6_END = pd.Timestamp("2026-07-06T23:59:59Z")
EXPECTED_FEATURE_COUNT = 390
EXPECTED_ROWS = 11922
EXPECTED_RHO = 0.4378501384944031

V6_ROWS_PATH = LOCAL_DATA / "phase3_mm1_v6_candidate_rows_exante.pkl"
V6_FEATURES_PATH = LOCAL_DATA / "phase3_mm1_v6_features_exante.npy"
V6_SIGNALS_PATH = LOCAL_DATA / "phase3_mm1_v6_signals_frozen.pkl"
V6_PROVENANCE_PATH = CONTRACTS / "DTRM_PHASE3_MM1_V6_EXANTE_PROVENANCE.json"
V6_MANIFEST_PATH = CONTRACTS / "DTRM_PHASE3_MM1_V6_DECISION_MANIFEST.json"
V5_MANIFEST_PATH = CONTRACTS / "DTRM_PHASE3_MM1_V5_DECISION_MANIFEST.json"
EVALUATION_CONTRACT_PATH = CONTRACTS / "DTRM_PHASE3_MM1_EVALUATION_CONTRACT.yaml"
SOLVER_AMENDMENT_PATH = CONTRACTS / "DTRM_PHASE3_MM1_SOLVER_AMENDMENT_V5.yaml"

REQUIRED_ROW_COLUMNS = ("news_id", "ticker", "date_dt")

# Git blob SHAs from the committed V5 ex-ante decision lineage. V6 must execute
# the exact same decision code, not merely numerically equal parameters.
FROZEN_V5_POLICY_BLOBS = {
    "src/dtrm/phase3_mm0_state.py": "43e1d654c970b2f6bbbc8d3c600105d918e5fd57",
    "src/dtrm/phase3_mm1_robust_value.py": "c8d05e002d0c1f5e646a593e13cfa570d4f17841",
    "src/dtrm/phase3_mm1_optimizer.py": "7d9f80db4d584d9106daa81015c9de1f781b5421",
    "research/experiments/run_phase3_mm0_rho_calibration.py": "5a9fc0c609b4cffd034a412d7101af8c7a450aea",
    "research/experiments/run_phase3_mm1_v5_decision_freeze.py": "8978a4ee78196a275d3f8299a63f4cc2bd652dde",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def git_branch() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def git_blob_sha(path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", path], cwd=REPO_ROOT, text=True
    ).strip()


def require_clean_tracked_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    if status:
        raise RuntimeError("Tracked working tree must be clean before freezing V6")


def require_frozen_v5_policy_code() -> dict[str, str]:
    observed = {}
    for relative_path, expected_blob in FROZEN_V5_POLICY_BLOBS.items():
        actual = git_blob_sha(relative_path)
        if actual != expected_blob:
            raise RuntimeError(
                f"Frozen V5 policy source changed before V6: {relative_path} "
                f"({actual} != {expected_blob})"
            )
        observed[relative_path] = actual
    if not np.isclose(float(RHO_MM0), EXPECTED_RHO, rtol=0.0, atol=0.0):
        raise RuntimeError("Frozen V5 rho changed before V6")
    return observed


def load_frozen_v6_provenance() -> dict:
    if not V6_PROVENANCE_PATH.exists():
        raise FileNotFoundError(f"Missing V6 ex-ante provenance: {V6_PROVENANCE_PATH}")
    provenance = json.loads(V6_PROVENANCE_PATH.read_text())
    if provenance.get("status") != "frozen_before_mm1_decision":
        raise RuntimeError("V6 provenance is not frozen for MM1 decision use")
    window = provenance.get("v6_window", {})
    if window.get("start") != V6_START.isoformat():
        raise RuntimeError("Frozen V6 provenance start timestamp mismatch")
    if window.get("end") != V6_END.isoformat():
        raise RuntimeError("Frozen V6 provenance end timestamp mismatch")
    firewall = provenance.get("information_firewall", {})
    if firewall.get("V5_results_used_to_change_V6_policy") is not False:
        raise RuntimeError("V6 provenance does not preserve the V5-policy firewall")
    return provenance


def require_frozen_input_hashes(
    provenance: dict,
    *,
    rows_sha256: str,
    features_sha256: str,
) -> None:
    artifacts = provenance.get("artifacts", {})
    rows_spec = artifacts.get("candidate_rows", {})
    features_spec = artifacts.get("feature_matrix", {})

    if rows_spec.get("path") != str(V6_ROWS_PATH.relative_to(REPO_ROOT)):
        raise RuntimeError("Frozen V6 candidate-row provenance path mismatch")
    if features_spec.get("path") != str(V6_FEATURES_PATH.relative_to(REPO_ROOT)):
        raise RuntimeError("Frozen V6 feature-matrix provenance path mismatch")
    if rows_spec.get("sha256") != rows_sha256:
        raise RuntimeError("V6 candidate-row SHA-256 does not match frozen provenance")
    if features_spec.get("sha256") != features_sha256:
        raise RuntimeError("V6 feature-matrix SHA-256 does not match frozen provenance")
    if features_spec.get("shape") != [EXPECTED_ROWS, EXPECTED_FEATURE_COUNT]:
        raise RuntimeError("Frozen V6 feature-matrix shape provenance mismatch")


def validate_v6_inputs(
    rows: pd.DataFrame,
    features: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    missing = set(REQUIRED_ROW_COLUMNS) - set(rows.columns)
    if missing:
        raise ValueError(f"Missing V6 ex-ante row columns: {sorted(missing)}")
    extra = set(rows.columns) - set(REQUIRED_ROW_COLUMNS)
    if extra:
        raise ValueError(
            "V6 candidate-row artifact must contain identity/date fields only; "
            f"unexpected columns: {sorted(extra)}"
        )

    normalized = rows.loc[:, REQUIRED_ROW_COLUMNS].copy()
    normalized["date_dt"] = pd.to_datetime(normalized["date_dt"], utc=True)
    if normalized.empty:
        raise ValueError("V6 candidate-row artifact must not be empty")
    if normalized[["news_id", "ticker"]].isna().any().any():
        raise ValueError("V6 row identities must not contain missing values")
    if normalized["date_dt"].isna().any():
        raise ValueError("V6 dates must be valid timestamps")
    if normalized.duplicated(["news_id", "ticker"]).any():
        raise ValueError("V6 candidate rows contain duplicate (news_id, ticker) keys")
    if (normalized["date_dt"] < V6_START).any() or (normalized["date_dt"] > V6_END).any():
        raise ValueError("V6 candidate rows fall outside the preregistered V6 window")

    X = np.asarray(features)
    if X.ndim != 2:
        raise ValueError("V6 feature matrix must be two-dimensional")
    if X.shape[0] != len(normalized):
        raise ValueError("V6 feature rows must match candidate-row count")
    if X.shape[1] != EXPECTED_FEATURE_COUNT:
        raise ValueError(f"V6 feature matrix must contain exactly {EXPECTED_FEATURE_COUNT} columns")
    if not np.issubdtype(X.dtype, np.number):
        raise ValueError("V6 features must be numeric")
    if not np.isfinite(X).all():
        raise ValueError("V6 features must contain only finite values")
    return normalized.reset_index(drop=True), np.asarray(X, dtype=np.float32)


def load_v6_inputs() -> tuple[pd.DataFrame, np.ndarray]:
    if not V6_ROWS_PATH.exists():
        raise FileNotFoundError(f"Missing ex-ante V6 candidate rows: {V6_ROWS_PATH}")
    if not V6_FEATURES_PATH.exists():
        raise FileNotFoundError(f"Missing ex-ante V6 feature matrix: {V6_FEATURES_PATH}")
    rows = pd.read_pickle(V6_ROWS_PATH)
    features = np.load(V6_FEATURES_PATH, allow_pickle=False)
    return validate_v6_inputs(rows, features)


def score_v6(rows, features, baseline_model, p10_model):
    dmatrix = xgb.DMatrix(features)
    baseline = baseline_model.predict(
        dmatrix, iteration_range=(0, BASELINE_SELECTED_ITERATION + 1)
    )
    raw_p10 = p10_model.predict(
        dmatrix, iteration_range=(0, P10_BEST_ITERATION + 1)
    )
    state = materialize_mm0_information_state(
        news_id=rows["news_id"].to_numpy(),
        ticker=rows["ticker"].to_numpy(),
        date_dt=rows["date_dt"].to_numpy(),
        baseline_point_score=baseline,
        raw_p10=raw_p10,
    )
    return state, np.asarray(raw_p10, dtype=np.float64)


def build_manifest(
    *,
    signals: pd.DataFrame,
    optimization,
    rows_sha256: str,
    features_sha256: str,
    signals_sha256: str,
    provenance_sha256: str,
    source_head: str,
    source_branch: str,
    offset_reproduced: float,
    threshold_reproduced: float,
    baseline_best_iteration: int,
    p10_best_iteration: int,
    policy_blobs: dict[str, str],
) -> dict:
    return {
        "contract": "DTRM_PHASE3_MM1_EVALUATION_CONTRACT",
        "artifact": "DTRM_PHASE3_MM1_V6_DECISION_MANIFEST",
        "status": "decision_frozen_pending_git_commit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cohort": {
            "id": "V6",
            "role": "prospective_temporal_replication",
            "start": V6_START.isoformat(),
            "end": V6_END.isoformat(),
            "latest_nominal_target_date": "2026-09-04",
            "realized_evaluation_before_target_maturity": "forbidden",
        },
        "source_code": {
            "git_head_before_manifest_commit": source_head,
            "git_branch": source_branch,
            "tracked_worktree_clean_before_run": True,
            "frozen_V5_policy_git_blobs": policy_blobs,
            "policy_code_byte_identical_to_V5_freeze": True,
        },
        "frozen_exante_provenance": {
            "path": str(V6_PROVENANCE_PATH.relative_to(REPO_ROOT)),
            "sha256": provenance_sha256,
            "input_hashes_enforced_before_scoring": True,
        },
        "frozen_policy": {
            "rho": float(RHO_MM0),
            "baseline_selected_iteration": BASELINE_SELECTED_ITERATION,
            "p10_best_iteration": P10_BEST_ITERATION,
            "p10_calibration_offset": P10_CALIBRATION_OFFSET,
            "p10_guardrail_threshold": P10_GUARDRAIL_THRESHOLD,
            "V5_results_used_to_change_policy": False,
        },
        "input_artifacts": {
            "candidate_rows": {
                "path": str(V6_ROWS_PATH.relative_to(REPO_ROOT)),
                "sha256": rows_sha256,
            },
            "features": {
                "path": str(V6_FEATURES_PATH.relative_to(REPO_ROOT)),
                "sha256": features_sha256,
                "columns": EXPECTED_FEATURE_COUNT,
            },
        },
        "phase2_reproduction": {
            "baseline_best_iteration": baseline_best_iteration,
            "baseline_selected_iteration": BASELINE_SELECTED_ITERATION,
            "p10_best_iteration": p10_best_iteration,
            "p10_calibration_offset_frozen": P10_CALIBRATION_OFFSET,
            "p10_calibration_offset_reproduced": offset_reproduced,
            "p10_threshold_frozen": P10_GUARDRAIL_THRESHOLD,
            "p10_threshold_reproduced": threshold_reproduced,
        },
        "cohort_structure": {
            "rows": int(len(signals)),
            "unique_news_id": int(signals["news_id"].nunique()),
            "canonical_tickers": int(signals["ticker"].nunique()),
            "duplicate_pairs": int(signals.duplicated(["news_id", "ticker"]).sum()),
            "K_H": int(optimization.k),
            "phase2_eligible_rows": int(optimization.eligible_rows),
        },
        "frozen_signals": {
            "path": str(V6_SIGNALS_PATH.relative_to(REPO_ROOT)),
            "sha256": signals_sha256,
        },
        "decision": {
            "phase2_champion_row_identities": selection_identities(
                signals, optimization.champion_indices
            ),
            "MM1_selected_row_identities": selection_identities(
                signals, optimization.selected_indices
            ),
            "robust_value_MM1": float(optimization.robust_value_selected),
            "robust_value_phase2": float(optimization.robust_value_champion),
            "robust_lift": float(optimization.robust_lift),
            "nominal_mean_MM1": float(optimization.nominal_mean_selected),
            "nominal_mean_phase2": float(optimization.nominal_mean_champion),
            "overlap_with_phase2": int(optimization.overlap_with_champion),
            "intervention": bool(optimization.intervention),
            "solver_status": optimization.solver_status,
            "solver_mip_gap": float(optimization.solver_mip_gap),
            "scipy_version": optimization.scipy_version,
            "numpy_version": optimization.numpy_version,
        },
        "information_firewall": {
            "V6_realized_outcomes_accessed": False,
            "V6_future_price_path_used_for_decision": False,
            "V5_results_used_to_change_V6_policy": False,
            "decision_reoptimization_after_manifest_commit": "forbidden",
            "manifest_commit_required_before_realized_evaluation": True,
            "realized_evaluation_before_2026_09_04": "forbidden",
        },
    }


def main() -> None:
    if V6_MANIFEST_PATH.exists():
        raise RuntimeError("V6 decision manifest already exists; refusing to overwrite freeze artifact")

    require_clean_tracked_worktree()
    source_head = git_head()
    source_branch = git_branch()
    policy_blobs = require_frozen_v5_policy_code()

    provenance = load_frozen_v6_provenance()
    provenance_sha256 = sha256_file(V6_PROVENANCE_PATH)
    rows_sha256 = sha256_file(V6_ROWS_PATH)
    features_sha256 = sha256_file(V6_FEATURES_PATH)
    require_frozen_input_hashes(
        provenance, rows_sha256=rows_sha256, features_sha256=features_sha256
    )

    rows, features = load_v6_inputs()
    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError(f"Frozen V6 row count changed: {len(rows)} != {EXPECTED_ROWS}")

    baseline_model, p10_model, offset_reproduced, threshold_reproduced = (
        reproduce_frozen_phase2_models()
    )
    if not np.isclose(offset_reproduced, P10_CALIBRATION_OFFSET, rtol=0.0, atol=1e-15):
        raise RuntimeError("Frozen Phase-2 P10 calibration offset did not reproduce")
    if not np.isclose(threshold_reproduced, P10_GUARDRAIL_THRESHOLD, rtol=0.0, atol=1e-15):
        raise RuntimeError("Frozen Phase-2 P10 threshold did not reproduce")

    state, raw_p10 = score_v6(rows, features, baseline_model, p10_model)
    signals = signal_frame(rows, state, raw_p10)
    V6_SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    signals.to_pickle(V6_SIGNALS_PATH)
    signals_sha256 = sha256_file(V6_SIGNALS_PATH)

    optimization = optimize_mm1(state)

    manifest = build_manifest(
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
    V6_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V6 DECISION FREEZE")
    print("frozen provenance: PASS")
    print("frozen V5 policy code: PASS")
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
    print("signals sha256:", signals_sha256)
    print("signals:", V6_SIGNALS_PATH)
    print("manifest:", V6_MANIFEST_PATH)
    print()
    print("NEXT REQUIRED ACTION: commit the V6 decision manifest before any realized evaluation.")
    print("V6 REALIZED EVALUATION REMAINS FORBIDDEN BEFORE 2026-09-04.")


if __name__ == "__main__":
    main()
