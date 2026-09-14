# DTRM Phase IV — Prospective Evidence Adequacy Review Amendment v4

Date: 2026-09-14. Status: PREREGISTERED_BEFORE_PERIODIC_ACTIVATION.

This amendment resolves two preactivation integrity findings without changing the frozen scientific campaign. No prospective campaign evidence, outcomes, predictions, portfolio results or MM1 results were used.

## Activation instant and fixed geometry

The inherited design remains 14 consecutive UTC calendar days with targets at 00:15, 06:15, 12:15 and 18:15 UTC, exactly 56 opportunities, at least 48 accepted, first/last-day evidence, no replacement/backfill and no early pass.

`start_utc_day` remains the UTC date of `prospective_start_utc`, and slot 0 remains `start_utc_day 00:15:00Z`. Because the inherited contract also requires the first registered opportunity to be strictly after activation, a compatible activation must satisfy `start_utc_day 00:00:00Z <= prospective_start_utc < start_utc_day 00:15:00Z`.

An incompatible activation instant is rejected fail-closed. The campaign is never shifted, shortened, extended or backfilled to accommodate it.

## Per-attempt workflow provenance

Every observed scheduled attempt, including reruns, must retain `workflow_path`, `workflow_blob_sha` and `workflow_identity`. These fields must be syntactically valid and exactly match the verified human-approved activation statement.

A first-attempt mismatch is `CONTRACT_MISMATCH` and cannot count. Reruns remain diagnostic/non-counting, but malformed or contradictory target/workflow provenance fails closed.

## Frozen remainder

The 120-minute start-lag bound, 60-minute run-duration bound, 180-minute completion bound, 60-minute publication bound, all downstream prohibitions and provider-rights status remain unchanged. Periodic capture remains inactive; this amendment authorizes neither activation nor merge.
