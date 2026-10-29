"""PURE G5.4 audit: decompose original transformed-target policy effect.

Does not undo clipping, reconstruct stock returns, access original sources,
train/optimize models, trade or authorize historical outcome access.
"""
from __future__ import annotations
import numpy as np

class DecompositionError(ValueError):
    pass

def _v(xs, label):
    a=np.asarray(xs,dtype=np.float64)
    if a.ndim!=1 or not len(a) or not np.isfinite(a).all():
        raise DecompositionError(label+": invalid numeric vector")
    return a

def _check_idx(idx,n,k,name):
    a=np.asarray(idx)
    if a.ndim!=1 or len(a)!=k or a.dtype.kind not in "iu" or len(np.unique(a))!=k:
        raise DecompositionError(name+": nonunique/invalid Top-K index")
    if np.any(a<0) or np.any(a>=n):
        raise DecompositionError(name+": index outside original rows")
    return a

def decompose_same_target(policy_indices,base_indices,
                          transformed_y_model,train_center_by_row):
    """ΔY_model = Δ(clipped_original_beta_excess) − Δ(TRAIN ticker center).

    Original row order and TRAIN-only per-ticker means must be separately
    source-hash audited; never refit ticker centers on old holdout outcomes.
    Original raw return beyond clip bounds is NOT recoverable.
    """
    y=_v(transformed_y_model,"model target")
    mu=_v(train_center_by_row,"TRAIN ticker center")
    if len(y)!=len(mu):
        raise DecompositionError("Aligned target / original ticker center mismatch")
    k=len(base_indices)
    if not k:raise DecompositionError("Empty Top-K")
    b=_check_idx(base_indices,len(y),k,"baseline")
    p=_check_idx(policy_indices,len(y),k,"policy")
    clipped=y+mu
    dy=float(np.mean(y[p])-np.mean(y[b]))
    dclip=float(np.mean(clipped[p])-np.mean(clipped[b]))
    dcenter=float(np.mean(mu[p])-np.mean(mu[b]))
    residual=dy-(dclip-dcenter)
    if not np.isclose(residual,0.,atol=1e-9,rtol=1e-9):
        raise DecompositionError("Model target decomposition identity drift")
    return {
        "status":"ALGEBRAIC_CLIPPED_TARGET_DECOMPOSITION_ONLY",
        "n":len(y),"k":k,
        "transformed_model_target_delta":dy,
        "pre_centered_clipped_target_delta":dclip,
        "train_ticker_mean_composition_delta":dcenter,
        "identity_residual":residual,
        "raw_unclipped_stock_return_recovered":False,
        "realized_tradable_pnl":None,
        "old_outcome_access_authorized_by_this_module":False,
    }
