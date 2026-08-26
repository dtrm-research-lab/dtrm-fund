"""Deterministic materialization of the Phase-3 MM0 information state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


BASELINE_SELECTED_ITERATION = 10
P10_BEST_ITERATION = 18
P10_CALIBRATION_OFFSET = -0.06494169682264328
P10_GUARDRAIL_THRESHOLD = -0.16665692627429962


@dataclass(frozen=True)
class MM0InformationState:
    """Frozen candidate-level information available to MM0."""

    news_id: np.ndarray
    ticker: np.ndarray
    date_dt: np.ndarray
    baseline_point_score: np.ndarray
    baseline_rank: np.ndarray
    calibrated_p10: np.ndarray
    phase2_guardrail_pass: np.ndarray

    @property
    def rows(self) -> int:
        return int(self.baseline_point_score.size)


def _readonly_copy(values, *, dtype=None) -> np.ndarray:
    array = np.asarray(values, dtype=dtype).copy()
    array.setflags(write=False)
    return array


def _validate_one_dimensional(name: str, array: np.ndarray) -> None:
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")


def materialize_mm0_information_state(
    *,
    news_id: Sequence,
    ticker: Sequence,
    date_dt: Sequence,
    baseline_point_score: Sequence[float],
    raw_p10: Sequence[float],
) -> MM0InformationState:
    """
    Materialize the strict MM0 information state from frozen Phase-2 outputs.

    The function deliberately accepts raw P10 rather than an already-calibrated
    value so that the frozen Phase-2 calibration offset and veto threshold are
    applied in exactly one place.

    ``baseline_rank`` is zero-based and reproduces the Phase-2 ordering
    convention ``np.argsort(-baseline_point_score)``. A rank of 0 is the first
    row in the frozen baseline ranking.
    """

    news = np.asarray(news_id)
    tickers = np.asarray(ticker)
    dates = np.asarray(date_dt)
    baseline = np.asarray(baseline_point_score, dtype=np.float64)
    p10_raw = np.asarray(raw_p10, dtype=np.float64)

    arrays = {
        "news_id": news,
        "ticker": tickers,
        "date_dt": dates,
        "baseline_point_score": baseline,
        "raw_p10": p10_raw,
    }

    for name, array in arrays.items():
        _validate_one_dimensional(name, array)

    lengths = {array.size for array in arrays.values()}
    if len(lengths) != 1:
        raise ValueError("all MM0 state inputs must have the same length")

    rows = baseline.size
    if rows == 0:
        raise ValueError("MM0 state inputs must not be empty")

    if not np.isfinite(baseline).all():
        raise ValueError("baseline_point_score must contain only finite values")

    if not np.isfinite(p10_raw).all():
        raise ValueError("raw_p10 must contain only finite values")

    calibrated = p10_raw + P10_CALIBRATION_OFFSET
    guardrail_pass = calibrated >= P10_GUARDRAIL_THRESHOLD

    # Preserve the exact frozen Phase-2 ranking convention. We convert the
    # returned order into a zero-based rank attached to each original row.
    order = np.argsort(-baseline)
    rank = np.empty(rows, dtype=np.int64)
    rank[order] = np.arange(rows, dtype=np.int64)

    return MM0InformationState(
        news_id=_readonly_copy(news),
        ticker=_readonly_copy(tickers),
        date_dt=_readonly_copy(dates),
        baseline_point_score=_readonly_copy(baseline, dtype=np.float64),
        baseline_rank=_readonly_copy(rank, dtype=np.int64),
        calibrated_p10=_readonly_copy(calibrated, dtype=np.float64),
        phase2_guardrail_pass=_readonly_copy(guardrail_pass, dtype=bool),
    )
