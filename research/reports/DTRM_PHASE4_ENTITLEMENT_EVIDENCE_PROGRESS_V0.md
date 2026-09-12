# DTRM Phase IV — Entitlement Evidence Intake v0 — Validation Progress

## Scientific boundary

This increment follows the integrated provider-evidence audit at merge commit `4e64bf27fed918fe0b022c21769e96d500a99d6e`. It defines only a sanitized, offline evidence-intake boundary for the still-unresolved `ACCOUNT_ENTITLEMENT` and `STORAGE_RETENTION_RIGHTS` gates.

No Financial Modeling Prep request, API-key inspection, account login, production MongoDB access, provisioning, runtime adapter execution, workflow activation, prospective history construction, outcome access, Temporal State fitting, training, model fitting or MM1 execution occurred.

Scientific status remains `BLOCKED_PROSPECTIVE_DEPLOYMENT`.

## Chronology

1. Preregistration commit: `0f49321811c3a992d7486dd122e25ae4a9a2a5fd`.
   - Created `DTRM_PHASE4_ENTITLEMENT_EVIDENCE_INTAKE_V0.md` before implementation.
   - Fixed the tracked result to `NO_EVIDENCE` with both rights gates blocked.
   - Reserved `HUMAN_VERIFIED_EVIDENCE_PRESENT` for a future separately registered human-review artifact.

2. Implementation commit: `bf3b6f1be1fc2d6381ac65aa44e94fa5a19b4804`.
   - Added canonical no-evidence statement, pure stdlib validator, offline/no-overwrite CLI, aggregate report and deterministic tests.
   - A sanitized statement with affirmative answers can be classified only as `EVIDENCE_PRESENT_UNVERIFIED`; it cannot authorize rights or a live provider-semantics probe.

3. Initial implementation validation:
   - `Tests` run `34685049849`: PASS.
   - `Phase IV gates` run `34685049858`: stopped at strict mypy after preservation and Ruff passed.
   - Exact defect: one redundant `cast(bool, value)` in `_require_bool`; synthetic Mongo passed independently.
   - No scientific contract, statement, report, permission or entitlement conclusion was changed in response.

4. Mechanical correction commit: `af35d1e791b25c8f65236058d9eee00454c282ad`.
   - Replaced the redundant cast with `return value` after an existing exact `type(value) is bool` guard.
   - No scientific or operational behavior changed.

5. Corrected-head validation:
   - `Tests` run `34685121345`: PASS — 890 passed, 20 skipped.
   - `Phase IV gates` run `34685121300`: PASS.
   - inherited source preservation: PASS for 157 inherited files and original Stage-0 contract;
   - Ruff: PASS;
   - strict mypy: PASS across 29 Phase-IV source/experiment files;
   - deterministic/inherited regressions: PASS;
   - all previously registered Phase-IV evidence reproductions: PASS;
   - disposable wheel build: PASS;
   - final source preservation: PASS;
   - synthetic Mongo functional job: PASS.

## Intake security boundary

The v0 validator rejects or structurally excludes:

- API keys, bearer/auth headers, cookies and sessions;
- Mongo URIs and database credentials;
- account/customer/invoice/order identifiers;
- billing addresses and email-shaped values;
- private-key material;
- raw contract text, screenshot content, account-email fields and provider payload fields.

An optional local redacted-evidence digest is accepted only as a lowercase SHA-256 and carries no authorization semantics.

The implementation performs no environment discovery, provider access, network I/O or Mongo access.

## Fixed canonical result

The tracked statement contains no account-specific evidence. Its only valid aggregate result is:

- `engineering_status=PASS_ENTITLEMENT_EVIDENCE_INTAKE`;
- `evidence_state=NO_EVIDENCE`;
- `account_entitlement_status=BLOCKED`;
- `storage_retention_rights_status=BLOCKED`;
- `human_rights_review_required=true`;
- `provider_semantics_probe_permitted=false`;
- `activation_readiness_status=BLOCKED`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`.

All provider/storage/runtime/activation/history/Temporal-State/training/outcome/model/MM1 permissions remain false.

## Next dependency

After human review and integration of this protocol, actual entitlement evidence must be summarized without secrets or raw private documents. A separate preregistered human-rights review must then determine whether each claimed right is directly supported. Only if programmatic access, exact payload storage and research retention are positively supported may the corresponding rights gates be closed and a separately preregistered bounded provider-semantics probe be proposed.
