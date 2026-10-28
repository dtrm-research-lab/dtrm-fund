# G2.17 — Canonical scientific protocol: candidate for immutable G2 freeze

**Editorial case:** ICOMPUTING-D-26-01069
**Source:** user-provided full editor/reviewer email body 2026-10-26
**Deadline:** 2026-11-25
**Method frozen original commit:** `c7502a690162459cdfb3413573e3133c42efb126`
**Status:** FREEZE CANDIDATE — independent tests and operator approval PENDING.
**Interpretation:** these decisions are pre-analysis specifications; old V2/V3/V4 outcomes are known. This is **not** prospective preregistration.
**Never authorize G3.1 automatically on this document.**

## I. Source and negative-evidence locks

Original target `forward_excess_beta` compares
60-calendar-day stock return with `beta_pre` × SPY return.
This is NOT_REALIZED_TRADING_PNL. No realized cashflow,
self-financing strategy return, turnover or fees have been
measured on the original historical cohort.
Original V1 absolute calibrated P10 > 0
admitted **zero** events and was infeasible.

Original V2/V3/V4 cohort sizes: 4,449 / 2,827 / 40,320.
Original K=floor(0.10N): 444 / 282 / 4,032.
Frozen relative calibrated P10 threshold:
`-0.16665692627429962`, P10 calibration offset
`-0.06494169682264328`, original best
P10 iteration 18, baseline iteration 10.
Original incremental means:
V2 +0.14429480582475662,
V3 +0.14943748898804188,
V4 +0.027561593800783157.
95% ticker-cluster intervals include zero for
V2 and V4; V4 weekly 4/6 positive.
Forward 60-day windows overlap, including
V2 and V3. Absolute candidate excess-beta
mean was negative in all reported original
successful cohorts. No new independent,
non-overlapping 60-day holdout has been
verified in historical audited source scope.

Original model/feature/price acquisition
vintage and vendor corporate-action
adjustments are NOT fully authenticated.
G1 reconstructed boosters are not
the original saved model binaries.
Model-agnostic refers to intended design
portability, NOT measured across-model efficacy.
Human input is the predefined deterministic
decision rule; there was no randomized
human-vs-AI intervention.

## II. Approved-for-test design; NOT approved to execute G3.1

**G3.0 ONLY, after operator scientific signoff and
immutable frozen protocol commit.**
- Trust only original SHA-verified local files,
  with explicit trusted-original-Pickle consent;
  never share private original FMP price
  or news/embedding data in GitHub.
- On original V2/V3 saved feature and
  signal pair orders, verify baseline predictions
  and calibrated-P10 veto masks using SHA-pinned
  retrospectively reconstructed booster weights.
  Numeric P10 original source reference may
  not exist in V2/V3; if missing, report
  'mask and baseline parity, numeric P10
  reference absent', NOT unqualified numeric
  P10 parity. Never guess from ambiguous
  prediction column names.
- Verify strictly Boolean source veto fields,
  original SHA of X and signal Pickle,
  iteration ranges [0,11) and [0,19),
  plus original threshold and offset.
  If any strict parity requirement fails,
  refuse G3.1 authorization.
- Do NOT load V2/V3/V4 original forward
  target/result Pickles in G3.0.
- **G3.1 remains blocked regardless of
  G3.0 runtime status until separately approved.**

**G3.1 A2 (conditional after G3.0 full parity) —
EXPLORATORY POST_OUTCOME.**
Use original model V0 19,880 VALID observations,
original source-calibrated P10 + same per-news
validation weights. Original weighted quantile
values via `np.argsort` + cumulative weights +
`searchsorted(side='left')` at q15/q25/q35,
same P10 predictive quantile not new P15/P25/P35.
Reproduce q25 original cutoff and V2/V3/V4
q25/K10 historic result before any alternative.
Report all nine cells, negative effects, missingness,
admitted rows, exact full-K feasibility and
both news/ticker cluster-bootstrap uncertainty.

**G3.1 A6 (conditional) — EXPLORATORY POST_OUTCOME.**
Use original calibrated P10 q25 veto and
baseline `np.argsort(-prediction)` tie/ranking,
same V2/V3/V4 originals, for coverage fractions
5/10/15%, K=floor(fraction × N) on each cohort.
Report all nine cells and infeasible counts,
no best-K optimization.

**G3.1 A3 (conditional) — RETROSPECTIVE
POST_OUTCOME_EXPLORATORY.**
Daily volatility score is sample `std(ddof=1)`
of exactly 60 simple returns from last 61 unique
historically dated closes **strictly before the
event UTC calendar date**. No event-day or later
close, and no 40-return primary fallback,
imputation, interpolation, adjustment, forward fill
or winsorization. Selected 61 closes must
be finite and strictly positive; duplicate
bar dates or invalid price source block or
exclude with full reasons. Source-price
quality must be counted before outcomes,
and all arms use identical common-eligible
test event/ticker pairs and
K=floor(.10 × common_N).

Conventional volatility veto cutoff comes
**only** from original validation V0 common-
eligible sample: set weighted risk percentile
to original P10 weighted admission fraction,
recompute original inverse-news-id weights
within that exact validation common sample,
record tie admission discrepancy. No
V2/V3/V4 target to choose risk threshold or
lookback. Keep baseline, P10, risk arms on
identical ranker and subset. Report all
three old cohorts, negative/null results,
full-K infeasible, sample exclusions, vintage
and unknown corporate-action adjustment status.

Original G2.9 price-cache metadata report SHA:
`65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`;
G2.10 date schema SHA:
`f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`;
G2.12 V2/V3/V4 dates SHA:
`e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`;
G2.13 V0 validation dates SHA:
`e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`.
All 47,596 old test pairs and all 19,880
original V0 validation pairs have >=61
historic dated closes *in a later archive*.
This is source-DATE coverage, not true
historic vendor as-of price availability.

**Uncertainty rule:** exactly 10,000
news_id and 10,000 ticker cluster resamples
(seeds 20260821, 20260822), duplicate full
cluster rows per draw; rerank/recompute K each
resample; 95% linear percentile CI
*only if every replicate feasible*.
Report all failures. Never pool 3 cohorts
as independent p-values. Existing old
outcomes already known; all new sensitivity
estimands explicitly secondary exploratory.

## III. Not-executable or descriptive reviewer dispositions

- **A1**: reuse original dependence-aware
  bootstrap evidence; ticker uncertainty
  includes zero in V2/V4, overlapping horizon.
- **A4**: separate excess-beta from absolute
  gross equity returns and no-investment cash;
  actual self-financing portfolio return,
  turnover, fees and slippage **NOT_EXECUTABLE**
  with authenticated historic trading ledger;
  no cash-versus-excess-beta false comparison.
- **A5**: no second preoutcome authentic
  frozen ranker; empirical cross-model
  independence **NOT_EXECUTABLE**.
- **A7**: literature/related work integration
  using verified references; no new financial
  inference or overstated causal claims.
- **X1**: new nonoverlapping 60-calendar-day
  prospective holdout **NOT_EXECUTABLE** with
  currently verified audited sources before
  2026-11-25; future independent
  pre-registered data collection is needed.

## IV. Exhaustive 22-point editor/reviewer trace

Official letter/editorial package: E-01..E-07,
including marked revisions, standalone
figures, authorship/legal/COI forms and
Editorial Manager 2026-11-25 resubmission.
Reviewer 1 decomposed themes R1-01..R1-07
(internal analysis IDs), reviewer 2 numbered
R2-01..R2-08. Content mapping:
`G2_REVIEWER_TRACEABILITY_PROVISIONAL.json`
and its G2.17 reconciled candidate.
These are 22 distinct tracked editorial
requirements, not 22 new experiments.
All G5/G6/G7 final documents remain
PENDING and no editorial submission is
claimed. Reviewer source is user-pasted
body, no independently verified provider MIME.

## V. Genuine freeze and approval rules

1. G2.16 synthetic + source gate must pass
   **CURRENT VERSION 31 source-only tests**.
   Earlier 29/29 PASS is valid only for
   previous G3.0 script version and cannot
   certify the later stricter P10 reference
   checker. The final operator G2.16 report
   SHA must be independently computed on
   the user's Mac and stored in G2 freeze record.
2. Old G2 final freeze checker must pass
   **actual 22** reviewer/editor items and
   properly linked conditional analysis specs
   or precise NOT_EXECUTABLE disposition.
3. Full scientific protocol, scope and
   source-hashed runner must have a
   **real immutable Git commit**, verifiable
   in the checked-out GitHub repository.
   No self-referential made-up SHA.
4. Human owner must inspect limitations,
   explicitly approve **G3.0 SOURCE PARITY
   ONLY**, and preserve that action in
   a separate audit-manifest JSON.
   The approval must be anchored to
   the final G2.16 report SHA and
   immutable scientific protocol commit.
5. G3.1 old-target access remains
   **NOT_AUTHORIZED** until a separately
   approved versioned reader/analysis runner,
   verified original source-parity result
   and a new bounded stage-specific gate.

**As of this candidate document: G2 NOT FROZEN,
G3.0 NOT YET AUTHORIZED, G3.1 BLOCKED.**
