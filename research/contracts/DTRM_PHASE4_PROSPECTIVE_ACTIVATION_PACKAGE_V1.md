# DTRM Phase IV — Prepared prospective activation package v1

Date: 2026-09-16. Status: **PREPARED_NOT_PROVISIONED_NOT_ARMED**.

Scientific parent: `dtrm-research-lab/dtrm-fund@dcd60c90d866cb43683934f9a174c057aea70717`, tree `a95ac8b96bfac8736ae7ea70ae5407c5fe8dedf6`.

This increment freezes the earliest safely supportable prospective campaign window after the operational-authority evidence merge. It prepares the exact backend-compatible activation statement v2, but **does not provision it, does not arm the workflow, does not start the campaign, and does not constitute human activation authorization**.

## Frozen campaign window

- `prospective_start_utc`: `2026-09-18T00:00:00Z`
- first counting target: `2026-09-18T00:15:00Z`
- last counting target: `2026-10-01T18:15:00Z`
- earliest finalization: `2026-10-01T22:15:00Z`
- 14 consecutive UTC days
- 56 scheduled opportunities
- minimum accepted: 48
- at least one accepted slot on the first UTC day and one on the last UTC day
- no backfill
- no early stopping
- only attempt 1 is counting-eligible

The start is strictly before slot zero, as required by the exact backend `SlotActivationBinding`.

## Exact activation statement

Path: `research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2.json`

- statement ID: `phase4-prospective-capture-2026-09-18-v1`
- SHA-256: `540a46f4b80e73cb776596936fd2d30fdf7d74d8a64d2c6ed2bd565deb8ed2b1`
- backend commit: `bf844932f8bb3e6773c329a45135fd754c6d8342`
- backend tree: `c090c3cb41165ee513de812dec562f497407df62`
- workflow blob: `0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22`
- schema: `dtrm.phase4.prospective_temporal_slot.v1`
- credential scope: `AUTHORIZED` against frozen evidence digest
- writer authority: `AUTHORIZED` against frozen evidence digest

The embedded field `periodic_capture_activation_permitted=true` is required by the backend activation-statement schema. It is **not operational permission by itself**. The campaign remains inert until all of the following occur after separate explicit human authorization:

1. exact statement bytes are provisioned through `PHASE4_ACTIVATION_STATEMENT_B64`;
2. exact statement ID is provisioned through `PHASE4_ACTIVATION_STATEMENT_ID`;
3. exact statement SHA-256 is provisioned through `PHASE4_ACTIVATION_STATEMENT_SHA256`;
4. `PHASE4_PROSPECTIVE_CAPTURE_ARMED` is set to exact lowercase `true`.

Until then, scheduled runs remain non-operational.

## Scientific boundary

This increment does not permit confirmatory history construction, Temporal State outcome fitting, outcome access, MM1 execution, Phase III mutation, or public redistribution of raw provider data. Provider-rights status remains deferred under the evidence-first amendment.

If the package cannot be integrated and provisioned before the frozen day-0 slot-zero boundary, it must be superseded by a new prospectively registered start; the start must not be silently moved.
