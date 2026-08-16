"""Legacy Top-K model-iteration selection."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TopKResult:
    iteration: int
    topk_mean: float
    topk_hit_rate: float


def topk_metrics(
    y_true,
    y_pred,
    fraction: float = 0.10,
) -> tuple[float, float]:
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

    if not 0.0 < fraction <= 1.0:
        raise ValueError(
            "fraction must be in the interval (0, 1]."
        )

    k = max(1, int(len(y) * fraction))

    order = np.argsort(-pred)
    selected = y[order[:k]]

    return (
        float(np.mean(selected)),
        float(np.mean(selected > 0)),
    )


def select_topk_iteration(
    evaluations,
) -> TopKResult:
    """
    Select the legacy iteration.

    evaluations is an iterable of:
        (iteration, topk_mean, topk_hit_rate)

    Primary criterion: maximum Top-K mean.
    Tie-breaker: maximum Top-K hit rate.
    """

    best = None

    for iteration, mean, hit_rate in evaluations:
        candidate = TopKResult(
            iteration=int(iteration),
            topk_mean=float(mean),
            topk_hit_rate=float(hit_rate),
        )

        if (
            best is None
            or candidate.topk_mean > best.topk_mean
            or (
                abs(
                    candidate.topk_mean
                    - best.topk_mean
                )
                < 1e-12
                and candidate.topk_hit_rate
                > best.topk_hit_rate
            )
        ):
            best = candidate

    if best is None:
        raise ValueError(
            "evaluations must not be empty."
        )

    return best
