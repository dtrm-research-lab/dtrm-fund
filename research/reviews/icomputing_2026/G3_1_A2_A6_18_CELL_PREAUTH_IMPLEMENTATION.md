# G3.1 A2/A6 — original source integrity PASS; 18-cell pure-code implementation prepared

**Case:** ICOMPUTING-D-26-01069
**Date:** 2026-10-28.
**Research status:** G2 FROZEN; G3.0 7,276-row V2/V3 numerical P10 and ranker parity PASS; G3.1 original historical financial outcome access STILL BLOCKED.

## Original six-file source integrity — OPERATOR PASS

Seven static protections **7/7 PASS** on Mac and original
`G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED`.

Original SHA-bound, size-checked G2.5 manifest source files:
- V2, 4,449 original signals and original model targets: **BOTH SHA PASS**.
- V3, 2,827 original signals and original model targets: **BOTH SHA PASS**.
- V4, 40,320 original V4 signals and **ORIGINAL V1 model targets**: **BOTH SHA PASS**.
- Total **47,596** original pairs, **six** separate files.
- No target Pickle deserialization, financial outcome
  calculation or new model predictions performed.
- Original result location:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json`.
- Original result JSON SHA256 **NOT YET USER-SUPPLIED**.

## Newly prepared implementation — NOT yet executed

Three modular source components:

### 1. Original 19,880 VALID rows (A2)

`ic_g3_1_a2_validation_only_source.py`

- Explicit `split="valid"`, **19,880** original
  validation pairs dated 2025-12-24 through 2026-01-21.
- Source `legacy_model_rows_2026-05-01.pkl`
  with originally observed retrospective SHA256
  `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
- Reuses pinned exact historical
  `run_probabilistic_xgb_v0.py` from
  `c7502a690162459cdfb3413573e3133c42efb126`.
- Builds the original **390** features and
  obtains raw original P10 validation
  predictions using exact reconstructed,
  SHA-bound candidate P10 booster,
  original iteration range `(0,19)`.
- Applies frozen P10 calibration offset
  `-0.06494169682264328`.
- Calculates ONLY validation-weighted
  q15, q25, q35 original calibrated P10
  cutoff values, with original `news_id`
  sample weights.
- Fails unless old q25 reproduces
  `-0.16665692627429962`.
- Does NOT calculate forward historical
  returns, read original holdout targets
  or save sensitive per-news vectors.
- Source feature model still has retrospectively
  reconstructed, not original saved, booster
  and source-vintage limitations.
- This function is **not yet authorized
  to run or independently tested against
  original source files**.

### 2. Original row-level signal↔target join

`ic_g3_1_a2_a6_join_contract.py`

- Original Phase II pairing on unique
  `(news_id,ticker)` with `validate="one_to_one"`.
- Exact `date_dt` UTC agreement.
- No missing keys, duplicate pairs,
  partial join, row count drift or
  sorting by index alone.
- Strict Boolean stored q25 P10 mask,
  exact numerical consistency of
  `p10_calibrated ≈ p10_raw + offset`
  and original q25 cutoff.
- Requires finite baseline scores and
  original `target_model` labels;
  **this function must only receive
  target DataFrames after separate,
  explicit G3.1 scientific approval**.
- No file I/O on import or function call;
  only in-memory DataFrames passed by
  a separately authorized future reader.

### 3. All 18 original sensitivity cells, fixed

`ic_g3_1_a2_a6_pure_grid.py`

- Exactly **nine A2** fixed weighted
  threshold-veto cells: 3 validation
  q15/q25/q35 × 3 original V2/V3/V4 cohorts.
- Exactly **nine A6** fixed capacity
  cells: 3 K fractions 5/10/15% × 3 cohorts.
- Before any alternate cutoff/capacity:
  exact original q25/K10 reproduced to
  original published cohort difference
  and hit-rate precision, or fail closed.
- Both original news-id and ticker
  10k cluster bootstrap replicates,
  recompute K per draw; failures counted
  and CIs withheld if any infeasible.
- All negative, null and infeasible cells
  visible; no optimizing q/K on outcomes.
- `forward_excess_beta` outcome is **not
  tradeable portfolio P&L**.
- All old outcomes already consumed:
  strictly **POST_OUTCOME_EXPLORATORY**.
- No file I/O or automatic execution.

## One operator command — PURE SYNTHETIC and original source report SHA

This command neither loads original target files
nor re-runs models; it tests the newly prepared
method on generated fake arrays. The fake
arrays intentionally use original cohort sizes and
published summary numbers as validation fixtures,
NOT original private per-event returns.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026"
for f in \
 ic_g3_1_a2_a6_join_contract.py \
 test_ic_g3_1_a2_a6_join_contract.py \
 ic_g3_1_a2_a6_pure_grid.py \
 test_ic_g3_1_a2_a6_pure_grid.py \
 ic_g3_1_a2_validation_only_source.py \
 test_ic_g3_1_a2_validation_only_source.py
do
  curl -fsSL "$BASE/$f" -o "$AUDIT/$f"
done
cd "$AUDIT"
python3 -m unittest \
  test_ic_g3_1_a2_a6_join_contract.py \
  test_ic_g3_1_a2_a6_pure_grid.py \
  test_ic_g3_1_a2_validation_only_source.py \
  -v
shasum -a 256 "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json"
BASH
```

**Expected if all current source tests succeed:**
15 keyed/date synthetic joins + 8 synthetic
18-cell grid tests + 5 static original V0-only
feature source tests = **28 checks PASS**.

If they fail, preserve the exact error and do
not proceed or promote G3.1. No extra full
source inventory should be repeated.

## What is next — a single real release decision, not new inventories

After source-only PASS, 28 synthetic source tests PASS
and original source-gate report SHA, produce and
review one complete **G3.1 A2/A6 outcome reader
and release protocol**:
- Requires exact immutable commit and
  explicit operator scientific authorization
  for **A2/A6 only**;
- Reads only trusted original SHA-verified
  V2/V3/V4 saved Phase II model targets,
  with one-to-one date/ticker/news keys;
- Recreates the original V0 validation
  q15/q25/q35 without V2/V3/V4 labels;
- Reproduces original q25/K10 3-cohort
  point estimates before sensitivity
  calculations;
- Executes the 18 specified old-cohort
  exploratory cells and both 10k
  cluster-bootstrap sets;
- Never silently changes P10 cutoff,
  K, model, source, test population,
  or missing-value policy based on known outcomes;
- Never authorizes A3 source-price
  analysis through an A2/A6 approval.

**DO NOT RUN G3.1 ON OLD FINANCIAL OUTCOMES
UNTIL THE SEPARATE G3.1 APPROVAL PASSES.**
