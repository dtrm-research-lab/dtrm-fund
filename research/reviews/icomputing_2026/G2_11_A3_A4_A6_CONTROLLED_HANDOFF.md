# G2.11 — Controlled A3/A4/A6 design handoff and gate-readiness status

Case: ICOMPUTING-D-26-01069 · Decision letter: 2026-10-26
Editor deadline: 2026-11-25 · Branch: research/ic-major-revision-2026
State: G0 HISTORIC CLOSED → G1 CLOSED WITH LIMITATION → G2 ACTIVE, UNFROZEN → G3 BLOCKED.

## G2.10 corrected local OPERATOR PASS (not merely prepared)

The operator ran `test_ic_g2_10_schema_dates_regression.py`
with **5/5 PASS**, followed by corrected
`ic_g2_a3_original_price_schema_dates.py`
with exact status:

`G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`.

The original `*_2026-07-05.pkl` source frames:
- **174/174** original frames have DATE_STRUCTURE_OK with
  declared `date` and `close` column names.
- **173 stock tickers + SPY**.
- **174/174** have >=61 strictly prior dated closes (60
  daily trailing returns) before each *first* original
  cohort event date, V4 2026-05-02, V2 2026-06-07,
  V3 2026-06-11.
- Trusted original Pickles were deserialized with
  explicit operator opt-in, but close values were
  not accessed as a calculation and no returns,
  volatility, targets, P&L or models were computed.
- The earlier 3-constant Python NameError
  was repaired, not a scientific sample failure.
- Local generated report:
  `~/dtrm-ic-audit/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json`.
  The report's own SHA256 is still **UNKNOWN** in
  the GitHub audit and must be supplied by operator
  before the next source-binding/freeze checkpoint.

**Critical limitation:** Snapshot suffix July 5 is later
than May/June events. Retrospective bar dates earlier
than events and 60 available closes **do not prove**
point-in-time vendor ingestion/price adjustments
or historical strategy execution conditions.
Also, first-event date coverage is not proof of
date/stock completeness for every signal or
original V0 validation population.

## Current proposed dispositions for reviewer points

| Package | Reviewer | G2 state | Safe G3 execution gate |
| --- | --- | --- | --- |
| A1 original uncertainty, overlap, human claims | R1-02, R1-06; R2-01, 03, 04, 07 | **Existing sealed historic evidence** | Reuse 2026 frozen summary; no rerun needed |
| A2 fixed P10 validation percentiles q15/q25/q35 | R1-03; R2-02 | **SOURCE+METHOD METADATA PASS at G2.7** | Freeze final per-source hashes and all 9 exploratory cohort cells, then execute only authorized steps |
| A3 conventional volatility benchmark | R1-04 | **G2.10 date coverage PASS; provider vintage OPEN; G2.11 draft** | All per-news-event pre-event close quality & mapping, original validation common source, adjusted-price/vintage caveat, one frozen cutoff and common K; then retrospective only |
| A4 negative excess-beta, flat arm, economic costs, realized returns | R1-05; R2-05 | **Interpretive specification draft; hypothetical execution NOT proven** | Separate excess-beta from absolute gross returns, flat cash and overlap-aware portfolio/cost accounting; otherwise transparently NOT_ESTIMABLE |
| A5 second original ranking model | R1-07 | **Original prior model not demonstrated** | Original pre-outcome ranker artifact or explicit non-executable/model-agnostic limitation |
| A6 K=10% rationale and sensitivity | R2-06 | **Draft qK=5/10/15% preanalysis** | Exact full-K, original ranker/veto, no best-K retune, report all 9 old-outcome cells; secondary exploratory |
| A7 finance AI literature | R2-08 | **Four publisher-verified citations** | G5 add accurate references and distinguish selective prediction vs causal human treatment |
| X1 independent later nonoverlapping 60d holdout | R1-01; R2-03 | **NOT EXECUTABLE IN CURRENT REVISION** | Future genuinely new prospective news captures; never invent September/October outcome |

**No financial A2/A3/A4/A6 analyses were executed as part
of G2.10 or G2.11.** Old V2/V3/V4 target outcomes
are consumed and future analyses are post-outcome
exploratory by definition.

## New machine-readable preanalysis descriptions

- `G2_11_A3_VOLATILITY_BENCHMARK_DRAFT.json`:
  original frozen ranker, conventional standard deviation
  (ddof=1) over 60 strictly prior trading daily returns
  (minimum 40) with **no event-day quote**; veto
  cutoff based solely on validation-only volatility
  and its original P10 validation admission fraction,
  original per-news weights. Common frozen eligible
  pair universe / K, full-K infeasibility and original
  clusters/seed settings. **Draft only** and no
  as-of vintage proof.
- `G2_11_A4_A6_ECONOMIC_CAPACITY_DRAFT.json`:
  negative mean `forward_excess_beta` != realized
  trading P&L; simple zero-yield cash flat must be
  compared against **absolute gross stock return**
  if calculated and not by subtracting cash from
  excess beta. Event-level gross return is not a
  self-financing capital-weighted strategy. Real
  turnover/cost/portfolio P&L cannot be claimed
  without event overlap and ticker position handling.
  Top-K grid fixed at 5/10/15% as post-outcome
  exploratory with original 10% anchor. All
  cells and infeasibility must be reported.

No validation risk cutoffs, ticker source date
quality tests, gross economic outcomes or
Top-K effects have been computed yet.

## Single next operator step — hash the executed G2.9/G2.10 local evidence

From any shell directory:

```bash
AUDIT="$HOME/dtrm-ic-audit"
shasum -a 256 \
  "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json"
```

Only SHA-256 metadata values are sent back to
research branch documentation; do not upload
original FMP price Pickles to GitHub.

The next work before G2 closes is source-binding
the complete original validation/evaluation event
date/ticker pairs to the same frozen price-cache
manifest, and explicit A3 price-vintage/adjustment
limitations. This must be an **outcome-blind
feasibility/coverage audit**; no risk or results
until final frozen G2 signoff.

## G2 exit and G3 authorizations

G2 can close with explicit `NOT_EXECUTABLE`
components, honest limitations and complete
registered exploratory analysis specs; it cannot
treat structural date coverage as original
point-in-time external vendor authentication.

The reviewer response will acknowledge the
important missing independent holdout and
lack of broad ticker/temporal robustness (ticker
cluster intervals include zero for V2 & V4);
none of these can be erased by a new post-hoc
volatile-price comparator.

**Stage: G2 ACTIVE; G3 BLOCKED; A3 source/date
STRUCTURAL PASS, as-of/adjustment/provenance OPEN.**
