# DTRM Phase IV — Operational authority evidence v1

Date: 2026-09-15. Status: **AUTHORIZED_AUTHORITY_EVIDENCE_START_UNBOUND**.

Scientific parent: `dtrm-research-lab/dtrm-fund@28b4e787c7b208d810245deda1b37d7881ab50e9`, tree `c90cd63641efc2606f6ede0a6d2fb6274b120830`.

This bounded increment records source-value-free operational evidence obtained from one explicitly human-authorized, non-counting diagnostic execution. It does not choose a prospective start, arm the schedule, provision activation variables, authorize periodic capture, open protected outcomes, execute MM1 or change Phase III.

## Exact runtime evidence

The diagnostic execution is GitHub Actions run `35001927608` against the exact registered backend schedule-bearing revision:

- backend commit: `bf844932f8bb3e6773c329a45135fd754c6d8342`;
- backend tree: `c090c3cb41165ee513de812dec562f497407df62`;
- workflow path: `.github/workflows/phase4_fmp_news_temporal_capture_v1.yml`;
- workflow blob: `0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22`;
- workflow identity: `phase4_fmp_news_temporal_capture_v1`;
- diagnostic job: success;
- scheduled-capture job: skipped;
- private artifact ID: `10409798325`;
- private artifact digest: `f42fc8bc1d23bf1a42b312b577dead856605fedc2dfc7c43b69edecca1f6c16e`;
- private artifact size: `117868` bytes.

The provider probe and deterministic temporal-index derivation both succeeded. The emitted temporal index retained `periodic_capture_activation_permitted=false`. No scheduled campaign slot was created or counted by this diagnostic execution.

## Credential-scope authorization

`credential_scope_status=AUTHORIZED` means only that the exact registered workflow and successful diagnostic establish the technical secret-exposure boundary required by the scheduled implementation:

- checkout, Python setup and package installation do not receive the provider credential;
- scheduled activation preflight does not receive the provider credential;
- only the diagnostic provider-capture step and the post-verification scheduled provider-capture step receive `FMP_API_KEY`;
- the secret value was not inspected or persisted in repository evidence and GitHub masked it in the diagnostic log;
- the successful diagnostic exercised the registered provider roles under this boundary.

This status is **not** a claim about FMP subscription rights, retention rights, endpoint entitlement breadth or commercial permission. Those remain represented separately by `provider_rights_status=DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT` under the already integrated Evidence-First amendment.

The canonical SHA-256 of the `credential_scope_evidence` object in the evidence file is:

`e1203bb38fd1c03448d5d622bceb791f3a1bc5ad325fa89e566889c6b37cbdf3`.

## Writer-authority authorization

`writer_authority_status=AUTHORIZED` is bounded to the exact Phase-IV counting evidence writer: the registered GitHub Actions workflow writing a private artifact after the fail-closed scheduled path.

The evidence establishes that:

- the workflow's GitHub token has `contents: read` only;
- the diagnostic private-artifact write succeeded;
- the diagnostic event is non-counting and its scheduled-capture job was skipped;
- the counting writer is gated by a schedule event, exact lowercase arm value and successful exact activation preflight;
- this evidence path performs no Mongo write and no mutation of the legacy news namespace;
- public raw provider-data redistribution remains forbidden.

The canonical SHA-256 of the `writer_authority_evidence` object in the evidence file is:

`f4b9d64046b6529a94313734d77f8766320c8a00b5047d0968ab0d2bdfa21390`.

## Provisioned evidence schema identity

The scheduled writer serializes its accepted counting record under the exact backend slot-domain schema:

`dtrm.phase4.prospective_temporal_slot.v1`

bound to slot-domain blob `5f04843e0f611dccee7121746780e7f74a21b9f2` at the registered backend revision.

For this artifact-first campaign boundary, this exact fail-closed record schema is the `provisioned_schema_identity` consumed by the later activation statement. This does not claim that the older optional Mongo namespaces are provisioned or used. Durable Mongo activation remains outside this increment.

## Remaining activation gate

After this increment, the following remain deliberately unbound:

- `prospective_start_utc = null`;
- `human_activation_authorized = false`;
- `periodic_capture_activation_permitted = false`.

No repository merge may infer those values. A later exact `dtrm.phase4.prospective_activation_statement.v2` must bind the already registered schedule-bearing backend revision, this exact schema identity and the sanitized credential/writer evidence digests, then select a valid future UTC start before slot zero. Periodic activation still requires a separate explicit human authorization.

## Scientific boundary

All remain false:

- confirmatory-history construction;
- Temporal State outcome fitting;
- protected outcome access;
- MM1 execution;
- Phase III policy mutation;
- public raw FMP redistribution.

The diagnostic artifact is evidence acquisition, not model evaluation.

## Machine-readable evidence

- `research/evidence/phase4_operational_authority_evidence_v1.json`
- `research/contracts/DTRM_PHASE4_OPERATIONAL_AUTHORITY_STATEMENT_V1.json`

The canonical pretty-JSON SHA-256 of the statement file is:

`1ed3703f2fbcc730b9c6ad1e100fb6522e62e9a872f121b0f5d6a678cec294b9`.
