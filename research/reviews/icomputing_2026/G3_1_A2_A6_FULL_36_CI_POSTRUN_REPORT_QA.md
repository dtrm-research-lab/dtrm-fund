# ICOMPUTING-D-26-01069 — G3.1 A2/A6 FULL bootstrap report read-only audit

**Date:** 2026-10-28.
**Status:** full original A2/A6 runner completed; point-level and CI-level independent audit pending.

## Exact operator evidence (retained original)

- Executed full original results status:
  `G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY`
- Frozen original science commit:
  `0c5e433f10ce742bc129b666dfc4551f4b2fd21b`
- Original q25/K10 point parity: V2/V3/V4 **PASS**.
- 18 original already-consumed historical A2/A6 cells, all observed feasible in `point` result.
- Original point report SHA256:
  `8493355a8711512e0182067ad5b10e652528acd348cbde21bd1291f56ca214bb`.
- Full 10,000-news and 10,000-ticker clustered outcome report SHA256:
  `53c4618f86f46a80a5a783c3449a8d120379f26c8d459c8e740dd4fb63697968`.
- The original full-mode terminal only printed that 18 cells and
  fixed cluster resampling completed; **did not print actual
  interval bounds or nonfeasible-replicate counts**.
- Both SHA values above are operator-computed local hashes, not
  remote verification of local report contents.

This independent QA is deliberately NEW AUDIT CODE, not a mutation
of original locked scientific runner. It reads only two local
**aggregate JSON reports**. It does NOT re-open any local original
Pickle, source XGBoost model, financial forward targets, cached FMP
price data or raw news identifier arrays, and does not recompute
the 360k resamples.

## The 36-block acceptance contract

`ic_g3_1_a2_a6_full_report_qa.py` verifies:

1. Exact original point and full report file SHA-256 plus common
   frozen scientific commit, G2 original frozen protocol,
   G3.0 original P10/ranker parity and old 6-source manifest.
2. Retrospective inferential scope remains disclosed:
   `forward_excess_beta` 60-day target is NOT realized portfolio P&L;
   no untouched 60d matured forward holdout; A3 is not authorized.
3. Exactly 18 unique preregistered cells: 9 A2
   q15/q25/q35 × V2/V3/V4, and 9 A6 K5/10/15 × V2/V3/V4,
   no new code-selected optimal threshold or capacity.
4. Original *all* point descriptors are identical between
   the previous `point` report and the new `full` report;
   no moving original policy nor replacement of one result.
5. Exactly 36 original news/ticker bootstrap result blocks,
   fixed 10,000 resamples and seeds 20260821(news)/20260822(ticker).
   Every block must disclose an integer count of infeasible draws.
6. **If any draw in a given block was infeasible, BOTH that
   block's mean/hit CI95 must be withheld (None).** If all
   10,000 were feasible, BOTH CIs must be finite, ordered
   numerical pairs. Never condition away failed draws.
7. Original policy q25/K10 appears twice in fixed grid:
   A2 q25 and A6 K10 for each cohort.
   The copied decision and same seeded bootstrap must
   return identical interval values and infeasibility counts.
8. The reader reports 36 status lines and aggregate valid,
   withheld and unadjusted mean-CI-exclusion counts.
   Any interval excluding zero is **only descriptive
   unadjusted post-outcome exploration**:
   no multiplicity correction across 18 cells,
   no causal claims, no independent validation.

**QA PASS means the JSON is structurally faithful to the
frozen protocol and can be interpreted with its limits;
it does NOT mean 36/36 CIs exist, that every CI excludes
zero or that DTRM is statistically superior to baseline.**

## One local command, zero original outcome/deserialization access

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
QA_COMMIT="c4bee96b71764fb4bcd76eb20f09177bcf61ce06"
BASE="research/reviews/icomputing_2026"
POINT="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_POINT_ONLY.json"
FULL="$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_FLOAT32_FULL_10K_CLUSTERS.json"

git -C "$REPO" fetch origin research/ic-major-revision-2026
git -C "$REPO" cat-file -e "$QA_COMMIT^{commit}"
git -C "$REPO" show "$QA_COMMIT:$BASE/ic_g3_1_a2_a6_full_report_qa.py" \
  > "$AUDIT/ic_g3_1_a2_a6_full_report_qa.py"
git -C "$REPO" show "$QA_COMMIT:$BASE/test_ic_g3_1_a2_a6_full_report_qa.py" \
  > "$AUDIT/test_ic_g3_1_a2_a6_full_report_qa.py"

cd "$AUDIT"
python3 -m unittest test_ic_g3_1_a2_a6_full_report_qa.py -v
python3 "$AUDIT/ic_g3_1_a2_a6_full_report_qa.py" \
  --point "$POINT" --full "$FULL"
BASH
```

**Expected if reports follow contract:**
11 isolated synthetic/statically tested QA rules `OK`;
then `G3_1_A2_A6_FULL_36_CLUSTER_BLOCKS_REPORT_QA_PASS`.
The output prints 18×2 aggregate lines. It may show
valid and withheld intervals; do not infer the count
in advance. User can paste the terminal summary for
a qualified post-outcome scientific interpretation.

## What remains explicitly blocked

A3 original price volatility comparison has its own
old-vintage caveats and controls. A4 actual cash
turnover/transaction costs and profits, A5 independent
old ranker and X1 nonoverlapping prospective 60d holdout
are not gained by this test. Before any *claim* of
robust policy superiority, evaluate news/ticker
clusters, infeasible replicates and multiplicity,
and clearly caveat observed old cohort selection.
