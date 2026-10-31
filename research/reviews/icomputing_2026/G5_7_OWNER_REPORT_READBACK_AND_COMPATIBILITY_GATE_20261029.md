# G5.7 — Read back original G5.6 owner evidence, WITHOUT opening market files

Case ICOMPUTING-D-26-01069. Date 2026-10-29.
State: **SOURCE-ONLY READBACK READY; V2/V3/V4 OUTCOME INSPECTION NOT AUTHORIZED**.

## Evidence received from owner after original local execution

- G5.5 original six-file SHA/metadata-only PASS: SHA256 `a9a39f0836f490dc2c8a464db224f546883e14e34cc3b6ff3b669cf726c32e2d`.
- G5.6 original TRAIN reconstruction on pinned public source commit `269c8c7a5ccff5273b99bc19c23ffdcdf03afde7`: TRAIN=**75,828** events across **171** tickers, original `float32` clipping+Kahan-centering parity **PASS**, original 174 price files SHA-checked, six original old cohort inputs hashed and **not deserialized**. Original G5.6 JSON SHA256: `ee6868bf190e4103f1951e53d4b66e34926b3f56f82974f4639b391f7bed963c`.
- `RPROMPT parameter not set` is shell/VS Code prompt integration with nounset, **not an experiment failure**.
- **Reporting bug G5.6 first run**: dict literal protected `status` was overwritten by `**fitted` `status`. First report says `TRAIN_CENTERS_NUMERIC_PARITY_ONLY` rather than the more specific `G56_TRAIN_ONLY_NUMERIC_PARITY_PASS_FULL_ROW_ARCHIVE_ORIGIN_UNATTESTED`. The original report **must NOT be rewritten**, original source SHA must remain pinned, status normalization is recorded as interpretation in a **separate** G5.7 readback.
- Historical full-row archive original SHA **UNATTESTED**, provider snapshot acquisition-time and adjustments **UNVERIFIED**. The original TRAIN mapping digest is not the 171 numeric centers, which remain unexported/private and must be reconstructed before a numerical V2/V3/V4 attribution.

## One Mac readback command (source JSON only, no pickle)

Use a NEW independent worktree for the updated reviewed code; do NOT update the old `~/dtrm-ic-g56-worktree` and do NOT re-run or overwrite the original G5.6 JSON.

```bash
bash <<'BASH'
set -euo pipefail
BASE="$HOME/Desktop/DTRM_Lab/dtrm-fund"
WT="$HOME/dtrm-ic-g57-readback"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
OLD="$AUDIT/IC_G56_original_train_centers_hash_only.json"
NEW="$AUDIT/IC_G57_G56_original_owner_evidence_readback.json"
EXPECTED="ee6868bf190e4103f1951e53d4b66e34926b3f56f82974f4639b391f7bed963c"

cd "$BASE"
git fetch origin research/ic-g5-3-information-parity-20261029
if [ -e "$WT" ]; then
  printf 'STOP: independent G5.7 worktree already exists, inspect before reuse\n' >&2
  exit 1
fi
git worktree add --detach "$WT" origin/research/ic-g5-3-information-parity-20261029
cd "$WT"
test -z "$(git status --porcelain)"
test ! -e "$NEW"
test "$(shasum -a 256 "$OLD" | awk '{print $1}')" = "$EXPECTED"

PYTHONPATH=src python3 research/reviews/icomputing_2026/ic_g5_6_original_report_readback.py \
    --report "$OLD" \
    --out "$NEW"
shasum -a 256 "$NEW"
BASH
```

Expected readback:
`G56_OWNER_REPORT_SHA_VERIFIED_TRAIN_PARITY_FULL_ROW_ORIGIN_UNATTESTED`;
`ORIGINAL_G56_SHA256=ee6868bf...`;
`TRAIN_N=75828 TRAIN_TICKERS=171`;
`FLOAT32_PARITY=PASS`;
`LEGACY_STATUS_COLLISION_RECORDED=True`;
`ORIGINAL_FULL_ROW_ARCHIVE_PROVEN=NO`;
`V2_V3_V4_OLD_LABEL_ACCESS=NONE`.

If any check fails, DO NOT bypass by editing JSON or changing expected SHA. Return exact error type and stage to research review; no original financial values needed.

## What this gate does NOT authorize

The readback only verifies local original **small aggregate JSON**, normalizes a prior **reporting** field collision with transparent provenance, and cannot verify the underlying private Pickles again, create original ticker center mappings from a SHA or approve unpickling old V2/V3/V4 targets.

**G5.7 source-compatibility gate is still required:** Before interpreting any V2/V3/V4 transformed label with V0 TRAIN mu, prove that the later separately saved archived labels used those very same original q1/q99 clip bounds and ticker training means; if source producer audit is unavailable, reconstruct archived original labels from frozen event dates, archived compatible quotes and authenticated beta and check numeric parity. Otherwise G5.7 must stop with `LABEL_TRANSFORM_COMPATIBILITY_NOT_ESTABLISHED`.

Only then may a separate, user-explicit **POST-OUTCOME EXPLORATORY** authorization allow outcome evaluation, all three cohorts retained, no tuning, conditional numerical decomposition or matched-information policy testing. This work alone earns no extra scientific reviewer points.
