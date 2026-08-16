"""Reproduce the historical DTRM legacy baseline end to end."""

from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

from dtrm.embedding_cache import (
    embeddings_for_news_ids,
    load_legacy_embedding_cache,
)
from dtrm.evaluation import regression_topk_metrics
from dtrm.feature_matrix import assemble_legacy_feature_matrix
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
    legacy_xgb_params,
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

def build_legacy_feature_matrix(
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

    return assemble_legacy_feature_matrix(
        embedding_matrix,
        text_matrix,
        ordered_rows["beta_pre"].to_numpy(),
        ordered_rows["ret_spy_evt"].to_numpy(),
    )

def prepare_training_data(
    ordered_rows: pd.DataFrame,
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
        ordered_rows.loc[
            train_mask,
            "ticker",
        ],
        ordered_rows.loc[
            train_mask,
            "excess_beta",
        ],
        ordered_rows.loc[
            valid_mask,
            "ticker",
        ],
        ordered_rows.loc[
            valid_mask,
            "excess_beta",
        ],
        ordered_rows.loc[
            test_mask,
            "ticker",
        ],
        ordered_rows.loc[
            test_mask,
            "excess_beta",
        ],
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

def train_legacy_model(
    X: np.ndarray,
    ordered_rows: pd.DataFrame,
    masks,
    targets,
    weights,
):
    dmatrices = {}

    for split in ("train", "valid", "test"):
        dmatrices[split] = xgb.DMatrix(
            X[masks[split]],
            label=targets[split],
            weight=weights[split],
        )

    history = {}

    model = xgb.train(
        legacy_xgb_params(),
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

    return model, dmatrices, history

def select_legacy_topk(
    model,
    dmatrices,
    targets,
):
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
        prediction = model.predict(
            dmatrices["valid"],
            iteration_range=(
                0,
                iteration + 1,
            ),
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

def evaluate_legacy_model(
    model,
    dmatrices,
    targets,
    selected_iteration: int,
):
    results = {}

    for split in ("valid", "test"):
        prediction = model.predict(
            dmatrices[split],
            iteration_range=(
                0,
                selected_iteration + 1,
            ),
        )

        results[split] = (
            regression_topk_metrics(
                targets[split],
                prediction,
                topk_fraction=LEGACY_TOPK_FRAC,
            )
        )

    return results

def main():
    _, ordered_rows = load_ordered_model_rows()

    X = build_legacy_feature_matrix(
        ordered_rows
    )

    masks, targets, weights = (
        prepare_training_data(
            ordered_rows
        )
    )

    model, dmatrices, history = (
        train_legacy_model(
            X,
            ordered_rows,
            masks,
            targets,
            weights,
        )
    )

    topk = select_legacy_topk(
        model,
        dmatrices,
        targets,
    )

    metrics = evaluate_legacy_model(
        model,
        dmatrices,
        targets,
        topk.iteration,
    )

    print()
    print("DTRM_BASELINE_LEGACY_V0")
    print(
        "best_rmse_iteration:",
        model.best_iteration,
    )
    print(
        "best_rmse_score:",
        model.best_score,
    )
    print(
        "selected_topk_iteration:",
        topk.iteration,
    )
    print(
        "selected_topk_mean:",
        topk.topk_mean,
    )
    print(
        "selected_topk_hit_rate:",
        topk.topk_hit_rate,
    )

    for split in ("valid", "test"):
        result = metrics[split]

        print()
        print(split.upper())
        print("rows:", result.rows)
        print("topk_rows:", result.topk_rows)
        print("rmse:", result.rmse)
        print("mae:", result.mae)
        print("r2:", result.r2)
        print(
            "mean_target:",
            result.mean_target,
        )
        print(
            "topk_mean:",
            result.topk_mean,
        )
        print(
            "hit_rate:",
            result.hit_rate,
        )
        print(
            "topk_hit_rate:",
            result.topk_hit_rate,
        )


if __name__ == "__main__":
    main()