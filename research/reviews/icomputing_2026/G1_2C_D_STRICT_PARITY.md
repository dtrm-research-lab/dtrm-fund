# IC Major Revision — G1.2c/d strict reconstruction parity and original row-key provenance

Date: 2026-10-27; manuscript ICOMPUTING-D-26-01069.

## Checkpoint entering this gate
Operator reported successful original historical XGBoost reconstruction at
commit `c7502a690162459cdfb3413573e3133c42efb126` with
12/12 historical metrics and calibration checks. Original V1/V4 frozen
40,320-row signals were tested with the reconstructed boosters.
The historical ranking predictions were numerically **identical**
(max absolute difference 0.0), and P10 admission masks were identical
for both V1 absolute-zero veto (0 passes) and V4 frozen-P25 veto
(23,348 passes). No outcomes outside previously used cohorts inspected.

The G1.2b implementation classifies numeric P10 parity as passing if
**either** recognized P10 numeric field agrees. Because `p10_raw` and
`p10_calibrated` are both present, **require both** to pass individually
before any further model-provenance conclusion.

## A. Strict P10 check; reads JSON ONLY, no model/Pickle

```bash
AUDIT="$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_dual_p10_check.py" \
  -o "$AUDIT/ic_g1_dual_p10_check.py"
python3 -m py_compile "$AUDIT/ic_g1_dual_p10_check.py"
python3 "$AUDIT/ic_g1_dual_p10_check.py" \
  --prior "$AUDIT/g1-reconstruction/IC_G1_2_row_parity.json"
```

Expected on successful *dual* numeric check:
`G1.2c: DUAL_P10_NUMERIC_PARITY_PASS_PROVENANCE_OPEN`.
If one numeric field fails, diagnose; do not substitute a different
quantile model or retune thresholds.

## B. Original 2026 source pair key/order audit; trusted historic Pickle read

```bash
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_pair_keys.py" \
  -o "$AUDIT/ic_g1_pair_keys.py"
python3 -m py_compile "$AUDIT/ic_g1_pair_keys.py"
python3 "$AUDIT/ic_g1_pair_keys.py" \
  --local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --original-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out "$AUDIT/g1-reconstruction/IC_G1_2_pair_keys.json" \
  --trust-original-pickles
```

It reads only original pair/source and signal Pickles:
`pairs_raw_2025-01-01_2026-06-06.pkl`,
`probabilistic_v1_holdout_signals_2026-06-06.pkl`.
It does **not** open future targets, market prices, the 2026-08+ holdout,
or private Phase IV data. Reports SHA of raw pairs (new local commitment)
and checks pair IDs, order, duplicate keys, and event dates when available.
A pair key/order match alone **does not independently reconstruct**
the 390-feature historical matrix. The embedding and beta
provenance remain to be separately audited. Do not mark as completed
scientific row provenance merely from identical sort.

## Subsequent required gates
1. Corroborate beta and embeddings/text mapping to pair keys and
   exact historical feature-matrix row order without future outcomes.
2. Record model SHAs and training provenance in a separate immutable
   candidate manifest; original boosters are *reconstructed*, not
   historic serialized originals.
3. Pre-register a new independent temporal cohort **before** reading
   its outcomes; check event dates, source freshness, news ingestion and
   60-day realized-price maturity. Keep MM1/Phase IV isolated.
4. Evaluate threshold sensitivity, alternate risk baselines, cluster
   dependence and realized portfolio costs as separate reviewer tests.

Nothing in G1.2c/d is a new out-of-sample performance result.

## 2026-10-27 correction — Superseded G1.2d equal-sized pair comparison

Operator's G1.2c strict numeric check PASSED on baseline, raw P10,
calibrated P10, V1 veto and V4 veto (see G0_G1_AUDIT.md).
The G1.2d raw pair equality test should **not** be used as a provenance
approval/rejection: it compared 265,145 local raw candidate pairs with
40,320 selected V1 signals and has no filtering-stage awareness. The
historical contract also lists 40,320 rows under the same raw filename,
so the source/contract cardinality mismatch is separately unresolved.
Use `G1_2E_SOURCE_SUBSET_RUNBOOK.md` and `ic_g1_source_subset.py`
for a correctly bounded membership and selection-lineage audit.
