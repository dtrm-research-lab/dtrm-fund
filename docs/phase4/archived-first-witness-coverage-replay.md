# Phase IV — replay of 21 real first-witness archived ZIPs (operator only)

This describes the **new portable implementation** `src/dtrm/phase4/archived_first_witness_coverage.py` and `research/experiments/run_phase4_archived_first_witness_coverage_v1.py`, *not* the older operator-local `phase4_archived_first_witness_coverage_v0.py` whose aggregate SHA is pinned in the exploratory report. The v1 serialization is different. The source protocol, fixed four UTC cutoffs and family isolation remain unchanged.

## Source inputs and security

Use the original 21 GitHub archive ZIP bytes that passed `PHASE4_ARCHIVE_PRESERVATION_PASS 21/21 original ZIP SHA256` on the user's Mac. File names are exact numeric artifact IDs with `.zip`; do not unzip/repack. The metadata-only manifest is included on this research branch at:

`research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json`

Its Git blob SHA must equal **`eb7c91b462ddb822835c20fc126492bfcae5eea0`**, identical to unmerged PR #41. Never upload raw ZIPs, text, headlines, provider IDs, symbols, scores or private URLs into public GitHub or chat.

## Local execution

From a checkout of PR #44, and with Python 3.11:

```bash
set -euo pipefail
export PYTHONPATH=src
python3 research/experiments/run_phase4_archived_first_witness_coverage_v1.py \
  --manifest research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json \
  --archive-dir "$HOME/Phase4-private-archive-backup" \
  --output "$HOME/Phase4-private-archive-backup/phase4_coverage_v1_private_aggregate.json"
```

The output is created once (fail on existing path) and contains **ONLY aggregate numbers**: per-family SHA, count of snapshots, distinct represented triples, total archive appearances and repeat appearances; and at each of the four UTC cutoffs the same counts per family and sums over families. The file is not the original old report SHA. Failure returns only `REPRODUCTION_NOT_CONFIRMED` and writes no final output. If a prior verified output exists, choose a **new** local filename, never overwrite or loosen the source metadata.

Expected on real data only, **not verified by CI**: `PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED`; 21 original captures, 3 families, global union 36,440, family-summed 38,968, and four cutoff sums 6,783 / 21,350 / 33,994 / 38,968. The new operator run is necessary to demonstrate actual *per-family cutoff appearance counts* and reproducibility; do not write assumed counts into the public report before it occurs.

## Share only a safe aggregate summary

On success, the following prints only the family SHA and the approved integer counts; no private link tuple is printed:

```bash
python3 - "$HOME/Phase4-private-archive-backup/phase4_coverage_v1_private_aggregate.json" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
print("reproduction_status:",r["reproduction_status"])
print("global_union:",r["globally_deduplicated_positive_representations"])
print("family_summed_distinct:",r["family_summed_distinct_positive"])
for c in r["cutoffs"]:
    print("cutoff_utc:",c["cutoff_utc"],
          "captures:",c["admitted_snapshots"],
          "sum_distinct:",c["family_summed_distinct_positive"],
          "sum_appearances:",c["family_summed_capture_appearances"])
    for f in c["families"]:
        print("  family:",f["family_sha256"][:12],
              "captures:",f["admitted_snapshots"],
              "distinct:",f["distinct_positive_representations"],
              "appearances:",f["captured_positive_appearances"],
              "repeated:",f["repeat_positive_appearances"])
PY
```

**Interpretation:** captures identify selected positive witness presence no later than an archive time, NOT first provider collection, original mapping creation or continuous history. Absence from selected/capped exports is UNKNOWN; old `asOf` cannot be used as an archive-created clock. Does not establish 60-day L, source rights, price vintage, or eligibility to train/evaluate C0/S/B/T/O. All scientific gates remain `BLOCKED_SOURCE_AUDIT`.
