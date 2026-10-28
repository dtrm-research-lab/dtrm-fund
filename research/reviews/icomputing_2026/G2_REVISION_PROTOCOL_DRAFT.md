# G2 — Intelligent Computing major revision analysis protocol (DRAFT, UNFROZEN)

Date 2026-10-27 · ICOMPUTING-D-26-01069
Branch: `research/ic-major-revision-2026`.
G1: `CLOSED_WITH_LIMITATION_DOCUMENTED`.
G2: `ACTIVE_DRAFT_NOT_FROZEN`.
G3: `BLOCKED_UNTIL_G2_CLOSED`.
Journal revised manuscript deadline: 2026-11-25.

## Purpose — the G2 exit gate

G2's deliverable is a **fixed editorial/scientific revision protocol**
that covers every actual review objection and freezes, *before any
new G3 computations*, which existing outcomes and post-hoc analyses
may be examined, which rules/metrics/thresholds apply, what
is impossible, and which limitation statements must be published.

This is broader than G1.3's *independent new-cohort* pre-registration.
G1.3 stays input-source BLOCKED without preventing completion
of the broader 7-gate paper-revision graph.

The list below records known concerns from the G0/G1 audit,
**not** an exhaustive/verbatim quotation of the actual
Intelligent Computing major-revision letter. The exact editor
and individual reviewer points must be retrieved, assigned
stable `E-xx`, `R1-xx`, `R2-xx` labels, and crosswalked
before this G2 protocol can become `FROZEN`.

## Scope lock — original controls: do not change

Original code:
`c7502a690162459cdfb3413573e3133c42efb126`.

Historical evaluated cohorts:
- V1/V4 reuses 2026-05-02 through 2026-06-06, 40,320 pairs;
  V1 absolute calibrated-P10>0 feasibility FAIL, zero accepted;
  V4 frozen relative guardrail accepted 23,348.
- V2: 2026-06-07..2026-06-10, 4,449 rows, K=444.
- V3: 2026-06-11..2026-06-14, 2,827 rows, K=282.
- V4: 40,320 rows, K=4,032.

V2/V3/V4 historically frozen primary comparison:
- baseline ranker, its original fixed inference iteration 10;
- candidate same ranker ordered list with relative-P10 veto
  `calibrated_P10 >= -0.16665692627429962`;
- P10 original quantile model best iteration 18 and its
  validation-only calibration offset
  `-0.06494169682264328`;
- selection top K = `floor(0.10*n)` per original
  cohort, with original rank-order/tie semantics;
- candidate must fill complete K, or report infeasibility.
- Target `forward_excess_beta`:
  60 calendar-day stock return minus `beta_pre` times
  market (SPY) 60 calendar-day return; original
  next-on-or-after price alignment within 5 days.
- `beta_pre` constructed only with pre-event information,
  252-day lookback, min 60 observations, 20-day tolerance.
- No old ranker refit, new optimization, cutoff adjustment,
  historical cohort relocation or changing calibration.

Original V2/V3/V4 observed Top-K excess-beta improvements:
`+0.1442948058`, `+0.1494374890`, `+0.0275615938`.
Existing ticker-cluster 95% CIs:
V2 `[-0.0062202, 0.1961534]`,
V3 `[0.0075385, 0.1933165]`,
V4 `[-0.0104682, 0.0718196]`.
Ticker-cluster intervals cross zero in V2 and V4.
Original V4 weekly robustness: positive 4 of 6 weeks,
nonuniform time dependence. V2/V3/V4 outcomes are
**already consumed and not new prospective tests**.
`forward_excess_beta` is **not realized trading P&L**.

Original row/model reproducibility support:
- 9-report/4-reconstructed-booster historical G1.2k dossier
  SHA256 `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
- G1.2m original date-only sample selection proof
  SHA256 `388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.
- The same-basename original V1 raw file 265145/40320
  contract ambiguity stays explicitly disclosed (original
  generator/copy chain not authenticated).

## Preliminary reviewer-objection/analysis response map

The reviewer letter is not yet transcribed or independently
mapped; identifiers below are internal provisional `Q-xx`,
**not** statements about what a specific reviewer said.

| ID | Topic / question to resolve | Planned G3 disposition and hard limits | G2 freeze inputs |
| --- | --- | --- | --- |
| Q-01 | Reproducibility and data lineage | `DESCRIPTIVE_DOCUMENTATION`: G1.2k numeric input/model parity; G1.2m predeclared original date rule; preserve physical snapshot metadata caveat | Artifact hashes, source provenance, exact wording |
| Q-02 | Calibrated P10/left-tail validity | `SECONDARY_POST_OUTCOME_EXPLORATORY`: preregister validation-only lower-tail diagnostics, fixed P10 baseline, potential P15/P25/P35 sensitivity; DO NOT retune selection based on original test outcomes | Quantile interpretation, frozen sample/metric, count every specification |
| Q-03 | Is P10 veto adding value beyond conventional risk/volatility filters? | `SECONDARY_POST_OUTCOME_EXPLORATORY` only if contemporaneous risk proxies reconstructable; matched Top-K capacity and same baseline ranking; show negative findings and data gaps | Comparator definitions, data availability/time alignment, test multiplicity |
| Q-04 | Decision value vs executed/tradable profit | `DESCRIPTIVE_DOCUMENTATION` initially; `NOT_EXECUTABLE` for any unverified actual-trading P&L; simulations require precommitted timestamped price fills/cost/turnover and concentration assumptions | Formal mapping of per-event signals to portfolio, realistic cost policy |
| Q-05 | Impact of K, fill capacity and abstention | `SECONDARY_POST_OUTCOME_EXPLORATORY` or `NOT_EXECUTABLE`; register K grid, no ex post best pick, full-K and flat/ABSTAIN rules | Exact K grid, capacity, tie-break, handling of infeasibility |
| Q-06 | Dependence on tickers and temporal market regime | `CONFIRMATORY_ALREADY_FROZEN` for the old news/ticker bootstrap and V4 weeks results; any new stress test labeled exploratory | Existing CI/seed/settings, additional preregistered dependence sensitivities |
| Q-07 | Human-defined rule vs causal human-judgment effect | `DESCRIPTIVE_DOCUMENTATION`: distinguish human-designed algorithm from randomized human treatment; no causal superiority claim without human-arm experiment | Rewrite of framing, boundaries of tested treatment |
| Q-08 | Alternative frozen ranker and robustness | `SECONDARY_POST_OUTCOME_EXPLORATORY` only if truly precommitted alternative and model artifacts exist; otherwise `NOT_EXECUTABLE` and reported | Pin independent ranker selection and its prior cutoff, leakage audit |
| Q-09 | Genuinely independent later 60d event test | `NOT_EXECUTABLE_NO_VERIFIED_INPUTS` for this revision: G1.3a/b metadata inventories found no authorized unused new investment-news source locally; future capture plan only | Do not infer unavailable globally; transparent study-design/timing limitations |
| Q-10 | Presentation of statistical confidence / multiple comparisons | `DESCRIPTIVE_DOCUMENTATION` and, if G3 statistical updates predeclared, `SECONDARY_POST_OUTCOME_EXPLORATORY`: cluster units, 60d overlap, CI crossing zero, post-outcome multiplicity | Define primary vs secondary metrics and no selective exclusion |

## Fixed hypothesis/evaluation claim

**Historical original hypothesis, not newly confirmatory**:
frozen calibrated downside information used as a veto on a
frozen ex-ante ranking improves within-cohort selected mean
`forward_excess_beta` relative to baseline top 10%,
with full-K feasibility.

**Supported now**:
positive old point estimates for V2/V3/V4 and exact historic
replay; positive old news-cluster CIs, but not uniformly
robust across ticker concentration or calendar weeks.

**Not supported now**:
causal benefit of human oversight, absolute returns or
profitability, independence of same-market 60d windows,
all-ticker confidence, true post-October prospective results.

## G3 authorization matrix (draft)

- `ALLOW` after G2 frozen: reproduction/auditing of already
  reported original numerical summaries; drafting methods,
  errata and limitation statements without new datasets.
- `CONDITIONAL`: new analyses of old, already consumed cohorts
  **only** after exact preanalysis specification is frozen
  (data files, SHA256, comparator formulas, sample rules,
  K fractions, seeds, CIs, negative-result disclosure).
  Label exploratory/post-outcome; keep exploratory claims
  separate from original V2/V3/V4 frozen comparisons.
- `NO`: G1.3 genuinely new 60d effectiveness study, given
  no demonstrated eligible event-time source and no full
  preregistered data window. No new target/price opening
  until independently approved study gate.
- `NO`: merging unrelated Phase IV STAMP/MM1 or PaymentGame
  experiments as equivalent HDPG evidence.
- `NO`: modifying any original experiment YAML and claiming
  the modified code was original.

## G2 exit criteria — ALL REQUIRED

- [ ] Full editor decision letter and all original reviewer
      comments enumerated verbatim or in accurately
      attributed requirements, without invented numbering.
- [ ] Objection→action→G3 experiment/limitation→G5 section→G6
      response table completed, with an audit reference.
- [ ] Each G3 test/proposed analysis has explicitly fixed
      dataset/source hashes, hypothesis, estimand, metrics,
      time spans, filters/exclusions, comparator, random
      seed, uncertainty method, stop/capacity conditions,
      multiple-analysis presentation, and success/failure
      interpretation; OR it is explicitly `NOT_EXECUTABLE`.
- [ ] Scientific claim ceiling and all existing V1 negative
      results, V2/V4 ticker-CI cross-zero, and V4 weekly
      nonuniformity explicitly protected.
- [ ] Separation of revised-paper work from frozen original
      tags and other research areas verified.
- [ ] Revision protocol SHA/commit and reviewer-mapping
      checksum recorded BEFORE beginning G3 computations.
- [ ] G2 adversarial protocol review checked for
      cherry-picking, leakage, forecast-vs-return conflation,
      causal-human-overclaim and post-outcome tuning.

**G2 remains ACTIVE_DRAFT_NOT_FROZEN; G3 computation NOT AUTHORIZED.**

## 2026-10-27 G2.2/G2.3 UPDATE — real 26 October editor/reviewer text supplied

**Supersedes the older 'reviewer source missing' statement in this
draft.** The manuscript author supplied the complete 2026-10-26
Intelligent Computing major-revision decision email in the
conversation. The source content is available for scientific
requirements mapping but its provider-origin MIME/SHA was not
independently retrieved (not required to reason about the
user-supplied contents). Avoid implying external cryptographic
authentication.

Actual audit trace now **22 mapped requirements**:
editor 7 administrative conditions (E-01…E-07);
reviewer #1 seven **internally decomposed, unnumbered**
themes (R1-01…R1-07); reviewer #2 eight numbered
comments (R2-01…R2-08).
See `G2_REVIEWER_TRACEABILITY_PROVISIONAL.json`
and `G2_2_AUTHENTIC_REVIEWER_REQUIREMENT_MAP.md`.

Distinct G3 packages: A1 old CI/dependence interpretation;
A2 original P10 weighted validation veto percentile
15/25/35 sensitivity (NOT new predictive quantile models);
A3 original-as-of-date volatility baseline; A4 financial
returns/turnover/downside/no-action/cost validity; A5
authentic frozen second ranker (conditional); A6 Top-K
fixed-grid capacity sensitivity; A7 cited finance AI
literature; X1 genuinely independent non-overlapping
60-calendar-day test **NOT EXECUTABLE from audited inputs**.
See `G2_3_ANALYSIS_PACKAGES_DRAFT.md` and
`G2_4_VERIFIED_LITERATURE_SHORTLIST.md`.

The 22 requirements have proposed paper/response
destinations, but exploratory G3 plans still lack
input and source SHA anchors, checked feasibility
and formally signed freeze. **G2 remains ACTIVE,
UNFROZEN. G3 is blocked.**

## G2.5/G2.6 prior-source readiness status (2026-10-27)

G2.5 operator-run 92 original candidate files SHA-streamed,
no historical or prospective outcomes read. The original
pinned V0 source and G1.2 numerical replay code explicitly
specify all ingredients to reconstruct the old validation
calibrated P10 distribution and original weighted q25
threshold. G2.6 source/JSON binding has been prepared
but **not operator-run**. See
`G2_6_VALIDATION_SOURCE_BINDING.md`.
G2 stays UNFROZEN; no new P15/P35 percentile
values, financial outcomes or G3 secondary analyses
have been generated.

## G2.6 source PASS, G2.7 A2 method draft (2026-10-27)

The original 19,880-row V0 validation P10 source and
weighted q25 = -0.16665692627429962 were successfully
bound to original SHA lineage by the operator at G2.6.
G2.5 source metadata report SHA256
`ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`
and eight input references are retained.

G2.7 now prepares the author/reviewer R1-03/R2-02
A2 preanalysis plan in
`G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json`,
with fixed original validation distribution cutoff
q=0.15/0.25/0.35, same original ranker/P10 and
9 total historical V2/V3/V4 cells; correct
POST-OUTCOME_EXPLORATORY label. This is a drafted,
committed **protocol** not an empirical result.
Final A3/A4/A6 feasibility, source checkpoints,
adversarial review, human G2 signoff and freeze
SHA remain pending; G3 still BLOCKED.

## G2.10 dates PASS and A3/A4/A6 plan designs (2026-10-27)

G2.10 corrected operator status:
`G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`.
Five static regression cases passed. All 174
original July-5 source price frames (173 stocks
and SPY) structurally have sufficient bar-date
history before the original first-event dates.
This does NOT prove any per-event or original
validation cohort completeness nor historical
vendor vintage/adjustment point-in-time status.

Additional reviewer-linked draft source:
`G2_11_A3_VOLATILITY_BENCHMARK_DRAFT.json`;
economic/flat and K-grid:
`G2_11_A4_A6_ECONOMIC_CAPACITY_DRAFT.json`.
Current G2 freeze requires complete input/report
SHA and row/date eligibility, deciding on A3
source-vintage limitations, and explicit human
scientific signoff before any G3 old-outcome
exploratory runs. The deadline remains
2026-11-25. G3 still BLOCKED.

## 2026-10-28 G2.13 data feasibility PASS / G2.14 pre-freeze

G2.13 operator `G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN`
PASSED 7/7 static regression tests, and
all original 19,880 V0 `valid` pairs
(167 tickers) have 60 prior bar DATE
coverage from original 2026-07-05 source.
Prior G2.12 confirmed all 47,596 original
V2/V3/V4 historical pair dates also pass.

Source pins: G2.12 report SHA
`e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`;
original V0 model rows retrospective SHA
`3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
G2.13 local report SHA not yet separately provided.

For reviewer requested A3 conventional risk
comparison, date-source availability is now
structurally established; **historical provider
quote-vintage acquisition and corporate-action
adjustments are not**, because the original
July-5 snapshot postdates old decision dates.
See `G2_14_SCIENTIFIC_PRE_FREEZE_REVIEW.md`
and `G2_14_PRE_FREEZE_ADVERSARIAL_DISPOSITIONS.json`
for explicit go/no-go status.

A point-by-point English preview response is
now in `G6_REVIEWER_RESPONSE_WORKING_PREVIEW.md`;
it is a **DRAFT**, not a completed G6,
and describes no unexecuted analysis as done.
G2 still UNFROZEN; G3 BLOCKED.
