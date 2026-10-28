# G3.1 — ORIGINAL q25/K10 historic reproduction STOP; bounded differential diagnostic

Case: ICOMPUTING-D-26-01069
Date: 2026-10-28

## Evidence of stoppage

Operator-authorized original A2/A6 `--mode point` runner
at immutable reviewed source commit
`5cf62c854643576ee6059ac44f55a805b8ff3137`
returned:

`G3.1 HALTED: ScientificGateError Old historical q25/K10 effect failed 1e-12 parity`

This occurred in the old q25/K10 gate of
`analyze_18_cells`, before its fixed 18 sensitivity
cells are built. **No new sensitivity results
or confidence intervals were calculated.**
The message did not report which of original V2, V3, V4
or whether mean versus hit-rate deviated.

Previously established evidence still holds:
- G2 original source/scope scientifically frozen at
  `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`.
- G3.0 original ranker/P10 7,276-row parity PASS,
  source report SHA256
  `a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a`.
- G3.1 source-only original six signal/target file SHA PASS,
  report SHA256
  `3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8`.
- 38/38 synthetic and static tests PASS for old approved
  A2/A6 protected code commit. That is **not**
  a historical empirical point-parity PASS.
- Frozen original primary Bootstrap source at
  `c7502a690162459cdfb3413573e3133c42efb126`:
  `research/experiments/run_phase2_primary_bootstrap.py`.
  `load_cohort` and `evaluate_selection` are used
  solely as immutable historical comparators.

## Why this is a separate bounded diagnostic

Original PhaseII and new protected implementation use
`np.argsort(-baseline_prediction)`,
`K=int(0.10*N)`, original boolean `p10_pass`,
and `candidate=order[p10_pass[order]][:K]`.
A difference is unexpected, but the current exception
cannot locate its source.

Use `ic_g3_1_original_q25_parity_diagnostic.py` to
calculate **ONLY three original q25/K10 original
published summary effects** from SHA-verified trusted
original files, with two independent implementations:

1. Frozen untouched original PhaseII
   `load_cohort` + `evaluate_selection`.
2. SHA-verified protected
   `source_exact_join` + original-only
   `select_topk`.

Report for V2/V3/V4: N, K, selected count,
original expected delta mean/hit,
frozen original observed delta mean/hit,
new protected observed delta mean/hit,
and exact differences. NO row identities or
per-row targets are saved or printed. NO alternate
q, capacity, 18 sensitivity cells, bootstrap, A3,
future return labels or new strategy model.

**If original frozen evaluator fails to reproduce
its own historical expected point numbers**, record
scientific provenance/result inconsistency; NEVER
retune expected deltas. **If original evaluator PASSes
and our protected evaluator fails**, debug new
join/dtype/order code preserving original source bytes.
**If both PASS**, investigate prior execution
or environmental discrepancy before resuming.
In every case old G3.1 stage stays blocked until
a separate source-verified resolution and review.

## Operator steps (read-only except local diagnostic JSON)

The user previously approved A2/A6 use of original
old outcomes in a protected point run; this
diagnostic also reads the same trusted old
target Pickles and requires its own explicit
confirmation of this restricted reuse.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
APPROVED_G31="5cf62c854643576ee6059ac44f55a805b8ff3137"

git -C "$REPO" fetch origin research/ic-major-revision-2026
DIAGNOSTIC_COMMIT="$(git -C "$REPO" rev-parse FETCH_HEAD)"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/$DIAGNOSTIC_COMMIT/research/reviews/icomputing_2026"

curl -fsSL "$BASE/ic_g3_1_original_q25_parity_diagnostic.py" \
  -o "$AUDIT/ic_g3_1_original_q25_parity_diagnostic.py"
curl -fsSL "$BASE/test_ic_g3_1_original_q25_parity_diagnostic.py" \
  -o "$AUDIT/test_ic_g3_1_original_q25_parity_diagnostic.py"

cd "$AUDIT"
python3 -m unittest test_ic_g3_1_original_q25_parity_diagnostic.py -v

python3 "$AUDIT/ic_g3_1_original_q25_parity_diagnostic.py" \
  --review-repo "$REPO" \
  --diagnostic-code-commit "$DIAGNOSTIC_COMMIT" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --original-local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --out "$AUDIT/g1-reconstruction/IC_G3_1_original_q25_K10_parity_diagnostic.json" \
  --authorize-original-q25-parity-diagnostic-only \
  --trust-previously-sha-audited-original-pickles

shasum -a 256 "$AUDIT/g1-reconstruction/IC_G3_1_original_q25_K10_parity_diagnostic.json"
echo "DIAGNOSTIC_COMMIT=$DIAGNOSTIC_COMMIT"
BASH
```

The diagnostic may return exit code **2** when it has
successfully *identified* a scientific discrepancy;
with `set -e` the trailing SHA/commit lines will
not then run. In that case a report **will already
exist**. The operator should send the three
V2/V3/V4 status lines and run separately:

`shasum -a 256 "$HOME/dtrm-ic-audit/g1-reconstruction/IC_G3_1_original_q25_K10_parity_diagnostic.json"`.

If it halts before report creation, send the
exact HALTED reason; do NOT alter or overwrite
original source reports.

**No claim of successful tests or source diagnostic
is made by simply committing this runbook.**
