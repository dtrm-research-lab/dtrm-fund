# G2.3 — Reviewer-linked G3 analysis packages, DRAFT / NO NEW INFERENCE

Manuscript: `ICOMPUTING-D-26-01069`
Date: 2026-10-27. Deadline 2026-11-25.
Original evidence: G1.2k sealed SHA256
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`;
G1.2m original cohort derivation SHA256
`388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.
No source V0–V4 contract, original tag, historic result or
original model binary may be rewritten.

## Data boundary common to A2/A3/A4/A6

- **Consumed** old event cohorts: V2 (June 7–10 2026;
  4,449 ticker/news rows, Top-K 444), V3 (June 11–14;
  2,827 rows, K=282) and V4 (May 2–June 6;
  40,320 rows, K=4,032). V1 original absolute P10>0
  accepted zero rows; negative result protected.
- Same ranker from old source commit `c7502a690162459cdfb3413573e3133c42efb126`,
  original ranker iteration 10 and quantile P10
  iteration 18 (indices 0:11 and 0:19), validation-only
  calibration offset -0.06494169682264328.
- Baseline ranks by frozen ex-ante model; original P25
  guardrail veto `P10_calibrated >= -0.16665692627429962`;
  fill candidate by stable baseline-order walk-down,
  `K=floor(0.10*N)`, strictly full K or mark infeasible.
- Same 60 calendar-day excess-beta target already known;
  no new independent inference. All newly calculated old-
  outcome comparisons are **post-outcome exploratory**,
  even if their **analysis** is specified before executing it.
- No selecting the best threshold, comparator, K grid point,
  cost assumption or subgroup after observing results.
- Reproducibility artifacts and original scientific inputs
  stay local/confidential; only aggregated verifiable output
  metrics/hash evidence may be published.

## A1 — Original uncertainty, dependence, temporal heterogeneity

Reviewer refs: R1-02/R1-06, R2-01/R2-03/R2-04/R2-07.
Disposition `EXISTING_HISTORICAL_RESULT_AND_CLAIM_REWORDING`.
No new statistical run needed merely to report:
- V2/V3/V4 incremental excess-beta Top-K means
  +0.1442948 / +0.1494375 / +0.0275616.
- 95% news-event cluster bootstrap existing CIs positive
  in all three cohorts.
- 95% ticker-cluster existing CIs cross zero for V2
  [-0.0062202, 0.1961534] and V4
  [-0.0104682, 0.0718196]. V3 [0.0075385, 0.1933165]
  excludes zero under same ticker approach.
- V4 weekly descriptive deltas are negative in W18
  and W19; positive W20–W23; four out of six weeks.
- V2/V3 event windows are adjacent, their forward
  60-day outcome calendars overlap, and V4 earlier
  outcomes overlap portions of those calendars.
  Events may be distinct, return observation windows
  are not independent. Do NOT call them three fully
  statistically independent 60d tests.
- Underlying target remains excess-beta not traded P&L.
- HDPG experiments evaluate machine ranking constrained
  by a human-*specified* deterministic governance
  policy, not randomized outcomes of human investment
  judgments. 'Model-agnostic architecture' is a
  design claim; one-ranker measured effects cannot
  establish empirical model independence.

A1 **ready for manuscript interpretation**, but G5
still follows G3/G4 gate order.

## A2 — Weighted calibrated-P10 validation threshold sensitivity

Reviewer refs: R1-03, R2-02.
Classification: `EXPLORATORY_POST_OUTCOME`.
**Predictive quantile P10 remains fixed.** The
threshold notation `P15/P25/P35` here means *weighted
15th/25th/35th percentiles of ORIGINAL validation-only
calibrated-P10 prediction distribution*, NOT
three separately trained P15/P25/P35 quantile models.

Intended fixed options: `q∈{0.15, 0.25, 0.35}`.
The `q=0.25` threshold is the **original
promoted -0.16665692627429962** anchor; software
recomputed validation `q=0.25` must reproduce it
to original numeric tolerance or stop. Do not use
reproduced test outcomes to calibrate thresholds.

For **each** V2, V3, V4 cohort and each `q`, report:
- validation-only numerical threshold, historical
  test admission count/rate;
- Top-K fill feasibility, selected Top-K K as originally
  defined (no downsizing/replacement);
- delta Top-K mean old `forward_excess_beta` versus
  same original baseline; candidate mean itself;
- Top-K hit-rate and candidate-minus-baseline
  hit-rate; original q=0.25 replicated row-for-row;
- news_id- and ticker-cluster CIs (if predeclared
  prior to any new run), all infeasible/bootstrap
  replication counts, limitations of overlapping
  windows and multiple exploratory comparisons.
Do not promote q=0.15 or q=0.35 based on best gains.
Preflight pending: verify original validation P10
array, `legacy_news_weights` cardinality and
weighted empirical quantile function with its
tie/interpolation; pin input SHAs. No G3 run yet.

## A3 — One conventional baseline, capacity matched

Reviewer ref: R1-04.
Classification: `EXPLORATORY_POST_OUTCOME_IF_INPUTS_VERIFIED`.
Preferred comparator: **trailing realized volatility**
(stock daily historical adjusted returns, at most the
60 prior trading sessions **strictly before event
timestamp**), no future labels. Possible minimum
history `>=40` observations, subject to verifying
the original returns/price snapshots and timezone
as-of semantics. The final formula and inclusion
must be explicitly fixed **before G3**, not guessed
from current uninspected files.

Fair-comparison protocol (conditional):
- Keep the same original frozen baseline ranking,
  same eligible `(news_id,ticker)` universe for all
  arms, stable ties, same K/full-K feasibility.
- Comparator rejects high pre-event volatility;
  determine its veto cutoff **using only original
  frozen training/validation samples**, preferably
  matched to original validation P25 pass capacity.
- Do not tune comparator threshold on V2/V3/V4
  return labels, or force performance equivalence.
- Missing lookback data: predeclare complete-case
  common eligibility across arms and report lost
  rows/coverage. This is a **secondary subset**,
  not a new redefinition of original V2/V3/V4.
- Report baseline, original probabilistic veto,
  conventional comparator on identical eligible
  rows with effect sizes, admission, fill and CIs.
- If historical point-in-time volatility cannot
  be reconstructed, label `NOT_EXECUTABLE`
  with an auditable reason; do not substitute
  `beta_pre` as a volatility measure without
  disclosing that these are different concepts.

## A4 — Economic interpretation, downside and flat/no-action

Reviewer refs R1-05, R2-05.
Classification `DESCRIPTIVE` + `EXPLORATORY_CONDITIONAL`.
The old target is 60d **excess beta**, not
market-tradable P&L or pure realized stock return.
Original old **candidate absolute excess-beta
means are still negative** even where relative
incremental gains are positive.

Minimum descriptive output requires no new outcome
calculation: state candidate/baseline old excess-beta
means and negative sign, and explain why
`candidate - baseline > 0` does NOT imply
`candidate > cash` or economic value net of fees.

Optional economic old-cohort replay, before G3 freeze:
- Define exact stock event entry/exit execution time
  and matched adjusted/unadjusted price schema.
- Define event-level gross stock return,
  max loss/downside quantiles, stock/ticker exposure
  concentration; SPY benchmark separately.
- Define a capital-constrained repeat-trade portfolio
  and self-financing overlap handling **before**
  computing turnover or P&L. Repeated events for
  the same ticker cannot be independent 'trades'.
- Define transaction-cost grid (if included) from
  **externally justified and fixed** fee/slippage
  assumptions; never cherry-pick best scenario.
- Flat arm = no risk exposure/positions; zero
  pretax nominal gross return only under explicit
  zero-yield cash simplification. Distinguish
  a decision-to-abstain from simply ranking negative
  excess-beta event means against zero.
- If authentic fill/cost/capital data unavailable,
  do **not** label any old excess-beta difference
  as realized portfolio outperformance. Limit
  discussion to illustrative assumptions.

## A5 — Second ranking model (conditional)

Reviewer R1-07.
Category `NOT_EXECUTABLE_PENDING_AUTHENTIC_ALT_RANKER`.
Need genuinely preexisting frozen ranker model checkpoint
prior to original V2/V3 outcomes, with separately pinned
source, model SHA, feature/ticker schema, training cutoff,
ex-ante alignment and no post-outcome policy tuning.
Training a new second model on consumed test outcomes to
satisfy the reviewer would NOT support confirmatory
model independence. If no authentic prior model,
explain method *design portability* and present
empirical single-ranker limitation.

## A6 — Capacity K and abstention

Reviewer R2-06 (plus R2-05).
Category `DESCRIPTIVE` + `EXPLORATORY_CONDITIONAL`.
Original K is `floor(0.10*N)`: a mechanical
fixed-selection budget, **not** a demonstrated
real-life capital/turnover capacity. Explain that
the 10% choice ensures same admitted cohort size
for a fair paired rule comparison, but is a
research policy, not empirically optimized investment
capacity.

If executable, fixed exploratory sensitivity fractions
`{0.05,0.10,0.15}` applied to *each* original
cohort, recomputing K with floor and always keeping
same K for baseline and guardrail within comparison;
report admission and fill feasibility, all deltas,
downside metrics and ticker clustering. No best-K
selection. If short-cluster/wide-CI behavior
dominates, characterize honestly.

## A7 — Literature upgrade

Reviewer R2-08. `DESCRIPTIVE_DOCUMENTATION`.
Use independently verified bibliographic references
from peer-reviewed financial machine learning,
risk control, decision support and human-AI
collaboration; record DOI and publication metadata,
check actual paper context rather than citation by
title alone. Differentiate algorithmic risk filters,
uncertainty-sensitive selective prediction,
AI-assisted finance and human objective design.
No claim of experimental human-vs-AI comparison.

## X1 — Truly later nonoverlapping holdout

Reviewer R1-01, R2-03.
Status `NOT_EXECUTABLE_UNDER_CURRENT_G1_INPUT_GATE`.
G1.3a/b found no source-and-timestamp-verified,
unused later investment-news event cohort within
the audited local research roots. Fully prospective
60-calendar-day forward outcomes from a new
Oct 27 observation cannot mature by the Nov 25
revision deadline. No original news data, new
60d targets or post-August outcomes were opened
during G1.3 availability scans.

G2 must distinguish: `no eligible cohort found
within searched local roots` versus `there is
no such cohort anywhere`. Do not claim latter.
Open independent evaluation as future work
with signed timestamp, original-model SHA,
outcome-blind inputs and temporal overlap embargo.

## Fixed G2 scientific acceptance rules

- G3 only after G2 freeze includes actual source
  artifact SHA, validated as-of cutoff,
  fixed candidate universe and method and ALL
  planned outcome summaries/uncertainty estimators.
- If feasibility FAIL, record `NOT_EXECUTABLE`
  or `INFEASIBLE` without replacing filters,
  selecting different K/thresholds or dropping
  difficult rows post hoc.
- All exploratory secondary analyses clearly
  separated from original historically frozen
  V2/V3/V4 comparisons. No new confirmatory
  p-values for already-known outcome datasets.
- Satisfying the reviewer through transparent
  negative, infeasible or limitation findings
  is scientifically valid; **do not claim the
  same inferential strength as a new independent test**.

**G2.3 STATUS = ANALYSIS_DESIGNS_DRAFT_NO_INPUT_HASHES_OR_G3_EXECUTION.**

## G2.5/G2.6 state update (2026-10-27): distinct source path for A2

G2.5 OPERATOR PASS: 92 original old-cohort candidate files
SHA-streamed, no source values deserialized. Five
validation-quantile filename matches include original
V2 frozen q25 threshold PKL, but do NOT alone imply
separate retained calibrated P10 validation predictions.
G2.5 inventory report is locally generated; SHA has
not yet been communicated.

Independently checked pinned original code and old
G1.2 historic 12/12 reconstruction implementation:
the **original V0 validation 19,880 rows**, original
P10 predictor at best iteration 18, validation news
weights and offset -0.06494169682264328 can be
reproduced along an already verified deterministic
G1 train/valid/test path; original weighted-q25 cutoff
is -0.16665692627429962. Weighted quantile uses
sort+cumulative weights+left searchsorted.

G2.6 `ic_g2_validation_source_binding.py` and
`G2_6_VALIDATION_SOURCE_BINDING.md` prepared as
source/JSON checks ONLY; local operator G2.6 has NOT
run. q15/q35 values and all existing old-cohort
sensitivity comparisons have **NOT** been computed.
A3 price source/event-time as-of provenance, A4
actual portfolio economics, and A6 K analyses
remain conditional on separately frozen rules.

## G2.6 executed + G2.7 spec now committed (2026-10-27)

G2.6 was operator-run and passed. G2.5 evidence
report SHA256: `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.
Original 19,880-validation P10 source path and exact
historical weighted q25 cutoff are now corroborated
by G1.2 12/12 old numeric replay, 9/9 code token
checks, and 8 old-cohort file hash refs.

G2.7 `G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json`
has been committed **before** running any q15/q35 or
V2/V3/V4 exploratory comparisons. It fixes the q-grid,
all 9 comparison cells, fixed K capacity, risk/full-K
feasibility and cluster/bootstrap method. G2.7
metadata-only program `ic_g2_a2_protocol_preflight.py`
prepared but not run by operator. The whole revision
G2 preanalysis plan still includes A3/A4/A6 feasibility,
final signoff and G2 freeze before any G3 run.

## G2.8 A3 source triage next operator gate (2026-10-27)

G2.7 A2 source/method preflight **OPERATOR PASS**.
The nine old V2/V3/V4 threshold sensitivity
cells are predeclared but NOT yet calculated,
and the entire G2 protocol is still UNFROZEN.

For A3, created `ic_g2_a3_price_source_triage.py`
and `G2_8_A3_PRICE_SOURCE_TRIAGE.md`: classify
earlier G2.5 catalog filenames and read original
pinned price-alignment `.py` code **only**.
Price names / the original availability of
`price_on_or_before` are not proof of complete
point-in-time adjusted trading prices.
If no authentic historical pre-event volatility
series and source-verified validation cutoff
can be demonstrated, record A3 infeasible rather
than constructing a favorable comparison ex post.

**G2.8 NOT YET OPERATOR-RUN; G3 still BLOCKED.**

## G2.8 operator status and G2.9 source-discovery correction (2026-10-27)

G2.8 returned
`G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY`
and classified **28 SPY**, **43 target/test**
and **21 other** old source filenames, with
zero explicit price-stock candidate basenames.
But G2.5's earlier regex applied solely to
each basename and omitted generic ticker/date
files inside `price_cache_fmp_pickle`.
That is a **bounded inventory omission**, not
scientific evidence that historical stock prices
are absent. Original frozen V0 code directly
loads original `*_2026-07-05.pkl` stock-price
snapshots from that directory, with a prior G1.2
historical preflight showing 174 files.

A3 is **NOT** declared non-executable on the
strength of G2.8. Created G2.9 direct
`price_cache_fmp_pickle` filename-and-hash
inventory, without deserializing prices; see
`G2_9_A3_DIRECT_PRICE_CACHE_INVENTORY.md`.

Even if many ticker price files exist, a sound
conventional risk comparator still needs
**strictly before each event close** returns,
historically available adjustment/quote sources,
original validation cutoff/capacity matching,
fixed missingness rules, and post-outcome
exploratory characterization. These are not
proven from file paths/snapshot suffix names.
G2 still active; G3 blocked.

## G2.10 date-only price coverage gate prepared (2026-10-27)

G2.9 operator PASS recovered **3,649** original
FMP price cache files, including **174** original
`2026-07-05` snapshots (**173 equities+SPY**)
and another 174 `2026-08-10` files, with zero
watched group files skipped from SHA inventory.
A3 original-source availability therefore no
longer has the G2.8 basename-only false-negative.

Next `G2_10_A3_PRICE_DATE_SCHEMA_GATE.md` and
`ic_g2_a3_original_price_schema_dates.py`
stage a trusted-original-Pickle, operator opt-in
check of **column-name schema and calendar
date coverage only**. No stock close values
are evaluated; all old performance comparisons
remain G3-blocked. Bar DATE < event DATE is
necessary but insufficient for source-vintage
availability; original original July-5 price
snapshot is later than May/June news.
G2.10 NOT YET OPERATOR-RUN.

## G2.10 operator PASS, G2.11 analysis designs (2026-10-27)

The corrected original 174-file snapshot schema/date-only
audit completed: five static tests PASS, every
file has `DATE_STRUCTURE_OK`, and every
file has >=61 historical close dates before
the earliest event dates for V4, V2 and V3.
**No market close values or outcomes were evaluated.**
Point-in-time acquisition and adjustments cannot
be established merely from a July 5 snapshot saved
after the May/June signal dates; all-row/event
coverage and original validation mapping unverified.

Prepared A3 volatility source/analysis design in
`G2_11_A3_VOLATILITY_BENCHMARK_DRAFT.json`
and separate A4 economic/flat and A6 top-K drafts
in `G2_11_A4_A6_ECONOMIC_CAPACITY_DRAFT.json`.
See `G2_11_A3_A4_A6_CONTROLLED_HANDOFF.md`.
These specify source and validity conditions
but are **DRAFT**, not experimental work,
and must not be interpreted as having performed
a risk benchmark or found trade profitability.
G2 still active, G3 locked.
