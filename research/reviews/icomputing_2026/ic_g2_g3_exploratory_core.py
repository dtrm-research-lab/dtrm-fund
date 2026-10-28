"""Pure, audit-oriented primitives for ICOMPUTING-D-26-01069 G3.

COMMITTING THESE FUNCTIONS DOES NOT AUTHORIZE G3. There is intentionally
NO CLI, file I/O, Pickle deserialization, fitting or implicit execution.
Only after G2 science signoff and a separately verified entry-point may
a caller supply original old outcome arrays. All V2/V3/V4 results are
POST_OUTCOME_EXPLORATORY and MUST retain original negative/CI limitations.

Frozen source semantics: NumPy argsort(-prediction), floor(N*fraction),
news-id legacy weights, weighted quantile via argsort/cumsum/searchsorted
side='left', bootstrap cluster duplicated all rows with replacement.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from math import isfinite
from typing import Sequence
import numpy as np

CASE="ICOMPUTING-D-26-01069"
PIN="c7502a690162459cdfb3413573e3133c42efb126"
Q25_FROZEN=-0.16665692627429962
P10_OFFSET=-0.06494169682264328
P10_VALID_SIZE=19880
A2_PERCENTILES=(.15,.25,.35)
A6_FRACTIONS=(.05,.10,.15)
N_BOOTSTRAP=10000
SEEDS={"news_id":20260821,"ticker":20260822}
HISTORICAL={
    "V2":(4449,0.14429480582475662,0.5788288288288288),
    "V3":(2827,0.14943748898804188,0.5851063829787234),
    "V4":(40320,0.027561593800783157,0.10168650793650791),
}

class ScientificGateError(RuntimeError):
    """Fail closed on missing inputs, drift or an infeasible Top-K."""

def _vec(x, dtype=float):
    v=np.asarray(x,dtype=dtype)
    if v.ndim!=1 or len(v)==0:
        raise ScientificGateError("Non-empty one-dimensional array required")
    return v

def _align(*arrays):
    n=len(arrays[0])
    if any(len(a)!=n for a in arrays):
        raise ScientificGateError("Different array lengths")

def legacy_news_weights(news_ids:Sequence)->np.ndarray:
    """Original weight=1 / count of SAME news_id within supplied split."""
    ids=_vec(news_ids,dtype=object)
    count={}
    for item in ids:
        count[item]=count.get(item,0)+1
    return np.asarray([1.0/count[item] for item in ids],dtype=np.float64)

def original_weighted_quantile(values:Sequence,weights:Sequence,q:float)->float:
    values=_vec(values,dtype=np.float64)
    weights=_vec(weights,dtype=np.float64)
    _align(values,weights)
    if not (np.isfinite(values).all() and np.isfinite(weights).all()
            and np.all(weights>0) and 0<=q<=1):
        raise ScientificGateError("Quantile requires finite values, positive weights, 0<=q<=1")
    order=np.argsort(values)
    cum=np.cumsum(weights[order])
    index=np.searchsorted(cum, float(q)*cum[-1], side="left")
    return float(values[order[min(int(index),len(values)-1)]])

def original_validation_p10_thresholds(raw_p10:Sequence,news_ids:Sequence):
    raw=_vec(raw_p10,dtype=np.float64)
    ids=_vec(news_ids,dtype=object)
    _align(raw,ids)
    if len(raw)!=P10_VALID_SIZE:
        raise ScientificGateError("Original V0 validation source must have 19880 rows")
    if not np.isfinite(raw).all():
        raise ScientificGateError("Nonfinite original P10 predictions")
    calibrated=raw+P10_OFFSET
    weights=legacy_news_weights(ids)
    cut={str(q):original_weighted_quantile(calibrated,weights,q)
         for q in A2_PERCENTILES}
    if not np.isclose(cut[str(.25)],Q25_FROZEN,rtol=0.0,atol=1e-6):
        raise ScientificGateError("Original q25 no longer reproduces frozen cutoff")
    return cut

@dataclass(frozen=True)
class Selection:
    n:int
    k:int
    admitted:int
    feasible:bool
    baseline_mean:float|None
    candidate_mean:float|None
    delta_mean:float|None
    baseline_hit_rate:float|None
    candidate_hit_rate:float|None
    delta_hit_rate:float|None

def select_topk(prediction:Sequence,target:Sequence,admitted:Sequence,fraction:float)->Selection:
    """No partial fill; exactly original descending argsort and pass veto."""
    x=_vec(prediction,dtype=np.float64)
    # Historic Phase II uses target_model.to_numpy() with ORIGINAL dtype.
    # Float32 np.mean returns a float32 aggregate before float(...);
    # coercing to float64 changes 1e-12 original q25/K10 parity.
    # Preserve floating target dtype for selection AND bootstrap.
    y=_vec(target,dtype=None)
    if y.dtype.kind!="f":
        y=y.astype(np.float64)
    mask=_vec(admitted,dtype=bool)
    _align(x,y,mask)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ScientificGateError("Nonfinite score or old outcome target")
    if not 0<fraction<=1:
        raise ScientificGateError("Invalid capacity fraction")
    n=len(y)
    k=int(n*fraction)
    if k<1:raise ScientificGateError("Empty Top-K, no implicit minimum 1")
    order=np.argsort(-x)
    baseline=order[:k]
    candidate=order[mask[order]][:k]
    eligible=int(mask.sum())
    bmean=float(np.mean(y[baseline]))
    bhit=float(np.mean(y[baseline]>0))
    if len(candidate)<k:
        return Selection(n,k,eligible,False,bmean,None,None,bhit,None,None)
    cmean=float(np.mean(y[candidate]))
    chit=float(np.mean(y[candidate]>0))
    return Selection(n,k,eligible,True,bmean,cmean,cmean-bmean,bhit,chit,chit-bhit)

def assert_original_q25_k10_replication(cohort:str, prediction, target, original_pass):
    if cohort not in HISTORICAL:
        raise ScientificGateError("Unknown original cohort")
    n,mean,hit=HISTORICAL[cohort]
    if len(prediction)!=n:
        raise ScientificGateError("Original cohort size drift")
    result=select_topk(prediction,target,original_pass,.10)
    if not result.feasible:
        raise ScientificGateError("Original q25/K10 no longer full-K feasible")
    if not (np.isclose(result.delta_mean,mean,atol=1e-12,rtol=0)
            and np.isclose(result.delta_hit_rate,hit,atol=1e-12,rtol=0)):
        raise ScientificGateError("Old historical q25/K10 effect failed 1e-12 parity")
    return result

def _cluster_codes(cluster_ids:Sequence):
    ids=_vec(cluster_ids,dtype=object)
    seen={}
    codes=np.empty(len(ids),dtype=np.int64)
    for i,key in enumerate(ids):
        if key not in seen: seen[key]=len(seen)
        codes[i]=seen[key]
    return codes,len(seen)

def cluster_bootstrap(prediction:Sequence,target:Sequence,admitted:Sequence,
                      clusters:Sequence,fraction:float,*,seed:int,replicates:int=10000):
    """Original duplicate-all-rows, recompute K and ranking each replicate.

    A single generator is seeded for this cell; results need NOT match
    old across-cohort sequential RNG draws. All new intervals are
    transparently secondary, not historical Phase II original bootstrap.
    If any replicate is infeasible, its intervals are withheld.
    """
    p=_vec(prediction,dtype=np.float64)
    # Historic Phase II uses target_model.to_numpy() with ORIGINAL dtype.
    # Float32 np.mean returns a float32 aggregate before float(...);
    # coercing to float64 changes 1e-12 original q25/K10 parity.
    # Preserve floating target dtype for selection AND bootstrap.
    y=_vec(target,dtype=None)
    if y.dtype.kind!="f":
        y=y.astype(np.float64)
    ok=_vec(admitted,dtype=bool)
    code,c=_cluster_codes(clusters)
    _align(p,y,ok,code)
    if c<1 or replicates<1:
        raise ScientificGateError("Invalid bootstrap dimensions")
    rng=np.random.default_rng(seed)
    rows=np.arange(len(p))
    means=[];hits=[];bad=0
    for _ in range(replicates):
        draws=rng.integers(0,c,size=c)
        counts=np.bincount(draws,minlength=c)
        ix=np.repeat(rows,counts[code])
        if not len(ix):
            bad+=1;continue
        r=select_topk(p[ix],y[ix],ok[ix],fraction)
        if not r.feasible:
            bad+=1;continue
        means.append(r.delta_mean)
        hits.append(r.delta_hit_rate)
    def ci(a):
        return [float(np.quantile(a,.025,method="linear")),
                float(np.quantile(a,.975,method="linear"))]
    return {
        "method":"cluster_bootstrap",
        "replicates":replicates,
        "seed":seed,
        "infeasible_replicates":bad,
        "ci95_delta_topk_mean":None if bad else ci(means),
        "ci95_delta_topk_hit_rate":None if bad else ci(hits),
        "interpretation":"POST_OUTCOME_EXPLORATORY_NOT_INDEPENDENT_CONFIRMATION"
    }

def _calendar_date(x):
    if isinstance(x,datetime):
        return (x.astimezone(timezone.utc).date()
                if x.tzinfo is not None else x.date())
    if isinstance(x,date):return x
    if isinstance(x,np.datetime64):
        return date.fromisoformat(str(x.astype("datetime64[D]")))
    if isinstance(x,str):
        return date.fromisoformat(x[:10])
    raise ScientificGateError("Unsupported original UTC event/bar date object")

def trailing_volatility_60(bar_dates:Sequence,close:Sequence,event_date):
    """Conservative A3 PRIMARY numeric policy: 60 COMPLETE past returns.

    Returns (score or None, reason), no mutation or outcome access.
    Exactly last 61 distinct dated closes strictly before event UTC
    calendar date. Invalid selected closes => ineligible; NO 40-return
    fallback, interpolation, forward filling, or winsorization.
    'Trading dates' means available saved bars, NOT an independently
    authenticated historic exchange calendar/provider vintage.
    """
    ds=list(bar_dates)
    saved_close=list(close)
    if len(ds)!=len(saved_close):raise ScientificGateError("Bar dates/close length mismatch")
    event=_calendar_date(event_date)
    prior=[]
    seen=set()
    for d,value in zip(ds,saved_close):
        td=_calendar_date(d)
        if td in seen:raise ScientificGateError("Duplicate daily stock bar date")
        seen.add(td)
        if td<event:
            prior.append((td,value))
    prior.sort(key=lambda x:x[0])
    if len(prior)<61:
        return None,"INSUFFICIENT_61_PRIOR_BARS"
    # Convert ONLY the selected pre-event 61 closes, not any future
    # rows. A nonnumeric, null or infinite selected bar makes the pair
    # ineligible for ALL A3 arms. No imputation or alternate history.
    try:
        window=np.asarray([v for _,v in prior[-61:]],dtype=np.float64)
    except (TypeError,ValueError,OverflowError):
        return None,"INVALID_SELECTED_HISTORIC_CLOSE"
    if not np.isfinite(window).all() or np.any(window<=0):
        return None,"INVALID_SELECTED_HISTORIC_CLOSE"
    ret=window[1:]/window[:-1]-1.
    if not np.isfinite(ret).all() or len(ret)!=60:
        return None,"INVALID_60_PRIOR_DAILY_RETURNS"
    vol=float(np.std(ret,ddof=1))
    if not isfinite(vol):
        return None,"INVALID_RISK_SCORE"
    return vol,"OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED"

def validation_only_volatility_cutoff(valid_vol,valid_original_p10_admit,news_ids):
    risk=np.asarray(valid_vol,dtype=np.float64)
    accept=np.asarray(valid_original_p10_admit,dtype=bool)
    ids=_vec(news_ids,dtype=object)
    _align(risk,accept,ids)
    valid=np.isfinite(risk)&(risk>=0)
    if not valid.any():raise ScientificGateError("No original validation common eligible pairs")
    # Legacy weighting is recomputed inside the exact common-eligible
    # validation split. A dropped ticker changes multiplicity for its
    # news_id; never silently retain full-split weights on a subset.
    weights=legacy_news_weights(ids[valid])
    frac=float(np.average(accept[valid],weights=weights))
    q=original_weighted_quantile(risk[valid],weights,frac)
    return {"cutoff":q,"original_p10_weighted_admission":frac,
            "volatility_weighted_admission":float(
                np.average(risk[valid]<=q,weights=weights)),
            "common_validation_pairs":int(valid.sum()),
            "vintage_status":"UNVERIFIED_LATER_SNAPSHOT"}
