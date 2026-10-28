# G3.1 A2/A6 — Source-only gate, NO old outcome access

Case: ICOMPUTING-D-26-01069
Date: 2026-10-28
State: G2 frozen; G3.0 original V2/V3 model-row parity **PASS**;
**G3.1 NOT AUTHORIZED**.

## Proven original model result, exact operator digest

Original local G3.0 output:
`G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED`.
V2 original 4,449 and V3 original 2,827 rows have
**zero** baseline-ranker numerical mismatches and
**zero** original P10 veto-mask disagreements.
Both old signals expose real numeric P10 fields
`p10_raw` and `p10_calibrated`; the original
G3.0 program only produces `ROW_PARITY_PASS`
when all available numeric comparisons also pass
at 1e-6 absolute threshold. Exact original
report SHA256 supplied by operator:

`a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a`.

Frozen G2 science commit:
`3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`.
Operator G2 source/synthetic gate SHA256:
`5232f42bd84e8b9a16d32d906b638bfd9f0f4a35234fa8440bc1f708d32f2946`.
The G2.17 original operator attestation remains
local; its own SHA can be computed, but this
gate reads it only to confirm source ancestry,
full G2 authorization for G3.0 and **G3.1 denial**.

## Exact original PhaseII target mapping — source evidence

Read from original `research/experiments/run_phase2_primary_bootstrap.py`
at frozen original code commit
`c7502a690162459cdfb3413573e3133c42efb126`:

| Cohort | Original signal filename | Original target filename | Rows |
| --- | --- | --- | ---: |
| V2 | `probabilistic_v2_holdout_signals_2026-06-10.pkl` | `probabilistic_v2_holdout_model_targets_2026-06-10.pkl` | 4,449 |
| V3 | `probabilistic_v3_holdout_signals_2026-06-14.pkl` | `probabilistic_v3_holdout_model_targets_2026-06-14.pkl` | 2,827 |
| V4 | `probabilistic_v4_holdout_signals_2026-06-06.pkl` | **`probabilistic_v1_holdout_model_targets_2026-06-06.pkl`** | 40,320 |

This V4/V1 historical linkage is critical:
V4 signals use original V1 model target rows
(identical news/ticker/date cohort), NOT an
invented new V4 target. This source-only step
does NOT read any target values or declare
their original source vintage authenticated.

Original PhaseII `load_cohort` joins original
signal and target pairs on
`news_id,ticker` with `validate=one_to_one`
and exact `date_dt` agreement, before
allowing evaluation. The future G3.1
read-only adapter must enforce **the same
key and date semantics**, validate numeric
finite `target_model` and original
q25/K10 reproductions, and refuse partial
cohort joins. Those checks are **not done**
by this preliminary metadata-only gate.

## Current new code, tests and intended result

- `ic_g3_1_a2_a6_source_gate.py`: source-only SHA
  preflight. It checks exact G2.5 historical
  source inventory SHA, G2.6 source binding,
  G2.16 operator PASS, G2.17 freeze approval,
  G3.0 report SHA and numeric P10 row parity.
  It then checks original six cohort signal
  and target file names, sizes, and SHA256
  against previously recorded **G2.5 original
  local metadata inventory**, and crosschecks
  all three signal digests against G2.6.
  Its output only describes source readiness;
  no Pickles are deserialized or financial
  arrays opened.
- `test_ic_g3_1_a2_a6_source_gate.py`:
  seven pure static protection tests
  (source compile, no pickle use, preserved
  historical V4/V1 lineage, SHA binding,
  old row-key join expectation and G3.1 lock).

If every original file matches the G2.5
SHA inventory, expect
`G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED`.
If any source lacks a SHA or mismatches,
expect `G3_1_A2_A6_SOURCE_SHA_OR_LINEAGE_GAPS_OUTCOMES_STILL_BLOCKED`
(exit 2) or a fail-closed `HALTED` message
if a mandatory report/source is absent.
Do not retroactively treat a new hash
as an old outcome-blind pre-commit.

## One Mac operator command: NO original financial data opened

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"

curl -fsSL "$BASE/ic_g3_1_a2_a6_source_gate.py" \
  -o "$AUDIT/ic_g3_1_a2_a6_source_gate.py"
curl -fsSL "$BASE/test_ic_g3_1_a2_a6_source_gate.py" \
  -o "$AUDIT/test_ic_g3_1_a2_a6_source_gate.py"

cd "$AUDIT"
python3 -m unittest test_ic_g3_1_a2_a6_source_gate.py -v
python3 "$AUDIT/ic_g3_1_a2_a6_source_gate.py" \
  --original-local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --g2-5-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-16-source-gate "$AUDIT/g1-reconstruction/IC_G2_17_latest_36_test_science_gate.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --out "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json"
BASH
```

**Important**: It reads file SHA256 *bytes* and
size only; no deserialization, no target_model
values, no P&L, no extra model predictions.
User should share only the aggregate status
lines and any fail-closed reason, not private
financial data. The output gate SHA will
be recorded before a separately requested
authorization of a final read-only
A2/A6 old outcome runner.

## What this gate cannot authorize

G3.1 A2/A6 still needs:
1. A genuinely reviewed, source-SHA-bound
   model-validation-only q15/q25/q35
   threshold reader and original old
   signal/target one-to-one join,
   not an invented validation prediction
   vector or silent outcome access.
2. Reproduction of exact original q25/K10
   V2/V3/V4 historic summary and
   complete original K before alternatives.
3. Complete fixed 18 retrospective
   exploratory cells (A2=9, A6=9),
   news/ticker clustered uncertainty,
   infeasible counts and original
   negative/stability limitations.
4. A new **explicit operator authorization**
   for precise G3.1 A2/A6 old outcome
   access tied to tested code and
   source gate SHA. Prior G2/G3.0 owner
   signoffs forbid that access.
5. A3 separately requires the prior-price
   numeric quality and source-vintage
   policy; no reuse of A2/A6 authorization
   for A3.

**NO NEW G3.1 FINANCIAL RESULTS COMPUTED.
A2/A6/A3 NOT AUTHORIZED.**
