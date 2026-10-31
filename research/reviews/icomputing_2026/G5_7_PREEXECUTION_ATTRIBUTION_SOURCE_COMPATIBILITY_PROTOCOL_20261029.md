# G5.7 — Historical attribution: pre-execution protocol and strict compatibility gates

Date: 2026-10-29. Case ICOMPUTING-D-26-01069.
**Protocol status:** FROZEN DESIGN / NO NEW V2-V3-V4 SOURCE OR OUTCOME ACCESS.
**Observed original G5.6 owner-operated TRAIN-only report** (provided 2026-10-29):
SHA256 `ee6868bf190e4103f1951e53d4b66e34926b3f56f82974f4639b391f7bed963c`,
reported TRAIN_N=75828, TRAIN_TICKERS=171, TRAIN_FLOAT32_CENTER_PARITY=PASS.
Archived G5.5 metadata source report SHA:
`a9a39f0836f490dc2c8a464db224f546883e14e34cc3b6ff3b669cf726c32e2d`.
The owner-provided log is **not a new heldout outcome**. Full legacy row source archival SHA and price vintage remain **UNATTESTED**.

## G5.6 status-field collision, transparent erratum

Original protected runner `269c8c7a5ccff5273b99bc19c23ffdcdf03afde7` inserted `"status":"G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED"` into a Python dict **before** `**fitted`, where `fitted["status"]="TRAIN_CENTERS_NUMERIC_PARITY_ONLY"`. Therefore the first successful operator report prints the latter status. This is a source-presentation bug, not evidence of altered TRAIN means. **Never rewrite, overwrite or retroactively rehash the original G5.6 report.** Subsequent code may correct the merge precedence; the original report should be interpreted via an independent hash-locked, source-aware readback, with both original and normalized statuses explicitly recorded.

## Critical novelty-validity checkpoint: label transformation compatibility (NOT YET TESTED)

G5.6 reconstructs original V0 TRAIN clipping and float32 ticker means, but the original G3.1/G3.2 V2/V3/V4 archived `target_model` labels were saved in **different June 2026 source archives**. It remains UNPROVEN that the identical V0 clipping thresholds and per-ticker centers were used to produce every later archived target.

**No actual attribution can be inferred merely by adding V0 mu_train[ticker] to a V2/V3/V4 target_model.** Mathematically that constructs a hypothetical de-centered score, not necessarily its original clipped beta-adjusted target. First prove the original V2/V3/V4 target producer's frozen preprocessing contract or independently reconstruct the original event forward target from compatible archived stock/SPY close, original event date and an authenticated pre-event beta for each row. Reproduce the archived `target_model` to strict original float32 representation (or predeclared conservative tolerance if a proven original rounding path requires it). No post-outcome selection of acceptable tolerance, training vintage or price cache. If original beta source or model-vintage original training transform is missing, classify `LABEL_TRANSFORM_COMPATIBILITY_NOT_ESTABLISHED` and do NOT call delta clipping-attribution established.

## Primary G5.7 research questions (entire old cohort sample; POST-OUTCOME EXPLORATORY)

1. For V2 N=4449, V3 N=2827 and V4 N=40320, does the original model-target Top-K delta exactly reproduce the previously published original baseline/P10 results on the original q25/K10 rule?
2. If and ONLY if source compatibility is verified, how does each source-matched old policy delta decompose into:
   `delta_Y_model = delta_clipped_source_beta_excess - delta_original_train_ticker_mean`?
   Report all three cohort components and sign/magnitude, including adverse/null results. Report per-ticker center source coverage and original source-vintage limitations, not individual ticker values or IDs.
3. Separately, if V0 continuous point-score distribution and continuous P10/volatility feature signals are source-reconstructed and validated, compare frozen point, soft-risk and hard-risk on **identical** original input information and K, with V0-fixed scaling. This is a second conditional analysis, not guaranteed by G5.6.

## Hard safety/validity gates before old target access

A. Lock and readback exact owner G5.5 and G5.6 SHA256; confirm required numeric TRAIN=75828, tickers=171, float32 parity and original source commit pin; preserve original bug note as lineage metadata. The digest of TRAIN ticker center map is a HASH ONLY: it is **not sufficient to reconstruct the 171 numeric means** from the report.
B. For a later outcome-containing analysis, recompute TRAIN ticker means in the same protected process after authentic source checks; verify mapping SHA equals the first G5.6 report. Do NOT publish 171 means or import public per-ticker CSV files. G5.6 does not persist numeric map by design. No hidden fallback to result-derived means.
C. Before accessing any original V2/V3/V4 Pickle, verify exact old G2/G3 manifests, original six file SHAs, 174 historical price-file SHA, original q25/K10 and validation-only thresholds, frozen Git source/test code. Require **separate, new explicit owner approval** for old post-outcome study, trust of local Pickles and price-vintage caveats. An earlier G3 approval, or the G5.6 TRAIN-only approval, does not authorize this.
D. Assert original sample N, original news_id/ticker/date one-to-one key join, complete K, original score sort and original float32 label precision. Reproduce original P10 vs baseline means to source-exact precision *before* new explanatory outputs. With original target transformation source incompatibility, report NO-GO and do not silently force equality.
E. Retain original fixed V0 cutoffs, K, and inference caveats; do not tune soft-risk IQR or scale using already-observed V2–V4 outcomes; no cherry picking favorable cohorts.
F. Even successful explained `target_model` or clipped-excess-beta effects are NOT actual gross stock return or cash/fees portfolio profitability. The original 60d windows overlap and stock archive vendor vintage/adjustment truth remains open. Independent true 60d holdout and genuine second ranking model are not present.
G. Do not re-run G5.6 just to correct the printed status: keep the original report hash, use readback+normalization with transparent explicit bug note. The updated code requires a NEW commit pin for any new scientific execution.

## Expected outcome classes, not promises

- `G57_SOURCE_COMPATIBILITY_AND_ORIGINAL_PARITY_PASS_POST_OUTCOME_EXPLORATORY`: only if original label/vintage/process provenance, original 3 cohort outcome means and TRAIN center digest all independently match. Results must include adverse cases.
- `G57_LABEL_TRANSFORM_COMPATIBILITY_NOT_ESTABLISHED`: inability to prove the original center/clip version for V2–V4 or to reproduce archived target_model; no claimed decomposition.
- `G57_INPUT_SOURCE_OR_METHOD_PARITY_FAIL_CLOSED`: row order, price, code, consent or original point outcome drift.
- `G57_INFORMATION_PARITY_SOFT_RISK_NOT_AUTHORIZED`: absent independent source-verified V0 point+risk calibration, even if old original source exists.

**Scoring**: G4.12 64/100 science baseline, G5/G6 working fixes provisionally ~67/100, **85/100 NOT ACHIEVED**. Original-source G5.6 reconstruction increases source readiness, not empirical effect estimate. Paper novelty only if relevant fair original-data contrasts and proper prior-art comparison survive, else record negative results.
