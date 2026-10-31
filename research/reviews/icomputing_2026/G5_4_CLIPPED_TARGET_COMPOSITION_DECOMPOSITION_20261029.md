# G5.4 — Attribution audit for preprocessed target: empirical decomposition candidate

Case ICOMPUTING-D-26-01069. Date 2026-10-29.
Status: PURE MATH/SYNTHETIC TESTS ONLY. Real historical V2/V3/V4 target decomposition NOT EXECUTED, no old-result authorization granted by this file.

## Why this is necessary

Original outcome Y_raw = R_stock,60d − beta_pre × R_SPY,60d was modified BEFORE model fitting and outcome evaluation:
- c_i = clip(Y_raw,i; train q01, train q99)
- μ_i = train mean of c_i for the ticker of row i (zero if unseen)
- Y_model,i = c_i − μ_i

This is explicitly implemented in src/dtrm/legacy_target_preprocessing.py. The old Phase-II bootstraps and current G3 selection comparisons use target_model = Y_model, NOT untransformed Y_raw.

When a policy changes the selected ticker mix, its mean transformed target can change even if its mean clipped pre-centered beta-adjusted return does not. This is not by itself label leakage; it is a measurement/estimand issue and a potential selection-composition effect.

## Exact algebraic attribution identity (not a novel theorem)

For policy g and reference b, identical original sample and K, let Δ mean denote selected g minus selected b.

Δ(Y_model) = Δ(c) − Δ(μ_train_ticker).

- Δ(c): pre-center but still TRAIN-clipped beta-adjusted target difference. It is **not** raw return or capital P&L.
- Δ(μ_train_ticker): how the policy's selected ticker mix changes the mean historical TRAIN ticker correction.
- Δ(Y_model): old paper comparison. This is NOT interchangeable with Δ(raw stock return).

The decomposition is an exact arithmetic identity subject to floating point rounding, provided original per-row μ from the precise frozen TRAIN fit is source-recovered, target rows are unchanged, and full-K selection indices are original.

**Synthetic adversarial sign reversal (NOT a market result):** base clipped signals both 10 with ticker TRAIN center 10 -> model labels 0; policy clipped signals both 9 with center 0 -> model labels 9. Then ΔY_model = +9, Δc = −1, Δμ = −10; +9 = −1 − (−10). An apparent model-target improvement is NOT guaranteed to imply an improvement even on the clipped pre-centered outcome.

This is a falsifiable diagnostic relevant to explaining what drives the previously reported differences. It is not a proof that the original HDPG effect **was** due to ticker centering; that requires real original source and outcome-based evaluation.

## New pure implementation

- ic_g5_4_target_decomposition.py: requires matching, finite, original ordered Y_model and per-row TRAIN ticker centers, original base/policy Top-K; rejects duplicates/missing rows. Returns exact three-part identity, residual and explicit failure to recover raw gross returns.
- test_ic_g5_4_target_decomposition.py: seven exclusively synthetic cases, including sign reversal, unchanged selected sets, center-zero identity, malformed/nonfinite/duplicate fail-closed conditions and no fabricated P&L.
- No file I/O, no pickle unpickling, no model training, no old news labels or return dates, no external API, no publication inference.

## Hard scientific gates for actual historical use

1. Separate full SHA-bound original TRAIN clipping q01/q99 and per-ticker μ reconstruction plus original 390-feature ranker and exact V2/V3/V4 pair order; never compute μ from old test targets.
2. Original P10 q25/K10 point effects parity, including old float32 means and original NumPy argsort/tie ordering; preserve all V2/V3/V4 selected indices and K.
3. Separate explicit author authorization of old-target access and source/tests immutable pin. Existing G3/A3 authorization is not automatically permission for this distinct decomposition.
4. Report per-cohort three terms, rounding residual, ticker composition, and dependence-sensitive uncertainty, whether favorable, null, negative or reversing.
5. No raw unclipped return, cash return, portfolio earnings or fees claim from reconstructed clipped target.
6. Treat as POST-OUTCOME EXPLORATORY because original old outcomes are already observed, regardless of this protocol date.

## Relationship to G5.3 matched-information question

The information-matched hard/soft comparison tests **rule enforcement versus alternate use of the same risk information**, conditional on its validity. This decomposition tests **whether apparent output gains are partly a consequence of train-derived ticker target centering under a policy-induced ticker-mix change**. Neither is a human-versus-machine performance trial.

## Publication originality and evidence standard

An exact identity is textbook algebra, NOT a newly discovered theorem. A credible scientific contribution might be an empirical, audited case showing how admission rules, additional risk signals and target-preprocessing choices jointly alter downstream decisions, with original source/selection parity and adverse cases retained. Closely related existing decision-focused/robust portfolio literature must be cited and compared; no priority claim absent actual experimental contrast.

Current G5/G6 candidate Word documents correct transformed-label semantics; no original V2/V3/V4 decomposition numbers exist yet. Thus this stage adds a falsifiable **mechanism audit plan and pure implementation**, not 85/100 achieved scientific evidence.
