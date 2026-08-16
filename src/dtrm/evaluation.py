"""Evaluation metrics used by the DTRM legacy baseline."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EvaluationMetrics:
    rows: int
    topk_rows: int
    rmse: float
    mae: float
    r2: float
    mean_target: float
    topk_mean: float
    hit_rate: float
    topk_hit_rate: float


def regression_topk_metrics(
    y_true,
    y_pred,
    topk_fraction: float = 0.10,
) -> EvaluationMetrics:
    y = np.asarray(y_true)
    pred = np.asarray(y_pred)

    if y.shape != pred.shape:
        raise ValueError(
            "y_true and y_pred must have the same shape."
        )

    if y.ndim != 1:
        raise ValueError(
            "y_true and y_pred must be one-dimensional."
        )

    if len(y) == 0:
        raise ValueError(
            "y_true and y_pred must not be empty."
        )

    if not 0.0 < topk_fraction <= 1.0:
        raise ValueError(
            "topk_fraction must be in the interval (0, 1]."
        )

    error = y - pred

    rmse = float(
        np.sqrt(np.mean(error ** 2))
    )

    mae = float(
        np.mean(np.abs(error))
    )

    ss_res = float(
        np.sum(error ** 2)
    )

    ss_tot = float(
        np.sum(
            (y - np.mean(y)) ** 2
        )
    )

    r2 = (
        1.0 - ss_res / ss_tot
        if ss_tot != 0.0
        else float("nan")
    )

    k = max(
        1,
        int(len(y) * topk_fraction),
    )

    order = np.argsort(-pred)
    selected = y[order[:k]]

    return EvaluationMetrics(
        rows=len(y),
        topk_rows=k,
        rmse=rmse,
        mae=mae,
        r2=r2,
        mean_target=float(np.mean(y)),
        topk_mean=float(np.mean(selected)),
        hit_rate=float(np.mean(y > 0)),
        topk_hit_rate=float(
            np.mean(selected > 0)
        ),
    )