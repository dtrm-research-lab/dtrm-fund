# Phase IV prospective collector deployment contract v0

Date: 2026-09-11. Status: REGISTERED_BEFORE_IMPLEMENTATION_OR_ACTIVATION.
Parent integration: `4870a643f7d4317909997551563fe296970dcccd`.

## Purpose and boundary

This addendum binds the production-writer target and the dormant implementation
boundary for the Phase-IV prospective capture protocol. It follows the
integrated protocol and synthetic conformance graph; it does not alter them or
reinterpret the retrospective evidence.

The target repository is the private repository
`tech-com-UA00001/theresistance-back`, repository id `1128196792`, default
branch `main`, at exact parent commit
`7a8107e4451891535366acaf766348785ccc157b` and tree
`f295888372d9ef3c089cc24dd1e72e6b1f2c92cf`. This is the same source snapshot
already inspected by the registered collector-lineage audit. Naming a target
commit authorizes no write to that repository in this increment.

This contract may be followed by a separate PR that implements and tests a
disabled shadow collector from that exact parent. It does not authorize merging
that implementation, enabling a workflow, creating a production collection,
using a credential, querying FMP or Mongo, migrating legacy rows, constructing
history, fitting a representation, accessing outcomes, running MM1 or promoting
scientific status. Every such transition remains a distinct human gate.

Phase III/MM1 and the original Phase-IV contract remain frozen. PRAGMA remains
architectural inspiration only.

## Existing evidence and source identities

The deployment design inherits, without upgrading, these pinned findings:

- the visible collector path is
  `agent/trump_model/news_collector.py` at blob
  `700e831db5c1d196a8e7c2c1dc6d10148237e710`;
- the visible path has insert-only intent but does not persist a distinct
  observation clock, immutable version/predecessor identity, mapping version or
  ticker-link availability;
- incremental collection begins after the maximum legacy provider date and
  therefore does not establish overlapping late-arrival/revision coverage;
- static schedule and ranking-freeze evidence cannot authenticate historical
  runtime deployment or repair the legacy collection;
- the retrospective census remains `RETROSPECTIVE_PROXY_PARTIAL`.

The manifest must bind the target repository id, parent commit/tree, selected
writer/workflow blob identities and the integrated prospective protocol
identities. Any mismatch fails before implementation is described as conforming.

## Isolation and storage contract

Prospective evidence is isolated from the legacy namespace.

| Role | Exact namespace | Runtime permission |
| --- | --- | --- |
| immutable event versions | `trumpMinMax.phase4ProspectiveNewsV0` | find + insert only after activation |
| immutable accepted-run manifests | `trumpMinMax.phase4ProspectiveRunsV0` | find + insert only after activation |
| legacy news | `trumpMinMax.trumpNews` | none from the prospective writer |

The dormant implementation must contain no code path that inserts, updates,
replaces, deletes, upserts, merges, renames, drops or creates indexes in the
legacy collection. It must not add prospective fields to legacy rows. Existing
models and publication continue to use their frozen paths; the shadow collector
cannot become a hidden model input.

The two prospective collections are append-only evidence stores. Runtime code
may use `find` and acknowledged `insert_one`/transactional insert operations
only. It may not update, replace, delete, upsert, bulk-rewrite, run `$out` or
`$merge`, execute server-side JavaScript, or weaken acknowledged write concern.
Required schema validators and unique indexes are provisioned by a separately
reviewed one-time operator step; runtime startup reads and verifies them but
does not repair or create them.

The future runtime credential must be dedicated to these two namespaces with
only the minimum read/insert permissions. It cannot reuse a broad application
credential. Its name, URI, username and value never appear in contracts,
manifests, reports, CLI arguments or logs. The agent and CI do not inspect
production environment-variable presence or contents.

## Event-version document

An admitted document implements the integrated
`dtrm.phase4.prospective_capture_bundle.v0` semantics and persists:

- source, conservative logical identity and identity method;
- deterministic content-derived version id and predecessor;
- exact archived provider payload plus its SHA-256;
- exact extracted UTF-8 content plus its SHA-256;
- run id, first-seen and version-observed UTC instants;
- mapping digest and immutable ticker links with `linked_at`;
- ledger sequence, prior record hash and record hash;
- collector repository, commit and request-fingerprint identities.

Provider bytes and extracted content are available only inside the protected
evidence store and test fixtures. Aggregate validation reports must not export
payload, content, URL, provider identifier, ticker list or per-record values.

`provider_id` is preferred only when the exact response supplies a nonempty
provider identifier. Otherwise identity uses the integrated exact-URL SHA-256
fallback: fragment removal only, with no other normalization. A candidate with
neither admissible identity is rejected and counted. Equal logical identity and
content digest is a repeat sighting; changed content is a new immutable version.

The mapping version is the SHA-256 of the exact versioned mapping artifact used
by the run. Mapping occurs after the complete response is received. Link time
cannot precede `version_observed_at`; a later mapping version never rewrites or
backdates an earlier link.

## Run, clock and atomic acceptance

One collector invocation has one lowercase UUID and the registered UTC runner
bracket:

1. `started_at` immediately before the first provider request;
2. `response_received_at` only after all registered response pages are received;
3. extraction, identity, content hashing and ticker mapping;
4. canonical aggregate staging and `completed_at` immediately before the
   transactional append;
5. transactional append of all new versions and one accepted-run manifest,
   followed by durable acknowledgement and workflow completion evidence.

Runner instants are recorded facts, not yet authenticated clocks. The accepted
run additionally binds repository, deployed commit, GitHub workflow name/run id,
attempt, event, runner start/completion timestamps, and the SHA-256 of its
canonical aggregate artifact. That later external workflow evidence can bound
deployment and clock plausibility; it cannot backdate availability. The
persisted `completed_at` is therefore a lower bound on database acceptance, not
a claim that acknowledgement had already occurred. The acknowledged transaction
and workflow completion provide later independently auditable bounds without
requiring an append-only manifest update.

Every registered provider request role and page must succeed. Timeout, HTTP
error, malformed response, pagination uncertainty, extraction exception,
counter mismatch, index/schema mismatch, partial write, ledger-head conflict or
artifact failure rejects the run. A rejected run produces no accepted-run
manifest and no event-version commit. Failure details remain redacted and may
be recorded only in ordinary workflow diagnostics.

All event-version inserts plus the accepted-run manifest occur in one Mongo
transaction with majority read concern, majority write concern and journaled
acknowledgement. The manifest is inserted last inside the transaction. A
zero-new-version run still appends one accepted-run manifest and preserves the
prior ledger head. Transaction or acknowledgement uncertainty fails closed.

GitHub workflow concurrency must serialize all prospective runs under one fixed
group with `cancel-in-progress=false`. The database also enforces unique run id,
version id, ledger sequence and accepted output-head constraints. An observed
conflict fails; runtime code does not repair, renumber or overwrite evidence.

## Coverage and overlap

The dormant implementation does not schedule or invoke the collector. It must
encode a fixed proposed overlap of seven complete UTC calendar days plus the
current partial day for each registered provider request role. It must paginate
to declared exhaustion under fixed bounds and count pages, candidates, exact
repeats, new versions and rejected candidates.

The dormant contract fixes `max_pages_per_role=100`,
`max_candidates_per_run=25000`, `max_new_versions_per_run=5000` and
`max_payload_bytes_per_candidate=1048576`. Reaching any bound before declared
exhaustion rejects the whole run as `BOUND_EXHAUSTED`; no partial prefix is
accepted or reported as complete. These are operational safety bounds, not
empirical tuning parameters. They may change only through an outcome-blind
preregistered amendment before activation.

Seven-day overlap is an instrument setting, not proof of provider completeness
or revision coverage. Any activation contract must revalidate that the pinned
FMP endpoints support the exact request/pagination semantics and must list the
request roles. If endpoint behavior cannot prove bounded exhaustion, activation
is blocked or the estimand is narrowed before outcomes.

No collected record is eligible for a scientific history merely because it is
stored. A later source/decision-clock audit must establish an accepted interval,
deployment continuity, clock rule, safety margin, coverage limitations and
common-cohort consequences before `history_construction_permitted` can change.

## Retention and authority

Before activation, the operator must approve a retention rule compatible with
the source licence and scientific reproducibility. The minimum proposed rule is
retention through the complete Phase-IV evaluation and five years after its
final research artifact. If that rule conflicts with source rights, activation
is blocked until a lawful separately registered alternative exists; runtime
code cannot silently shorten retention.

The deployment evidence must enumerate every application, workflow and human
with write authority to the new namespaces for the accepted interval. Unknown
or broader write authority does not invalidate engineering collection, but it
keeps source authentication and confirmatory history blocked.

## Agentic implementation graph

| Node | Input to immutable output | Failure invariant | Permitted side effects in dormant PR |
| --- | --- | --- | --- |
| deployment manifest validator | exact JSON to frozen binding | target/protocol/storage/flags must match this contract | none |
| request planner | explicit cutoff and roles to bounded UTC windows/pages | seven-day overlap; no max-legacy-date shortcut | none |
| response normalizer | synthetic provider pages to typed candidates | exact schema/limits; no imputation | none |
| version builder | candidate + frozen prior state to immutable version/repeat/rejection | protocol identities and clocks exact | none |
| transaction planner | versions + prior head to immutable write plan | insert-only operations and reconciled manifest | none |
| aggregate serializer | accepted synthetic plan to canonical report | no source values; scientific blocks fixed | none |
| I/O interfaces | protocol definitions only | no production adapter or credential discovery in dormant PR | none |

Domain nodes are deterministic, frozen and independently tested. I/O is defined
by interfaces and exercised with synthetic fakes only. Importing or testing the
module cannot read environment values, open a network connection, connect to
Mongo or mutate a workflow.

## Deployment manifest and fixed states

This increment may implement a fail-closed validator for a machine-readable
manifest with exact target/source/protocol/storage/clock/coverage/retention and
permission fields. Its only accepted engineering state is
`PASS_PROSPECTIVE_DEPLOYMENT_CONTRACT`.

Every accepted manifest and report states:

- `implementation_permitted=true` only for a disabled synthetic-tested writer
  PR from the pinned parent;
- `activation_permitted=false`;
- `production_source_access_permitted=false`;
- `production_storage_mutation_permitted=false`;
- `source_authenticated=false`;
- `clock_authenticated=false`;
- `coverage_authenticated=false`;
- `history_construction_permitted=false`;
- `training_permitted=false`;
- `outcome_access_permitted=false`;
- `model_fitting_performed=false`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`.

No CLI, manifest field or engineering test can promote these values.

## Required validation

The contract/manifest increment must test exact schema, target repository id,
commit/tree/blob identities, protocol contract hashes/commits, isolated
namespaces, operation allowlists, transaction policy, clock order, overlap,
retention proposal, credential non-disclosure and every fixed permission flag.
State must be immutable, canonical and input-order independent. Invalid input
must fail without echoing rejected values or producing an accepted report.

Regression gates are scoped Ruff, strict mypy, all inherited/unit/functional
tests, all prior Phase-IV reproductions, collector-lineage validation,
disposable package build, source preservation before/after, current-head CI and
human review. No production Mongo service, FMP endpoint or secret is used.

## Promotion sequence

1. Integrate this deployment contract/manifest only after current-head review.
2. Read the target repository's governing instructions and open a separate
   dormant implementation PR from the exact pinned parent.
3. Prove pure nodes and fake transaction boundaries; keep workflows disabled.
4. Review source licence, index/schema provisioning, dedicated credentials,
   writer authority and request semantics.
5. Register and review a separate activation manifest with the exact deployment
   commit/workflow and a prospective start instant.
6. The human operator provisions storage/secret and explicitly activates.
7. Audit multiple accepted runs before considering a decision-clock binding.

No later step is implied by approval of an earlier one. No outcome-driven
retuning is permitted.

## Current authorization

This commit authorizes only a machine-readable deployment manifest, its pure
validator, deterministic synthetic tests/report and repository validation. It
does not authorize changes to `theresistance-back`, production collection or
workflow activation. Human merge approval is required after a concrete PR and
current-head validation.
