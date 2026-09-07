# Phase IV collector and archive lineage audit v0

Date: 2026-09-07. Status: registered before repository-content inspection.
Parent evidence: `DTRM_PHASE4_SOURCE_METADATA_LIVE_20260907T183459Z.json`.
Integrated parent: `ebe77c66ad74b3fc75791be10b502f6ab613b12d` (PR #2).

## Question and fixed sources

Determine whether the code that collects and publishes DTRM news establishes a reproducible observation clock, immutable content vintages, and point-in-time ticker-link provenance for Phase IV. This is a static code-lineage audit. It cannot prove runtime behavior, database history, vendor guarantees, or past deployment state by itself.

The inspection is limited to these repository snapshots, discovered before content review:

| Repository | Pinned default-branch commit | Role hypothesis |
| --- | --- | --- |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `badb20158890e9982c7806382cc3e151782af372` | Candidate collector/model pipeline |
| `tech-com-UA00001/theresistance-back` | `7a8107e4451891535366acaf766348785ccc157b` | Candidate publication/orchestration backend |

The historical `tech-com-UA00001/DTRM_Fund_Agent` URL currently redirects to repository id `1128196792`, identified by the connected repository catalogue as `theresistance-back`. The redirect is routing evidence only and is not evidence that every historical collector version moved there.

## Allowed inspection

Read recursive Git trees at the pinned commits. Select files by path/name matches for collector, news, FMP, Mongo, ingestion, persistence, archive, version, schedule, workflow, orchestrator, and publication concepts. Search the two pinned default branches for `trumpNews`, database writes (`insert`, `update`, `replace`, `bulk_write`, `delete`), timestamp assignment, content hashes, ticker matching, deduplication, unique indexes, upserts, source identifiers, version/archive collections, and collector entrypoints. Fetch every cited file at its pinned commit and bind it by Git blob SHA.

Inspection may include source, workflow/configuration, tests, and documentation. It excludes secrets and secret values, workflow logs, databases, APIs, artifacts, outcomes, targets, scores, realized returns, Phase-III result files, and any mutation of the inspected repositories. Names of environment variables may be reported only when necessary to trace a connection boundary.

## Evidence questions

For each relevant write path, record:

1. Source endpoint or upstream record identifier used, without querying the endpoint.
2. Destination database/collection and exact stored fields visible in code.
3. Insert/update/replace/upsert/delete semantics and deduplication key.
4. Whether collection time, first-seen time, version-observed time, content digest, predecessor/version identity, mapping version, and link-availability time are persisted.
5. Whether changed content or ticker links overwrite a record, append a new immutable version, or follow an unresolved path.
6. Whether schedules, retries, pagination, or lookback/backfill behavior can create ambiguity in first observation.
7. Whether tests enforce any of these properties.

For the publication backend, record only whether it copies, transforms, or preserves news provenance. Do not treat a public output timestamp as source observation time unless the code explicitly binds those semantics.

## Decision rules

- `SUPPORTED_STATICALLY`: a property is explicit in code and any required configuration is visible at the pinned commit.
- `CONTRADICTED_STATICALLY`: visible code implements an incompatible behavior such as mutable replacement without retained versions.
- `UNRESOLVED`: relevant code, deployment binding, runtime evidence, schema, or semantics is absent or ambiguous.

No property becomes scientifically authenticated from static code alone. ObjectId generation time, file modification time, commit time, API `date`, execution time, and public publication time are not interchangeable clocks.

If no immutable observation/version history is found, report the limitation. Do not manufacture historical timestamps from ObjectId, Git history, current collection contents, collector cadence, or vendor publication dates. A later contract may define a coarser day-level event-history experiment only if its point-in-time construction is supportable and scientifically distinct from true observed-vintage history.

## Deliverable and gates

Produce one report and one machine-readable evidence manifest in this repository. The manifest binds inspected repositories, commits, selected paths, Git blob SHAs, and findings; it contains no copied secrets or raw source data. The report separates facts, inferences, contradictions, and unresolved items and keeps `scientific_status=BLOCKED_SOURCE_AUDIT` unless a later registered addendum closes every required source and decision-clock gate.

Validate manifest schema, deterministic serialization, citation binding, no forbidden paths/terms, source preservation, lint/type checks for any new validator, full regression tests, synthetic evidence if code is added, and a disposable package build. Human review is required before integration.

No collector modification, new collection, data migration, live query, history construction, model fitting, MM1 execution, outcome access, cohort selection, or scientific promotion is authorized by this audit.
