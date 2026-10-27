# G0 — Operator-reported recovery and deterministic historical replay

Date: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.

## Recovery: OPERATOR-REPORTED PASS (not yet independently inspected manifest)
Local terminal output:
```
Required files located: 10/10
Hash integrity errors: 0; duplicates: 0
Status: PRESENCE_AND_ANCHOR_HASHES_OK_NOT_REPRODUCED
```
Interpretation: five V1 files have historical SHA256 anchors and their hashes matched;
five additional files were found and hashed but lack independent historical anchors.
No raw data or complete path inventory was transmitted. G0 *historical replay* remains open.

## Point replay — approved procedure

`ic_g0_reproduce.py` performs:
- second read-only discovery of the six selection/target pickles used by V2–V4;
- same-bytes check against the operator's prior locally generated discovery JSON;
- historical anchored SHA recheck where available;
- schema and one-to-one joins (news_id, ticker), timestamp equality and finite values;
- reproduce Top-K, P10 pass count, baseline/candidate means and hit rates;
- compare all counts/dates/numerical results with frozen historical contracts, tolerance 1e-12;
- write only aggregate statistics and PASS/FAIL checks to path-redacted JSON.

It DOES NOT generate new research findings, fit models, rederive targets from raw prices,
prove model training reproducibility, or rerun 10,000 bootstrap replicates.

**Pickle safety**: pandas.read_pickle executes Python pickle loading and therefore must be
used only with the operator's trusted original local files. The CLI requires
`--trust-local-pickles` explicitly. This is distinct from G0 discovery, which only hashes files.

Run on the trusted Mac:
```bash
mkdir -p "$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g0_reproduce.py" \
  -o "$HOME/dtrm-ic-audit/ic_g0_reproduce.py"

python3 -m py_compile "$HOME/dtrm-ic-audit/ic_g0_reproduce.py"

python3 "$HOME/dtrm-ic-audit/ic_g0_reproduce.py" \
  --search-root "$HOME" \
  --discovery-manifest "$HOME/dtrm-ic-audit/IC_G0_discovery_manifest.json" \
  --out "$HOME/dtrm-ic-audit/IC_G0_point_replay.json" \
  --trust-local-pickles
```

Do not upload original .pkl or .npy files. Return only G0 JSON summary.

## Gate interpretation

If all three point estimates pass: mark `POINT_REPLAY_PASS_NOT_RAW_REPRODUCED`.
This is **not** a full scientific validation: raw target reconstruction, model inference,
dataset chronology, CI replication and independent testing are separate work.

If any failure: stop and diagnose prior manifests, source schema, hash provenance,
dependencies and earlier local analysis outputs before permitting a new test.

Next: G0 bootstrap replication and G1 maturity/untouched-holdout provenance audit.
