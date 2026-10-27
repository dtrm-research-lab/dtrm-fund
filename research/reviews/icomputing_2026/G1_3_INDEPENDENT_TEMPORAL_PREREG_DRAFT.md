# IC major revision — G1.3 independent temporal evidence: PREREGISTRATION DRAFT, NOT FROZEN

Prepared: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.
This is an outcome-blind study DESIGN, not a study result and NOT
authorization to load any new market returns, prices or target labels.

## Rationale and completed foundation

Historic G1.2k dossier SHA256:
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
Nine audit reports, four locally hash-bound reconstructed XGBoost models,
40,320 V1 rows, complete 390-feature matrix numerical parity
(15,724,800 coordinates). Ranker & raw P10 predictions match
old V1 numerical signals and calibrated P10 agrees within 1e-6.
No independent test is implied by this reproduction.

V1 was 2026-05-02 through 2026-06-06, and V4 reuses that V1
calendar cohort. A genuinely **new event cohort** must not
reuse any of the old V1/V2/V3/V4 observations or news IDs.
Cannot establish independence just from differently named files.
Original training data extends through 2026-05-01.

## Two mutually distinct evaluation classes

A. **New event-date temporal retrospective holdout, outcome-blind before
evaluation**: may use an event interval after the consumed original
V1/V2/V3/V4 cohorts, provided news, inputs, 60-day target prices
and source provenance exist, the outcomes have not been viewed by
model-design/development staff, the event+pair keys are disjoint, and
all evaluation rules are *frozen* before any target open. It may be
new-to-this-analysis but must NOT be called genuinely prospective
if news/price outcomes already existed at the time of preregistration.
A new event cohort by itself is not statistically independent of
old returns due to overlapping 60-day windows; explicitly test
calendar forward-window overlap and choose embargo.

B. **Genuinely forward-prospective observation**: the first event is
seen/fixed AFTER the preregistration/study start, model predictions
are timestamped and hash-committed before 60-day outcomes mature.
A 60-**calendar**-day horizon plus 5-day allowable end-price
alignment means outcomes from a late-October 2026 start cannot
all be finalized by the November 25, 2026 journal deadline.
This can be planned as a later follow-up; do not invent a positive
result to meet the revision date.

## Invariants carried forward from original experiment

- Frozen source commit:
  `c7502a690162459cdfb3413573e3133c42efb126`.
- Historical original ranker inference uses iteration 10, i.e.
  `iteration_range=(0,11)`.
- Historical calibrated P10 uses best iteration 18, i.e.
  `iteration_range=(0,19)`, plus validation-only
  calibration offset **-0.06494169682264328**.
- Frozen V2/V3/V4 relative risk veto:
  `calibrated_p10 >= -0.16665692627429962`.
  **Do not use V1's old absolute P10>0 gate for the V2/V4 comparison**.
- Same deterministic baseline ranking for both arms; 10% Top-K
  using historically defined flooring and tie-breaking.
- Candidate walk-down baseline rank, skipping pairs below the
  frozen calibrated P10 cutoff, requiring full K.
- Primary outcome: mean forward excess-beta target
  `stock_forward_return - beta_pre * SPY_forward_return`.
- Forward horizon: **60 calendar days**, using prices on or
  after the event and the event+60d target, each within 5d
  original tolerance. `beta_pre` only uses event-time
  information with the original 252-day backward lookback,
  minimum 60 observations and 20-day tolerance.
- No future-inclusive SPY event return as a feature.
- No model retraining, no hyperparameter search, no quantile
  recalibration and no cutoff tuning using new cohort targets.
- Four candidate model SHA256 values must be pinned from the
  verified local G1.2k dossier before new inference begins.
  Previous original weights are NOT serialized; these are
  hash-bound numerically-equivalent historic reconstructions.

## Mandatory prereg fields — UNSPECIFIED / NOT FROZEN

1. Target *population* and concrete original event-time window,
   unique `news_id`/ticker universe and asset normalization
   policy, acquisition providers and timestamps, dataset hash.
2. Temporal independence method relative to all V1/V2/V3/V4
   outcomes: define 60-day forward-window calendar embargo,
   avoid shared news IDs, and disclose any retained ticker overlap.
3. News/embedding provider, availability timestamps (as-of
   each event), sources and licensing. Demonstrate complete
   event-time 384d embedding, five text features, beta_pre
   access without lookahead. No backfilled headlines accepted
   as if retrieved live.
4. Date of original final result maturity, stock/SPY price
   provider/adjustment version, next-on-or-after price
   alignment 5-calendar-day tolerance, missing-price behavior.
5. Sample size/candidate coverage and independent event
   clusters. Predefine minimum eligible pairs, unique news,
   risk-gate fill feasibility, exclusion rules, and whether
   insufficient evidence leads to ABSTAIN.
6. Predictive mechanism and tie-breaking: exact historical
   inference method, 10% floor Top-K, ranking and admitted
   candidate selection; hash-source all inputs and outputs.
7. Predefine analysis and statistical uncertainty:
   point delta Top-K mean excess-beta and hit-rate;
   10,000 news-cluster replicates seed 20260821, 10,000
   ticker-cluster replicates seed 20260822, and
   weekly descriptive sensitivity where sample supports it;
   retain infeasible resample counts and overlapping-return caveat.
8. Baselines/ablation experiments, trading friction
   sensitivity and repeated-ticker exposure must be labeled
   *secondary*; do not silently change primary decision rule.
9. Operator eligibility attestations: outcomes untouched,
   original historical 390-feature numeric replay passed,
   G1.2 source filename/cardinality caveat disclosed,
   locked data collection cutoffs, embargo and output hash.
10. **External prereg timestamp and code commit** made BEFORE
    any new target/label inspection, with signed manifest.

When these fields are complete and feasibility tests
(process inputs/events and DO NOT OPEN TARGET OUTCOMES) pass,
emit a **separate frozen preregistered protocol commit** and
signed timestamp. This DRAFT is intentionally NOT a frozen
preregistration, and does not authorize scoring.

## Known source constraints (as of 2026-10-27 audit)

Historical accessible news caches only confirmed through
2026-06-06; newer sufficient news inputs have NOT been verified.
Some price filename caches extend to August 2026; naming
alone is NOT evidence that full forward prices are available
to any proposed new event window.
Original V1 contract pairs-basename row-cardinality discrepancy
(40,320 listed vs 265,145 local) remains open.
The 2026-11-25 journal revision deadline constrains what
can be claimed from a *genuinely newly started* 60d holdout.
A well-documented historical retrospective cohort under strict
outcome blinding is not the same as a prospective forward run.

## Scientific stop rules

- No available verified new-cohort news/event-time inputs => do
  not pick a cohort by looking at market returns.
- Target outcomes already viewed/used by model designers =>
  label as exploratory and do not market as independent test.
- Price maturity incomplete => postpone outcome scoring,
  do not approximate partial 60-day labels.
- Hash/feature/model lineage inconsistent => stop and audit.
- Risk gate cannot fill complete Top-K => report feasibility
  failure, not a tuned replacement threshold.
- P-values or ticker-cluster uncertainty crossing zero =>
  present accurately, never claim universal robustness.
- No sponsor claim of absolute profitability from
  excess-beta target metrics.

**Status: G1.3_PREREG_DRAFT_UNFROZEN; NEW_INFERENCE_BLOCKED.**

## 2026-10-27 update — historical sample-selection structural check

G1.2m was operator-run and succeeded using the predeclared
historical original V1 event interval 2026-05-02 to
2026-06-06 inclusive and original BRK.B→BRK-B alias:
**40,320 derived original pair keys, exact historical key
set, row order and UTC event timestamps; zero extra/missing**.
This establishes structural observational correspondence of
the historical raw candidate universe (265,145 pairs) to V1.
The source file's same-basename contract cardinality and
original physical copy/generation provenance are still open.

G1.3a metadata-only newer-news source discovery is now
PREPARED but has not been run, so no specific subsequent
cohort dates or news availability can yet be preregistered.
Both retrospective outcome-blind and truly prospective
modes remain UNAUTHORIZED until the signed full protocol
and inputs/outcome access gates pass.
