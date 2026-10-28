"""G3.2 A3 3-arm old historical point effects — PURE ARRAY MATH ONLY.

Not an execution authorization: NO deserialization, source I/O, CLI,
model fitting, bootstrap, new policy thresholds or source adjustments.
Original V0-only q25 and daily-volatility cutoffs were frozen before
reading old outcomes. Three arms share identical N, original order,
baseline predictions and K=floor(.1*N) for a *paired* 3-policy comparison.

All original old outcomes had already been consulted in G3.1:
this is POST_OUTCOME_EXPLORATORY and uses retrospective July-5
stock price archives with unverified vendor acquisition vintage.
The 60d forward excess-beta model target is NOT realized portfolio P&L.
"""
from __future__ import annotations
import numpy as np
from ic_g2_g3_exploratory_core import (
    select_topk,assert_original_q25_k10_replication,ScientificGateError,
    trailing_volatility_60
)

EXPECTED={"V2":4449,"V3":2827,"V4":40320}
Q25=-0.16665692627429962
RISK_CUTOFF=0.020823002555902668
K_FRACTION=.10

def _must(ok,why):
    if not ok:raise ScientificGateError(why)

def source_risk_admission_mask(signals,prices,cohort):
    """Original signal order preserved; no extraction of financial targets.

    Called only after SHA-bound source reader has passed signal/price
    source validations; validates dates and original date-restricted
    complete-case trailing-risk eligibility once again.
    """
    import pandas as pd
    _must(cohort in EXPECTED and len(signals)==EXPECTED[cohort],
          "Unknown/changed original cohort")
    _must(all(k in signals.columns for k in
              ("ticker","news_id","date_dt")),
          "Original source pair identity/date columns absent")
    event=pd.to_datetime(signals["date_dt"],utc=True,errors="coerce")
    _must(not event.isna().any(),"Invalid original event datetime")
    memo={}
    risk=[]
    for ticker,date in zip(signals["ticker"].tolist(),event.dt.date.tolist()):
        symbol="BRK-B" if ticker=="BRK.B" else str(ticker)
        key=(symbol,date)
        if key not in memo:
            _must(symbol in prices,
                  "Original old stock no longer has verified source prices")
            bars,close=prices[symbol]
            score,status=trailing_volatility_60(bars,close,date)
            _must(status=="OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED"
                  and score is not None,
                  "Original common-eligible risk score changed: "+status)
            memo[key]=score
        risk.append(memo[key])
    vol=np.asarray(risk,dtype=np.float64)
    _must(vol.shape==(EXPECTED[cohort],) and
          np.isfinite(vol).all() and (vol>=0).all(),
          "Original full source risk mask numeric drift")
    return vol<=RISK_CUTOFF

def three_arm_point_effects(cohort,pred,target,p10_mask,vol_mask):
    """Paired points on exactly the same original sources + sample.

    Report original 3-arm values and DELTA P10-RISK directly,
    without deducing the difference from independent CI overlaps.
    Source target dtype is preserved exactly (original float32).
    """
    _must(cohort in EXPECTED,
          "Only original V2/V3/V4 allowed")
    n=EXPECTED[cohort]
    pred=np.asarray(pred,dtype=np.float64)
    y=np.asarray(target)
    p10=np.asarray(p10_mask,dtype=bool)
    risk=np.asarray(vol_mask,dtype=bool)
    _must(len(pred)==len(y)==len(p10)==len(risk)==n,
          "Old original common sample cardinality drift")
    _must(y.dtype.kind=="f" and np.isfinite(y).all() and
          np.isfinite(pred).all(),
          "Original numeric targets/predictions invalid")
    original=assert_original_q25_k10_replication(
        cohort,pred,y,p10)
    base=select_topk(pred,y,np.ones(n,dtype=bool),K_FRACTION)
    pv=select_topk(pred,y,p10,K_FRACTION)
    rv=select_topk(pred,y,risk,K_FRACTION)
    _must(base.feasible and pv.feasible and rv.feasible,
          "An original A3 arm cannot fill fixed K10")
    _must(original.k==base.k==pv.k==rv.k==int(.10*n)
          and original.delta_mean==pv.delta_mean
          and original.delta_hit_rate==pv.delta_hit_rate,
          "Original Phase II q25/K10 point replication drift")
    order=np.argsort(-pred)
    a=order[p10[order]][:base.k]
    b=order[risk[order]][:base.k]
    return {
      "cohort":cohort,"common_original_pairs":n,
      "same_original_prediction_ranking_for_all_arms":True,
      "K_floor_10_percent":base.k,
      "p10_admitted_pairs":pv.admitted,
      "risk_admitted_pairs":rv.admitted,
      "all_three_original_arms_full_K":True,
      "topk_overlap_p10_risk":len(set(a.tolist())&set(b.tolist())),
      "original_baseline_topk_mean_forward_excess_beta":base.baseline_mean,
      "original_p10_q25_topk_mean_forward_excess_beta":pv.candidate_mean,
      "validation_risk_topk_mean_forward_excess_beta":rv.candidate_mean,
      "p10_minus_baseline_delta_mean":pv.delta_mean,
      "risk_minus_baseline_delta_mean":rv.delta_mean,
      "p10_minus_risk_paired_delta_mean":pv.candidate_mean-rv.candidate_mean,
      "original_baseline_topk_hit_rate":base.baseline_hit_rate,
      "original_p10_topk_hit_rate":pv.candidate_hit_rate,
      "validation_risk_topk_hit_rate":rv.candidate_hit_rate,
      "p10_minus_baseline_delta_hit":pv.delta_hit_rate,
      "risk_minus_baseline_delta_hit":rv.delta_hit_rate,
      "p10_minus_risk_paired_delta_hit":
          pv.candidate_hit_rate-rv.candidate_hit_rate,
      "paired_news_cluster_ci":None,
      "paired_ticker_cluster_ci":None,
      "independent_new_matured_holdout":False,
      "risk_price_vendor_vintage_verified":False,
      "financial_target_is_realized_trading_pnl":False,
      "interpretation":"DATE_RESTRICTED_POST_OUTCOME_EXPLORATORY_UNADJUSTED_POINT_ONLY"
    }
