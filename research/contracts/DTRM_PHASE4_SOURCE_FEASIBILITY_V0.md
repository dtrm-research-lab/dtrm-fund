# Phase IV bounded source feasibility v0

Date: 2026-09-08. Registered before implementation or new live source queries.
Parent: PR #3 merge `f5148f2f6787d3282c04a357e59d32ed3c515ba8`.

## Scope

One read aggregation on `trumpMinMax.trumpNews`, ascending `_id`, limit 1000,
followed by one index-catalog cursor (at most 65 entries; reject above 64).
No arbitrary namespace/query, writes, index creation, outcomes, text retrieval,
cohort selection, training, history construction, or external collector changes.
Coverage means only this nonrepresentative sample, never a census or vintage.
No interpretation of `_id` as observation time.

Fixed type paths: `raw`, `dedupe_key`, `raw.id`, `raw.articleId`, `raw.article_id`,
`raw.url`, `raw.link`, `raw.newsUrl`, `raw.publishedDate`, `raw.date`,
`raw.first_seen_at`, `raw.observed_at`, `raw.updated_at`, `raw.version_id`,
`raw.content_sha256`, `raw.mapping_version`, `raw.linked_at`.
Nested paths use Mongo dotted-path semantics; a parent array can yield an array,
not per-element counts. Field presence cannot establish provenance semantics.

Date diagnostics apply only to `date`, `raw.publishedDate`, `raw.date`.
Server-side conversion accepts string/date types only, never numeric/ObjectId
coercion. Return counts by parse class and UTC year, never individual dates:
`missing`, `null`, `non_date_type`, `invalid_string`, `bson_date`,
`explicit_timezone_string`, `date_only_string`, `naive_string`.
For parseable strings, classify exact YYYY-MM-DD as date-only, terminal Z or
signed HH:MM/HHMM as explicit timezone, and other parseable strings as naive.
Naive/date-only parsing uses server UTC conversion solely for diagnostic year
bins; it is not an approved timezone assumption for decisions. BSON date also
does not prove semantic clock identity. Year histograms are sample coverage,
not dataset eligibility or experiment-period selection.

Index catalog metadata may transit memory but is never logged/copied. Emit
only total count and counts of exact single-field ascending `date` and
`dedupe_key` indexes. For dedupe, additionally count unique+sparse indexes with
no partial filter, collation override, hidden flag, TTL, or buildUUID. Even a
matching definition is not historical enforcement or immutable revision proof.
Do not return index names, unknown keys, filter values or arbitrary options.

## Graph contract

| Node | Input / output | Invariants / failure |
| --- | --- | --- |
| query builder | constants / fresh aggregation | pure; fixed sort, limit, type projection and facets |
| normalizer | aggregate / frozen tuple counters | exact keys, fixed types/classes, positive int bins, no bool counts, reconcile all totals <=1000, unique bins; reject before output |
| index sanitizer | bounded catalog / frozen counters | only allowlisted aggregate properties; no raw values in result; malformed catalog fails |
| report | immutable counts / deterministic JSON | hashes bind specification and counters only; always BLOCKED_SOURCE_AUDIT |
| Mongo boundary | existing env or explicitly named dotenv / validated report inputs | no secret display; no automatic env search; override=false; client/cursors close on failure; fixed error codes |
| CLI | explicit synthetic or Mongo mode / new evidence file | no-overwrite check before connection, exclusive creation; errors never echo driver/input text |

Live boundary uses existing `MONGO_URI` or inherited `db_password` convention,
URL-encoded as before; it may load only an explicitly selected dotenv file.
Client operation timeout 60s, server selection 10s, socket 20s, retryReads=false;
aggregate maxTimeMS=20000, allowDiskUse=false. Catalog uses PyMongo client
operation timeout (list_indexes has no maxTimeMS keyword). Two reads are not
an atomic snapshot. Record start/end audit clocks separately from source clocks.
No credentials or implicit live execution in CI. Missing configuration is a
live-validation blocker, not permission to seek secrets in another environment.

## Validation and decision-clock guard

Unit tests: exact schema, corruption, immutable state, deterministic ordering,
date-bin consistency and sanitized catalog. Functional tests: complete CLI,
fake transport failures/closure, missing configuration and no-overwrite.
Integration: actual Mongo service in isolated CI with synthetic documents only;
fixture setup writes are restricted to that disposable localhost service.
No production URI/env file is accepted by the service test. Exercise real
aggregation semantics, >1000 input cap, nested arrays and index sanitization.
Regression: entire inherited suite, old synthetic byte comparisons, preservation,
lint, strict typing, disposable wheel build and current-head CI before review.

Even perfect diagnostics cannot authorize a day-level decision clock. A later
addendum must bind source availability, mapping history, market-price timing,
baseline compatibility and revision treatment with explicit evidence. Without
that evidence, both authentic historical reconstruction and a confirmatory
day-level experiment remain blocked. Prospective collection would require a
separate approved change. No outcome-driven retuning.

Technical mechanics: [Mongo field paths](https://www.mongodb.com/docs/manual/core/field-paths/),
[$convert](https://www.mongodb.com/docs/manual/reference/operator/aggregation/convert/),
[PyMongo list_indexes](https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.list_indexes).
