# DTRM Phase IV — Entitlement Evidence Intake v0

- Status: registered before implementation, account inspection or provider access
- Date: 2026-09-12
- Scientific parent integration: `4e64bf27fed918fe0b022c21769e96d500a99d6e`
- Scientific parent tree: `c4ca946530e05f9e5d6d3cbfcee741c0ff18f8fe`
- Depends on: `DTRM_PHASE4_PROVIDER_EVIDENCE_AUDIT_V0.md`
- Amends: none; this is a new evidence-governance gate after the integrated public provider-evidence audit

## Scientific purpose

Phase IV asks whether an event-history representation improves the frozen robust MM1 policy beyond point-in-time probabilistic state. The prospective path remains scientifically blocked until source rights, provider semantics, storage/provisioning, runtime authority and activation are separately authenticated.

The immediately unresolved rights gates are:

- `ACCOUNT_ENTITLEMENT`;
- `STORAGE_RETENTION_RIGHTS`.

This increment defines how non-secret account/provider evidence may later be presented and classified without leaking credentials, billing identifiers, private contractual text or provider data into the repository. It does not determine that the current account has sufficient rights because no account-specific evidence has yet been supplied or reviewed.

This increment is outcome-blind and must not inspect returns, labels, portfolio results, model scores, Temporal State representations or MM1 outputs.

## Fixed graph cut

The v0 graph is governance-only:

`sanitized evidence statement -> exact intake validator -> aggregate intake classification -> human rights review checkpoint`

It contains no provider request, API key, account login, browser session, billing portal access, Mongo connection, runtime adapter, workflow activation or prospective collection.

## Evidence states fixed before implementation

The intake classifier may emit only one of these evidence states:

1. `NO_EVIDENCE`
   - no account/provider evidence statement has been supplied;
   - both rights gates remain blocked.

2. `EVIDENCE_PRESENT_UNVERIFIED`
   - a structurally valid sanitized evidence statement exists;
   - its truth/authenticity has not been independently reviewed;
   - both rights gates remain blocked.

3. `HUMAN_VERIFIED_EVIDENCE_PRESENT`
   - permitted only in a future separately registered review artifact after a human reviewer has examined the underlying redacted/provider-written evidence outside the repository;
   - this intake v0 implementation must **not** generate this state from ordinary input or tests.

Therefore successful v0 engineering validation must remain `NO_EVIDENCE` until actual evidence is supplied in a later human-controlled step.

## Acceptable future evidence classes

A later human may review one or more of the following outside the repository:

- redacted account/plan entitlement summary visible in the provider account;
- redacted Order Form or subscription terms identifying allowed datasets/use;
- written provider support/sales/legal clarification;
- provider-issued licensing statement covering storage/retention/research use.

The repository may store only a sanitized structured attestation of what was verified, not the source document itself unless a later contract explicitly authorizes that storage.

## Minimum questions the future evidence must answer

A future human-reviewed attestation must answer, without secrets or identifiers:

1. Is programmatic access to the registered FMP news endpoints permitted under the applicable account/agreement?
2. May exact provider response payload/content be stored for research reproducibility?
3. May stored material be retained through Phase-IV evaluation?
4. Is any minimum/maximum retention period imposed?
5. What deletion/cessation obligation applies on termination or entitlement loss?
6. Is internal research/derived analysis permitted?
7. Are publication, display or redistribution of provider content restricted?
8. Are additional storage-security controls required?

Unknown or ambiguous answers must remain `UNKNOWN`; they must not be inferred as permission.

## Sanitized statement schema

Implementation may define one canonical JSON intake statement containing only:

- schema version and graph identity;
- evidence state (`NO_EVIDENCE` for the tracked canonical artifact);
- evidence classes present as booleans;
- non-identifying evidence date if known;
- non-identifying provider scope label fixed to `FINANCIAL_MODELING_PREP`;
- answers to the minimum questions as `YES`, `NO` or `UNKNOWN`;
- optional SHA-256 of a local redacted evidence file **only if** a later human-controlled step supplies one; the tracked canonical v0 artifact must leave it null;
- reviewer attestation fields, all null/false in the tracked canonical v0 artifact;
- fixed operational/scientific permission flags.

The statement must not contain account email, account ID, customer ID, invoice/order number, billing address, payment data, API key, bearer token, cookie, session ID, authentication header, Mongo URI, database credential, raw contract/order-form text, screenshot content, provider payload, returned article/news content or personal data.

## Human review rule

A structurally valid statement is not sufficient evidence of rights.

The implementation must not convert `EVIDENCE_PRESENT_UNVERIFIED` into authorization. A later promotion requires:

- an explicit human review event;
- a separately registered review artifact or contract;
- a reviewer attestation that the underlying evidence directly supports each promoted right;
- no unresolved contradiction between evidence sources;
- no use of secrets or raw provider/account material in repository evidence.

Any field that is `UNKNOWN`, contradictory or unsupported keeps the corresponding gate blocked.

## Pure validator contract

Implementation may add a deterministic stdlib-only validator that:

1. rejects extra keys and type mismatches;
2. accepts only the fixed tracked canonical `NO_EVIDENCE` statement in v0 CI;
3. validates future sanitized statements structurally without treating them as authorization;
4. rejects secret-, credential- and identifier-shaped material without echoing it;
5. rejects raw contractual/provider text fields;
6. never reads environment variables, credential stores, browser state, provider accounts or network resources;
7. emits only aggregate classification evidence;
8. cannot promote provider access, storage mutation, activation, history construction, Temporal State fitting, outcome access, model fitting or MM1 execution.

## Fixed tracked v0 output

For the repository-tracked canonical no-evidence statement, the only permitted result is:

- `engineering_status=PASS_ENTITLEMENT_EVIDENCE_INTAKE`;
- `evidence_state=NO_EVIDENCE`;
- `account_entitlement_status=BLOCKED`;
- `storage_retention_rights_status=BLOCKED`;
- `human_rights_review_required=true`;
- `provider_semantics_probe_permitted=false`;
- `activation_readiness_status=BLOCKED`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`.

The following permissions remain false:

- production provider access;
- production storage mutation;
- runtime adapter execution;
- workflow activation;
- provider semantics live probe;
- history construction;
- Temporal State representation fitting;
- training;
- outcome access;
- model fitting;
- MM1 execution.

No test, fixture or user-supplied sanitized statement may promote those permissions in this increment.

## Validation gates

Before review, implementation must pass:

- scoped Ruff;
- strict mypy;
- full deterministic/inherited regression suite;
- exact canonical no-evidence statement/review reproduction;
- negative tests for credential/account-identifier/raw-text leakage;
- source preservation for all 157 inherited Phase-III files and original Stage-0 contract;
- disposable package build;
- current-head `Tests` and `Phase IV gates` workflows.

The Phase-IV workflow may be extended only with the explicit canonical entitlement-intake reproduction. It must not add secrets, account access, provider requests or production storage access.

## Promotion sequence after this increment

1. Human review and merge of this intake protocol.
2. Human supplies a sanitized summary of actual entitlement evidence outside secrets/raw documents.
3. A separately registered human-rights review artifact classifies each required answer and records only sanitized conclusions.
4. If and only if programmatic use + exact storage + research retention are positively supported, close `ACCOUNT_ENTITLEMENT` and `STORAGE_RETENTION_RIGHTS` in that later gate.
5. Then preregister a bounded live provider-semantics probe.
6. Execute that probe only after separate explicit human authorization.
7. Storage/provisioning/runtime/activation remain separate gates.
8. Multiple accepted prospective runs are required before any history-construction proposal.
9. Temporal State fitting and frozen-MM1 comparison remain later preregistered experiments.

Approval of this contract authorizes only the offline evidence-intake implementation and validation described above.