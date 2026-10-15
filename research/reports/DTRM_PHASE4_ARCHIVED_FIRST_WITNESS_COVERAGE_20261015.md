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

## Reproduction v1 on real archives — operator evidence, 2026-10-15

**Source:** operator's Mac terminal, at git head `03a119f48f477792c2d75c76495ebe6bf2da9097` after a fast-forward update and before any source-only release/merge. The `_lzma` portability failure on the earlier head was corrected by a contract-first amendment; rerun returned `PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED`. The operator privately retained 21 originals, and the v1 code pins exact ZIP SHA256 and the canonical 21-source manifest Git blob `eb7c91b462ddb822835c20fc126492bfcae5eea0`. **This is an independently runnable, operator-executed v1 reproduction of original descriptive family/cutoff figures, not a repository CI replay of private inputs**. The new v1 JSON output's SHA256 has **not** been supplied; it must not be equated to the older descriptive v0 SHA.

The independently frozen full family identifiers were abbreviated in the user-shared summary. Each cell below is `admitted snapshots / distinct positives within family / total selected capture appearances / repeated positive witness appearances`.

| Cutoff UTC | September I: `bfe784a3e76f` | September II: `ee19badac6cc` | October: `debddfd23c42` |
| --- | --- | --- | --- |
| 2026-09-19T00:00:00Z | 3 / 6,783 / 9,877 / 3,094 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| 2026-10-01T00:00:00Z | 4 / 8,248 / 13,082 / 4,834 | 7 / 13,102 / 22,244 / 9,142 | 0 / 0 / 0 / 0 |
| 2026-10-10T00:00:00Z | 4 / 8,248 / 13,082 / 4,834 | 8 / 14,604 / 25,391 / 10,787 | 6 / 11,142 / 17,842 / 6,700 |
| 2026-10-15T00:00:00Z | 4 / 8,248 / 13,082 / 4,834 | 8 / 14,604 / 25,391 / 10,787 | 9 / 16,116 / 26,891 / 10,775 |

| Cutoff UTC | Total captures | Family-summed distinct (not cross-family union) | Selected appearances | Repeated appearances |
| --- | ---: | ---: | ---: | ---: |
| 2026-09-19T00:00:00Z | 3 | 6,783 | 9,877 | 3,094 |
| 2026-10-01T00:00:00Z | 11 | 21,350 | 35,326 | 13,976 |
| 2026-10-10T00:00:00Z | 18 | 33,994 | 56,315 | 22,321 |
| 2026-10-15T00:00:00Z | 21 | 38,968 | 65,364 | 26,396 |

**Consistency checks:** within each family/cutoff, `appearances = distinct + repeats`; the final family sum `38,968` exceeds the globally deduplicated union `36,440` by `2,528` cross-family duplicated **representation-count units**, not by 2,528 independent historical observations. All preregistered strict-cutoff figures matched the expected descriptive v0 totals. This settles the observed family-cutoff detail requested in Codex's P2 without changing source admission status.

**Registered computation parity achieved in the operator's full-protocol replay:** At exact repository head `ee0b9e0b3a31df70e6f3227cfada8ca0d0d9e44d`, the operator's Mac completed the updated, SHA-pinned v1 reducer on the same 21 private original ZIPs. Its redacted terminal output reports `PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED`, `source_archive_count=21`, global union `36440`, `2d_capped_count=13`, `5d_capped_count=21`, `sum(len(f["captures"]) for f in families)=21`, and both `historical_first_seen_authenticated=false` and `negative_history_authenticated=false`. The **operator-reported SHA256 of the actual private full-protocol output bytes is `3324efbb6cb8540b74c89af0c633b15656fd04260058b1ebed217b1c6484b1cb`**. This is an SHA claim from user-supplied local CLI output, not an independent GitHub signature or a second off-Mac computation. The v1 code correction, test validation and local full-protocol replay are complete; original archive evidence rights, link first-seen, absence and full 60-day history are still unauthenticated. Nothing here implies original link first-seen, continuous availability, source absence, 60-day lookback completion, licensed re-use, eligible historical decisions, prices, fitting or financial results. `BLOCKED_SOURCE_AUDIT` remains.

## Necessary next evidence

1. Independently authenticate each artifact-created UTC and storage/right-to-use at the chosen decision cutoff, and bind the content-vintage/source selection-policy manifests.
2. Preserve an append-only, time-stamped *positive-only* ledger of article-version-to-asset links. Any absence from filtered/capped exports remains UNKNOWN; two captures do not prove uninterrupted link persistence.
3. Establish source mutation / revision chronology, including any documents potentially affected by the September 19 workflow-reported backfill calls (see **separately unmerged PR #41** for pinned workflow/run provenance). This does **not** prove Mongo matched/modified counts or per-document original linkage timing; leave original link `first_available_at` unknown unless independently evidenced. No direct Mongo read/write authorized here.
4. Independently verify price-vintage availability, common eligible universe and C0/S/B/T/O clocks, and preregister fixed lookback L, partitions, embargo, outcome maturity and eligibility **before any real model training**.
5. Preserve isolation: Phase III/MM1 157 frozen blobs and humanclause.com remain unchanged, AWS Lambda approved quota does not authorize deployment, capture activation or scientific counting.

**Fixed scientific gate:** `BLOCKED_SOURCE_AUDIT`; `metadata_independently_authenticated_by_analysis=false`, `historical_first_seen_authenticated=false`, `negative_history_authenticated=false`, `source_completeness_authenticated=false`, `historical_60_day_lookback_authenticated=false`, `model_fitting_permitted=false`, `mm1_execution_permitted=false`, `outcomes_access_permitted=false`. This result is a source-identification/feasibility finding, **not validation of PRAGMA, economic uplift or model convergence**.
