# G5.3 — Scientific readout: target-label correction and information parity

Date 2026-10-29; Intelligent Computing ICOMPUTING-D-26-01069.
Status: TECHNICAL SOURCE-ONLY PASS; NO HISTORICAL MATCHED-INFORMATION RESULTS; 85/100 SCIENCE NOT YET ACHIEVED.

## Original source semantics, a material correction

Original exante_target.py defines Y_raw = 60d stock forward return − beta_pre × 60d SPY forward return. Both run_exante_baseline_v0.py and run_probabilistic_xgb_v0.py call preprocess_legacy_targets on these raw values, yielding Y_model = clip(Y_raw, train q01,q99) − mean_clipped_target(ticker, TRAIN). The original Phase-II bootstrap uses target_model and therefore all Top-K historical level/delta/hit analyses use TRANSFORMED Y_model.

It is therefore incorrect to claim negative original selected Y_model means imply negative raw stock returns or P&L. The old selected-outcome differences on the common transformed target remain meaningful with original historical/provenance limits. One cannot invert model clipping to reconstruct stock returns by adding beta*SPY, and cash zero return is not comparable to zero transformed model target.

## Document corrections already created privately

- IC_G5_2_TARGET_SEMANTICS_CORRECTED_WORKING_20261029.docx: SHA256 f28625a544502d031b58c7a6894caec5ad0f93336d765d9745d72ce30ed3386d; rendered 19 pages.
- IC_G6_2_TARGET_SEMANTICS_CORRECTED_WORKING_20261029.docx: SHA256 dbfdf30097f2b40a7fb804a3875901bb7efdcc8c6c96458581145cbbc13b1d8b; rendered 6 pages.
- Corrected original abstract/methods/cohort/limitations/conclusion statements and G6 R1-04/R1-05/R2-05 responses. These are author-held drafts and NOT exact Editorial Manager-verified original source.

## Source-only PASS; what it does NOT say

GitHub Actions workflow 40849518820: SUCCESS, 18/18 tests; repo Tests 40849518794 SUCCESS. Source SHA 5f6e9d85363bf843cd3d94273db8d7001d239b46. Protocol committed ahead of core at 1b263aadd126b7168dbc97af6f416f7cdc849673.

12 synthetic tests cover same point/risk information across raw, soft and hard policy selection, validation-only IQR scale, capacity/abstention, original float32 semantics and no passed holdout outcomes. Six original-module synthetic fixtures verify training-only clipping/centering, unseen tickers, float32 and clipping noninvertibility.

No real old original target data accessed, no author permission to access old outcome labels under G5.3, no independent 60d test, no second authenticated ranker, no real portfolio P&L, no human authority effect. This CI pass is NOT a scientific old-outcome efficacy result.

## New close literature challenge

- Anis and Kwon (2025), End-to-end, decision-based, cardinality-constrained portfolio optimization, European Journal of Operational Research 320, 739–753, DOI 10.1016/j.ejor.2024.08.030. Do not claim first capacity-constrained decision evaluation.
- Tu and Li (2024), Robust portfolio selection with smart return prediction, Economic Modelling 135, 106719, DOI 10.1016/j.econmod.2024.106719. Do not claim first decision-aware risk filtering.
- Cho (2026), When uncertainty doesn't help: Operator learning ignores belief uncertainty in portfolio optimization, Finance Research Open 2(2), 100107, DOI 10.1016/j.finr.2026.100107. Already explicitly separates additional inputs from additional information: PRIORITY direct antecedent to verify by full text; no first-ever information parity novelty claim.
- Zhang et al. (AAAI 2026), Coverage-Constrained Human-AI Cooperation with Multiple Experts, DOI 10.1609/aaai.v40i21.38866. Coverage with human/AI has existing literature.
- Kou et al. Financial Innovation 2026 already cited [4] in original manuscript.

Potential bounded contribution: historical finance-news case of a frozen ranker + validation-frozen calibrated P10 hard gate + matched Top-K and documented adverse ordinary volatility screen + source-sensitive counterfactual audit. The new equal-information comparison is an UNEXECUTED design, not a proven distinct algorithm.

## Hard 85-point gates

1. Independently verify original V0 continuous point ranking predictions and continuous risk-score features for V2/V3/V4; boolean masks alone are inadequate.
2. Freeze and obtain explicit owner authorization for source SHA-pinned old historical post-outcome exploratory study before target access; report ALL cohorts/arms, failures and paired calendar-aware caveats. Do not tune the soft coefficient to favorable old outcomes.
3. Obtain raw untransformed event-level absolute stock/market returns and audited price vintage, corporate actions, cash alternative and capital ledger before any economic claim.
4. Genuine compatible preexisting alternate frozen ranker, otherwise NO-GO (legacy baseline script is not sufficient).
5. No authenticated new independent 60-day outcome-blind cohort currently.
6. Finish G5/G6/G7 Editorial Manager source-matching, verbatim reviewer comments, figures and signatures by 2026-11-25.

## Fixed scoring

G4.12 science 63.53/100, prior G5.1/G6.1 manuscript improvements only provisionally ~67.1/100. A documentation-only conditional ceiling ~74.4/100, authentic economic + information-matched experiment scenario ~80.6/100 and with genuine second ranker ~84.4/100. ALL are diagnostic scenarios, not proof achieved. Newly discovered target semantics removes a prior overclaim but DOES NOT fulfill gross/net P&L reviewer requests. 18 synthetic source tests earn engineering credibility only, not 85 points.
