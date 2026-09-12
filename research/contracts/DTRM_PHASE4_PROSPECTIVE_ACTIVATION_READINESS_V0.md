# Phase IV prospective activation readiness contract v0

Date: 2026-09-12. Status: REGISTERED_BEFORE_READINESS_IMPLEMENTATION_OR_ACTIVATION.
Parent integration: `cdd78c38f8b543bc8a06f6fbca5f852926682621`.

## Purpose and scientific boundary

This addendum defines the outcome-blind readiness gate between the integrated
credential-free prospective-news shadow and any later activation manifest.

It inherits the Phase-IV prospective deployment contract and does not rewrite the
prospective capture protocol, dormant writer design, retrospective findings,
Phase-III/MM1 baseline, or the original Phase-IV research question.

The central scientific objective remains unchanged: determine whether a
historical event representation improves the already frozen robust policy beyond
point-in-time information. PRAGMA remains architectural inspiration only. No
Temporal State representation, embedding, Transformer, target, label, outcome,
MM1 execution, tuning or evaluation is permitted by this increment.

This contract authorizes only a pure machine-readable activation-readiness
review, deterministic validation, synthetic evidence and repository/public-
documentation binding. It does not authorize provider requests, production
Mongo access, collection/index creation, credential discovery, workflow
activation, production mutation or historical sequence construction.

## Integrated dormant writer binding

The reviewed dormant writer is now integrated in
`tech-com-UA00001/theresistance-back` at merge commit
`e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5`, tree
`2b5422f554119ecf48663d5506d9fdd38ab7738f`.

The merge has two parents:

- previously pinned production parent
  `7a8107e4451891535366acaf766348785ccc157b`;
- validated dormant feature head
  `9eab8ee4b6ac9f7a0f67550a0e75e2489a5bc7d7`.

The dormant graph remains isolated under the modern backend package and has no
production adapter, CLI, provider client, Mongo client, secret lookup, scheduler
or enabled workflow. The exact merged code paths to bind in the readiness
manifest are:

- `src/theresistance_backend/domains/markets/prospective_news.py`;
- `src/theresistance_backend/application/plan_prospective_news_capture.py`;
- `src/theresistance_backend/ports/prospective_news.py`;
- `docs/architecture/ADR-017-phase4-prospective-news-shadow-v0.md`;
- `docs/architecture/ADR-017A-phase4-prospective-news-clock-binding-v0.md`;
- `docs/architecture/ADR-017B-phase4-prior-state-causality-v0.md`.

A manifest mismatch in repository, commit, tree or bound blobs fails the
readiness review. Integration of the dormant writer is necessary but not
sufficient for activation.

## Readiness dimensions

Activation readiness is conjunctive. Every required dimension must be supported
by separately attributable evidence before an activation manifest may be
registered. Unknown, missing, contradictory or account-specific evidence that
has not been supplied remains blocking.

### 1. Provider endpoint identity and request semantics

The three registered provider roles remain exactly:

| Role | Endpoint |
| --- | --- |
| `fmp_articles` | `https://financialmodelingprep.com/stable/fmp-articles` |
| `general_latest` | `https://financialmodelingprep.com/stable/news/general-latest` |
| `stock_latest` | `https://financialmodelingprep.com/stable/news/stock-latest` |

On 2026-09-12 the public FMP documentation page at
`https://site.financialmodelingprep.com/developer/docs/stable` exposed these
stable endpoint identities and examples using `page=0&limit=20`.

That public page is sufficient to bind endpoint names only. It does not, for
this research contract, authenticate all semantics required by the proposed
seven-complete-day overlap: accepted date filters, ordering stability,
pagination termination, maximum page size, historical/revision visibility,
late-arrival behavior or a provider guarantee that an empty/short page proves
bounded exhaustion.

Therefore endpoint identity may be recorded as `DOCUMENTED`, while
`request_semantics_authenticated` and `bounded_exhaustion_authenticated` remain
false until separately reviewed evidence proves the exact behavior used by the
future adapter. No live probing is authorized by this contract.

Any later adapter must preserve the fixed safety bounds from the integrated
deployment contract. If provider semantics cannot prove bounded exhaustion, the
activation gate fails or the prospective estimand is narrowed by a new
outcome-blind preregistration before activation.

### 2. Source licence and retention authority

The integrated deployment design proposes storing exact provider payload bytes
and exact extracted content and retaining evidence through Phase-IV evaluation
and for five years after the final research artifact.

The public FMP Terms of Service observed on 2026-09-12 state that the applicable
data/APIs depend on the customer account or Order Form and that, absent prior
written approval, customers may not make unauthorized copies; the public
personal-use language also states that content may not be copied/downloaded
without prior written approval. The same terms require controls for locations
where FMP data is stored.

Those public terms do not establish that the user's actual subscription or any
Order Form grants the archival, research, retention and storage rights required
by the Phase-IV evidence design. They therefore cannot be treated as permission.

`licence_retention_authorized` is fixed false in this increment. Promotion
requires sanitized operator evidence of a specific FMP subscription/order/written
authorization that is compatible with:

- programmatic access to the three registered news roles;
- protected storage of exact response payload/content;
- the proposed retention horizon or a separately preregistered lawful
  alternative;
- research use within the intended project scope;
- any required storage-location/security obligations.

No contract, report or repository file may contain account credentials, API
keys, payment information, private order-form contents or other secrets. If the
rights cannot be established, activation remains blocked and the evidence design
must be revised before any provider request is made.

### 3. Storage schema and one-time provisioning

The target namespaces remain:

- `trumpMinMax.phase4ProspectiveNewsV0`;
- `trumpMinMax.phase4ProspectiveRunsV0`.

The legacy namespace `trumpMinMax.trumpNews` remains forbidden to the
prospective writer.

Before activation, a separately reviewed one-time operator procedure must define
and provision the exact schema validators and uniqueness constraints required by
the deployment contract. At minimum the evidence must establish constraints for
run identity, immutable version identity, ledger sequence and accepted
output-ledger head, plus the event/run document schemas expected by the future
adapter.

Runtime startup may verify these objects but may not create, repair, weaken or
silently migrate them. This readiness increment does not connect to Mongo and
does not assert that either prospective namespace currently exists.

`storage_schema_provisioned` is therefore fixed false.

### 4. Dedicated least-privilege credential

The future runtime credential must be dedicated to the two prospective
namespaces and permit only the registered read/insert behavior needed for
transactional capture. It must not reuse a broad application credential and
must have no permission on the legacy news collection.

The agent and CI must not inspect whether such a secret exists, its value, URI,
username or environment-variable contents. Readiness can later consume only a
sanitized operator assertion or independently safe metadata describing the
credential's scope.

`least_privilege_credential_provisioned` is fixed false.

### 5. Complete writer authority

Before source authentication can be considered, the project must enumerate all
applications, workflows and human/operator identities capable of writing the two
prospective namespaces during the proposed accepted interval.

Unknown or broader authority keeps confirmatory history blocked. The enumeration
must not disclose secret values. This increment performs no production
authorization query.

`writer_authority_enumerated` is fixed false.

### 6. Runtime adapter, workflow and concurrency

The integrated backend has only pure domain/application/port code. No production
FMP adapter, Mongo prior-state reader, transaction sink, activation CLI or
prospective workflow is authorized or present by virtue of the dormant merge.

A later engineering increment may be proposed only after this readiness
contract is integrated. It must descend from the exact integrated writer commit,
remain disabled, use explicit dependency boundaries, verify provisioned schema
without mutating it, redact failures, preserve insert-only semantics, and define
one fixed GitHub workflow concurrency group with
`cancel-in-progress=false`.

Creating that disabled adapter/workflow still does not activate it.

`runtime_adapter_validated` and `workflow_activation_ready` are fixed false in
this increment.

### 7. Prospective start and external clock evidence

No prospective scientific start instant is registered here.

A later activation contract must bind:

- exact backend deployed commit and tree;
- exact workflow file/blob and workflow identity;
- exact provider roles and request semantics;
- exact provisioned schema identity;
- sanitized evidence of credential scope and writer authority;
- explicit UTC prospective start instant chosen before the first authorized
  provider request.

The first accepted run may occur only after that instant. No legacy or
pre-start row can be promoted into confirmatory prospective history.

`prospective_start_registered` is fixed false and
`clock_authenticated` remains false.

## Agentic readiness graph

| Node | Input | Immutable output | Failure invariant | Side effects |
| --- | --- | --- | --- | --- |
| `normalize_readiness_manifest` | exact JSON | typed frozen state | exact schema only | none |
| `validate_dormant_writer_binding` | repository/commit/tree/blobs | bound writer | exact integrated writer required | none |
| `validate_provider_binding` | roles/endpoints/public-evidence labels | provider review | roles and endpoint strings exact; semantics cannot be promoted | none |
| `validate_licence_gate` | sanitized status only | licence review | retention authority stays false without approved evidence | none |
| `validate_storage_gate` | namespace/policy status | storage review | no claim of provisioning | none |
| `validate_authority_gate` | credential/authority status | authority review | no secret material; both remain false | none |
| `validate_runtime_gate` | adapter/workflow/start statuses | runtime review | no activation-ready promotion | none |
| `enforce_scientific_floor` | all readiness dimensions | blocked readiness state | histories/outcomes/training/fitting remain false | none |
| `serialize_readiness_review` | accepted state | canonical aggregate JSON | no secrets/account/source values | none |

Every node is deterministic and side-effect free. The implementation must not
read process environment variables, access a network, connect to Mongo, call
FMP, inspect GitHub secrets or mutate either repository.

## Machine-readable readiness state

The canonical manifest may represent evidence already established by immutable
repository/public-document bindings, but it must remain conservative.

The only permitted v0 conclusion is:

- `engineering_status=PASS_PROSPECTIVE_ACTIVATION_READINESS_REVIEW`;
- `readiness_status=BLOCKED`;
- `activation_permitted=false`;
- `production_source_access_permitted=false`;
- `production_storage_mutation_permitted=false`;
- `request_semantics_authenticated=false`;
- `bounded_exhaustion_authenticated=false`;
- `licence_retention_authorized=false`;
- `storage_schema_provisioned=false`;
- `least_privilege_credential_provisioned=false`;
- `writer_authority_enumerated=false`;
- `runtime_adapter_validated=false`;
- `workflow_activation_ready=false`;
- `prospective_start_registered=false`;
- `source_authenticated=false`;
- `clock_authenticated=false`;
- `coverage_authenticated=false`;
- `history_construction_permitted=false`;
- `training_permitted=false`;
- `outcome_access_permitted=false`;
- `model_fitting_performed=false`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`.

No manifest field, CLI flag or test fixture can promote these values in this
increment.

## Validation requirements

Implementation must:

- validate exact parent scientific integration and exact merged backend
  commit/tree/file identities;
- validate the three endpoint role/path bindings and distinguish endpoint
  documentation from authenticated request semantics;
- reject any attempt to claim licence/retention authority, storage provisioning,
  credential provisioning, writer-authority completion, runtime readiness,
  start registration or scientific promotion;
- reject connection strings, API keys, authorization headers, private-key
  material and other direct secret-shaped values;
- serialize only canonical aggregate readiness evidence;
- preserve all 157 inherited Phase-III files and the original Stage-0 contract;
- reproduce every prior Phase-IV canonical synthetic report;
- pass scoped Ruff, strict mypy, full inherited tests, package build,
  current-head CI and human review.

Public documentation observations are evidence about publicly visible text only.
They are not evidence about the user's account, subscription, Order Form,
provider completeness, production configuration or storage state.

## Promotion sequence after this increment

1. Integrate this readiness contract/review only after current-head validation
   and human approval.
2. Resolve the FMP licence/retention gate using sanitized account-specific or
   written-rights evidence. If incompatible, redesign and preregister before any
   provider request.
3. Register a separate disabled runtime-adapter/provisioning contract before
   implementing concrete provider/Mongo/workflow boundaries.
4. Human operator provisions schema/indexes and dedicated credential under the
   reviewed procedure; agent consumes only sanitized evidence.
5. Audit complete writer authority and exact provider request/pagination
   semantics.
6. Register a distinct activation contract binding exact deployed code,
   workflow, provisioned boundary and prospective UTC start instant.
7. Human operator explicitly activates.
8. Audit multiple accepted runs for continuity, source/clock/coverage limits and
   common-cohort consequences.
9. Only then may a separate Temporal State history-construction contract be
   proposed. Representation fitting and the frozen MM1 comparison require later
   preregistration and remain outcome-blind until their own gate opens.

No later step is implied by approval of an earlier one.

## Current authorization

This registration authorizes only the pure readiness manifest/validator,
synthetic review, repository binding and public-document evidence labels
described above. It does not authorize changes to `theresistance-back`, a live
provider call, production Mongo access, provisioning, secrets, workflow
activation, history construction, Temporal State fitting, outcomes or MM1.
