# G4.10 — Decisive novelty adjudication and G5 authoring release

**Manuscript** ICOMPUTING-D-26-01069, candidate original author-held manuscript SHA256 `811c571ba30fc175878be5fe70fd7bcc55e551a9773d19401ce561da892b1085`.
**Date:** 2026-10-28. **Decision:** **GO TO SUBSTANTIVE G5 MANUSCRIPT REVISION under bounded empirical contribution; NO CLAIM OF STRONG ALGORITHMIC/GOVERNANCE NOVELTY PASS.**
**Ethical constraints:** do not describe this as new confirmatory evidence, a second independent ranker, a new non-overlapping 60d holdout or an intervention with human participants. PRs #50, #51, #52 are engineering/exploratory experiments, **not admissible human-governance efficacy results**.

## 1. What is the contribution that survives prior-art challenge?

We **do not** claim to invent reject options, thresholded admissibility, human decision rights, decision-focused optimization, risk filtering, source hashes or model risk management.

The bounded contribution of **this submitted work** is the **documented empirical comparison of decisions induced by separately calibrated uncertainty/feasibility rules around one previously frozen financial ranker**, with fixed capacity K, a validation-frozen original threshold, outcome and bootstrap sensitivity, negative feasibility and replacement variants, and a direct adverse conventional-risk comparator **explicitly retained after it refutes specificity/superiority of P10**.

This is **an original domain-specific experimental result/case study** if source authenticity, methods and claims are independently checked. It is **not** a demonstrated novel algorithm, causal effect of human authority, or guaranteed *major advance* for the journal. The journal can reasonably judge the contribution too incremental. Accept that risk rather than inventing originality.

Most differentiated *observed* aspect is **the asymmetry between the ranking's predicted ordering and the downstream observed beta-adjusted target under alternative pre-specified admissibility policies** and a *refutation-driven evaluation* of the initial favorite rule. Even that phenomenon is known conceptually in decision-focused ML; the new element is its particular frozen financial experiment, not a fundamental discovery that predictions are fallible.

## 2. Prior art: negative-control comparison at the CLAIM level

| Proposed novelty | Closest antecedent / already known | Source-specific experiment outcome | Judgment |
| --- | --- | --- | --- |
| Human specifies goals rather than computes every ranking | Kou et al., *Human–AI hybrid finance: from AI tools to decision systems*, 2026 (original ref [4]) | Human-specified objective and rules documented, no human intervention randomized | **NOT NOVEL / philosophical motivation only** |
| Selective abstention/risk–coverage rules | Geifman & El-Yaniv 2017/2019 selective prediction | Top-K eligibility with fail-closed insufficient candidates, frozen q25-of-P10 | **KNOWN MECHANISM, specialized application** |
| Prediction ≠ downstream decision utility | Wilder et al. AAAI 2019 decision-focused learning | Fixed model score ordering versus 60d forward beta-adjusted targets | **KNOWN PRINCIPLE, observed case** |
| Lower-tail probabilistic veto superior to conventional risk filter | Financial risk-screening conventional antecedents | P10 vs volatility: V2 −0.0886291; V3 −0.0918325; V4 −0.0440593 | **REFUTED as a generic superiority claim; A3 retrospective and historical vendor-vintage caveat** |
| Hybrid human judgment outperforms agent autonomy | Madras et al. 2018; Vaccaro et al. 2024; Kou et al. 2026 | NO actual human arms in original V2/V3/V4 | **NOT IDENTIFIED** |
| Meaningful human appeal/decision authority can be audited | Prior contestability and human oversight literature; regulatory risk-management traditions | Original guardrail gate + source audit, later 9a–c synthetic mechanism tests, human N=0 | **TECHNICAL WORKFLOW POSSIBILITY ONLY, NO HUMAN BENEFIT** |
| Exact provenance and candid adverse findings | Open science/reproducibility practices | Original fixed rule, negative V0/V1, V2/3/4, clusters, A2/A6, A3 comparisons | **VALID SCIENTIFIC HYGIENE, not first provenance idea** |

## 3. Precise results this article MAY claim, not more

Original P10 q25/K=10% vs unfiltered same ranker, historical Top-K mean **`forward_excess_beta`** differences:
- V2 +0.14429480582475662, baseline −0.1949552, candidate −0.0506604.
- V3 +0.14943748898804188, baseline −0.1790372, candidate −0.0295997.
- V4 +0.027561593800783157, baseline −0.0545888, candidate −0.0270272.
- V2/V4 original **ticker-cluster nominal 95% confidence intervals include zero**; V4 four of six weekly slices favorable; all guarded mean absolute targets negative.
- V0 quantile replacement ranker failed; V1 P10>0 veto admitted **zero** of 40,320 available rows.
- G3.1 post-original exploratory A2/A6 sensitivity: 18 policy × cohort appearances, **15 distinct**, q25/K10 duplicated; multiple comparisons and different RNG-reseed bootstrap intervals, NOT independent replication.
- G3.2 **retrospective** trailing-volatility risk veto relative to unfiltered baseline: +0.23292389139533043 (V2), +0.24126996472477913 (V3), +0.07162084616720676 (V4). This filter performs better on observed historical means than P10 in **all three cohorts**. Six original-source paired nominal cluster CIs exclude zero in favor of volatility but are post-outcome and non-multiplicity-adjusted. **Original market vendor historical acquisition/vintage unavailable**, preventing authentic point-in-time traded feasibility claims.
- Overlapping 60-day target windows; no authenticated unused nonoverlapping 60-day holdout, no independently frozen second ranker, no measured real P&L/cash-vs-portfolio, no causal governance effect or actual human-control noninferiority. Do not claim general model-agnostic **empirical** validation.

## 4. Scientific claim ladder: originality **not** a binary vote

**PASS bounded empirical:** 'Under a frozen rank-and-capacity setting, explicit validation-frozen eligibility changes selected actions and observed historical forward beta-adjusted targets; sensitivity and a conventional comparator expose dependence on rule choice.' Scope one ranker, three overlapping historical targets.

**PASS procedural:** 'A research contract that freezes ranker/capacity/threshold can support traceable accept/reject decisions and candid failure recording.' This is an implementation/case study, not novelty of explicit contracts.

**DISCUSSION only:** 'Decision authority over objectives and eligibility remains a meaningful research/governance issue despite machine prediction capability.' No human intervention tested.

**FAIL as result:** 'Human-defined risk guardrails in general outperform machines', 'P10 is best', 'HDPG causes human accountability', 'AI without humans is worse or noninferior', 'three independent 60d replications', 'tradable excess return', 'full model-agnostic empirical demonstration'.

## 5. Two useful falsifiable implications, clearly labeled *conceptual, not newly validated theories*

1. **Score optimum / outcome mismatch:** If s is the frozen ranker score, the unfiltered Top-K must maximize the sum of s among feasible K-subsets; adding a veto cannot improve that objective. It may change later observed Y because s is an imperfect proxy and a veto introduces extra information. **This is basic constrained optimization and not an original mathematical theorem.**
2. **Controller-label non-identification:** With identical input, policy and deterministic executor, a 'human' or 'machine' policy-owner label changes no action. To test effective authority, vary and record who can select/refuse/revise g and measure real behavior and utility. G4.9a–c synthetic tests show implementation possibilities, **not** human effects. **This is an identification boundary, not a Human Clause performance result.**

## 6. Final editorial choice

**Do not start another optimization/seed search or hunt for 'alpha' to force novelty.** The initial G4.9c learned synthetic rule was almost replicated by a transparent `score-w*risk` rule; this is adverse to an incremental ML method claim, not to the prior financial original experiment.

**GO G5 now** on original source with title/sections retained and a conservative manuscript contribution:
- State the experimental question as *policy-induced decisions around frozen predictive ranks*, not 'human versus AI performance'.
- Explicitly contrast Kou (authority architecture), Geifman (selective abstention) and Wilder (downstream utility); describe present work as one empirical instance with an inspectable, validation-frozen Top-K risk-veto protocol.
- Prioritize the conventional volatility negative comparator as a **main Results + Discussion** finding, not obscure supplementary material.
- Explain original date protocol vs overlapping 60d outcome independence, two cluster schemes/RNG lineage, negative absolute means, missing actual return/fees and price vintage.
- Separate tested software enforcement/frozen source and **untested** accountability/real human control.
- Maintain four original journal-required body sections, figures and author declarations.

**GO G6 concurrently**: reviewers receive a row-by-row response *in the manuscript itself*, acknowledging that R1 nonoverlap holdout, second ranker and economic return arms were not completed. Do not claim their critiques were resolved by synthetic G4.9c.

## 7. Limited blockers to final editorial shipment (not blockers to working G5 draft)

1. Verify author-held `FINAL_v2.docx` exact identity against Editorial Manager. For now every revised manuscript must say **CANDIDATE REVISED WORKING DRAFT**, not certified submitted-version redline.
2. Read independently G3.1/G3.2 aggregate original JSON and complete original-vs-new bootstrap interval lineage proof.
3. Require final G5 article and 22 E/R6 point-by-point answers, plus separate editable figures/forms by 2026-11-25.
4. Journal editorial and independent adversarial reader decide whether a bounded empirical contribution is a sufficient *major advance*. No self-issued guarantee.

**G4.10 adjudication:** The search for a grand, previously unknown 'human > machine' theorem is **closed without evidence**. The original contribution's scientific path is **conditionally viable** as a bounded, reproducible empirical financial decision-policy comparison. G5/G6 authoring is **AUTHORIZED NOW**. The possibility of reviewer rejection for insufficient theoretical innovation remains candidly open.
