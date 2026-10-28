# G4.9c — Independent-utility authority challenge: PRE-EXECUTION protocol

Date: 2026-10-28. Case: ICOMPUTING-D-26-01069.
STATUS AT THIS COMMIT: **DESIGN FROZEN BEFORE PILOT OUTCOMES**.
This is a NEW experimental-development track, not a revision to the frozen
historical G2/G3 finance experiment and not a retrospective noninferiority test.
Parent: G4.9b consented keyboard prototype, PR #51, human N=0.

## Motivating research question

When an algorithm proposes an admissibility policy, what does retaining an
effective right of human authorization/override do to independent task
utility, constraints, correction, workload and abstention? **Both
superiority of fully delegated choices and noninferiority of governed
decisions are empirical questions, not assumptions.**

### Crucial design distinction

The preceding 12-case G4.9b A arm is a deterministic script selecting a fixed
policy; its score is NOT an independent downstream outcome. G4.9c introduces
a locally TRAINED (learned) policy-selection model and an evaluation oracle
with simulated realized utilities. This is stronger as an *engineering
benchmark* but the learned model is NOT an LLM or field autonomous agent,
the oracle is synthetic, and there are no real human participants or
prospectively observed user outcomes in the initial run.

## G4.9c.1 fixed engineering protocol

- Dataset: 300 synthetic training cases and 60 **separate** synthetic
  held-out evaluation cases. Seed: 20261029. No reused IDs or random draws.
- Shared visible information: per-case user risk-weight w; synthetic
  candidates (id, point-predicted score, risk 0..5, verified, blocked).
  Agent and human should see EXACTLY this information and the same menu
  {cautious risk<=2, balanced risk<=4, open risk<=5}. The shared *hard*
  guard is verified, not blocked and risk<=5. No outcome labels in
  evaluation input.
- Each policy selects the highest **predicted score** candidate that
  respects its limit, with stable ID tie-break. If none, ABSTAIN.
- Independent (but synthetic) oracle utility for chosen candidate:
  `realized_quality - w * risk`, where realized quality is generated
  once per candidate from point-predicted score plus fixed seeded noise
  before applying policies. Realized-quality outcome is NOT shown to
  either policy chooser, nor used for fitting/retuning on holdout.
  If ABSTAIN, predeclared utility 0. No trades, real P&L, external
  scores, survey satisfaction or real-world welfare.
- Learned challenger: offline regularized linear policy-value estimator
  trained on **train-only** policy outcome utilities, input is features
  based on the *pre-outcome* winning candidate for a policy and user w.
  For each case select policy maximizing model-estimated utility.
  No external LLM, no network, no runtime labels or hyperparameter
  sweeps. The intercept and coefficients are ridge fit with fixed
  regularization 0.01. Ties use fixed menu order.
- All three decision-rights arms in a subsequent human trial must use
  the **same learned policy proposer** and the **same visible candidate
  information**, not silently different advice or true outcomes:
  A = model's learned policy; B = person authorizes/changes/declines A;
  C = person selects without being shown A. The hard gate enforces the
  ultimately authorized rule, even on disfavored tasks.
- Engineering holdout labels are available ONLY to a physically
  separate evaluator method; the trained agent function is passed
  labeled training rows and stripped public evaluation cases.
  Source is openly inspectable so the engineering benchmark is NOT a
  cryptographically sealed or externally blind evaluation.
- Allowed engineering metrics: independent synthetic utility against
  oracle per arm; fraction candidate refusals/abstentions; hard-safety
  violations; policy choices; simple counts of authorization checks;
  explicit source, sample and generated-label hashes.
  No post-hoc replacement of a model if it performs poorly.

## G4.9c.2 real-human experiment: design conditions, NOT authorized by CI

Before recruitment: appropriate research ethics/privacy review,
participant consent, common objective and constraints across arms,
independent outcome assessor, participant/task randomization or
well-defined crossover with washout, complete predeclared exclusion and
attrition rules, statistical unit and clustering, and sample-size/power
analysis. Real participant data must remain private and never be
invented or collected by CI. A consenting human decision cannot be
replaced by a scripted variable.

Human trial proposed endpoints:
- Primary: user-authorized **verified** outcome utility
  (not model predicted score), plus refusal/abstention costs.
- Governance: actual legitimate override/correction frequency,
  improper intervention and constraint failure under a **common**
  independently adjudicated legitimate user mission.
- Operational: human decision time, additional interaction burden,
  agent calls/latency and false refusals.
- Fidelity/causal attribution: same model, options, inputs, safety
  rules, external outcome grader; participant and item effects logged
  and analyzed appropriately.

Noninferiority requires an independently justified **pre-outcome**
margin delta, appropriate one-sided lower CI, and sample power. This
engineering study does NOT supply that margin or noninferiority result.
The learned model is not a general autonomous agent and the synthetic
oracle does not establish a population welfare claim.

## Falsification, gates, manuscript

Technical **NO-GO** on data contamination, train/test ID overlap,
leaked test labels into fitted coefficients, unapproved action,
outcome oracle visible in participant display, failed reproducibility,
all-zero/vacuous benchmark, or hidden selective reporting. Retain any
negative or adverse comparison in aggregate.

Engineering **PASS** means reproducible train/evaluation, learned
policy actually changes with visible features, oracle scoring is
independent of policy predictions, zero common hard-guard breaches,
and CI tests pass. It does not demonstrate human control benefit.

Current *Intelligent Computing* revision should use this as a
supplemental method/engineering demonstration only if editorially
coherent; no human equivalence/causal authority claim unless an
independent prospective human study actually runs and is valid.
G5/G6 continue in parallel to meet the author-reported 2026-11-25
deadline. This research should not block resubmission.

No G4.9c execution was performed before this protocol commit.
