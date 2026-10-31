# G5.7c — Protected original Notebook CODE-CELL ONLY source provenance, not outcome evaluation

**Date:** 2026-10-29. **Case:** ICOMPUTING-D-26-01069.
**Status:** SOURCE-ONLY CI 95/95 tests PASS, owner private notebook inspection NOT EXECUTED.

## Scientific reason

G5.7b original owner's SHA `b8d0d10eef98fe57a85cd1ddc65262aaa905d01f53c3733f397389a2cf73e308` established `G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE`. The sole literal V2/V3/V4 source reference was `research/experiments/run_phase2_primary_bootstrap.py`, a **consumer** that reads old saved labels and writes a different bootstrap file. The original June target-producer code may exist in a Jupyter notebook, which was expressly excluded from G5.7a/b. The current `dtrm-fund` public main GitHub history queried through 2026-06-30 returned no commits; public current git history alone cannot establish June generation.

## Optional owner command, separately authorized

A notebook `.ipynb` file can embed raw old results as cell outputs. This code opens **notebook files** but uses a streaming JSON tokenizer that skips nested `outputs` payloads, never JSON-decodes them, stores only transient **code-cell source**, never executes any notebook cell, never reads a financial `.pkl`, and reports only source paths, SHA and boolean/counter evidence. It hashes raw notebook bytes for provenance. This is **NOT** a claim that notebook bytes are unread; it is a narrow **code-only parser**.

The tool requires `--authorize-notebook-code-inspection` as the operator's affirmative authorization. It refuses symlinks, caps 400 notebooks, 16MB per notebook, 128MB total, and fails closed on malformed data. It skips original `Outputs` directories. If one notebook exceeds the cap it records a skip, not a negative proof.

```bash
bash <<'BASH'
set -euo pipefail
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
WT="$HOME/dtrm-ic-g57c-notebook-source"
PIN="0ee9fbfeab985a1ad9f815902c75e96012db9d70"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
IN="$AUDIT/IC_G57B_EXACT_ARCHIVE_WRITER_SOURCE_DISAMBIGUATION.json"
OUT="$AUDIT/IC_G57C_ORIGINAL_NOTEBOOK_CODE_PRODUCER_SOURCE.json"
NOTEBOOKS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks"
EXPECTED="b8d0d10eef98fe57a85cd1ddc65262aaa905d01f53c3733f397389a2cf73e308"

cd "$REPO"
git fetch origin research/ic-g5-3-information-parity-20261029
test ! -e "$WT"
git worktree add --detach "$WT" "$PIN"
cd "$WT"
test "$(git rev-parse HEAD)" = "$PIN"
test -z "$(git status --porcelain)"
test -d "$NOTEBOOKS"
test ! -e "$OUT"
test "$(shasum -a 256 "$IN" | awk '{print $1}')" = "$EXPECTED"

PYTHONPATH=src python3 \
    research/reviews/icomputing_2026/ic_g5_7c_notebook_code_source_scan.py \
    --g57b-original-report "$IN" \
    --original-notebooks-root "$NOTEBOOKS" \
    --out "$OUT" \
    --authorize-notebook-code-inspection

shasum -a 256 "$OUT"
BASH
```

Statuses include `G57C_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY`,
`G57C_NOTEBOOK_DYNAMIC_WRITER_LEADS_ONLY`,
`G57C_NOTEBOOK_TARGET_REFERENCES_ONLY`, or
`G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS`.
**None** means the original label producer executed on the indicated date, that V2/V3/V4 used the reconstructed V0 TRAIN mean or clipping, that sources are point-in-time tradable, or that further private old outcome access is approved.

## False-positive and no-result audit requirements

A Jupyter **output** which mentions `probabilistic_v2_holdout_model_targets_2026-06-10.pkl` is not a code-cell reference or producer. A source-cell `pd.read_pickle` is a reader. Source-cell `target_model.to_pickle(path)` without literal filename may be a **dynamic lead**, not an exact archive identity. A notebook filename/mtime does not certify its execution date. An absent lead after bounded source scanning is **source-provenance incompleteness**, not evidence the data cannot exist. The original 75,828 TRAIN/171 ticker reconstruction still stands as an aggregate source-parity result, but no V2/V3/V4 attribution follows without later compatibility proof.

**CI run** [40866497531](https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40866497531): **95/95 tests PASS**; includes deliberately misleading embedded output text and malformed/notebook symlinks. The source-only test numbers are technical, not an 85/100 scientific rebuttal score.
