# G3.1 A2/A6 — final protected release: 38 synthetic/static checks, explicit old-outcome consent

**Case:** ICOMPUTING-D-26-01069.
**Status:** SOURCE/PURE-MATH 28/28 OPERATOR PASS. **NEW PROTECTED RUNNER NOT YET TESTED OR APPROVED**.
**Original G2 freeze:** `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`.
**Scientific interpretation:** Old V2/V3/V4 outcomes were already seen. All new sensitivity cells are SECONDARY **POST_OUTCOME_EXPLORATORY**, not independent test results. Target is beta-adjusted 60d outcome, NOT self-financing P&L.

## Closed operator evidence

Original seven source-only protection tests previously PASS, and source report `G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED` carried 6/6 original V2/V3/V4 signal/target SHA checks.

The original source-only report SHA256 has now been **operator supplied**:

`3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8`.

Original G3.0 V2/V3 7,276-row baseline and P10 numeric parity PASS, report SHA:
`a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a`.

The user's latest local test showed **28/28 PASS**:
- 15 synthetic exact pair-key/date/source P10 join cases.
- 8 synthetic original-cohort q25/K10/18 sensitivity-cell cases.
- 5 static original 19,880-row V0 validation-only source cases.

A Pandas date parsing warning was emitted only during an intentionally invalid-date test; it was non-fatal.

## Final prepared controlled runner

`ic_g3_1_a2_a6_protected_runner.py` joins only approved pieces:
1. Verify the **actual immutable Git commit** contains the exact runner and its eight referenced source/test files. Local files must match those bytes; no mutable-branch code substitution.
2. Verify archived G2.17 owner approval, G3.0 report SHA and source-only original six-file G3.1 report SHA (all separately operator-anchored).
3. **Rehash all six old local signal/target files BEFORE unpickling anything**, verify file length and original G2.5 SHA, and enforce V4 signals use **V1 target** data file.
4. Require the human operator to **explicitly attest** (a) permission for old consumed outcomes limited to A2/A6, (b) no new independent matured 60d holdout, (c) original excess-beta is not realized trading P&L, and (d) consent to unpickling **previously audited trusted original files**. No cryptographic owner signature is claimed.
5. Rebuild original V0 **19,880 VALID** P10 using the frozen 390-feature source and saved model hash without reading historical forward targets, derive validation-only q15/q25/q35.
6. AFTER approval, load only the six previously SHA-pinned original Phase II signal/target files. Require exact one-to-one unique `news_id,ticker` plus matching original `date_dt`, strict P10 calibrated/rule parity and finite targets.
7. **BEFORE computing sensitivities**, reproduce old q25/K10 V2/V3/V4 incremental mean and hit-rate at 1e-12. Mismatch -> hard stop. Fixed nine A2 and nine A6 cells.
8. `--mode point`: report exactly 18 point-estimate cells and old policy parity; bootstrap explicitly NOT YET RUN. `--mode full`: full original grid and fixed 10,000 news + 10,000 ticker cluster resamples per feasible cell; report all infeasibilities and suppress affected intervals, no cherry-picking.
9. No A3 price-cache retrospective volatility, no alternate model, no new independent forward-return inference, no user-level identity or per-news target disclosure, no output overwrite.

Created **10** additional static source-only release security tests in
`test_ic_g3_1_a2_a6_protected_runner.py`.
Added to prior 28 = **38** required checks on current code.
These ten are currently **NOT YET MAC OPERATOR-RUN**;
GitHub source readback does not constitute a test PASS.

## Step 1 — Run ALL current 38 synthetic/static tests (NO original target access)

This command only downloads exact code by Git commit SHA and executes
synthetic/static tests. It DOES NOT deserialize historical targets.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
git -C "$REPO" fetch origin research/ic-major-revision-2026
G31_CANDIDATE="$(git -C "$REPO" rev-parse FETCH_HEAD)"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/$G31_CANDIDATE/research/reviews/icomputing_2026"
for file in \
  ic_g2_g3_exploratory_core.py \
  ic_g3_1_a2_a6_join_contract.py \
  test_ic_g3_1_a2_a6_join_contract.py \
  ic_g3_1_a2_a6_pure_grid.py \
  test_ic_g3_1_a2_a6_pure_grid.py \
  ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_1_a2_validation_only_source.py \
  ic_g3_1_a2_a6_protected_runner.py \
  test_ic_g3_1_a2_a6_protected_runner.py
do
  curl -fsSL "$BASE/$file" -o "$AUDIT/$file"
done
cd "$AUDIT"
python3 -m unittest \
  test_ic_g3_1_a2_a6_join_contract.py \
  test_ic_g3_1_a2_a6_pure_grid.py \
  test_ic_g3_1_a2_validation_only_source.py \
  test_ic_g3_1_a2_a6_protected_runner.py -v
printf '%s\n' "$G31_CANDIDATE" > "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_CODE_COMMIT.txt"
printf 'RELEASE_CANDIDATE_SHA=%s\n' "$G31_CANDIDATE"
BASH
```

Expected: `Ran 38 tests ... OK`.

## Step 2 — operator authorization of old-consumed outcomes (ONLY AFTER 38 PASS)

**This is a NEW authorization decision.**
The existing human approval for G2/G3.0 explicitly
denied old targets. The operator must now choose
to approve A2/A6 old-outcome access and accept the
scientific limitations above. Do NOT run this step
until Step 1 returned a complete 38-test PASS.

The runner's source input and protected tests must
be those exact downloaded by the frozen candidate
Git commit. The operator must supply that exact
`G31_CANDIDATE` SHA printed in Step 1.

```bash
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
G31_CANDIDATE="$(cat "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_CODE_COMMIT.txt")"

python3 "$AUDIT/ic_g3_1_a2_a6_protected_runner.py" \
  --review-repo "$REPO" \
  --approved-commit "$G31_CANDIDATE" \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --g3-0-report "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g1-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --original-local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --original-frozen-repo "$AUDIT/frozen_source_c7502a" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --reconstructed-models "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --out "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_18_cells_POINT_ONLY.json" \
  --mode point \
  --authorize-retrospective-a2-a6-old-outcome-access \
  --acknowledge-no-independent-60d-holdout \
  --acknowledge-no-realized-tradable-pnl \
  --trust-original-audited-pickles
```

This step genuinely deserializes original historical
model-target Pickles and computes original 18 point
estimates, which is why a **new explicit owner action
is mandatory**. It prints only aggregate q15/q25/q35
values, number of cells and original parity status;
the JSON remains local.

If `G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN`,
the full 10k-per-arm news/ticker uncertainty stage
is still pending. Reuse the exact same signed
scientific code/source and fixed settings for
`--mode full` but a **different output filename**.
Do not report point estimates as statistically
confirmed results.

## Remain blocked

A3 volatility and any use of retrospective July-5
FMP price values; A4 realized investable strategy
P&L/turnover/fees; A5 second historical ranker
and X1 independent matured non-overlapping 60d
holdout are **not authorized** or empirically
available through this A2/A6 approval.

**G3.1 outcome access still BLOCKED until the operator
voluntarily executes the explicit approval stage.**
