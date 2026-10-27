# G2.8 — Conventional-risk comparator (A3) source availability gate

Date: 2026-10-27 · ICOMPUTING-D-26-01069
Reviewer: R1-04 (additional volatility- or downside-based benchmark).
Graph: G0 closed → G1 closed with limitation → G2 ACTIVE, UNFROZEN → G3 BLOCKED.

## Starting from actual G2.7 operator PASS

The operator executed G2.7 and obtained
`G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN`.

- Eight original source artifact hashes referenced.
- A2 weighted validation percentile grid `[0.15,0.25,0.35]`
  fixed for all three original V2/V3/V4 old cohorts,
  i.e. 9 post-outcome exploratory cells.
- G2.6 operator source binding SHA256:
  `1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`.
- A2 draft protocol SHA256 (operator local copy):
  `5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8`.
- G2.5 original filename/SHA-only inventory SHA256:
  `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.
- Report stored at
  `~/dtrm-ic-audit/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json`.
  The operator did NOT report this report's own SHA256.
- No alternative thresholds, historical outcomes, market
  prices, newly observed event cohort or model execution inspected.

## Scientific A3 question and fair comparison requirements

Can a **conventional, original point-in-time** stock
trailing-volatility veto produce comparable or better
decision value than the frozen P10 veto when combined
with the **same** ex-ante XGBoost ranking and capacity?

This is **not** a test of trading profitability and
not an independent new temporal efficacy result.
V2/V3/V4 outcomes have already been seen.

Preliminary fixed comparator *concept* (NOT YET FULLY PREREGISTERED):
- Keep original frozen ranker, stable ties and eligible
  ticker/news universe for the main comparison.
- Volatility = sample standard deviation of daily
  historical stock returns over the preceding 60
  trading observations, all dated **strictly before**
  the original news event/as-of timestamp.
- Require at least 40 valid prior return observations
  or predeclare an ineligible row. Exact price
  adjustment / provider, holidays and daily-close
  cutoff need source verification.
- Risk rule rejects highest volatility stocks;
  set its cut point on the **original validation
  population only**, preferably matching the original
  P25 validation pass capacity. Never fit on V2/V3/V4
  outcomes or use a price from after event time.
- Compare the original P10 veto and this conventional
  filter on the same predeclared complete-case universe,
  same baseline ranking, exactly the same K and
  same full-K/infeasibility conditions.
- Freeze any secondary common-coverage sample size,
  threshold and volatility lookback before outcome reads.
  Do not pretend reduced coverage equals original
  V2/V3/V4 full-cohort performance.
- Report admission, fill, old excess-beta effects
  and news/ticker cluster uncertainty. Report loss
  of coverage and unfavorable or infeasible results.
- Historical original P10 results must not be altered;
  only supplementary post-outcome exploratory effects
  may be discussed.

**Important:** The original `price_on_or_after` used
for 60-day target construction and the original
`price_on_or_before` used in historical alignment are
methods, NOT themselves original as-of-dated daily price
datasets. The presence of targets, event-time beta
values or a historical price filename is insufficient.

## G2.8 operator metadata-only triage

The new script `ic_g2_a3_price_source_triage.py`:
- Reads only JSON reports from G2.5, G2.6, G2.7 and
  the original frozen `.py` source for price/return
  alignment.
- Checks original report SHA fingerprints, pinned Git
  HEAD, clean original tracked worktree and G3 blocked.
- Classifies **filenames only** from 92 existing
  G2.5 SHA-recorded sources. It excludes files
  mentioning `holdout`, `target`, `forward`,
  `evaluation`, etc. from price-source eligibility.
- Does not deserialize scientific files, inspect a
  stock price, compute risk, open future return
  labels or run model inference.
- Its classification is a bounded search, not proof
  of archive completeness: price files with generic
  names may be missed.

Run **from `~/Desktop/DTRM_Lab`**:

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_a3_price_source_triage.py" \
  -o "$AUDIT/ic_g2_a3_price_source_triage.py"

python3 -m py_compile "$AUDIT/ic_g2_a3_price_source_triage.py"

python3 "$AUDIT/ic_g2_a3_price_source_triage.py" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-7-preflight "$AUDIT/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json" \
  --g2-7-plan "$AUDIT/G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --out "$AUDIT/g1-reconstruction/IC_G2_8_A3_price_source_triage.json"
```

The expected result depends on actual catalog filenames:

- `G2_8_A3_POTENTIAL_SOURCE_NAMES_FOUND_PRICE_VALUES_UNREAD`:
  some original research file names plausibly indicate
  prices/risk observations, but content and point-in-time
  coverage are **UNVERIFIED**. Next step: a separately
  audited, trusted historical **schema-and-date-only**
  feasibility investigation, not performance evaluation.
- `G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY`:
  no credible candidate filename from the scanned
  catalog. Does NOT rule out generically named archives
  or connected-provider data; do not invent synthetic
  volatility series or claim conventional benchmark PASS.

Neither state authorizes G3. G2 can still close with
A3 `NOT_EXECUTABLE` when authentic source coverage
cannot be established, with a transparent reviewer response
and separate planned post-revision acquisition.

## Remaining G2 closure conditions

A2: source/method gate PASS, **G3 old-outcome analysis not executed**.
A3: as-of risk dataset not yet demonstrated.
A4: flat option and economic limitations must distinguish
forward excess-beta from realizable trade P&L; if no
execution ledger, not executable as observed P&L.
A5: independent second-ranker source still conditional.
A6: predefine K sensitivity or clearly justify original
10% as arbitrary equal comparison capacity.
A7: verify and incorporate literature.
X1: independent non-overlapping 60-day outcome still
unavailable for the deadline.

**G2.8 file-name feasibility NOT YET OPERATOR-RUN. G3 BLOCKED.**
