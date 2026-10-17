# Phase IV — Recoverable archived link-state witnesses, exploratory observation v0

**Observed 2026-10-15; metadata-only derived comparison, no market outcome inspection.** This report supplements the distinct [September 19 executed-backfill evidence](DTRM_PHASE4_PRECOHORT_BACKFILL_EXECUTION_PROVENANCE_V0.md). It is an **exploratory source-feasibility observation**, not a preregistered statistical result or confirmation. No actual Mongo read, FMP requests, market-price value analysis, training or MM1 invocation.

## Archive provenance and fidelity

All files below were fetched from **successful production backend GitHub Actions `DTRM daily ranking` runs** with GitHub-managed archive ID and first-observed artifact-created timestamp. The original ZIP and full `ranking_news_evidence/daily_news_freeze_manifest_v1.json` and 2d/5d candidate JSON bytes were checked **locally**; independent `.sha256` files and manifest candidate digests match the actual JSON. Raw headline/text, provider URL, article IDs, ticker lists, rankings and future outcomes are deliberately **not reproduced** in this report.

| Run date / run ID | GitHub artifact ID | GitHub artifact created (UTC) | Frozen `asOf` market date | ZIP SHA-256 |
| --- | --- | --- | --- | --- |
| 2026-09-18 / [35291554064](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35291554064) | 10526157092 | Earlier GitHub creation time not read back in this observation | 2026-09-17 | `eb1671687e09351b02a9cff9fda6e9f23bc2c008af4d65efadadf0c6b58a12ce` |
| 2026-09-22 / [35673999508](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35673999508) | 10672371720 | Earlier GitHub creation time not read back in this observation | 2026-09-21 | `b79e36136039ce5d039aaf3caaae69c6420f7a7dbb20145cdc2d3d3a7c4ab9f3` |
| 2026-10-13 / [38340013884](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/38340013884) | 11785683539 | 2026-10-13 03:11:15Z | 2026-10-12 | `6c01b08ea9684f4f9a93c6bfb123fa79edea7b2bba8c608a6accec968c504ff5` |
| 2026-10-14 / [38494941625](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/38494941625) | 11862953853 | 2026-10-14 01:24:19Z | 2026-10-13 | `3f7af3d8f6c4053a23b31308da6ff12546bb7ad8c093b5e01efd1f8684c0cb6d` |

Actual Oct-13 and Oct-14 `familyManifestSha256` agrees on `debddfd23c420d3a5aedd642edef90e4a5d6eb2e27e3ddb7d0e4140ac1420891`, whereas their independently frozen `sourceNewsSha256` differs, as expected of successive news snapshots. This binds algorithm family consistency, **not** article-first-seen times.

## Safe aggregate readback

| `asOf` date | Verified current news | Verified current news–ticker pairs | Recent verified news | 2d candidate count | 5d candidate count |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-17 | 11,307 | 77,175 | Not extracted in initial safe comparison | 500 (capped) | 500 (capped) |
| 2026-09-21 | 11,042 | 75,643 | Not extracted in initial safe comparison | 273 | 500 (capped) |
| 2026-10-12 | 10,752 | 77,111 | 802 | 250 | 500 (capped) |
| 2026-10-13 | 10,783 | 77,427 | 797 | 497 | 500 (capped) |

Comparisons performed privately on matching `fmpArticleId` plus matching `textSha256` **only**, checking the set of ticker values in memory but releasing **counts only**, with no per-article IDs, tickers, URL or text output:

| Adjacent archive comparison | Common article IDs | Same text digest among common IDs | Common articles with unchanged ticker set | Certified shared article–ticker pairs | Different linked ticker sets among same-text common IDs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Oct 12 `asOf` → Oct 13 `asOf`, 2d | 227 | 227 | 227 | **1,312** | 0 |
| Oct 12 `asOf` → Oct 13 `asOf`, 5d | 230 | 230 | 230 | **1,332** | 0 |
| Sep 17 `asOf` → Sep 21 `asOf`, 2d | 0 | 0 | 0 | 0 | 0 |
| Sep 17 `asOf` → Sep 21 `asOf`, 5d | 0 | 0 | 0 | 0 | 0 |

**Interpretation:**

1. The **227** matched articles and **1,312** shared article–ticker pairs in the two **uncapped** Oct 12→Oct 13 2d candidate outputs form a real **positive observed-in-both-archives subset**. Each linked pair was represented by the generation of both archived outputs, at the latest by the respective GitHub artifact-created timestamps. This establishes a *witness upper bound for knowledge of the frozen snapshot representation*, not the exact first availability of the original article vintage or first formation of the association. It does not authenticate historical prices, time ordering at the earlier news publication date, or any decision before the archive creation.
2. The 5d exports are **hard-capped at 500 items**, so absence there means **NOT_OBSERVED_IN_TRUNCATED_OUTPUT**, never false/missing-at-source. Its overlap does not define a market-news census. Even the uncapped 2d batch includes provider URL, linkage and selection filters and is not exhaustive of the whole source.
3. Sep17→Sep21 zero candidate overlap is driven by largely non-overlapping rolling windows and hard caps; **it does not indicate that associations disappeared, were newly inserted or were unaffected by the Sep19 backfill**. No article-specific effect of the 3 reported update calls is established by these two archives.
4. The shared linked-pair witness is an **exploratory recoverable lower-bound subset** selected after verifying available artifacts; no confirmatory window or statistical hypothesis should be chosen based on this count. This already points to recoverable *positive* Time State records from archived GitHub snapshots **without launching AWS**. It must not be promoted as an authenticated exhaustive event history or a 60-day historical model sample.
5. A responsible future tool needs **authenticated capture times and exact archive hashes, publication/version digest, point-in-time ticker matching semantics, source publication clock, URL/selection policy**, plus a frozen unbiased manifest BEFORE any prospective coverage analysis. Build an append-only per-link positive witness ledger, deduplicating exact vintage/link evidence. **Never use absence from truncated/filtred outputs as historical negative evidence.** Actual first-seen/last-absent causal interval boundaries require independently complete archival coverage or writer mutation logs.
6. Source hashes and link-pair equality prove **snapshot representation repeatability**, not a causal effect of Temporal State on MM1 returns. All G2/G3/G4/G5 real-source gates remain closed; no model fitting, outcome access, scientific counting, or live MM1 use is authorized by this observation.

## Next engineering increment

A standalone, locally executable **source-archive-witness verifier** should ingest a pair of trusted downloaded ZIP paths plus external GitHub run metadata (trusted run ID, archive SHA256 and createdAt), verify all internal manifests/digests, and emit **only** aggregate positive witness/changed-existing-link counts, explicit truncation/selection classification and immutable artifact identities. Keep real articles, text, ticker identifiers and URLs private. No Mongo/FMP/AWS read or unattended network in that offline verifier. The private original ZIP files should not be checked into GitHub or attached to a public research report.
