# DTRM Phase IV — Evidence-First Operational Amendment v0

- Status: REGISTERED_BEFORE_LIVE_CAPTURE_OR_RUNTIME_ADAPTER_CHANGE
- Date: 2026-09-12
- Scientific parent integration: `c5f5f16d103222e51914140f257f0922966188d1`
- Scientific parent tree: `22b1003cc30142e1722683e88e6c10b64bfd4ff7`
- Backend dormant writer integration: `e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5`
- Backend dormant writer tree: `2b5422f554119ecf48663d5506d9fdd38ab7738f`
- Amends operational gating only; Phase III/MM1 and the original Phase-IV scientific hypothesis remain frozen.

## 1. Purpose

Phase IV exists to test whether event history improves the frozen robust decision policy beyond point-in-time probabilistic information. The project has already established that retrospective legacy news cannot authenticate what information was actually available at each decision time. Prospective evidence collection is therefore the scientifically preferred route.

Prior readiness increments conservatively treated unresolved Financial Modeling Prep account-specific storage/retention rights as a prerequisite to any live provider request. The human research operator has now explicitly directed that this uncertainty must not stop evidence collection before the scientific value of Phase IV is known.

This amendment therefore separates two independent axes:

1. `scientific_evidence_status`: whether prospective observations may be collected and preserved for the Phase-IV research experiment;
2. `provider_rights_status`: whether account-specific licence, retention, redistribution and long-term storage rights have been fully reviewed.

The second axis remains unresolved. It is not silently promoted to permission. It simply ceases to block bounded private experimental evidence collection.

## 2. Human research authorization recorded before live capture

On 2026-09-12, before any Phase-IV live prospective capture under this amendment, the human research operator explicitly authorized the project to:

- continue collecting scientific evidence without first contacting FMP for written clarification;
- obtain raw provider data required for evidence;
- preserve and work on raw data as scientifically necessary;
- defer provider-rights clarification until the project has evidence about the impact and value of Phase IV.

This is a research-operator authorization, not a representation that FMP has granted any particular contractual right. Provider rights remain a distinct unresolved risk.

## 3. Evidence-first principle

The collector must preserve enough information to answer the scientific question without reconstructing history after outcomes are known. The prospective evidence boundary therefore continues to permit the exact evidence design already preregistered:

- exact raw provider response payload for admitted observations;
- exact extracted UTF-8 content;
- payload and content SHA-256 digests;
- source identity and conservative event identity;
- immutable version/predecessor lineage;
- first-seen and version-observed UTC instants;
- collector run clocks and request fingerprint;
- mapping-version identity and immutable ticker-link provenance;
- append-only ledger sequence and record hashes;
- accepted-run manifest and code/workflow lineage.

Raw evidence must not be weakened merely to avoid the unresolved rights question. If later provider clarification requires a different retention or publication boundary, that change must be outcome-blind, separately registered, and must not rewrite what the collector actually observed.

## 4. Provider-rights status is deferred, not resolved

The account-specific rights review remains scientifically relevant but is reclassified as:

`provider_rights_status=DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT`

This means:

- the repository makes no claim that exact-payload archival, retention duration, redistribution or publication rights are established;
- Issue #18 remains the eventual provider-rights clarification dependency;
- unresolved rights do not block private research collection under this amendment;
- unresolved rights **do** continue to block public redistribution of raw FMP payload/content and any claim that the evidence store is licensed for indefinite/product use;
- before any raw provider material is publicly released, redistributed, commercialized or promoted into a long-term production product, the rights question must be revisited.

Derived scientific findings may later be evaluated separately from raw-data publication. Nothing in this amendment authorizes raw provider-data publication.

## 5. Security and data-handling boundary

Live capture may use a provider credential already provisioned outside the repository, but:

- API keys, bearer headers, cookies, account identifiers, Mongo URIs and secret values must never be committed, echoed in reports or written into evidence documents;
- the runtime adapter must obtain secrets only from the execution environment/secret store;
- logs must redact request authorization material and must not emit raw payload/content by default;
- raw evidence must remain in a private research boundary or private CI artifact/evidence store;
- aggregate validation reports remain source-value-free;
- legacy `trumpMinMax.trumpNews` remains untouched by the Phase-IV prospective path.

The existing prospective namespaces remain the preferred durable store:

- `trumpMinMax.phase4ProspectiveNewsV0`
- `trumpMinMax.phase4ProspectiveRunsV0`

A bounded private GitHub Actions artifact may be used as an initial live-probe evidence boundary before durable Mongo activation, provided it preserves the exact raw response bytes, canonical hashes, run clocks, code identity and request fingerprint and does not pretend to be confirmatory history.

## 6. What becomes authorized by this amendment

After this amendment is implemented and validated, the following transitions may be proposed and executed in separate engineering increments without first resolving provider rights:

- concrete FMP network adapter for the three registered news roles;
- bounded live provider-semantics probe using the existing secret boundary;
- private raw-response evidence capture;
- exact hashing and extraction at the I/O boundary;
- deterministic conversion into the already registered prospective-capture domain model;
- private artifact persistence for initial live evidence;
- later append-only Mongo persistence after the storage boundary is technically reviewed;
- repeated prospective evidence runs needed to establish an authentic observation interval.

The three registered provider roles remain:

| Role | Endpoint |
| --- | --- |
| `fmp_articles` | `https://financialmodelingprep.com/stable/fmp-articles` |
| `general_latest` | `https://financialmodelingprep.com/stable/news/general-latest` |
| `stock_latest` | `https://financialmodelingprep.com/stable/news/stock-latest` |

The fixed operational safety bounds remain outcome-blind unless separately amended before use:

- `max_pages_per_role=100`
- `max_candidates_per_run=25000`
- `max_new_versions_per_run=5000`
- `max_payload_bytes_per_candidate=1048576`

## 7. What remains scientifically blocked

Evidence collection is not evidence interpretation. This amendment does **not** yet authorize:

- treating any collected interval as complete or provider-authenticated;
- constructing the final scientific Temporal State history;
- choosing treatment windows based on realized performance;
- opening protected outcomes;
- fitting or tuning a Temporal State representation against outcomes;
- changing the frozen Phase-III/MM1 policy;
- evaluating MM1 with Temporal State;
- selecting the final cohort based on outcome performance.

Those gates remain closed until enough prospective evidence exists to preregister a history-construction and Temporal-State representation contract outcome-blindly.

## 8. Scientific status model after this amendment

The previous `BLOCKED_PROSPECTIVE_DEPLOYMENT` state remains historically valid for prior artifacts but is superseded for the new evidence-first operational path.

The new aggregate state is:

- `scientific_evidence_status=AUTHORIZED_PROSPECTIVE_EVIDENCE_CAPTURE`
- `provider_rights_status=DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT`
- `live_provider_probe_permitted=true`
- `private_raw_evidence_capture_permitted=true`
- `private_raw_evidence_processing_permitted=true`
- `public_raw_provider_data_redistribution_permitted=false`
- `confirmatory_history_construction_permitted=false`
- `temporal_state_outcome_fitting_permitted=false`
- `outcome_access_permitted=false`
- `mm1_execution_permitted=false`
- `phase3_policy_mutation_permitted=false`

A runtime adapter or workflow still must bind exact code, fail closed on missing credentials/HTTP/schema/bounds errors, and preserve the registered causal clock and lineage rules.

## 9. First live-evidence increment

The immediate next engineering increment should be a bounded, manually invoked private evidence probe in `tech-com-UA00001/theresistance-back` descending from `e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5`.

It should:

1. use the existing `FMP_API_KEY` secret boundary without inspecting or printing the secret;
2. call only the three registered stable news roles;
3. record `started_at` immediately before the first request and `response_received_at` after all accepted response bytes are received;
4. archive exact raw response bytes in a private run artifact;
5. calculate request/payload/content digests and aggregate counts;
6. characterize observed ordering, page behavior, empty/short-page behavior and repeatability without inferring guarantees that were not observed;
7. perform no Mongo write in the first probe;
8. expose no raw payload/content in logs or public reports;
9. produce a canonical aggregate evidence report suitable for later review;
10. keep history, Temporal State fitting, outcomes and MM1 closed.

This first probe is evidence acquisition, not model evaluation.

## 10. Promotion sequence toward the scientific objective

1. Integrate this amendment after current-head tests and human merge approval.
2. Implement and validate the bounded live FMP evidence probe in the backend.
3. Human-authorized execution produces the first prospective raw-evidence artifact.
4. Repeat enough outcome-blind runs to characterize request behavior, revisions/late arrivals and temporal continuity.
5. Audit the accepted interval and define the usable event-history boundary.
6. Preregister the Temporal State representation before protected outcomes are opened.
7. Construct the event-history state from accepted prospective evidence.
8. Feed that state into the frozen Phase-III/MM1 decision layer without retuning MM1.
9. Open outcomes only under the preregistered comparison contract.
10. Compare Temporal State + frozen MM1 against the point-in-time probabilistic-state + frozen MM1 control.
11. Only after scientific value is observed should the project decide whether provider-rights clarification, longer retention, productization or alternative data sourcing is worth pursuing.

## 11. Validation requirements

Before merge, this amendment must be mechanically bound to the exact parent integration and must prove:

- no Phase-III/MM1 source or frozen data changed;
- no prior Phase-IV evidence artifact was rewritten;
- provider rights remain explicitly unresolved;
- live evidence collection is separated from outcome/model permissions;
- public raw-data redistribution remains false;
- secret material is absent from the amendment and any machine-readable companion;
- current tests, Phase-IV gates, Ruff, strict mypy, package build and source-preservation gates remain green.

## 12. Authorization boundary

Approval of this amendment authorizes the project to continue toward the Phase-IV scientific objective using private prospective raw FMP evidence before provider-rights clarification. It does not authorize raw-data redistribution, product deployment, outcome-driven retuning or mutation of the frozen Phase-III/MM1 policy.
