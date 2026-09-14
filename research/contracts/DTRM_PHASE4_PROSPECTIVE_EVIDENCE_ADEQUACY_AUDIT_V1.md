# DTRM Phase IV — Prospective Evidence Adequacy Audit v1

**Status:** preregistered design; implementation permitted; capture activation remains forbidden.

## Scientific purpose

Freeze, before periodic evidence capture begins, the deterministic rule that will decide whether the registered Phase IV prospective interval contains enough source evidence to proceed to an outcome-blind Temporal State representation preregistration.

This audit evaluates evidence availability and integrity only. It does not inspect market outcomes, model performance, MM1 decisions, or any downstream treatment effect.

## Lineage

- Scientific parent integration: `ca7ef0570281f6a1143d7a93efae5d69edc2b8a4`
- Prospective temporal evidence registration: `243797ee398b43f6684ce7a43057711167ed79ba`
- First accepted live backend run: `34777031881`
- First accepted artifact digest: `sha256:661d8b9b701af85655a14ad49f54dd9c48634ff83411fe0cd8ed94f50b8644b5`
- Registered request fingerprint: `932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`

The exact backend temporal-index integration and the exact 14-day UTC interval will be bound by a later activation statement after the temporal-index implementation is merged. This document does not authorize that activation.

## Frozen interval geometry

The inherited Phase IV prospective-evidence contract remains unchanged:

- 14 consecutive UTC calendar days;
- four target opportunities per UTC day;
- target clock times: `00:15`, `06:15`, `12:15`, `18:15` UTC;
- exactly 56 registered target slots;
- minimum 48 accepted slots;
- missing slots are never replaced or backfilled;
- no early stopping and no early scientific pass.

## Slot identity

After activation binds `start_utc_day`, slot indices are deterministic:

- slot `0` = `start_utc_day 00:15:00Z`;
- slots increase first by the four fixed daily clock times and then by UTC day;
- slot `55` = day 14 at `18:15:00Z`.

Every target timestamp must therefore map to exactly one integer slot in `[0, 55]`. Duplicate evidence records for one target slot invalidate that slot rather than increasing the accepted count.

## Accepted-slot rule

A target slot is `ACCEPTED` only when all of the following are true:

1. the evidence was produced by the registered periodic workflow through GitHub Actions event `schedule`; `workflow_dispatch`, reruns intended as backfill, local executions, or other triggers never count toward the 56 slots;
2. the triggering cron expression is one of the four registered cron expressions and maps to that target slot;
3. the capture run starts no earlier than its target timestamp and no later than **120 minutes** after it;
4. the run is associated with the backend commit/tree bound in the later activation statement;
5. the registered request fingerprint matches exactly;
6. the private raw probe contract succeeds for all nine observations;
7. the derived temporal-index contract succeeds;
8. the raw artifact and derived temporal-index artifact each have a valid SHA-256 digest recorded in the source-value-free slot record;
9. the GitHub run identifier is a positive integer and is unique across accepted slots;
10. no contract mismatch, duplicate logical identity, malformed source evidence, output-integrity failure, or other registered fail-closed error occurred.

The 120-minute schedule-lag bound is frozen before activation and may not be relaxed because of observed capture success or failure.

## Non-accepted slots

Every target slot that is not accepted is classified as exactly one of:

- `MISSING`: no eligible scheduled run exists for the target slot;
- `FAILED`: an eligible scheduled run exists but its bounded raw probe or temporal-index derivation fails;
- `LATE`: the eligible scheduled run begins more than 120 minutes after target;
- `DUPLICATE`: more than one otherwise-eligible scheduled evidence record claims the same target slot;
- `CONTRACT_MISMATCH`: lineage, commit/tree, request fingerprint, workflow/event, cron, digest, or slot identity does not match the activation/evidence contract.

These classifications are metadata-only and are never repaired through a later replacement capture.

## Finalization clock

The audit remains `PENDING_INTERVAL` until both conditions hold:

1. all 56 registered target timestamps are in the past; and
2. 120 minutes have elapsed after slot 55's target timestamp.

Before that clock, neither reaching 48 accepted slots nor reaching any other threshold permits scientific closure.

## Final evidence gate

After the finalization clock:

- `PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1` iff accepted slots >= 48;
- otherwise `FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1`.

A PASS authorizes only the next preregistration step: defining and freezing the outcome-blind Temporal State representation over the accepted prospective evidence. It does **not** authorize outcome access, Temporal State outcome fitting, MM1 execution/evaluation, Phase III mutation, public redistribution of raw provider data, or provider-rights claims.

A FAIL does not authorize retroactive backfill, extension, replacement slots, threshold relaxation, or outcome-driven redesign. Any new evidence campaign would require a new preregistration with explicit scientific justification.

## Audit input surface

The implementation shall consume only a source-value-free evidence ledger containing:

- activation statement identifier/digest;
- bound start/end UTC days;
- bound backend commit/tree;
- fixed request fingerprint;
- one record per observed scheduled attempt with target slot identity, target UTC timestamp, GitHub event and cron, GitHub run id, runner start UTC clock, success/failure code, raw artifact digest, and temporal-index digest.

The audit must not require article URLs, titles, content, provider IDs, tickers, market outcomes, portfolio values, predictions, MM1 decisions, or any other source/provider value.

## Engineering requirements

- pure deterministic audit core;
- immutable input models;
- exact schema validation and SHA-256 validation;
- duplicate slot/run detection;
- fail closed on malformed clocks or lineage;
- deterministic canonical JSON report;
- unit, functional, and regression tests covering 56/56 PASS, exactly 48 PASS, 47 FAIL, premature PENDING, missing, failed, late, duplicate, manual-trigger exclusion, wrong request fingerprint, wrong backend lineage, and malformed digests;
- inherited Phase III source-preservation gate remains mandatory.

## Explicit permissions

Permitted by this preregistration:

- implement and test the metadata-only adequacy auditor;
- implement source-value-free per-slot evidence records needed by that auditor;
- configure, but not activate, the fixed periodic workflow.

Still forbidden until a later explicit human activation gate:

- periodic capture activation;
- binding/starting the live 14-day evidence interval.

Still forbidden after activation unless separately authorized by a later scientific gate:

- confirmatory history construction;
- outcome access;
- Temporal State outcome fitting/tuning;
- MM1 execution/evaluation;
- Phase III policy mutation;
- public raw FMP redistribution.
