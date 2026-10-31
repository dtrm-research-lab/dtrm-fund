# G5.3 — Source-first scientific gate: information parity, transformed targets and economic identifiability

**Date:** 2026-10-29. Case ICOMPUTING-D-26-01069. **Status:** SCIENTIFIC PROTOCOL AND TECHNICAL DESIGN, NOT HISTORICAL EXPERIMENT EXECUTED. Original Phase-II outcome data are already seen; any new contrast on V2/V3/V4 is **POST-OUTCOME EXPLORATORY**, even if source/design is committed before rerunning it.

## Source-level discovery that changes the economic interpretation of G5

The original frozen sources `research/experiments/run_exante_baseline_v0.py` and `run_probabilistic_xgb_v0.py` call `preprocess_legacy_targets` after constructing raw 60-day forward beta-adjusted returns. The Phase-II bootstrap `research/experiments/run_phase2_primary_bootstrap.py` uses `target_model`. See `src/dtrm/legacy_target_preprocessing.py`.

The actual evaluated label is:

`Y_raw = R_stock,60d - beta_pre * R_SPY,60d`,

`Y_model = clip(Y_raw, TRAIN_q01, TRAIN_q99) - mu_ticker_train`,

with `mu_ticker_train` equal to the **TRAIN clipped** target's ticker mean and zero for an unseen ticker. Training cutoff and centering are fitted strictly on TRAIN. The V2/V3/V4 Top-K means/positive-target shares, original and post-outcome, thus refer to **TRANSFORMED MODEL TARGETS**, not untransformed gross returns and not economic alpha/P&L. Negative transformed-target means **do not establish** negative absolute stock returns or negative portfolio profits.

### Newly corrected author-held Word working artifacts

- `IC_G5_2_TARGET_SEMANTICS_CORRECTED_WORKING_20261029.docx`, SHA256 `f28625a544502d031b58c7a6894caec5ad0f93336d765d9745d72ce30ed3386d`; 19-page rendered working draft, 12 substantial paragraphs rewritten, no change to original experimental numeric values or result tables, table header semantics clarified.
- `IC_G6_2_TARGET_SEMANTICS_CORRECTED_WORKING_20261029.docx`, SHA256 `dbfdf30097f2b40a7fb804a3875901bb7efdcc8c6c96458581145cbbc13b1d8b`; 6-page rendered working draft, reviewer responses R1-04, R1-05 and R2-05 corrected.
- Both remain **candidate manuscript sources**, not the exact journal portal-certified version; no manuscript copy or private target records committed publicly.

**Scientific consequence:** original differences in the same Y_model scale still compare old policy packages, subject to source/provenance and dependence limits. Claims about raw returns, cash, fees and P&L require *the original event-time stock/market price inputs*, correctly adjusted, and a separate capital and execution ledger. It is invalid to reconstruct stock return by merely adding beta × SPY return to the clipped/demeaned Y_model. Inversion of clipping loses information and ticker centering requires historically correct means; even algebraically recoverable rows are not trades.

## Falsifiable original-data question G5.3: isolating INFORMATION from ENFORCEMENT

Compare THREE arms on the SAME original per-row pair set, frozen point-ranker predictions and Top-K K=floor(.10 N):
1. `RAW_RANKER`: rank solely on original frozen point predictions.
2. `SOFT_RISK`: *same* frozen point predictions **plus the same original continuous risk signal** used by the hard veto; sort `score + lambda * safer_risk_signal` and take K. No hard veto.
3. `HARD_RISK`: original frozen ranker score order, but only among rows admitted by the frozen validation-only P10 q25 (or separately frozen validation-only volatility cutoff).

For **P10**, safer signal = calibrated P10 (larger is safer); for **volatility**, safer signal = negative trailing volatility (smaller is safer). For a transparent, non-outcome-fitted `lambda`, use **validation-only IQR(original point scores) / IQR(continuous risk signal)**, fixed multiplier 1 and no post-outcome tuning. The continuous risk signal, not merely an admission mask, MUST be available from original frozen source and matched by pair/order. Zero/invalid validation spread makes the study **NO-GO**, not a reason to choose a favorable scale.

Evaluation old outcome: ORIGINAL same transformed Y_model, original matching and first-source SHA. Explicit paired quantities:
- `hard_minus_soft`: consequences of enforcing a hard admission veto versus using the **same risk information** for soft re-ranking.
- `soft_minus_raw`: information plus soft scoring versus point-only ranker.
- `hard_minus_raw`: original full policy+information package effect; may be parity-checked to original known q25/K10.
- Coverage, full-K feasibility, hard/soft candidate overlap, news/ticker paired bootstrap and calendar dependence caveat; **no confirmatory significance** on old consulted targets.

This design is not a theorem about human authority and not a guaranteed unique method. Earlier decision-focused optimization, selective prediction and ordinary risk optimization are close prior art. Novelty can only be claimed *conditionally* as an auditable applied experimental contrast if implementation, comparable sources and adverse outcomes survive review.

## Hard gates before historical execution

1. Independently verify saved frozen original point-prediction, *continuous* calibrated P10 and trailing volatility scores per original row and V0 validation; masks only are insufficient for a soft matched-information comparison.
2. Original correct news/ticker/date join, source hashes, 40,320 V4 precision, original row cardinality (V2 4,449; V3 2,827; V4 40,320), original q25/K10 predictions and effects parities.
3. Never open old target pickles implicitly. Require **explicit owner authorization** for any new exploratory old outcome analysis after SHA-pinning the source runner and all source/test files. Pure math unit tests on synthetic fixtures are NOT authorization.
4. Fix calibration scaling exclusively on original V0 validation data; no V2/V3/V4 outcome changes, optimizing λ or trying favorable settings.
5. Preserve all complete policy/cohort results, both news/ticker cluster CIs if valid, sensitivity to dependence and historical price provenance uncertainty. Reject a null/adverse result; do not silently redesign the rule.
6. For **economic** gross stock returns and cash/fees, require original (untransformed) event-level entry/exit prices with corporate-action basis and source-vintage explicitly qualified, plus synchronized market, calendar and capital-book rules. Otherwise **ECONOMIC_NOT_ESTIMABLE**, without imputation.

## Editorial acceptance criteria

A **reproducible fair matched-information original-data contrast** with source-verifiable temporal chronology and honest adverse findings may strengthen R2-01 novelty and R1-04 source/method criticism; it does NOT fulfill missing independent unused 60d test (R1-01), second genuinely frozen ranker (R1-07) or real portfolio P&L (R1-05, R2-05). An *independently source-verified* hypothetical untransformed single-event return sensitivity might partially improve the last two reviewer requests, but cannot turn them into a tradable capital-account study.

**SCORE RULE:** Original independent G4.12 rubric: 64/100 science. G5.1 sensitivity+temporal fixes can provisionally motivate ~67/100 only after review. Full verified documentary corrections have a conditional ~74/100 ceiling. **85/100 is an objective, NOT an achieved score, and it requires authentic new evidence not yet present.** Protect submission by November 25, 2026. No fake second model/holdout or post-outcome favorable scoring.

## Control and source separation

G4.9a–c simulated human authority remains a separate engineering benchmark. It does not demonstrate the human thesis and is not merged into this financial experiment. PRs #49–52 are draft. The author-held revised manuscript is private and must not be committed to the public research repository.
