# G4.2 — Editorial/scientific pivot brief (HDPG revised article + future Human Clause research)

**Case:** ICOMPUTING-D-26-01069  
**Status:** WORKING, ADVERSARIAL REVIEW OPEN; not manuscript text, not a retrospective revised preregistration.  
**Decision:** adopt a narrower experimental claim while articulating a wider **future governance hypothesis**. Do not rename the old experimental intervention or change a historical endpoint.

## 1. Distinguish four concepts which reviewers could otherwise collapse

1. **Prediction / ranking:** the original frozen model maps historical feature rows to scores and a fixed candidate ordering.
2. **Algorithmic decision constraint:** a deterministic policy (original q25 on calibrated P10, or retrospective conventional volatility veto) filters admissions while preserving a fixed Top-K rule.
3. **Human-specified governance:** people select objectives, admissible restrictions and what outcome to evaluate. This is a *design act* in the current study, not an observed randomized human intervention.
4. **Institutional authority/accountability:** consent, veto, appeal, ownership of consequences, dynamic correction. These are normative/governance propositions and can be operationalized in future systems; they were not experimentally measured in the existing investment test.

**Cannot infer:** (2) outperforms all machine policies; (3) causally adds value over (2); (4) improves welfare; human-governed system is statistically noninferior to autonomous system.

## 2. Proposed narrow question and method for THIS research article

**Question:** What changes, and with what uncertainty, when explicit frozen admission rules and selection-capacity constraints are applied to a fixed machine ranking of historical finance events?

**Treatment:** same original ranking on matched eligible observations; baseline/unfiltered vs original P10 veto, with validation-only cutoff; supplementary post-outcome exploratory variation of q15/q25/q35, K5/10/15, and pre-event dated trailing-stock-volatility comparator calibrated on V0 validation.

**Estimand:** difference in mean 60-calendar-day beta-adjusted forward target and positive-target hit fraction under the same frozen row/selection design; NOT net economic trading return, NOT a causal value of a human person.

**Result to foreground:** original P10 improvements over no-veto baseline are observed in V2/V3/V4, with many ticker CIs admitting zero; retrospective conventional volatility exceeds original P10 in all three point effects and six nominal direct ticker/news cluster comparison intervals exclude zero. Do not omit V1 zero-admission historical failure.

**Permissible claim:** an explicit, inspectable constraint interface changes model-output selection; the effect depends on which restriction is chosen. This demonstrates why governance policies require empirical audit and cannot be assumed beneficial simply because humans authored them.

**Unproven:** the claim that 'a machine without a human in control is not much better' because the historic 'machine-only' baseline also has human-specified goals and no explicit governance-control randomized arm. Likewise, the notion of 'free governance' requires cost/regret/utility metrics that were never measured.

## 3. Minimal mathematical formalization (expository; NOT presented as novel validated theorem)

Let D be the exact eligible cohort; s_i the frozen model rank scores; a_i(g) ∈ {0,1} the admission from a prespecified constraint g; and K = floor(k |D|). Define S(g,k) as the first K admitted records ordered by the original rank (a failure/abstention flag if fewer than K survive). The unfiltered reference is S(1,k).

An experimental difference in a fixed historical target y is: Δ(g,k) = mean_{i in S(g,k)} y_i − mean_{i in S(1,k)} y_i.

For a paired policy comparison on the same original observation universe: Δ(g1,g2,k) = mean_{i in S(g1,k)} y_i − mean_{i in S(g2,k)} y_i.

The existing source computes these fixed-capacity quantities, including paired re-ranking on identical cluster-resampled rows; the published contribution is **NOT** a proof of optimality over g, absence of dependence, or deployment-time implementability.

A **future** governance contract may additionally record purpose, authorized human owner, admissible constraints, a refusal criterion, evidence trace, challenge/revision interface and responsibilities. These metadata must not be retroactively described as empirically validated in original G3 runs.

## 4. Main novelty challenge: skeptical competing explanations

- **Skeptic A:** 'It is ordinary risk filtering / selective classification with a human label.' Response required: distinguish concretely from existing selective prediction and constraint baselines, disclose overlaps, and limit novelty to the exact audited protocol/architecture if there is no independent methodological novelty. Geifman & El-Yaniv (2017) already study risk-coverage/reject options.
- **Skeptic B:** 'Every model is built by humans; governance alone has no empirical effect.' Correct. Treat governance as explicit *specification and contestability*, not a causal human-in-loop performance factor. Operational benefits need separate instrumentation/experiment.
- **Skeptic C:** 'Volatility wins; therefore P10 and the proposed framework fail.' Concede no historical P10 superiority. A transparent comparison framework can reveal its own unfavorable policy, but novelty beyond conventional benchmarking is still to be argued, not presumed.
- **Skeptic D:** 'Nominal ticker CIs exclude zero for A3; your inference is universal.' They do not address overlapping 60-day outcomes, post-outcome use, price-provider vintage, multiplicity or prospective transfer.
- **Skeptic E:** 'You discovered no governance-performance cost.' Not tested; the historical favorable P10-vs-baseline contrasts are not human-governance noninferiority tests.

**G4 novelty gate:** make a table contrasting specific features with selective prediction/risk-coverage, policy filters, audit trails/decision logging, and human-AI governance frameworks. For every supposedly unique component identify evidence of implementation AND a published baseline that lacks it. Any unsupported novelty assertion must be deleted or weakened before G5.

## 5. Revised article architecture required by Intelligent Computing

Retain the original title/terminology unless editorial continuity review approves limited title change. Exactly **four main body sections** as prescribed for Research Articles, e.g.:

1. **Introduction:** motivation; explain machine optimization vs explicit governance specifications, related work and bounded experimental question. Avoid philosophical text as primary evidence.
2. **Materials and Methods:** frozen legacy ranking/target/row ordering, exact cutoff and K, preregistered-vs-postoutcome distinction, comparator calibration, bootstrap by news and ticker, code/data lineage. Include an Experimental and Technical Design diagram only if a compliant editable source exists.
3. **Results and Discussion:** original V1 failure and V2/V3/V4 effects, A2/A6 all cells, A3 full adverse comparator, intervals and overlap qualifications, no realized P&L. Place all material negative/null results in main text.
4. **Conclusion:** method-level takeaways and precise limitations; governance principle as interpretation, prospective authority/control experiments as future work.

Add abstract <=250 words, authorship/affiliations, author contributions, funding, competing interests, data availability, references, figure sources, supplementary source traceability. Verify one-column line-numbered template. The journal guidance presently requires exactly four prescribed top-level sections and separate editable figure files at revision; no figures created by exporting PowerPoint/Word graphic content. Case-specific editor letter may impose stricter requirements than general website guidance.

**No manuscript source/diff or editorial forms have been certified as available in the repo. G5 cannot be called complete from this document.**

## 6. G6 response strategy (outline, NOT a finished response letter)

Opening paragraph should acknowledge three substantive revisions:
(a) all relevant original uncertainty and negative results preserved;
(b) original predefined sensitivity and conventional volatility comparator explored with exact source safeguards and explicit post-outcome label;
(c) HDPG conclusion narrowed from human superiority to a reproducible, deterministic policy-evaluation mechanism with an important governance implication, without claiming causal human involvement.

For every reviewer item: point-by-point response, result (including negative/null) or documented limitation, exact manuscript section/line and figure reference AFTER G5 exists. Explicitly name the A3 adverse finding. Avoid declaring X1, A5 or A4 'satisfied' when empirically missing.

## 7. Separate future hypothesis (DO NOT add to revised article as a current empirical finding)

**Question:** Can legitimate human authorization of objective/constraint choices be preserved without materially harming measurable outcomes, while improving contestability/accountability?

A defensible new experiment would compare on matched tasks at least:
A. autonomous system executing a fixed authorized mission with its own policy selection within a specified delegation;
B. same system/model, resources and data under explicit human-approved policies;
C. agent-proposed policies subject to a transparent human approval/veto procedure.

Require actual human participants and measured interventions if the thesis claims *human* causal benefit. Preserve comparable objectives while distinguishing who has authority to change them; do not define 'autonomous' as a system without any human-designed objective.

**Preregister before observing outcomes:** task set, randomization/blocking, outcome utility and harm metrics, governance adherence, override/appeal and correction metrics, exposure/cost/latency, analysis units, multiple tests, power, attrition, minimum practically significant noninferiority margin δ, appropriate confidence-interval tests and failure criteria. Mere nonsignificance does NOT imply equivalence. A successful noninferiority result would remain domain-bound, not general proof about autonomous intelligence.

Possible prospectively instrumented domain: Guardian purchasing lifecycle (need → recommendation → verified delivery / returns). This is future work **outside** the present finance revision; it must not silently become additional evidence for the 2026 article.

## 8. Literature and policy sources requiring precise positioning

- Geifman Y, El-Yaniv R. Selective Classification for Deep Neural Networks. NeurIPS 2017. https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html — reject option / risk coverage baseline.
- Vaccaro M, Almaatouq A, Malone T. When combinations of humans and AI are useful: A systematic review and meta-analysis. Nature Human Behaviour (2024). https://doi.org/10.1038/s41562-024-02024-1 — mixed collaboration outcomes; not evidence of this HDPG intervention.
- Rudin C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nature Machine Intelligence (2019). https://doi.org/10.1038/s42256-019-0048-x — outer veto does NOT render XGBoost intrinsically interpretable.
- Gu S, Kelly B, Xiu D. Empirical Asset Pricing via Machine Learning. Review of Financial Studies (2020). https://doi.org/10.1093/rfs/hhaa009 — economic evaluation benchmark.
- Journal guidelines: https://spj.science.org/page/icomputing/for-authors — exact four main sections and figure/editorial constraints.

Do not overstate uniqueness or claim any of the cited papers validates HDPG. Bibliography needs G5 cross-check against prior manuscript and related manuscripts/preprints to avoid redundant/omitted citations.

## 9. GO / NO-GO decision record

- **GO:** G4 challenge and G5 preparatory structure and actual manuscript acquisition.
- **NO-GO:** authorizing any new original-data analysis, recalibration, promotion of a winning q/K from old outcomes, declaration of human-versus-autonomous equivalence, claim that G4 is closed, submission to editor before responses/manuscript/figures/forms match.
- **Entry to G5 full drafting:** independent challenge complete; source original manuscript identified and read; claim ledger reconciled; novelty over baselines at least precisely bounded. Missing original document may justify an outline but not a 'full manuscript revised' status.

**G4.2 remains OPEN.** These are proposed scientifically disciplined edits and future research ideas, not newly tested facts.
