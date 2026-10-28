# G3.2 A3 — original price numeric quality gate, before any risk/outcome benchmark

**Manuscript:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Reviewer topic:** R1-04, comparison with conventional trailing realized volatility.  
**Current status:** SOURCE CODE PREPARED; local numeric PRICE gate **not yet run**.  
**Source scope:** unchanged frozen G2 experimental design, G3.1 A2/A6 complete and audited.

## Why this step is necessary and distinct

A2/A6 was completed on three original already-consumed cohorts:
18/18 point cells and 36/36 news/ticker CI blocks passed a
strict aggregate report audit. However only V3's two
distinct policy settings (original q25/K10 and q35/K10)
had nominal positive mean-delta intervals under
**both** news and ticker clusterings. Those
18 cells cannot answer the reviewer question
whether a conventional pre-event trailing
volatility filter improves decision quality
relative to original P10 on a common sample.

A3 does NOT imply more scientific confirmation.
This is a different conventional-comparator
question, secondary **POST_OUTCOME_EXPLORATORY**,
with original May–June model outcomes already known.

**Already established in G2 and NOT to be re-run:**
- G2.9 original historical `2026-07-05` cache:
  174 files, 173 stocks plus SPY, 174 SHA-hashed.
  Report SHA
  `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`.
- G2.10 original price source schema/bar dates:
  174 original July-5 files, provider-vintage UNVERIFIED.
  SHA
  `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`.
- G2.12 per-event, strictly prior 61 dated close bars:
  **47,596 / 47,596** old V2/V3/V4 pairs
  with price DATE coverage. SHA
  `e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`.
- G2.13 original V0 VALID rows:
  **19,880 / 19,880** rows, 167 tickers,
  similarly 61 earlier source bar dates.
  SHA
  `e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`.
- Frozen G2.17 A3 PRIMARY method: exactly
  the last 61 distinct daily closes strictly
  prior to event UTC day, 60 simple close-to-close
  returns and `std(ddof=1)`. NO 40-return fallback,
  event-day data, imputation, corporate-action
  repair or winsorizing. Invalid selected close
  excludes pair from all three later A3 arms.

These earlier gates checked **DATED-BAR COVERAGE,
NOT numeric close validity**, vendor acquisition
timestamps, or point-in-time split adjustments.

## First bounded implementation now prepared

`ic_g3_2_a3_numeric_source_quality_gate.py`
plus `test_ic_g3_2_a3_numeric_source_quality_gate.py`.

Inputs: the five original SHA-locked G2.6/9/10/12/13
local evidence JSONs; original SHA-locked
`legacy_model_rows_2026-05-01.pkl` and V2/V3/V4
old SIGNAL files, and exact 174 saved July-5
price archives (no forward target files).
No selected stock/news identifier or numeric
close/volatility source vector is serialized.

The reader requires explicit human permission for
**read-only trusted local original Pickle
deserialization and numeric price quality**.
Pickle can execute code even if it is a local file:
trust only previously audited original sources.
All original cache files and old model/signal
files are SHA-checked BEFORE any Pickle is opened.
Its own gate, pure core and synthetic tests must
match a single immutable Git commit supplied
in `--code-commit`.

The output contains aggregates by V0 VALID
and V2/V3/V4, numerical risk eligibility
counts, failure reasons, original provenance
report SHAs and the exact prospective-vintage
qualification. No risk cutoff, baseline/P10/risk
comparison, ranker outcome or bootstrap is
performed. Even a 66,476/66,476 PASS leaves
original point-in-time vendor-vintage and
corporate-action revision authenticity OPEN.

## Step 1: 34 synthetic/static checks (no prices loaded)

The 22 established frozen G2 mathematical
tests and 12 new G3.2 A3 source gate tests
must ALL PASS. The latter are **prepared but
NOT YET run on original Mac**.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
mkdir -p "$AUDIT/g1-reconstruction"
git -C "$REPO" fetch origin research/ic-major-revision-2026
A3_COMMIT="$(git -C "$REPO" rev-parse FETCH_HEAD)"
ROOT="research/reviews/icomputing_2026"

for file in \
  ic_g2_g3_exploratory_core.py \
  test_ic_g2_g3_exploratory_core.py \
  ic_g3_2_a3_numeric_source_quality_gate.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py
do
  git -C "$REPO" show "$A3_COMMIT:$ROOT/$file" > "$AUDIT/$file"
done

cd "$AUDIT"
python3 -m unittest \
  test_ic_g2_g3_exploratory_core.py \
  test_ic_g3_2_a3_numeric_source_quality_gate.py -v

printf '%s\n' "$A3_COMMIT" > "$AUDIT/g1-reconstruction/IC_G3_2_A3_QUALITY_CODE_COMMIT.txt"
echo "A3_SOURCE_CODE_COMMIT=$A3_COMMIT"
BASH
```

**Expected, not yet demonstrated:** `Ran 34 tests — OK`.

## Step 2: explicit price-numeric-only source authorization

The following is a new decision to allow reading
the archived July-5 original price CLOSE arrays
for **source quality only**, under the science
limits above. It does NOT authorize opening
V2/V3/V4 forward target Pickles or doing any
A3 financial performance comparison.

Run only AFTER Step 1 passes and you agree
that the later saved snapshot is not proven
contemporaneous at every old event date.

```bash
bash <<'BASH'
set -euo pipefail
AUDIT="$HOME/dtrm-ic-audit"
REPO="$HOME/Desktop/DTRM_Lab/dtrm-fund"
A3_COMMIT="$(cat "$AUDIT/g1-reconstruction/IC_G3_2_A3_QUALITY_CODE_COMMIT.txt")"
OUT="$AUDIT/g1-reconstruction/IC_G3_2_A3_NUMERIC_SOURCE_QUALITY_ONLY.json"

test ! -e "$OUT"
python3 "$AUDIT/ic_g3_2_a3_numeric_source_quality_gate.py" \
  --review-repo "$REPO" \
  --code-commit "$A3_COMMIT" \
  --original-price-cache "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle" \
  --original-local-data "$REPO/research/local_data" \
  --g2-6-binding "$AUDIT/g1-reconstruction/IC_G2_6_validation_source_binding.json" \
  --g2-9-report "$AUDIT/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json" \
  --g2-10-report "$AUDIT/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json" \
  --g2-12-report "$AUDIT/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json" \
  --g2-13-report "$AUDIT/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json" \
  --out "$OUT" \
  --authorize-a3-price-numeric-source-quality-only \
  --trust-original-audited-pickles \
  --acknowledge-price-provider-vintage-unverified

shasum -a 256 "$OUT"
BASH
```

**Possible outcomes:**
- `G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED`:
  all 19,880 validation and 47,596 old event pair
  windows have 60 usable strictly prior returns
  from later, vintage-unverified original snapshots.
- `G3_2_A3_NUMERIC_CLOSE_SOURCE_PARTIAL_COMMON_SAMPLE_REQUIRED_VINTAGE_UNVERIFIED`:
  at least one numerical close invalid or source
  row excluded; detailed aggregated reasons
  are saved. Exit code 2 is a legitimate
  negative source-result, not a model failure.
  **Preserve the report**; use frozen common-case
  policy for a possible later comparator,
  without changing lookback or excluding
  other unfavorable observations.
- `G3.2 A3 SOURCE QUALITY HALTED`:
  source SHA/schema/lineage mismatch or missing
  archived input, exit 3, no authorized
  performance result. Preserve old reports
  and do not loosen old source checks.

## Next stages, not yet implemented or authorized

If source numeric quality proves feasible:
(1) reconstruct validation-only original P10
eligibility/matched weighted volatility cutoff
on the exact V0 COMMON eligible subset,
(2) separately peer-review G3.2 A3
baseline vs frozen P10 vs conventional
volatility policy on identical old cohort
common paired observations and original
K=floor(.10 × common N), and
(3) only then use original previously-consumed
target labels with explicit new scoped
operator consent and fixed news/ticker
10k bootstrap; report all negative,
infeasible and source-vintage limitations.

**A3 cannot be published as an authenticated
real-time ex-ante price-risk comparator while
original price vendor acquisition vintage and
corporate-action adjustments remain unverified.**
It can at best be a carefully labeled
retrospective date-restricted control using
historically dated but later-acquired data.
