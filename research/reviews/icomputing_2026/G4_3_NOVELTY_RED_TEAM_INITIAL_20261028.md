# G4.3 — Novelty red-team, first pass (adversarial; NOT PASSED)

**Manuscript:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Status:** PRELIMINARY CHALLENGE, SOURCE-MANUSCRIPT GAP OPEN  
**Goal:** identify the strongest prior-art and construct-validity attacks *before* G5 rewrite. Sources below are a targeted, not systematic, comparison.

## Comparator matrix

| Existing literature/convention | Established idea | Potential HDPG contribution | Adversarial finding |
| --- | --- | --- | --- |
| Selective classification / reject-option methods (Geifman & El-Yaniv 2017) | Explicit risk/coverage tradeoff, selective abstention controlled by a user-specified risk target. | Frozen rank-and-select decision contract, explicit capacity/eligibility and exact row/source audit. | A veto, even one chosen by a human, is not novel by itself. Demonstrate distinctive artifact/operational contract rather than redefining selective prediction. |
| Conventional financial volatility filter / risk screens | Human-defined deterministic pretrade filters are long-established. | Same-ranker paired audit reveals how a probabilistic gate fares against a conventional veto. | This **competitor outperforms P10** in available A3 historical test; benchmark is retrospective with price-vintage limits. Do not claim best risk filter. |
| Interpretable or transparent high-stakes ML (Rudin 2019) | Accountability and interpretability of decisions are established demands. | External inspectable constraints around an opaque predictive ranking. | An auditable outer constraint does not make XGBoost predictions interpretable. |
| Human–AI complementarity experiments (Vaccaro et al. 2024) | Human+AI can lose to best standalone component; outcome depends on task. | Motivates testing governance-control independently from predictive synergy. | No human vs AI vs human+AI experimental arms here. Meta-analysis cannot be cited as causal evidence for HDPG. |
| Governance and accountability frameworks | Human control, traceability and accountability are established design/organizational concerns. | Engineering application in decision-rule freeze, reproducible source verification and reviewable policy effects. | Documentation alone is not proof of deployed human contestability, legitimacy, or incremental decision utility. |

## Strongest skeptical reviewer verdict

'The reported experiments are **one XGBoost ranking plus deterministic admission filters** under a fixed K. This resembles existing rejection/risk-screening methodology. The proposed broader Human Clause concept is normatively appealing, but the paper did not randomize human authority, observe human policy edits, or measure recourse, accountability, or loss of governance control. Novelty as superior human-in-the-loop inference is unsupported.'

**Adversarial response we can defend now:** accept the narrow experimental description, retain all adverse results, and explain any genuinely distinctive engineering contribution (frozen decision contract, binding source/target lineage, explicit failure handling, paired counterfactual policy audits) **only to the extent it is implemented and evidenced.** If those are only good research practices, present them as safeguards, not as invented algorithms.

**NOVELTY OPEN:** This first comparison cannot establish that the methodological contribution meets Intelligent Computing's 'major advance' bar. A reviewer could reasonably still call it an application of existing techniques. The original submitted paper and exact claimed novelty are required to evaluate changes.

## Construct-validity and inference attacks

1. *Machine-only* is a misleading label: the baseline ranker, data set, prediction target, risk budget and even the 'AI system' were chosen by humans. No independent variable 'human control present/absent' is manipulated.
2. *Human-defined* is not synonymous with *measurable human intervention*, nor with *human superiority*. The paper tests a deterministic algorithmic component.
3. A nominal CI excluding zero for a historical **P10–volatility** difference is not evidence of autonomous-vs-governed noninferiority. The former difference has the opposite sign, favoring volatility.
4. Bootstrap cluster resampling by news or ticker does not automatically protect dependence from overlapping 60-day market periods, repeated security exposure, or common macro shocks.
5. Policy-veto admission matched by validation news weights does not mean equal admitted historical pair counts; observed V2/V3/V4 risk veto admits fewer pairs than P10. Selection K was matched, so describe this fairly.
6. P10 q35 vs q25 *separate* CIs cannot test their paired difference; do not promote q35 or select K5 after seeing historical results.
7. Price archive later than signal date means the volatility feature's *dated bar lookback* is not an authenticated historical as-of adjustment/vintage.
8. Absolute forward_excess_beta means remain negative even where policy-to-baseline deltas are positive; neither 'profit' nor 'better than cash' is established.
9. Original exact submitted manuscript, figure set and bibliography have not been matched to the available G2/G3 source in this PR; until that occurs G4 cannot be signed off.

## Journal and literature sources verified for this initial audit

- Intelligent Computing author guidance: https://spj.science.org/page/icomputing/for-authors (Research Articles require a major advance; four prescribed main sections, 250-word maximum abstract, reproducibility/statistics and separate figure files at revision).
- Geifman & El-Yaniv. Selective Classification for Deep Neural Networks, NeurIPS 2017: https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html
- Vaccaro, Almaatouq & Malone. When combinations of humans and AI are useful: A systematic review and meta-analysis, Nature Human Behaviour 2024: https://doi.org/10.1038/s41562-024-02024-1 (106 experiments, 370 effects; pooled human+AI lower than best standalone component; not direct evidence for governance).
- Rudin. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead, Nature Machine Intelligence 2019: https://doi.org/10.1038/s42256-019-0048-x

## Critical additional prior art discovered 2026-10-28

**Kou G et al., "Human–AI hybrid finance: from AI tools to decision systems," Financial Innovation (2026), DOI: 10.1186/s40854-026-00941-w; published 2026-05-31.** This is a *particularly close conceptual antecedent*, not mere background. It explicitly reframes AI in finance from model prediction/performance to decision-system architecture, the allocation of authority, oversight, accountability, and contestability, and describes delegation frontiers, meaningful oversight and workflow auditability.

Source: https://link.springer.com/article/10.1186/s40854-026-00941-w

**Consequences:**
- Do **NOT** claim that Human Clause/our revised article is first to separate model performance from human authority, define meaningful oversight, or recognize an AI-assisted financial workflow as a sociotechnical decision system. Those general propositions are prominently present in a May-2026 peer-reviewed publication.
- Contrast the proposed **operational artifact and experiment** against this source: fixed risk/selection contract, validation-only cutoffs, exact source SHA boundary, point-parity preservation and policy comparison under matched Top-K, with documented negative findings. These may be valuable reproducibility properties; their novelty and generalizability still require honest, element-by-element comparison.
- Add this antecedent to G5 related work and G6 novelty argument with an accurate attribution. A stronger manifesto-like introductory claim without a new algorithm or evaluated governance-control outcome risks being insufficient for Intelligent Computing's 'major advance' criterion.
- Independently verify precise bibliography and overlap with the submitted manuscript before final citations.

This discovery *increases novelty risk* and strengthens the case for a narrower empirical/methodological contribution rather than broad priority claims.

**Source-specific correction (G4.4):** The candidate original August-2026 submitted manuscript **already cites Kou et al. 2026 as its reference [4] and discusses the human/AI decision-authority distinction in Introduction paragraph 10.** The earlier 'add this antecedent to G5 related work' is to be read as **strengthen the direct differentiation and avoid overclaiming novelty**, not as a newly discovered missing bibliography entry. See G4_4_ORIGINAL_MANUSCRIPT_TARGETED_READ_20261028.md. Candidate attachment SHA256 811c571ba30fc175878be5fe70fd7bcc55e551a9773d19401ce561da892b1085; Editorial Manager exact submission match remains unverified.

## Exit test for G4.3

Before G4 PASS, audit actual submitted abstract/title/introduction/contribution list; compare to these baselines at claim level, explicitly mark any claim requiring experiments which the submission does not contain, and agree a narrower novelty statement. A philosophical mission is not a substitute for a tested methodological advance.

**Disposition:** G4 NOVELTY = RISK / UNRESOLVED. G5 full rewrite withheld pending submitted manuscript source and independent adversarial agreement. 
