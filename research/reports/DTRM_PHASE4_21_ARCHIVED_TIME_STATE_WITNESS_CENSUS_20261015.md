# Phase IV — 21 archived ranking captures: positive Time State recovery census

**Exploratory, outcome-blind observation dated 2026-10-15.** This is a discovered-archive sample, **not** preregistered confirmation, a real-time provider first-seen audit, a complete stock-news universe, or a trained Temporal State model. No raw article IDs, ticker strings, text, URLs, prices, model scores or outcomes are included here.

## Reproducible archive and transport boundaries

GitHub API inventory of `tech-com-UA00001/theresistance-back` schedule-triggered `DTRM daily ranking` runs from 2026-09-01 through 2026-10-14: **32 scheduled runs observed: 31 success, one failure (2026-09-04)**. Of the 31 success runs, **21 currently have a retrievable `daily-ranking-*` GitHub artifact** dated 2026-09-16 through 2026-10-14. Earlier 10 successful runs currently return **no artifact** from the GitHub API; this is not evidence that they never produced snapshots, and does not cover other schedule/dispatch paths.

All 21 ZIPs were fetched via the authorized GitHub connector to the private analysis runtime, not checked into the repo. The original ZIP SHA256, each embedded `ranking_news_evidence/daily_news_freeze_manifest_v1.json` (or pinned legacy `Outputs/ranking_news_evidence/` prefix) and its SHA receipt, and each `daily_news_candidates_{2d,5d}_v1.json` with SHA receipt and manifest digest/count were verified. A single legitimate ZIP (archive generated on 2026-09-23, frozen `asOf=2026-09-22`) uses the legacy `Outputs/ranking_news_evidence/` internal root; remaining twenty use `ranking_news_evidence/`. The two accepted roots are separately preregistered as a fix in PR #42. The aggregate-only private inventory has **SHA-256 `14c10f19012010073a157b2d9aefc2007c8f768a4077f13ce0bdf000924daa37`** and records exact 21 run IDs, archive IDs, artifact-created UTC times, ZIP/family/source hashes, counts and adjacent overlap counts, without emitting underlying symbols or articles. This inventory hash commits to *that specific local report*, not to independent source attestation or exhaustive data.

## Quantified recoverable witness scope

| Metric | Verified exploratory count |
| --- | ---: |
| Frozen `asOf` dates represented | 21 |
| Range of `asOf` dates | 2026-09-15 to 2026-10-13 (29 inclusive calendar days) |
| Distinct frozen `familyManifestSha256` identities | **3** |
| Snapshots in consecutive family segments | **4, 8, 9** |
| Adjacent archive pairs in chronological order | 20 |
| Same-family adjacent pairs | **18** |
| Pairs crossing a family identity change | **2** |
| 5-day exports **at 500-candidate cap** | **21/21** |
| 2-day exports **at 500-candidate cap** | **13/21** |
| Distinct represented tuples across 2d and 5d exports, dedup `(articleId, exactTextSha256, ticker)` | **36,440** |
| Sum of positive shared tuple appearances across 18 same-family adjacent comparisons, 2-day export | **22,348** |
| Same metric for 5-day export | **26,396** |

**Crucial interpretation:** 36,440 is the size of the union of *selected positive represented triplets*, **not** unique source articles, original link creation events, valid model training examples, independent observations or an exhaustive news history. The 22,348/26,396 pair counts are **sums across transitions** and repeat the same tuple whenever it appears in three or more captures; never treat them as independent or additive to the 36,440 union.

The three lineage segments are:

| Market `asOf` range | Snapshots | Frozen family digest (prefix for display) |
| --- | ---: | --- |
| 2026-09-15–2026-09-18 | 4 | `bfe784a3e76f` |
| 2026-09-21–2026-09-30 | 8 | `ee19badac6cc` |
| 2026-10-01–2026-10-13 | 9 | `debddfd23c42` |

The lineage boundaries Sep-18→Sep-21 and Sep-30→Oct-01 cannot be counted as *same-policy* matched-arm comparisons without a separate preregistered mapping across family versions. Positive intersection across the boundary may still exist, but does not prove equivalence of the selection process.

## Unobserved events are not negative events

All 21 five-day exports hit `_MAX_CANDIDATES=500`, and thirteen two-day exports hit the same cap. Both windows use URL/metadata/deduplication/eligibility gates. Even in a **not-capped** export, failure to find an article/asset pair cannot be interpreted as proof of nonexistence in the original `trumpMinMax.trumpNews` collection. Weekends, unequal source materialization dates, a replacement news SHA and family transitions further limit adjacent inference. Exact timestamp to use for positive representation is the **separately observed GitHub artifact-created UTC** time; the earlier `asOf` market date and original provider publication timestamp are not admissible substitutes for that first positive evidence.

Across twenty adjacent archive comparisons, the script observed **zero changed ticker sets among article IDs with equal text SHA appearing in both selected outputs**. That is a censored overlap property; it does **not** disprove historical backfills or indicate that mutable `matched_tickers` never changed. The verified 2026-09-19 applied backfill (run 35439965103) attests a script-reported update procedure, but **these snapshots cannot identify the three exact mutated documents or their historical link availability**.

## Status and predeclared next gates

- **RECOVERABLE:** positive archived representation at or before an independently pinned artifact creation instant; immutable ZIP and internal content/lineage SHA witnesses. This can seed a provenance-aware *selected-subset* ledger, not a complete negative/positive history.
- **PARTIAL/UNKNOWN:** source/vintage discovery and linking times earlier than archive capture, missing linked IDs, potential updates between captures, selection censoring, actual provider first availability and exact C0 daily price-vintage knowledge.
- **SEPARATE PROSPECTIVE:** append-only content/link observation timestamps and mutation receipts, user-authorized AWS dormant diagnostic deployment (quota alone not deployment), explicit source rights, common chronological C0/S/B/T/O cutoffs, fixed L and partition assignments **before** coverage/test statistics, 60-day+5-day future outcome maturity and independent financial price clock.

Every scientific gate remains blocked: `source_authenticated=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`. No changes to frozen Phase III/MM1 or its active production service.

**Method details:** strictly offline in-memory ZIP readback; SHA256 validation of each source ZIP / candidate / manifest, per-archive lineage identity/score scope, aggregate-only set operations; original article IDs, symbols, URLs and texts remain confined to private analyst runtime and are never committed.
