# DTRM Phase 3 MM1 — Confirmatory Evidence Review

## Status

**Temporal replication supported under the preregistered point-evaluation contract.**

This review summarizes the frozen Phase-3 MM1 evidence after completion of the preregistered V5 confirmation cohort and the preregistered V6 prospective temporal replication cohort. It does not alter the MM1 policy, uncertainty family, rho, Phase-2 guardrail, target construction, promotion metric, or any previously frozen decision.

## Frozen scientific question

Does the preregistered MM1 robust subset decision improve realized Top-K decision value relative to the promoted Phase-2 calibrated-P10 guardrail on new temporal cohorts, using the same frozen target_model semantics and without outcome-driven policy changes?

## V5 — primary confirmation cohort

- Role: primary MM1 promotion holdout.
- Phase-2 realized Top-K mean target_model: `-0.026074727841529793`.
- MM1 realized Top-K mean target_model: `0.031173931286900932`.
- Realized incremental delta: `+0.057248659128430725`.
- Phase-2 hit rate: `0.6554934823091247`.
- MM1 hit rate: `0.7104283054003724`.
- Hit-rate delta: `+0.05493482309124764`.
- Classification: `PROMOTED_POINT`.

### V5 preregistered primary uncertainty analysis

News-event (`news_id`) cluster bootstrap, 10,000 replicates, seed `20260827`:

- Delta Top-K mean target_model CI95: `[0.04347436500585557, 0.07485787854304315]`.
- Delta hit-rate CI95: `[0.0244122965641953, 0.10027861679715344]`.
- Infeasible replicates: `0`.
- Evidence label: `PRIMARY_NEWS_CLUSTER_CI_SUPPORTS_POSITIVE_INCREMENT`.

### V5 preregistered ticker sensitivity

Ticker-cluster bootstrap, 10,000 replicates, seed `20260828`:

- Delta Top-K mean target_model CI95: `[-0.018879195232209624, 0.14999300634021678]`.
- Delta hit-rate CI95: `[-0.11667003593890389, 0.29720456544335166]`.
- Infeasible replicates: `0`.
- Evidence label: `TICKER_CLUSTER_SENSITIVITY_CI_INCLUDES_ZERO`.

Interpretation: the V5 primary news-event-cluster analysis supports a positive incremental effect, while ticker-cluster sensitivity shows that the strength of the conclusion is not invariant to cross-sectional security concentration.

## V6 — prospective temporal replication cohort

V6 was preregistered before V5 outcomes could change the MM1 policy and was evaluated only after target maturity.

- Phase-2 realized Top-K mean target_model: `-0.1018182919063799`.
- MM1 realized Top-K mean target_model: `0.008832130386594108`.
- Realized incremental delta: `+0.11065042229297402`.
- Phase-2 hit rate: `0.4186241610738255`.
- MM1 hit rate: `0.5771812080536913`.
- Hit-rate delta: `+0.15855704697986583`.
- Classification: `PROMOTED_POINT`.

Governance checks recorded in the V6 result:

- `MM1_reoptimized: false`
- `rho_retuned: false`
- `threshold_retuned: false`
- `frozen_actions_changed: false`
- `V5_results_used_to_change_V6_policy: false`

## Confirmatory conclusion

Under the preregistered Phase-3 evaluation contract, the frozen MM1 decision rule produced positive realized incremental decision value versus the promoted Phase-2 guardrail on both the V5 confirmation cohort and the later V6 prospective replication cohort.

Accordingly, the project may now claim **temporal replication of the frozen MM1 decision rule at the preregistered point-evaluation level**.

The strongest support is:

1. positive preregistered V5 point improvement;
2. a V5 primary news-event-cluster bootstrap interval excluding zero;
3. positive preregistered V6 prospective temporal replication without V5-driven retuning.

## Required limitations

This evidence does **not** establish:

- absolute profitability;
- guaranteed future realized returns from ex-ante robustness;
- minimax-theorem equality;
- causal market effects;
- independent observations or independent trading opportunities;
- robustness uniformly across security concentration structures.

Dependencies remain through shared news events, repeated tickers, overlapping 60-day forward-return windows, and common market exposure. The V5 ticker-cluster sensitivity interval includes zero and must accompany any broad robustness claim.

## Permitted scientific claim

> The frozen MM1 robust decision layer improved realized Top-K decision value relative to the promoted Phase-2 calibrated-P10 guardrail on a preregistered confirmation cohort and replicated positively on a later preregistered prospective temporal cohort, without outcome-driven policy retuning. Primary V5 news-event-cluster inference supported the positive increment, while ticker-cluster sensitivity remained inconclusive.

## Source artifacts

- `research/contracts/DTRM_PHASE3_MM1_EVALUATION_CONTRACT.yaml`
- `research/reports/DTRM_PHASE3_MM1_V5_REALIZED_RESULT.json`
- `research/reports/DTRM_PHASE3_MM1_V5_PRIMARY_BOOTSTRAP.json`
- `research/reports/DTRM_PHASE3_MM1_V5_TICKER_SENSITIVITY_BOOTSTRAP.json`
- `research/contracts/DTRM_PHASE3_MM1_V6_DECISION_MANIFEST.json`
- `research/contracts/DTRM_PHASE3_MM1_V6_REALIZED_PRICE_PROVENANCE.json`
- `research/reports/DTRM_PHASE3_MM1_V6_REALIZED_RESULT.json`
