# DTRM Fund — Phase 3 MinMax Contract

## Status

DRAFT CONTRACT — NO SCENARIOS, NO MINMAX CODE, NO PROMOTION CLAIMS.

This document defines the mathematical decision contract for Phase 3 before any adversarial scenario is created or any optimization code is implemented.

## Phase 3 research question

Can adversarial scenario reasoning built on frozen probabilistic signals improve decision robustness relative to the Phase-2 guardrail, without sacrificing its observed decision value?

## Scientific vision

Phase 3 will ultimately investigate whether learned historical event representations can provide an empirically grounded uncertainty set for adversarial decision reasoning.

That later line of work is explicitly out of scope for this contract. This document defines only the MinMax decision layer that such an uncertainty set may eventually feed.

## Frozen Phase-2 champion

Phase 3 starts from the promoted Phase-2 decision mechanism and does not replace it.

The Phase-2 champion consists of:

- a frozen ex-ante deterministic XGBoost ranking;
- selected ranking iteration: 10;
- calibrated P10 downside information;
- P10 best iteration: 18;
- calibration offset: -0.06494169682264328;
- relative veto threshold: -0.16665692627429962;
- preservation of the original baseline ranking;
- rejection of candidates below the frozen calibrated-P10 threshold;
- walk-down of the original ranking until Top-K = 10% is filled.

No Phase-3 experiment may silently retrain the Phase-2 predictor, retune its threshold, change its Top-K fraction, change its fill policy, or redefine its observed decision-value metric.

## 1. Frozen information state

For each decision time t, define

Z_t

as the complete information state that is legitimately available at time t and allowed under the temporal-integrity rules inherited from Phase 2.

The Phase-2 decision is

a_t^(2) = pi_2(Z_t)

where pi_2 is the frozen Phase-2 guardrail policy.

Phase 3 may consume Z_t but may not alter the frozen Phase-2 models or construct Z_t using future information.

### Binding status

The exact executable representation of Z_t is NOT YET BOUND in Phase 3.

Before MinMax implementation, this contract must identify the concrete Phase-2 artifacts, columns, model outputs, and timestamps that constitute Z_t.

## 2. Admissible action set

Define

A_2(Z_t)

as the set of decisions that remain admissible after all frozen Phase-2 constraints have been applied.

The Phase-2 champion decision must always remain admissible:

a_t^(2) in A_2(Z_t).

Phase 3 is therefore a constrained challenger. It may reason only inside the decision space still considered legal by the Phase-2 governance layer.

In particular, Phase 3 must not recover an asset already vetoed by the frozen Phase-2 guardrail unless a later explicitly approved contract changes that rule.

### Binding status

The exact executable construction of A_2(Z_t) is NOT YET BOUND in Phase 3.

Before MinMax implementation, this contract must map A_2(Z_t) to the concrete Phase-2 selection and fill-policy code.

## 3. Uncertainty set

Define

U(Z_t)

as the set of admissible adverse states considered at decision time t.

For u in U(Z_t), u represents a plausible adverse realization compatible with information legitimately available through Z_t and with the experimental rules fixed before observing the evaluation outcome.

At this stage, U(Z_t) is intentionally undefined.

No fixed shocks, market regimes, synthetic crashes, historical analogues, Monte Carlo draws, or learned event scenarios are authorized by this contract.

### Non-negotiable restriction

U(Z_t) must be defined before evaluation outcomes are inspected for the relevant experiment.

The adversary may challenge a decision inside a predeclared uncertainty set. It may not use realized future outcomes to construct that set retrospectively.

## 4. Decision value

Let

V(a, u)

be the decision value obtained by admissible action a under adverse state u.

Phase 3 must preserve comparability with Phase 2. Therefore V must be anchored to the same scientific notion of decision value used to establish the Phase-2 champion, unless a separate preregistered comparison explicitly justifies an additional metric.

Phase 3 must not introduce a value function merely because it favors the challenger.

### Binding status

The exact executable definition of V is NOT YET BOUND in Phase 3.

Before MinMax implementation, this contract must identify the Phase-2 outcome variable and evaluation functions used for champion-versus-challenger comparison.

## 5. Baseline-anchored robust improvement

A naive robust decision would solve

a_t^MM = argmax_{a in A_2(Z_t)} min_{u in U(Z_t)} V(a, u).

Phase 3 instead anchors robustness to the frozen Phase-2 champion.

Define incremental decision value

Delta V_t(a, u) = V(a, u) - V(a_t^(2), u).

Define the Robust Improvement Margin

Gamma_t(a) = min_{u in U(Z_t)} Delta V_t(a, u).

The Phase-3 challenger is

a_t^(3) = argmax_{a in A_2(Z_t)} Gamma_t(a).

Because the Phase-2 decision itself remains admissible,

Gamma_t(a_t^(2)) = 0.

Therefore Phase 3 has a formal fallback action: preserve the Phase-2 decision.

## 6. Intervention rule

The challenger may replace the Phase-2 decision only if its preregistered robust-improvement criterion is satisfied.

The conceptual strict form is

Gamma_t(a_t^(3)) > 0.

Otherwise

a_t^(3) = a_t^(2).

A later gate may introduce numerical tolerances or statistical requirements, but they must be frozen before holdout evaluation.

## 7. Ex-ante and ex-post claims are separate

Phase 3 must not confuse robust optimization with guaranteed realized performance.

Ex-ante robustness is represented by Gamma and is defined only relative to U(Z_t).

Ex-post observed decision value is evaluated on subsequently realized outcomes using the same frozen evaluation discipline as Phase 2.

A positive robust margin does not imply guaranteed positive realized return.

## 8. Mathematical naming

The operational project stage is named MinMax.

The current decision operator is mathematically a max-min expression:

max_a min_u.

No equality with min_u max_a is assumed. Such equality would require conditions that have not been established for this discrete decision problem.

## 9. Invariants inherited from Phase 2

Until explicitly superseded by a future approved contract:

1. temporal integrity remains mandatory;
2. Phase-2 models remain frozen;
3. Phase-2 calibration remains frozen;
4. the relative calibrated-P10 veto threshold remains frozen;
5. the baseline ranking remains frozen;
6. Top-K remains 10%;
7. the fill policy remains frozen;
8. Phase 2 remains an admissible fallback decision;
9. negative Phase-3 results must be retained;
10. no Phase-3 method is promoted without champion-versus-challenger evidence.

## 10. Required bindings before code

MinMax implementation is BLOCKED until the following three bindings are completed and reviewed:

### Binding A — Z_t

Identify the exact Phase-2 data/model artifacts that form the frozen information state at decision time.

### Binding B — A_2(Z_t)

Identify the exact Phase-2 code that constructs the admissible candidate/selection space after the guardrail.

### Binding C — V(a,u)

Identify the exact Phase-2 decision-value target and evaluation code that Phase 3 must preserve.

Only after A, B, and C are frozen may Phase 3 define U(Z_t).

Only after U(Z_t) is preregistered may MinMax code be implemented and evaluated.

## 11. Out of scope for this contract

The following are deliberately deferred:

- definition of adversarial scenarios;
- number of scenarios;
- probability weights;
- historical-event retrieval;
- BERT/Transformer event representations;
- PRAGMA-inspired sequence learning;
- Monte Carlo simulation;
- regime clustering;
- scenario severity parameters;
- QUBO construction;
- portfolio-weight optimization;
- quantum or quantum-inspired optimization.

## Gate 3.0 — contract gate

PASS requires all of the following:

- the Phase-2 champion is explicitly frozen;
- Z_t, A_2(Z_t), U(Z_t), V(a,u), and Gamma_t(a) have unambiguous mathematical roles;
- U(Z_t) remains unspecified at this stage;
- the fallback to Phase 2 is explicit;
- no code or scenario parameters have been selected using Phase-3 holdout outcomes;
- Bindings A, B, and C remain clearly marked as prerequisites to implementation.

Passing Gate 3.0 authorizes only the binding work. It does not authorize scenario construction or outcome evaluation.
