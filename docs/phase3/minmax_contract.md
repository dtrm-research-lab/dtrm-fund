# Phase 3 — MinMax Contract v0

## Research hypothesis

Can adversarial scenario reasoning built on frozen probabilistic signals improve decision robustness relative to the Phase-2 guardrail, without sacrificing its observed decision value?

## Scope

This contract defines the mathematical object studied in the MinMax line of Phase 3.

It does **not** define scenarios, shocks, historical retrieval, model architecture, or implementation details.

Phase 3 must remain anchored to the frozen Phase-2 decision system.

---

## 1. Frozen information state

For each decision time `t`, define:

\[
Z_t
\]

as the complete information state that is admissible and available at decision time `t` under the Phase-2 temporal-integrity rules.

`Z_t` contains only signals already permitted by the frozen Phase-2 experiment.

Phase 3 MUST NOT retrain, recalibrate, or retroactively modify `Z_t` using future information.

The frozen Phase-2 policy is:

\[
a_t^{(2)} = \pi_2(Z_t)
\]

where `a_t^(2)` is the decision produced by the Phase-2 guardrail.

---

## 2. Admissible decision set

Define:

\[
\mathcal{A}_2(Z_t)
\]

as the set of decisions that remain legal after all frozen Phase-2 rules and guardrails have been applied.

Therefore:

\[
a_t^{(2)} \in \mathcal{A}_2(Z_t)
\]

Phase 3 MUST NOT rescue decisions excluded by Phase 2, alter the experimental universe, bypass a veto, or modify a frozen constraint.

---

## 3. Uncertainty set

Define:

\[
\mathcal{U}(Z_t)
\]

as the set of admissible adverse states against which a candidate decision may be evaluated.

At Contract v0, the construction of `U(Z_t)` is intentionally **undefined**.

The only frozen semantic requirement is:

> An element `u` in `U(Z_t)` represents an adverse but admissible realization compatible with information available at time `t`.

The adversary MUST NOT modify training data, model parameters, calibration, Phase-2 thresholds, experimental rules, or use future-observed information unavailable at `t`.

No numerical shocks or synthetic scenarios are authorized by this contract.

---

## 4. Decision value

Let:

\[
V(a,u)
\]

be the value assigned to decision `a` under admissible adverse state `u`.

The value definition used in Phase 3 MUST remain aligned with the Phase-2 concept of decision value. A new objective MUST NOT be introduced merely because it favors the Phase-3 challenger.

The precise executable form of `V` will be bound to the frozen Phase-2 evaluation contract before implementation.

---

## 5. Baseline-anchored robust improvement

For any admissible candidate decision `a`, define its incremental value relative to the frozen Phase-2 decision under the **same** state `u`:

\[
\Delta V_t(a,u)
=
V(a,u)-V(a_t^{(2)},u)
\]

Define the Robust Improvement Margin:

\[
\Gamma_t(a)
=
\min_{u\in\mathcal{U}(Z_t)}
\Delta V_t(a,u)
\]

The Phase-3 MinMax challenger is:

\[
a_t^{(3)}
=
\arg\max_{a\in\mathcal{A}_2(Z_t)}
\Gamma_t(a)
\]

Equivalently:

\[
a_t^{(3)}
=
\arg\max_{a\in\mathcal{A}_2(Z_t)}
\min_{u\in\mathcal{U}(Z_t)}
\left[
V(a,u)-V(a_t^{(2)},u)
\right]
\]

Because the Phase-2 action itself is admissible:

\[
\Gamma_t(a_t^{(2)}) = 0
\]

Therefore Phase 3 has no mathematical basis to intervene unless an admissible alternative achieves a positive robust improvement margin.

The default/fallback decision is the frozen Phase-2 decision.

---

## 6. Contractual interpretation

Phase 3 is not authorized to maximize raw expected return independently of Phase 2.

Its task is narrower:

> Search within the Phase-2 admissible decision space for an alternative whose worst-case incremental decision value is superior to the frozen Phase-2 decision.

This separates two distinct evaluation objects:

### Ex-ante robustness

\[
\Gamma_t
\]

measures robustness inside the admissible uncertainty set.

### Ex-post observed decision value

The realized future outcome is evaluated later under the same frozen experimental protocol used to evaluate the Phase-2 champion.

Ex-ante robustness MUST NOT be presented as a guarantee of superior realized return.

---

## 7. Frozen vs. open components

### Frozen from Phase 2

- temporal-integrity rules;
- admissible information at decision time;
- Phase-2 policy `pi_2`;
- Phase-2 guardrails and vetoes;
- experimental universe and constraints;
- evaluation protocol;
- champion decision `a_t^(2)`;
- the meaning of decision value, subject only to executable binding.

### Open in Phase 3

- construction of the uncertainty set `U(Z_t)`;
- scenario representation;
- scenario weighting, if any;
- numerical solution procedure;
- robust promotion gates.

None of these open components may be selected using TEST/HOLDOUT outcomes.

---

## 8. Next gate

No scenario generator or MinMax implementation may be created until the following are explicitly bound to existing Phase-2 artifacts:

1. the executable representation of `Z_t`;
2. the exact Phase-2 admissible decision set `A_2(Z_t)`;
3. the exact executable definition of `V`.

Only after those three bindings are verified may Phase 3 define the first candidate uncertainty set `U(Z_t)`.
