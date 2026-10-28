# G3.0 PASS → G3.1 bounded exploratory launch decision

**Manuscript** ICOMPUTING-D-26-01069 · **Operator event** 2026-10-28.
**State:** G2 scientifically frozen; G3.0 PASS; G3.1 OLD OUTCOME ACCESS STILL BLOCKED.
**Original immutable G2 freeze commit:** `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`.

## G3.0 independently qualified success

Operator pasted the following console output from a local
SHA-gated `ic_g3_0_original_model_row_parity.py` run:

```
G3.0: G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED
V2 ROW_PARITY_PASS ranker mismatches 0 veto mask disagreements 0
V3 ROW_PARITY_PASS ranker mismatches 0 veto mask disagreements 0
No old forward-target/outcome values opened; G3.1 still BLOCKED.
```

V2 4,449 rows + V3 2,827 rows = **7,276 old source
model rows**. Both passed original baseline XGBoost ranker
numerical prediction, original calibrated P10 veto-mask
agreement. The approved G3.0 runner only emits unqualified
`ROW_PARITY_PASS` if the original saved source contains
an explicitly named `p10_raw` or `p10_calibrated`
numeric reference, with no > 1e-6 row mismatches
for each reference it actually observed. This
conclusion follows from the frozen runner's code; **it
does not independently authenticate a pre-outcome
serialized version of the model**, or that an
earlier saved source is a genuine contemporaneous
market vendor data vintage.

Original G3.0 local result:
`$HOME/dtrm-ic-audit/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json`.
The operator has **not yet supplied SHA256 of this
generated report**; do not falsely state it is
bound cryptographically by the repository.

## Finite source-only binding task: one local command

```bash
AUDIT="$HOME/dtrm-ic-audit"
REPORT="$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json"
shasum -a 256 "$REPORT"
python3 - "$REPORT" <<'PY'
import json,sys
with open(sys.argv[1],encoding="utf-8") as f:
    data=json.load(f)
print("G3.0 status:", data["status"])
for cohort in ("V2","V3"):
    r=data["cohorts"][cohort]
    print(cohort, "rows:",r["rows"],
          "numeric_P10_references:",sorted(r["original_p10_numeric_reference"].keys()),
          "reference_mismatch_counts:",
          {k:v["nonfinite_or_mismatched_rows"]
           for k,v in r["original_p10_numeric_reference"].items()},
          "ranker_mismatch_count:",r["ranker_rows_exceeding_1e_6"],
          "P10_veto_mismatches:",r["original_p10_veto_mask_disagreements"])
print("G3.1 old target access authorized:",
      data["g3_1_financial_comparison_authorized"])
PY
```

Only a SHA256 digest and aggregate counts/column names
are shared. No private news IDs, prices or old financial
target values leave the local machine.

## Scope of separately reviewed G3.1 analysis (no run yet)

**Stage A — A2 q15/q25/q35 + A6 K=5/10/15%**.
These can reuse the original already consumed
V2 (4,449), V3 (2,827), V4 (40,320) signal and
preexisting 60-day `forward_excess_beta` outcome
targets, but they must NOT open outcome labels
until all these conditions have been met:
- Canonical G2 frozen A2/A6 plan, original V0 validation
  q25 weighted threshold, old model ranks and P10 masks
  exact original q25/K10 parity preserved; original
  V4 row lineage from G1 already documented.
- New read-only source adapter and tests, exact original
  SHA-bound target files and row-ID/date/ticker
  alignment. No joining by order alone without a
  documented source identity check.
- Original V0 validation P10 weighted thresholds
  q15/q25/q35 strictly calibration-only, not tuned on
  old V2/V3/V4 outcomes.
- 18 cells **in total** (nine A2 and nine A6),
  including negative/infeasible cells, same fixed
  Top-K rule and both clustering methods.
- No best-performing threshold/K promotion;
  post-outcome exploratory interpretation only.
- An explicit, separate operator-approved bounded
  `G3_1_A2_A6_POST_OUTCOME_EXPLORATORY` authorization
  bound to exact code and G3.0 source-report digest.
  G3.0/earlier G2 operator approvals do NOT confer it.

**Stage B — A3 conventional historical volatility
comparison**. Its original provider-vintage and
adjusted-closing price state is UNVERIFIED because
the July-5 historical archive was saved after
May/June decisions. Before source values are used,
freeze exact 60 prior daily returns (61 positive
finite pre-event closes), common-eligible universe
for all three arms, no 40-return fallback, and
V0 validation-only volatility veto admission cutoff.
If a trustworthy historical *as-of* interpretation
cannot be established, the narrow allowable claim
is a **retrospective dated-bar volatility
exploration**, not ex-ante tradable superiority.
This stage requires its own authorization and
source adapter test PASS.

The original V2/V4 ticker-cluster 95% intervals
include zero; V2 and V3 forward targets overlap.
The original excess-beta target is not tradable
P&L. A4 realized cash/turnover/cost ledger, A5
second independent original model and X1
nonoverlapping matured prospective holdout
remain NOT EXECUTABLE with currently verified
historic source scope.

**NO G3.1 financial experiments have been run
in preparing this handoff.**
