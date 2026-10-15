# Phase IV — positive archived first-witness Time State coverage (exploratory)

**Analysis performed 2026-10-15 after the source-only computation protocol was committed as `8487814faa20655b3b88ab2db02517e589ebe792`.** This is an *outcome-blind exploratory* diagnostic of actual private archive ZIP content, not a registered causal effect or a real-time complete source history. No company symbols, articles, provider URLs, source text, financial prices or target returns have been recorded here.

## Immutable input and local result

The previously recorded 21 ZIP original SHA identities and GitHub artifact-created UTC values are in PR #41's public metadata-only canonical manifest, **Git blob SHA-1 `eb7c91b462ddb822835c20fc126492bfcae5eea0`**. The archive ZIPs are held privately, not copied to this repository. Local read-only code `phase4_archived_first_witness_coverage_v0.py` loaded the earlier safe aggregate source inventory and found all 21 original ZIPs by SHA256 rather than by assumed filenames. It verified each ZIP SHA, internal frozen manifest + digest receipt, both 2d and 5d candidate JSON + receipts, each candidate digest as pinned by manifest, exact family/source digest and selected candidate item counts. The local **aggregate-only** report `phase4_archived_first_witness_coverage_20261015.json` has SHA256 **`b3f3b391db6ab143b259b83e9a27f70ac910fa6f3febb0a4e008017c10862940`**; the local provenance input inventory is the prior aggregate-only `phase4_archived_time_state_inventory_20261015.json`. These paths are local, not repo-held and do NOT constitute execution of PR #41's exact canonical `derive_phase4_archived_time_state_inventory_v0.py` CLI on all real ZIPs.

**Analysis is only positive archival representation**. Let the private key e = (provider article ID, exact news-vintage text SHA256, ticker symbol), and let a_i be the GitHub artifact-created UTC time. Within each exact frozen family digest, for snapshot i compute observed selected e in the union of the sealed 2d and 5d candidate lists, cumulative distinct, *first_in_available_archives_within_family* (current set minus cumulative earlier positive archives), and repeated selected appearance (current intersection previous positive union). `first_in_available_archives` is NOT event first-seen in FMP/Mongo and NOT when the source link was created. Every omission, including in an uncapped 2d export, remains unknown because data were URL- and candidate-selected. Full family SHA is used as a hard partition; no cross-family model-policy equivalence is assumed.

## Actual grouped positive archive coverage

| Frozen source/model family digest prefix | Snapshots | Market asOf span | Family-specific distinct positive representations | Repeated positive appearances | Total selected capture appearances |
| --- | ---: | --- | ---: | ---: | ---: |
| `bfe784a3e76f` | 4 | 2026-09-15 to 09-18 | **8,248** | 4,834 | 13,082 |
| `ee19badac6cc` | 8 | 2026-09-21 to 09-30 | **14,604** | 10,787 | 25,391 |
| `debddfd23c42` | 9 | 2026-10-01 to 10-13 | **16,116** | 10,775 | 26,891 |

**Family-specific sum = 38,968**, not cross-family unique. The independent global union over all 21 archived selected representations is **36,440**, so **2,528** of that family-wise summed distinct tally are duplicates between the *family partitions* (this is a count difference, not 2,528 independent duplicate events). Selected positives in an archive are not an unbiased historical training sample and repetitions are not independent source examples.

## Hypothetical strict knowledge cutoffs (UTC)

Each cutoff was fixed before this exploratory computation. An archive is available for a hypothetical replay only if its **GitHub artifact_created_at UTC is strictly earlier than the cutoff**; the market `asOf` is never used as the evidence-availability clock.

| Decision cutoff UTC | Previously created archives | Sum of family-separated distinct positive representations (not deduplicated cross-family) |
| --- | ---: | ---: |
| 2026-09-19 00:00 | **3** | **6,783** |
| 2026-10-01 00:00 | **11** | **21,350** |
| 2026-10-10 00:00 | **18** | **33,994** |
| 2026-10-15 00:00 | **21** | **38,968** |

The observed positive archive witness coverage is increasing across available captures. This is a **monotonic cumulative union of archived *selected evidence*** by construction, and is NOT proof that a model knew each link as of the historical market-date, nor a test of increasing predictive signal, temporal causality or a robust strategy's returns. Most archived five-day views were capped; full 60-day historical source observation is *not* demonstrated by 21 captures spanning only 29 market-calendar dates. Family breaks constrain longitudinal comparability.

## Necessary next evidence

1. Independently authenticate each artifact-created UTC and storage/right-to-use at the chosen decision cutoff, and bind the content-vintage/source selection-policy manifests.
2. Preserve an append-only, time-stamped *positive-only* ledger of article-version-to-asset links. Any absence from filtered/capped exports remains UNKNOWN; two captures do not prove uninterrupted link persistence.
3. Establish source mutation / revision chronology, including any documents potentially affected by the September 19 workflow-reported backfill calls (see **separately unmerged PR #41** for pinned workflow/run provenance). This does **not** prove Mongo matched/modified counts or per-document original linkage timing; leave original link `first_available_at` unknown unless independently evidenced. No direct Mongo read/write authorized here.
4. Independently verify price-vintage availability, common eligible universe and C0/S/B/T/O clocks, and preregister fixed lookback L, partitions, embargo, outcome maturity and eligibility **before any real model training**.
5. Preserve isolation: Phase III/MM1 157 frozen blobs and humanclause.com remain unchanged, AWS Lambda approved quota does not authorize deployment, capture activation or scientific counting.

**Fixed scientific gate:** `BLOCKED_SOURCE_AUDIT`; `metadata_independently_authenticated_by_analysis=false`, `historical_first_seen_authenticated=false`, `negative_history_authenticated=false`, `source_completeness_authenticated=false`, `historical_60_day_lookback_authenticated=false`, `model_fitting_permitted=false`, `mm1_execution_permitted=false`, `outcomes_access_permitted=false`. This result is a source-identification/feasibility finding, **not validation of PRAGMA, economic uplift or model convergence**.
