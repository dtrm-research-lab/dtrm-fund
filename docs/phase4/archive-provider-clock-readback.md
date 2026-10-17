# Phase IV — offline GitHub artifact clock readback (operator runbook)

This checks **metadata only**. It never opens archived ranking ZIP content, makes network requests or grants model-science permissions. The exact 21-source manifest comes from unmerged PR #41: `research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json`; Git blob `eb7c91b462ddb822835c20fc126492bfcae5eea0`. Save that file privately without reformatting its bytes. The verifier pins its Git blob SHA-1 and will reject edits.

### 1. Acquire provider responses (local operator, authenticated GitHub CLI)

Prerequisite: `gh auth status` confirms permission to see the private backend repository. Prepare a private directory outside both repos; do **not** commit these raw responses. Example using the 21 run IDs from the pinned manifest:

```bash
set -euo pipefail
BACKEND=tech-com-UA00001/theresistance-back
MANIFEST=/absolute/private/path/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json
PAGES=/absolute/private/path/provider-artifact-pages
mkdir -p "$PAGES"
python3 - "$MANIFEST" > /tmp/phase4-archive-run-ids.txt <<'PY'
import json,sys
with open(sys.argv[1],encoding="utf-8") as f:
    src=json.load(f)
for a in src["archives"]:
    print(a["run_id"])
PY
while IFS= read -r run; do
  gh api "repos/$BACKEND/actions/runs/$run/artifacts" > "$PAGES/$run.json"
done < /tmp/phase4-archive-run-ids.txt
```

The GitHub API may fail or return a partial page: such input remains **unconfirmed**. Do not manipulate the frozen values to force a pass.

### 2. Verify locally without network

From this feature checkout with Python 3.11 and project `PYTHONPATH=src`:

```bash
PYTHONPATH=src python3 -m dtrm.phase4.archive_provider_clock \
  --manifest "$MANIFEST" \
  --pages-dir "$PAGES" \
  --inspected-at-utc "$CHECKED_AT_UTC" \
  --output "/absolute/private/path/phase4-provider-clock-aggregate.json"
```

Set `CHECKED_AT_UTC` to the **actual** readback acquisition UTC time (not a fabricated value). The option is operator-reported, not independently notarized. A pass asserts only matching supplied metadata; it explicitly leaves `metadata_independently_authenticated=false`. Failure emits only a fixed redacted error and writes no assessment.

### 3. Preserve original ZIP bytes before provider expiry

First archived artifact ID `10424883893` (original archive SHA256 `ef382dd98efa3d71c4c71a32f48b40eb67ae28ca226cf6748517a6ce427320a9`) expires according to GitHub at **2026-10-16T00:41:51Z**. The other 20 have staggered deadlines. If private 21-archive backups are **already present and SHA-verified**, do not redownload. Otherwise use authenticated GitHub artifact downloads promptly, preserve **original ZIP bytes**, and compare every `zip_sha256` against the canonical manifest; no unzip/repack as a SHA equivalent. Never place source ZIPs or the provider raw pages in a public PR or issue.

The existing PR #41 canonical original ZIP integrity reducer and PR #42 pair verifier remain separate. PR #44's locally generated coverage-output reproducibility does not follow from this metadata-only pass.
