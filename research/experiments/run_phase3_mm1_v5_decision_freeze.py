"""Freeze the ex-ante Phase-3 MM1 V5 decision before any V5 outcome access."""

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

from run_phase3_mm0_rho_calibration import (
    prepare_reference_data,
    reproduce_phase2_signals,
    train_frozen_models,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"

V5_START = pd.Timestamp("2026-06-15T00:00:00Z")
V5_END = pd.Timestamp("2026-06-25T23:59:59Z")
EXPECTED_FEATURE_COUNT = 390

V5_ROWS_PATH = LOCAL_DATA / "phase3_mm1_v5_candidate_rows_exante.pkl"
V5_FEATURES_PATH = LOCAL_DATA / "phase3_mm1_v5_features_exante.npy"
V5_SIGNALS_PATH = LOCAL_DATA / "phase3_mm1_v5_signals_frozen.pkl"
V5_MANIFEST_PATH = (
    REPO_ROOT
    / "research"
    / "contracts"
    / "DTRM_PHASE3_MM1_V5_DECISION_MANIFEST.json"
)

REQUIRED_ROW_COLUMNS = ("news_id", "ticker", "date_dt")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()


def git_branch() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()


def require_clean_tracked_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    if status:
        raise RuntimeError(
            "Tracked working tree must be clean before freezing the V5 decision"
        )


def validate_v5_inputs(
    rows: pd.DataFrame,
    features: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray]:
    missing = set(REQUIRED_ROW_COLUMNS) - set(rows.columns)
    if missing:
        raise ValueError(f"Missing V5 ex-ante row columns: {sorted(missing)}")

    extra = set(rows.columns) - set(REQUIRED_ROW_COLUMNS)
    if extra:
        raise ValueError(
            "V5 candidate-row artifact must contain identity/date fields only; "
            f"unexpected columns: {sorted(extra)}"
        )

    normalized = rows.loc[:, REQUIRED_ROW_COLUMNS].copy()
    normalized["date_dt"] = pd.to_datetime(normalized["date_dt"], utc=True)

    if normalized.empty:
        raise ValueError("V5 candidate-row artifact must not be empty")

    if normalized[["news_id", "ticker"]].isna().any().any():
        raise ValueError("V5 row identities must not contain missing values")

    if normalized["date_dt"].isna().any():
        raise ValueError("V5 dates must be valid timestamps")

    if normalized.duplicated(["news_id", "ticker"]).any():
        raise ValueError("V5 candidate rows contain duplicate (news_id, ticker) keys")

    if (normalized["date_dt"] < V5_START).any() or (normalized["date_dt"] > V5_END).any():
        raise ValueError("V5 candidate rows fall outside the preregistered V5 window")

    X = np.asarray(features)
    if X.ndim != 2:
        raise ValueError("V5 feature matrix must be two-dimensional")

    if X.shape[0] != len(normalized):
        raise ValueError("V5 feature rows must match candidate-row count")

    if X.shape[1] != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"V5 feature matrix must contain exactly {EXPECTED_FEATURE_COUNT} columns"
        )

    if not np.issubdtype(X.dtype, np.number):
        raise ValueError("V5 features must be numeric")

    if not np.isfinite(X).all():
        raise ValueError("V5 features must contain only finite values")

    return normalized.reset_index(drop=True), np.asarray(X, dtype=np.float32)


def load_v5_inputs() -> tuple[pd.DataFrame, np.ndarray]:
    if not V5_ROWS_PATH.exists():
        raise FileNotFoundError(
            f"Missing ex-ante V5 candidate rows: {V5_ROWS_PATH}"
        )
    if not V5_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Missing ex-ante V5 feature matrix: {V5_FEATURES_PATH}"
        )

    rows = pd.read_pickle(V5_ROWS_PATH)
    features = np.load(V5_FEATURES_PATH, allow_pickle=False)
    return validate_v5_inputs(rows, features)


def reproduce_frozen_phase2_models():
    (
        _valid_rows,
        valid_reference_values,
        valid_weights,
        dtrain,
        dvalid,
    ) = prepare_reference_data()

    baseline_model, p10_model = train_frozen_models(dtrain, dvalid)

    (
        _baseline_valid,
        _calibrated_p10_valid,
        _p10_pass_valid,
        offset_reproduced,
        threshold_reproduced,
    ) = reproduce_phase2_signals(
        baseline_model,
        p10_model,
        dvalid,
        valid_reference_values,
        valid_weights,
    )

    return (
        baseline_model,
        p10_model,
        float(offset_reproduced),
        float(threshold_reproduced),
    )


def score_v5(
    rows: pd.DataFrame,
    features: np.ndarray,
    baseline_model,
    p10_model,
):
    dmatrix = xgb.DMatrix(features)

    baseline = baseline_model.predict(
        dmatrix,
        iteration_range=(0, BASELINE_SELECTED_ITERATION + 1),
    )
    raw_p10 = p10_model.predict(
        dmatrix,
        iteration_range=(0, P10_BEST_ITERATION + 1),
    )

    state = materialize_mm0_information_state(
        news_id=rows["news_id"].to_numpy(),
        ticker=rows["ticker"].to_numpy(),
        date_dt=rows["date_dt"].to_numpy(),
        baseline_point_score=baseline,
        raw_p10=raw_p10,
    )

    return state, np.asarray(raw_p10, dtype=np.float64)


def signal_frame(rows: pd.DataFrame, state, raw_p10: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": rows["news_id"].to_numpy(),
            "ticker": rows["ticker"].to_numpy(),
            "date_dt": rows["date_dt"].to_numpy(),
            "baseline_point_score": state.baseline_point_score,
            "baseline_rank": state.baseline_rank,
            "raw_p10": raw_p10,
            "calibrated_p10": state.calibrated_p10,
            "phase2_guardrail_pass": state.phase2_guardrail_pass,
        }
    )


def selection_identities(signals: pd.DataFrame, indices: np.ndarray) -> list[dict]:
    subset = signals.iloc[np.asarray(indices, dtype=np.int64)].copy()
    subset = subset.sort_values("baseline_rank", kind="stable")

    identities = []
    for row in subset.itertuples(index=False):
        news_id = row.news_id.item() if isinstance(row.news_id, np.generic) else row.news_id
        identities.append(
            {
                "news_id": news_id,
                "ticker": str(row.ticker),
                "date_dt": pd.Timestamp(row.date_dt).isoformat(),
                "baseline_rank": int(row.baseline_rank),
            }
        )
    return identities


def build_manifest(
    *,
    signals: pd.DataFrame,
    optimization,
    rows_sha256: str,
    features_sha256: str,
    signals_sha256: str,
    source_head: str,
    source_branch: str,
    offset_reproduced: float,
    threshold_reproduced: float,
    baseline_best_iteration: int,
    p10_best_iteration: int,
) -> dict:
    duplicate_pairs = int(signals.duplicated(["news_id", "ticker"]).sum())

    return {
        "contract": "DTRM_PHASE3_MM1_EVALUATION_CONTRACT",
        "artifact": "DTRM_PHASE3_MM1_V5_DECISION_MANIFEST",
        "status": "decision_frozen_pending_git_commit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cohort": {
            "id": "V5",
            "start": V5_START.isoformat(),
            "end": V5_END.isoformat(),
        },
        "source_code": {
            "git_head_before_manifest_commit": source_head,
            "git_branch": source_branch,
            "tracked_worktree_clean_before_run": True,
        },
        "input_artifacts": {
            "candidate_rows": {
                "path": str(V5_ROWS_PATH.relative_to(REPO_ROOT)),
                "sha256": rows_sha256,
            },
            "features": {
                "path": str(V5_FEATURES_PATH.relative_to(REPO_ROOT)),
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
            "duplicate_pairs": duplicate_pairs,
            "K_H": int(optimization.k),
            "phase2_eligible_rows": int(optimization.eligible_rows),
        },
        "frozen_signals": {
            "path": str(V5_SIGNALS_PATH.relative_to(REPO_ROOT)),
            "sha256": signals_sha256,
        },
        "decision": {
            "phase2_champion_row_identities": selection_identities(
                signals,
                optimization.champion_indices,
            ),
            "MM1_selected_row_identities": selection_identities(
                signals,
                optimization.selected_indices,
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
            "V5_realized_outcomes_accessed": False,
            "V5_future_price_path_used_for_decision": False,
            "V2_V3_V4_MM1_realized_results_used": False,
            "decision_reoptimization_after_manifest_commit": "forbidden",
            "manifest_commit_required_before_realized_evaluation": True,
        },
    }


def main() -> None:
    if V5_MANIFEST_PATH.exists():
        raise RuntimeError(
            "V5 decision manifest already exists; refusing to overwrite a freeze artifact"
        )

    require_clean_tracked_worktree()
    source_head = git_head()
    source_branch = git_branch()

    rows_sha256 = sha256_file(V5_ROWS_PATH)
    features_sha256 = sha256_file(V5_FEATURES_PATH)

    rows, features = load_v5_inputs()

    (
        baseline_model,
        p10_model,
        offset_reproduced,
        threshold_reproduced,
    ) = reproduce_frozen_phase2_models()

    state, raw_p10 = score_v5(
        rows,
        features,
        baseline_model,
        p10_model,
    )

    signals = signal_frame(rows, state, raw_p10)
    V5_SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    signals.to_pickle(V5_SIGNALS_PATH)
    signals_sha256 = sha256_file(V5_SIGNALS_PATH)

    optimization = optimize_mm1(state)

    manifest = build_manifest(
        signals=signals,
        optimization=optimization,
        rows_sha256=rows_sha256,
        features_sha256=features_sha256,
        signals_sha256=signals_sha256,
        source_head=source_head,
        source_branch=source_branch,
        offset_reproduced=offset_reproduced,
        threshold_reproduced=threshold_reproduced,
        baseline_best_iteration=int(baseline_model.best_iteration),
        p10_best_iteration=int(p10_model.best_iteration),
    )

    V5_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V5 DECISION FREEZE")
    print("rows:", len(signals))
    print("K_H:", optimization.k)
    print("Phase-2 eligible rows:", optimization.eligible_rows)
    print("robust value MM1:", optimization.robust_value_selected)
    print("robust value Phase 2:", optimization.robust_value_champion)
    print("robust lift:", optimization.robust_lift)
    print("overlap with Phase 2:", optimization.overlap_with_champion)
    print("intervention:", optimization.intervention)
    print("signals:", V5_SIGNALS_PATH)
    print("manifest:", V5_MANIFEST_PATH)
    print()
    print("NEXT REQUIRED ACTION: commit the manifest before any V5 realized evaluation.")


if __name__ == "__main__":
    main()
