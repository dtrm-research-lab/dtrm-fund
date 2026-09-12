# Phase IV — Provider Evidence Audit v0 progress

## Scope

This increment follows the integrated prospective activation-readiness gate at merge commit `02bdc19e501697395526bac7a5a661637dd945f8`. It is documentary and outcome-blind. It does not call Financial Modeling Prep, inspect an API key or account, connect to MongoDB, provision infrastructure, activate a workflow, construct event history, access outcomes, fit a Temporal State representation or execute MM1.

Scientific status remains `BLOCKED_PROSPECTIVE_DEPLOYMENT`.

## Contract-first chronology

- Scientific parent: `02bdc19e501697395526bac7a5a661637dd945f8`, tree `23c460d70e508cfafce688f70053a9758f175a26`.
- Preregistration: `8fbe5301d2cd5a7af219dbf185d69b8d63c991f1`.
- Registered contract SHA-256: `708dcc4e43da77aaa6b5686d1343c1924a557b9e7a19e9734708abf265ad1b84`.
- Initial implementation: `f375f9d46c793f4fdab548de80a3ccb7aec75e21`.
- Mechanical strict-typing correction: `a06d09896c4a27680b69713bfd230b3bde8eac1c`.

The scientific/documentary findings were fixed in the preregistration before implementation. The later typing correction changes only CLI type narrowing and does not modify the contract, evidence manifest, canonical review, rights findings, provider-semantics findings or permission state.

## Public documentary evidence

Official FMP public surfaces were inspected on 2026-09-12 without authenticated provider access:

- `https://site.financialmodelingprep.com/developer/docs`
- `https://site.financialmodelingprep.com/terms-of-service`
- `https://site.financialmodelingprep.com/developer/docs/pricing?planType=commercial`

The API documentation publicly lists the three registered stable endpoint identities and demonstrates `page` / `limit` examples for each:

- `fmp_articles`
- `general_latest`
- `stock_latest`

The documentation supports only documentary endpoint identity and pagination-parameter existence. It does not authenticate the research protocol's exact date-window, ordering stability, terminal-page/exhaustion rule, revision semantics, late-arrival semantics, decision-interval completeness or provider observation clock.

Public terms make dataset/API availability and usage dependent on the applicable account, subscription and/or Order Form, and describe restrictions and obligations relevant to copying/downloading, display/redistribution, stored-data security and termination. No account-specific agreement or written provider authorization was inspected, so archival/storage/research-retention rights remain blocked rather than inferred.

These pages are mutable public surfaces; the repository records the observation date and documentary claims but does not claim an immutable provider snapshot.

## Implemented evidence graph

Added a canonical manifest, pure validator, offline CLI, aggregate canonical review and deterministic tests. The implementation is stdlib-only for the validation graph and has no network, provider, environment-secret discovery or Mongo dependency.

The fixed successful review is:

- `engineering_status=PASS_PROVIDER_EVIDENCE_AUDIT`
- `documentary_endpoint_identity_status=PASS`
- `documentary_pagination_parameter_status=PASS`
- `provider_request_semantics_status=BLOCKED`
- `account_entitlement_status=BLOCKED`
- `activation_readiness_status=BLOCKED`
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`

Six unresolved gates remain: account entitlement, date-window semantics, exhaustion semantics, ordering stability, revision/late-arrival semantics and storage/retention rights.

All provider access, storage mutation, runtime-adapter execution, workflow activation, history construction, Temporal State fitting, training, outcome access, model fitting and MM1 execution permissions remain false.

## Validation evidence

Initial implementation head `f375f9d46c793f4fdab548de80a3ccb7aec75e21`:

- source preservation: PASS for all 157 inherited files;
- scoped Ruff: PASS;
- synthetic-Mongo job: PASS;
- strict mypy found exactly one CLI typing error before the full scientific gate could continue: indexing an `object`-typed nested review value in `validate_phase4_provider_evidence.py`.

The error was corrected in separate commit `a06d09896c4a27680b69713bfd230b3bde8eac1c` by explicitly narrowing the already validated aggregate permissions object. No scientific evidence or fixed finding changed.

Corrected head `a06d09896c4a27680b69713bfd230b3bde8eac1c`:

- `Tests` run `34684249440`: PASS, `837 passed, 20 skipped`;
- `Phase IV gates` run `34684249517`: PASS;
- scoped Ruff: PASS;
- strict mypy: PASS;
- complete deterministic and inherited regressions: PASS;
- all prior Phase-IV canonical evidence reproductions: PASS;
- disposable wheel build: PASS;
- source preservation before and after gates: PASS for 157 inherited files and the original Stage-0 contract;
- synthetic-Mongo functional tests: PASS.

This evidence commit adds the provider-evidence validator itself as an explicit canonical Phase-IV workflow reproduction. Current-head CI after that commit remains the final remote gate.

## Next permitted operation

After current-head validation and human review, this increment may be integrated. Integration would close only the public documentary audit.

It would not authorize a live FMP request. The next scientific dependency is account-specific entitlement evidence. If and only if rights are sufficient, a separate preregistered, bounded and outcome-blind provider-semantics probe can be proposed. Human authorization remains required before any such live provider access.
