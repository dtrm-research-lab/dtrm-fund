# DTRM Phase IV — Provider Evidence Audit v0

- Status: registered before implementation or provider access
- Date: 2026-09-12
- Scientific parent integration: `02bdc19e501697395526bac7a5a661637dd945f8`
- Scientific parent tree: `23c460d70e508cfafce688f70053a9758f175a26`
- Amends: none; this is a new evidence-only gate after the integrated activation-readiness review

## Scientific purpose

Phase IV asks whether an event-history representation improves the frozen robust MM1 policy beyond point-in-time probabilistic state. Retrospective confirmatory history remains scientifically unusable because historical availability and revision timing are not authenticated. A dormant prospective writer now exists, but prospective activation remains blocked.

This increment narrows that block by separating facts supported by current public Financial Modeling Prep (FMP) documentation from facts that require account-specific entitlement evidence or a separately authorized live semantics probe.

This audit is outcome-blind. It must not inspect returns, labels, portfolio results, model scores, Phase-IV representations, Transformer states or MM1 outputs.

## Fixed graph cut

The v0 graph is documentary only:

`official public documentation -> exact evidence manifest -> pure evidence review -> human checkpoint`

It does not contain a provider request, API key, account login, Mongo connection, runtime adapter, workflow, scheduler or activation path.

## Bound sources

The audit may use only the following public FMP surfaces observed on 2026-09-12:

1. API documentation root: `https://site.financialmodelingprep.com/developer/docs`
2. Terms of Service: `https://site.financialmodelingprep.com/terms-of-service`
3. Commercial pricing surface: `https://site.financialmodelingprep.com/developer/docs/pricing?planType=commercial`

The evidence manifest records documentary claims, not copied page bodies. Public pages are mutable and the repository does not claim to possess an immutable provider snapshot.

## Documentary endpoint findings fixed before implementation

The official API documentation currently lists these three registered prospective source roles and example endpoints:

- `fmp_articles` -> `https://financialmodelingprep.com/stable/fmp-articles?page=0&limit=20`
- `general_latest` -> `https://financialmodelingprep.com/stable/news/general-latest?page=0&limit=20`
- `stock_latest` -> `https://financialmodelingprep.com/stable/news/stock-latest?page=0&limit=20`

Therefore v0 may conclude only:

- the three endpoint identities are publicly documented;
- `page` and `limit` are publicly demonstrated for each endpoint;
- the documentation describes these feeds as latest/recent news surfaces.

The same public surface does **not** establish, for this research protocol:

- a date-window query equivalent to the preregistered seven-complete-day overlap plus current partial UTC day;
- contractual ordering stability across pages or repeated calls;
- the exact terminal-page / exhaustion rule;
- whether empty, short or repeated pages prove exhaustion;
- revision semantics for a logical article/event;
- late-arrival semantics;
- completeness of the feed for any decision interval;
- a provider-authenticated observation clock.

No missing semantic may be inferred from endpoint names, sample responses, common REST conventions, legacy collector behavior or third-party SDKs.

## Documentary rights findings fixed before implementation

The public Terms of Service observed on 2026-09-12 state that the specific Data/APIs available to a customer are identified by the pricing surface, documentation, Order Form or customer account, and that use is subject to the applicable account/Order Form scope.

The public terms also impose restrictions relevant to this research design, including restrictions on copying/downloading without prior approval under personal-use terms, controls around display/redistribution, security requirements for locations where FMP data is stored, and deletion/cessation obligations on termination. The commercial pricing surface states that display/redistribution requires a specific data display/licensing agreement.

This repository does not interpret those clauses as account-specific authorization. It records only that public terms make entitlement conditional on the customer's actual subscription/agreement.

Therefore v0 fixes:

- `account_entitlement_evidence_present=false`;
- `exact_payload_storage_authorized=false`;
- `research_retention_authorized=false`;
- `redistribution_authorized=false`;
- `termination_retention_authorized=false`.

No legal conclusion is promoted from public documentation alone.

## Required future evidence classes

The following remain separate future gates:

### Account entitlement evidence

A human may later provide a redacted plan/account/Order Form description or written provider clarification that is sufficient to establish the permitted datasets, use case, storage, research retention and any publication/display constraints. Secrets, API keys, billing identifiers and personal credentials must never be committed.

### Provider semantics probe

A live probe, if later authorized, requires a separate preregistered contract before any request. It must use a dedicated least-privilege credential, fixed non-outcome-sensitive request times, bounded pages, no historical reconstruction, aggregate evidence output and no source content in logs/reports. It must test ordering, pagination termination, repeat-call stability and late-arrival/revision behavior without using market outcomes.

Approval of this documentary audit does not authorize that probe.

## Evidence manifest contract

Implementation may add one canonical JSON manifest containing only:

- source URLs and observation date;
- registered endpoint role/path identities;
- booleans for what public documentation does and does not establish;
- public-terms evidence categories;
- unresolved evidence gates;
- fixed scientific/operational permission flags.

The manifest must contain no API key, authentication header, cookie, account identifier, billing information, provider payload, article title, URL from a returned news item, ticker, Mongo URI or database secret.

## Pure validator contract

Implementation may add a deterministic stdlib-only validator that:

1. rejects extra keys and type mismatches;
2. canonicalizes only explicitly unordered policy/evidence sets;
3. requires exact source URLs, endpoint identities and fixed documentary findings;
4. rejects any false-to-true promotion of account rights, provider semantics, activation or scientific permissions;
5. rejects secret-shaped strings without echoing rejected values;
6. produces only aggregate review evidence;
7. performs no network, environment, filesystem discovery beyond explicit input/output files, provider or storage access.

## Fixed v0 output

After successful engineering validation, the only permitted outcome is:

- `engineering_status=PASS_PROVIDER_EVIDENCE_AUDIT`;
- `documentary_endpoint_identity_status=PASS`;
- `documentary_pagination_parameter_status=PASS`;
- `provider_request_semantics_status=BLOCKED`;
- `account_entitlement_status=BLOCKED`;
- `activation_readiness_status=BLOCKED`;
- `scientific_status=BLOCKED_PROSPECTIVE_DEPLOYMENT`.

The following permissions remain false:

- production provider access;
- production storage mutation;
- runtime adapter execution;
- workflow activation;
- history construction;
- Temporal State representation fitting;
- training;
- outcome access;
- model fitting;
- MM1 execution.

No test or fixture may promote those fields.

## Validation gates

Before review, implementation must pass:

- scoped Ruff;
- strict mypy;
- full deterministic/inherited regression suite;
- exact canonical evidence reproduction;
- source preservation for all 157 inherited Phase-III files and the original Stage-0 contract;
- disposable package build;
- current-head `Tests` and `Phase IV gates` workflows.

The workflow may be extended only with the explicit canonical provider-evidence audit reproduction. It must not add secrets, permissions, provider requests or production storage access.

## Promotion sequence after this increment

1. Human review and merge of this documentary audit.
2. Obtain account-specific entitlement evidence without committing secrets.
3. If rights are sufficient, preregister a bounded live provider-semantics probe.
4. Execute and audit that probe only after explicit human authorization.
5. Only after rights + semantics + storage/provisioning + runtime-adapter gates are satisfied may an activation manifest be registered.
6. Human activation remains separate.
7. Audit multiple accepted prospective runs before proposing history construction.
8. Only then may a Temporal State representation experiment be preregistered against frozen MM1.

Approval of this contract authorizes only the evidence-only implementation and validation described above.