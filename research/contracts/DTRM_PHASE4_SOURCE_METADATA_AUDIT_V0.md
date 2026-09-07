# Phase IV source metadata inventory v0

Date: 2026-09-07. Status: registered before implementation or live inspection.
Parent ontology: `DTRM_PHASE4_EVENT_ONTOLOGY_V0.md`.
Integrated parent: `c6f07549ba733866809aa05156365611e2002b62` (PR #1).

## Purpose and scope

Inventory the presence and BSON types of candidate provenance fields in the actual news collection before selecting a source mapping or constructing histories. This is the first bounded source-audit operation, not the completion of Stage 1 or the leakage firewall. Metadata coverage may guide the next provenance investigation; protected outcomes may not guide this operation or the research design.

The source namespace is `trumpMinMax.trumpNews`, as bound by the frozen V5/V6 builders at `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`. The operation observes at most 1,000 documents in ascending `_id` order. This is an explicitly nonrepresentative, bounded current-collection sample, not an event-time ordering, a census, a historical snapshot, or a confirmation cohort. Do not infer chronology or ingestion time from ObjectId.

## Fixed metadata candidates

Only these top-level fields may be referenced, in this order:

`_id`, `date`, `matched_tickers`, `published_at`, `publishedDate`, `first_seen_at`, `firstSeenAt`, `version_observed_at`, `observed_at`, `ingested_at`, `fetched_at`, `created_at`, `updated_at`, `version_id`, `supersedes_version_id`, `content_sha256`, `linked_at`, `mapping_version`, `asset_links`.

Except for the inherited `_id`, `date`, and `matched_tickers`, these names are discovery hypotheses, not observed schema or approved semantic mappings. No alias is automatically assigned to the ontology. Missing fields mean missing in this sample at these exact paths, not absence from every document, nested structure, upstream vendor, archive, or collection.

The database pipeline is fixed: sort by `_id`, limit to 1,000, project each candidate to its `$type` string under an internal field key while suppressing `_id` values, then facet into document count and per-field type counts. No text, title, actual identifiers, ticker values, timestamp values, labels, scores, returns, prices, or arbitrary fields are returned. No `$out`, `$merge`, joins, arbitrary query, or dynamic namespace is permitted. Only a single read aggregation is issued; application code performs no database writes.

Missing and null are separate bins. BSON `date` does not establish the field's provenance semantics; `string` does not establish date precision or timezone. Array/object contents are not inspected. No date values, timestamp precision, revision continuity, content bytes, mapping history, or temporal eligibility is verified by these counters.

## Typed graph and boundaries

| Node or boundary | Input → output | Invariants and failure behavior |
| --- | --- | --- |
| `build_metadata_pipeline` | Frozen constants → fresh pipeline | Pure; no caller-supplied fields/query/stages; fixed read-only scope |
| Mongo adapter | Local connection configuration → aggregate response | One bounded aggregate; close client even on failure; total client timeout 60s, server selection 10s, server execution 20s; no printed URI, password, or exception message |
| `normalize_metadata_counts` | Aggregate object → immutable typed counts | Exact keys; known BSON type aliases only; unique type bins; integer counts excluding booleans; positive bin counts; each field totals the sample count; count is 0–1,000 |
| `build_metadata_report` | Typed counts + execution mode → report | Pure, canonical ordering and digest; always `BLOCKED_SOURCE_AUDIT`, training/outcome access false |
| CLI file boundary | Explicit synthetic fixture or Mongo mode → new JSON report | Mutually exclusive modes, explicit output, refuse overwrite before connecting; write success only after complete validation |

The Mongo adapter uses local `MONGO_URI`, or the existing builder's `db_password` connection convention with URL-encoded password. An explicitly named dotenv file may be loaded without overriding environment variables. Neither credential source is included in reports. Synthetic mode never loads connection configuration or imports the database driver. Connection/protocol failures return a fixed error category and no success report.

Report schema: `dtrm.phase4.source_metadata_inventory.v0`. Include execution mode, fixed namespace and sample rule, observed document count, sorted type counters for all candidate fields, pipeline SHA-256, normalized-count SHA-256, and explicit unresolved scope. Digests bind the query specification and returned counters, not a raw-data snapshot or historical provenance. Live reports additionally record the local audit start/completion UTC instants, which are audit times only. A zero-document response is valid empty evidence and remains blocked.

## Required validation

Test null versus missing, all-missing fields, empty collection response, complete-looking metadata staying blocked, count/type/key corruption, duplicate bins, totals and sample-cap checks, deterministic serialization, immutable counts, fixture mode without database imports, adapter limits and closure on error, refusal to overwrite before connecting, and redaction of driver exceptions. Synthetic evidence must reproduce exactly. Run scoped lint, strict typing, the complete regression suite, preservation, and a disposable wheel build. A fake transport validates the adapter contract; it is not a live-server integration test.

## Remaining evidence and decision clock

After the local live report, investigate the semantics and retention of available fields through the collector/writer and archived vintages. Bind an actual source snapshot, timeline/coverage, revision and link evidence, universe/mapping history, and a shared decision clock before Stage 2.

Static evidence: the frozen V6 builder truncates `date` to a calendar day; the V5 beta helper includes cached price observations whose timestamp is `<= event_date`. This source code alone does not establish when a same-day price was available. Price-cache timestamp conventions, event availability, and target/execution timing therefore require a joint decision-clock addendum. No Phase-III code or result is revised.

No training, historical sequence construction, MM1 execution, outcome access, date/cohort selection for confirmation, or scientific promotion belongs to this increment. Full preregistration remains incomplete.

## Technical references

- MongoDB [`$type`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/type/): BSON aliases and distinct missing/null behavior.
- MongoDB [`$project`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/project/) and [aggregation stages](https://www.mongodb.com/docs/manual/reference/mql/aggregation-stages/): projection and facets.
- PyMongo [aggregation](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/) and [operation timeouts](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/connection-options/csot/): read transport and bounds.

References support implementation mechanics only, not scientific evidence for temporal representations.
