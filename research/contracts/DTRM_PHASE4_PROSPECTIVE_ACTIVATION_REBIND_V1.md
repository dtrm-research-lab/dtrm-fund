# DTRM Phase IV — Prospective activation rebind v1

Date: 2026-09-16. Status: **REBIND_PREPARED_NOT_PROVISIONED_NOT_ARMED**.

Scientific parent: `dtrm-research-lab/dtrm-fund@d919ce57852652ee2e61ddbdb9e4188480e23f55`,
tree `1d8e6aeaa2eff2ff58d89d932e6380fccb11497e`.

This increment supersedes the prepared-but-never-provisioned activation statement from PR #26
after the backend scheduler workflow was hardened in `theresistance-back` PR #93.

## What changed

The scientific runtime remains frozen at:

- backend commit: `bf844932f8bb3e6773c329a45135fd754c6d8342`
- backend tree: `c090c3cb41165ee513de812dec562f497407df62`

The scheduler executor is now bound to:

- backend scheduler merge commit: `e73d5af5196ca765bd741722bba7fd85c6ae6b7c`
- backend scheduler merge tree: `60165123fe82e05d120e4350780b65102828ec99`
- validated PR head: `83f015bc642ac63483f6dee1d41668cff385dbe2`
- workflow blob: `a79ec00ec5761f5fb8cc8a6c017be8bbe7eb75c3`

The hardened workflow checks out the frozen Phase-IV runtime for capture while deriving the
workflow blob from the actual scheduled-event revision. Unrelated backend development can
therefore continue without changing the scientific runtime; a change to the workflow itself
still fails closed against the activation statement.

## Superseded statement

The statement `phase4-prospective-capture-2026-09-18-v1`
(SHA-256 `540a46f4b80e73cb776596936fd2d30fdf7d74d8a64d2c6ed2bd565deb8ed2b1`)
was never provisioned and was never armed. It remains in the repository as immutable audit
evidence and must not be provisioned.

## Rebound statement

Path:
`research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2_REBOUND.json`

- statement ID: `phase4-prospective-capture-2026-09-18-v2`
- SHA-256: `5625b8930f5c6aefd9aa6193c5211c74ec61d96a4d88ea72307c42bbe654dbd5`
- schema: `dtrm.phase4.prospective_activation_statement.v2`
- prospective start: `2026-09-18T00:00:00Z`
- first slot: `2026-09-18T00:15:00Z`
- last slot: `2026-10-01T18:15:00Z`
- 56 opportunities, minimum 48 accepted

Relative to the superseded statement, only `activation_statement` and `workflow_blob_sha`
change. Backend runtime, request fingerprint, provider roles, evidence authorities, schema,
campaign window, and downstream scientific prohibitions remain frozen.

## Operational boundary

This rebind does **not** provision GitHub variables, does not set
`PHASE4_PROSPECTIVE_CAPTURE_ARMED=true`, does not call FMP, and does not start the campaign.

A separate final activation gate is still required after this rebind has passed regression,
exact-head CI, Codex review, and integration.
