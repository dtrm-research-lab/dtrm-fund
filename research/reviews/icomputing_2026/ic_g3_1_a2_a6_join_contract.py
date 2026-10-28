"""G3.1 A2/A6 PRE-AUTHORIZATION pure original cohort join contract.

No file access, no deserialization, no automatic experiment execution.
A separately approved and SHA-pinned future G3.1 runner may call this
function with already-verified and independently consented original
trusted local source frames. The output retains identifiers in memory
only; never commit original joined data or raw target arrays.

Historical source authority: frozen original
research/experiments/run_phase2_primary_bootstrap.py
commit c7502a690162459cdfb3413573e3133c42efb126.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

PIN="c7502a690162459cdfb3413573e3133c42efb126"
Q25=-0.16665692627429962
OFFSET=-0.06494169682264328
COHORT_SIZES={"V2":4449,"V3":2827,"V4":40320}
REQUIRED_SIGNAL={
    "news_id","ticker","date_dt","baseline_prediction",
    "p10_pass","p10_raw","p10_calibrated"
}
REQUIRED_TARGET={"news_id","ticker","date_dt","target_model"}

class OriginalJoinError(ValueError):
    pass

def _must(condition,reason):
    if not condition:raise OriginalJoinError(reason)

def source_exact_join(signals:pd.DataFrame,targets:pd.DataFrame,cohort:str):
    """Join the original files by unique two-part pair key AND exact date.

    Fail-closed:
    - No index/position-aligned guessing or silent row drops;
    - No NaN keys, duplicates, null dates, or ambiguous source schema;
    - Fixed original V2/V3/V4 cohort count and original signal order;
    - Date timestamps identical after UTC normalization;
    - No nonfinite original target/model scores;
    - Original relative q25 calibrated-P10 veto mask reproduced.
    """
    _must(cohort in COHORT_SIZES,"Unknown original cohort")
    n=COHORT_SIZES[cohort]
    _must(isinstance(signals,pd.DataFrame) and isinstance(targets,pd.DataFrame),
          "Original sources must be DataFrame objects")
    _must(REQUIRED_SIGNAL.issubset(signals.columns),
          "Missing original signal source columns")
    _must(REQUIRED_TARGET.issubset(targets.columns),
          "Missing original target source columns")
    _must(len(signals)==n and len(targets)==n,
          "Unexpected original signal/target row count")
    for label,frame in (("signals",signals),("targets",targets)):
        _must(not frame[["news_id","ticker","date_dt"]].isna().any().any(),
              "Null original keys or dates in "+label)
        _must(not frame.duplicated(["news_id","ticker"]).any(),
              "Duplicate original news/ticker pair in "+label)
    joined=signals.merge(
        targets[["news_id","ticker","date_dt","target_model"]],
        on=["news_id","ticker"],how="inner",validate="one_to_one",
        sort=False,suffixes=("_signal","_target")
    )
    _must(len(joined)==len(signals)==len(targets),
          "Missing original news/ticker pair(s), no partial join allowed")
    # The original PhaseII study uses merge(sort=False), so the signal
    # source must preserve the exact pre-join original pair order.
    expect_keys=list(zip(signals["news_id"],signals["ticker"]))
    joined_keys=list(zip(joined["news_id"],joined["ticker"]))
    _must(expect_keys==joined_keys,
          "Original sorted signal source key ordering changed")
    srcdate=pd.to_datetime(joined["date_dt_signal"],utc=True,errors="coerce")
    dstdate=pd.to_datetime(joined["date_dt_target"],utc=True,errors="coerce")
    _must(not srcdate.isna().any() and not dstdate.isna().any()
          and bool(srcdate.equals(dstdate)),
          "Original event timestamps differ or parse ambiguously")
    origmask=joined["p10_pass"]
    _must(origmask.isin([True,False]).all()
          and all(isinstance(x,(bool,np.bool_)) for x in origmask.tolist()),
          "Original frozen P10 mask not strict Boolean")
    score=joined["baseline_prediction"].to_numpy(dtype=float)
    raw=joined["p10_raw"].to_numpy(dtype=float)
    calibrated=joined["p10_calibrated"].to_numpy(dtype=float)
    target=joined["target_model"].to_numpy(dtype=float)
    _must(np.isfinite(score).all() and np.isfinite(raw).all()
          and np.isfinite(calibrated).all() and np.isfinite(target).all(),
          "Nonfinite original numeric model/target source value")
    _must(bool(np.allclose(calibrated,raw+OFFSET,rtol=0,atol=1e-6)),
          "Original P10 raw/calibrated offset numeric mismatch")
    _must(np.array_equal(calibrated>=Q25,origmask.to_numpy(dtype=bool)),
          "Original P10 q25 decision flag mismatch")
    return joined

def extract_source_arrays(joined:pd.DataFrame):
    """Full original in-memory cohort arrays; NEVER serialize these."""
    return {
      "prediction":joined["baseline_prediction"].to_numpy(dtype=float),
      "p10_calibrated":joined["p10_calibrated"].to_numpy(dtype=float),
      "original_q25_pass":joined["p10_pass"].to_numpy(dtype=bool),
      "target":joined["target_model"].to_numpy(dtype=float),
      "news_id":joined["news_id"].to_numpy(dtype=object),
      "ticker":joined["ticker"].to_numpy(dtype=object)
    }
