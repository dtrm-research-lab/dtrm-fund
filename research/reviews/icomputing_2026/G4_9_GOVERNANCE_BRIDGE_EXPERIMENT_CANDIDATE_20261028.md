# G4.9 — Human Clause authority–performance bridge: candidate for current IC revision, with explicit research gates

**Date:** 2026-10-28 | **Manuscript:** ICOMPUTING-D-26-01069 | **Status:** DESIGN CANDIDATE ONLY / NOT FROZEN / NOT EXECUTED / NOT EVIDENCE OF HUMAN GOVERNANCE EFFECT.

## Why not stop at the original rank-and-veto experiment?

The revision should not abandon the goal of understanding human decision authority. A reproducible policy-veto case study with only the current G3 finance results has **weak novelty** under the journal Research Article 'major advance' requirement. But the G3 financial data do **not** identify how much actual human approval/override rights cost in performance. The next question requires a new independent experimental factor: who can **approve, change, veto and challenge** a decision policy, not just which deterministic policy is applied.

**Core proposed research question (bounded):** Under the same ranking model, data and user-authorized mission, does adding *effective human policy authority* measurably change constraint compliance, correctability, operational burden, and task utility relative to bounded autonomous policy selection?

**Dual hypotheses, not assumed truths:**
- Mechanism H-M: externally enforced human-approved policies cause fewer **unauthorized actions** in test cases designed to challenge policy integrity than a specified autonomous rule-selection/enforcement implementation. Report all failures; do NOT make the comparison tautological by counting 'violations' only in one arm.
- Utility H-U: human-approval arm is **non-inferior** in a fixed, justified delivered-task utility, with Δ=U_human-authority−U_autonomy > −δ. The margin δ must be set before seeing outcome observations based on substantive user tolerance, cost, risk and statistical power; a nonsignificant difference is not evidence of noninferiority. If insufficient power/sample or a justified margin is unavailable, H-U remains **UNTESTED**.

## Provenance and methodological separation

- **Existing Article experiment / archival G3:** original frozen XGBoost, no-additional-veto Top-K versus original P10 vs volatility, fixed 60d forward_excess_beta, retrospective with overlapping targets, historically unverified provider-vintage, post-outcome exploratory comparator. Its data cannot be retroactively relabeled as human-governed vs autonomous.
- **New experiment / G4.9 proposal:** entirely new protocol, distinct endpoint, new test task(s), independent approved evaluation specification, **not** an extension of G2's frozen confirmatory experiment. Explicitly announce in G5 as *supplemental mechanism/feasibility evaluation* only if executed, independently audited and editorially coherent.
- Never contaminate the current article's claim by silently incorporating Guardian's future real customer purchase data or presenting simulations as actual human-welfare outcomes.

## Stage 0 — Exact conceptual decomposition (must precede experiment)

We distinguish three mechanisms which our original work mixed:

**P — policy informational content**: P10/volatility introduces auxiliary information to refine a frozen ranker. A positive historic target delta is a policy+signal package effect, not human-authorship effect.

**A — policy authority**: who is entitled to establish a goal, approve a constraint, override/refuse, grant exceptions, or revoke an authorization. To test A, the system must implement and LOG real action-right enforcement; a description of 'human in control' is insufficient.

**O — operational burden**: elapsed time, additional decisions, inability to fill K, human review effort and opportunity cost. Even if outputs with a fixed g are identical, approval workflow can introduce measurable overhead.

**Identity control:** If both arms execute the EXACT same fixed policy on identical inputs with identical deterministic code, they return identical selected rows by construction. That invariant is a useful software property, but **not empirical proof** that human-governed systems are non-inferior in utility or produce improved human agency.

## Stage 1 — Mechanism evaluation (new bounded experiment potentially feasible for this revision)

**Task family:** bounded simulated rank→select→reject→correct financial decision cases, constructed from a public or synthetic schema with non-sensitive fake instruments/news; no real trades. Freeze task generation and tests BEFORE running model-agent policy proposals or any reviewers. Cases deliberately include ordinary/feasible, capacity-shortfall/abstain, goal conflict, policy-revision requests, conflicting instructions, and attempts to bypass the approved veto. All cases have an **ex-ante user-authorization contract** and reference compliance answers defined by an assessor blind to the arm output. The reference contract is not disclosed to a model competing to select a policy beyond permitted user information.

**Shared conditions for all arms:** same available ranking scores, candidate information, objective/task, model/service version, financial risk limits, synthetic ground truth or known reference, prompt budget, time/cost accounting, fixed policy menu and safety gate. No arm is authorized to perform illegal/unsafe real actions. No hidden alternative predictive signal in only one arm.

**Arms:**
- **A — bounded autonomous rule choice:** agent selects from the same permitted safe policy menu and executes within the general user mission. It is not 'AI without any human input'. Reference safe invariant/legal hard stops are the same as other arms.
- **B — agent proposes, accountable human authorizes:** agent sees the same menu and information, proposes policy, human participant may approve/modify/refuse according to a recorded protocol; execution is enforced by a separate deterministic authorization gate; downstream agent may not silently replace it.
- **C — human chooses within same menu:** human participant sees the same information and independently chooses policy, machine executes; compare with B to distinguish advice and human authorization.
- **M — matched-policy implementation sanity check (software test, not causal outcome arm):** identical frozen policy and inputs with authorization labels/owners varied; deterministic selections must match exactly, showing outcome rows alone do not reveal who held authority.

**Important design constraint:** A vs B/C changes *who selects/approves the policy*, not just whether extra rules were available. If humans are included, real user participation and consent plus an independent ethics/safety assessment are needed. A synthetic scripted 'human' is only a **simulation of policy enforcement**, never evidence of actual human cognitive behavior or preferences. Predeclare actor exposure, random task order, participant clustering and assessor blinding.

**Outcome metrics, fixed prior to data:**
1. Primary mechanism: rate of actual constraint violations / unauthorized policy alterations relative to the SAME external adjudication contract across all arms (include false refusals and missed corrections, not only positive compliance).
2. Recovery: fraction of correct user challenges/overrides enforced and recorded; false overrides or blocked legitimate requests; audit/replay fidelity.
3. Utility/proxy: achieved task-quality score against a **predeclared benchmark** where truth is available, number of valid choices, no unauthorized purchases/trades.
4. Cost: agent tokens/calls, latency, review actions, human time, unresolved cases, K fill / abstention burden.
5. Prespecified composite or multi-objective Pareto comparison of quality vs constraint compliance/cost, with multiplicity control and cluster-aware uncertainty; no favorable metric chosen after outcomes.

**Attack/competence tasks:** user tries to change constraints after approval; AI recommends unsupported exceptions; input candidates missing provenance; profile goals conflict; answer/refusal should either respect authorized policy or safely request authorization. Report both ordinary and adversarial cases; measure difficulty buckets and all failures.

**Mechanism gate (after new experiments):** source/runner tests pass, corpus SHA/seed fixed, actual authorization gate enforced, provenance and rejection logs immutable, all arms reported, no data leakage to evaluator, independent blind challenge and confidence intervals; explicit real-human vs synthetic designation. Until then, do not put numerical claims in manuscript.

## Stage 2 — Prospective noninferiority (stronger Human Clause thesis; may not fit this submission)

True noninferiority of outcome quality requires user-relevant utility measured after the decision (e.g. the user receiving the product they actually needed or independently valid finance P&L), an appropriate population, task-level randomization or matching, power, attrition plan and a **substantively justified** δ frozen before data collection. If you cannot recruit actual participants with consent or collect sufficient matured outcomes before 2026-11-25, do not add a numerical no-loss claim to Intelligent Computing.

The present financial historical data can justify design choices and illustrate policy sensitivity but **cannot** close this new causal comparison. If real task outcomes cannot mature by the revision deadline, keep future noninferiority study separate.

## Explicit GO / NO-GO for proposed addition to *Intelligent Computing*

**GO to a supplemental bounded G5 subsection ONLY if** all of the following exist and are signed:
1. A one-page, frozen, read-only preregistered Stage-1 protocol, with same-info arms and explicit real vs synthetic participant identity.
2. New corpus/cases and external authorization contract whose labels were not observed before freezing evaluation definitions; task design and independent grading checks.
3. Pilot feasibility meets power/uncertainty requirements for the exact intended *mechanism* claim; if not, label a software test, not human behavioral evidence.
4. Unbiased results and adverse outcomes retained; assessor blind if possible; independent review and README to reproduce.
5. Manuscript's central topic **remains** financial decision architecture. New evidence connects directly to enforced selection-rule governance; added section does not become a separate full paper inside the revision.
6. Additional study does not jeopardize timely G5/G6/G7 authoring and 2026-11-25 Editorial Manager deadline.

**NO-GO if** only scripted human approval, synthetic scores, toy benchmark or same-policy invariant exists and the desired claim is that 'humans are not worse than autonomous AI in economic performance'. Such outputs may support implemented enforcement/technical feasibility only, not human value or economic utility. No retrospective choice of δ or thresholds.

## Novelty challenge in light of 2025–2026 literature

Additional closely relevant sources checked for this candidate:
- Agarwal, Moehring, Wolitzky. *Designing Human-AI Collaboration: A Sufficient-Statistic Approach*, NBER w33949 (June 2025, revised Aug 2026), DOI 10.3386/w33949; prospectively tested human/AI delegation and effort effects, policy optimization. Does not validate HDPG; makes generic human-vs-machine collaboration novelty harder.
- Sun, Fang (published 2026-08-09). *Authority and Responsibility Allocation in Human–AI Collaborative Decision-Making: Governance Mechanisms for Enterprises*, DOI 10.62762/TSSR.2026.930520; already distinguishes rights of access, recommendation, selection, approval, veto, execution and escalation and responsibility. Therefore **do not claim to invent decision-rights taxonomy**. Our potential contribution would have to be *empirical enforcement/cost evaluation of a specific source-verifiable financial decision contract*, not creation of the abstract taxonomy.
- Kou et al. (May 2026), DOI 10.1186/s40854-026-00941-w, already cited in original article: finance-based human–AI governance architecture.
- Kimbrough et al. Aug 2026, SSRN 10.2139/ssrn.7316382, tested delegation reluctance and choice alignment in economic tasks; relevant **working paper**, not peer-reviewed journal evidence.
- Nature 2025, *Delegation to artificial intelligence can increase dishonest behaviour*, DOI 10.1038/s41586-025-09505-x; human principal delegation and compliance risk shown on ethically bounded tasks, not evidence of HDPG efficacy.

**State of evidence:** G4.9 is a proposal to address reviewer novelty criticisms. No such experiment has been built or performed here. A purely software-side enforcement test would be valuable for proving auditable policy authority mechanically, but insufficient to establish behavioral control advantage or financial noninferiority.

## Handoff and next decision

1. **G4.9a:** frozen detailed causal diagram and Stage-1 mechanism pilot specification, including existing code reuse and task schema, before any new outcome observation. RED-TEAM signoff and editor/reviewer coherence.
2. **G4.9b:** execute only if source/time/consent/ethics/logging feasibility permits; report failures as carefully as successes.
3. **G4.9c:** independent audit and determine whether to add to current IC revision as clearly labeled *new secondary method/mechanism test*, or preserve as separate prospective Human Clause study.
4. **G5 draft:** proceed in parallel on original+supplementary financial evidence so manuscript is not held hostage by unexecuted Stage-1 pilot.

**G4 status remains OPEN.** No human-governed-vs-autonomous equivalence has been measured.
