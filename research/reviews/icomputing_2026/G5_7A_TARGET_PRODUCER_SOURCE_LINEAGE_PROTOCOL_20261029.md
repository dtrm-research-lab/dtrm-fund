# G5.7a — Static original target-producing source search (before old outcome access)

Date: 2026-10-29. ICOMPUTING-D-26-01069.
**Status: design/source search; NO ORIGINAL V2/V3/V4 TARGET VALUES READ.**

## Input evidence

Owner G5.5 hash-only report SHA: `a9a39f0836f490dc2c8a464db224f546883e14e34cc3b6ff3b669cf726c32e2d`.
Owner G5.6 TRAIN-only numeric report SHA: `ee6868bf190e4103f1951e53d4b66e34926b3f56f82974f4639b391f7bed963c`.
Owner G5.7 readback SHA: `e5d4e9281da809006c450be8a37c4c6c84cc51f2077b20e2c979ec061893020f`.
Observed TRAIN N=75,828, tickers=171, frozen float32 Kahan/clipped target original reference PASS. The G5.7 readback was performed by the owner; GitHub and this cloud session have the operator's **textual report**, not private old cohort data.

## Scientific attribution prerequisite

The original G5.6 reconstruction calculates TRAIN clipping/ticker centers from `legacy_model_rows_2026-05-01.pkl`. But the V2, V3, V4 `target_model` cohorts were archived later in separate June files. **Source evidence that all three used exactly the same numeric clipping bounds and means as V0 is currently missing.**

One cannot conclude `Y_model + original_V0_train_ticker_mean = historical precentered_clipped_Y` without that source compatibility. We also cannot infer real stock returns / tradable P&L from clipped transformed targets.

## Bounded source-only operator search

Only locate *candidate producing code*, never the outcome values. The tool `ic_g5_7a_target_producer_source_scan.py` scans **only operator-selected, non-symlink .py files** in two bounded original-code directories, subject to max-size / file count. It does not open .pkl, .csv, .ipynb (notebook output cells can contain results), images, market/embedding data, or current APIs.

Look for three original exact June 2026 filenames:
- V2: `probabilistic_v2_holdout_model_targets_2026-06-10.pkl`
- V3: `probabilistic_v3_holdout_model_targets_2026-06-14.pkl`
- V4: `probabilistic_v1_holdout_model_targets_2026-06-06.pkl`

Report **relative source paths, SHA256 of .py bytes, presence of literal target filename, static `target_model` references, `preprocess_legacy_targets` references and candidate serialization/write calls**. No source snippets, secrets, raw labels, ticker rows or absolute local paths are serialized. A nearby `to_pickle` call is **only a possible writer**; it does NOT prove that the specific target file was produced with original q01/q99 and TRAIN ticker means. A reader with the exact filename is not counted as a producer.

Output classes:
- `G57A_SOURCE_WRITER_CANDIDATE_ONLY_PROVENANCE_OPEN`: at least one potential writer in scanned sources; separate manual code review and source/execution chain required.
- `G57A_TARGET_REFERENCES_ONLY_NO_PRODUCER_PROOF`: matching filename but no writer in bounded source set.
- `G57A_NO_EXACT_TARGET_SOURCE_IN_BOUNDED_PY_SCOPE`: cannot find target filename in explicitly scanned Python sources. Not proof that producing code does not exist elsewhere, particularly original Jupyter notebooks (not read here).
- Even multiple same-module writer calls do not establish production chronology, source execution, model version, train-center identity, archival hash, label parity or whether the notebook was modified after the fact.

**Scientific stop:** on nonproof, **do not run V2/V3/V4 target decomposition**, do not read archived outcomes, and do not inflate reviewer readiness toward 85/100.

## Future authorization not carried by this scan

Only after identifying a plausible producing script, freeze its own historical file/commit SHA, inspect its precise data-loading and preprocessing provenance (no outcome data), and obtain independently corroborated generation-time hashes/logs. If unavailable, describe a missing provenance boundary and consider separately preregistered recreated target experiments with clear retrospective status; never silently substitute the V0 TRAIN centers into June archives.

The present source-only scan **does not authorize** new old outcome access, financial-performance estimates, human-agent comparison, or post-hoc hyperparameter search. G5/G6 editorial defense retains all previously known negative and null results.
