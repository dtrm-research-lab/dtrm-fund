# Phase IV — replay of 21 real first-witness archived ZIPs (operator only)

This describes the **new portable implementation** `src/dtrm/phase4/archived_first_witness_coverage.py` and `research/experiments/run_phase4_archived_first_witness_coverage_v1.py`, *not* the older operator-local `phase4_archived_first_witness_coverage_v0.py` whose aggregate SHA is pinned in the exploratory report. The v1 serialization is different. The source protocol, fixed four UTC cutoffs and family isolation remain unchanged.

## Source inputs and security

Use the original 21 GitHub archive ZIP bytes that passed `PHASE4_ARCHIVE_PRESERVATION_PASS 21/21 original ZIP SHA256` on the user's Mac. File names are exact numeric artifact IDs with `.zip`; do not unzip/repack. The metadata-only manifest is included on this research branch at:

`research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json`

Its Git blob SHA must equal **`eb7c91b462ddb822835c20fc126492bfcae5eea0`**, identical to unmerged PR #41. Never upload raw ZIPs, text, headlines, provider IDs, symbols, scores or private URLs into public GitHub or chat.

## Python 3.11 installations without `_lzma`

Some `pyenv` Python builds on macOS lack the optional native `_lzma` extension. The v2 compatibility addendum treats that as **optional for DEFLATE ZIPs**: the module imports without it, but any archive member actually requiring LZMA still yields only `REPRODUCTION_NOT_CONFIRMED`, never partial counts. No Python reinstall and no archive redownload is required if the original ZIPs use supported compression. Refresh the existing local checkout with `git pull --ff-only` before rerunning. An import failure from an older checkout does not imply corrupted original archives.

## Local execution

From a checkout of PR #44, and with Python 3.11:

```bash
set -euo pipefail
export PYTHONPATH=src
REPORT="$HOME/Phase4-private-archive-backup/phase4_coverage_recheck_$(date -u +%Y%m%dT%H%M%SZ).json"
python3 research/experiments/run_phase4_archived_first_witness_coverage_v1.py \
  --manifest research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json \
  --archive-dir "$HOME/Phase4-private-archive-backup" \
  --output "$REPORT"
shasum -a 256 "$REPORT"
```

The output is created once (fail on existing path) and contains **ONLY aggregate numbers**: per-family SHA, count of snapshots, distinct represented triples, total archive appearances and repeat appearances; and at each of the four UTC cutoffs the same counts per family and sums over families. The file is not the original old report SHA. Failure returns only `REPRODUCTION_NOT_CONFIRMED` and writes no final output. If a prior verified output exists, choose a **new** local filename, never overwrite or loosen the source metadata.

Operator evidence **already verified on Mac at exact head `ee0b9e0b3a31df70e6f3227cfada8ca0d0d9e44d`**: `PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED`, 21 original captures, 3 families, global selected union 36,440, family-summed 38,968; four cutoff sums 6,783 / 21,350 / 33,994 / 38,968. This is an operator-reported local PASS, **not a CI run against private inputs**. New future repetitions must use unique output filenames and explicitly record their SHA256.

## Full-protocol metrics and reproducibility after the 21-ZIP first replay

The real archived coverage v1 **already replayed successfully** on the operator's Mac at prior head `03a119f48f477792c2d75c76495ebe6bf2da9097`: 21 ZIPs, global selected positive union 36,440, cutoff counts 6,783/21,350/33,994/38,968, and all per-family appearances/repeats reproduced. The aggregate-only, user-supplied terminal excerpt is committed at `research/reports/DTRM_PHASE4_OPERATOR_FIRST_WITNESS_CUTOFF_EXCERPT_20261015.json`; it is explicitly NOT the original locally written v1 JSON bytes or a cryptographic receipt of that output.

A later **protocol-completeness** implementation amendment now additionally emits every capture's `first_witness_within_family`, `repeat_witness_within_family`, `cumulative_distinct_family_witnesses`, `positive_representations_in_capture`, `capped_2d`, `capped_5d`, and `elapsed_days_since_first_family_artifact` (as well as old exact scientific gate keys and manifest SHA256). The per-capture details are safe aggregate counts/known capture times only; they must never include article IDs, tickers, news text, URLs or link hashes. On the real original 21 ZIPs the locked cap totals are **13** capped 2d and **21** capped 5d; the full-protocol output was **reproduced locally on the amended head `ee0b9e0`**, with 21 capture records and both registered negative-history/first-seen flags `false`. Operator-reported private output SHA256: `3324efbb6cb8540b74c89af0c633b15656fd04260058b1ebed217b1c6484b1cb`. This digest cannot be independently checked without the private bytes and does not authenticate external historical availability.

The original v1 output and full-protocol output already exist on the operator's Mac; the example above therefore chooses a new time-stamped path. Reusing the old path intentionally fails closed. Record each new output's SHA256 locally and share only digests and redacted aggregate counters; never upload the ZIPs.

## Share only a safe aggregate summary

On success, the following prints only the family SHA and the approved integer counts; no private link tuple is printed:

```bash
python3 - "${REPORT:-$HOME/Phase4-private-archive-backup/phase4_coverage_full_protocol_20261015.json}" <<'PY'
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
