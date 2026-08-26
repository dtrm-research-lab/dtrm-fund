"""Calibrate the Phase-3 MM0 budget parameter rho on Phase-2 VALID only."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

from dtrm.exante_target import forward_excess_beta_target
from dtrm.legacy_target_preprocessing import preprocess_legacy_targets
from dtrm.sample_weights import legacy_news_weights
from dtrm.xgb_config import (
    LEGACY_EARLY_STOP_ROUNDS,
    LEGACY_NUM_BOOST_ROUND,
    legacy_xgb_params,
    quantile_xgb_params,
)

from run_exante_baseline_v0 import (
    build_exante_feature_matrix,
    load_exante_price_cache,
    load_ordered_model_rows,
)


EXPECTED_VALID_ROWS = 19_880
BASELINE_SELECTED_ITERATION = 10
EXPECTED_BASELINE_BEST_ITERATION = 6
P10_BEST_ITERATION = 18
P10_CALIBRATION_OFFSET = -0.06494169682264328
P10_THRESHOLD = -0.16665692627429962
TOPK_FRACTION = 0.10

REPLICATES = 10_000
SEED = 20260826
RHO_UPPER_QUANTILE = 0.95
EPS = 1e-12

OUTPUT = Path(
    "research/local_data/phase3_mm0_rho_calibration.json"
)


def build_raw_targets(rows: pd.DataFrame, prices) -> np.ndarray:
    spy_prices = prices["SPY"]
    result = []

    for row in rows.itertuples(index=False):
        target = forward_excess_beta_target(
            stock_prices=prices[row.ticker],
            market_prices=spy_prices,
            beta=float(row.beta_pre),
            event_date=row.date_dt,
            horizon_days=60,
            tolerance_days=5,
        )
        if target is None:
            raise ValueError(
                f"Missing target for {row.ticker} at {row.date_dt}"
            )
        result.append(target)

    return np.asarray(result, dtype=np.float64)


def weighted_quantile(
    values: np.ndarray,
    weights: np.ndarray,
    quantile: float,
) -> float:
    order = np.argsort(values)
    values = np.asarray(values)[order]
    weights = np.asarray(weights)[order]

    cumulative = np.cumsum(weights)
    cutoff = quantile * cumulative[-1]
    index = np.searchsorted(cumulative, cutoff, side="left")

    return float(values[index])


def prepare_reference_data():
    _, ordered_rows = load_ordered_model_rows()

    train_mask = ordered_rows["split"].eq("train").to_numpy()
    valid_mask = ordered_rows["split"].eq("valid").to_numpy()

    train_rows = ordered_rows.loc[train_mask].reset_index(drop=True)
    valid_rows = ordered_rows.loc[valid_mask].reset_index(drop=True)

    if len(valid_rows) != EXPECTED_VALID_ROWS:
        raise RuntimeError(
            f"VALID rows mismatch: {len(valid_rows)} != "
            f"{EXPECTED_VALID_ROWS}"
        )

    prices = load_exante_price_cache()

    train_raw = build_raw_targets(train_rows, prices)
    valid_raw = build_raw_targets(valid_rows, prices)

    targets = preprocess_legacy_targets(
        train_rows["ticker"],
        train_raw,
        valid_rows["ticker"],
        valid_raw,
        [],
        [],
    )

    train_weights = legacy_news_weights(train_rows["news_id"])
    valid_weights = legacy_news_weights(valid_rows["news_id"])

    X = build_exante_feature_matrix(ordered_rows)
    X_train = X[train_mask]
    X_valid = X[valid_mask]

    dtrain = xgb.DMatrix(
        X_train,
        label=targets["train"],
        weight=train_weights,
    )
    dvalid = xgb.DMatrix(
        X_valid,
        label=targets["valid"],
        weight=valid_weights,
    )

    return (
        valid_rows,
        targets["valid"],
        valid_weights,
        dtrain,
        dvalid,
    )


def train_frozen_models(dtrain, dvalid):
    baseline_history = {}
    baseline_model = xgb.train(
        legacy_xgb_params(),
        dtrain,
        num_boost_round=LEGACY_NUM_BOOST_ROUND,
        evals=[(dtrain, "train"), (dvalid, "valid")],
        early_stopping_rounds=LEGACY_EARLY_STOP_ROUNDS,
        evals_result=baseline_history,
        verbose_eval=False,
    )

    if int(baseline_model.best_iteration) != EXPECTED_BASELINE_BEST_ITERATION:
        raise RuntimeError(
            "Baseline reproduction failed: "
            f"best_iteration={baseline_model.best_iteration}"
        )

    p10_history = {}
    p10_model = xgb.train(
        quantile_xgb_params(0.10),
        dtrain,
        num_boost_round=LEGACY_NUM_BOOST_ROUND,
        evals=[(dtrain, "train"), (dvalid, "valid")],
        early_stopping_rounds=LEGACY_EARLY_STOP_ROUNDS,
        evals_result=p10_history,
        verbose_eval=False,
    )

    if int(p10_model.best_iteration) != P10_BEST_ITERATION:
        raise RuntimeError(
            "P10 reproduction failed: "
            f"best_iteration={p10_model.best_iteration}"
        )

    return baseline_model, p10_model


def reproduce_phase2_signals(
    baseline_model,
    p10_model,
    dvalid,
    target_valid: np.ndarray,
    valid_weights: np.ndarray,
):
    baseline = baseline_model.predict(
        dvalid,
        iteration_range=(0, BASELINE_SELECTED_ITERATION + 1),
    )

    p10_raw = p10_model.predict(
        dvalid,
        iteration_range=(0, P10_BEST_ITERATION + 1),
    )

    offset_reproduced = weighted_quantile(
        target_valid - p10_raw,
        valid_weights,
        0.10,
    )

    if not np.isclose(
        offset_reproduced,
        P10_CALIBRATION_OFFSET,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError(
            "P10 calibration offset reproduction failed: "
            f"{offset_reproduced} != {P10_CALIBRATION_OFFSET}"
        )

    calibrated_p10 = p10_raw + P10_CALIBRATION_OFFSET

    threshold_reproduced = weighted_quantile(
        calibrated_p10,
        valid_weights,
        0.25,
    )

    if not np.isclose(
        threshold_reproduced,
        P10_THRESHOLD,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError(
            "P10 threshold reproduction failed: "
            f"{threshold_reproduced} != {P10_THRESHOLD}"
        )

    p10_pass = calibrated_p10 >= P10_THRESHOLD

    return (
        baseline,
        calibrated_p10,
        p10_pass,
        offset_reproduced,
        threshold_reproduced,
    )


def observed_stress(
    baseline: np.ndarray,
    calibrated_p10: np.ndarray,
    target: np.ndarray,
):
    floor = np.minimum(baseline, calibrated_p10)
    width = baseline - floor

    z = np.zeros(len(target), dtype=np.float64)
    active = width > EPS

    z[active] = np.clip(
        (baseline[active] - target[active]) / width[active],
        0.0,
        1.0,
    )

    return floor, width, z


def phase2_champion_indices(
    baseline: np.ndarray,
    p10_pass: np.ndarray,
) -> np.ndarray | None:
    k = int(len(baseline) * TOPK_FRACTION)

    if k <= 0:
        raise ValueError("Top-K is empty")

    order = np.argsort(-baseline)
    passing_order = order[p10_pass[order]]

    if len(passing_order) < k:
        return None

    return passing_order[:k]


def stress_summary(
    selected_idx: np.ndarray,
    baseline: np.ndarray,
    floor: np.ndarray,
    width: np.ndarray,
    target: np.ndarray,
    z: np.ndarray,
) -> dict[str, float | int]:
    selected_width = width[selected_idx]
    selected_target = target[selected_idx]
    selected_floor = floor[selected_idx]
    selected_baseline = baseline[selected_idx]
    selected_z = z[selected_idx]

    return {
        "topk_rows": int(len(selected_idx)),
        "rho_point_estimate": float(np.mean(selected_z)),
        "positive_wedge_rate": float(
            np.mean(selected_width > EPS)
        ),
        "zero_width_rate": float(
            np.mean(selected_width <= EPS)
        ),
        "realized_below_floor_rate": float(
            np.mean(selected_target < selected_floor)
        ),
        "realized_above_nominal_rate": float(
            np.mean(selected_target >= selected_baseline)
        ),
        "full_stress_rate": float(
            np.mean(selected_z >= 1.0 - EPS)
        ),
        "zero_stress_rate": float(
            np.mean(selected_z <= EPS)
        ),
    }


def bootstrap_rho(
    valid_rows: pd.DataFrame,
    baseline: np.ndarray,
    p10_pass: np.ndarray,
    z_obs: np.ndarray,
) -> tuple[np.ndarray, int]:
    cluster_codes, cluster_labels = pd.factorize(
        valid_rows["news_id"],
        sort=False,
    )
    n_clusters = len(cluster_labels)
    row_index = np.arange(len(valid_rows))

    rng = np.random.default_rng(SEED)
    values = np.empty(REPLICATES, dtype=np.float64)
    infeasible = 0

    for replicate in range(REPLICATES):
        draws = rng.integers(
            0,
            n_clusters,
            size=n_clusters,
        )
        counts = np.bincount(
            draws,
            minlength=n_clusters,
        )
        multiplicity = counts[cluster_codes]
        idx = np.repeat(row_index, multiplicity)

        selected = phase2_champion_indices(
            baseline[idx],
            p10_pass[idx],
        )

        if selected is None:
            infeasible += 1
            values[replicate] = np.nan
        else:
            values[replicate] = float(
                np.mean(z_obs[idx][selected])
            )

        if (replicate + 1) % 1000 == 0:
            print(
                f"bootstrap {replicate + 1}/{REPLICATES}",
                flush=True,
            )

    return values, infeasible


def main() -> None:
    (
        valid_rows,
        target_valid,
        valid_weights,
        dtrain,
        dvalid,
    ) = prepare_reference_data()

    baseline_model, p10_model = train_frozen_models(
        dtrain,
        dvalid,
    )

    (
        baseline,
        calibrated_p10,
        p10_pass,
        offset_reproduced,
        threshold_reproduced,
    ) = reproduce_phase2_signals(
        baseline_model,
        p10_model,
        dvalid,
        target_valid,
        valid_weights,
    )

    selected = phase2_champion_indices(
        baseline,
        p10_pass,
    )
    if selected is None:
        raise RuntimeError(
            "Frozen Phase-2 guardrail cannot fill VALID Top-K"
        )

    floor, width, z_obs = observed_stress(
        baseline,
        calibrated_p10,
        target_valid,
    )

    point = stress_summary(
        selected,
        baseline,
        floor,
        width,
        target_valid,
        z_obs,
    )

    bootstrap, infeasible = bootstrap_rho(
        valid_rows,
        baseline,
        p10_pass,
        z_obs,
    )

    if infeasible != 0:
        raise RuntimeError(
            f"{infeasible} bootstrap replicates were infeasible"
        )

    if not np.isfinite(bootstrap).all():
        raise RuntimeError("Non-finite bootstrap rho values")

    rho_mm0 = float(
        np.quantile(
            bootstrap,
            RHO_UPPER_QUANTILE,
            method="linear",
        )
    )
    rho_mm0 = min(1.0, max(0.0, rho_mm0))

    result = {
        "contract": "DTRM_PHASE3_MM0_RHO_CALIBRATION",
        "reference_split": "phase2_validation_only",
        "validation_rows": int(len(valid_rows)),
        "validation_news_id_clusters": int(
            valid_rows["news_id"].nunique()
        ),
        "phase2_reproduction": {
            "baseline_best_iteration": int(
                baseline_model.best_iteration
            ),
            "p10_best_iteration": int(
                p10_model.best_iteration
            ),
            "p10_calibration_offset_reproduced": float(
                offset_reproduced
            ),
            "p10_threshold_reproduced": float(
                threshold_reproduced
            ),
            "guardrail_pass_rows": int(np.sum(p10_pass)),
            "guardrail_pass_rate": float(np.mean(p10_pass)),
        },
        "point": point,
        "bootstrap": {
            "method": "news_id_cluster_bootstrap",
            "replicates": REPLICATES,
            "seed": SEED,
            "infeasible_replicates": infeasible,
            "q025": float(
                np.quantile(bootstrap, 0.025, method="linear")
            ),
            "median": float(
                np.quantile(bootstrap, 0.50, method="linear")
            ),
            "q95_one_sided_upper": rho_mm0,
            "q975": float(
                np.quantile(bootstrap, 0.975, method="linear")
            ),
        },
        "rho_MM0": rho_mm0,
        "governance": {
            "primary_rule": "one_sided_95pct_upper_percentile",
            "phase3_holdout_used": False,
            "phase2_test_used": False,
            "V2_V3_V4_outcomes_used": False,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2) + "\n"
    )

    print()
    print("DTRM PHASE 3 MM0 RHO CALIBRATION")
    print("reproduction: PASS")
    print("VALID rows:", len(valid_rows))
    print("VALID news_id clusters:", valid_rows["news_id"].nunique())
    print("Phase-2 pass rows:", int(np.sum(p10_pass)))
    print("rho point:", point["rho_point_estimate"])
    print("rho q95 upper:", rho_mm0)
    print(
        "below-floor diagnostic:",
        point["realized_below_floor_rate"],
    )
    print("saved:", OUTPUT)


if __name__ == "__main__":
    main()
