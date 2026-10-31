# G5.7d — One and only one excluded Notebook: source-only operator runbook

Date: 2026-10-29; Intelligent Computing case ICOMPUTING-D-26-01069.
Original G5.7c: status NO PRODUCER FOUND IN BOUNDED NOTEBOOKS, 14 scanned and one >16MB skipped; original report SHA256 `e9b45fda73c8668caa5ae983cfa9dc542a084f8618055cff791c4a5ad82dab8f`. One skipped notebook remains unknown; no claim of completed source discovery. Original old V2/V3/V4 target values unopened.

**Source-only CI:** [GitHub Actions 40868278129](https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40868278129) ran **104/104 tests PASS** against frozen public source revision `0634ed6a3a40931b4423ea9b665689286fbe074c`, including nine fake one-excluded-file tests. No private notebook/outcome values were used in CI.

## STEP 1, metadata-only, no notebook JSON code inspection

```bash
bash <<'BASH'
set -euo pipefail
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
WT="$HOME/dtrm-ic-g57d-one-notebook"
PIN="0634ed6a3a40931b4423ea9b665689286fbe074c"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
PREVIOUS="$AUDIT/IC_G57C_ORIGINAL_NOTEBOOK_CODE_PRODUCER_SOURCE.json"
META="$AUDIT/IC_G57D_ONE_OMITTED_NOTEBOOK_METADATA_ONLY.json"
ORIGINAL_NOTEBOOKS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks"
EXPECTED="e9b45fda73c8668caa5ae983cfa9dc542a084f8618055cff791c4a5ad82dab8f"
cd "$REPO"
git fetch origin research/ic-g5-3-information-parity-20261029
test ! -e "$WT"
git worktree add --detach "$WT" "$PIN"
cd "$WT"
test "$(git rev-parse HEAD)" = "$PIN"
test -z "$(git status --porcelain)"
test ! -e "$META"
test "$(shasum -a 256 "$PREVIOUS" | awk '{print $1}')" = "$EXPECTED"

PYTHONPATH=src python3 \
 research/reviews/icomputing_2026/ic_g5_7d_one_omitted_notebook_gate.py \
 --original-g57c-report "$PREVIOUS" \
 --original-notebooks-root "$ORIGINAL_NOTEBOOKS" \
 --out "$META"

shasum -a 256 "$META"
BASH
```

The process does SHA256 streaming on the 14 already scanned notebooks, verifies the original 15-file scope/14 SHA matches, then hashes **only** the current skipped notebook bytes without parsing any code cells or outputs. Does not access original financial Pickles, price archives or cohort outcomes.

Possible statuses:
- `G57D_ONE_OMITTED_NOTEBOOK_PINNED_AND_CODE_READ_CAPABLE` — original source inventory intact, skipped notebook current SHA/size pinned, <=128MB; operator can **separately approve** STEP 2.
- `G57D_ONE_OMITTED_NOTEBOOK_TOO_LARGE_FINITE_SOURCE_STOP` — >128MB, **NO code inspection permitted in this experiment**, stop and report unresolved historical provenance.
- Any integrity fail — stop. No replacement, no source-boundary widening.

## STEP 2, OPTIONAL and DISTINCT owner approval for excluded code cells ONLY

**Do not perform automatically**. Requires inspection of STEP 1 evidence and owner's separate affirmative choice to inspect this one notebook source. The original G5.7c reader streams JSON and skips `outputs` without decoding or emitting output content; source code is transiently AST-parsed, never executed. The notebook bytes must be read and hashed; the skipped notebook is **not** pre-June historically authenticated by its current SHA or filename.

```bash
bash <<'BASH'
set -euo pipefail
WT="$HOME/dtrm-ic-g57d-one-notebook"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
PREVIOUS="$AUDIT/IC_G57C_ORIGINAL_NOTEBOOK_CODE_PRODUCER_SOURCE.json"
META="$AUDIT/IC_G57D_ONE_OMITTED_NOTEBOOK_METADATA_ONLY.json"
CODE_REPORT="$AUDIT/IC_G57D_ONE_OMITTED_NOTEBOOK_CODE_SOURCE_ONLY.json"
ORIGINAL_NOTEBOOKS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks"
PIN="0634ed6a3a40931b4423ea9b665689286fbe074c"
cd "$WT"
test "$(git rev-parse HEAD)" = "$PIN"
test ! -e "$CODE_REPORT"
SHA_META="$(shasum -a 256 "$META" | awk '{print $1}')"

PYTHONPATH=src python3 \
 research/reviews/icomputing_2026/ic_g5_7d_one_omitted_notebook_gate.py \
 --original-g57c-report "$PREVIOUS" \
 --original-notebooks-root "$ORIGINAL_NOTEBOOKS" \
 --verified-metadata-report "$META" \
 --verified-metadata-sha256 "$SHA_META" \
 --inspect-omitted-code \
 --authorize-inspect-omitted-notebook-code \
 --out "$CODE_REPORT"

shasum -a 256 "$CODE_REPORT"
BASH
```

Regardless of status, the output always states no executed historical producer proof, no validated June archive target transformation, and no old V2–V4 outcome access. If this final bounded source test fails to find a meaningful writer, close the historical attribution by `LABEL_TRANSFORM_COMPATIBILITY_NOT_ESTABLISHED` and pivot to manuscript/response improvement and independently defensible risk/economic study. This is NOT a 60-day independent holdout or trading P&L, and 85/100 reviewer rebuttal readiness has not been obtained.
