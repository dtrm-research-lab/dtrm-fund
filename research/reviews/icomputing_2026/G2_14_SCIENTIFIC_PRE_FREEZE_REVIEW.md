# G2.14 — Scientific adversarial checkpoint before freezing the revision protocol

**Manuscript:** ICOMPUTING-D-26-01069
**Decision:** Major revision, 26 October 2026
**Deadline:** 25 November 2026
**Checkpoint:** 28 October 2026
**Status:** PRE-FREEZE DRAFT — not an approved experiment, G3 BLOCKED.

## Executive finding: stop repeating inventories; choose scientifically defensible experiments

A genuine source-data feasibility milestone is now met.
Historical `G2.13` passed **7/7** code-only regression
tests and **19,880/19,880** original V0 validation rows
with 60 strictly earlier dated prices, across **167**
symbols (validation dates 2025-12-24 to 2026-01-21).
The original V2/V3/V4 archive had already shown
**47,596/47,596** individual event/ticker pair-date
coverage, with original V1/V4 order/key equality.

These source facts are **necessary** for building a
conventional retrospectively dated volatility
comparator. They are **not sufficient** for
promising a contemporaneously implementable
risk filter or tradable strategy. The original
source `*_2026-07-05.pkl` files were compiled
after the old validation and test decisions,
and their version/adjustment vintage remains
unauthenticated. Source closes have not
been evaluated for numeric quality in the
G2 pre-analysis steps.

The key scientific decision is to accept a
**bounded retrospective exploratory comparison**
(A3) **if and only if** all missing-close,
ticker coverage, as-of labeling, common-case
selection and validation-only threshold rules
are frozen without using known V2/V3/V4 target
results. No independent confirmation is possible
from those already consumed outcomes.

This is an adversarial **design review draft**,
not an assertion that independent human
review, the full G2 freeze checker, or
any new experiment has completed.

## Source and result anchors

| Original evidence | Scientific status | Hash or check |
| --- | --- | --- |
| Frozen original V0 implementation | Unchanged | `c7502a690162459cdfb3413573e3133c42efb126` |
| Historic G1 sealed replication dossier | Numerical reproduction, provenance limited | `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac` |
| G2.5 old original files inventory | 92 metadata-only files | `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7` |
| G2.6 original P10 weighted validation source | 9 code rules PASS, q25 original replicated | `1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2` |
| G2.7 A2 study specification | 9 threshold × cohort cells fixed, NOT run | `5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8` |
| G2.9 original price-cache inventory | 3,649 files, 174 original July-5 snapshots | `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb` |
| G2.10 original date schema | 174/174 60-return date eligibility at first cohort events | `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3` |
| G2.12 all old holdout event dates | 47,596/47,596 pair-date coverage, 7 tests PASS | `e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f` |
| G2.13 original V0 validation dates | 19,880/19,880, 7 tests PASS | Output SHA **NOT YET PROVIDED** |
| Original V0 model-row input | New retrospective source SHA, not historic pre-outcome timestamp | `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724` |

G2.13 output (local only):
`$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json`.

## Adversarial design red flags and required control

**RISK 01 — Survivor/vintage leakage, CRITICAL.**
The July-5 price archive is retrospective to
December–June decision dates. Earlier bar dates
alone do not demonstrate that adjusted prices,
symbol history and corporate actions had
those exact values as of the historic event.
Control: never call A3 *prospective*,
*event-time authenticated*, *independently
validated* or *economically executable*. A
post-hoc **historically dated-bar volatility
reconstruction** may be analyzed only after
this limitation is explicit and the fixed
formula/inputs are sealed. If even retrospective
validity fails, mark A3 NOT_EXECUTABLE.

**RISK 02 — Numeric input eligibility, HIGH.**
A3 date-only PASS says nothing about `close`
values being finite/positive, stock split
jumps, duplicates after normalization or
interior gaps. Must specify exact numeric
validation and pair exclusions *before*
any financial score/outcome analysis. Preserve
excluded counts and their distribution by
cohort and source, not a favorable subset.

**RISK 03 — Fair comparator validation, HIGH.**
A3 risk cutoff can never be calibrated on
V2/V3/V4 outcomes. Fix it from the original
V0 `split="valid"` sample only: original
P10 validation admission budget versus
weighted percentile of past-only 60-day
volatility using the same legacy news weights.
Ties/pass discrepancy and the original
non-weighted/raw acceptance count must be
reported. Do not select another volatility
lookback, threshold or risk feature by old
outcome gain.

**RISK 04 — Sample-definition shift, HIGH.**
The baseline, original q25 veto and
volatility arms must all share exactly
the same predeclared eligible pairs,
ranking, tie policy and K. If price
data force excluding pairs, label results
a **secondary complete-case estimand**,
never silently substitute for original
full-cohort HDPG effect. Full-K
feasibility failures stay visible.

**RISK 05 — False economic interpretation, HIGH.**
The old outcome `forward_excess_beta` is
not realized capital-weighted trading P&L.
Flat/cash cannot be compared directly
with an excess-beta score as though the
units were absolute strategy returns.
Without execution timestamps, positions,
self-financing capital, overlap netting,
actual fee/spread assumptions and price
adjustments, report turnover/costs and
strategy P&L as **NOT_ESTIMABLE**,
rather than present event-level theoretical
forward returns as trading profits.

**RISK 06 — Reusing consumed outcomes, CRITICAL.**
The original V2/V3/V4 60-day outcomes are
already known, overlap over time, and V2
and V4 ticker-cluster 95% intervals include
zero. An additional cutoff/K/volatility
comparison can be a transparent **post-outcome
exploratory sensitivity analysis**, not
a newly independent confirmatory
hypothesis test or causal evidence.

**RISK 07 — Human/model-generalization, HIGH.**
A preselected human-authored filter does
not measure experimental human judgment,
and a single frozen XGBoost ranker does
not establish empirical model independence.
Use design-level versus observed-treatment
claims consistently in manuscript/rebuttal.
A second pre-outcome frozen model is not
verified; adding a newly trained one
could not recreate independent original
evidence.

## Constrained work-package disposition before any G3

| Work | User/editor evidence | G2 decision candidate |
| --- | --- | --- |
| A1 old CIs, overlaps, human claims | Previously sealed G1, no new target values needed | **DESCRIPTIVE** in G4/G5 |
| A2 q15/q25/q35 weighted P10 validation veto | G2.7 source/method preflight PASS | **ELIGIBLE TO FREEZE AS EXPLORATORY**, 9 historical cells, no best-q promotion |
| A3 trailing-stock-volatility conventional comparator | G2.12/G2.13 bar dates PASS | **CONDITIONALLY ELIGIBLE** only with numeric source validity, missingness, common-universe, provider-vintage caveat and validation-only cutoff frozen |
| A4 economic/flat/cost interpretation | No observed capital/portfolio cost ledger established | **DESCRIPTIVE NOW**; actual tradable P&L/turnover **NOT_ESTIMABLE** unless separately sourced and fully predeclared |
| A5 second ranker | No authenticated alternative historic ranker established | **NOT EXECUTABLE**, narrow model-agnostic claim |
| A6 original 10% K and 5/10/15% grid | Fixed original rank + veto, no new cost data needed | **ELIGIBLE TO FREEZE AS EXPLORATORY**, nine historical cells, same full-K rule |
| A7 relevant finance AI citations | G2.4 publisher checked shortlist | **DOCUMENTATION**, incorporate accurately in G5 |
| X1 nonoverlapping independent holdout | G1.3 old source search found none | **NOT EXECUTABLE IN THIS REVISION**, genuine future prospective study only |

Do not authorize G3 analysis just because a row
is marked *eligible to freeze*. Those categories
are decisions to **complete a protocol** and
pass a final source/signature check, not evidence
that the experiment has been executed.

## Finite G2 exit checklist — no new broad inventories

1. **One operator artifact bind:** SHA256 of
   `IC_G2_13_A3_V0_validation_bar_dates.json`.
2. **One finite original-stock numeric/date policy:**
   fixed 60-prior-return formula, missing-price
   and adjusted-vintage treatment; declare lack
   of archival acquisition proof instead of
   implying it has been found.
3. **A2+A6 executable spec and A3 conditional
   secondary spec** with exact source hash,
   matched baseline/K definition, report
   columns, original 10k bootstrap cluster
   estimators, infeasible-resample behavior.
4. **A4/A5/X1 fixed disposition:** genuine
   additional data or justified no-test;
   never invent return/cost or alternate
   ranking model evidence.
5. **G2 reviewer 22-item traceability** and
   honest rebuttal draft, G2 final
   freeze validator, manual scientific
   adversarial signoff and frozen commit.

**G2 CURRENT STATUS: ACTIVE, NOT FROZEN.
G3 EXPERIMENTS: NOT AUTHORIZED.**
