# DTRM Phase IV — Scheduled revision addendum v1

Date: 2026-09-14. Status: **PREREGISTERED_SCHEDULED_REVISION_BOUND_UNARMED**.

Scientific parent: `dtrm-research-lab/dtrm-fund@a7e03fdd72e4b2132d877d7e30785803398650a9`, tree `02e4517b021a0337fef49416e0d5fba76b8182f4`.

Backend schedule-bearing merge: `tech-com-UA00001/theresistance-back@bf844932f8bb3e6773c329a45135fd754c6d8342`, tree `c090c3cb41165ee513de812dec562f497407df62`.

Validated backend PR head: `ce04527c9a36c9055c9180a534dda0d91ba69952`.

Dormant backend ancestry anchor: `974a7a744642cc8268ca5972df4ef208f629ed2b`.

This addendum performs the required post-merge scientific binding of the exact schedule-bearing backend revision. It changes no scientific parameter and grants no activation authority.

## Exact merged workflow binding

The registered workflow is exactly:

- path: `.github/workflows/phase4_fmp_news_temporal_capture_v1.yml`
- Git blob: `0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22`
- stable workflow identity: `phase4_fmp_news_temporal_capture_v1`
- cron expressions, in registered order:
  - `15 0 * * *`
  - `15 6 * * *`
  - `15 12 * * *`
  - `15 18 * * *`

The exact merged backend revision descends from the dormant backend merge `974a7a744642cc8268ca5972df4ef208f629ed2b`; the validated PR head is the second parent of the backend merge commit.

## Provider and request binding

The ordered provider roles remain frozen as:

1. `fmp_articles`
2. `general_latest`
3. `stock_latest`

Registered request fingerprint SHA-256:

`932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`

No provider payload, credential, source value or outcome is contained in this addendum.

## Runtime arm and activation boundary

The schedule-bearing workflow remains inert by default. The scheduled capture job may run only when repository variable `PHASE4_PROSPECTIVE_CAPTURE_ARMED` is exactly lowercase `true`, and that arm value alone grants no campaign side effect.

The exact activation statement v2 must still be provisioned later through the registered source-value-free variables and must verify the exact runtime commit, tree, workflow path, workflow blob, workflow identity, registered start, provider roles and request fingerprint before any scheduled provider access, private evidence mutation, failure-record emission, artifact upload or counting decision.

This addendum records the present state as:

- schedule default armed: **false**;
- periodic capture activation permitted: **false**;
- activation statement provisioned: **false**;
- `prospective_start_utc` bound: **false**;
- credential/writer authority claimed: **false**.

## Credential scoping

Installation and activation preflight are credential-free. `FMP_API_KEY` is unavailable to checkout, Python setup, package installation, provenance derivation and activation preflight. It is scoped only to the provider-capture step after successful activation/runtime verification.

No scientific contract, log, argument or artifact may contain the credential value.

## Finite-slot and rerun semantics

The frozen campaign remains 14 consecutive UTC days, four targets per day, exactly 56 opportunities, slots 0–55 inclusive.

Scheduled attempt 1 derives its target from the first-attempt runner start clock and the registered cron. Targets outside slots 0–55 fail closed before every campaign side effect.

A scheduled rerun must never derive a replacement target from the rerun clock. Until an immutable attempt-1 record keyed by the same GitHub `run_id` is separately implemented and validated, every scheduled rerun fails closed before provider access, evidence mutation, failure recording, artifact upload or counting. Reruns remain non-counting.

Manual `workflow_dispatch` remains diagnostic and non-counting.

Scheduled side effects after slot 55 remain forbidden even if the arm variable were later left set to `true`.

## Frozen downstream prohibitions

Until the prospective campaign completes and the preregistered adequacy audit passes, all remain forbidden:

- confirmatory-history construction;
- Temporal State outcome fitting;
- outcome access;
- MM1 execution;
- Phase III policy mutation;
- public raw-provider-data redistribution.

This addendum does **not** authorize setting `PHASE4_PROSPECTIVE_CAPTURE_ARMED`, provisioning activation variables, selecting `prospective_start_utc`, claiming schema/credential/writer authority, calling FMP or starting the 14-day campaign. Each remains behind a later explicit activation authorization.

## Machine-checkable statement

`research/contracts/DTRM_PHASE4_SCHEDULED_REVISION_ADDENDUM_STATEMENT_V1.json`

Canonical SHA-256: `98e245830a08b79423fc95c67033fa47aa066e00beaa1d4bf47f110e0ca93ac7`.
