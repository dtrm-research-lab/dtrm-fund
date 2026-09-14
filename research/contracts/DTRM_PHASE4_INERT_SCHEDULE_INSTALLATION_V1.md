# DTRM Phase IV — Inert schedule installation amendment v1

Date: 2026-09-14. Status: **PREREGISTERED_BEFORE_SCHEDULE_INSTALLATION_OR_PERIODIC_CAPTURE**.

Scientific parent: `56952d9c9a6f00a79e8ee2e52765853be58edaae`, tree `9ba1bd4f7565268af0f5c409d073fa7672bb58f8`.

Backend dormant lineage anchor: `tech-com-UA00001/theresistance-back@974a7a744642cc8268ca5972df4ef208f629ed2b`, tree `0edcbca9d38b3a35b9b6a7b5fbb32b04d67119c9`.

This amendment resolves the pre-activation provenance problem identified during review of the post-merge binding readiness contract. It permits engineering installation of the already preregistered cron geometry while preserving a hard distinction between **schedule presence** and **periodic capture activation**.

## Decision

A descendant backend increment may add exactly these four GitHub Actions cron expressions to `.github/workflows/phase4_fmp_news_temporal_capture_v1.yml`:

- `15 0 * * *`
- `15 6 * * *`
- `15 12 * * *`
- `15 18 * * *`

The workflow identity remains `phase4_fmp_news_temporal_capture_v1`.

Schedule installation is permitted only if scheduled capture is fail-closed and inert by default. The scheduled capture job must not make an FMP request, mutate private evidence, upload a campaign artifact, emit a failure record, or make a counting decision unless the repository variable `PHASE4_PROSPECTIVE_CAPTURE_ARMED` is exactly the lowercase string `true` **and** the exact activation statement v2 has first been successfully verified against the runtime revision, registered start and finite campaign target interval.

Missing, empty, malformed or any other arm value means **unarmed**. The default state is unarmed. Manual `workflow_dispatch` may remain available only as diagnostic/non-counting behavior under the previously registered rules.

## Activation material

Arming alone is insufficient. Before **any scheduled side effect**, the runner must obtain and validate the exact source-value-free activation statement v2 using these repository-variable names:

- `PHASE4_ACTIVATION_STATEMENT_B64`
- `PHASE4_ACTIVATION_STATEMENT_ID`
- `PHASE4_ACTIVATION_STATEMENT_SHA256`

The decoded statement must pass the existing fail-closed backend `dtrm.phase4.prospective_activation_statement.v2` verifier before any provider access, private evidence mutation, artifact upload, failure-record emission, or counting decision. The verified binding must match the actual schedule-bearing backend commit/tree, workflow path/blob/identity, ordered provider roles, registered request fingerprint and canonical `prospective_start_utc`.

The runner must then derive the scheduled target from the runner start clock and registered cron. A scheduled side effect is permitted only when that derived target is one of the frozen campaign slots **0 through 55 inclusive**. A target before slot 0 or after slot 55 is outside the activation interval and must fail closed before every campaign side effect.

If the statement is missing, malformed, stale, expired, digest-mismatched, not activation-permitted, outside its registered 14-day interval, or inconsistent with runtime provenance, the scheduled event must terminate without a campaign artifact, slot/failure record, counting decision, provider request or private evidence write. Such an event is not a campaign opportunity and cannot later be backfilled.

No secret value belongs in the activation statement. The FMP credential remains a GitHub secret and is never copied into scientific evidence, contracts, logs or arguments.

## Pre- and post-campaign scheduled events

GitHub may emit cron events after the schedule-bearing workflow reaches the default branch but before the campaign is armed and fully statement-verified, and it may continue emitting cron events after slot 55 while the workflow remains installed. Both classes are scheduler observations only.

Before slot 0 and after slot 55, scheduled events must terminate before all campaign side effects and are never campaign opportunities, missing slots, failures, reruns or backfill candidates. The arm variable remaining `true` after slot 55 does not extend the campaign and grants no provider access, evidence mutation, failure record, artifact upload or counting decision.

The 14-day/56-opportunity interval begins only from the separately registered `prospective_start_utc` in the exact activation statement v2, after the final human activation authorization. The activation instant must remain on the selected UTC day and strictly before `00:15:00Z`.

Installing the cron therefore does not select day 0, consume a target opportunity, extend the campaign beyond slot 55 or change the scientific estimand.

## Required post-merge scheduled-revision addendum

After the inert schedule-bearing backend increment is merged, but before arming, a separate scientific addendum must bind the exact resulting:

- backend merge commit and tree;
- workflow path, Git blob and stable identity;
- exact four cron expressions;
- ordered provider roles and registered request fingerprint;
- ancestry to dormant backend merge `974a7a744642cc8268ca5972df4ef208f629ed2b`;
- exact runtime arm-gate, statement-verification and finite-slot semantics.

The final activation statement v2 must bind that exact merged schedule-bearing revision. A PR-head SHA or pre-merge prediction is insufficient.

## Frozen campaign geometry

No scientific parameter changes here: 14 consecutive UTC days, targets `00:15`, `06:15`, `12:15`, `18:15`, exactly 56 opportunities (slots 0–55), minimum 48 accepted slots, at least one accepted first-day slot and one accepted last-day slot, no backfill, no early stopping, and only scheduled attempt 1 may be counting-eligible.

## Frozen prohibitions

Until campaign completion and the preregistered adequacy audit PASS, all remain forbidden: confirmatory-history construction, Temporal State outcome fitting, outcome access, MM1 execution, Phase III mutation and public raw-provider-data redistribution.

This amendment does **not** authorize setting the arm variable, selecting `prospective_start_utc`, claiming schema/credential/writer authorization, accessing provider data, or starting the campaign. Those remain later explicit gates.

## Machine-checkable statement

`research/contracts/DTRM_PHASE4_INERT_SCHEDULE_INSTALLATION_STATEMENT_V1.json`

Canonical SHA-256: `375c04c4e537095df21db10919f9f3d8e827a6886a4c1db902dc30ccbcb11c3c`.
