"""Deterministic Phase-3 MM0 action finalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from dtrm.phase3_mm0_state import MM0InformationState


TOPK_FRACTION = 0.10


@dataclass(frozen=True)
class MM0ActionSelection:
    """Frozen full-K selection produced by an admissible MM0 veto mask."""

    selected_indices: np.ndarray
    k: int

    @property
    def rows(self) -> int:
        return int(self.selected_indices.size)


def _readonly_copy(values, *, dtype=None) -> np.ndarray:
    array = np.asarray(values, dtype=dtype).copy()
    array.setflags(write=False)
    return array


def phase2_champion_keep_mask(state: MM0InformationState) -> np.ndarray:
    """Return the no-additional-veto mask embedded in Binding B."""

    return _readonly_copy(state.phase2_guardrail_pass, dtype=bool)


def finalize_mm0_action(
    state: MM0InformationState,
    additional_keep_mask: Sequence[bool],
) -> MM0ActionSelection:
    """
    Finalize an admissible MM0 action using the frozen Phase-2 fill policy.

    The supplied mask may only remove rows that already pass the Phase-2
    guardrail. It cannot rescue a Phase-2-vetoed row, change the frozen
    ranking, or change the Top-K fraction. The selected set is therefore the
    first K retained rows in the frozen baseline ranking.
    """

    keep = np.asarray(additional_keep_mask)

    if keep.ndim != 1:
        raise ValueError("additional_keep_mask must be one-dimensional")

    if keep.size != state.rows:
        raise ValueError("additional_keep_mask must match MM0 state length")

    if keep.dtype.kind != "b":
        raise ValueError("additional_keep_mask must contain booleans")

    # Binding B dominance: Phase 3 may add vetoes, never rescue Phase-2 fails.
    if np.any(keep & ~state.phase2_guardrail_pass):
        raise ValueError("MM0 action cannot rescue a Phase-2-vetoed candidate")

    k = int(state.rows * TOPK_FRACTION)
    if k <= 0:
        raise ValueError("MM0 Top-K is empty for this cohort")

    if int(np.count_nonzero(keep)) < k:
        raise ValueError("MM0 action must leave enough candidates to fill Top-K")

    # baseline_rank is attached to original rows. Sorting it reconstructs the
    # exact frozen Phase-2 baseline order materialized by Adapter A.
    order = np.argsort(state.baseline_rank)
    retained_order = order[keep[order]]
    selected = retained_order[:k]

    if selected.size != k:
        raise RuntimeError("MM0 action finalization failed to fill Top-K")

    return MM0ActionSelection(
        selected_indices=_readonly_copy(selected, dtype=np.int64),
        k=k,
    )
