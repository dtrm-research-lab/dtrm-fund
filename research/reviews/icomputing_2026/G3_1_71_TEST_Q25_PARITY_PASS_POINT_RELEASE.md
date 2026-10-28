# G3.1 A2/A6 — 71/71 protected tests + original Phase II q25/K10 parity PASS

**Case:** ICOMPUTING-D-26-01069
**Date:** 2026-10-28

## Tested immutable scientific source

`0c5e433f10ce742bc129b666dfc4551f4b2fd21b`

No subsequent audit commit updates that SHA or modifies the scientific source version whose 71 regression tests passed.

## Direct, operator-attested local evidence

- 22 old core math protection, 16 source join, 9 fixed 18-cell synthetic grid, 5 original P10 VALID-only source protections, 10 protected-runner code/consent and 9 original-point differential diagnostic tests: **71/71 PASS**.
- Original diagnostic:
  `G3_1_ORIGINAL_Q25_K10_ALL_3_PARITY_PASS_INVESTIGATE_PRIOR_FAILURE`,
  exit code 0.
- Source `target_model` native dtype: **float32** for V2/V3/V4; the revised join and point/core retain that dtype when aggregating original returns.
- V2 N=4,449 K=444 original = historic expected = protected delta mean `0.14429480582475662`; delta hit `0.5788288288288288`.
- V3 N=2,827 K=282 delta mean `0.14943748898804188`; delta hit `0.58510638297872342`.
- V4 N=40,320 K=4032 delta mean `0.027561593800783157`; delta hit `0.10168650793650791`.
- Local SHA256 of diagnostic report:
  `218d6064ea6824c3fa78d46d29e5b68d90de64aa16e10dea5707d0086e7a0df5`.

Previous empirical failure on immutable
`5cf62c854643576ee6059ac44f55a805b8ff3137`
is explained by unintentional promotion from original
float32 to float64 before calculation of NumPy mean.
No frozen historical outcome reference, source file,
P10 cutoff, Top-K rule, validation lookback, inference
seed, 1e-12 gate or model weights were changed.

## Next independently consented bounded experiment: A2/A6 POINT ONLY

The **18 cells are not yet computed**, and a value may be
infeasible if the veto leaves fewer than K admitted rows.
The existing operator permission for a frozen original
parity diagnostic is **not a substitute** for an explicit
new A2/A6 execution decision.

The already tested `ic_g3_1_a2_a6_protected_runner.py`
in the exact SHA above requires four owner attestations,
checks every local source module and test against the
same commit, and re-hashes six original cohort inputs
against the older G2.5 SHA commitments before opening
trusted Pickles. It only accesses known old 60-day
`forward_excess_beta` targets.
No A3 prices, actual portfolio P&L or prospective
cohort are accessed.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
CODE_SHA="0c5e433f10ce742bc129b666dfc4551f4b2fd21b"
OUT="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_POINT_ONLY.json"
git -C "$REPO" cat-file -e "$CODE_SHA^{commit}"
test ! -e "$OUT"

python3 "$AUDIT/ic_g3_1_a2_a6_protected_runner.py" \
  --review-repo "$REPO" \
  --approved-commit "$CODE_SHA" \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g1-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --original-local-data "$REPO/research/local_data" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --reconstructed-models "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --out "$OUT" \
  --mode point \
  --authorize-retrospective-a2-a6-old-outcome-access \
  --acknowledge-no-independent-60d-holdout \
  --acknowledge-no-realized-tradable-pnl \
  --trust-original-audited-pickles

shasum -a 256 "$OUT"
python3 - "$OUT" <<'PY'
import json,sys
with open(sys.argv[1],encoding="utf-8") as f: r=json.load(f)
print("G3.1 status:",r["status"])
print("Total cells:",len(r["results"]["cells"]))
for row in r["results"]["cells"]:
  print(row["work_package"],row["cohort"],row["setting"],
        "K:",row["k_required"],"admitted:",row["admitted_pairs"],
        "feasible:",row["full_k_feasible"],
        "delta_mean:",row["delta_mean_forward_excess_beta"],
        "delta_hit:",row["delta_hit_rate"])
PY
BASH
```

Expected terminal status, only if actual original
V0 q25, source join, model/source SHA and original
three-cohort q25/K10 outcome gates PASS:

`G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN`.

This is **not** scientific confirmation of the 18
cells' superiority: results are post-outcome
sensitivity point estimates, without confidence
intervals, based on nonindependent old cohort labels.
If any original gate fails, log the exact error
and halt. Do not overwrite original frozen reports
or retune anything to fit the outcomes.

The full 10k-news/ticker clustered A2/A6 CIs
are a separate later scientific operation and
A3 retrospective price-volatility remains
prohibited.
