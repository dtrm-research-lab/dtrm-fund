# Beat the Machine III: Robust Decisions Under Model Uncertainty

## Preregistered Temporal Replication of a MaxMin Decision Layer for Equity Selection

**Working manuscript for SSRN**

**Author(s):** [Human author(s)]  
**Affiliation:** DTRM Research Lab  
**Series:** Beat the Machine  
**Status:** Draft v0.1 — Abstract, Introduction, contribution disclosure, and future-research bridge

---

## Abstract

Modern machine-learning systems increasingly produce calibrated scores, quantiles, and uncertainty estimates, yet the final action is often still obtained by ranking a point prediction and selecting the largest values. This paper studies a different question: whether realized decision quality can be improved without retraining the predictive model, solely by changing how a frozen probabilistic information state is converted into action.

We introduce MM1, a preregistered MaxMin decision layer for Top-K equity selection. MM1 receives only frozen Phase-2 ex-ante signals: a baseline point estimate, a calibrated lower-tail estimate, baseline rank, and the promoted probabilistic guardrail. For each eligible candidate, the gap between the baseline and calibrated lower-tail estimate defines an asset-specific downside width. A budgeted adversarial uncertainty set then permits a limited fraction of selected positions to realize downside simultaneously. MM1 chooses the exact-K subset that maximizes its own worst-case mean value, while preserving a preregistered fallback and deterministic tie hierarchy.

The predictive models, calibration offset, guardrail threshold, uncertainty budget, objective, optimizer semantics, and promotion criterion were frozen before realized outcomes were accessed. On the preregistered V5 temporal holdout, MM1 improved realized Top-K target-model value relative to the promoted Phase-2 guardrail by 0.05725 and increased hit rate by 5.49 percentage points. A preregistered news-event-cluster bootstrap produced a 95% interval for the value difference of [0.04347, 0.07486], although ticker-cluster sensitivity was materially wider and included zero. The identical frozen MM1 policy was then evaluated prospectively on the non-overlapping V6 holdout, with no V5-driven retuning. MM1 again improved realized decision value, by 0.11065, and increased hit rate by 15.86 percentage points.

These results support temporal replication of positive incremental decision value from a robust decision layer relative to an already-promoted probabilistic ranking rule. The study does not establish absolute profitability, causal market effects, or uniform robustness across dependency structures. More broadly, the findings motivate a separation between prediction and decision: the machine may estimate uncertainty, but the decision rule still determines how that uncertainty is acted upon.

**Keywords:** robust optimization; MaxMin; uncertainty; equity selection; machine learning; decision rules; preregistration; human-in-the-loop; temporal replication; financial AI

---

# 1. Introduction

Machine learning in finance is commonly framed as a prediction problem. Models are trained to estimate future returns, rank securities, classify events, or infer conditional risk. Progress is then evaluated by asking whether a new model predicts more accurately than the previous one. This framing is natural, but incomplete. A prediction is not yet a decision.

Once a model has produced a score, probability, or predictive distribution, a second problem begins: how should those estimates be converted into action? In many practical systems the decision rule is far simpler than the model that precedes it. Securities may be sorted by a point forecast and the highest-ranked observations selected. A lower-tail estimate may be used as a veto. A probability may be compared with a threshold. These rules can be effective, but they also imply that substantial modelling effort is followed by a comparatively thin decision layer.

This paper studies whether value can be created at that second layer while leaving the predictive system unchanged.

The work is the third stage of the *Beat the Machine* research programme. The programme is not based on opposition to machine intelligence. Its central hypothesis is instead that increasingly capable machines do not eliminate the importance of problem definition. A machine can search a large decision space, estimate conditional outcomes, and solve an optimization problem. It does not thereby determine which uncertainty should matter, what constraints should bind, when a previous policy should be preserved, or what evidence should be required before a new decision rule is promoted. Those are design choices.

The guiding principle is therefore simple:

> **The machine searches. The human defines the game.**

In the preceding phase of this programme, a deterministic equity-ranking model was extended with probabilistic downside information. A calibrated lower-tail estimate was used as a guardrail: baseline order was preserved, candidates failing the lower-tail threshold were skipped, and selection continued down the baseline ranking until the required Top-K cardinality was reached. That intervention improved realized decision value over the deterministic predecessor on the promoted Phase-2 cohorts. The relevant consequence for the present paper is that Phase 3 does not begin from a weak baseline. It begins from the strongest already-promoted probabilistic decision rule.

The Phase-3 question is therefore deliberately narrower and more demanding:

> **Can a robust decision rule improve realized Top-K equity selection relative to an already-promoted probabilistic guardrail while the predictive models, uncertainty estimates, information set, and evaluation rule remain frozen?**

Answering this question requires separating model uncertainty from decision robustness. Let the baseline prediction for candidate i be b_i and the calibrated lower-tail estimate be l_i. The downside width is

\[
d_i = \max(0, b_i - l_i).
\]

Rather than interpret this lower-tail information only as a binary veto, MM1 treats it as a candidate-specific adverse-deviation scale. For a selected set S of fixed cardinality K, an adversarial scenario takes the form

\[
y_i = b_i - z_i d_i, \qquad 0 \leq z_i \leq 1,
\]

subject to a budget

\[
\sum_{i \in S} z_i \leq \rho K.
\]

The robust value of S is the minimum mean value attainable under that budgeted uncertainty set, and MM1 chooses the eligible exact-K set maximizing this worst-case value. The uncertainty budget rho is not fitted to the eventual Phase-3 outcomes. It is frozen ex ante from the predefined calibration procedure. Likewise, the candidate information state contains no realized forward return, no target-model outcome, and no post-event information.

This design allows a particularly clean comparison. The predictive models do not change. The baseline scores do not change. The calibrated lower-tail estimates do not change. The Phase-2 guardrail does not change. Only the mapping from the frozen ex-ante information state to the final exact-K action changes.

The study also places unusual emphasis on governance and outcome blindness. Before realized evaluation, the project froze the Phase-2 model iterations, lower-tail calibration offset, guardrail threshold, uncertainty budget, MM1 objective, eligible action set, fallback rule, tie hierarchy, and optimizer semantics. For each confirmatory cohort, the exact Phase-2 and MM1 actions were generated and committed before the corresponding target-model vector was constructed. Large local artifacts were bound to tracked manifests using SHA-256 digests. After outcome access, MM1 reoptimization, threshold retuning, rho retuning, model retraining, and result-driven row deletion were forbidden.

The primary holdout, V5, covers a new temporal cohort following the previously consumed Phase-2 evaluation windows. MM1 produced a non-champion intervention with positive ex-ante robust lift. Once the frozen decision manifest had been committed, realized targets were constructed under the same 60-calendar-day forward-return semantics and the same frozen Phase-2 preprocessing rules. Relative to the promoted Phase-2 guardrail, MM1 increased realized Top-K target-model value by 0.05725. The selected-action hit rate increased from 65.55% to 71.04%.

The preregistered primary uncertainty analysis resampled news-event clusters with policy recomputation inside each replicate. Across 10,000 replicates, the 95% percentile interval for the realized value difference was [0.04347, 0.07486], excluding zero. This is supportive evidence under the prespecified news-event clustering unit, not a claim of universal statistical significance. A prespecified ticker-cluster sensitivity analysis produced a substantially wider interval, [-0.01888, 0.14999], which included zero. The latter result is retained as an explicit limitation because repeated securities and cross-sectional concentration remain relevant dependencies in this setting.

The strongest test of the method, however, is temporal replication. V6 was preregistered before its 60-day target window was mature and was explicitly designated as a future replication holdout rather than an alternative cohort that could replace V5. The exact V5 policy — including rho, the Phase-2 threshold, the robust objective, fallback semantics, promotion direction, and decision logic — was carried forward unchanged. V5 outcomes were forbidden from altering V6 policy.

After V6 target maturity, the previously frozen actions were evaluated. Phase 2 achieved a realized target-model mean of -0.10182, while MM1 achieved 0.00883, yielding an incremental difference of 0.11065. Hit rate increased from 41.86% under Phase 2 to 57.72% under MM1, a difference of 15.86 percentage points. No MM1 reoptimization, model retraining, rho retuning, threshold retuning, or action substitution occurred between the V5 and V6 evaluations.

The contribution of the paper is therefore not a claim that robust optimization guarantees market profits. It is more specific. First, it demonstrates that an explicit decision layer can add realized value even when the predictive system is frozen. Second, it provides a budgeted MaxMin formulation that converts lower-tail uncertainty into a portfolio-selection criterion rather than only a veto. Third, it evaluates that rule under an outcome-blind, manifest-based research design. Fourth, it obtains a positive prospective temporal replication using the same frozen policy on a non-overlapping cohort.

This distinction matters beyond equity selection. As AI systems become increasingly capable of generating forecasts and uncertainty estimates, the final policy layer becomes a central object of study. A high-capacity model can expand the search space, but the objectives, constraints, fallback rules, and evidentiary gates remain choices. Better machines do not uniquely determine better decisions.

The remainder of the paper is organized as follows. Section 2 positions the work relative to probabilistic ranking, robust optimization, and human-defined decision systems. Section 3 describes the frozen Phase-2 information state and the Phase-3 preregistration. Section 4 formalizes the MM1 uncertainty set and exact-K robust objective. Section 5 presents the outcome-blind implementation and solver design. Section 6 reports V5 confirmatory results and dependency-aware sensitivity analyses. Section 7 reports the preregistered V6 temporal replication. Section 8 discusses interpretation, limitations, and the distinction between predictive quality and decision quality. Section 9 outlines a next research stage in which the point-in-time information state is replaced by a learned temporal state.

---

# 2. Contributions and Scope

The paper makes four principal contributions.

1. **Prediction–decision separation.** It isolates the incremental value of a decision rule by keeping the predictive models, calibration, lower-tail estimates, and reference guardrail frozen.
2. **Budgeted MaxMin decision layer.** It introduces an exact-K robust selection rule in which candidate-specific lower-tail gaps define downside widths and an ex-ante uncertainty budget limits simultaneous adverse realization.
3. **Outcome-blind confirmatory workflow.** It binds candidate states, actions, policy parameters, and realized-data stages through tracked contracts, manifests, and cryptographic hashes before outcome access.
4. **Prospective temporal replication.** It reports positive incremental realized decision value in both the preregistered V5 holdout and the non-overlapping V6 replication holdout under an unchanged policy.

The scope is deliberately narrower than several possible interpretations of these results. MM1 is evaluated relative to the promoted Phase-2 probabilistic guardrail, not relative to the market itself. The paper therefore makes no claim of absolute profitability, guaranteed alpha, causal market impact, minimax-equilibrium equality, or uniform robustness to every dependency structure. The ticker-cluster sensitivity result is retained precisely because the evidence does not support such a stronger statement.

---

# 9. Future Research: From Point-in-Time State to Temporal State

The present framework improves the decision rule while holding the information state fixed. This creates a natural next question: should the information state itself remain point-in-time?

MM1 currently receives a compact ex-ante state composed of the current news–ticker pair, baseline prediction, calibrated lower-tail estimate, rank, and Phase-2 eligibility flag. This design is intentionally austere and was essential for isolating the contribution of robust decision-making. It does not, however, explicitly represent the path by which an asset arrived at that state.

A next stage of the *Beat the Machine* programme will investigate a learned **temporal state**. Instead of representing a candidate only through Z_t, the system would encode a chronological sequence of heterogeneous asset events,

\[
E_{i,1}, E_{i,2}, \ldots, E_{i,t},
\]

and learn a latent state

\[
h_{i,t} = f(E_{i,1:t}).
\]

The motivating analogy is recent work on financial event-sequence foundation models. PRAGMA, for example, pretrains a Transformer-based architecture on heterogeneous banking event sequences using self-supervised masked modelling and produces reusable representations for downstream financial tasks. The proposed extension here is not to import PRAGMA directly or replace MM1 with a Transformer. Instead, the research question is whether a richer sequential representation can improve the information state supplied to the already-established robust decision layer.

The intended comparison is therefore conceptually:

\[
\text{Point-in-time state} \rightarrow \text{uncertainty} \rightarrow \text{MM1}
\]

versus

\[
\text{Temporal state} \rightarrow \text{uncertainty} \rightarrow \text{MM1}.
\]

This preserves the central separation developed in the present paper. Representation learning may improve what the machine knows about the path into the current state; robust optimization still determines how the frozen uncertainty state is converted into action. In the language of the broader programme, the machine expands and compresses the search space, while the human-defined decision architecture continues to define the game.

**Reference to be incorporated in bibliography:**  
Ostroukhov, M., Mikhailov, R., Iashin, V., Sokolov, A., Akshonov, A., Protasov, V., Beloborodov, D., Mullin, V., Yokunda Enzmann, R., Kolovos, G., Renders, J., Nesterov, P., and Repushko, A. (2026). *PRAGMA: Revolut Foundation Model*. arXiv:2604.08649.

---

# Contribution and AI-Assistance Disclosure

## Human contribution

The human author(s) retain responsibility for conceptualization, research questions, methodological choices, preregistration, experimental governance, data-access decisions, interpretation of results, claim boundaries, validation, supervision, and final manuscript approval. All decisions to freeze or amend scientific contracts, all promotion criteria, and all interpretations of V5 and V6 evidence remain human decisions.

## OpenAI Agent contribution

**OpenAI Agent (OpenAI; GPT-5.6 Sol)** contributed as an AI research and engineering assistant under human direction. Its contributions included software-engineering assistance, code and contract review, reproducibility and consistency checks, experimental documentation, manuscript structuring, drafting, language editing, and synthesis of already-authorized research artifacts. The agent also assisted in maintaining explicit information-firewall rules during the staged Phase-3 workflow.

### AI-assistance disclaimer

The OpenAI Agent is not an author and is not presented as an independent scientific decision-maker. It cannot accept responsibility for the integrity, interpretation, or publication of the work. It did not possess authority to change frozen hypotheses, objectives, uncertainty definitions, promotion rules, or evaluation criteria on the basis of realized V5 or V6 outcomes. Scientific judgment, verification of generated material, interpretation of evidence, and responsibility for the final manuscript remain with the human author(s). Any AI-generated text, code, or analytical suggestion used in the research was subject to human review before acceptance into the project.

---

# Draft Bibliography Placeholders

- [Beat the Machine I — full citation to insert]
- [Beat the Machine II — full citation to insert; SSRN DOI to verify in final bibliography]
- [Robust optimization / budgeted uncertainty foundational references]
- [Financial machine-learning ranking / uncertainty references]
- [Human-in-the-loop / decision-support references]
- Ostroukhov, M. et al. (2026). *PRAGMA: Revolut Foundation Model*. arXiv:2604.08649.

---

## Drafting status

**Completed in v0.1**
- Working title and subtitle
- Abstract
- Introduction
- Contribution and scope statement
- Future-research bridge to temporal state / PRAGMA-inspired Phase 4
- OpenAI Agent contribution and AI-assistance disclosure

**Next sections to build**
- Related Work
- Phase-2 frozen baseline and information state
- MM1 mathematical formulation
- Exact optimization and tie hierarchy
- Preregistration and information-firewall methodology
- V5 results and bootstrap/sensitivity evidence
- V6 prospective replication
- Discussion and limitations
- Conclusion
- Full bibliography
