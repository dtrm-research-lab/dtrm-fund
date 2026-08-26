"""Run the preregistered V5 primary news_id cluster bootstrap for MM1.

The V5 point result is already frozen. This runner performs the supportive
uncertainty analysis exactly as preregistered: uniformly resample observed
news_id clusters with replacement, duplicate every row belonging to each
cluster draw, recompute n and K, rebuild the frozen Phase-2 information state,
rerun the exact frozen MM1 policy using ex-ante signals only, and then evaluate
both replicate-specific actions on the same resampled target_model rows.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from dtrm.phase3_mm0_state import materialize_mm0_information_state
from dtrm.phase3_mm1_optimizer import optimize_mm1


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"
REPORTS = REPO_ROOT / "research" / "reports"

DECISION_MANIFEST_PATH = (
    REPO_ROOT / "research" / "contracts" / "DTRM_PHASE3_MM1_V5_DECISION_MANIFEST.json"
)
POINT_RESULT_PATH = REPORTS / "DTRM_PHASE3_MM1_V5_REALIZED_RESULT.json"
SIGNALS_PATH = LOCAL_DATA / "phase3_mm1_v5_signals_frozen.pkl"
TARGET_PATH = LOCAL_DATA / "phase3_mm1_v5_target_model.pkl"

OUTPUT_SUMMARY = REPORTS / "DTRM_PHASE3_MM1_V5_PRIMARY_BOOTSTRAP.json"
OUTPUT_DISTRIBUTIONS = LOCAL_DATA / "phase3_mm1_v5_primary_bootstrap_distributions.npz"

REPLICATES = 10_000
SEED = 20260827
TOPK_FRACTION = 0.10
CONFIDENCE_LEVEL = 0.95


REQUIRED_SIGNAL_COLUMNS = (
    "news_id",
    "ticker",
    "date_dt",
    "baseline_point_score",
    "raw_p10",
)
REQUIRED_TARGET_COLUMNS = (
    "news_id",
    "ticker",
    "date_dt",
    "target_model",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_clean_tracked_worktree() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    if status:
        raise RuntimeError("Tracked working tree must be clean before V5 primary bootstrap")


def require_committed_json(path: Path, *, expected_status: str | None = None) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    relative = str(path.relative_to(REPO_ROOT))
    try:
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"],
            cwd=REPO_ROOT,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Required bootstrap provenance is not committed: {relative}") from exc

    local = path.read_bytes()
    if committed != local:
        raise RuntimeError(f"Local provenance differs from committed Git bytes: {relative}")

    payload = json.loads(local)
    if expected_status is not None and payload.get("status") != expected_status:
        raise RuntimeError(f"Unexpected provenance status in {relative}")
    return payload


def load_bootstrap_frame(decision_manifest: dict, point_result: dict) -> pd.DataFrame:
    expected_signals_sha = decision_manifest["frozen_signals"]["sha256"]
    expected_target_sha = point_result["target_artifact"]["sha256"]

    if not SIGNALS_PATH.exists() or sha256_file(SIGNALS_PATH) != expected_signals_sha:
        raise RuntimeError("Frozen V5 signal artifact does not match the decision manifest")
    if not TARGET_PATH.exists() or sha256_file(TARGET_PATH) != expected_target_sha:
        raise RuntimeError("Frozen V5 target artifact does not match the point result")

    signals = pd.read_pickle(SIGNALS_PATH)
    targets = pd.read_pickle(TARGET_PATH)

    missing_signals = set(REQUIRED_SIGNAL_COLUMNS) - set(signals.columns)
    missing_targets = set(REQUIRED_TARGET_COLUMNS) - set(targets.columns)
    if missing_signals:
        raise RuntimeError(f"V5 signals missing bootstrap columns: {sorted(missing_signals)}")
    if missing_targets:
        raise RuntimeError(f"V5 targets missing bootstrap columns: {sorted(missing_targets)}")

    if signals.duplicated(["news_id", "ticker"]).any():
        raise RuntimeError("Frozen V5 signals contain duplicate news_id/ticker keys")
    if targets.duplicated(["news_id", "ticker"]).any():
        raise RuntimeError("Frozen V5 targets contain duplicate news_id/ticker keys")

    frame = signals.merge(
        targets[["news_id", "ticker", "date_dt", "target_model"]],
        on=["news_id", "ticker"],
        how="inner",
        validate="one_to_one",
        sort=False,
        suffixes=("_signal", "_target"),
    )

    if len(frame) != len(signals) or len(frame) != len(targets):
        raise RuntimeError("V5 bootstrap signal/target merge is not one-to-one complete")

    signal_dates = pd.to_datetime(frame["date_dt_signal"], utc=True)
    target_dates = pd.to_datetime(frame["date_dt_target"], utc=True)
    if not signal_dates.equals(target_dates):
        raise RuntimeError("V5 bootstrap signal and target dates differ")

    numeric_columns = ("baseline_point_score", "raw_p10", "target_model")
    for column in numeric_columns:
        if not np.isfinite(frame[column].to_numpy(dtype=np.float64)).all():
            raise RuntimeError(f"V5 bootstrap column contains non-finite values: {column}")

    expected_rows = int(decision_manifest["cohort_structure"]["rows"])
    if len(frame) != expected_rows:
        raise RuntimeError("V5 bootstrap row count differs from decision manifest")

    return frame.reset_index(drop=True)


def _identity_lookup(frame: pd.DataFrame) -> dict[tuple[str, str, str], int]:
    keys = [
        (
            str(row.news_id),
            str(row.ticker),
            pd.Timestamp(row.date_dt_signal).isoformat(),
        )
        for row in frame.itertuples(index=False)
    ]
    if len(keys) != len(set(keys)):
        raise RuntimeError("V5 bootstrap frame identities are not unique")
    return {key: position for position, key in enumerate(keys)}


def _identity_positions(
    frame: pd.DataFrame,
    identities: list[dict],
    *,
    k: int,
) -> np.ndarray:
    lookup = _identity_lookup(frame)
    requested = [
        (
            str(item["news_id"]),
            str(item["ticker"]),
            pd.Timestamp(item["date_dt"]).isoformat(),
        )
        for item in identities
    ]
    if len(requested) != k or len(set(requested)) != k:
        raise RuntimeError("Frozen V5 action identities do not contain exactly K unique rows")
    try:
        return np.asarray([lookup[key] for key in requested], dtype=np.int64)
    except KeyError as exc:
        raise RuntimeError(f"Frozen V5 action identity absent from bootstrap frame: {exc}") from exc


def reproduce_frozen_point(frame: pd.DataFrame, decision_manifest: dict) -> dict[str, float]:
    k = int(decision_manifest["cohort_structure"]["K_H"])
    decision = decision_manifest["decision"]
    target = frame["target_model"].to_numpy(dtype=np.float64)

    phase2 = _identity_positions(
        frame,
        decision["phase2_champion_row_identities"],
        k=k,
    )
    mm1 = _identity_positions(
        frame,
        decision["MM1_selected_row_identities"],
        k=k,
    )

    phase2_values = target[phase2]
    mm1_values = target[mm1]
    return {
        "phase2_value": float(np.mean(phase2_values)),
        "MM1_value": float(np.mean(mm1_values)),
        "delta_topk_mean_target_model_vs_phase2": float(
            np.mean(mm1_values) - np.mean(phase2_values)
        ),
        "phase2_hit_rate": float(np.mean(phase2_values > 0.0)),
        "MM1_hit_rate": float(np.mean(mm1_values > 0.0)),
        "delta_topk_hit_rate": float(
            np.mean(mm1_values > 0.0) - np.mean(phase2_values > 0.0)
        ),
    }


def resampled_row_indices(
    cluster_codes: np.ndarray,
    *,
    n_clusters: int,
    rng: np.random.Generator,
) -> np.ndarray:
    draws = rng.integers(0, n_clusters, size=n_clusters)
    counts = np.bincount(draws, minlength=n_clusters)
    row_multiplicity = counts[np.asarray(cluster_codes, dtype=np.int64)]
    return np.repeat(np.arange(cluster_codes.size, dtype=np.int64), row_multiplicity)


def evaluate_resampled_policy(
    frame: pd.DataFrame,
    resampled_idx: np.ndarray,
) -> dict[str, float | int] | None:
    idx = np.asarray(resampled_idx, dtype=np.int64)
    if idx.ndim != 1 or idx.size == 0:
        raise ValueError("Bootstrap replicate indices must be a non-empty vector")

    resampled = frame.iloc[idx].reset_index(drop=True)
    n = len(resampled)
    k = int(n * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("Bootstrap replicate Top-K is empty")

    state = materialize_mm0_information_state(
        news_id=resampled["news_id"].to_numpy(),
        ticker=resampled["ticker"].to_numpy(),
        date_dt=resampled["date_dt_signal"].to_numpy(),
        baseline_point_score=resampled["baseline_point_score"].to_numpy(dtype=np.float64),
        raw_p10=resampled["raw_p10"].to_numpy(dtype=np.float64),
    )

    try:
        optimization = optimize_mm1(state)
    except ValueError as exc:
        if "eligible pool cannot fill" in str(exc):
            return None
        raise

    if optimization.k != k:
        raise RuntimeError("Bootstrap MM1 optimizer returned a K inconsistent with the replicate")
    if optimization.selected_indices.size != k or optimization.champion_indices.size != k:
        return None

    target = resampled["target_model"].to_numpy(dtype=np.float64)
    phase2_values = target[np.asarray(optimization.champion_indices, dtype=np.int64)]
    mm1_values = target[np.asarray(optimization.selected_indices, dtype=np.int64)]

    return {
        "rows": n,
        "K_H": k,
        "phase2_value": float(np.mean(phase2_values)),
        "MM1_value": float(np.mean(mm1_values)),
        "delta_topk_mean_target_model_vs_phase2": float(
            np.mean(mm1_values) - np.mean(phase2_values)
        ),
        "phase2_hit_rate": float(np.mean(phase2_values > 0.0)),
        "MM1_hit_rate": float(np.mean(mm1_values > 0.0)),
        "delta_topk_hit_rate": float(
            np.mean(mm1_values > 0.0) - np.mean(phase2_values > 0.0)
        ),
    }


def cluster_bootstrap(
    frame: pd.DataFrame,
    *,
    rng: np.random.Generator,
    replicates: int = REPLICATES,
) -> tuple[np.ndarray, np.ndarray, int]:
    if replicates <= 0:
        raise ValueError("replicates must be positive")

    cluster_codes, cluster_labels = pd.factorize(frame["news_id"], sort=False)
    n_clusters = int(len(cluster_labels))
    if n_clusters <= 0:
        raise ValueError("V5 bootstrap requires at least one news_id cluster")

    delta_mean = np.full(replicates, np.nan, dtype=np.float64)
    delta_hit = np.full(replicates, np.nan, dtype=np.float64)
    infeasible = 0

    for replicate in range(replicates):
        idx = resampled_row_indices(
            cluster_codes,
            n_clusters=n_clusters,
            rng=rng,
        )
        result = evaluate_resampled_policy(frame, idx)
        if result is None:
            infeasible += 1
        else:
            delta_mean[replicate] = float(
                result["delta_topk_mean_target_model_vs_phase2"]
            )
            delta_hit[replicate] = float(result["delta_topk_hit_rate"])

        if replicates == REPLICATES and (replicate + 1) % 1000 == 0:
            print(f"bootstrap {replicate + 1}/{REPLICATES}", flush=True)

    return delta_mean, delta_hit, infeasible


def percentile_interval(values: np.ndarray) -> list[float]:
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("Percentile interval requires a finite non-empty vector")
    return [
        float(np.quantile(values, 0.025, method="linear")),
        float(np.quantile(values, 0.975, method="linear")),
    ]


def require_outputs_absent() -> None:
    existing = [path for path in (OUTPUT_SUMMARY, OUTPUT_DISTRIBUTIONS) if path.exists()]
    if existing:
        raise RuntimeError(
            "V5 primary bootstrap refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def main() -> None:
    require_outputs_absent()
    require_clean_tracked_worktree()

    decision_manifest = require_committed_json(
        DECISION_MANIFEST_PATH,
        expected_status="decision_frozen_pending_git_commit",
    )
    point_result = require_committed_json(
        POINT_RESULT_PATH,
        expected_status="realized_point_evaluation_complete_pending_commit",
    )

    if point_result["decision_manifest"]["sha256"] != sha256_file(DECISION_MANIFEST_PATH):
        raise RuntimeError("V5 point result is bound to a different decision manifest")
    if point_result["point_evaluation"]["classification"] != "PROMOTED_POINT":
        raise RuntimeError("V5 primary bootstrap expected the already-frozen point classification")

    frame = load_bootstrap_frame(decision_manifest, point_result)
    point = reproduce_frozen_point(frame, decision_manifest)

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
            raise RuntimeError(f"Frozen V5 point result does not reproduce before bootstrap: {key}")

    print("DTRM PHASE 3 MM1 V5 PRIMARY NEWS_ID BOOTSTRAP")
    print("point result reproduction: PASS")
    print("rows:", len(frame))
    print("news_id clusters:", frame["news_id"].nunique())
    print("replicates:", REPLICATES)
    print("seed:", SEED)

    rng = np.random.default_rng(SEED)
    delta_mean, delta_hit, infeasible = cluster_bootstrap(frame, rng=rng)

    REPORTS.mkdir(parents=True, exist_ok=True)
    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUTPUT_DISTRIBUTIONS,
        delta_topk_mean_target_model_vs_phase2=delta_mean,
        delta_topk_hit_rate=delta_hit,
    )
    distributions_sha = sha256_file(OUTPUT_DISTRIBUTIONS)

    if infeasible == 0:
        mean_ci = percentile_interval(delta_mean)
        hit_ci = percentile_interval(delta_hit)
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
