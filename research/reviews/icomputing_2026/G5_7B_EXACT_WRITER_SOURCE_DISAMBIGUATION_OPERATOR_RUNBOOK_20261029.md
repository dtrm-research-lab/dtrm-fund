# G5.7b — Exact-target producer vs source consumer: Mac operator runbook

Date 2026-10-29; case ICOMPUTING-D-26-01069.

**Operator input is genuine original G5.7a SHA report:** `4c1dc4bb7309e89020c58600fd58166958d74926173e4807bd1235b99c152c19`. Scanner checked 38 .py files, produced 12 candidates and exactly 1 filename reference per V2/V3/V4. This is source-only information, not actual target-label production.

## WHY a stricter classification is needed

Original frozen public `research/experiments/run_phase2_primary_bootstrap.py` **reads** saved V2/V3/V4 `target_model` files by `pd.read_pickle` then uses `np.savez_compressed` for derived bootstrap output. G5.7a erroneously allowed unrelated `savez_compressed` to mark same-module target filename references as writer candidates. A possible false positive is scientifically material: source *consumption* of old labels cannot establish their *generation* or the original TRAIN ticker centers.

G5.7b re-hashes the 12 operator-identified exact `.py` source files, parses AST, and only identifies a static source write candidate if the original exact basename appears as the argument of a matching archive-writing operation, never because a different `.npz` file is saved. Dynamic writer paths are NOT inferred and remain unresolved. It does NOT load prices, news, `.pkl`, `.ipynb`, or results. It does NOT prove executed producer provenance, output artifact lineage, model training-vintage identity, or V2/V3/V4 label-transform compatibility.

## Read-only local execution

```bash
bash <<'BASH'
set -euo pipefail
BASE="$HOME/Desktop/DTRM_Lab/dtrm-fund"
WT="$HOME/dtrm-ic-g57b-source"
PIN="5a603c4dd63daa8d32729a52f3227d488e03d5ea"
AUDIT="$HOME/dtrm-ic-audit/g1-reconstruction"
INPUT="$AUDIT/IC_G57A_JUNE_TARGET_PRODUCER_SOURCE_ONLY_SCAN.json"
OUT="$AUDIT/IC_G57B_EXACT_ARCHIVE_WRITER_SOURCE_DISAMBIGUATION.json"
NOTEBOOKS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks"
ORIGINAL_EXPERIMENTS="$BASE/research/experiments"
EXPECTED="4c1dc4bb7309e89020c58600fd58166958d74926173e4807bd1235b99c152c19"

cd "$BASE"
git fetch origin research/ic-g5-3-information-parity-20261029
test ! -e "$WT"
git worktree add --detach "$WT" "$PIN"
cd "$WT"
test "$(git rev-parse HEAD)" = "$PIN"
test -z "$(git status --porcelain)"
test ! -e "$OUT"
test "$(shasum -a 256 "$INPUT" | awk '{print $1}')" = "$EXPECTED"

PYTHONPATH=src python3 \
  research/reviews/icomputing_2026/ic_g5_7b_direct_writer_disambiguation.py \
  --g57a-original-report "$INPUT" \
  --source-root "$NOTEBOOKS" \
  --source-root "$ORIGINAL_EXPERIMENTS" \
  --out "$OUT"

shasum -a 256 "$OUT"
BASH
```

## Interpretation and strict stop

Expected source-only status is `G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE` if source references have no clearly bound archive writer. `G57B_DIRECT_EXACT_ARCHIVE_WRITE_CANDIDATE_PROVENANCE_OPEN` indicates a **candidate only**, not an executed historical producer. Original June target-model compatibility remains **UNPROVEN** under either status. The script prints exact source-relative .py paths for the V2/V3/V4 literal references, with `READ_PICKLE`, `OTHER_SAVEZ`, and `DIRECT_WRITE` flags. Do not upload code snippets, secret data, full original financial files or raw return records.

If scanner finds only the known Phase-II **consumer**, do not force an attribution by assuming V2/V3/V4 model targets used the same TRAIN clipping and centering. Consider a new bounded search of other **pre-June provenance/source histories**, but do not touch notebooks with embedded results or original private outcomes without a separate audit/approval. A source-only negative does NOT show a generator could never exist; it shows the scanned `.py` code did not prove one.

**Source test status:** 85/85 source-only checks PASS at GitHub Actions run 40865395580 and general repository Tests PASS (no historical financial outcomes accessed). This is not a scientific 85/100 reviewer readiness score.
