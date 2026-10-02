# DTRM Phase IV — v3 external scheduler architecture v0

**Status:** preregistered implementation architecture only. Scheduler provisioning and scientific activation remain blocked.

## Purpose

Bind the operational architecture that will replace GitHub `schedule` after the decisive v2 scheduler-latency failure, without changing any scientific parameter and without selecting a future campaign start.

The already validated GitHub execution boundary remains the dormant `repository_dispatch` workflow `phase4_fmp_news_temporal_capture_v3`. The real non-counting diagnostic established that the `repository_dispatch -> validated runner` path can start within the frozen 120-minute limit. That diagnostic used a local scheduler identity and therefore does not bind the campaign scheduler.

## Selected architecture

The external scheduler implementation is:

`AWS EventBridge Scheduler -> AWS Lambda dispatcher -> GitHub repository_dispatch -> dormant Phase IV v3 workflow`

The scheduler uses **56 one-time `at(...)` schedules**, one for each preregistered target. This mirrors the exact scientific slot geometry instead of relying on an indefinitely recurring cron. Each schedule is evaluated in UTC and uses `FlexibleTimeWindow=OFF`.

AWS EventBridge Scheduler has at-least-once target-delivery semantics. Therefore the architecture does not interpret scheduler delivery as exactly-once scientific evidence. Duplicate protection is an explicit fail-closed boundary.

## Duplicate / retry boundary

Before any GitHub network request, the Lambda dispatcher must perform a durable DynamoDB conditional put keyed by the exact campaign statement identity, target slot, target UTC timestamp and deterministic dispatch identifier.

The claim is created **before** attempting the GitHub POST. If the claim already exists, the invocation terminates without a GitHub request. EventBridge/Lambda retries therefore cannot silently create an additional GitHub run for the same scientific target.

After the first durable claim, the dispatcher permits at most **one** GitHub `repository_dispatch` POST attempt. A timeout, non-success response, Lambda failure after the claim, or other ambiguous delivery is treated as a missed opportunity; it is not repaired, retried as a new target or backfilled. This intentionally prefers loss of one slot over duplicate scientific evidence.

The deterministic dispatch identifier already frozen in the backend remains derived from campaign statement identity/digest, target slot and target UTC timestamp.

## Authentication and secrets

The dispatch envelope remains authenticated with HMAC-SHA256. The campaign HMAC material and the GitHub credential must not be stored in source control. The AWS dispatcher must retrieve sensitive material from AWS Secrets Manager under least-privilege IAM.

The GitHub credential is operationally limited to the target backend repository and only the permission required to create the dedicated `repository_dispatch` event. The exact credential authority and secret-provisioning evidence must be bound before activation.

The dispatcher has no FMP credential, provider adapter, provider values, outcomes or MM1 access.

## Frozen scientific invariants

This architecture does not alter:

- Phase II control or frozen Phase III/MM1;
- the three provider roles or request fingerprint;
- the temporal-slot schema;
- 14 consecutive UTC days;
- target clocks `00:15`, `06:15`, `12:15`, `18:15` UTC;
- exactly 56 opportunities and minimum 48 accepted slots;
- first-day and last-day coverage requirements;
- start lag <=120 minutes;
- run duration <=60 minutes;
- completion lag <=180 minutes;
- publication lag <=60 minutes;
- first-attempt-only eligibility;
- no backfill and no early stopping.

## Remaining gates before any campaign activation

This document does **not** bind an AWS account, AWS region, Lambda ARN, EventBridge schedule-group/schedule ARNs, DynamoDB table ARN, Secrets Manager secret ARNs, GitHub credential authority, campaign start, or a campaign activation statement.

Before v3 can be armed, a later increment must:

1. implement and test the provider-neutral AWS dispatcher and fail-closed conditional claim;
2. provision the exact AWS resources without provider access;
3. record source-value-free AWS resource identity and IAM/authentication evidence;
4. run one separately human-authorized, non-counting real diagnostic through the **final AWS scheduler identity**;
5. bind the resulting scheduler-to-GitHub timing evidence and exact backend/workflow provenance;
6. create and integrate a new future activation statement;
7. receive fresh explicit human activation authorization before slot 0.

Until all of those gates pass, `activation_permitted=false`, `counting_capture_permitted=false`, and real scheduler diagnostics remain separately authorization-gated.
