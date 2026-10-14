# Phase IV history coverage design — review addendum v2: freeze partitions before coverage

**2026-10-14. Registered before updating the PR #36 contract again.** This is a narrow scientific anti-selection-bias correction, not G5 completion.

## P1 trigger

Exact-head Codex review `a4c76b4` found that the exact candidate manifest and lookback `L` were frozen before coverage-bin computation, but a later Step D still assigned candidates or cohort dates to TRAIN / VALID / CALIBRATION / untouched CONFIRMATORY TEST **after** visibility of which dates/assets had richer history. That permits post-coverage selecting favorable test opportunities for T without altering candidate identity, contradicting the original estimand.

## Requirement

1. Before **any per-candidate coverage-bin assessment or release of source-richness diagnostics**, freeze a deterministic, outcome-blind **partition assignment rule**, plus the input candidate manifest and declared dependencies. After source capture (if future exact IDs are unknowable), materialize and immutably bind the exact `candidate → TRAIN|VALID|CALIBRATION|CONFIRMATORY_TEST` assignment along with candidate identity, decision-cutoff UTC instant, source window `L`, point-in-time mapping/universe and assignment digest. All of these must be committed **before** coverage calculations. No split reassignment by coverage, feasibility, model performance, labels or market results.
2. The split rule must declare its chronological ordering, shared histories/ticker dependence, label-availability maturity, purging and embargo constraints relative to the **future 60-calendar-day outcome with inherited five-day price tolerance**, and treatment of any impossible or too-small partition. Later scientific feasibility can declare `BLOCKED_INSUFFICIENT_PARTITION_COVERAGE` but cannot repair it by post-hoc moving candidates/dates. Source capture and exploratory feasibility may precede binding a final confirmatory evaluation, but the confirmatory splits used for analysis must be sealed before richness metrics; a split rule changed afterwards starts a separate scientific experiment.
3. Full model-fitting recipes, seeds, optimizer inputs and inference methods still require a later **independent G5 preregistration**; freezing partition assignments now is a **necessary but not sufficient** gate, and is not permission to train.
4. Do not label prospectively captured 14-day transport slots as independent TRAIN/TEST financial cohorts without actual forward-target maturity. The rule will be validated before deployment; no confirmatory window is selected from the observed data.

Prior v0 and review addendum v1 statements about source provenance, exact cohort, history lookback and nonauthorizations remain unchanged. Review with exact-head CI and Codex before human merge authorization.
