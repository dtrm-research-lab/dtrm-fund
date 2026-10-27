# IC G0 — Local data recovery runbook

Created 2026-10-27. Manuscript ICOMPUTING-D-26-01069.

## Preconditions
- Run on the Mac with the original authorized research datasets, not inside public CI.
- Only read local files you own / are authorized to inspect. Do not upload licensed FMP data, raw .pkl/.npy files, credentials or vendor market snapshots.
- Review the source of `ic_g0_discover.py` before running. Standard library only; no pip needed.
- SHA checks never unpickle or execute any data.

## One-command workflow
```bash
mkdir -p "$HOME/dtrm-ic-audit"

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g0_discover.py" \
  -o "$HOME/dtrm-ic-audit/ic_g0_discover.py"

python3 "$HOME/dtrm-ic-audit/ic_g0_discover.py" \
  --search-root "$HOME" \
  --out "$HOME/dtrm-ic-audit/IC_G0_discovery_manifest.json"
```

Submit **only** the small JSON manifest for remote review. The manifest omits local file paths. Do not share the recovered data.

If the first scan is incomplete, use these targeted approaches:
```bash
mdfind -name probabilistic_v2_holdout_signals_2026-06-10.pkl
mdfind -name probabilistic_v1_holdout_features_2026-06-06.npy
```
Spotlight may not index all folders. If originals are on a dedicated external drive or iCloud directory, rerun with explicit `--search-root "/Volumes/DriveName"` or `--search-root "$HOME/Library/Mobile Documents"` (quote paths that contain spaces). Omit directories you do not wish to inspect.

## Interpretation
- `PRESENCE_AND_ANCHOR_HASHES_OK_NOT_REPRODUCED`: named data present, all five original V1 SHA anchors match. It does **not** prove that V2-V4 results have been numerically reproduced or data chronology is clean.
- `NEEDS_FOLLOW_UP`: at least one named file missing, duplicated or hash-invalid.
- A hash mismatch is a stop; do not overwrite originals.
- Identically named copies with different hashes must be reconciled against acquisition logs.

## After discovery (separate controlled stage)
1. On the trusted local computer, inventory model weights, source snapshot identifiers, validated code dependencies and vendor price coverage. Preserve original copies.
2. Check file schemas under a security-controlled execution environment; never unpickle an untrusted download.
3. Reproduce the frozen V2/V3/V4 numbers independently; compare to historical contracts.
4. Pre-register a truly uninspected new window after mapping actual 60-day realized intervals.
5. Run risk filters and cost/abstention checks only after G1 gates.

## Temporal caution
- V3 latest signal: 2026-06-14.
- Nominal t+60 endpoint: around 2026-08-13; configured tolerance permits price matches up to approximately 2026-08-18.
- An August **19 or later** starting event window is a conservative *calendar candidate* for disjoint forward intervals; actual market-price timestamps must still be checked.
- As of 2026-10-27, allowing 60+5 calendar days to maturity constrains a conservative fully matured start-date window to approximately **2026-08-19 through 2026-08-23**.
- These dates are not pre-approved holdouts. Existing investigator exposure, original train/test cutoffs, availability and sample adequacy must also pass.
