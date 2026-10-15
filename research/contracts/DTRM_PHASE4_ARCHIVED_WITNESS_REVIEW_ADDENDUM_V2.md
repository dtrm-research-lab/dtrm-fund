# Phase IV archived witness — reviewed real ZIP layout compatibility addendum v2

**2026-10-15, registered before code.** An outcome-blind local audit of 21 real archived `DTRM daily ranking` ZIPs from 2026-09-16 through 2026-10-14 has confirmed two legitimate internal entry roots:
- `ranking_news_evidence/` (20 archives);
- `Outputs/ranking_news_evidence/` (one archive, generated 2026-09-23, asOf 2026-09-22).

The original v0 verifier hardcodes the first layout. That would fail to recognize genuine older source witnesses and overstate gaps in recoverable Temporal State. **Do not weaken digest validation or accept arbitrary prefixes**. In each archive choose exactly one of these two fixed roots, reject both-present ambiguity, and require all six expected files (three JSON and three corresponding SHA receipts) under the chosen root. Mixed or unrecognized roots remain `INVALID_PHASE4_ARCHIVED_WITNESS`. The output may include a neutral `early_zip_layout` / `late_zip_layout` label if helpful, never provider text/URL/tickers.

Tests must build entirely synthetic archives in both layouts, check valid cross-layout comparisons under same family SHA, reject mixed/dual layouts, then reverify 4/4 CI and strictly false scientific permissions. No external/source/price/outcome/MM1/AWS I/O is added.

**Real offline exploratory evidence (not a confirmatory model outcome):** 21 archived complete ZIPs pass SHA receipts and manifest/candidate checks; their frozen `asOf` dates span 2026-09-15 through 2026-10-13. There are three distinct frozen family SHA values (4, 8 and 9 snapshots), with 18 adjacent same-family transitions. All 21 5d candidate exports hit the fixed 500 cap; 13/21 2d exports also hit the cap. Across both candidate windows, 36,440 unique (article ID, exact text SHA, ticker) **represented positive witnesses** were counted in the local private analysis. These selected outputs are neither an exhaustive source inventory nor first-seen timestamps; no negative/absence evidence may be inferred. Aggregate-only source audit inventory must keep original values private, and actual live-source/fit/financial gates remain BLOCKED.
