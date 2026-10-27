# G2.6 — Bind original validation P10 / G1 replay to G2.5 source hashes

Date: 2026-10-27. Case ICOMPUTING-D-26-01069.
Gate: G2 remains ACTIVE/UNFROZEN. G3 remains BLOCKED.

## Operator outcome of G2.5

The operator ran the three-root bounded inventory:
`G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3`.

- **92 files** identified and SHA256 streamed, **zero** oversized
  omissions; no deserialization and no financial values read.
- Filename-category hits: features 10, historical cohorts 44,
  price/beta-history 50, validation/quantile 5
  (categories overlap).
- The compact `probabilistic_v2_frozen_p10_threshold.pkl`
  (248 bytes) and other historic frozen V2/V3/V4
  features/signals are present by name and current SHA.
- No separate authenticated, **individual 19,880-row
  validation-P10 score vector and news weight vector** has
  yet been identified: five filename matches do not
  constitute those arrays, and their absence was NOT proven.
- Price/beta-history filename matches are **not**
  sufficient evidence for point-in-time volatility,
  economic execution cost, turnover or actual P&L.

## Important source recovery for A2

The already verified original G1.2 training reconstruction
`ic_g1_reconstruct.py` reproduces, using the pinned
original V0 `run_probabilistic_xgb_v0.py` source:

1. Original train/valid/test masks and transformed
   targets, independently checked against baseline.
2. Validation **19,880 rows** and
   `legacy_news_weights` based on original news IDs.
3. XGBoost P10 validation predictions at original best
   iteration **18**.
4. Frozen validation calibration offset
   `-0.06494169682264328`.
5. The exact original weighted empirical quantile
   implementation: sorted calibrated P10 predictions,
   cumulative news weights, `searchsorted(side='left')`.
6. Original weighted q=0.25 cutoff
   `-0.16665692627429962`.
7. The G1.2 original reconstruction previously passed
   12/12 numeric precommitted historic checks.

Thus a deterministic **original validation source route
exists** for frozen weighted percentile q=0.15,0.25,0.35,
without introducing alternate models or fitting a threshold
on the old V2/V3/V4 test targets.

**Do not execute this prospective sensitivity analysis
yet.** G2 must predeclare and freeze the exact q-grid,
the input hashes, all old-cohort admission/full-K/metric
and clustering calculations, and how infeasible points
are represented. V2/V3/V4 outcomes are already consumed,
so new secondary comparisons are explicitly exploratory.

## G2.6 operator source-binding check (no scientific data opened)

From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g2_validation_source_binding.py" \
  -o "$AUDIT/ic_g2_validation_source_binding.py"

python3 -m py_compile "$AUDIT/ic_g2_validation_source_binding.py"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_reconstruct.py" \
  -o "$AUDIT/ic_g1_reconstruct_source_for_g2.py"
python3 -m py_compile "$AUDIT/ic_g1_reconstruct_source_for_g2.py"

python3 "$AUDIT/ic_g2_validation_source_binding.py" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --g1-sealed "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --g1-preflight "$AUDIT/g1-reconstruction/IC_G1_2_preflight.json" \
  --g1-rebuild "$AUDIT/g1-reconstruction/IC_G1_2_rebuild.json" \
  --g1-reconstruction-code "$AUDIT/ic_g1_reconstruct_source_for_g2.py" \
  --g2-inventory "$AUDIT/g1-reconstruction/IC_G2_historical_analysis_sources.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json"
```

**Note:** The G1 reconstruction script is fetched separately
from the review branch for read-only inspection; no original
G1 scripts are executed or models retrained by G2.6.
Do NOT point `--frozen-repo` at a mutable working
branch; its HEAD must be exactly
`c7502a690162459cdfb3413573e3133c42efb126`
and tracked state clean.

Expected source-ready status:

`G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED`

On a failed source or SHA gate the program stops.
This check reads only JSON audit reports and `.py`
source code and Git metadata. It does not open any
Pickle, NumPy array, financial observation, price,
model binary, training label, test target, or newer
event cohort; it produces no q=0.15/0.35 values.

## G2→G3 protected transition

- A2: original score/calibration computation route
  may be deterministically reconstructable; still
  requires **frozen exploratory preanalysis plan**.
- A3: conventional risk baseline NOT yet certified
  as-of historical time; do not infer from 50 names.
- A4: no executable portfolio/cost model verified.
- A6: original old pair/feature/signal files
  identified; K sensitivity requires frozen formula.
- X1: independent new temporal sample unavailable
  in audited roots and not authorized.

G2 may close **even if some analyses are documented
NOT_EXECUTABLE**, but not by silently dropping an
authentic reviewer objection.

**Current state: G2 OPEN, G3 BLOCKED; operator G2.6 NOT RUN YET.**

## Superseding operator outcome — G2.6 PASSED on 2026-10-27

The source binding was **executed** after the initial
runbook was published. Status exactly
`G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED`.
All nine frozen V0 source token checks passed.
Eight old input artifact SHA references were found.
Original weighted-validation q25 matched
`-0.16665692627429962`.
G2.5 metadata audit SHA was checked as
`ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.

The earlier 'G2.6 NOT RUN YET' footer above is
superseded by this executed status. No G3 financial
reanalysis or alternative cutoff calculation occurred.

**Next** `G2_7_A2_PREREG_SOURCE_PREFLIGHT.md`: formal
documentation-only A2 grid gate. Overall G2 freeze
and all G3 experimental scoring remain BLOCKED.
