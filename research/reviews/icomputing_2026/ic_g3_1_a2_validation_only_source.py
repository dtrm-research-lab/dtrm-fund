"""G3.1 A2 original V0 validation-P10 replay, separate from old outcomes.

UNEXECUTED preparation for a separately approved G3.1 runner only.
On import, performs NO source loading, model inference or file I/O.
This function reconstructs the *validation FEATURE* matrix only,
then predicts original model P10, without loading prices, computing
raw forward-return targets or opening V2/V3/V4 target Pickles.

Original trusted local Pickles/embedding files can execute code during
deserialization; caller must first verify signed G3.1 authorization,
all local source hashes and explicitly trusted original source origin.
Never serialize validation news IDs, embeddings or per-row prediction
vectors into the manuscript, console, GitHub or shared report.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,importlib.util,subprocess,sys
import numpy as np

PIN="c7502a690162459cdfb3413573e3133c42efb126"
ORIGINAL_ROWS="legacy_model_rows_2026-05-01.pkl"
ORIGINAL_FULL="legacy_pairs_enriched_2025-01-01_2026-05-01.pkl"
ROWS_SHA="3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724"
G1_SEAL_SHA="7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac"

def _sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for b in iter(lambda:fp.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def reconstruct_valid_p10_only(
   *,frozen_root,local_data,old_outputs,
   reconstructed_models,g1_dossier_path
):
    """Return in-memory raw validation P10, original news IDs, thresholds.

    This function may ONLY be invoked by a future G3.1 runner whose
    explicit, separate operator authorization and exact code SHA have
    already passed. It is NOT a runnable independent standalone CLI.
    """
    from ic_g2_g3_exploratory_core import (
        original_validation_p10_thresholds,ScientificGateError
    )
    repo=Path(frozen_root).expanduser()
    inputs=Path(local_data).expanduser()
    outputs=Path(old_outputs).expanduser()
    model_dir=Path(reconstructed_models).expanduser()
    dossier_path=Path(g1_dossier_path).expanduser()
    for p in (repo,inputs,outputs,model_dir):
        if not p.is_dir() or p.is_symlink():
            raise ScientificGateError("Frozen original research source directory missing/unsafe")
    if not (dossier_path.is_file() and not dossier_path.is_symlink()
            and _sha(dossier_path)==G1_SEAL_SHA):
        raise ScientificGateError("Original source reconstruction dossier SHA mismatch")
    import json
    dossier=json.loads(dossier_path.read_text(encoding="utf-8"))
    if (dossier.get("source_commit")!=PIN or
       dossier.get("status")!="HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN"):
        raise ScientificGateError("Original G1 source dossier not lineage PASS")
    head=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],
         check=True,capture_output=True,text=True).stdout.strip()
    dirty=subprocess.run(["git","-C",str(repo),"status","--porcelain","--untracked-files=no"],
         check=True,capture_output=True,text=True).stdout.strip()
    if head!=PIN or dirty:
        raise ScientificGateError("Frozen original G1 source commit mutated")
    original_source=repo/"research/experiments/run_probabilistic_xgb_v0.py"
    orig_rows=inputs/ORIGINAL_ROWS
    original_full=inputs/ORIGINAL_FULL
    source_news=outputs/"news_2025-01-01_2026-05-01.pkl"
    original_embeddings=[
       outputs/"news_emb_2025-01-01_2026-05-01.dat",
       outputs/"news_emb_shape_2025-01-01_2026-05-01.pkl",
       outputs/"news_emb_index_2025-01-01_2026-05-01.pkl"
    ]
    for p in (original_source,orig_rows,original_full,source_news,*original_embeddings):
        if not p.is_file() or p.is_symlink():
            raise ScientificGateError("Original training/validation feature input missing/unsafe")
    if _sha(orig_rows)!=ROWS_SHA:
        raise ScientificGateError("Original validation model rows changed since G2.13")
    p10path=model_dir/"p10.ubj"
    if (not p10path.is_file() or p10path.is_symlink() or
        _sha(p10path)!=dossier.get("reconstructed_unapproved_model_sha256",{}).get("p10.ubj")):
        raise ScientificGateError("Reconstructed original P10 booster weights SHA changed")
    # Historical original 'src' must be loaded from pinned root only.
    # G1.2 already established exact 390-feature V1 row parity; no
    # Phase IV, STAMP, modern revised or other outcome label code used.
    sys.path.insert(0,str(repo/"src"))
    spec=importlib.util.spec_from_file_location("ic_g31_original_p10_valid_only",original_source)
    if spec is None or spec.loader is None:
        raise ScientificGateError("Cannot load frozen historical P10 source")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    module.LOCAL_DATA=inputs
    module.FULL_ROWS_PATH=original_full
    module.MODEL_ROWS_PATH=orig_rows
    module.OUTPUTS=outputs
    module.NEWS_PATH=source_news
    module.EMBEDDING_DAT_PATH=original_embeddings[0]
    module.EMBEDDING_SHAPE_PATH=original_embeddings[1]
    module.EMBEDDING_INDEX_PATH=original_embeddings[2]

    # No historical price cache, return target, beta-excess label
    # preprocessing or quantile model FITTING is performed.
    _,rows=module.load_ordered_model_rows()
    mask=rows["split"].eq("valid").to_numpy()
    if int(mask.sum())!=19880:
        raise ScientificGateError("Original frozen validation split size drift")
    features=module.build_exante_feature_matrix(rows)
    if not (features.ndim==2 and features.shape==(len(rows),390)
            and np.isfinite(features).all()):
        raise ScientificGateError("Original 390-feature matrix invalid")
    import xgboost as xgb
    booster=xgb.Booster()
    booster.load_model(str(p10path))
    raw=booster.predict(xgb.DMatrix(features[mask]),iteration_range=(0,19))
    news_ids=rows.loc[mask,"news_id"].to_numpy()
    thresholds=original_validation_p10_thresholds(raw,news_ids)
    return raw,news_ids,{
       "original_validation_pairs":19880,
       "validated_only_predictive_P10":True,
       "raw_target_labels_loaded":False,
       "heldout_financial_target_labels_loaded":False,
       "historic_vendor_vintage_verified":False,
       "thresholds_validation_only":thresholds,
       "original_model_rows_sha256":ROWS_SHA,
       "g1_original_source_dossier_sha256":G1_SEAL_SHA,
    }
