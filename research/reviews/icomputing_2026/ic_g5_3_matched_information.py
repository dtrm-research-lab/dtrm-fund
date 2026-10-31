"""G5.3 information-matched hard veto vs soft risk re-ranking; PURE MATH ONLY.

No original sources, target access, IO, fitting on heldout, trades, or new research
authorization. V2/V3/V4 outcomes were seen, so new comparisons are exploratory.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

class GateFailure(ValueError):
    """Fail closed without silently choosing a new rule/soft weight."""

@dataclass(frozen=True)
class InformationMatchedPlan:
    signal_name: str
    risk_direction: int
    cutoff: float
    point_iqr: float
    signal_iqr: float
    multiplier: float = 1.0

    @property
    def coefficient(self) -> float:
        return self.multiplier * self.point_iqr / self.signal_iqr

def _finite_vector(x, name):
    a = np.asarray(x, dtype=np.float64)
    if a.ndim != 1 or len(a) < 2 or not np.isfinite(a).all():
        raise GateFailure(f"{name}: finite 1d vector with >=2 elements required")
    return a

def calibrate_on_validation(*, name: str, point_validation,
                            risk_validation, frozen_cutoff: float,
                            direction: int, multiplier: float = 1.0):
    """Only ORIGINAL V0 validation score distributions. No outcomes used."""
    a = _finite_vector(point_validation, "point_validation")
    b = _finite_vector(risk_validation, "risk_validation")
    if len(a) != len(b) or direction not in (1, -1):
        raise GateFailure("Unmatched validation rows or signal direction")
    if name not in ("p10_calibrated", "trailing_volatility"):
        raise GateFailure("Risk signal not frozen")
    if (name == "p10_calibrated" and direction != 1) or (
            name == "trailing_volatility" and direction != -1):
        raise GateFailure("Risk orientation mismatch")
    if not np.isfinite(frozen_cutoff) or multiplier != 1.0:
        raise GateFailure("Nonfinite frozen cutoff or posthoc multiplier")
    pq = np.quantile(a, [.25, .75])
    rq = np.quantile(b, [.25, .75])
    p_iqr = float(pq[1] - pq[0])
    r_iqr = float(rq[1] - rq[0])
    if p_iqr <= 0 or r_iqr <= 0:
        raise GateFailure("Degenerate validation risk/point scale; no fallback")
    return InformationMatchedPlan(name, direction, float(frozen_cutoff),
                                  p_iqr, r_iqr, 1.0)

def chosen_indices(point, risk, plan: InformationMatchedPlan,
                   *, fraction: float = .10):
    """Same continuous risk signal, same point ranker, same K, different policy.

    This selector NEVER receives old target labels. Original frozen code sorts
    with np.argsort(-pred); soft sorting uses same tie semantics.
    """
    a = _finite_vector(point, "point")
    b = _finite_vector(risk, "risk")
    if len(a) != len(b) or not 0 < fraction <= 1:
        raise GateFailure("Mismatched original cohort or invalid capacity")
    if (plan.signal_name, plan.risk_direction) not in (
            ("p10_calibrated", 1), ("trailing_volatility", -1)):
        raise GateFailure("Invalid policy risk direction")
    k = int(len(a) * fraction)
    if k < 1:
        raise GateFailure("Empty K; no implicit minimum")
    admitted = b >= plan.cutoff if plan.risk_direction == 1 else b <= plan.cutoff
    if np.count_nonzero(admitted) < k:
        raise GateFailure("Hard veto cannot fill K; no partial fill")
    base_order = np.argsort(-a)
    soft_order = np.argsort(-(a + plan.coefficient * plan.risk_direction * b))
    return {"n":len(a),"k":k,"admitted":int(np.count_nonzero(admitted)),
            "raw":base_order[:k],
            "hard":base_order[admitted[base_order]][:k],
            "soft":soft_order[:k]}

def evaluate_old_outcome_only_after_authorized_reader(selection, old_targets):
    """Label-only evaluator; CALLER must have separate SHA-pinned authorization.

    Output remains transformed original Y_model, NOT raw stock return or P&L.
    """
    y = np.asarray(old_targets)
    if (y.ndim != 1 or len(y) != selection["n"] or y.dtype.kind != "f"
            or not np.isfinite(y).all()):
        raise GateFailure("Original outcome dtype/shape drift")
    arms = {a:selection[a] for a in ("raw","hard","soft")}
    if any(len(ids)!=selection["k"] or len(set(ids.tolist()))!=selection["k"]
           for ids in arms.values()):
        raise GateFailure("Original distinct full-K selection drift")
    means = {a:float(np.mean(y[ids])) for a,ids in arms.items()}
    return {
        "status":"POST_OUTCOME_EXPLORATORY_TRANSFORMED_TARGET_ONLY",
        "mean_transformed_target":means,
        "hard_minus_soft":means["hard"]-means["soft"],
        "soft_minus_raw":means["soft"]-means["raw"],
        "hard_minus_raw":means["hard"]-means["raw"],
        "hard_soft_overlap":len(set(arms["hard"]) & set(arms["soft"])),
        "n":selection["n"],"k":selection["k"],
        "previously_consulted_outcomes":True,
        "human_authority_effect_tested":False,
        "independent_unused_60d_holdout":False,
        "realized_tradable_pnl":None}
