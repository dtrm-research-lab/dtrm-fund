# DTRM Phase IV — Human Rights Review v0

- Status: preregistered before evidence review or rights promotion
- Date: 2026-09-12
- Scientific parent integration: `62c2a2735d663413390aa966a2be3cd934c77ce6`
- Scientific parent tree: `7c51ad4b601be2699ad0a63f1ff3f93f787c2c77`
- Depends on: `DTRM_PHASE4_ENTITLEMENT_EVIDENCE_INTAKE_V0.md`
- Scientific status at registration: `BLOCKED_PROSPECTIVE_DEPLOYMENT`

## Scientific purpose

Phase IV cannot use a prospective provider path until the rights to access, store and retain the source material are positively supported by account-specific/provider-written evidence. The integrated entitlement-intake protocol deliberately stopped at `NO_EVIDENCE` because no such evidence had been supplied.

This increment preregisters the human review protocol that will evaluate only a sanitized structured summary of underlying evidence reviewed outside the repository. It does not inspect an FMP account, accept credentials, fetch private contractual material, call FMP, access MongoDB, activate a runtime, construct history, access outcomes, fit Temporal State, train a model or execute MM1.

No account-specific evidence is available at registration. Therefore the tracked v0 result is fixed to `PENDING_HUMAN_EVIDENCE` and both rights gates remain blocked.

## Fixed graph cut

`sanitized entitlement statement -> human-review attestation record -> deterministic policy validator -> aggregate rights classification`

The deterministic validator checks internal consistency only. It cannot establish authenticity or legal meaning by itself. Authenticity and direct support must come from a human reviewer who inspected the underlying redacted/provider-written evidence outside the repository.

## Permitted evidence boundary

The repository may receive only a sanitized structured summary. It must not contain:

- API keys, bearer/auth headers, cookies, session IDs or passwords;
- account/customer/order/invoice identifiers;
- account email or billing/payment information;
- raw private contract/order-form text;
- screenshots or copied private portal content;
- provider payloads or returned news/article content;
- Mongo URIs or database credentials;
- personal data not required by this protocol.

An optional lowercase SHA-256 digest of a locally retained redacted evidence artifact may be referenced only as a non-authorizing integrity pointer. The source artifact itself remains outside the repository unless a later contract explicitly permits its storage.

## Review questions fixed before implementation

The human-review attestation must classify each item as `SUPPORTED`, `NOT_SUPPORTED` or `UNKNOWN`:

1. `programmatic_endpoint_access`
2. `exact_payload_storage`
3. `retain_through_phase4_evaluation`
4. `internal_research_use`
5. `termination_or_entitlement_loss_obligation_known`
6. `publication_display_redistribution_restrictions_known`
7. `storage_security_obligations_known`
8. `retention_duration_compatible_with_phase4`

`UNKNOWN` must never be inferred as permission.

## Evidence source classes

A human reviewer may attest that one or more of these evidence classes were inspected outside the repository:

- `ACCOUNT_PLAN_SUMMARY`
- `ORDER_FORM_OR_SUBSCRIPTION_TERMS`
- `PROVIDER_WRITTEN_CLARIFICATION`
- `PROVIDER_LICENSING_STATEMENT`

At least one provider/account-specific evidence class is required before any positive rights conclusion can be considered.

## Review states

The review policy recognizes three states:

1. `PENDING_HUMAN_EVIDENCE`
   - no human-reviewed sanitized evidence statement exists;
   - both rights gates remain `BLOCKED`.

2. `HUMAN_REVIEW_COMPLETED_BLOCKED`
   - evidence was reviewed but one or more mandatory rights questions are `NOT_SUPPORTED` or `UNKNOWN`, or evidence sources contradict one another;
   - both rights gates remain `BLOCKED` unless a later preregistered amendment narrows the blocked right without weakening the evidence rule.

3. `HUMAN_REVIEW_COMPLETED_SUPPORTED`
   - may be represented only by a later human-controlled evidence commit after underlying evidence has actually been reviewed;
   - requires direct positive support for programmatic endpoint access, exact payload storage, retention through Phase-IV evaluation, internal research use and retention-duration compatibility;
   - requires known termination/deletion, redistribution/display and storage-security obligations;
   - requires contradiction-free evidence and explicit reviewer attestation.

The tracked canonical v0 artifact must remain `PENDING_HUMAN_EVIDENCE` because no evidence has been supplied at registration.

## Rights classification rule

For the tracked v0 artifact, the only valid rights classification is:

- `account_entitlement_status=BLOCKED`
- `storage_retention_rights_status=BLOCKED`

A future human-reviewed artifact may classify a right as `SUPPORTED_BY_REVIEW` only when every prerequisite for that right is explicitly supported and the reviewer attestation is complete. Even `SUPPORTED_BY_REVIEW` does **not** authorize production provider access, live semantics probing, storage mutation or activation. Those remain separate preregistered gates with separate explicit human authorization.

## Mandatory reviewer attestation

A completed human review must record only non-identifying metadata:

- `human_review_completed=true`
- `review_date` as a calendar date
- `evidence_classes_reviewed`
- optional redacted-evidence SHA-256 digest
- `direct_support_confirmed=true`
- `contradiction_free=true`
- `raw_private_material_stored_in_repo=false`
- `secrets_or_identifiers_stored_in_repo=false`

No reviewer name, email, account identifier or provider-account identifier is required or permitted in the tracked schema.

## Tracked canonical v0 state

Because no human evidence has been provided, implementation and CI must reproduce exactly:

- `engineering_status=PASS_HUMAN_RIGHTS_REVIEW_PROTOCOL`
- `review_state=PENDING_HUMAN_EVIDENCE`
- `account_entitlement_status=BLOCKED`
- `storage_retention_rights_status=BLOCKED`
- `provider_semantics_probe_eligible=false`
- `activation_readiness_status=BLOCKED`
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`

All operational/scientific permissions remain false:

- production provider access;
- production storage mutation;
- runtime adapter execution;
- workflow activation;
- provider-semantics live probe;
- history construction;
- Temporal State representation fitting;
- training;
- outcome access;
- model fitting;
- MM1 execution.

## Pure validator contract

Implementation may add a stdlib-only deterministic validator that:

1. validates exact schema and rejects extra keys;
2. validates three-state review answers without interpreting private evidence;
3. rejects secrets, identifiers and raw-private-material-shaped fields without echoing them;
4. enforces that `PENDING_HUMAN_EVIDENCE` contains no completed-review attestation;
5. enforces that a completed review cannot be marked supported unless all mandatory prerequisites are explicitly supported;
6. enforces that contradiction, unknown mandatory rights or incomplete attestation keeps rights blocked;
7. never reads environment variables, provider accounts, browser state, network resources, MongoDB or credentials;
8. emits aggregate policy classification only;
9. never grants operational permissions in this increment.

## Validation gates

Before review/merge, the increment must pass:

- scoped Ruff;
- strict mypy;
- full deterministic/inherited regression suite;
- exact canonical pending-review artifact reproduction;
- negative tests for secret/account-identifier/raw-private-material leakage;
- negative tests proving unsupported/unknown/contradictory evidence cannot promote rights;
- source preservation for all 157 inherited Phase-III files and original Stage-0 contract;
- disposable package build;
- current-head `Tests` and `Phase IV gates` workflows.

The Phase-IV workflow may be extended only with an offline canonical human-rights-review reproduction. No secret, provider request or production storage access may be added.

## Promotion sequence after this increment

1. Human review and merge of this protocol.
2. Human supplies a sanitized evidence summary derived from actual provider/account evidence reviewed outside the repository.
3. A separate evidence commit records only the structured attestation and aggregate conclusions.
4. If the review is fully positive and contradiction-free, rights may become `SUPPORTED_BY_REVIEW` in that evidence artifact.
5. Even then, a bounded provider-semantics probe must be separately preregistered and separately authorized before any FMP request.
6. Storage provisioning, least-privilege credentials, runtime adapter and activation remain separate gates.
7. Multiple accepted prospective runs are required before history construction.
8. Temporal State fitting and frozen-MM1 comparison remain later preregistered experiments.

Approval of this contract authorizes only the offline protocol implementation and deterministic validation described above.