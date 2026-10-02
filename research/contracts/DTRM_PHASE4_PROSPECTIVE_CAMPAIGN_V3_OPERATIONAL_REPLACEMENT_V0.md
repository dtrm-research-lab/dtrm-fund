# DTRM Phase IV — Prospective Campaign v3 Operational Replacement v0

**Status:** preregistered operational design only; implementation permitted; activation forbidden.

## Scientific purpose

Replace only the failed scheduling transport from campaign v2. No scientific parameter is retuned from outcomes or from observed provider values.

The Phase IV question remains unchanged: whether historical-event representation improves the frozen robust policy beyond point-in-time information.

## Invariants preserved

The superseding campaign must preserve:

- Phase II probabilistic-state control;
- frozen Phase III MM1 policy and solver;
- provider roles: `fmp_articles`, `general_latest`, `stock_latest`;
- request fingerprint `932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`;
- provisioned temporal slot schema;
- 14 consecutive UTC days;
- four targets per day at `00:15`, `06:15`, `12:15`, `18:15` UTC;
- exactly 56 target slots;
- minimum 48 accepted slots;
- at least one accepted first-day slot and one accepted last-day slot;
- start lag <=120 minutes;
- run duration <=60 minutes;
- completion lag <=180 minutes;
- publication lag <=60 minutes;
- no backfill;
- no early stopping;
- only the first counting attempt for a target may be eligible.

No provider-value, market-outcome, portfolio, prediction, MM1, or treatment-result information may influence this replacement.

## Operational diagnosis from v2

Campaign v2 failed because GitHub's `schedule` event itself was emitted several hours after nominal cron targets. The GitHub runner then started within seconds of event creation. The replacement therefore separates the UTC scheduler from GitHub's scheduled-event service while keeping GitHub Actions as the execution and private-artifact writer.

## v3 trigger architecture

The counting workflow shall be triggered by an **independent UTC scheduler** through an authenticated GitHub `repository_dispatch` event type dedicated to Phase IV v3.

The dispatch payload must contain only source-value-free scheduling metadata:

- campaign statement identifier;
- deterministic target slot;
- deterministic target UTC timestamp;
- dispatch identifier unique to that target;
- dispatch UTC timestamp;
- authentication/signature metadata needed by the preflight.

The scheduler must emit exactly one intended dispatch per registered target. Transport retries, if any, must preserve the same dispatch identifier and never create a new scientific target.

GitHub `schedule`, `workflow_dispatch`, local execution, reruns, and all other event types are non-counting for v3.

## Authentication and fail-closed requirements

Before exposing `FMP_API_KEY`, the workflow must verify:

1. event type is the exact registered `repository_dispatch` type;
2. campaign statement identifier/digest matches the later activation statement;
3. target slot and target timestamp are internally consistent with the frozen 56-slot geometry;
4. dispatch timestamp is not after the 120-minute target window;
5. dispatch authentication/signature validates against a secret not stored in source control;
6. runtime commit/tree and workflow path/blob/identity match the later activation binding;
7. request fingerprint, provider roles, schema identity, credential authority, and writer authority match the registered values.

Any failure stops before provider credential exposure.

## Counting clock

Scientific start lag remains measured from the registered target UTC timestamp to the actual validated capture start, not to dispatch creation.

A run starting after target +120 minutes is `LATE`, even if dispatch occurred on time.

A run starting before target is ineligible.

## Duplicate and retry semantics

Only `run_attempt == 1` can be counting-eligible.

Multiple source-value-free records claiming the same target remain non-repairable under the adequacy audit. Implementation must therefore prefer single-dispatch operation and fail closed rather than silently replace evidence.

No rerun may reconstruct a missing target.

## Pre-activation gates

Before any v3 campaign can be armed:

- backend implementation and tests must pass;
- Phase III source-preservation regression must pass;
- exact workflow blob and runtime commit/tree must be bound;
- scheduler identity and authentication evidence must be recorded;
- one separately authorized, non-counting real dispatch diagnostic must demonstrate that repository-dispatch creation and runner start remain within the preregistered timing bound;
- a new prospective activation statement must bind a future start date;
- explicit human activation authorization is required;
- arming must occur before day-0 slot 0.

No activation date is selected by this document.

## Permissions

Permitted now:

- implement the v3 repository-dispatch workflow and its fail-closed preflight;
- implement a provider-neutral dispatcher contract and synthetic tests;
- implement source-value-free diagnostic evidence;
- test all failure paths without provider access.

Forbidden now:

- periodic v3 capture activation;
- real provider access through v3;
- confirmatory history construction;
- outcome access;
- Temporal State outcome fitting;
- MM1 execution/evaluation;
- Phase III mutation;
- public raw-provider redistribution.
