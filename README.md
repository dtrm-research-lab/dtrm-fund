# DTRM Fund

**An open-source research project by DTRM Research Lab.**

DTRM Fund is an applied research project investigating how **human judgment, artificial intelligence, game theory, and optimization** can be combined to build more robust decision systems.

Financial portfolio construction is used as a measurable experimental environment: models make predictions and optimization systems search for solutions, while human judgment defines objectives, constraints, guardrails, and the conditions under which a result should be trusted.

> **Machine searches. Human defines the game.**

## Research question

Can a Human-in-the-Loop system remain more robust and decision-useful than increasingly autonomous model-only optimization when both are evaluated repeatedly under the same data, timing, costs, and market conditions?

The project is designed around falsifiable experiments rather than claims of guaranteed performance.

## Research path

The initial research program progresses from a reproducible legacy baseline toward:

1. leakage-safe and reproducible XGBoost baselines;
2. probabilistic prediction and uncertainty estimation;
3. MinMax and adversarial scenario analysis;
4. QUBO-based portfolio construction;
5. quantum-inspired and hybrid quantum optimization;
6. controlled Human-in-the-Loop comparison against autonomous alternatives.

Each stage must be compared against the previous champion under consistent experimental conditions before it can be promoted.

## Research principles

- **Experiment before claim.** Results must be measurable and reproducible.
- **Temporal integrity.** Information unavailable at prediction time must not enter model features.
- **Champion vs. challenger.** New methods must demonstrate improvement against a frozen baseline.
- **Human judgment is explicit.** Objectives, constraints, guardrails, and promotion criteria are part of the experiment.
- **Negative results matter.** Failed hypotheses are useful research outcomes and should not be silently discarded.

## Status

**Early research infrastructure.** The existing experimental work is being reconstructed into tested, reproducible Python components before new optimization layers are introduced.

No stable research release has been published yet.

## License

Source code in this repository is licensed under the **Apache License 2.0** unless otherwise stated.

## Disclaimer

This repository is for research and educational purposes only. Nothing in this project constitutes investment advice, an offer, or a recommendation to buy or sell any financial instrument.
