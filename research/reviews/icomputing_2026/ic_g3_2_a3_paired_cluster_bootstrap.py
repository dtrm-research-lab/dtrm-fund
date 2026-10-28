"""G3.2 A3 paired old-cohort three-arm cluster bootstrap — PURE ARRAY MATH.

This code cannot load any user files or authorize previously
consumed old forward targets. It can only receive arrays supplied
by a future separately consented SHA-bound runner.

Fixed original source N and P10 q25/risk V0 cutoffs are immutable.
For each news-id/ticker bootstrap draw, duplicate ALL original rows
from resampled clusters IN ORIGINAL row order, preserving float32
60-day forward excess-beta targets, then recompute common K=floor(.1*N)
and the ranker (baseline), original P10 q25, original volatility arms
on the SAME resampled rows. Never artificially backfill a veto arm.

If EITHER filtered arm fails to admit full Top-K on ANY of 10,000
draws, WITHHOLD ALL three paired policy difference intervals
(mean AND hit) for the entire cluster scheme and disclose the exact
infeasible draw count; never condition on only successful draws.

All resulting 95% percentile CIs are unadjusted retrospective
post-outcome exploratory, with no certified original pre-event
vendor quote vintages, independent new 60d holdout or realized P&L.
"""
from __future__ import annotations
import numpy as np
from ic_g2_g3_exploratory_core import (
    select_topk,ScientificGateError,SEEDS,N_BOOTSTRAP
)
from ic_g3_2_a3_three_arm_pure_points import EXPECTED,K_FRACTION

NAMES=("p10_minus_risk","p10_minus_baseline","risk_minus_baseline")

def _require(condition,message):
    if not condition:
        raise ScientificGateError(message)

def _clusters(values):
    seen={}
    ids=np.asarray(values,dtype=object)
    code=np.empty(len(ids),dtype=np.int64)
    for i,v in enumerate(ids):
        _require(v is not None and v==v,"Null original cluster ID")
        if v not in seen:seen[v]=len(seen)
        code[i]=seen[v]
    return code,len(seen)

def original_paired_a3_cluster_bootstrap(cohort,pred,target,p10_mask,risk_mask,
                                        clusters,*,scheme,
                                        replicates=N_BOOTSTRAP):
    """All-arm paired percentile intervals; no original-source I/O.

    Return six 95% CIs (mean/hit × 3 comparisons) or withhold
    all six whenever any sampled K cannot fill either veto.
    """
    _require(cohort in EXPECTED,"Original V2/V3/V4 cohort only")
    _require(scheme in SEEDS,"Only frozen news_id/ticker cluster schemes")
    _require(type(replicates) is int and replicates==10000,
             "Fixed 10k original cluster resamples required")
    n=EXPECTED[cohort]
    p=np.asarray(pred,dtype=np.float64)
    y=np.asarray(target)
    a=np.asarray(p10_mask,dtype=bool)
    b=np.asarray(risk_mask,dtype=bool)
    grp=np.asarray(clusters,dtype=object)
    _require(len(p)==len(y)==len(a)==len(b)==len(grp)==n,
             "A3 paired cluster sample N/key alignment drift")
    _require(y.dtype.kind=="f" and
             np.isfinite(y).all() and np.isfinite(p).all(),
             "Invalid original old forward target/prediction")
    code,c=_clusters(grp)
    _require(c>=1,"No cluster groups")
    original_p=select_topk(p,y,a,K_FRACTION)
    original_v=select_topk(p,y,b,K_FRACTION)
    _require(original_p.feasible and original_v.feasible,
             "Original A3 three-arm sample cannot fill K")
    rng=np.random.default_rng(SEEDS[scheme])
    rows=np.arange(n)
    collected={
      "p10_minus_risk":{"mean":[],"hit":[]},
      "p10_minus_baseline":{"mean":[],"hit":[]},
      "risk_minus_baseline":{"mean":[],"hit":[]},
    }
    bad=0
    for _ in range(replicates):
        draws=rng.integers(0,c,size=c)
        weight=np.bincount(draws,minlength=c)
        # Same historic G3.1 resampling method, retains original
        # individual row order while duplicating whole clusters.
        ix=np.repeat(rows,weight[code])
        if not len(ix) or int(len(ix)*K_FRACTION)<1:
            bad+=1;continue
        xp=p[ix];yp=y[ix];ap=a[ix];bp=b[ix]
        pv=select_topk(xp,yp,ap,K_FRACTION)
        rv=select_topk(xp,yp,bp,K_FRACTION)
        if not(pv.feasible and rv.feasible):
            bad+=1;continue
        # Both candidate arms share the same baseline top-K selection.
        _require(pv.k==rv.k and
                 pv.baseline_mean==rv.baseline_mean and
                 pv.baseline_hit_rate==rv.baseline_hit_rate,
                 "A3 bootstrap paired baseline/ranker drift")
        for name,dm,dh in (
             ("p10_minus_risk",
              pv.candidate_mean-rv.candidate_mean,
              pv.candidate_hit_rate-rv.candidate_hit_rate),
             ("p10_minus_baseline",pv.delta_mean,pv.delta_hit_rate),
             ("risk_minus_baseline",rv.delta_mean,rv.delta_hit_rate)):
            collected[name]["mean"].append(dm)
            collected[name]["hit"].append(dh)
    def ci(values):
        return [float(np.quantile(values,.025,method="linear")),
                float(np.quantile(values,.975,method="linear"))]
    result={
      "method":"PAIRED_COMMON_CLUSTER_ROWS_ALL_THREE_ARMS",
      "scheme":scheme,
      "seed":SEEDS[scheme],
      "replicates":replicates,
      "original_rows":n,
      "unique_cluster_count":c,
      "infeasible_replicates":bad,
      "feasible_replicates":replicates-bad,
      "full_K_recomputed_each_draw":True,
      "infeasible_any_arm_withholds_all_intervals":True,
      "source_float_dtype_preserved":str(y.dtype),
      "comparison_intervals":{},
      "inferential_status":"RETROSPECTIVE_UNADJUSTED_NOT_INDEPENDENT_CONFIRMATION",
      "provider_price_vintage_verified":False,
      "tradable_realized_pnl":False,
    }
    for name in NAMES:
        result["comparison_intervals"][name]={
          "ci95_delta_mean":None if bad else ci(collected[name]["mean"]),
          "ci95_delta_hit_rate":None if bad else ci(collected[name]["hit"]),
        }
    return result
