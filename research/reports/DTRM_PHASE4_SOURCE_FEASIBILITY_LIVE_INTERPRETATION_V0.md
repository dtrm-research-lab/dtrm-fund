# Phase IV source-feasibility live evidence — interpretation v0

Date: 2026-09-08.
Evidence file: `DTRM_PHASE4_SOURCE_FEASIBILITY_LIVE_20260908T213801Z.json`.
Operator-reported file SHA-256 and repository-byte SHA-256:
`0c0c633cd7eb9fef439788db894795f02edcfb10a844eb3f192a1c4b5d7d2995`.

## Evidence identity and boundary

The user ran the registered read-only feasibility command on their Mac. The
agent did not access Mongo configuration, secrets or source records. The user
shared the sanitized aggregate JSON and its digest. Reconstructing the exact
registered two-space canonical serialization produced the same file digest.
The fixed pipeline digest is
`ab2be4c672405785094fd49b92444fb6bdf93d291a9e414cbac08c7013b3462d`;
the normalized counters/index evidence digest is
`3df9d397a3c67722220f64a1bd0c8fdf2d5d978ed3c469c7ef70fa71b8f60ad0`.
Both independently recomputed values match the report.

The audit read 1,000 documents in ascending `_id` order. The sample is bounded,
nonrepresentative and not sorted by event time; the aggregation and index read
are not atomic. Results apply only to the registered paths and this sample.
They do not establish a collection-wide absence or historical index behavior.

## Observed aggregate facts

- `raw` is an object in all 1,000 sampled documents.
- Top-level `date` is a parseable naive string in all 1,000: 604 diagnostic
  year 2024 and 396 diagnostic year 2025. UTC conversion was diagnostic only;
  it does not authenticate timezone, availability or decision-clock semantics.
- `raw.publishedDate` is a naive string in 955 documents and missing in 45;
  `raw.date` is a naive string in 45 and missing in 955. Likewise `raw.url` is
  a string in 955 and `raw.link` in 45. These matching marginal counts suggest
  source-schema variants worth documenting, but this report contains no
  cross-tabulation and cannot establish that the same 45 records form each
  variant.
- No registered source identifier was present at `raw.id`, `raw.articleId` or
  `raw.article_id` in the sample. `raw.newsUrl` was also absent throughout.
- Every sampled document lacks each registered historical-provenance field:
  `raw.first_seen_at`, `raw.observed_at`, `raw.updated_at`, `raw.version_id`,
  `raw.content_sha256`, `raw.mapping_version` and `raw.linked_at`.
- `dedupe_key` is missing in every sampled document. The current catalog has
  three indexes: one ascending `date`, one ascending `dedupe_key`, and that
  dedupe index currently qualifies as unique, sparse and unqualified under the
  registered sanitizer. A sparse current index permits documents without the
  key and proves neither past enforcement nor immutable version lineage.

## Scientific decision

This evidence does **not** authenticate a historical availability clock or an
observed content vintage. Provider publication strings can describe when an
article says it was published, but cannot prove when the machine first saw that
exact version or ticker association. The static collector audit additionally
showed a current-time fallback, no overlap in incremental collection, broad
dedupe fallback and no immutable revision archive. The sources corroborate the
same blocker rather than repair each other.

Accordingly:

- Authentic retrospective `as-of` history construction is not permitted from
  this current collection alone.
- Publication chronology must not be relabelled as machine observation history.
- No history representation, baseline/Transformer fitting, outcome access or
  frozen MM1 execution is authorized.
- `BLOCKED_SOURCE_AUDIT`, `decision_clock_authenticated=false`,
  `history_construction_permitted=false` and `training_permitted=false` remain
  scientifically necessary.

This is a negative feasibility finding, not a negative result for the Phase-IV
hypothesis. The representation hypothesis has not yet been tested.

## Defensible paths forward

Before committing exclusively to prospective data, one final retrospective
salvage audit is scientifically permissible if separately preregistered. It may
test, without outcomes or source-text disclosure, whether Mongo `ObjectId`
generation time is supportable as a conservative insertion-time proxy in this
specific writer path; whether all relevant writers were insert-only; whether
backfills and collection lag can be identified; and whether repeated source
URLs appear as separate immutable records. `ObjectId` must remain inadmissible
unless code, runtime and aggregate consistency evidence jointly support its
meaning. Its embedded client-clock seconds are not self-authenticating, and it
cannot by itself establish version content or historical ticker mapping.

If that registered salvage gate fails or leaves material ambiguity, the
preferred confirmatory path is prospective, append-only collection under a
separately approved contract. It must preserve collection/first-seen time,
exact-version observation time, immutable content bytes and digest, source
identity, predecessor/version identity, mapping version and link-availability
time. Provider publication time remains distinct. Repeated overlapping pulls,
revision handling, failure logging, watermark/tie semantics and retention must
be fixed before collection starts.

Before Stage 2, the project must also bind the decision schedule and timezone,
the frozen control's beta/price dependencies against that cutoff, historical
universe/mapping semantics, current-event handling, and the confirmatory
exposure window. A retrospective development-only publication chronology would
be a different, weaker estimand and requires an explicit new approval; it cannot
quietly stand in for “information the machine already knew.”

No choice between these paths is made from model outcomes. PRAGMA remains
architectural inspiration only.

## Validation record

The tracked report has a dedicated regression assertion for its exact file
digest, fixed pipeline digest, normalized evidence digest, execution mode and
all six false scientific-permission/readiness flags. Agent-run gates on the
complete evidence tree: 47 targeted source-feasibility tests passed; the full
suite passed with 453 tests and three dedicated-CI Mongo tests skipped locally.
Scoped Ruff and strict mypy (13 files) passed. All three prior synthetic reports
reproduced byte for byte; pinned collector-lineage validation passed with 12
findings; disposable-source wheel build and pre/post preservation passed. The
current PR head must repeat its remote checks before human integration review.
