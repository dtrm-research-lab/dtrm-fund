# Phase IV — Archived positive-link witness verifier v0

**2026-10-15 | CONTRACT PREREGISTERED BEFORE IMPLEMENTATION.** Bounded research tool, branch `feature/phase4-archived-positive-link-witness-v0`, based on accepted Phase IV research branch `3c9c7a2443213c991bba4cb621b97d9a56b3dd6c`; separate from PRs #39–#41, no MM1/prod edits. Exploratory source-availability feasibility only, not confirmatory research.

## Scientific target

A retrospective current Mongo row cannot establish what news-to-ticker mapping existed at a historical cutoff, especially after the independently verified 2026-09-19 `--apply` backfill (see PR #41). However pre-existing **GitHub Actions frozen ranking artifacts** may independently attest a **positive observed representation** at an external immutable archive timestamp. Verify archived snapshots first, compare exact article version + ticker pair witnesses, and **never infer absence from a rolling-window, URL-selected or capped output**.

This tool compares two already-local, archived **DTRM daily ranking** GitHub Actions ZIP artifacts. It does not fetch web/GitHub/Mongo/AWS/FMP content; CI uses synthetic archives only. Operator provides out-of-band GitHub run ID, original ZIP SHA256 and artifact-created UTC timestamp for each archive; code checks these but **does not authenticate the supplied GitHub metadata against GitHub's API**. Proper source authority remains external and G2–G5 BLOCKED.

## Strict, read-only inputs

- Exactly two complete ZIP bytes (early/late), 0 < archive bytes <= 10 MiB each, no decrypted or extracted filesystem writes. Every entry has bounded decompressed size <= 8 MiB and total <= 20 MiB; path traversal and duplicate ZIP filenames rejected (no zip bomb). Reject invalid/non-ZIP errors with fixed error.
- Each archive must contain the expected `ranking_news_evidence/` files: `daily_news_freeze_manifest_v1.json` and `.json.sha256`, `daily_news_candidates_2d_v1.json`, `.sha256`, `daily_news_candidates_5d_v1.json`, `.sha256`. Verify each full SHA-256, and manifest-declared candidate digests and counts; validate candidate metadata matches manifest `asOf`, `sourceNewsSha256`, `familyManifestSha256`, `windowDays=2|5`, `provider=financial-modeling-prep`, schema version 1.0. Reject JSON duplicate keys or non-finite constants. The source manifest's own digest is checked from its adjacent file, and sha strings must be exactly 64 lowercase hexadecimal chars. Reject broken link/candidate schema, unknown shape, duplicate article IDs or duplicate tickers within an item.
- External metadata: fixed numeric positive unique `run_id`, expected ZIP SHA256, `artifact_created_at` with explicit UTC offset. Require early created_at < late created_at and early `asOf` date < late `asOf` date; no inferred article creation from `asOf`. At current stage metadata trust flags remain FALSE even after matching supplied SHA/datetime.
- The **full** item may carry private source headline, URL, text and ticker values, but the analysis reads only `fmpArticleId`, `textSha256`, and `tickers`; it never prints, writes, hashes individually for publication, or returns article ID/text/ticker identifiers, item excerpts or URLs in a report.

## Frozen matching and observation semantics

For each 2d and 5d export separately, within known source-selection windows:
1. `shared_article_ids`: intersection of identical `fmpArticleId` across earlier/later captures; this is only an exploratory candidate identity, subject to provider identity issues.
2. `shared_exact_text_versions`: subset with exact same `textSha256`.
3. `stable_article_ticker_links`: count pairs `(fmpArticleId,textSha256,ticker)` present in **both** frozen snapshots; `articles_with_unchanged_ticker_set` counts exact-text articles whose ticker set is unchanged.
4. `changed_link_set_on_exact_text`: number of exact-text shared articles with differing ticker sets. Report aggregate `later_only_pairs` and `earlier_only_pairs` **only among these shared articles**; classify as changed *representation*, **not independently proven in-database mutation or first-seen time**.
5. Any missing article/ticker in one output has state **UNKNOWN_NOT_OBSERVED_IN_SELECTED_EXPORT** and is NEVER proof it did not exist in Mongo or at provider time; this includes uncapped 2d batch due URL/eligibility filters, and all 500-capped windows. If item_count==500 set `potentially_truncated=true`, never completeness=true. Non-overlap due changing rolling date windows must not be misread as absence or backfill.
6. Identical family manifest SHA between snapshots required for comparison; otherwise `BLOCKED_FAMILY_LINEAGE_MISMATCH` and no positive witness count. Distinct snapshot news SHAs are fine.
7. Use immutable dataclasses/tuples and report detached fresh JSON. Report only SHA256s, allowed run IDs, provided archive times, market asOf dates, capped flags and aggregate counts, explicit **blocked** status. `engineering_status=PASS_ARCHIVED_POSITIVE_WITNESS_COMPARISON`; `scientific_status=BLOCKED_SOURCE_AUDIT`; `snapshot_metadata_independently_authenticated=false`, `original_link_first_seen_authenticated=false`, `absence_authenticated=false`, `source_completeness_authenticated=false`, `price_clock_authenticated=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`.

## Pre-registered test and output safeguards

Synthetic in-memory ZIP fixtures with correct/incorrect nested hashes; stable pairs, revised ticker set on same text, changed text, duplicate ID/duplicate ticker, invalid SHA, malformed archive/JSON, duplicate JSON keys, date inversion and family mismatch, 500 cap, detached state, no private content leaks. End-to-end offline run on privately available GitHub archives after tests is exploratory and produces **aggregate-only counts**; original ZIPs must **never** be committed, sent in chat or republished by this tool. No intervention on MM1 or active collector, no AWS deployment or new network calls.

## Interpretation of real exploratory observation already registered

The separately observed Oct-12 `asOf`→Oct-13 `asOf` 2d snapshots have 227 common exact-text article IDs and 1,312 stable article–ticker link representations; the 5d exports are at a 500-item ceiling. Sep-17→Sep-21 snapshots have zero overlap due date-window shift and caps; this cannot be interpreted as missing/purged links. These are **observational inputs selected after artifact discovery**; the tool shall not treat them as confirmatory, historical completeness or evidence of economic benefit. Source citation, artifact hash lineage and detailed limitations are stored in PR #41's `DTRM_PHASE4_ARCHIVED_LINK_STATE_WITNESS_EXPLORATION_V0.md`.

No code implementation shall start until this preregistration commit exists.
