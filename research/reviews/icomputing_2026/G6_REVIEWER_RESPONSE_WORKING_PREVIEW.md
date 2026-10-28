# Working draft — Point-by-point response to Intelligent Computing reviewers

**Manuscript:** ICOMPUTING-D-26-01069
**Decision:** Major revision, 2026-10-26
**Due:** 2026-11-25

**STATUS: WORKING RESPONSE / NOT SUBMITTED / NO NEW ANALYSES CLAIMED.**
This draft is written **before** G2 protocol freeze or G3 experimental runs.
Every future-outcome, benchmark or additional return value is
intentionally marked **[PENDING G3]**; no such result exists yet.
The quoted statements below are paraphrased summaries of
the author-supplied 2026-10-26 reviewer letter,
not verbatim reviewer quotations.

## Cover note (working text)

We thank the Editor and both reviewers for their careful and
constructive assessment of the manuscript. We agree that
the current results warrant a more precise distinction
between improvements in a frozen decision ranking and
robustness, genuine model independence, and economically
realizable financial returns. In the revision, we aim
to strengthen methodological transparency, disclose
the limits of the overlapping 60-day historical
outcome windows and ticker-cluster uncertainty,
add prespecified exploratory sensitivity and
conventional-risk comparisons where source
feasibility permits, and narrow the claims about
human judgment and economic performance. We
retain unsuccessful tests and original evidence
without retrospective revision of the promoted
policy. **[EDIT AFTER G3/G4: enumerate actual
analyses completed and revised section numbers.]**

## Reviewer #1

### R1-01 — Independent non-overlapping temporal test

**Response (limitation):** We agree that a truly
independent temporal holdout with non-overlapping
60-day outcomes is needed to assess external
robustness convincingly. The original V2 and V3
event windows are adjacent and their forward
outcomes are correlated through overlapping
calendar periods. We cannot represent these
results as independent forward-horizon replications.
A targeted audit of available historical sources
did not establish another genuinely unused
point-in-time event cohort with a matured,
non-overlapping 60-day outcome before the
revision deadline. We therefore will explicitly
acknowledge this unresolved limitation and
present a prospective frozen-model acquisition
and evaluation protocol as future work. We
do not create a synthetic or retrospectively
selected 'independent' holdout.

**Planned manuscript revision:** Results and
limitations; protocol for future prospective
validation. **[PENDING G5 section numbers]**

### R1-02 — Ticker-cluster uncertainty and overlapping outcome windows

**Response:** We agree that the original
ticker-cluster 95% intervals prevent broad
claims of statistically robust outperformance
across all cohorts. The original incremental
Top-K `forward_excess_beta` means were
approximately +0.1443 (V2), +0.1494 (V3)
and +0.0276 (V4); the ticker-cluster intervals
for V2 (approximately -0.0062 to +0.1962)
and V4 (-0.0105 to +0.0718) include zero.
We will report inference under the distinct
news and ticker clustering schemes, explain
why V2/V3 60-day outcomes overlap and avoid
describing the three cohorts as statistically
independent 60-day tests.

**Planned manuscript revision:** Results, limitations.

### R1-03 — Original q25 cutoff and q15/q25/q35 sensitivity

**Response:** We agree that a single veto
cutoff requires sensitivity analysis.
Importantly, 'P10' refers to the 10th predictive
quantile of the model, whereas the original
'25th percentile' is a separate weighted
threshold of those calibrated P10 predictions
on the validation distribution. The original
promoted threshold was
`-0.16665692627429962`, fixed before the
original historical holdouts. The proposed
sensitivity uses weighted validation P10
percentile thresholds q=0.15, 0.25 and
0.35, preserving the same model, ranking,
capacity and outcomes; no alternative
prediction quantile models are trained.
All acceptance rates, Top-K fills and
effects, including adverse and infeasible
ones, will be reported without selecting
a better-performing cutoff retrospectively.
**[PENDING G3: actual q15/q35 thresholds
and all nine V2/V3/V4 outcome/feasibility cells.]**

**Planned manuscript revision:** Methodology and
exploratory sensitivity results.

### R1-04 — Conventional volatility/downside benchmark

**Response:** We agree that a probabilistic veto
must be contrasted with a standard risk-control
filter to isolate its incremental methodological
value. The original fixed ranker and full-K
selection will be shared across arms. The
proposed conventional control uses a stock's
trailing volatility based exclusively on
strictly pre-event historical dated bars, with
a validation-only cutoff matched to the
original P10 validation admission budget.
The same complete-case event/ticker universe
will apply to all arms, and excluded rows
will be disclosed. We emphasize an important
source limitation: the original 2026-07-05
FMP cache contains earlier bar dates, but
was saved after the old signal decisions;
historical provider acquisition and
corporate-action-adjustment vintage have
not been independently authenticated.
Thus any supplemental benchmark using
these data is a **retrospective, post-outcome
exploratory** comparison, not proof of a
deployable contemporaneous signal.
**[PENDING G2 FREEZE/G3: finalize numeric
price/missingness controls and report all
old-cohort results or explain infeasibility.]**

**Planned manuscript revision:** Benchmark methods,
exploratory results and source-vintage limitations.

### R1-05 — Negative absolute targets, practical returns, downside, turnover and costs

**Response:** We agree that incremental
improvements in `forward_excess_beta`
must not be conflated with investment profit.
The guardrail-improved absolute excess-beta
mean remained negative in the originally
reported successful cohorts. This target
is beta-adjusted 60-calendar-day forward
performance, not a self-financing realized
portfolio return. We will make that
distinction explicit and discuss downside,
noninvestment, turnover, trading costs and
overlapping repeated ticker exposures.
Any illustrative historical gross-stock-return
or cost scenario will be clearly separated
from the original target and will require
a fully specified price/entry/exit/capital
accounting protocol. Where a trustworthy
portfolio ledger is unavailable, realized
P&L, turnover and cost impact will be
identified as **not estimable**, rather than
asserted as empirical findings.
**[PENDING G2/G3: determine scope of any
defensible supplemental economic analysis.]**

**Planned manuscript revision:** Economic interpretation
and limitations.

### R1-06 — What exactly was human-defined; model-agnostic claims

**Response:** We agree. The experiment evaluates
a **human-specified deterministic rule**
that constrains a machine-generated ranking,
not direct interventions by human decision
makers or a causal human-versus-AI
comparison. We will distinguish the
governance design principle from its
experimental evidence and replace any
unqualified causal superiority language.
Likewise, the architecture can be designed
to accommodate alternate rankers, but
the observed results currently apply
to the single tested frozen model.

**Planned manuscript revision:** Introduction,
framework, discussion and abstract.

### R1-07 — Second ranking model

**Response:** We agree that applying the
same guardrail to another independently
specified ranker would provide evidence
for empirical model independence.
No authenticated second pre-outcome frozen
ranker with compatible source/feature
lineage has yet been established in the
audited historical materials. We will
avoid presenting design portability as
an experimentally demonstrated
across-model effect; any second-ranker
experiment is conditional on authentic
source provenance and is otherwise
future work. **[Do not claim a second
model experiment without new evidence.]**

**Planned manuscript revision:** Evidence scope
and future work.

## Reviewer #2

### R2-01 — Human-defined judgment versus algorithmic filter

**Response:** We concur that the experimental
effect identified is attributable to the
addition of the predefined deterministic
constraint, rather than a measured marginal
effect of live human judgment. We will
clarify that HDPG's human role is the
upstream specification of objective,
failure definition, veto rule and governance
accountability, while the downstream
application is algorithmic. We will
contrast this governance interpretation
with standard algorithmic filtering,
without claiming a causal superiority
effect attributable to human intervention.

**Planned manuscript revision:** Methods and discussion.

### R2-02 — Choice of P10 and weighted 25th percentile

**Response:** We will distinguish the
chosen predictive lower tail (P10) from
the percentile used to set an admission
veto on the validation distribution.
P10 encodes downside-sensitive uncertainty;
the original validation q25 cutoff is a
separate governance/selection rule.
Neither choice will be described as
proven optimal. We will report a fixed
exploratory weighted q15/q25/q35
validation cutoff sensitivity, preserving
the original q25 rule.
**[PENDING G3 numerical sensitivity.]**

**Planned manuscript revision:** Model choice,
decision rule and sensitivity.

### R2-03 — V2/V3 overlapping forward outcomes

**Response:** We agree. Distinct, adjacent
news event windows do not imply independent
60-day forward-return outcome periods.
The revision will remove any language
treating V2–V4 as three independent
temporal validations and explicitly note
the overlapping observation calendar.

**Planned manuscript revision:** Study design,
inference and limitations.

### R2-04 — V2 and V4 ticker-cluster intervals include zero

**Response:** The original 95% ticker-cluster
intervals for V2 and V4 overlap zero.
We will explicitly treat this as an
important limitation, not claim
uniform ticker-level statistical
robustness and separate ticker- from
news-event-cluster evidence.

**Planned manuscript revision:** Results and discussion.

### R2-05 — No-action/flat, target nontradability and transaction costs

**Response:** A noninvestment alternative
is an important decision option,
especially when the original
absolute excess-beta means are
negative. However, flat cash gross
returns and `forward_excess_beta`
are not the same estimand; directly
comparing zero cash to negative
beta-adjusted score would
misstate tradable performance.
We will discuss abstention
using a separately defined absolute
return or properly funded
portfolio metric when supportable,
and acknowledge spread, fees,
slippage and overlapping exposure
limitations otherwise.
**[PENDING executable source/portfolio
accounting feasibility.]**

**Planned manuscript revision:** Decision/abstention
discussion and economic limitations.

### R2-06 — Justification of K = floor(0.10N)

**Response:** We agree that K=10% is a
fixed experimental selection-budget
assumption rather than a proven
capital/liquidity capacity. It
was held equal for paired
baseline-versus-veto comparisons,
not optimized from old outcomes.
We will clarify the rationale
and, subject to final
preanalysis controls, show a
fixed retrospective sensitivity
at 5%, 10% and 15% coverage
with the same original ranker
and original q25 gate.
**[PENDING G3: all nine
K-by-cohort cells and infeasibility.]**

**Planned manuscript revision:** Capacity
policy and sensitivity.

### R2-07 — V4 attenuation and weekly instability

**Response:** The frozen V4 incremental
mean (+0.0276) is much smaller than
V2/V3 (~+0.14–0.15), and only
four of the six V4 weeks had
positive incremental outcomes.
This argues for a narrow,
regime-dependent and
sampling-sensitive interpretation
rather than a consistently
large stable effect. We will
disclose that temporal heterogeneity
and the V4 ticker-cluster CI
including zero without assigning
an unverified causal explanation
to a specific market regime.

**Planned manuscript revision:** Cohort
heterogeneity, discussion and limitations.

### R2-08 — Relevant AI decision-making literature in finance

**Response:** We agree and will broaden
related work on machine learning
for asset pricing, selective
prediction/abstention, interpretable
high-stakes systems and human-AI
complementarity. We will distinguish
prior algorithmic risk filters from
the governance architecture
proposed in HDPG and avoid
claiming that references
establish missing financial
robustness. Bibliography
will be verified against
publisher source and original
manuscript duplicates.
**[G2.4 literature shortlist
prepared; insertion into G5
not yet completed.]**

**Planned manuscript revision:** Introduction
and Related Work.

## Final package completeness (editor E-01–E-07)

**NOT YET DONE:** Complete response/rebuttal
(E-01), highlighted independent manuscript
(E-02), publication-quality separate
figure source files (E-03), signed all-author
License and COI forms (E-04), image
permission paperwork where relevant (E-05),
conditional authorship-change signatures
(E-06), and 2026-11-25 Editorial Manager
resubmission (E-07).

Reviewers' IDs R1-01..R1-07 are **our own
audit segmentation** of Reviewer #1's
un-numbered original paragraphs; R2-01..R2-08
preserve Reviewer #2's original numbered order.

**No scientific or editorial deliverables should be
reported as completed until corresponding G3/G4/G5/G6/G7
artifacts have been produced and audited.**
