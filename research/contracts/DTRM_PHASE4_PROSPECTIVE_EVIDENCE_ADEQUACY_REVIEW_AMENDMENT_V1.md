# DTRM Phase IV — Prospective Evidence Adequacy Review Amendment v1

**Date:** 2026-09-14  
**Status:** preregistered before periodic activation and before any registered 14-day campaign slot  
**Parent adequacy preregistration:** `835f5c6f01825abdaf9a3cc266f9ba1dfb24c55d`  
**Scientific parent integration:** `ca7ef0570281f6a1143d7a93efae5d69edc2b8a4`  
**Prospective evidence registration:** `243797ee398b43f6684ce7a43057711167ed79ba`

## Purpose

This amendment resolves review-discovered ambiguities in the prospective evidence adequacy gate **before live periodic activation**. It does not use provider observations, market outcomes, portfolio results, predictions, MM1 decisions, or any protected outcome surface.

The scientific campaign remains unchanged:

- 14 consecutive UTC days;
- target clocks `00:15`, `06:15`, `12:15`, `18:15` UTC;
- exactly 56 registered target slots;
- minimum 48 accepted slots;
- no replacement/backfill;
- no early stopping.

## 1. Preserve inherited boundary-day evidence

A final PASS requires all of the following:

1. at least 48 accepted slots overall;
2. at least one accepted slot on UTC day 1 of the registered interval;
3. at least one accepted slot on UTC day 14 of the registered interval.

This is not a new scientific relaxation or optimization. It makes the adequacy auditor preserve the boundary-day requirement already present in the inherited prospective temporal-evidence contract.

## 2. Bind the audit to the exact human-approved activation statement

The immutable audit binding must include and serialize:

- `activation_statement` — the exact later activation statement identifier;
- `activation_statement_sha256` — SHA-256 of that exact activation statement;
- `start_utc_day`;
- exact backend repository commit;
- exact backend repository tree.

An audit that cannot validate these fields fails closed. Two activation statements using the same backend revision remain distinguishable by statement identity/digest.

No activation statement exists merely because this amendment exists. Periodic activation remains prohibited until a later exact-head statement is created and explicitly authorized by the human operator.

## 3. Separate eligible start lag from completion deadline

The registered scheduler-start tolerance remains:

- earliest accepted start: target time;
- latest accepted start: target time + 120 minutes.

A successful slot record must additionally carry `completed_at_utc` and satisfy:

- `completed_at_utc >= started_at_utc`;
- maximum run duration: **60 minutes**;
- therefore no accepted completion may occur later than target time + **180 minutes**.

The final interval decision may not be emitted before:

`slot_55_target_at_utc + 180 minutes`.

At or after that clock, no subsequently arriving run can become newly accepted under this contract, because every accepted run must already have completed by its slot-specific completion deadline. This prevents a supposedly final `FAIL` from later flipping to `PASS`.

Runs completing after the registered completion deadline are non-accepted and classified `LATE`.

## 4. Explicit downstream prohibitions

Every canonical adequacy report, including PASS reports, must explicitly serialize these frozen prohibitions as `false`:

- `confirmatory_history_construction_permitted`;
- `temporal_state_outcome_fitting_permitted`;
- `outcome_access_permitted`;
- `mm1_execution_permitted`;
- `phase3_policy_mutation_permitted`;
- `public_raw_provider_data_redistribution_permitted`.

A PASS authorizes only the next **outcome-blind Temporal State representation preregistration**. It does not authorize confirmatory history construction, outcome fitting, outcome access, MM1 execution/evaluation, Phase III mutation, or public redistribution of raw provider material.

## 5. Scientific non-adaptation statement

These clarifications are fixed in response to contract-integrity review before campaign activation. They are not based on observed campaign success/failure, provider-value content, market outcomes, or model performance. The 56-slot geometry and 48-slot minimum are unchanged.
