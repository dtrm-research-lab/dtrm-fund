# Phase IV prospective activation readiness v0 — progress

Date: 2026-09-12.

## Scope

This increment implements the pure readiness review preregistered in
`DTRM_PHASE4_PROSPECTIVE_ACTIVATION_READINESS_V0.md`. It sits between the merged
dormant prospective writer and any later runtime-adapter, provisioning or
activation proposal.

It does not activate a provider or workflow, connect to Mongo, inspect secrets,
construct prospective history, fit a Temporal State representation, access
outcomes or execute MM1.

## Registered ancestry

- Scientific parent integration:
  `cdd78c38f8b543bc8a06f6fbca5f852926682621`.
- Readiness preregistration:
  `dde70ab0e58a9c48ba1be0dc2894ac0d2b435e18`.
- First implementation:
  `f1af66500698ca5432e3342291e4f18b6db39473`.
- Integrated dormant backend writer:
  `tech-com-UA00001/theresistance-back@e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5`,
  tree `2b5422f554119ecf48663d5506d9fdd38ab7738f`.
- Validated dormant feature head preserved as merge parent:
  `9eab8ee4b6ac9f7a0f67550a0e75e2489a5bc7d7`.

The readiness manifest binds the exact merged domain, application, ports and
ADR blobs rather than trusting a moving branch name.

## Public provider evidence boundary

The FMP stable developer documentation observed on 2026-09-12 documents the
registered `fmp-articles`, `news/general-latest` and `news/stock-latest`
endpoint identities and shows page/limit examples. This evidence is recorded as
`DOCUMENTED` endpoint identity only.

It does not authenticate the date-window, ordering, terminal pagination,
bounded-exhaustion, revision or late-arrival semantics required by the proposed
prospective capture design. Those readiness flags therefore remain false.

The public FMP Terms of Service observed on the same date make the applicable
API/data rights dependent on the account or Order Form and contain restrictions
on unauthorized copying/downloading plus obligations around stored FMP data.
No account-specific or written authorization was inspected. Consequently this
increment does not infer permission to archive exact payload/content or to use
the proposed retention horizon; the licence/retention gate remains false.

## Pure readiness implementation

The implementation adds:

- a canonical machine-readable readiness manifest;
- a frozen deterministic validator with exact recursive schema/value checks;
- normalization only for the two policy sets whose order is not evidence
  (`dormant_writer.files` and `provider.roles`);
- direct rejection of Mongo URI, API-key, authorization-header, bearer-token and
  private-key shaped material without echoing rejected values;
- an offline CLI with no-overwrite output semantics;
- a canonical aggregate review report;
- acceptance/failure tests covering writer identity, provider evidence,
  licence, storage, authority, runtime, scientific promotion, secrets and CLI
  behavior.

The v0 validator cannot promote readiness. Its accepted conclusion is fixed to
`PASS_PROSPECTIVE_ACTIVATION_READINESS_REVIEW` for engineering and `BLOCKED` /
`BLOCKED_PROSPECTIVE_DEPLOYMENT` for readiness/science.

## First-head validation evidence

GitHub push workflows for implementation head
`f1af66500698ca5432e3342291e4f18b6db39473` passed before this evidence update:

- `Phase IV gates` run `34683099206`: PASS;
- `Tests` run `34683099211`: PASS;
- source preservation before and after: `PASS_SOURCE_PRESERVATION`, 157 inherited
  files and original Stage-0 contract intact;
- scoped Ruff: PASS;
- strict mypy: PASS, 25 source files;
- full test suite: 791 passed, 6 skipped;
- all prior canonical Phase-IV evidence reproduced;
- synthetic Mongo job: PASS;
- disposable wheel build: PASS.

The six skips are the existing expected dedicated-Mongo cases in the general
suite; the separate synthetic-Mongo job passed.

## Current scientific state

`BLOCKED_PROSPECTIVE_DEPLOYMENT` remains the correct state. The dormant writer
merge and the readiness validator improve provenance and falsifiability but do
not establish source/clock/coverage authentication.

The currently blocking readiness dimensions are:

1. account-specific FMP licence/retention authority;
2. exact provider request/pagination/exhaustion semantics;
3. one-time schema/index provisioning evidence;
4. dedicated least-privilege credential evidence;
5. complete writer-authority enumeration;
6. a separately preregistered disabled runtime adapter/workflow;
7. a separately preregistered prospective UTC start instant.

No protected outcome has been accessed and no Phase-IV representation choice has
been made in response to results.

## Next permitted operation

After current-head CI and human integration review, resolve the source-rights
boundary using sanitized account-specific evidence. A later runtime adapter and
provisioning procedure require their own preregistered increment. Temporal State
history construction remains downstream of actual prospective activation and
multiple accepted-run audits.
