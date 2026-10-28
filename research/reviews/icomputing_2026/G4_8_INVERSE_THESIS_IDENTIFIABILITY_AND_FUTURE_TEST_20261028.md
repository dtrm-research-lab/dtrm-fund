# G4.8 — Inverse thesis: the absence of an additional veto is not presumptively optimal; human-authority hypothesis remains unidentified

**Case:** ICOMPUTING-D-26-01069, 2026-10-28.  
**Status:** DUAL-TRACK SCIENTIFIC POSITION, **G4 OPEN**; NOT a new empirical result, NOT G2 protocol modification.  
**Editorial goal:** rebut unjustified machine-vs-human dichotomy without importing an untested equivalence hypothesis.  
**Future scientific goal:** prospectively test whether retaining human decision authority can achieve a justified noninferiority margin in utility while providing demonstrably more effective contestability/oversight.

## A. Precisely what the inverse claim does and does not say

**Reject thesis H_human-universal:** 'Human-defined constraints always outperform a machine-generated selection.' Clearly not: A3 conventional volatility is stronger than specific P10; both filters and the baseline ultimately involve human-authored choices.

**Reject thesis H_machine-universal:** 'A fixed machine ranking without any additional admission filter always has better true downstream outcomes than adding an explicit, prespecified filter.' A narrowly bounded historical counterexample exists in the tested metric: P10 and volatility each had higher **observed** mean 60-day forward beta-adjusted targets than the unfiltered fixed Top-K ranking across V2/V3/V4. This refutes **universal dominance in that observed sample/metric**, NOT a universal hypothesis about autonomous machine governance. It is not out-of-time confirmatory nor independent cohort validation.

**Unmeasured thesis H_governance-noninferiority:** 'Real human authority over the rule set can be maintained without more than a substantively acceptable loss of final user utility relative to delegated autonomous authority.' The historic rank-and-veto experiment cannot test this; it changes rules/signals but not who held governance authority, human appeal, execution or subsequent behavior.

**A missing proof of machine superiority is NOT proof of machine-human equivalence.** Similarly, failure to reject a zero-difference null is not a valid noninferiority inference.

## B. Formal identification barrier for existing HDPG data

Observed decision under frozen scoring s, a deterministic rule g, original data D and budget K is:
a = F(D,s,g,K).

Let controller C ∈ {human, agent} describe who specified or authorized g. In the actual historical samples, g and its implementation F are fixed. If two controllers select the SAME g and have the SAME scores, data, budget and execution mechanism:

F(D,s,g_human,K) = F(D,s,g_agent,K) whenever g_human = g_agent.

Their selected rows and measured static forward targets are then **identical by construction**; no statistical analysis of those outcome rows can identify a separate *effect of the controller's identity*. The choice/legitimacy/process difference becomes measurable only if the controller can change g, manage exceptions, override, update goals, accept responsibility or contest decisions, and those variables are actually instrumented and compared.

This is a simple identification observation, NOT a novel theorem and NOT proof of governance superiority.

The original treatment **also changes the signal set**: calibrated P10 brings additional learned predictive information and conventional volatility brings additional price-history information. Thus even the observed policy-versus-unfiltered target difference is a *bundled policy + auxiliary information effect*, not an isolated effect of the label 'human' on a rule.

## C. Editorial claim ladder: what wording is admissible

| Level | Claim | Status for current revision |
| --- | --- | --- |
| L0 mechanical | A frozen point ranking and explicit deterministic admission rule can be combined at fixed K, with defined infeasible/refusal behavior | **SUPPORTED** by original source and historical gates. |
| L1 descriptive | In consumed V2/V3/V4, policy-constrained selections had higher observed mean 60d beta-adjusted targets than the same fixed ranker with no additional veto | **SUPPORTED** as an old historical point comparison; uncertainty/source caveats mandatory. |
| L2 algorithmic uncertainty | Some P10 v baseline effects robust under all nominal cluster schemes/cohorts | **NOT SUPPORTED**: q25/K10 ticker CIs include zero for V2 and V4; overlapping calendars and multiple comparisons remain. |
| L3 policy superiority | P10 is the best or uniquely beneficial way to control an ML ranker | **CONTRADICTED** in old A3 by conventional volatility comparator; additional source-vintage caution. |
| L4 human causal effect | A person retaining authority improves decisions relative to AI acting on the same information/rules | **NOT IDENTIFIED**: no randomized controller, measured overrides, or agent-chosen constraints. |
| L5 noninferiority | Human-governed system is within δ of autonomous system on utility at comparable task/resource conditions | **NOT TESTED**: δ must be chosen externally, prospectively, with valid CI/power. |
| L6 normative | Performance alone cannot by itself grant legitimate decision authority over goals and acceptability | **A REASONED GOVERNANCE CLAIM**, not an empirical conclusion or mathematical consequence of beta-adjusted target. |

## D. Why the finance experiment still matters

If scores s perfectly equaled future observed y, unfiltered Top-K would maximize y for that fixed K on that original universe, and an additional veto could not improve it. Actual scores imperfectly estimate unknown y, so filters using extra tail/volatility information can improve *historical* realized objective while reducing top-score admissibility.

Conventional volatility's historical greater improvement is valuable negative evidence: human-specified rules are **contestable rather than inherently correct**. Choosing P10 because it is a sophisticated probabilistic layer would be unjustified if a simpler validation-calibrated comparator does better.

Thus the evidenced lesson is **policy choice matters and must be audited**. The normative Human Clause claim that humans retain authority to specify and contest those policies is an interpretation and design priority, not the treatment measured here.

## E. Fair prospective experiment to actually test governance vs autonomous authority

**Do not execute under the existing G2/G3 finance protocol.** Freeze a *separate* new study before outcome labels/rewards. Proposed research domain: Guardian's need→candidate→transaction→verified-delivery lifecycle, with user-consented supervised test conditions; alternatively an independent investment deployment with demonstrably acquisition-time authentic sources and matured outcomes.

Define the subject of comparison as **who authorizes objectives and policy exceptions**, not whether any human ever shaped the software. Both baseline and human-governed agent MUST begin with an explicit user-authorized delegated scope, equal safety/legal protections and the same available information and model, task set, time and budget.

Suggested factorial or multi-arm design to isolate mechanisms:
- **A (delegated agent choice):** the same agent selects admissibility policy from a *predeclared safe menu* inside user-authorized mission; bounded execution and safety guardrails unchanged.
- **B (explicit human policy authorization):** the same agent, same policy menu/data/resources, but user selects or ratifies the policy before execution; user can refuse/contest according to fixed protocol.
- **C (agent proposes, user can challenge):** same agent and possible policies, explicit proposal/override logs and structured explanation; tests actual interaction/contestability. If A vs B performance differences arise from different choices of g, those are the *policy-selection effects of controller*, not a mystical effect of identity.
- **D (matched-policy mechanical control, if feasible):** agent follows the EXACT same fixed g in both formal authority labels; outputs should match, demonstrating that downstream y alone cannot identify authority and allowing process/equity differences to be studied separately.

**Pre-register primary estimands:** U(outcome actually delivered relative to user-provided need) and/or prospective finance utility defined on executable capital returns. Explicitly record safety/constraint violations, unjustified action rates, forced abstentions, correction rate, successful appeals, burden/latency, verified delivery, refunds and actual costs. Define the utility and adverse outcomes before data collection, with user/organization preferences fixed to avoid moving the target.

**Two requirements to defend governance preservation**:
1. **Utility noninferiority**: δ is a justified, meaningful *acceptable maximum loss* fixed before data. For difference Δ = E[U_B − U_A], the lower one-sided bound of appropriate confidence interval must be greater than −δ. No 'p>0.05' substituting for equivalence. If equivalence rather than noninferiority is claimed, need both predeclared lower AND upper equivalence margins and suitable test.
2. **Governance benefit**: predeclare a separate objective metric for effective authority/contestability rather than merely a UI control present; user *could actually block/correct* wrong proposed actions. Show improvement with a valid comparator and uncertainty, not no-op clicking.

Design safeguards: actual users consent to experimental task assignment; no deceptive high-stakes execution or unauthorized purchases, no change to policy after outcome knowledge, objective same across arms, independent review of consent/safety, appropriate unit-level randomization/blocking, clustering by participants/tasks, sample size/power, missing outcome/attrition policy and multiplicity plan.

## F. A productive falsification test for the new Human Clause claim

The proposed future thesis MUST be falsifiable. It is refuted/limited if:
- Human-authorization arm has a clearly unacceptable utility loss: CI lower bound below −δ, or credible excess risk/failed delivery.
- Control affordances are merely symbolic and do not increase timely user interventions/appeals when appropriate.
- Agent selection dominates under properly equalized information and policies, or added oversight predictably fails under workload.
- Governance improves after changing objective definitions ex post, selecting only successful users, or withholding adverse cases; not acceptable.

**The converse is also possible:** if governance preserves utility but adds no meaningful ability to contest/modify, that is NOT evidence of a Human Clause benefit. Our goal is joint evidence, not a 'no significant performance difference' headline.

## G. Safe manuscript-ready direction (discussion only)

'Our original experiment does not compare human deliberation with fully autonomous decision-making. It compares a frozen machine ranking with explicit deterministic admission constraints under fixed selection capacity. In the examined historical cohorts, the rank-only selection did not uniformly dominate the constrained selections on the measured forward beta-adjusted target. At the same time, a simpler conventional risk constraint yielded larger retrospective improvements than the original probabilistic rule. These observations motivate a separate question: whether authentic human authority over goals and constraints can be preserved with an acceptable prospective utility trade-off. Answering it requires matched-information, authority-manipulation and noninferiority designs absent from the present study.'

**Do not present the above as a new result.** It is a proposed interpretation and follow-up protocol, conditional on journal editorial acceptance of the narrowed scope.

## H. G4 → G5 decision

- **GO to provisional discussion drafting**, with quantified historic results, negative A3 finding and controlled claim ladder.
- **NO-GO** to a title/abstract claiming 'human vs autonomous machine' equivalence, or a post hoc δ fit.
- **NOVELTY remains OPEN**: prior art already covers reject option, human-AI deferral, decision-focused modeling, user control and financial hybrid governance. A reproducible *specific falsifiable contract* can be an engineering contribution, but journal 'major advance' remains a reviewer judgment requiring exact comparative mechanism articulation.
- **Further evidence priority:** read-only reconciliation of original/G3.1 CI streams, private aggregate-only G3.2 JSON QA, exact submitted manuscript confirmation; no further reanalysis of private original target unless newly justified and separately authorized.
