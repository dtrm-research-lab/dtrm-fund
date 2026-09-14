# DTRM Phase IV — Prospective Evidence Adequacy Review Amendment v3

**Date:** 2026-09-14  
**Status:** preregistered before periodic activation and before any registered campaign slot  
**Parent adequacy preregistration:** `835f5c6f01825abdaf9a3cc266f9ba1dfb24c55d`  
**Review amendment v1:** `44d82ac66d283196d1077b799a012a693f9ead7e`  
**Review amendment v2:** `ce02affb746f26cbc0121e9ccb5fbed705601209`  
**Inherited activation-readiness contract:** `DTRM_PHASE4_PROSPECTIVE_ACTIVATION_READINESS_V0.md`

## Purpose

This amendment resolves review-discovered provenance and finalization ambiguities before live periodic activation. It uses no provider observations from the future campaign, market outcomes, portfolio results, predictions, MM1 decisions, or protected outcome surface. The scientific campaign remains unchanged: 14 UTC calendar days, 56 registered target slots, minimum 48 accepted slots, first/last-day evidence, no replacement/backfill, and no early scientific pass.

## 1. Preserve the complete inherited activation binding

The later human-approved activation statement must preserve every binding category already required by the inherited activation-readiness contract rather than replacing that contract with a narrower calendar-day/backend tuple.

The registered activation statement schema for this campaign is therefore `dtrm.phase4.prospective_activation_statement.v2` with exactly these source-value-free fields:

- `schema_version`;
- `activation_statement`;
- `backend_commit`;
- `backend_tree`;
- `workflow_path`;
- `workflow_blob_sha`;
- `workflow_identity`;
- `provider_roles` — ordered exactly as `fmp_articles`, `general_latest`, `stock_latest`;
- `request_fingerprint_sha256` — the already registered request semantics fingerprint;
- `provisioned_schema_identity`;
- `credential_scope_status` — exactly `AUTHORIZED`;
- `credential_scope_evidence_sha256` — digest of sanitized non-secret evidence;
- `writer_authority_status` — exactly `AUTHORIZED`;
- `writer_authority_evidence_sha256` — digest of sanitized non-secret evidence;
- `prospective_start_utc` — explicit UTC instant chosen before the first authorized provider request;
- `periodic_capture_activation_permitted` — exactly `true`.

The adequacy auditor derives `start_utc_day` from the UTC calendar date of `prospective_start_utc`. It must verify the exact activation-statement bytes against a separately trusted human-approved statement identifier and SHA-256 digest before accepting any campaign ledger.

The auditor fails closed on schema drift, identifier/digest mismatch, non-canonical UTC start, wrong backend lineage, wrong workflow identity/blob/path, wrong provider roles, wrong request fingerprint, missing provisioned-schema identity, non-authorized credential/writer status, malformed authority-evidence digests, or missing activation permission.

No secret values, credentials, provider content, or raw authority material are placed in the activation statement.

## 2. Scheduled reruns retain target provenance but never count

Every observed `schedule` attempt retains its registered target identity, including reruns:

- `slot` is an integer in `[0,55]`;
- `target_at_utc` equals the deterministic target clock for that slot;
- `cron` equals the registered cron for that slot.

For `run_attempt == 1`, the record may participate in slot classification. For `run_attempt > 1`, the record is diagnostic/non-counting regardless of success and may never backfill, replace, or increase the accepted-slot count.

A rerun's target identity refers to the original registered opportunity and must not be re-derived from the rerun execution start time. Missing or contradictory target provenance fails closed.

## 3. Classify timeliness before duplicate invalidation

Finalization stability requires post-deadline records to be incapable of invalidating an already accepted timely slot.

For each target slot, the auditor first partitions first-attempt scheduled records by the frozen timing contract:

- start no earlier than target and no later than target + 120 minutes;
- completion not before start;
- run duration no more than 60 minutes;
- completion no later than target + 180 minutes;
- record publication not before completion;
- publication no more than 60 minutes after completion and no later than target + 240 minutes.

Records outside these bounds are `LATE` for timing purposes before duplicate resolution.

Then:

1. if more than one **non-late** first-attempt record claims the same slot, the slot is `DUPLICATE` and is not accepted;
2. if exactly one non-late first-attempt record exists, that record alone determines the slot's `ACCEPTED`, `FAILED`, or `CONTRACT_MISMATCH` status; additional late records cannot change that slot status;
3. if no non-late first-attempt record exists but one or more late first-attempt records exist, the slot is `LATE`;
4. if no first-attempt scheduled record exists, the slot is `MISSING`.

The report additionally serializes `late_first_attempt_records` as a metadata-only count so post-deadline arrivals remain visible without changing an already finalized accepted-slot count.

This rule does not permit backfill. It prevents evidence arriving outside the registered publication window from flipping a finalized PASS or invalidating a timely accepted opportunity.

## 4. Downstream prohibitions remain unchanged

Every report continues to serialize `false` for:

- `confirmatory_history_construction_permitted`;
- `temporal_state_outcome_fitting_permitted`;
- `outcome_access_permitted`;
- `mm1_execution_permitted`;
- `phase3_policy_mutation_permitted`;
- `public_raw_provider_data_redistribution_permitted`.

A PASS still authorizes only the next outcome-blind Temporal State representation preregistration.

## 5. Non-adaptation statement

These rules are fixed solely from preactivation contract-integrity review. They do not use campaign success/failure, provider-value content, market outcomes, model performance, or MM1 behavior. The 14-day geometry, four daily targets, 56 target slots, minimum 48 accepted slots, boundary-day requirement, 120-minute start lag, 60-minute run-duration bound, 180-minute completion bound, and 60-minute publication bound are unchanged.
