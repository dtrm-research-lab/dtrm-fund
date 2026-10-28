# G2.15 — Single freeze decision packet after G2.13 source-hash closure

**Case:** ICOMPUTING-D-26-01069 · **Date:** 2026-10-28
**Decision deadline:** 2026-11-25
**Status:** SCIENTIFIC PRE-FREEZE DECISION REGISTER, NOT AUTHORISATION TO EXECUTE G3.

## Inputs closed

We have **verified bar-date coverage**, not independent financial results:
- Original V0 validation **19,880/19,880** pairs, 167 tickers,
  event dates 2025-12-24 through 2026-01-21.
- V2 **4,449/4,449**, V3 **2,827/2,827**,
  V4 **40,320/40,320**, i.e. **47,596/47,596**
  distinct old test event/ticker pairs. Original V1
  and V4 signal key/date sets and row order agree.
- Original July-5 FMP price cache 174 series
  (173 stocks, SPY), confirmed source SHA inventory;
  no numeric price or predictive calculation was
  performed in the source/date checks.
- Original `legacy_model_rows_2026-05-01.pkl`
  currently SHA `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
- G2.12 report SHA:
  `e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`.
- **New G2.13 report SHA from operator**:
  `e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`.

Report digests are **operator-supplied local file SHA256**,
not provider-authenticated market-data vintages.

## Hard scientific decision on the A3 source

**Not justified:** 'Point-in-time volatility known when each
historic signal was generated.' The original July-5
cache was saved after V0 validation and May/June V2–V4
signals. We have not authenticated FMP download
timestamps, vendor corrections, split/dividend
adjustments or real contemporaneous input vintage.

**Potentially justified:** 'Retrospectively reconstructed
volatility from daily bars dated strictly before each
event', provided fixed numeric price/missingness
rules and validation-only cutoff source are frozen,
reported with source-vintage limitations and equal
baseline selection universe. This is supplementary
**POST_OUTCOME_EXPLORATORY**, NOT a genuinely new
independent temporal holdout and NOT tradable P&L.

If price quality or coverage fails this fixed
common-source design, mark the affected cells
`INFEASIBLE` and transparently provide the
comparison limitation. Do not replace the original
q25 or select a favorable alternative filter.

## Finite go/no-go decisions for the major revision

| Analysis | G2 verdict | Required research output |
| --- | --- | --- |
| A1 historic CIs, overlaps, deterministic human rule | **READY FOR DESCRIPTIVE G5 EDIT** | Preserve V1 zero-pass and original V2/V3/V4 values; explain V2/V4 ticker CI including zero and V2/V3 shared horizon |
| A2 q15/q25/q35 validation-weighted P10 veto | **ELIGIBLE FOR CONDITIONAL G3 AFTER FREEZE** | Exactly 3×3=9 old-outcome exploratory cells; no model retraining, no best-q promotion; original q25 must reproduce |
| A3 conventional trailing-volatility comparator | **SOURCE-DATE READY; EXECUTION CONDITIONAL** | Freeze numeric close eligibility, risk formula, equal common-eligible cohorts and validation-only cutoff; source-vintage caveat; no event-day bar |
| A4 gross cash/flat, turnover, costs, absolute P&L | **DESCRIPTIVE NOW; PORTFOLIO RETURNS NOT ESTIMABLE** | Distinguish 60d forward excess-beta from investable cash returns; never claim realized P&L without position/capital/fee ledger |
| A5 second original ranker | **NOT EXECUTABLE FROM VERIFIED SOURCE** | Narrow model-agnostic claim to architecture; do not fabricate second pre-outcome model |
| A6 fixed K policy and 5/10/15% sensitivity | **ELIGIBLE FOR CONDITIONAL G3 AFTER FREEZE** | Exactly 3×3=9 old-cohort exploratory cells, equal original ranker/veto, fixed full-K and infeasible handling |
| A7 human-AI finance literature | **READY FOR G5 EDIT AFTER CITATION RECHECK** | Cite actual sources only and avoid substituting literature for unrun experiments |
| X1 new nonoverlapping 60d independent holdout | **NOT EXECUTABLE UNDER VERIFIED G1 SOURCE SCOPE** | Explicit limitation and prospective future plan; no manufactured test sample |

## Final G2 freeze blockers — not new general inventories

**B-01: Frozen implementation.** A2/A6 still need
tested exact **G3 analysis code plus content SHA**
and parity against original V2/V3/V4 q25/K10
before running any alternative rule. A3 needs
a separately source-checked implementation with
identical ranker, event keys, weighting and
common-sample semantics. Draft JSON alone
does **not** authorize a scoring run.

**B-02: Numeric source use/eligibility policy.**
Before opening original quote numeric values,
freeze the primary A3 rule: select last 61
trading bars with dates strictly earlier than
the UTC event calendar day; require 60 valid
consecutive daily close-to-close returns,
positive finite closes and no date duplicates.
If any selected bar's close is invalid,
exclude that event pair from **all** comparator
arms, and report missingness. Do not replace
missing observations, interpolate, winsorize
split jumps or change window after observing
historical targets. The earlier draft allowed
a minimum 40-return fallback; it is **not
approved as primary** until an explicit
decision resolves that competing policy.
A separate 40-min fallback could be labeled
exploratory only if fixed before G3.

**B-03: Retrospective vintage.** Frozen answer
must say 'past-dated prices extracted from a
later archived snapshot', not original
event-time acquisition proof. If authentic
provider-vintage adjusted close cannot be
established, disclose as limitation even
when a retrospective A3 benchmark is run.

**B-04: Bootstrap feasibility.** A2/A6/A3
need exact original 10,000-cluster-replicate
news-id and ticker bootstrap code/tests,
resample ranking/capacity and declare how
infeasible replicates are handled. Existing
draft requires reporting all and withholding
affected CIs unless a valid rule was
predeclared. No post-outcome exception.

**B-05: Explicit scope disposition.** A4
portfolio P&L/turnover/cost cannot be
presented as measured without a full
cash-flow/position/entry/exit ledger;
a second original ranker and independent
60-day holdout not yet supported. Their
NO-RUN paths must be accepted in final G2
reviewer traceability, with full limitation.

**B-06: Formal G2 graph freeze.** The
existing fail-closed
`ic_g2_freeze_preflight.py` still requires
22 complete editorial/reviewer trace links,
`all_g3_analyses_specified`, a real
`revision_protocol_freeze_commit`, pinned
G3 script hashes or justified nonexecution
and scientific signoff. The current reviewer
matrix has `all_g3_analyses_specified=false`
and `revision_protocol_freeze_commit=null`.
These must **not be filled speculatively**.

## Immediate author workflow

No further broad source-name/date scans. Preserve
all original source and report hashes. Complete
frozen G3 code + source-scoped numeric eligibility
policy, review/approve the precise conditional
A3 scope, then run the final fail-closed G2
preflight and independent adversarial scientific
review. Only then make a unique freeze commit and
authorize the exact G3 analysis permitted by
the reviewed design.

G5 manuscript and G6 response drafting can
proceed in parallel on **existing facts only**;
none of those drafts counts as completed
G3, G4 or final editorial submission.

**Current decision: NO-GO TO G3. G2 NOT FROZEN.**

## 2026-10-28 G2.16 superseding 40/60 decision and pure-code gate

The prior B-02 open 40-vs-60-return convention
has now been **decided at protocol level**:
A3 PRIMARY uses exactly 60 valid close-to-close
daily returns from the 61 most recent saved
bar dates strictly before event date, no
40-return fallback, no filling, winsorization
or post-event price input. A3 common-sample
complete-case effect is **secondary** and
not the original full-cohort result.
Provider price-source vintage and corporate
action adjustments remain unverified.

Created `ic_g2_g3_exploratory_core.py`
and 21 synthetic tests, plus
`G2_16_EXPLORATORY_SCOPE_CANDIDATE.json`,
`ic_g2_16_scientific_freeze_preflight.py`,
and `G2_16_SYNTHETIC_FREEZE_RUNBOOK.md`.
The status of these executable synthetic
tests is **NOT YET OPERATOR EXECUTED**;
GitHub source static review alone is
not a PASS.

Original G1.2 reconstructed booster object
identity remains UNAPPROVED until per-row
source/model parity. The conditional first
G3 stage is `G3.0` model/signal parity
**without forward targets**. Only after
actual G2 full freeze and successful
G3.0 can G3.1 A2/A3/A6 explore original
outcome-consumed cohorts.

No original G2 V2/V3/V4 result, original
model/threshold nor negative bootstrap
evidence was altered. G3 financial
scoring remains BLOCKED.
