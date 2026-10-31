# G5.6 — Operator runbook: original TRAIN-only target-center reconstruction

**2026-10-29 · ICOMPUTING-D-26-01069 · SOURCE-ONLY CI PASS, PRIVATE TRAIN RUN NOT YET EXECUTED**

This runbook is *optional for the data owner when using their original Mac*. Its first section is read-only source SHA/metadata preflight. The second section **requires new explicit operator authorization**, decodes trusted original TRAIN/model/price Pickles, and never opens V2/V3/V4 *outcome* values. Neither stage is allowed to train a fresh ranker, retune P10, claim economic alpha or send raw observations to GitHub.

## Step 1 — Pin exact public source and verify archived local inputs, no financial-value access

```bash
set -euo pipefail
cd "$HOME/Desktop/DTRM_Lab/dtrm-fund"
git fetch origin
WT="$HOME/dtrm-ic-g56-worktree"
if [ -e "$WT" ]; then
  echo "Worktree already exists: inspect it manually, refuse overwrite" >&2
  exit 1
fi
git worktree add --detach "$WT" origin/research/ic-g5-3-information-parity-20261029
cd "$WT"
git status --short
python3 --version
CODE_COMMIT="$(git rev-parse HEAD)"
printf 'Reviewed G5.6 code commit: %s\n' "$CODE_COMMIT"

AUDIT="$HOME/dtrm-ic-audit"
TRAIN="$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data"
OUTS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs"
PRICES="$OUTS/price_cache_fmp_pickle"
G31="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json"
STAGE1="$AUDIT/g1-reconstruction/IC_G55_original_private_source_metadata_only.json"

PYTHONPATH=src python3 research/reviews/icomputing_2026/ic_g5_5_private_source_metadata_gate.py \
  --source-only-report "$G31" \
  --original-local-data "$TRAIN" \
  --legacy-outputs "$OUTS" \
  --original-price-cache "$PRICES" \
  --out "$STAGE1"

shasum -a 256 "$STAGE1"
```

**First-stage expected status:** `G55_ORIGINAL_LOCAL_SOURCE_HASHES_AND_TRAIN_INPUT_NAMES_PASS_NO_TARGET_VALUES`, six historical signal/target SHA identities and original TRAIN model-row SHA PASS. Do not continue on errors. Reuse an existing report only if it is independently inspected: the scripts refuse overwrites.

## Step 2 — Separate owner-approved TRAIN-only numerical reconstruction

**Run this part only if the operator has reviewed the code/permissions and voluntarily authorizes trusted local Pickle deserialization.** The original 174 archived price files are hashed before any is unpickled; their acquisition-time source vintage and corporate action adjustment history are **not certified**. The full legacy row archive still has no independently attested original historical SHA in this chain; reconstruction is explicitly conditional.

```bash
set -euo pipefail
cd "$HOME/dtrm-ic-g56-worktree"
CODE_COMMIT="$(git rev-parse HEAD)"
AUDIT="$HOME/dtrm-ic-audit"
TRAIN="$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data"
OUTS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs"
PRICES="$OUTS/price_cache_fmp_pickle"
G31="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json"
STAGE1="$AUDIT/g1-reconstruction/IC_G55_original_private_source_metadata_only.json"
STAGE1_SHA="$(shasum -a 256 "$STAGE1" | awk '{print $1}')"
REPORT="$AUDIT/g1-reconstruction/IC_G56_original_train_centers_hash_only.json"

PYTHONPATH=src python3 research/reviews/icomputing_2026/ic_g5_6_train_only_protected_runner.py \
  --repo "$PWD" \
  --approved-code-commit "$CODE_COMMIT" \
  --original-local-data "$TRAIN" \
  --legacy-outputs "$OUTS" \
  --original-price-cache "$PRICES" \
  --g31-source-only-report "$G31" \
  --g55-metadata-report "$STAGE1" \
  --g55-metadata-sha256 "$STAGE1_SHA" \
  --g2-6-report "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12-report "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13-report "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --out "$REPORT" \
  --authorize-train-only-numeric-reconstruction \
  --trust-original-audited-pickles \
  --acknowledge-price-vendor-vintage-unverified \
  --acknowledge-original-full-row-provenance-unbound \
  --acknowledge-no-old-holdout-outcomes

shasum -a 256 "$REPORT"
```

**Expected successful but QUALIFIED status:** `G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED`. Report contains only train sample N, number of training tickers, original clipping bounds, ordered-hash commitments of float32 ticker centers, original model train-label hash, audited source hashes and explicit limitations. No raw returns, individual ticker means or news IDs written. Hash commitments need not be publicly shared.

The runner checks original local Python code against the exact reviewed `--approved-code-commit`, verifies the original source-code Git blob SHA and historical reports, original six saved cohort files SHA **without unpickling**, all 174 historical price SHA values **before** decoding original TRAIN and price sources, then generates original `forward_excess_beta_target` only for the original ordered TRAIN split. Uses original `train_only_clip_bounds` and Kahan float32 means and refuses a parity mismatch.

## Decision after stage 2

- If successful: record **TRAIN centering reconstruction feasible but full-row historical provenance not yet independently attested**, and proceed to a separately designed G5.7 old-cohort attribution authorization. The G5.6 output is **not** evidence of a historical policy improvement.
- If blocked: preserve exact error type and source names only, do not repair by substituting current quotes or by recomputing centers from V2–V4 labels.
- If the operator wishes to release only a safe progress summary, communicate the status and report SHA (not raw path/data) and the unresolved full row source provenance.
- G5.7 must separately prove source definition compatibility for V2/V3/V4 stored transformed labels. An original V0 centering reconstruction is not proof every later cohort used that same origin.
- Scientific review score remains fixed until actual original outcome contrasts survive independent review; a 54/54 CI PASS is **engineering**, not additional financial evidence.

## Platform and trust notes

- Original `*.pkl` are executable upon deserialization and must be considered trusted only after independent source review; never run arbitrary downloads, unverified external archives or code from an unreviewed branch with these flags.
- `git worktree` and original cache paths may differ locally; do not guess replacements, especially for original 2026-07-05 prices.
- No automation created; the owner controls the local execution.
- Original G2.9/G2.10/G2.12/G2.13/G2.6 SHA requirements remain unmodified. Original quote-vintage issues are disclosed, not cured.
- This report has no independent heldout 60-day cohort, no realized economic P&L and no human authority experiment.
