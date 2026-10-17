# Phase IV — archived positive-only Temporal State ledger mechanics v0

**2026-10-15 — frozen before implementation.** Independent, synthetic-only research graph based on accepted scientific branch `research/phase4-temporal-state` at `3c9c7a2443213c991bba4cb621b97d9a56b3dd6c`. Separately observed real archive corpus (21 successful surviving ZIPs, 36,440 distinct *selected positive* representations in 3 family regimes) is documented under PR #41; its actual IDs, ticker symbols, source text, GitHub output contents and price/outcomes **are not used here**. This is NOT a training sample, a declared 60-day L, or source clock authentication.

## Research purpose

Define a conservative *partial observation state*, not an inferred complete stock-news history. Archived ZIPs may prove that a specific article exact version–asset link is positively represented by the time the SHA-sealed GitHub artifact is created, but such data cannot establish exact original `linked_at` or prove that an omitted pair never existed. Two positive captures do not establish continuous persistence between them. Distinguish **known positive representation at a specific archived snapshot by cutoff**, **unknown origin/absence**, **family lineage**, and **cutoff admissibility**, without feature engineering on outcomes.

## Closed synthetic input contract

A pure in-memory dict only:
- exact `schema_version = dtrm.phase4.archived_positive_ledger_fixture.v0`, `dataset_role=synthetic`, `snapshots` length 1–64, `cutoffs` length 1–64.
- snapshot exact keys `snapshot_tag`, `family_sha256`, `artifact_sha256`, `artifact_created_at`, `positive_link_tags`. Tag format exactly `snapshot_01`..`snapshot_64` unique. Both SHA strings lowercase 64 hex; timestamp full ISO8601 with second precision, optional <=6 decimal fraction and explicit valid UTC offset. Reject unknown offset `-00:00`, naive, invalid, timezone normalization overflow. External authority of supplied timestamp/digest is never asserted.
- `positive_link_tags` list 0–64 of **fictional opaque** tags `link_01`..`link_64`, unique per snapshot. A tag denotes exact (article ID, content vintage, asset) representation within an already fixed **same family**; it carries **no real ticker, article ID, text, URL, hash of a low-entropy ticker, source provenance or outcome**. Empty output is never authenticated absence. Repeats on distinct dated snapshots are allowed and indicate independent positive observations.
- `cutoffs` 1–64 explicit UTC-offset ISO instants as above; normalize and deduplicate by UTC instant, reject duplicate. No lookback L defaults or derived output/label timing.
- A snapshot's `artifact_created_at` must be unique across **all** input snapshots and strictly chronologically comparable, forbidding fabricated two identical capture clocks. Input order arbitrary; reporting canonical sorted order.

## Definition of positive-only temporal state

For each ordered `decision_cutoff` and **each distinct `family_sha256`**:
1. Admit a synthetic archived snapshot to the *positive observation replay* iff its `artifact_created_at < decision_cutoff` (strict, ties excluded). Do NOT use nominal `asOf`, source publication date, or a future archive.
2. Count `witnessed_distinct_link_tags` as the union of opaque tags appearing in at least one admitted snapshot of **that family**; never merge families. Also count `positive_witness_appearances` (repeated captured appearances) and `available_snapshot_count`. For each family, `most_recent_witness_age_seconds` = floor difference cutoff - latest admitted **nonempty** snapshot timestamp (null if no positive witnesses). Time is only the capture age, not original news age.
3. Compute global `known_positive_archive_representations` as sum of **per-family** distinct counts, explicitly not a unique global source population across families, and `unknown_absence_cannot_be_inferred=true`. Zero positive observations from selected archives remains `ZERO_WITNESSED_NOT_AUTHENTICATED_ZERO_HISTORY`.
4. All outputs consist solely of aggregate counts, full source family digest (not private ticker values), normalized cutoff timestamps and fixed statuses. No list of link_tag, source strings or per-link digest is returned, logged or encoded into report SHA; output must be detached immutable dataclasses/tuples, canonical order, no input mutation.
5. False scientific authority flags unconditionally: `scientific_status=BLOCKED_SOURCE_AUDIT`, `github_metadata_independently_authenticated=false`, `original_link_first_seen_authenticated=false`, `source_completeness_authenticated=false`, `historical_absence_authenticated=false`, `g5_lookback_frozen=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`. Synthetic-only PASS is a proof of mechanics, not source/science admission.

## Acceptance tests

At least: cutoff exact boundary tie, later archive excluded, positive repetition dedup versus appearances, family split even on same opaque tag, initially empty snapshots, all-future snapshots, canonical order and timezone equivalence, duplicate/invalid link tags, duplicate snapshots, duplicate normalized UTC cutoffs, malformed/untrusted clock and `-00:00`, immutable detached output, no raw/link-tag values in report, full inherited tests + Ruff/mypy + Phase-III blob preservation.

**No** new AWS/CloudFormation/S3/Lambda writes, no real Mongo/FMP/news/price/market return, no trained B/T, no production MM1 change. Do not treat this as operator authorization to build actual historical ledger until source/archive rights and independent capture authority are proved, and common C0/S/B/T/O estimand, cohort/partitions, first-available price clocks and L are preregistered separately.
