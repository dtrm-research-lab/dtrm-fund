# ICOMPUTING-D-26-01069 — G3.1 A2/A6 point estimates PASS; clustered interval review

**Operator observation date:** 2026-10-28.

## Empirical outcome stage already completed

The operator ran original source SHA-bound,
separately consented `--mode point` at
frozen revision
`0c5e433f10ce742bc129b666dfc4551f4b2fd21b`.
Status:
`G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN`.

- Original Phase II q25/K10 numerical/delta hit
  parity PASS V2, V3, V4 before alternatives.
- Frozen validation-only P10 cuts:
  `q15=-0.17323055863380432`,
  `q25=-0.16665692627429962`,
  `q35=-0.16293590515851974`.
- The **18 prespecified** historical
  cells (9 A2 + 9 A6) are **observed feasible**.
- All 18 observed delta means and
  hit-rate deltas positive in the old,
  already outcome-consumed historical data.
- V2 and V3 had largest fixed-K10 delta at
  q35, with historical original q25 below
  it; q15 had lower delta.
- V4 had largest observed K-sensitivity
  delta at K5 rather than K10, unlike V2/V3.
- **Operator local SHA256 point report:**
  `8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb`.
- **No** bootstrap confidence intervals
  or new independent temporal holdout
  have yet been executed.

The point report is immutable operator-attested
local evidence. Never rewrite the prior failures
or source-float32 precision corrections.
All new estimates remain
`POST_OUTCOME_EXPLORATORY`. The dependent
V2/V3/V4 cohorts should not be naively pooled.

## Next full-mode stage — explicit A2/A6-only consent

The already 71-test-passed, source SHA-locked
runner is the exact same frozen commit above,
`ic_g3_1_a2_a6_protected_runner.py`.
Its `full` mode runs **10,000 original news_id
cluster bootstraps and 10,000 ticker cluster
bootstraps per feasible A2/A6 cell**.
At 18 feasible original-sample cells, that
means **up to 360,000 1x cluster draws**,
including duplicated q25/K10 policy cells
per historical cohort. The implementation
is computationally demanding.

Do NOT infer all CIs are valid from only
a `G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY`
status. Some resampled cells can become
*infeasible* even if original sample was
fully feasible. The frozen bootstrap module
intentionally withholds its CI when any
replicate fails to fill K. Every cell and
cluster type must be inspected individually;
do not discard infeasible replicates,
replace K, loosen original veto or select
an alternative threshold by outcome.

No causal identification, no independent
new 60-day holdout, no original contemporaneous
provider model-weight archive and no
self-financing realized portfolio
cost/P&L claim follows from the intervals.
Multiple testing across 18 cells must
be disclosed; descriptive overlap
or one unadjusted CI excluding zero
is NOT familywise-confirmed policy superiority.

### Operator command, original data read after explicit flags

Run the following ONLY with owner approval to
repeat original A2/A6 historical target access
and compute post-outcome exploratory CIs.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
COMMIT="0c5e433f10ce742bc129b666dfc4551f4b2fd21b"
POINT="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_POINT_ONLY.json"
FULL="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_FULL_10K_CLUSTERS.json"

test "$(shasum -a 256 "$POINT" | awk '{print $1}')" = "8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb"
git -C "$REPO" cat-file -e "$COMMIT^{commit}"
test ! -e "$FULL"

python3 "$AUDIT/ic_g3_1_a2_a6_protected_runner.py" \
  --review-repo "$REPO" \
  --approved-commit "$COMMIT" \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g1-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --original-local-data "$REPO/research/local_data" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --reconstructed-models "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --out "$FULL" \
  --mode full \
  --authorize-retrospective-a2-a6-old-outcome-access \
  --acknowledge-no-independent-60d-holdout \
  --acknowledge-no-realized-tradable-pnl \
  --trust-original-audited-pickles

shasum -a 256 "$FULL"

python3 - "$FULL" "$POINT" <<'PY'
import json,sys,math
from collections import Counter
with open(sys.argv[1],encoding="utf-8") as f: full=json.load(f)
with open(sys.argv[2],encoding="utf-8") as f: original=json.load(f)
assert full["status"]=="G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY"
assert full["immutable_a2_a6_runner_commit"]=="0c5e433f10ce742bc129b666dfc4551f4b2fd21b"
assert full["six_original_source_report_sha256"]=="3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8"
frows=full["results"]["cells"]
prows=original["results"]["cells"]
assert len(frows)==len(prows)==18
count=Counter()
for a,b in zip(frows,prows):
    key=(a["work_package"],a["cohort"],a["setting"])
    assert key==(b["work_package"],b["cohort"],b["setting"])
    for metric in ("k_required","admitted_pairs","full_k_feasible",
                   "delta_mean_forward_excess_beta","delta_hit_rate"):
        assert a[metric]==b[metric],(key,metric,"point estimate changed")
    for cluster,field in (("news","news_cluster_bootstrap"),
                          ("ticker","ticker_cluster_bootstrap")):
        x=a[field]
        assert x is not None,(key,cluster,"missing bootstrap block")
        assert x["replicates"]==10000,(key,cluster,"wrong replicate count")
        invalid=x["infeasible_replicates"]
        ci=x["ci95_delta_topk_mean"]
        chit=x["ci95_delta_topk_hit_rate"]
        if invalid:
            assert ci is None and chit is None,(key,cluster,"unsafe CI")
            count[cluster+"_WITHHELD"]+=1
        else:
            assert ci is not None and chit is not None
            assert len(ci)==len(chit)==2
            assert all(math.isfinite(v) for v in ci+chit)
            count[cluster+"_VALID"]+=1
        print(*key,cluster,"infeasible=",invalid,
              "mean_CI95=",ci,"hit_CI95=",chit)
print("Aggregate cluster statuses:",dict(count))
print("POST_OUTCOME_EXPLORATORY. No familywise adjusted claim.")
PY
BASH
```

**Expected success:** runner writes an original local JSON,
and the read-only report QA verifies **18 unchanged
point estimates** alongside exactly 10k news and
10k ticker draws per cell, with absent intervals
where any draw could not fill the required K.

If computationally interrupted, a full output
is deliberately NOT fabricated or overwritten;
the existing point report and immutable source
remain valid. A later reproducible rerun
must use the same immutable commit, mode, flags,
source SHAs and another original output pathname
if a partial file already exists.

**A3 price-volatility and realized trading P&L
remain separately blocked.**
