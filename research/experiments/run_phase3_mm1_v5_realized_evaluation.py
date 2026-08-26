"""Evaluate the frozen Phase-3 MM1 V5 decision on realized targets.

This Stage-2 runner is intentionally non-optimizing. It requires the committed
ex-ante decision manifest and committed realized-price provenance, reconstructs
the frozen Phase-2 target_model semantics, and evaluates only the two exact-K
actions whose identities were frozen before outcome access.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from dtrm.exante_target import forward_excess_beta_target
from dtrm.legacy_target_preprocessing import preprocess_legacy_targets

from run_exante_baseline_v0 import load_exante_price_cache, load_ordered_model_rows
from run_phase3_mm0_rho_calibration import build_raw_targets


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA = REPO_ROOT / "research" / "local_data"
REPORTS = REPO_ROOT / "research" / "reports"

DECISION_MANIFEST_PATH = (
    REPO_ROOT / "research" / "contracts" / "DTRM_PHASE3_MM1_V5_DECISION_MANIFEST.json"
)
PRICE_PROVENANCE_PATH = (
    REPO_ROOT
    / "research"
    / "contracts"
    / "DTRM_PHASE3_MM1_V5_REALIZED_PRICE_PROVENANCE.json"
)
SIGNALS_PATH = LOCAL_DATA / "phase3_mm1_v5_signals_frozen.pkl"
CANDIDATE_ROWS_PATH = LOCAL_DATA / "phase3_mm1_v5_candidate_rows_exante.pkl"
FEATURES_PATH = LOCAL_DATA / "phase3_mm1_v5_features_exante.npy"
PRICE_SNAPSHOT_PATH = LOCAL_DATA / "phase3_mm1_v5_price_snapshot.pkl"
TARGET_OUTPUT = LOCAL_DATA / "phase3_mm1_v5_target_model.pkl"
RESULT_OUTPUT = REPORTS / "DTRM_PHASE3_MM1_V5_REALIZED_RESULT.json"

EXPECTED_FEATURE_COUNT = 390
BETA_FEATURE_INDEX = 389
ROBUST_VALUE_TOLERANCE = 1.0e-12


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
        raise RuntimeError("Tracked working tree must be clean before V5 realized evaluation")


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
        raise RuntimeError(f"Required evaluation provenance is not committed: {relative}") from exc

    local = path.read_bytes()
    if committed != local:
        raise RuntimeError(f"Local provenance differs from committed Git bytes: {relative}")

    payload = json.loads(local)
    if expected_status is not None and payload.get("status") != expected_status:
        raise RuntimeError(f"Unexpected provenance status in {relative}")
    return payload


def _require_hash(path: Path, expected: str, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 mismatch: {actual} != {expected}")


def load_frozen_inputs(decision_manifest: dict, price_provenance: dict):
    frozen_signals = decision_manifest["frozen_signals"]
    _require_hash(SIGNALS_PATH, frozen_signals["sha256"], "V5 signals")

    candidate_spec = decision_manifest["input_artifacts"]["candidate_rows"]
    feature_spec = decision_manifest["input_artifacts"]["features"]
    _require_hash(CANDIDATE_ROWS_PATH, candidate_spec["sha256"], "V5 candidate rows")
    _require_hash(FEATURES_PATH, feature_spec["sha256"], "V5 feature matrix")

    price_spec = price_provenance["price_snapshot"]
    _require_hash(PRICE_SNAPSHOT_PATH, price_spec["sha256"], "V5 price snapshot")

    signals = pd.read_pickle(SIGNALS_PATH).reset_index(drop=True)
    candidate_rows = pd.read_pickle(CANDIDATE_ROWS_PATH).reset_index(drop=True)
    features = np.load(FEATURES_PATH, allow_pickle=False)
    prices = pd.read_pickle(PRICE_SNAPSHOT_PATH)

    if len(signals) != int(decision_manifest["cohort_structure"]["rows"]):
        raise RuntimeError("V5 signals row count differs from decision manifest")
    if features.shape != (len(signals), EXPECTED_FEATURE_COUNT):
        raise RuntimeError("V5 feature matrix shape differs from frozen decision inputs")
    if not np.isfinite(features).all():
        raise RuntimeError("V5 feature matrix contains non-finite values")

    left = signals[["news_id", "ticker", "date_dt"]].copy()
    right = candidate_rows[["news_id", "ticker", "date_dt"]].copy()
    left["date_dt"] = pd.to_datetime(left["date_dt"], utc=True)
    right["date_dt"] = pd.to_datetime(right["date_dt"], utc=True)
    if not left.equals(right):
        raise RuntimeError("V5 feature-row identities no longer align with frozen signals")

    if prices.duplicated(["ticker", "date"]).any():
        raise RuntimeError("V5 price snapshot contains duplicate ticker/date rows")

    beta_pre = np.asarray(features[:, BETA_FEATURE_INDEX], dtype=np.float64)
    if not np.isfinite(beta_pre).all():
        raise RuntimeError("Frozen V5 beta_pre feature contains non-finite values")

    return signals, beta_pre, prices


def price_series_by_ticker(prices: pd.DataFrame) -> dict[str, list[tuple]]:
    frame = prices[["ticker", "date", "close"]].copy()
    frame["ticker"] = frame["ticker"].astype(str)
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.tz_localize(None)
    frame["close"] = pd.to_numeric(frame["close"], errors="raise")

    result: dict[str, list[tuple]] = {}
    for ticker, group in frame.groupby("ticker", sort=False):
        ordered = group.sort_values("date", kind="stable")
        result[str(ticker)] = list(zip(ordered["date"].dt.date, ordered["close"].astype(float)))
    return result


def build_v5_raw_targets(
    signals: pd.DataFrame,
    beta_pre: np.ndarray,
    prices: pd.DataFrame,
) -> np.ndarray:
    if len(signals) != len(beta_pre):
        raise ValueError("V5 signals and frozen beta_pre must have identical row counts")

    price_map = price_series_by_ticker(prices)
    if "SPY" not in price_map:
        raise RuntimeError("V5 price snapshot is missing SPY")

    spy_prices = price_map["SPY"]
    raw = np.empty(len(signals), dtype=np.float64)

    for position, row in enumerate(signals.itertuples(index=False)):
        ticker = str(row.ticker)
        if ticker not in price_map:
            raise RuntimeError(f"V5 price snapshot is missing {ticker}")

        # V5 news dates are date-level observations. Converting the frozen UTC
        # timestamp to its calendar date avoids mixing tz-aware event timestamps
        # with date-only FMP closes while preserving the frozen event day.
        event_date = pd.Timestamp(row.date_dt).date()
        target = forward_excess_beta_target(
            stock_prices=price_map[ticker],
            market_prices=spy_prices,
            beta=float(beta_pre[position]),
            event_date=event_date,
            horizon_days=60,
            tolerance_days=5,
        )
        if target is None or not np.isfinite(target):
            raise RuntimeError(
                "INFEASIBLE: incomplete frozen V5 target observability for "
                f"{row.news_id}/{ticker}/{event_date}"
            )
        raw[position] = float(target)

    return raw


def build_v5_target_model(signals: pd.DataFrame, raw_v5: np.ndarray) -> tuple[np.ndarray, dict]:
    """Apply the frozen Phase-2 TRAIN-only clipping and ticker de-meaning."""

    _, ordered_rows = load_ordered_model_rows()
    train_rows = ordered_rows.loc[ordered_rows["split"].eq("train")].reset_index(drop=True)
    historical_prices = load_exante_price_cache()
    train_raw = build_raw_targets(train_rows, historical_prices)

    processed = preprocess_legacy_targets(
        train_rows["ticker"],
        train_raw,
        [],
        [],
        signals["ticker"],
        raw_v5,
    )
    target_model = np.asarray(processed["test"], dtype=np.float32)
    if target_model.shape != (len(signals),) or not np.isfinite(target_model).all():
        raise RuntimeError("Frozen Phase-2 preprocessing produced invalid V5 target_model")

    metadata = {
        "clip_lower": float(processed["clip_lower"]),
        "clip_upper": float(processed["clip_upper"]),
        "train_ticker_means": int(len(processed["ticker_means"])),
        "unseen_V5_tickers": sorted(
            set(str(t) for t in signals["ticker"].unique()) - set(processed["ticker_means"])
        ),
    }
    return target_model, metadata


def identity_key(item: dict) -> tuple[str, str, str]:
    return (
        str(item["news_id"]),
        str(item["ticker"]),
        pd.Timestamp(item["date_dt"]).isoformat(),
    )


def selection_positions(signals: pd.DataFrame, identities: list[dict], *, k: int) -> np.ndarray:
    keys = [
        (str(row.news_id), str(row.ticker), pd.Timestamp(row.date_dt).isoformat())
        for row in signals.itertuples(index=False)
    ]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Frozen V5 signals are not unique by news_id/ticker/date")

    lookup = {key: position for position, key in enumerate(keys)}
    requested = [identity_key(item) for item in identities]
    if len(requested) != k or len(set(requested)) != k:
        raise RuntimeError("Frozen action identities do not contain exactly K unique rows")

    try:
        result = np.asarray([lookup[key] for key in requested], dtype=np.int64)
    except KeyError as exc:
        raise RuntimeError(f"Frozen action identity is absent from V5 signals: {exc}") from exc
    return result


def evaluate_frozen_actions(
    signals: pd.DataFrame,
    target_model: np.ndarray,
    decision_manifest: dict,
) -> dict:
    decision = decision_manifest["decision"]
    k = int(decision_manifest["cohort_structure"]["K_H"])

    phase2 = selection_positions(
        signals,
        decision["phase2_champion_row_identities"],
        k=k,
    )
    mm1 = selection_positions(
        signals,
        decision["MM1_selected_row_identities"],
        k=k,
    )

    same_action = np.array_equal(np.sort(phase2), np.sort(mm1))
    phase2_values = np.asarray(target_model[phase2], dtype=np.float64)
    mm1_values = np.asarray(target_model[mm1], dtype=np.float64)

    phase2_mean = float(np.mean(phase2_values))
    mm1_mean = float(np.mean(mm1_values))
    realized_delta = 0.0 if same_action else float(mm1_mean - phase2_mean)
    phase2_hit = float(np.mean(phase2_values > 0.0))
    mm1_hit = float(np.mean(mm1_values > 0.0))
    hit_delta = 0.0 if same_action else float(mm1_hit - phase2_hit)

    if same_action:
        classification = "NO_INCREMENTAL_ACTION"
        promoted = False
    else:
        if decision.get("intervention") is not True:
            raise RuntimeError("Frozen manifest actions differ but intervention is false")
        if float(decision.get("robust_lift", 0.0)) <= ROBUST_VALUE_TOLERANCE:
            raise RuntimeError("Frozen MM1 intervention lacks the required strict robust lift")
        if realized_delta > 0.0:
            classification = "PROMOTED_POINT"
            promoted = True
        else:
            classification = "NOT_PROMOTED_REALIZED"
            promoted = False

    return {
        "classification": classification,
        "promoted": promoted,
        "same_action": bool(same_action),
        "phase2_value": phase2_mean,
        "MM1_value": mm1_mean,
        "delta_topk_mean_target_model_vs_phase2": realized_delta,
        "phase2_hit_rate": phase2_hit,
        "MM1_hit_rate": mm1_hit,
        "delta_topk_hit_rate": hit_delta,
        "K_H": k,
    }


def require_outputs_absent() -> None:
    existing = [path for path in (TARGET_OUTPUT, RESULT_OUTPUT) if path.exists()]
    if existing:
        raise RuntimeError(
            "V5 realized evaluator refuses to overwrite existing outputs: "
            + ", ".join(str(path) for path in existing)
        )


def main() -> None:
    require_outputs_absent()
    require_clean_tracked_worktree()

    decision_manifest = require_committed_json(
        DECISION_MANIFEST_PATH,
        expected_status="decision_frozen_pending_git_commit",
    )
    price_provenance = require_committed_json(
        PRICE_PROVENANCE_PATH,
        expected_status="frozen_before_target_model_construction",
    )

    if price_provenance["decision_manifest"]["sha256"] != sha256_file(DECISION_MANIFEST_PATH):
        raise RuntimeError("Realized price provenance is bound to a different decision manifest")

    signals, beta_pre, prices = load_frozen_inputs(decision_manifest, price_provenance)
    raw_v5 = build_v5_raw_targets(signals, beta_pre, prices)
    target_model, preprocessing = build_v5_target_model(signals, raw_v5)

    target_frame = signals[["news_id", "ticker", "date_dt"]].copy()
    target_frame["beta_pre_frozen"] = beta_pre
    target_frame["raw_target"] = raw_v5
    target_frame["target_model"] = target_model

    LOCAL_DATA.mkdir(parents=True, exist_ok=True)
    target_frame.to_pickle(TARGET_OUTPUT)
    target_sha = sha256_file(TARGET_OUTPUT)

    evaluation = evaluate_frozen_actions(signals, target_model, decision_manifest)

    result = {
        "stage": "DTRM_PHASE3_MM1_V5_REALIZED_EVALUATION",
        "status": "realized_point_evaluation_complete_pending_commit",
        "decision_manifest": {
            "path": str(DECISION_MANIFEST_PATH.relative_to(REPO_ROOT)),
            "sha256": sha256_file(DECISION_MANIFEST_PATH),
        },
        "price_provenance": {
            "path": str(PRICE_PROVENANCE_PATH.relative_to(REPO_ROOT)),
            "sha256": sha256_file(PRICE_PROVENANCE_PATH),
            "price_snapshot_sha256": price_provenance["price_snapshot"]["sha256"],
        },
        "target_construction": {
            "formula": "stock_forward_return - beta_pre_frozen * SPY_forward_return",
            "horizon_days": 60,
            "price_tolerance_days": 5,
            "beta_source": "frozen V5 feature matrix column 389",
            "beta_precision": "float32 feature value promoted to float64 for arithmetic",
            "preprocessing": "frozen Phase2 TRAIN-only 1pct/99pct clipping plus TRAIN ticker de-meaning",
            **preprocessing,
        },
        "row_integrity": {
            "signal_rows": int(len(signals)),
            "target_rows": int(len(target_frame)),
            "complete_one_to_one": True,
            "rows_dropped_after_outcome_access": 0,
        },
        "target_artifact": {
            "path": str(TARGET_OUTPUT.relative_to(REPO_ROOT)),
            "sha256": target_sha,
        },
        "frozen_exante_diagnostics": {
            "robust_value_MM1": float(decision_manifest["decision"]["robust_value_MM1"]),
            "robust_value_phase2": float(decision_manifest["decision"]["robust_value_phase2"]),
            "robust_lift": float(decision_manifest["decision"]["robust_lift"]),
            "overlap_with_phase2": int(decision_manifest["decision"]["overlap_with_phase2"]),
            "intervention": bool(decision_manifest["decision"]["intervention"]),
            "solver_status": decision_manifest["decision"]["solver_status"],
        },
        "point_evaluation": evaluation,
        "bootstrap": {
            "primary_news_id": "pending_separate_preregistered_runner",
            "ticker_sensitivity": "pending_separate_preregistered_runner",
        },
        "governance": {
            "MM1_reoptimized_after_outcome_access": False,
            "rho_retuned": False,
            "threshold_retuned": False,
            "V2_V3_V4_MM1_realized_results_used": False,
            "V6_policy_change_permitted_from_V5": False,
        },
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    RESULT_OUTPUT.write_text(json.dumps(result, indent=2) + "\n")

    print("DTRM PHASE 3 MM1 V5 REALIZED EVALUATION")
    print("row integrity: PASS")
    print("rows:", len(target_frame))
    print("K_H:", evaluation["K_H"])
    print("Phase-2 realized value:", evaluation["phase2_value"])
    print("MM1 realized value:", evaluation["MM1_value"])
    print("realized delta:", evaluation["delta_topk_mean_target_model_vs_phase2"])
    print("Phase-2 hit rate:", evaluation["phase2_hit_rate"])
    print("MM1 hit rate:", evaluation["MM1_hit_rate"])
    print("hit-rate delta:", evaluation["delta_topk_hit_rate"])
    print("classification:", evaluation["classification"])
    print("promoted point:", evaluation["promoted"])
    print("target artifact:", TARGET_OUTPUT)
    print("target sha256:", target_sha)
    print("result:", RESULT_OUTPUT)
    print("NEXT REQUIRED ACTION: inspect and commit the point result before bootstrap.")


if __name__ == "__main__":
    main()
