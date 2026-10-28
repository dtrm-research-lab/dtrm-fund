# G4.7 — Novelty Challenge: direct prior-art comparison and construct-validity test

**Case:** ICOMPUTING-D-26-01069 | **Date:** 2026-10-28 | **G4 status:** ADVERSARIAL OPEN; NOT A NOVELTY PASS.
**Source:** external, checked publisher/meeting pages plus GitHub historical original code and operator-attested G3 aggregate reports. Literature review is a bounded targeted review, NOT an exhaustive systematic search.
**Scope:** clarify the strongest scientifically defensible new angle WITHOUT changing original targets, hypotheses, seeds, report contents or retrospective source vintage.

## Governing question

**Can an explicit decision-authority / admissibility contract add empirically testable value around a fixed machine ranking, without requiring a presumption that a human-authored rule or a machine-authored rule must always outperform the other?**

**Original experiment actually identifies a narrower contrast:** the change in historical 60-calendar-day beta-adjusted forward target when a *fixed ranker without an additional risk veto* is compared with the same fixed ranker under predeclared P10-q25 or a supplemental conventional volatility veto.

That baseline is NOT 'a fully autonomous machine free of humans'; training targets, data, K, objective and operational authority were all human-specified. P10 adds an independently calibrated tail predictive model, and volatility adds historical price-risk information. Hence historical improvements are not a clean causal effect of **human governance per se** and confound the existence of a rule with access to different auxiliary information.

## Prior-art confrontation: what is already known, what HDPG has, what remains unproven

| Prior work | Already established / cannot claim as new | What our existing HDPG source actually implements or evaluates | Novelty verdict |
| --- | --- | --- | --- |
| Geifman & El-Yaniv, NeurIPS 2017, *Selective Classification for Deep Neural Networks* | Reject/abstain by confidence/risk and trade off risk vs coverage, user-specified desired risk. | Deterministic admission veto over a frozen non-classification ranked financial universe, a fixed **filled Top-K**, original q25 threshold and a quantified comparison of fallback/feasibility. | **Application/engineering distinction**, not first reject-option or human-defined threshold. |
| Geifman & El-Yaniv, ICML 2019, *SelectiveNet* | Joint modeling of prediction and rejection; rejection itself is not novel. | Outer independent calibrated quantile P10 model is trained separately from frozen point ranker, so intervention is modular; no co-trained optimal rejection. | Modular non-retrained design is a choice, **not proven universally superior**. |
| Madras, Pitassi & Zemel, NeurIPS 2018, *Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer* | Explicit algorithm-human delegation and optimized referral to an external decision-maker. | No human is actually handed cases, no human action outcomes or human-bias adjustments measured; current veto is algorithmically executed. | **Cannot claim priority on human involvement/delegation or superior complementarity.** |
| Wilder, Dilkina & Tambe, AAAI 2019, *Decision-Focused Learning* | Predictive accuracy may misalign with actual decision utility; optimize downstream decision quality. | HDPG freezes original ranker, keeps decision objective separate and studies outcome effect of admissibility policies. | Separation and empirical audit can be useful; **mismatch between forecasts and decisions is established prior art**. |
| Dietvorst, Simmons & Massey, Management Science 2018, *Overcoming Algorithm Aversion* | Some human editing control can increase utilization and satisfaction with algorithms in experiments; desire for control already empirically explored. | No experiment on user preference, acceptance, satisfaction, control experience or human override frequency. | Normative control rationale is plausible but **not established by HDPG tests**. |
| Vaccaro, Almaatouq & Malone, Nature Human Behaviour 2024 | Meta-analysis across 106 studies/370 effects shows human+AI not automatically better than strongest component; performance task-specific. | Our single frozen-ranker filtering experiment is NOT a human-only / AI-only / human+AI comparison. | Cite as a **warning against either universal superiority thesis**, never a validation of HDPG. |
| Yurrita et al., PACM HCI 2025, *Identifying Algorithmic Decision Subjects' Needs for Meaningful Contestability* | Appeals, responsibility attribution and contestability are existing research objects; paper interviewed affected decision subjects. | Frozen rule and source hashes permit reproducible audits, but no actual affected human appeal/reversal measured. | Auditability not interchangeable with observed user contestability. |
| Kou et al., Financial Innovation 2026, *Human–AI hybrid finance: from AI tools to decision systems* | Explicit authority, oversight, accountability, delegation frontier and decision systems in finance; **already cited as [4] in original manuscript**. | HDPG is a concrete, narrow *fixed ranking + quantitative veto + source-bound evaluation* instance with adverse benchmark; no empirical authority-mapping experiment. | Closest conceptual competitor. **Do not claim new authority theory; maybe a quantitative case implementation**. |

## Formal observation: optimizing a score is not optimizing an unknown realized target

Let s_i be the frozen ranker's point score; y_i the later observed historical beta-adjusted forward target; q_i the separately trained P10 (or v_i pre-event-dated volatility); K=floor(0.1N); A_g(i) an eligibility rule. Fix the original eligible row set and ordering.

S0 = TopK_by_s(D,K) (ranker with no *additional* veto)
Sg = TopK_by_s({i in D: A_g(i)=1},K), if |{i:A_g(i)=1}|≥K; otherwise abstain/fail closed.

By construction ∑_{i∈S0} s_i ≥ ∑_{i∈Sg} s_i (the unfiltered Top-K is optimal for the **same score** over a superset of choices).

**Nothing follows for ∑ y_i** because s_i is a prediction, not a realized perfect oracle. A second signal q or v may correctly remove highly ranked but adverse-outcome selections. The positive old P10 and conventional-volatility deltas illustrate that the top-score optimum need not optimize later observed y.

**This is not a new mathematical theorem, nor isolated proof of human authority value.** The veto adds information; the original unfiltered baseline does not consume the same auxiliary tail/risk signal. The comparison identifies a *policy package effect* in old outcomes, not a controlled comparison between 'human' and 'machine' that equalizes information sets.

## Negative evidence that the revised manuscript MUST feature

- V0 replacement ranking failed; V1 absolute calibrated P10 > 0 admitted **zero**; do not omit failures.
- Original P10 q25/K10 vs no-additional-veto Top-K mean forward_excess_beta deltas V2 +0.14429480582475662; V3 +0.14943748898804188; V4 +0.027561593800783157. Original ticker clustered CIs include zero V2/V4; G3.1 exploratory reproduced means with different per-cell RNG CI streams.
- A3 conventional trailing volatility vs the same reference deltas V2 +0.23292389139533043; V3 +0.24126996472477913; V4 +0.07162084616720676.
- P10−volatility direct differences -0.0886290855705738, -0.09183247573673725, -0.04405925236642361 for V2, V3, V4. All six A3 **nominal/unadjusted** news/ticker CI bounds from operator-attested 60k bootstrap exclude zero in favor of volatility.
- Historical future outcome windows overlap; auxiliary price cache original archived 2026-07-05, after signal decision dates, provider acquisition vintage/corporate actions unverified; source inputs are licensed and partial unavailable, the post-outcome A3 design remains exploratory; no real funded portfolio return.
- Never say 'a machine alone performs worse than a human'. Say 'an unfiltered frozen ranking did not uniformly dominate its pre-specified constrained variants on this measured historical target.'

## Candidate claim taxonomy and novelty decision

| Claim | Decision |
| --- | --- |
| HDPG invented human accountability, meaningful oversight, abstention, or decision-focused optimization | REJECT: established prior literature. |
| HDPG empirically proves humans are better than AI | REJECT: no human-only or human-intervention arm. |
| HDPG proves machine autonomy without humans is not materially better than human-governed AI | REJECT: no randomized decision-rights manipulation, identical-information autonomous comparator, prospective margin or controller-outcome data. |
| A fixed ranked selection with explicit admissibility has different historic realized target performance than the same ranked selection without added veto | SUPPORTED IN REPORTED HISTORIC METRIC; requires strict target/confidence/provenance qualification. |
| Original P10 q25 beats conventional volatility on old cohorts | CONTRADICTED BY OBSERVED A3 EXPLORATION. |
| An inspectable and source-bound fixed-selection audit of contrasting policies yields falsifiable results, including adverse/null outcomes | SUPPORTED AS AN EXPERIMENTAL/ENGINEERING PRACTICE; its sufficiency as a novel *major advance* still unproven. |
| HDPG is a generic transferable governance architecture for many models/domains | DESIGN CLAIM ONLY; only one tested original ranker and no measured human accountability outcomes. |

**G4.7 decision: NO STRONG NOVELTY PASS.** The defensible editorial contribution is at most a transparent, controlled empirical *case study of pre-specified decision constraints around one financial model*, plus a carefully bounded governance interpretation. If reviewers demand new algorithmic or causal human-governance mechanism, existing evidence cannot honestly satisfy them.

## Verified references (targeted set, not systematic)

1. Geifman Y, El-Yaniv R (2017), *Selective Classification for Deep Neural Networks*, NeurIPS 30: https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html.
2. Geifman Y, El-Yaniv R (2019), *SelectiveNet*, ICML/PMLR 97: https://proceedings.mlr.press/v97/geifman19a.html.
3. Madras D, Pitassi T, Zemel R (2018), *Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer*, NeurIPS 31: https://papers.neurips.cc/paper_files/paper/2018/hash/09d37c08f7b129e96277388757530c72-Abstract.html.
4. Wilder B, Dilkina B, Tambe M (2019), *Melding the Data-Decisions Pipeline*, AAAI 33: https://doi.org/10.1609/aaai.v33i01.33011658.
5. Dietvorst BJ, Simmons JP, Massey C (2018), *Overcoming Algorithm Aversion*, Management Science 64(3), DOI 10.1287/mnsc.2016.2643.
6. Vaccaro M, Almaatouq A, Malone TW (2024), *When combinations of humans and AI are useful*, Nature Human Behaviour, DOI 10.1038/s41562-024-02024-1.
7. Yurrita M et al. (2025), *Identifying Algorithmic Decision Subjects' Needs for Meaningful Contestability*, PACM HCI, DOI 10.1145/3757415.
8. Kou G, Li Y, Wang H, Wang X (2026), *Human–AI hybrid finance*, Financial Innovation 12(125), DOI 10.1186/s40854-026-00941-w.

**No original data were reopened; G4.7 contains no new retrospective outcomes, no tuning, no policy promotion, no manuscript changes.**
