# G4.9c — Executed learned-policy engineering benchmark and authority-interface mock audit

**Date:** 2026-10-28 | **Editorial case:** ICOMPUTING-D-26-01069.
**Scientific state:** TECHNICAL SOFTWARE READINESS PASS; HUMAN CAUSAL / NONINFERIORITY NOT TESTED.
**Pre-execution protocol commit:** `333de0347f830dd7d581e992fcaa8fc905b04043`.
**Evaluated complete software/test/workflow commit:** `6d8eb42381c7d4705d49c520f711987d7e18dcec`.
**CI specialised:** https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40771489643 — **SUCCESS, 23/23 tests PASS**.
**CI full project:** https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40771489747 — **SUCCESS**.
**No actual human participation, actual external LLM, financial transaction or new old-outcome access.**

## What was done (non-retrospectively fixed input/data schema)

- Specified training and evaluation schema/seed BEFORE running the new model;
  generator seed 20261029, 300 synthetic training cases and 60 heldout distinct
  synthetic cases. The 60 evaluation labels were **not passed** to
  training or policy selection; the oracle is a *separately accessed*
  synthetic realized quality mapping and fixed user risk penalty.
- Trained a regularized linear policy-value learner using train-only
  simulated utility labels across the same 3 admissibility policies.
  This is a learned offline algorithm, **not an agentic LLM**.
- Every configuration uses the same synthetic candidate fields, same
  information and same hard veto; an external oracle computes actual
  *synthetic* outcome utility AFTER policy selection.
- 60/60 heldout tasks are included in aggregates; abstention is
  assigned the predeclared utility 0. No policy selection based on
  heldout outcomes; no posthoc retuning or exclusion.
- Added an *optional* adult, opt-in, offline human approval/direct-choice
  interface (6 B / 6 C cases), context-bound local HMAC events, private
  `0600` records and local readback. All CI human-response simulations
  use mock input, temporary private dirs, and immediate deletion.
  No record of a real person was collected.

## Results: all are SYNTHETIC

| Quantity | Result |
| --- | ---: |
| Training cases | 300 |
| Strictly separate synthetic heldout cases | 60 |
| Specialized CI tests | 23 / 23 PASS |
| Full project CI | PASS |
| Shared hard constraint violations | 0 |
| Learner policy selected: cautious / balanced / open | 44 / 14 / 2 |
| Mean realized **synthetic** utility, fixed balanced policy | 80.81257747 |
| Mean realized **synthetic** utility, learned policy | 83.45532793 |
| Mean realized **synthetic** hindsight best policy (unavailable at decision time) | 84.19572118 |
| Learned minus fixed balanced descriptive utility | +2.64275047 |
| Actual participant N | **0** |
| Genuine external agentic LLM N | **0** |
| Human-control causal benefit | **NOT ESTIMATED** |
| Human-government/non-autonomous noninferiority | **NOT TESTED** |

A 2.64275-point improvement belongs ONLY to this synthetic distribution and
value function. It is not a statistical human-control effect, future market
return, user welfare, reproducible live economic advantage or a claim that
the agent is optimal. No CI, p-value or externally justified noninferiority
margin was computed for these synthetic hand-constructed scenarios.

The hindsight best-policy ceiling uses *realized synthetic labels* to
pick the best of 3 rules ex post and is **infeasible for an ex-ante
decision-maker**; it is reported only as a diagnostic upper bound.

The learned selector is *more legitimate than the G4.9b fixed stub as an
algorithmic rule-choice comparator*, but its training data use artificially
specified outcomes. Its utility success against fixed balanced therefore
cannot answer whether delegating real decisions improves outcomes.

## Technical trust, privacy and construct-validity caveats

1. The generator, agent and evaluation oracle all exist as public code,
   therefore source-knowledge leakage remains possible despite runtime
   train/test isolation. This is NOT a sealed externally administered test.
2. The hidden outcomes are synthetic and correlated with public ranking
   scores by design; the benchmark provides a development environment
   rather than independent empirical decision-quality evidence.
3. Real human authorization is a substantive intervention only if a
   person actually consents and chooses. CI mocks cannot be counted.
4. The local signer/verifier share one operator-controlled HMAC secret.
   It cannot independently establish who typed the decision, and
   operator-held keys can fabricate a plausible session.
5. The objective and constraint menu are shared across arms; this
   avoids a trivial unfair comparator. Yet observed social/legal
   legitimacy of human authority is not measured by this prototype.
6. Human decision time is measurable in the new CLI once real sessions
   exist, but there are **no observed seconds from humans** now.
7. Any numeric noninferiority claim requires authentic participant
   N, independent utility, a substantively fixed margin, power
   and suitable cluster/randomization inference; none exist here.
8. Nothing in G4.9c changes or upgrades the older G2/G3 original
   P10-vs-baseline financial evidence. The new task is disjoint
   synthetic data, with a different utility endpoint.

## Falsifiable next gate: how actual authority could be tested

**Protocol admission for a real human experiment** is blocked until
independent ethics/privacy/consent clearance, agent model version freeze,
evaluation by an assessor independent of agent/human choice, and
pre-registered balanced participant/task assignment with adequate
sample and time burden measurement. Contested-policy tasks must contain
a legitimate user-goal conflict and be scored by the SAME neutral
criteria in all arms. Ensure that an agent's lack of approval is not
simply counted as a violation absent an independent task-level harm.

**Minimum honest hypothesis if recruiting a feasibility pilot:**
users can actually refuse/override model-proposed admission policies;
the executor obeys that authorization; and decisions/costs can be
independently reconstructed. This tests interaction/feasibility, not
the proposition that humans are 'at least as good as an autonomous AI'.

**Final journal disposition:** G4.9c is at most a technical
supplement for an applied decision architecture, not a new empirical
result about real human governance. G5/G6 should continue using
original bounded G3 evidence and not wait for speculative recruitment
before 2026-11-25.

## Integrity / availability

Exact modeled-source lineage is tied to the protocol and current
GitHub commits. CI Actions uploads an **aggregate-only synthetic JSON**
with a canonical report SHA digest and file SHA hashes, retention 30 days.
No raw confidential market dataset, model credentials, human respondent
logs or secret HMAC key are committed.

**G4.9c engineering smoke PASS. G4 Novelty Gate OPEN.**

## Adversarial G4.9c2 follow-up: additional comparator (2026-10-28)

**This was devised AFTER observing the original 60-case G4.9c result and is EXPLORATORY, not part of its pre-execution protocol.** A transparent, non-trained policy chooser maximizes the *public* score minus the visible synthetic user risk penalty over the same three selectable policies. No heldout synthetic realized labels are used when choosing.

- Exact original heldout: transparent **83.28853647** vs learned **83.45532793** vs fixed balanced **80.81257747**. Transparent and learned differ in 2/60 policy decisions. Learned leads transparent by just **0.16679147** utility points in this one synthetic seed.
- Additional 32 separate synthetic generator seeds 20261030..20261061, each fresh 300 training/60 heldout: transparent-minus-learned mean across seeds **+0.05694396**, with transparent leading in 9 seeds, learned in 6, and 17 equal. Mean different policies **0.8125/60** per seed. This is synthetic exploratory sensitivity, **not** a confidence interval about the real world.
- The utility generator is *score + independent mean-zero noise - visible risk penalty*. Consequently a transparent score-minus-risk decision rule is almost optimal for the simulator by construction. The result does not establish intrinsic value of machine learning, human autonomy or policy authorization. **The paper novelty gate is NOT satisfied by this benchmark.**
- Original GitHub-source rerun, numeric references and the 32-seed experiment: GitHub Actions **40772876816**, 23 tests PASS; `g49c_transparent_challenge.py`; detailed artifact `G49C_2_TRANSPARENT_BASELINE_ADVERSARIAL_READOUT_20261028.md`.

**Editorial decision:** retain as reproducibility/technical appendix or separate research engineering record only; do not present synthetic policy-comparator superiority as a central new scientific result for the *Intelligent Computing* major revision. Genuine human-authority evidence remains absent (N=0), as does an LLM baseline and a justified noninferiority margin.

