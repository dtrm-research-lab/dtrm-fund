# Phase IV prospective capture protocol v0

Date: 2026-09-10. Status: REGISTERED_BEFORE_IMPLEMENTATION_OR_DEPLOYMENT.
Parent integration: `6314de2e53f01409918e01e519f5acfa98b7c09f`.

## Purpose and scientific boundary

This addendum defines the first prospective source instrument for Phase IV. Its
purpose is to preserve what a collector observed, when it observed it, which
content version it observed, and when each ticker association was produced.
It addresses the provenance failure established by the retrospective audits;
it does not reinterpret or promote the retrospective census.

The original Phase-IV contract and frozen Phase III/MM1 remain unchanged. This
increment may implement a pure synthetic conformance graph and canonical audit
report only. It does not authorize a production collector change, network or
Mongo access, historical sequence construction, representation fitting,
outcome access, MM1 execution, cohort selection or scientific promotion.
PRAGMA remains architectural inspiration only.

An engineering pass means that a synthetic envelope conforms to this protocol.
It does not authenticate a deployed clock, prove collection coverage, or make
the Phase-IV treatment hypothesis testable. Production deployment, clock trust,
retention, write authority and decision-cutoff compatibility require later
repository-bound evidence and human approval.

## Information model

The protocol version is `dtrm.phase4.prospective_capture_bundle.v0`. A bundle is
one collector invocation and contains exactly:

- `schema_version`;
- `dataset_role`, fixed to `synthetic` in this increment;
- `collector`, the immutable collector/source identity;
- `previous_ledger_head_sha256`, null only for a declared genesis ledger;
- `run`, the invocation clock and aggregate counters;
- `records`, the zero or more new immutable versions admitted by the run.

The collector identity contains exactly `collector_id`, `repository`,
`commit`, `source`, `mapping_version` and `clock_policy`. This v0 conformance
graph permits only `source=fmp_news` and
`clock_policy=utc_runner_bracket_v0`. Repository, deployed commit and mapping
digest values are identity bindings, not proof that the named code ran.

The run contains exactly:

- `run_id`, a lowercase UUID;
- `started_at`, read immediately before the first provider request;
- `response_received_at`, read after all admitted response bytes arrive and
  before event extraction or ticker mapping;
- `completed_at`, read after the canonical bundle has been durably staged;
- `request_fingerprint_sha256`, a secret-free digest of the ordered provider
  request roles and fixed parameters;
- `observed_candidates`, `new_versions`, `repeat_sightings` and
  `rejected_candidates`.

All instants are timezone-aware ISO-8601 values normalized to UTC. They obey
`started_at <= response_received_at <= completed_at`. Counters are nonnegative
integers, booleans are rejected, and
`observed_candidates = new_versions + repeat_sightings + rejected_candidates`.
The record count equals `new_versions`. Rejections remain counted; the protocol
does not silently drop them or encode their source values in the audit report.

## Immutable version record

Each new version contains exactly:

- `sequence_no`, consecutive from one within the bundle;
- `run_id`;
- `source_event_id` and `identity_method`;
- `version_id` and optional `supersedes_version_id`;
- `payload_sha256` and `content_sha256`;
- `version_observed_at` and `first_seen_at`;
- `asset_links`;
- `previous_record_sha256` and `record_sha256`.

No target, price, return, score, rank, prediction, embedding, split or action
field is accepted. Payload and content bytes are archived by the later
production implementation and verified against their digests at that I/O
boundary; this synthetic metadata graph does not ingest or emit source bytes.

`identity_method` is either `provider_id` or `exact_url_sha256`. For the URL
fallback, `source_event_id` is the lowercase SHA-256 of the exact UTF-8 provider
URL after fragment removal only. No host, path, case, slash, query, tracking or
percent-encoding normalization is permitted. The fallback is conservative: two
non-identical retained URLs are different logical events until a future
outcome-blind identity addendum says otherwise.

`version_id` is
`sha256("fmp_news\\0" + source_event_id + "\\0" + content_sha256)` using UTF-8
bytes. Equal logical identity and equal content therefore produce an exact
repeat sighting, not a new version. A changed content digest produces a new
version linked to the immediately preceding version by
`supersedes_version_id`. Chains are linear, complete within the supplied prior
state plus bundle, and cannot fork, skip, cycle or move backwards in observed
time. The first version has no predecessor and fixes `first_seen_at`; every
later version repeats that exact value.

`version_observed_at` is fixed to `response_received_at`: it is the conservative
run-level upper bracket for when the complete response became available, not
the provider publication time. It must never be replaced with provider time,
Mongo ObjectId time, workflow schedule or commit time.

Each asset link contains exactly `ticker`, `mapping_version` and `linked_at`.
Ticker syntax follows the registered event ontology. `mapping_version` equals
the collector mapping digest, and `linked_at` lies between
`version_observed_at` and `completed_at`. A later mapping change creates new
provenance; it does not rewrite an earlier record or backdate a link.

## Ledger integrity

Records are canonically ordered by `sequence_no`. Record hash input is the
canonical JSON object containing every record field except `record_sha256`,
serialized as UTF-8 with sorted keys, compact separators and no NaN values.
`record_sha256` is its SHA-256.

For sequence one, `previous_record_sha256` equals the bundle's
`previous_ledger_head_sha256`; both are null only at genesis. Every later record
references the prior record hash. The output ledger head is the final record
hash, or the unchanged previous head for a zero-new-version run. Input order
permutations serialize identically after validation; a broken hash, gap,
duplicate sequence or disconnected prior head fails closed.

This chain detects alteration or omission relative to a known head. It does
not by itself prove that all provider events were collected, that the writer was
exclusive, or that external storage retained the bundle.

## Pure conformance graph

| Node | Immutable input to output | Invariants and failure | Side effects |
| --- | --- | --- | --- |
| envelope normalizer | exact JSON object to typed bundle | exact keys/types, synthetic role, UTC clocks, fixed identities | none |
| counter reconciler | typed bundle to typed bundle | nonnegative exact counters and record-count equality | none |
| version validator | bundle to validated revision state | derived version IDs, complete linear chains, conservative observation clock | none |
| link validator | revision state to validated link state | ontology ticker syntax, exact mapping version, no backdating | none |
| ledger validator | validated state to capture assessment | consecutive order, canonical record hashes and prior-head continuity | none |
| audit serializer | assessment to canonical JSON | aggregate/identity-only output, deterministic bytes, scientific blocks | none |
| synthetic CLI | explicit fixture and new output paths | no overwrite/symlink, fixed redacted failures | read fixture; exclusively create report |

Typed domain state is frozen and tuple-backed. Parsing detaches it from mutable
input. Public entrypoints revalidate all boundaries. Failure creates no accepted
report, performs no repair and never echoes a rejected value.

## Audit output and scientific state

The canonical audit report contains protocol/graph identity, the canonical
input digest, collector identity, normalized run clocks, aggregate counters,
record/version/link counts, input/output ledger heads and completed nodes. It
contains no payload, content, URL, provider identifier, ticker list, credential,
environment value, model value or outcome.

Every accepted report states:

- `engineering_status=PASS_SYNTHETIC_PROSPECTIVE_CAPTURE_PROTOCOL`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`;
- `source_authenticated=false`;
- `collector_deployed=false`;
- `clock_authenticated=false`;
- `coverage_authenticated=false`;
- `history_construction_permitted=false`;
- `training_permitted=false`;
- `outcome_access_permitted=false`;
- `model_fitting_performed=false`.

No field or operator option may promote these values in v0.

## Precommitted acceptance cases

Tests must establish at least:

1. canonical round-trip, input-order invariance and frozen detached state;
2. timezone normalization and all clock-order boundaries, including equality;
3. boolean/negative/noninteger counter rejection and exact reconciliation;
4. zero-version continuation, valid genesis, and invalid null/non-null heads;
5. exact version-ID derivation, repeat/new-version accounting, complete linear
   revision chains, and rejection of forks, gaps, cycles and backwards time;
6. exact asset-link schema, ticker syntax, mapping identity and link-time range;
7. consecutive sequence numbers, canonical record hashes, chain continuity and
   mutation detection;
8. rejection of source bytes, URLs, targets, prices, scores, embeddings,
   predictions, actions and any extra key at every boundary;
9. deterministic aggregate-only report and recomputed input/report identities;
10. CLI success, invalid-input no-output, existing-path/symlink refusal and
    redacted fixed errors;
11. all scientific promotion flags permanently false;
12. every earlier Phase-IV reproduction, regression, quality, package and
    inherited-source preservation gate remains green.

Synthetic success does not count as a deployed collector test. A later
production PR must add tests at the actual writer boundary for exact archived
bytes, clock capture order, acknowledged append-only persistence, idempotent
repeat handling, overlapping collection, revision discovery, retention,
exclusive write authority and a signed/run-bound ledger head.

## Next promotion gates

After this contract and its synthetic implementation pass current-head CI and
human review, the next contract may bind an exact collector repository/parent
commit, storage namespace, retention rule, deployment workflow, UTC clock
source, overlap schedule, request roles, write operation and artifact/run
evidence. That deployment must start a new prospective interval; it cannot
backdate the retrospective collection.

Only after multiple accepted runs may a separate source/decision-clock audit
consider authenticating a usable interval. History window, common cohort,
partitions, exposure ledger, representation baseline and outcomes remain later
gates. No outcome-driven retuning is permitted.

## Current authorization

This registration authorizes only contract checks, a pure synthetic conformance
implementation, deterministic fixtures/reports and repository validation. It
does not authorize any production writer or workflow modification. Human merge
approval is required after a concrete PR and current-head validation.
