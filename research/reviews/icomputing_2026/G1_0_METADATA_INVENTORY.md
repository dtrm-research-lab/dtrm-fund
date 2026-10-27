# IC Major Revision — G1.0 Outcome-Blind Data Availability Gate

Date: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.
Prerequisite: G0.1–G0.3 operator-reported local replay PASS; no new temporal result claimed.

## What this checks
`ic_g1_inventory.py` scans **file names and metadata only** under operator-selected roots.
It does not open research files, deserialize Pickles, compute outcomes, load model weights,
read prediction values, change source snapshots or contact network services.

File name dates show acquisition/snapshot names only. They are not proof that
individual event dates, actual trading prices, or target maturities are available.
The report omits full local paths, retains only small filename samples and category counts.
Review the report before sharing if your filenames contain private identifying information.

## Run from DTRM_Lab
```bash
mkdir -p "$HOME/dtrm-ic-audit"
curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_inventory.py" \
  -o "$HOME/dtrm-ic-audit/ic_g1_inventory.py"
python3 -m py_compile "$HOME/dtrm-ic-audit/ic_g1_inventory.py"

python3 "$HOME/dtrm-ic-audit/ic_g1_inventory.py" \
  --root "$PWD/dtrm-fund" \
  --root "$PWD/theresistance-back" \
  --out "$HOME/dtrm-ic-audit/IC_G1_metadata_inventory.json"
```
Use absolute, existing directory names if not in DTRM_Lab. The user may add
`--root "$PWD/theresistance"` if needed. Do **not** scan private Phase IV
unless explicitly authorized and scientifically relevant.

## G1 sequence and gates
- G1.0 (this stage): obtain availability-only catalog; no values inspected.
- G1.1: locate immutable model binaries, frozen VALID quantile table and
  **new** news-event/price/feature inputs without reading holdout targets;
  capture SHA and data permissions.
- G1.2: write pre-registered candidate window and exact rule before access to
  outcomes, including how infeasibility/missing data is handled.
- G1.3: independently verify exact event and actually matched price intervals.
- G1.4: only after gate approval, predict with frozen models and evaluate on
  a disjoint matured holdout, maintaining original K, threshold and tie order.

## Scientific temporal constraint
The latest original V3 event was 2026-06-14. Nominal t+60 reaches about
2026-08-13; the configured price alignment tolerates up to 5 further days,
so **2026-08-19 UTC** is a conservative *candidate* beginning after the
potential original end. This is only a calendar bound; row-level matching is
required before proof of no overlap.

On 2026-10-27 the matured segment is short. A longer disjoint late-August to
mid-September cohort would improve reviewer relevance but its 60-day labels
and vendor prices may not mature until November, near the 2026-11-25 deadline.
Do not prematurely peek at outcomes or optimize the period based on results.
Ask the editor for an extension if rigorous validation needs it.

## Report interpretation
A file named `news_*_2026-08-xx.pkl` is metadata indicating a possibly relevant
snapshot, not evidence the news rows or training cutoff are compatible.
If the inventory finds no late-August data, this does not justify fabricating
an independent holdout or recycling prior exposed outcomes.
