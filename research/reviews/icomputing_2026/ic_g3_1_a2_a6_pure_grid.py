"""G3.1 A2/A6 secondary 18-cell exploratory grid — PURE, NO FILE I/O.

This module is source code prepared for review, NOT experimental
authorization. It does not load original data, deserialize Pickles,
execute source loaders or run any analysis on import. A future
separately operator-authorized, exact-SHA versioned runner must
supply only verified and keyed original V0 validation and old
V2/V3/V4 source arrays; it must check source gate and owner signoff
BEFORE accessing original forward targets.

All original V2/V3/V4 60-day outcomes are already known: POST_OUTCOME
EXPLORATORY ONLY. Never imply independent confirmation or realized P&L.
"""
from __future__ import annotations
import numpy as np
from ic_g2_g3_exploratory_core import (
  A2_PERCENTILES,A6_FRACTIONS,HISTORICAL,
  SEEDS,N_BOOTSTRAP,Q25_FROZEN,
  original_validation_p10_thresholds,
  assert_original_q25_k10_replication,
  select_topk,cluster_bootstrap,ScientificGateError,
)

COHORT_ORDER=("V2","V3","V4")
ADMISSION_GRID=("A2","A6")

def _record(arm:str,cohort:str,setting:float,pred,target,p10,mask,
            news_ids,tickers,fraction:float,replicates:int,bootstrap:bool):
    result=select_topk(pred,target,mask,fraction)
    response={
       "work_package":arm,
       "cohort":cohort,
       "setting":setting,
       "n_original_pairs":result.n,
       "k_required":result.k,
       "admitted_pairs":result.admitted,
       "admitted_rate":result.admitted/result.n,
       "full_k_feasible":result.feasible,
       "baseline_mean_forward_excess_beta":result.baseline_mean,
       "veto_mean_forward_excess_beta":result.candidate_mean,
       "delta_mean_forward_excess_beta":result.delta_mean,
       "baseline_hit_rate":result.baseline_hit_rate,
       "veto_hit_rate":result.candidate_hit_rate,
       "delta_hit_rate":result.delta_hit_rate,
       "news_cluster_bootstrap":None,
       "ticker_cluster_bootstrap":None,
       "inferential_scope":"POST_OUTCOME_EXPLORATORY_NOT_PROSPECTIVE",
    }
    if result.feasible and bootstrap:
        response["news_cluster_bootstrap"]=cluster_bootstrap(
            pred,target,mask,news_ids,fraction,
            seed=SEEDS["news_id"],replicates=replicates)
        response["ticker_cluster_bootstrap"]=cluster_bootstrap(
            pred,target,mask,tickers,fraction,
            seed=SEEDS["ticker"],replicates=replicates)
    return response

def analyze_18_cells(
    *,
    original_valid_p10_raw,
    original_valid_news_ids,
    old_cohorts:dict,
    bootstrap:bool=True,
    replicates:int=N_BOOTSTRAP,
):
    """Prepare all 18 old-cohort exploratory cells, fail on old parity.

    Inputs:
      validation: original 19,880 raw P10 scores + news IDs, same
        frozen V0 validation row order, NOT old V2/V3/V4 targets.
      old_cohorts: {V2,V3,V4} mapping with named arrays
        prediction,p10_calibrated,original_q25_pass,target,news_id,ticker
        from a separately authorized, verified keyed source adapter.

    Never mutate inputs or promote q15/q35 or K5/K15.
    """
    if not (isinstance(old_cohorts,dict) and
            set(old_cohorts)==set(COHORT_ORDER)):
        raise ScientificGateError("Exactly original V2/V3/V4 cohorts required")
    if not (isinstance(replicates,int) and
            ((bootstrap and replicates==N_BOOTSTRAP) or not bootstrap)):
        raise ScientificGateError("Real analysis requires exactly 10000 cluster draws")
    cut=original_validation_p10_thresholds(
        original_valid_p10_raw,original_valid_news_ids)
    if not np.isclose(cut[str(.25)],Q25_FROZEN,rtol=0,atol=1e-6):
        raise ScientificGateError("Original original q25 validation cutoff drift")
    old_parity={}
    arrays={}
    for cohort in COHORT_ORDER:
        v=old_cohorts[cohort]
        required={"prediction","p10_calibrated","original_q25_pass",
                  "target","news_id","ticker"}
        if not (isinstance(v,dict) and required.issubset(v)):
            raise ScientificGateError("Missing original source data for "+cohort)
        n=HISTORICAL[cohort][0]
        for key in required:
            if len(v[key])!=n:
                raise ScientificGateError("Original "+cohort+" array "+key+" count drift")
        p10=np.asarray(v["p10_calibrated"],dtype=float)
        stored=np.asarray(v["original_q25_pass"],dtype=bool)
        if not (np.isfinite(p10).all()
            and np.array_equal(p10>=Q25_FROZEN,stored)):
            raise ScientificGateError("Original q25/Calibrated P10 mask drift in "+cohort)
        old_parity[cohort]=assert_original_q25_k10_replication(
            cohort,v["prediction"],v["target"],stored)
        arrays[cohort]=v
    rows=[]
    for cohort in COHORT_ORDER:
        v=arrays[cohort]
        for q in A2_PERCENTILES:
            threshold=cut[str(q)]
            eligible=np.asarray(v["p10_calibrated"],dtype=float)>=threshold
            rows.append(_record("A2",cohort,q,v["prediction"],v["target"],
                     v["p10_calibrated"],eligible,v["news_id"],v["ticker"],
                     .10,replicates,bootstrap))
        for frac in A6_FRACTIONS:
            rows.append(_record("A6",cohort,frac,v["prediction"],v["target"],
                     v["p10_calibrated"],v["original_q25_pass"],
                     v["news_id"],v["ticker"],frac,replicates,bootstrap))
    if len(rows)!=18 or {x["work_package"] for x in rows}!={"A2","A6"}:
        raise ScientificGateError("Missing fixed 18 exploratory cells")
    return {
      "status":"G3_1_A2_A6_POST_OUTCOME_EXPLORATORY_18_CELLS",
      "cutoffs_validation_only":cut,
      "frozen_q25":Q25_FROZEN,
      "old_historical_q25_k10_parity":{
        k:{"n":v.n,"k":v.k,"delta_mean":v.delta_mean,
           "delta_hit_rate":v.delta_hit_rate}
        for k,v in old_parity.items()
      },
      "cells":rows,
      "cells_expected":18,
      "replicates_per_news_or_ticker_cell":replicates if bootstrap else 0,
      "source_provenance":"Historical outcome-consumed inputs, NOT prospectively authenticated",
      "target_is_tradable_portfolio_profit":False,
      "independent_new_60_day_holdout":False,
      "g3_1_execution_authorized_by_this_module":False,
    }
