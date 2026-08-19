"""Run the DTRM full-distribution probabilistic score experiment."""

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

from dtrm.embedding_cache import (
    embeddings_for_news_ids,
    load_legacy_embedding_cache,
)
from dtrm.evaluation import regression_topk_metrics
from dtrm.exante_target import forward_excess_beta_target
from dtrm.feature_matrix import assemble_exante_feature_matrix
from dtrm.legacy_model_rows import order_selected_legacy_rows
from dtrm.legacy_target_preprocessing import preprocess_legacy_targets
from dtrm.sample_weights import legacy_news_weights
from dtrm.text_features import legacy_text_feature_matrix
from dtrm.topk_selection import (
    select_topk_iteration,
    topk_metrics,
)
from dtrm.xgb_config import (
    LEGACY_EARLY_STOP_ROUNDS,
    LEGACY_NUM_BOOST_ROUND,
    LEGACY_TOPK_FRAC,
    LEGACY_TOPK_SCAN_STEP,
    quantile_xgb_params,
)


REPO_ROOT = Path(__file__).resolve().parents[2]

LOCAL_DATA = REPO_ROOT / "research" / "local_data"

OUTPUTS = (
    Path.home()
    / "Desktop"
    / "Play4Fun"
    / "PCDoMoney_Backend"
    / "Notebooks"
    / "Outputs"
)

PRICE_CACHE = OUTPUTS / "price_cache_fmp_pickle"

FULL_ROWS_PATH = (
    LOCAL_DATA
    / "legacy_pairs_enriched_2025-01-01_2026-05-01.pkl"
)

MODEL_ROWS_PATH = (
    LOCAL_DATA
    / "legacy_model_rows_2026-05-01.pkl"
)

NEWS_PATH = (
    OUTPUTS
    / "news_2025-01-01_2026-05-01.pkl"
)

EMBEDDING_DAT_PATH = (
    OUTPUTS
    / "news_emb_2025-01-01_2026-05-01.dat"
)

EMBEDDING_SHAPE_PATH = (
    OUTPUTS
    / "news_emb_shape_2025-01-01_2026-05-01.pkl"
)

EMBEDDING_INDEX_PATH = (
    OUTPUTS
    / "news_emb_index_2025-01-01_2026-05-01.pkl"
)

QUANTILES = {
    "p10": 0.10,
    "p50": 0.50,
    "p90": 0.90,
}

PROBABILISTIC_SCORE_WIDTH_PENALTY = 0.5

def load_exante_price_cache():
    """Load the fixed 2026-07-05 historical price snapshot."""

    prices = {}

    for path in PRICE_CACHE.glob("*_2026-07-05.pkl"):
        ticker = path.name.split("_", 1)[0]
        frame = pd.read_pickle(path)

        prices[ticker] = list(
            zip(
                frame["date"],
                frame["close"],
            )
        )

    return prices

def build_exante_raw_targets(
    ordered_rows: pd.DataFrame,
    prices,
) -> np.ndarray:
    """Construct forward excess-beta targets for all model rows."""

    spy_prices = prices["SPY"]

    targets = []

    for row in ordered_rows.itertuples(index=False):
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
                f"Missing ex-ante target for "
                f"{row.ticker} at {row.date_dt}"
            )

        targets.append(target)

    return np.asarray(targets, dtype=np.float64)

def load_ordered_model_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    full_rows = pd.read_pickle(FULL_ROWS_PATH)
    model_rows = pd.read_pickle(MODEL_ROWS_PATH)

    full_keys = list(
        zip(
            full_rows["news_id"],
            full_rows["ticker"],
        )
    )

    selected_keys = list(
        zip(
            model_rows["news_id"],
            model_rows["ticker"],
        )
    )

    order = order_selected_legacy_rows(
        full_rows["ticker"],
        full_rows["date_dt"],
        full_keys,
        selected_keys,
    )

    ordered_rows = (
        model_rows
        .iloc[order]
        .reset_index(drop=True)
    )

    return full_rows, ordered_rows

def build_exante_feature_matrix(
    ordered_rows: pd.DataFrame,
) -> np.ndarray:
    news = pd.read_pickle(NEWS_PATH)

    news_lookup = (
        news
        .set_index("news_id")["news_text"]
    )

    embeddings, news_index = (
        load_legacy_embedding_cache(
            EMBEDDING_DAT_PATH,
            EMBEDDING_SHAPE_PATH,
            EMBEDDING_INDEX_PATH,
        )
    )

    embedding_matrix = embeddings_for_news_ids(
        embeddings,
        news_index,
        ordered_rows["news_id"],
    )

    text_matrix = legacy_text_feature_matrix(
        ordered_rows["news_id"].map(
            news_lookup
        )
    )

    return assemble_exante_feature_matrix(
        embedding_matrix,
        text_matrix,
        ordered_rows["beta_pre"].to_numpy(),
    )

def prepare_training_data(
    ordered_rows: pd.DataFrame,
    raw_targets: np.ndarray
):
    train_mask = (
        ordered_rows["split"]
        .eq("train")
        .to_numpy()
    )

    valid_mask = (
        ordered_rows["split"]
        .eq("valid")
        .to_numpy()
    )

    test_mask = (
        ordered_rows["split"]
        .eq("test")
        .to_numpy()
    )

    targets = preprocess_legacy_targets(
        ordered_rows.loc[train_mask, "ticker"],
        raw_targets[train_mask],
        ordered_rows.loc[valid_mask, "ticker"],
        raw_targets[valid_mask],
        ordered_rows.loc[test_mask, "ticker"],
        raw_targets[test_mask],
)

    weights = {
        "train": legacy_news_weights(
            ordered_rows.loc[
                train_mask,
                "news_id",
            ]
        ),
        "valid": legacy_news_weights(
            ordered_rows.loc[
                valid_mask,
                "news_id",
            ]
        ),
        "test": legacy_news_weights(
            ordered_rows.loc[
                test_mask,
                "news_id",
            ]
        ),
    }

    masks = {
        "train": train_mask,
        "valid": valid_mask,
        "test": test_mask,
    }

    return masks, targets, weights

def build_dmatrices(
    X: np.ndarray,
    masks,
    targets,
    weights,
):
    """Build the shared train, validation and test matrices."""

    dmatrices = {}

    for split in ("train", "valid", "test"):
        dmatrices[split] = xgb.DMatrix(
            X[masks[split]],
            label=targets[split],
            weight=weights[split],
        )

    return dmatrices


def train_quantile_models(dmatrices):
    """Train one independent XGBoost model per quantile."""

    models = {}
    histories = {}

    for name, alpha in QUANTILES.items():
        history = {}

        print()
        print(
            f"TRAINING {name.upper()} "
            f"(alpha={alpha})"
        )

        model = xgb.train(
            quantile_xgb_params(alpha),
            dmatrices["train"],
            num_boost_round=LEGACY_NUM_BOOST_ROUND,
            evals=[
                (
                    dmatrices["train"],
                    "train",
                ),
                (
                    dmatrices["valid"],
                    "valid",
                ),
            ],
            early_stopping_rounds=(
                LEGACY_EARLY_STOP_ROUNDS
            ),
            evals_result=history,
            verbose_eval=50,
        )

        models[name] = model
        histories[name] = history

    return models, histories


def predict_at_iteration(
    model,
    dmatrix,
    iteration: int,
):
    """Predict using trees through the supplied iteration."""

    return model.predict(
        dmatrix,
        iteration_range=(
            0,
            int(iteration) + 1,
        ),
    )

def probabilistic_decision_score(
    predictions,
) -> np.ndarray:
    """
    Combine expected return and predictive uncertainty.

    score = P50 - 0.5 * (P90 - P10)
    """

    return (
        predictions["p50"]
        - PROBABILISTIC_SCORE_WIDTH_PENALTY
        * (
            predictions["p90"]
            - predictions["p10"]
        )
    )

def evaluate_probabilistic_score(
    models,
    dmatrices,
    targets,
):
    """Evaluate the fixed full-distribution score."""

    results = {}

    for split in ("valid", "test"):
        predictions = {}

        for name, model in models.items():
            iteration = (
                int(model.best_iteration)
                if model.best_iteration is not None
                else LEGACY_NUM_BOOST_ROUND - 1
            )

            predictions[name] = (
                predict_at_iteration(
                    model,
                    dmatrices[split],
                    iteration,
                )
            )

        score = probabilistic_decision_score(
            predictions
        )

        results[split] = (
            regression_topk_metrics(
                targets[split],
                score,
                topk_fraction=LEGACY_TOPK_FRAC,
            )
        )

    return results

def select_quantile_topk(
    model,
    dmatrices,
    targets,
):
    """Select the Top-K iteration for one quantile model."""

    max_iteration = (
        int(model.best_iteration)
        if model.best_iteration is not None
        else 200
    )

    max_iteration = max(
        20,
        max_iteration,
    )

    scan_iterations = list(
        range(
            0,
            max_iteration + 1,
            LEGACY_TOPK_SCAN_STEP,
        )
    )

    if scan_iterations[-1] != max_iteration:
        scan_iterations.append(
            max_iteration
        )

    evaluations = []

    for iteration in scan_iterations:
        prediction = predict_at_iteration(
            model,
            dmatrices["valid"],
            iteration,
        )

        mean, hit_rate = topk_metrics(
            targets["valid"],
            prediction,
            fraction=LEGACY_TOPK_FRAC,
        )

        evaluations.append(
            (
                iteration,
                mean,
                hit_rate,
            )
        )

    return select_topk_iteration(
        evaluations
    )


def pinball_loss(
    target: np.ndarray,
    prediction: np.ndarray,
    alpha: float,
    weights=None,
) -> float:
    """Return quantile pinball loss."""

    error = target - prediction

    loss = np.maximum(
        alpha * error,
        (alpha - 1.0) * error,
    )

    if weights is None:
        return float(np.mean(loss))

    return float(
        np.average(loss, weights=weights)
    )

def weighted_quantile(
    values: np.ndarray,
    weights: np.ndarray,
    quantile: float,
) -> float:
    """Return a weighted empirical quantile."""

    order = np.argsort(values)

    values = np.asarray(values)[order]
    weights = np.asarray(weights)[order]

    cumulative = np.cumsum(weights)
    cutoff = quantile * cumulative[-1]

    index = np.searchsorted(
        cumulative,
        cutoff,
        side="left",
    )

    return float(values[index])

def quantile_diagnostics(
    target: np.ndarray,
    predictions,
    weights,
):
    
    """Evaluate calibration and interval quality."""

    p10 = predictions["p10"]
    p50 = predictions["p50"]
    p90 = predictions["p90"]

    crossing = (
        (p10 > p50)
        | (p50 > p90)
    )

    inside_80 = (
        (target >= p10)
        & (target <= p90)
    )

    return {
        "pinball_p10": pinball_loss(
            target,
            p10,
            0.10,
        ),
        "pinball_p50": pinball_loss(
            target,
            p50,
            0.50,
        ),
        "pinball_p90": pinball_loss(
            target,
            p90,
            0.90,
        ),
        "coverage_p10": float(
            np.mean(target <= p10)
        ),
        "coverage_p50": float(
            np.mean(target <= p50)
        ),
        "coverage_p90": float(
            np.mean(target <= p90)
        ),
        "coverage_80_interval": float(
            np.mean(inside_80)
        ),
        "mean_interval_width": float(
            np.mean(p90 - p10)
        ),
        "crossing_rate": float(
            np.mean(crossing)
        ),
        "weighted_pinball_p10": pinball_loss(
            target, p10, 0.10, weights
        ),
        "weighted_pinball_p50": pinball_loss(
            target, p50, 0.50, weights
        ),
        "weighted_pinball_p90": pinball_loss(
            target, p90, 0.90, weights
        ),
        "weighted_coverage_p10": float(
            np.average(target <= p10, weights=weights)
        ),
        "weighted_coverage_p50": float(
            np.average(target <= p50, weights=weights)
        ),
        "weighted_coverage_p90": float(
            np.average(target <= p90, weights=weights)
        ),
        "weighted_coverage_80_interval": float(
            np.average(inside_80, weights=weights)
        ),
    }

def evaluate_probabilistic_models(
    models,
    dmatrices,
    targets,
    weights,
    selected_p10_iteration: int,
    selected_p50_iteration: int,
):
    """
    Evaluate both probabilistic quality and the preserved
    P50 Top-K decision methodology.
    """

    validation_predictions = {}

    for name, model in models.items():
        iteration = (
            int(model.best_iteration)
            if model.best_iteration is not None
            else LEGACY_NUM_BOOST_ROUND - 1
        )

        validation_predictions[name] = (
            predict_at_iteration(
                model,
                dmatrices["valid"],
                iteration,
            )
        )

    calibration_offsets = {}

    for name, alpha in QUANTILES.items():
        residual = (
            targets["valid"]
            - validation_predictions[name]
        )

        calibration_offsets[name] = (
            weighted_quantile(
                residual,
                weights["valid"],
                alpha,
            )
        )

    print()
    print("VALIDATION CALIBRATION OFFSETS")

    for name in ("p10", "p50", "p90"):
        print(
            name,
            calibration_offsets[name],
        )

    results = {}

    for split in ("train", "valid", "test"):
        quantile_predictions = {}

        for name, model in models.items():
            iteration = (
                int(model.best_iteration)
                if model.best_iteration is not None
                else LEGACY_NUM_BOOST_ROUND - 1
            )

            quantile_predictions[name] = (
                predict_at_iteration(
                    model,
                    dmatrices[split],
                    iteration,
                )
            )

        calibrated_predictions = {
            name: (
                prediction
                + calibration_offsets[name]
            )
            for name, prediction
            in quantile_predictions.items()
        }

        p10_decision_prediction = (
            predict_at_iteration(
                models["p10"],
                dmatrices[split],
                selected_p10_iteration,
            )
        )

        p50_decision_prediction = (
            predict_at_iteration(
                models["p50"],
                dmatrices[split],
                selected_p50_iteration,
            )
        )

        results[split] = {
            "decision": regression_topk_metrics(
                targets[split],
                p50_decision_prediction,
                topk_fraction=LEGACY_TOPK_FRAC,
            ),
            "probabilistic": quantile_diagnostics(
                targets[split],
                quantile_predictions,
                weights[split],
            ),
            "probabilistic_calibrated": (
                quantile_diagnostics(
                    targets[split],
                    calibrated_predictions,
                    weights[split],
                )
            ),
            "decision_p10": regression_topk_metrics(
                targets[split],
                p10_decision_prediction,
                topk_fraction=LEGACY_TOPK_FRAC,
            ),
        }

    return results


def main():
    _, ordered_rows = load_ordered_model_rows()

    prices = load_exante_price_cache()

    raw_targets = build_exante_raw_targets(
        ordered_rows,
        prices,
    )

    X = build_exante_feature_matrix(
        ordered_rows
    )

    masks, targets, weights = (
        prepare_training_data(
            ordered_rows,
            raw_targets,
        )
    )

    dmatrices = build_dmatrices(
        X,
        masks,
        targets,
        weights,
    )

    models, _histories = (
        train_quantile_models(
            dmatrices
        )
    )

    score_metrics = (
        evaluate_probabilistic_score(
            models,
            dmatrices,
            targets,
        )
    )

    p10_topk = select_quantile_topk(
    models["p10"],
    dmatrices,
    targets,
    )

    p50_topk = select_quantile_topk(
        models["p50"],
        dmatrices,
        targets,
    )

    metrics = evaluate_probabilistic_models(
        models,
        dmatrices,
        targets,
        weights,
        p10_topk.iteration,
        p50_topk.iteration,
    )

    print()
    print("DTRM_XGB_PROBABILISTIC_SCORE_V0")

    print()
    print(
        "probabilistic_score:",
        "p50 - 0.5 * (p90 - p10)",
    )

    for split in ("valid", "test"):
        result = score_metrics[split]

        print()
        print(
            f"{split.upper()} PROBABILISTIC SCORE"
        )
        print(
            "topk_mean:",
            result.topk_mean,
        )
        print(
            "topk_hit_rate:",
            result.topk_hit_rate,
        )

    for name in ("p10", "p50", "p90"):
        model = models[name]

        print()
        print(name.upper())
        print(
            "best_quantile_iteration:",
            model.best_iteration,
        )
        print(
            "best_quantile_score:",
            model.best_score,
        )

    print()
    print(
        "selected_p10_topk_iteration:",
        p10_topk.iteration,
    )
    print(
        "selected_p10_topk_mean:",
        p10_topk.topk_mean,
    )
    print(
        "selected_p10_topk_hit_rate:",
        p10_topk.topk_hit_rate,
    )

    print()
    print(
        "selected_p50_topk_iteration:",
        p50_topk.iteration,
    )
    print(
        "selected_p50_topk_mean:",
        p50_topk.topk_mean,
    )
    print(
        "selected_p50_topk_hit_rate:",
        p50_topk.topk_hit_rate,
    )

    for split in ("train", "valid", "test"):
        decision = (
            metrics[split]["decision"]
        )

        decision_p10 = (
            metrics[split]["decision_p10"]
        )

        probabilistic = (
            metrics[split]["probabilistic"]
        )

        calibrated = (
            metrics[split][
                "probabilistic_calibrated"
            ]
        )

        print()
        print(split.upper())

        print("rows:", decision.rows)
        print(
            "topk_rows:",
            decision.topk_rows,
        )

        print(
            "p50_rmse:",
            decision.rmse,
        )
        print(
            "p50_mae:",
            decision.mae,
        )
        print(
            "p50_r2:",
            decision.r2,
        )
        print(
            "mean_target:",
            decision.mean_target,
        )

        print(
            "p10_topk_mean:",
            decision_p10.topk_mean,
        )
        print(
            "p10_topk_hit_rate:",
            decision_p10.topk_hit_rate,
        )

        print(
            "p50_topk_mean:",
            decision.topk_mean,
        )
        print(
            "hit_rate:",
            decision.hit_rate,
        )
        print(
            "p50_topk_hit_rate:",
            decision.topk_hit_rate,
        )

        print(
            "pinball_p10:",
            probabilistic["pinball_p10"],
        )
        print(
            "pinball_p50:",
            probabilistic["pinball_p50"],
        )
        print(
            "pinball_p90:",
            probabilistic["pinball_p90"],
        )

        print(
            "coverage_p10:",
            probabilistic["coverage_p10"],
        )
        print(
            "coverage_p50:",
            probabilistic["coverage_p50"],
        )
        print(
            "coverage_p90:",
            probabilistic["coverage_p90"],
        )
        print(
            "coverage_80_interval:",
            probabilistic[
                "coverage_80_interval"
            ],
        )

        print(
            "weighted_pinball_p10:",
            probabilistic["weighted_pinball_p10"],
        )
        print(
            "weighted_pinball_p50:",
            probabilistic["weighted_pinball_p50"],
        )
        print(
            "weighted_pinball_p90:",
            probabilistic["weighted_pinball_p90"],
        )

        print(
            "weighted_coverage_p10:",
            probabilistic["weighted_coverage_p10"],
        )
        print(
            "weighted_coverage_p50:",
            probabilistic["weighted_coverage_p50"],
        )
        print(
            "weighted_coverage_p90:",
            probabilistic["weighted_coverage_p90"],
        )
        print(
            "weighted_coverage_80_interval:",
            probabilistic[
                "weighted_coverage_80_interval"
            ],
        )

        print(
            "mean_interval_width:",
            probabilistic[
                "mean_interval_width"
            ],
        )
        print(
            "crossing_rate:",
            probabilistic["crossing_rate"],
        )

        print(
            "calibrated_weighted_pinball_p10:",
            calibrated["weighted_pinball_p10"],
        )
        print(
            "calibrated_weighted_pinball_p50:",
            calibrated["weighted_pinball_p50"],
        )
        print(
            "calibrated_weighted_pinball_p90:",
            calibrated["weighted_pinball_p90"],
        )

        print(
            "calibrated_weighted_coverage_p10:",
            calibrated["weighted_coverage_p10"],
        )
        print(
            "calibrated_weighted_coverage_p50:",
            calibrated["weighted_coverage_p50"],
        )
        print(
            "calibrated_weighted_coverage_p90:",
            calibrated["weighted_coverage_p90"],
        )
        print(
            "calibrated_weighted_coverage_80_interval:",
            calibrated[
                "weighted_coverage_80_interval"
            ],
        )

        print(
            "calibrated_mean_interval_width:",
            calibrated["mean_interval_width"],
        )
        print(
            "calibrated_crossing_rate:",
            calibrated["crossing_rate"],
        )

if __name__ == "__main__":
    main()