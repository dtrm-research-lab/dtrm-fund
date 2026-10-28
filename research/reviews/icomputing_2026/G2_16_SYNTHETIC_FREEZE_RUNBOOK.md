# G2.16 — Finite scientific pre-freeze evidence gate, before G3

**Review:** ICOMPUTING-D-26-01069 · **Date:** 2026-10-28
**Editorial deadline:** 2026-11-25
**Graph:** G2 ACTIVE / G3 NOT YET AUTHORIZED

## Scope decisions now written as executable pure-method contracts

- **A3 PRIMARY:** Exactly **60** historical daily simple
  close-to-close returns from the **61 most recent
  unique bar dates STRICTLY before** each historical
  news event UTC calendar date. `ddof=1` sample
  standard deviation. A proposed fallback of
  **40 returns was REJECTED** for the primary
  comparison before any new price-value access.
  Invalid/non-numeric/null/nonpositive selected
  historical close => this pair excluded from
  **ALL three arms** for A3 common-case only.
  Never impute, use future/event-day close, winsorize,
  fill partial K or tune risk cutoff on old outcomes.
- **A3 validation cutoff:** Original validation-only
  frozen weighted P10 pass fraction and trailing
  volatility weighted empirical quantile on the
  exact **common-eligible validation subset**.
  Original news-id weights are recalculated
  within the common-eligible V0 subset, and
  the actual validation pass discrepancy caused
  by equal/tied risk values is reported.
- **A3 inference ceiling:** The July-5 price
  archive was saved AFTER original validation
  and test signal dates. Even with strictly
  earlier bar dates and complete date coverage,
  actual provider acquisition vintage,
  contemporary corporate-action adjustments,
  survivorship and market-tradability remain
  **UNVERIFIED**. The comparison can only
  be a transparently retrospective
  **POST_OUTCOME_EXPLORATORY** analysis.
- **A2:** Same original P10 model, original
  19,880-row V0 weighted validation
  quantiles q=0.15/0.25/0.35; original
  q25 must reproduce -0.16665692627429962.
  Nine historical test cells; no predictive
  P15/P25/P35 model retraining, no new
  best-percentile selection.
- **A6:** Original q25 veto, original score
  order `np.argsort(-baseline_prediction)`,
  fixed K fractions 5/10/15% (integer
  floor) with nine historical test
  cells, no advantageous post-hoc
  choice of K or fraction.
- **Uncertainty:** 10,000 news and 10,000
  ticker cluster bootstrap replicates,
  seeds 20260821/20260822, duplicated
  full cluster rows and full-K resampling.
  All infeasible replicates counted, their
  affected intervals withheld, no
  pooled significance test.
- **A4/A5/X1:** Economically realizable
  strategy P&L and cost/turnover,
  independent second historic ranker and
  a nonoverlapping matured 60d holdout
  remain unverified/not executable as
  experiments on original sources.
- **Original limitations:** V1 original zero-pass
  rule, negative selected mean excess-beta,
  original V2/V4 ticker-cluster CIs including
  zero and overlapping V2/V3 60-day targets
  must remain visible in rebuttal.

### Immutable scientific source anchors

Historical model source:
`c7502a690162459cdfb3413573e3133c42efb126`

Already operator-sealed local report SHA256:
- G2.9 `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`
- G2.10 `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`
- G2.12 `e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`
- G2.13 `e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`

The original G2.13 observation was 19,880/19,880
validation source pair-date coverage and the
original G2.12 observation was 47,596/47,596
V2/V3/V4 event pair-date coverage.
No numeric price values/results have
been calculated in G2.

### Current GitHub artifacts

- `G2_16_EXPLORATORY_SCOPE_CANDIDATE.json` —
  exact candidate G3.0 source-parity and
  G3.1 A2/A3/A6 exploratory execution policy,
  marked **NOT FROZEN**.
- `ic_g2_g3_exploratory_core.py` —
  pure NumPy implementations for original
  weighted validation quantiles, Top-K,
  10k cluster bootstrap, full-60
  historical trailing-volatility primitive,
  validation-only risk cutoff; **no I/O/CLI**.
- `test_ic_g2_g3_exploratory_core.py` —
  synthetic-only tests for source semantics,
  strict timing, invalid closes,
  full K and negative/bootstrap gates.
- `ic_g2_16_scientific_freeze_preflight.py` —
  fail-closed metadata and synthetic
  regression gate. Reads only JSON metadata
  and Python source; does not open
  actual quotes, targets or models.

**IMPORTANT:** Original G1.2K booster objects
remain **UNAPPROVED for G3 scoring** until
original row-by-row P10 and baseline-model
prediction/source parity has been independently
verified. G3.0 must pass this before A2/A3/A6
may use original consumed outcome targets.
Existing historical reconstruction 12/12
aggregate numeric checks are not a
substitute for 47,596 per-row historical
signal/P10 parity.

## One operator command: executable synthetic tests + 22-item traceability

The following reads only previously saved
small JSON reports and synthetic NumPy
test vectors. It does NOT deserialize
Pickles, inspect actual price values,
fit models, compute any new G3 result,
or overwrite prior source reports.

Run from the current original `$HOME/dtrm-ic-audit`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"

curl -fsSL "$BASE/G2_16_EXPLORATORY_SCOPE_CANDIDATE.json" -o "$AUDIT/G2_16_EXPLORATORY_SCOPE_CANDIDATE.json"
curl -fsSL "$BASE/G2_REVIEWER_TRACEABILITY_PROVISIONAL.json" -o "$AUDIT/G2_REVIEWER_TRACEABILITY_PROVISIONAL.json"
curl -fsSL "$BASE/ic_g2_g3_exploratory_core.py" -o "$AUDIT/ic_g2_g3_exploratory_core.py"
curl -fsSL "$BASE/test_ic_g2_g3_exploratory_core.py" -o "$AUDIT/test_ic_g2_g3_exploratory_core.py"
curl -fsSL "$BASE/ic_g2_16_scientific_freeze_preflight.py" -o "$AUDIT/ic_g2_16_scientific_freeze_preflight.py"

python3 -m py_compile "$AUDIT/ic_g2_g3_exploratory_core.py" "$AUDIT/test_ic_g2_g3_exploratory_core.py" "$AUDIT/ic_g2_16_scientific_freeze_preflight.py"

python3 "$AUDIT/ic_g2_16_scientific_freeze_preflight.py" \
  --spec "$AUDIT/G2_16_EXPLORATORY_SCOPE_CANDIDATE.json" \
  --engine "$AUDIT/ic_g2_g3_exploratory_core.py" \
  --tests "$AUDIT/test_ic_g2_g3_exploratory_core.py" \
  --reviewer-matrix "$AUDIT/G2_REVIEWER_TRACEABILITY_PROVISIONAL.json" \
  --g2-9 "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10 "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12 "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13 "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --out "$AUDIT/g1-reconstruction/IC_G2_16_synthetic_science_gate.json"
```

Expected if successful:
`G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING`.

This is **NOT** a G2 global freeze or permission to
open old financial targets. The next subgate is
**G3.0 original model/source numeric parity**,
not immediate G3.1 comparisons. If
parity fails, we stop and report limited
reproducibility rather than retune a model.

## Precise stop point and next action

G2 full scientific signoff requires:
1. Synthetic tests pass and source evidence
   hashes/checks are verified.
2. Reviewer map of 22 is complete; the
   old global G2 freeze checker cannot be
   marked passed by merely setting JSON
   fields without authentic source/code
   experiment parity and human approval.
3. Source-to-signal per-row original
   G3.0 parity harness is integrated and
   independently validated before
   any outcome/benchmark G3.1 analysis.
4. Only a signed immutable protocol commit
   may authorize specific G3 analyses.

**Until this is true, G3_1 is BLOCKED.**
