"""G5.6 pure numerical TRAIN-only reconstructed target-center contract.

NO I/O, NO pickle, NO any V2/V3/V4 observation, NO P&L, NO inference.
Caller must ensure all rows are genuine original TRAIN rows and authorized.
"""
from __future__ import annotations

import hashlib
import json
from typing import Sequence

import numpy as np

from dtrm.legacy_target_preprocessing import preprocess_legacy_targets, _kahan_mean_float32
from dtrm.target_clipping import train_only_clip_bounds


class TrainOnlyError(ValueError):
    pass


def centers_from_train(*, ticker:Sequence[str], raw_targets:Sequence[float])->dict:
    """Use frozen source semantics, check independent Kahan/clip replay."""
    tickers=list(ticker)
    targets=np.asarray(raw_targets,dtype=np.float64)
    if not tickers or len(tickers)!=len(targets) or targets.ndim!=1:
        raise TrainOnlyError("Original TRAIN ticker/raw label cardinality mismatch")
    if not np.isfinite(targets).all() or any(not isinstance(t,str) or not t for t in tickers):
        raise TrainOnlyError("Nonfinite TRAIN label or invalid ticker")
    lower,upper=train_only_clip_bounds(targets)
    if not (np.isfinite(lower) and np.isfinite(upper) and lower < upper):
        raise TrainOnlyError("Invalid original TRAIN-only clip bounds")

    # Original preprocessing call, deliberately empty V0 VALID/TEST.
    original=preprocess_legacy_targets(
        train_tickers=tickers,train_targets=targets,
        valid_tickers=[],valid_targets=[],test_tickers=[],test_targets=[])
    if original["clip_lower"]!=lower or original["clip_upper"]!=upper:
        raise TrainOnlyError("TRAIN quantile clipping parity mismatch")
    original_means=original["ticker_means"]
    clipped=np.clip(np.asarray(targets,dtype=np.float32),
                    lower,upper).astype(np.float32)

    grouped:dict[str,list[np.float32]]={}
    for t,raw in zip(tickers,clipped):
        grouped.setdefault(t,[]).append(raw)
    independently_reconstructed={
        t:_kahan_mean_float32(samples) for t,samples in grouped.items()}
    if list(independently_reconstructed)!=list(original_means):
        raise TrainOnlyError("Ticker first-seen ordering drift")
    for t,x in independently_reconstructed.items():
        a=np.asarray(x,dtype=np.float32).tobytes()
        b=np.asarray(original_means[t],dtype=np.float32).tobytes()
        if a!=b:
            raise TrainOnlyError("Independent TRAIN ticker Kahan mean float32 mismatch")
    centers=np.array([independently_reconstructed[t] for t in tickers],dtype=np.float32)
    raw_centered=(clipped-centers).astype(np.float32)
    if original["train"].dtype!=np.float32 or not np.array_equal(
            raw_centered.view(np.uint32),original["train"].view(np.uint32)):
        raise TrainOnlyError("Original TRAIN centered label float32 mismatch")
    if len(original["valid"]) or len(original["test"]):
        raise TrainOnlyError("VALID/TEST data unexpectedly generated")

    # SHA of ticker/float32 *ordered dictionary* only; no labels or
    # per-ticker values are serialized in the public audit report.
    h=hashlib.sha256()
    for t,v in sorted(independently_reconstructed.items()):
        h.update(len(t.encode("utf-8")).to_bytes(4,"big"))
        h.update(t.encode("utf-8"))
        h.update(np.asarray(v,dtype="<f4").tobytes())
    return {
        "status":"TRAIN_CENTERS_NUMERIC_PARITY_ONLY",
        "train_rows":len(targets),
        "train_tickers":len(independently_reconstructed),
        "clip_lower":float(lower),
        "clip_upper":float(upper),
        "train_ticker_mean_float32_mapping_sha256":h.hexdigest(),
        "train_centered_float32_parity":True,
        "original_train_centered_bytes_sha256":
            hashlib.sha256(original["train"].tobytes()).hexdigest(),
        "validation_or_test_labels_consumed":False,
        "v2_v3_v4_targets_consumed":False,
        "economic_returns_or_trading_pnl_inferred":False,
    }
