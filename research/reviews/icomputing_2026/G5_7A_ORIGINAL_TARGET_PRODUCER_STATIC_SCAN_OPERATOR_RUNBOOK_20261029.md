# G5.7a — Local source-only June target-producer scan, original old financial outcomes NOT opened

Case ICOMPUTING-D-26-01069 · Date 2026-10-29.
Original owner-provided G5.7 readback SHA256: `e5d4e9281da809006c450be8a37c4c6c84cc51f2077b20e2c979ec061893020f`.

**Purpose:** locate original source code that MAY have written the exact three `target_model` archives, to decide whether the G5.6 V0 TRAIN clipping/ticker centers can be applied to V2/V3/V4. Existing public frozen dtrm-fund code defines the transform and later Phase-II loaders reference targets, but **does not by itself establish that the June saved labels use identical TRAIN parameters**.

**Source scan is restricted to .py files.** It intentionally does not open `.pkl` or `.ipynb` (Jupyter may embed financial outcomes in notebook output cells), nor CSV/data/prices. It reports filenames only relative to operator-supplied code roots and SHA hashes, no original script excerpts or secret source content.

## Operator command (Mac) — safe source-only preflight

```bash
bash <<'BASH'
set -euo pipefail

REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
WT="$HOME/dtrm-ic-g57a-source"
PIN="f1fd501d059b7ba55ea15b4d8290f57c4a942d1b"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
OUT="$AUDIT/IC_G57A_JUNE_TARGET_PRODUCER_SOURCE_ONLY_SCAN.json"
PYCODE="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks"
ORIGINAL_EXPERIMENTS="$REPO/research/experiments"

cd "$REPO"
git fetch origin research/ic-g5-3-information-parity-20261029
if [ -e "$WT" ]; then
  echo "STOP: G5.7a worktree already exists; inspect before reuse" >&2
  exit 1
fi
git worktree add --detach "$WT" "$PIN"
cd "$WT"

test "$(git rev-parse HEAD)" = "$PIN"
test -z "$(git status --porcelain)"
test -d "$PYCODE"
test -d "$ORIGINAL_EXPERIMENTS"
test ! -e "$OUT"

PYTHONPATH=src python3 \
  research/reviews/icomputing_2026/ic_g5_7a_target_producer_source_scan.py \
  --source-root "$PYCODE" \
  --source-root "$ORIGINAL_EXPERIMENTS" \
  --out "$OUT"

shasum -a 256 "$OUT"
BASH
```

The scanner checks exact V2, V3 and V4 target basenames; files containing only `pd.read_pickle` or literal target filenames are **not** writers. A same-file `to_pickle`/dump is **only** a candidate because static co-occurrence is not execution proof. Even if one is found, the program **always** reports `v2_v3_v4_label_transform_compatibility_proven=false`; do not elevate to a science claim.

### Expected statuses

- `G57A_SOURCE_WRITER_CANDIDATE_ONLY_PROVENANCE_OPEN`: candidate producing script(s), inspect their code and independent execution lineage next.
- `G57A_TARGET_REFERENCES_ONLY_NO_PRODUCER_PROOF`: readers/references, no identified writer.
- `G57A_NO_EXACT_TARGET_SOURCE_IN_BOUNDED_PY_SCOPE`: no exact saved target archive name in scoped .py; **does not exclude notebooks**, other directories, dynamic file naming.

If neither original code directory exists, do not invent a replacement; record absence and narrow/adjust only with actual source provenance and explicit documented operator scope.

## After PASS — scientific limitation remains

A producing source must establish: correct original per-split numeric TRAIN data, training ticker means, cutoffs, frozen source lineage, saved date and archive hash, and numeric data parity. Searching source alone does not establish these. **G5.7 V2/V3/V4 decomposition remains NO-GO** until its label compatibility is independently demonstrated, plus distinct old outcome access authorization. Do not open old target files based solely on this report.

No score increase toward 85/100 is justified by source-only tests or a possible source filename.
