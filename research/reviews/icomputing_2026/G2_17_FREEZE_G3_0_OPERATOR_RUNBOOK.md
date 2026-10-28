# G2.17 — Release candidate gate, operator signoff, and G3.0 ONLY

Case: ICOMPUTING-D-26-01069, 2026-10-28.
Deadline: 2026-11-25. This file describes an *unexecuted* operator workflow.
It never authorizes G3.1 original-target/price-result analyses.
All new comparisons remain POST_OUTCOME_EXPLORATORY.

## Operator-reported previous G2.16 state

The previous source-control script ran **29 tests PASS**
and traced **22** reviewer/editor requirements, with
original core source SHA256
`b5dd4de494942b617354ab448c90ec6f9ff32c9ae1861308a4f9bd50a2023090`
and scientific spec SHA256
`f2d2c11fe41a27d08600d9a71fad29e25a57e8dd9413ec814d5a34775da52ddb`.

**DO NOT REUSE THAT PASS**: the protected G3.0
original P10 evidence check and operator approval
were strengthened *after* that 29-case run.
The current 22-method + nine G3.0 +
five freeze-builder protection checks require
**36 tests**, and the G2.16 report must
pin these CURRENT script bytes and the
reconciled reviewer traceability candidate.

Original G2.9/G2.10/G2.12/G2.13 local reports
retain previously operator-computed SHA256.
No re-deserialization is required for G2.17.

## 1. Candidate scientific freeze decisions

See:
- `G2_17_FINAL_PROTOCOL_FREEZE_CANDIDATE.md`;
- `G2_17_REVIEWER_TRACEABILITY_FREEZE_CANDIDATE.json`;
- `G2_16_EXPLORATORY_SCOPE_CANDIDATE.json`.

**Frozen original rule:** quantile P10, calibrated
offset -0.06494169682264328; validation weighted
q25 threshold -0.16665692627429962;
ranker iteration 10, quantile iteration 18,
K=floor(0.10N). No source alteration.
A2 weighted q15/25/35, A3 exactly 60
past-only 60 daily returns and matched
common-case comparison, A6 5/10/15% K
are secondary retrospective analyses and are explicitly
**POST_OUTCOME_EXPLORATORY**, never prospective validation.

The retrospective July-5 FMP snapshot is
NOT point-in-time acquisition/adjustment
authenticated for earlier historic signal
dates. Original V2 and V4 ticker-cluster
95% intervals cross zero and V2/V3 forward
60-day outcomes overlap. G1 unverified
new nonoverlapping holdout and alternate
historical model are NOT_EXECUTABLE.
Historic excess-beta is NOT a profit ledger.

**Formal approval at this gate authorizes
only G3.0 original model/old signal parity,**
no G3.1 old financial outcome access.

## 2. Operator step A — fetch exact Git release candidate and rerun 36 tests

Use local Git review checkout at
`$HOME/Desktop/DTRM_Lab/dtrm-fund`.
This is not the separately preserved
`$AUDIT/frozen_source_c7502a`, which must
stay pinned to the original historic code.

In zsh, lines beginning with `#` may
print `command not found: #` unless
`setopt interactivecomments`. The
commands here contain no inline comments.

```bash
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"

git -C "$REPO" fetch origin research/ic-major-revision-2026
FROZEN_CANDIDATE_COMMIT="$(git -C "$REPO" rev-parse FETCH_HEAD)"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/$FROZEN_CANDIDATE_COMMIT/research/reviews/icomputing_2026"

for file in G2_16_EXPLORATORY_SCOPE_CANDIDATE.json G2_17_REVIEWER_TRACEABILITY_FREEZE_CANDIDATE.json G2_17_FINAL_PROTOCOL_FREEZE_CANDIDATE.md ic_g2_g3_exploratory_core.py test_ic_g2_g3_exploratory_core.py ic_g3_0_original_model_row_parity.py test_ic_g3_0_protection.py ic_g2_17_operator_freeze.py test_ic_g2_17_freeze_builder_protection.py ic_g2_freeze_preflight.py ic_g2_16_scientific_freeze_preflight.py
do
  curl -fsSL "$BASE/$file" -o "$AUDIT/$file" || exit 1
done

python3 "$AUDIT/ic_g2_16_scientific_freeze_preflight.py" \
  --spec "$AUDIT/G2_16_EXPLORATORY_SCOPE_CANDIDATE.json" \
  --engine "$AUDIT/ic_g2_g3_exploratory_core.py" \
  --tests "$AUDIT/test_ic_g2_g3_exploratory_core.py" \
  --g3-0-source "$AUDIT/ic_g3_0_original_model_row_parity.py" \
  --g3-0-tests "$AUDIT/test_ic_g3_0_protection.py" \
  --freeze-builder "$AUDIT/ic_g2_17_operator_freeze.py" \
  --freeze-builder-tests "$AUDIT/test_ic_g2_17_freeze_builder_protection.py" \
  --reviewer-matrix "$AUDIT/G2_17_REVIEWER_TRACEABILITY_FREEZE_CANDIDATE.json" \
  --g2-9 "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10 "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12 "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13 "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --frozen-repo "$AUDIT/frozen_source_c7502a" \
  --out "$AUDIT/g1-reconstruction/IC_G2_17_latest_36_test_science_gate.json"
```

**Expected if the CURRENT tests actually pass:**
`G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING`
plus `Synthetic tests PASS: 36`.
Old 29-case evidence remains in its
own original JSON, not overwritten.
If tests HALT, do not approve;
preserve failure output and fix source
before signing. Do not invent a PASS.

## 3. Operator step B — explicit scientific owner attestation (ONLY after step A PASS)

Read the final scientific protocol and
the no-independent-holdout/vintage/ticker
cluster limitations in section 1 first.

The operator must explicitly select
three independent command-line approval
flags. The freeze-builder verifies
the **actual Git commit contains exactly
the scripts, methodology and reviewer
traceability recorded as passing the
latest 36-test report**, runs the complete
old 22-item fail-closed reviewer gate
on the finalized local matrix, and writes
the operator-attested audit manifest.

This is an operator CLI approval, **not
a cryptographic digital signature**.

```bash
python3 "$AUDIT/ic_g2_17_operator_freeze.py" \
  --review-branch-repo "$REPO" \
  --freeze-commit "$FROZEN_CANDIDATE_COMMIT" \
  --latest-g2-16-pass "$AUDIT/g1-reconstruction/IC_G2_17_latest_36_test_science_gate.json" \
  --inputs-dir "$AUDIT" \
  --matrix-out "$AUDIT/g1-reconstruction/IC_G2_17_approved_reviewer_matrix.json" \
  --editor-review-gate-out "$AUDIT/g1-reconstruction/IC_G2_17_editor_reviewer_freeze_check.json" \
  --out "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --approve-g3-0-source-parity-only \
  --acknowledge-retrospective-data-vintage-risk \
  --acknowledge-no-independent-60day-holdout
```

**If and only if** this returns
`G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY`,
the operator has attested that protocol
and approval are complete for one protected
G3.0 original source/model parity run.
The manifest contains the exact
G2.16 local report SHA and Git commit.

## 4. Explicit G3.0 execution separate from freeze

The operator can next run the SHA-gated
`ic_g3_0_original_model_row_parity.py`.
It opens only trusted original V2/V3
signal Pickles and NPY feature rows,
plus SHA-pinned reconstructed candidate
booster binaries; the original target
labels and financial price/return
data remain CLOSED.

A G3.0 result must differentiate
baseline numerical parity, P10 veto-mask
parity and independent saved numeric P10
per-row reference availability. If such
numeric references are missing, the
diagnostic will not falsely assert
full original P10 numerical parity,
and G3.1 stays blocked.

Use exact protected source from
`FROZEN_CANDIDATE_COMMIT`, not an
uncontrolled later branch revision.

```bash
python3 "$AUDIT/ic_g3_0_original_model_row_parity.py" \
  --g2-16-synthetic-gate "$AUDIT/g1-reconstruction/IC_G2_17_latest_36_test_science_gate.json" \
  --g2-freeze-approval "$AUDIT/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json" \
  --g1-sealed-dossier "$AUDIT/g1-reconstruction/IC_G1_2_historical_dossier.json" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --models-dir "$AUDIT/g1-reconstruction/reconstructed_UNAPPROVED" \
  --original-local-data "$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data" \
  --out "$AUDIT/g1-reconstruction/IC_G3_0_original_v2_v3_model_row_parity.json" \
  --trust-original-pickles
```

If the data folder or model folder differs,
derive its exact path from prior G1 runbook
and the original source/commit, not a guess.
Do not modify any original source file
to make the check pass. Explicit trusted
original-Pickle consent is required.

**G3.1 A2/A3/A6 remains NOT AUTHORIZED
and must receive a separate, source-verified,
author-signed approval after G3.0 and
scientific source-vintage interpretation.**
