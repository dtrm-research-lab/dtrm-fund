# G2 scientific freeze — operator-attested PASS; G3.0 source-only now authorized

**Editorial case:** ICOMPUTING-D-26-01069
**Operator event:** 2026-10-28
**Frozen original reference:** `c7502a690162459cdfb3413573e3133c42efb126`
**Scientific review protocol immutable commit:** `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`
**Status:** `G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY`

## Exact operator-reported evidence

Operator ran the SHA- and Git-verified
`ic_g2_17_operator_freeze.py` with **all three explicit
scientific attestation flags** after a full
`G2_16_SYNTHETIC_AND_SOURCE_GATE_PASS_G3_0_PARITY_AND_MANUAL_FREEZE_PENDING`
of **36/36** source/synthetic and security checks
against **22/22** editor/reviewer traceability anchors.

Console output included:
- `G2.17: G2_FULL_PROTOCOL_FROZEN_AUTHORIZE_G3_0_SOURCE_PARITY_ONLY`
- `G2.16 latest tests: 36 reviewer/editor requirements: 22`
- `Frozen Git commit: 3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0`
- `Operator source-gate report SHA256:
  5232f42bd84e8b9a16d32d906b638bfd9f0f4a35234fa8440bc1f708d32f2946`
- `Operator approval manifest:
  /Users/me/dtrm-ic-audit/g1-reconstruction/IC_G2_17_operator_scientific_freeze_approval.json`
- `G3.0 original V2/V3 model-signal parity: AUTHORIZED; NOT EXECUTED.`
- `G3.1 old forward targets, returns or profits: BLOCKED.`

**Source authenticity:** evidence is the operator's
terminal transcript from private local original files.
No local approval-manifest bytes were uploaded to
GitHub or independently verified by this connector.
The manifest is operator-attested by explicit CLI
action, **not a cryptographically signed identity proof**.

G2.9/G2.10/G2.12/G2.13 historic source
reports remain SHA-anchored. Latest G2.16
scientific core digest
`b5dd4de494942b617354ab448c90ec6f9ff32c9ae1861308a4f9bd50a2023090`
and spec digest
`f2d2c11fe41a27d08600d9a71fad29e25a57e8dd9413ec814d5a34775da52ddb`
were both reported with successful tests.

## Authorized next action — G3.0 ONLY

Retrieve the EXACT original approved model row-parity
source from `3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0` or reuse the locally downloaded
file that matches this SHA. The fixed, protected
runner is:
`research/reviews/icomputing_2026/ic_g3_0_original_model_row_parity.py`.

Trusted original local input paths supported by
pinned G1/G2 audit runbooks:
- G1 sealed dossier:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G1_2_historical_dossier.json`
- Original G2.6 binding:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_6_validation_source_binding.json`
- Reconstructed but otherwise UNAPPROVED original
  booster candidates:
  `$HOME/dtrm-ic-audit/g1-reconstruction/reconstructed_UNAPPROVED`
- SHA-bound original V2/V3 feature and signal files:
  `$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data`.

### Exact operator command

```bash
AUDIT="$HOME/dtrm-ic-audit"
FROZEN_COMMIT="3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0"
BASE="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/$FROZEN_COMMIT/research/reviews/icomputing_2026"
curl -fsSL "$BASE/ic_g3_0_original_model_row_parity.py" -o "$AUDIT/ic_g3_0_original_model_row_parity.py"
python3 -m py_compile "$AUDIT/ic_g3_0_original_model_row_parity.py"
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

**Trusted Pickle caveat:** the original saved feature
`.npy` is loaded with `allow_pickle=False`, but
the previously SHA-verified original signal `.pkl`
files still require deserialization by Pandas; this
may execute malicious code if the files were
externally modified or are untrusted. Use only
previously audited local source files.

G3.0 computes original model **prediction/
Boolean veto-mask** parity for V2/V3 and
checks any explicitly named original numeric
P10 reference fields. It never reads original
financial forward target/result source files
for risk/return/P&L estimates. It must not
misrepresent mask equality as independently
authenticated numerical P10 reference equality
if a source column is absent. Original reconstructed
boosters are still not independently original
serialized pre-event model weights.

## Hard block after G3.0

Even if G3.0 reports strict
`G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED`,
additional user/scientific approval and a
versioned, audited source-checked G3.1 reader
are mandatory **before** any A2/A3/A6 new
post-outcome exploratory analysis of
forward beta returns.

The independent untouched 60-day holdout,
original FMP vintage and original V2/V4
ticker-cluster CI caveats remain unresolved.

**DO NOT EXECUTE G3.1 HERE.**
