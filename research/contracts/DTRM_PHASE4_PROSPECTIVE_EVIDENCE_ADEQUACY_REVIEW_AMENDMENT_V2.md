# DTRM Phase IV — Prospective Evidence Adequacy Review Amendment v2

**Date:** 2026-09-14  
**Status:** preregistered before periodic activation and before any registered 14-day campaign slot  
**Parent adequacy preregistration:** `835f5c6f01825abdaf9a3cc266f9ba1dfb24c55d`  
**Review amendment v1:** `44d82ac66d283196d1077b799a012a693f9ead7e`  
**Scientific parent integration:** `ca7ef0570281f6a1143d7a93efae5d69edc2b8a4`  
**Prospective evidence registration:** `243797ee398b43f6684ce7a43057711167ed79ba`

## Purpose

This second pre-activation amendment closes provenance and finalization ambiguities found by exact-head review. It is fixed before periodic activation, before any registered campaign slot, and without provider values, market outcomes, portfolio results, predictions, MM1 decisions, or protected outcomes.

The scientific campaign remains unchanged: 14 consecutive UTC days, 56 registered target slots, minimum 48 accepted slots, boundary-day evidence, no replacement/backfill, and no early stopping.

## 1. Verify exact activation-statement bytes against a trusted reference

The adequacy auditor may not construct its activation binding from independently supplied start date / commit / tree fields.

Instead, the audit boundary must receive:

1. the **exact UTF-8 bytes** of the later human-approved activation statement; and
2. a separately trusted activation reference containing the expected statement identifier and expected SHA-256 digest.

The auditor must:

- recompute SHA-256 over the exact activation-statement bytes;
- require equality with the trusted expected digest;
- parse the bytes as strict JSON with no non-finite values;
- require the exact activation statement identifier to match the trusted identifier;
- derive `start_utc_day`, backend commit, backend tree and request fingerprint only from those verified bytes;
- require the request fingerprint to equal the preregistered fingerprint;
- fail closed on malformed bytes, schema drift, extra/missing keys, invalid dates or lineage, identifier mismatch, or digest mismatch.

The registered activation-statement payload for v1 is exactly these keys:

- `schema_version = dtrm.phase4.prospective_activation_statement.v1`;
- `activation_statement`;
- `start_utc_day` (`YYYY-MM-DD`);
- `backend_commit` (40 lowercase hex);
- `backend_tree` (40 lowercase hex);
- `request_fingerprint_sha256`;
- `periodic_capture_activation_permitted = true`.

The trusted identifier/digest must originate from the later human-approved control-plane record. They must not be recomputed from the supplied bytes at the same call site and then treated as trust evidence.

No live activation statement is created or authorized by this amendment.

## 2. Workflow reruns are never counting evidence

Each ledger attempt must carry positive integer `run_attempt`.

For the registered periodic workflow:

- only `event_name = schedule` with `run_attempt = 1` is counting-eligible;
- any `schedule` record with `run_attempt > 1` is a diagnostic rerun and never counts, never backfills a missing/failed slot, and never creates a duplicate accepted opportunity;
- diagnostic reruns are counted separately in the audit report as ignored reruns;
- the original first attempt remains the only candidate for that registered opportunity.

This mirrors the backend schedule-readiness rule and preserves the preregistered no-backfill constraint.

## 3. Freeze a record-publication deadline before final PASS/FAIL

Completion and ledger publication are distinct clocks.

The v1 start/completion rules remain:

- latest eligible start: target + 120 minutes;
- maximum run duration: 60 minutes;
- latest eligible completion: target + 180 minutes.

Each ledger attempt must additionally carry `recorded_at_utc`, the source-value-free append/publication clock for the immutable slot record. A counting-eligible record must satisfy:

- `recorded_at_utc >= completed_at_utc`;
- maximum record-publication lag after completion: **60 minutes**;
- therefore latest eligible record publication: target + **240 minutes**.

A scheduled first attempt whose record is published after its slot-specific publication deadline is non-accepted and classified `LATE`.

The final evidence decision remains `PENDING_INTERVAL` until:

`slot_55_target_at_utc + 240 minutes`.

After this publication deadline, no newly published slot record can become accepted under this contract. A later invocation may observe a late record, but that record cannot change accepted-slot count or convert final FAIL to PASS.

The extra 60 minutes is an operational publication grace only. It does not change the 56-slot geometry, the 48-slot threshold, the 120-minute scheduler-start tolerance, or the scientific treatment.

## 4. Explicit final-report lineage

Every canonical audit report must serialize:

- activation statement identifier and verified digest;
- review amendment v1 commit;
- this review amendment v2 commit;
- maximum schedule lag;
- maximum run duration;
- maximum completion lag;
- maximum record-publication lag;
- finalization/publication-deadline clock;
- ignored non-scheduled attempts;
- ignored scheduled reruns;
- all frozen downstream prohibitions.

## 5. Required regression gates

Before integration, tests must prove at minimum:

- activation bytes with a wrong trusted digest fail closed;
- activation bytes with a wrong trusted identifier fail closed;
- activation payload schema drift / extra keys fail closed;
- binding fields are derived from verified bytes rather than parallel caller fields;
- `schedule` attempt 1 can count;
- `schedule` attempt 2+ never counts or backfills;
- an attempt completing at target +180 and recorded at target +240 remains eligible;
- the audit remains PENDING immediately before target +240;
- a record timestamp after target +240 is LATE and cannot increase accepted count;
- exactly 48 accepted slots with first/last-day evidence still PASS after the publication deadline;
- a later-added record whose `recorded_at_utc` is beyond its deadline cannot flip a final FAIL to PASS.

## 6. Scientific non-adaptation statement

These rules are contract-integrity clarifications fixed before campaign activation. They are not selected from observed provider availability, campaign success/failure, market outcomes, model performance, or MM1 behavior. No outcome gate is opened by this amendment.
