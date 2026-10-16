# Phase IV — prospective per-asset coverage and immutable clock acquisition v0

**16 October 2026. CONTRACT FIRST / DESIGN FOR REVIEW; no source reads, AWS execution, training, outcomes, or Phase-III/MM1 changes.**
Parent: Phase-IV source-authenticated history coverage/decision-clock design v0 and review addenda. This contract is an *operational refinement*, not an independent confirmation registration, a replacement for v3's 14 UTC days / 56 target slots, nor an assertion that retrospectively dated Mongo records were first observed on publication date.

## Observed pre-design facts and strict limits

An operator-local bounded, majority-read, non-atomic current Mongo pilot on 2026-10-16 passed. Its private report shows complete-day **publication** date coverage and that `matched_tickers` is an array of objects on all currently sampled rows. A follow-up local weekday/weekend comparison found a large calendar-dependent density difference. Public commits intentionally do not include report counts, per-source digests, news, ticker identities, or operator credential details. None of those reports proves historical content vintage, original ingestion clock, historical stock association, trading-calendar sufficiency, or immutable acquisition.

Merged PR #40 provides a separately permissioned `$type`-only, aggregate BSON census to assess the nested object *shape*; even a positive shape report does not prove an asset-link's authenticity or `linked_at`. An earlier live backend `--apply` procedure updated or attempted to update existing associations; therefore neither present `matched_tickers` nor an ObjectId generation timestamp is an admissible first-link timestamp.

## 1. Registered input identity: one frozen candidate manifest before any history bins

Before any per-asset coverage assessment or historical sequence feature, freeze an **outcome-blind** and reproducible manifest of decision candidates `(event_key, asset_id_asof, decision_cutoff_utc)`, with stable source and cohort identity, explicit common universe, point-in-time symbol/corporate-action mapping and matching controls. No ticker may be added or removed based on observed history counts or outcomes. Freeze `lookback_L` (independent of 60-day *forward target*), earliest authenticated capture boundary, decision cutoffs, content and link eligibility definitions, raw revision-collapse logic, and chronological assignment to TRAIN/VALID/CALIBRATION/untouched TEST (or deterministically immutable assignment rule) **before looking at per-candidate history-bin results**. Freeze dependence-aware purge/embargo: 60-calendar-day outcome horizon plus inherited five-day price tolerance. Never use a random row split.

The four nominal UTC v3 probe slots `00:15/06:15/12:15/18:15` are *capture triggers*, NOT automatically the stock-decision cutoffs. A distinct registered decision timetable must be checked against the exact frozen Phase-II C0 input availability (prices and pre-event beta). If incompatible: `BLOCKED_CONTROL_CLOCK_MISMATCH`, not a changed MM1.

## 2. Three distinct clocks and a proof of availability

For each logical source event `e`, version `v`, mapping to asset `a` and decision cutoff `t`:

- `published_at`: provider/editor time, descriptive only and never eligible first-seen evidence.
- `version_observed_at`: the **first independently authenticated response-received UTC time** at which the exact content version was acquired by the research collector, carrying trusted runtime identity, source request fingerprint, response bracket, provider role, provider event identity, raw private content digest and revision/predecessor chain.
- `linked_at`: first **independently authenticated** UTC time at which exact `(e,v,a,mapping_version)` mapping/association was available. Mapping changes are append-only revisions, not rewrites to older vintages.
- `ledger_committed_at`: immutable evidence-record persistence/acknowledgement instant, stored separately; delayed persistence and partial failures must not silently manufacture an earlier availability time.
- `target_slot_utc` and `dispatch_at` are transport diagnostics, never substitutes for response-received or first-link clocks.

An admitted version-link at `t` requires `max(version_observed_at,linked_at) < t` **strictly**; ties or timestamp uncertainty that overlaps `t` are `UNKNOWN_AVAILABILITY` unless an independently verified sequence watermark resolves ordering. Precision/error bounds, UTC normalization, producer clock source and external receipt authority are frozen before promotion. A trusted observed event may be older than the requested lookback, but only a separately justified complete retrospective window permits labeling zero prior observations.

## 3. Exact prospective acquisition and immutable storage contract (NOT YET IMPLEMENTED)

Private source-value boundary must bind: source role (distinct `fmp_articles`, `general_latest`, `stock_latest`, no pooling their clocks), request fingerprint `932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`, run attempt, GitHub workflow commit/tree, authenticated v3 campaign/slot/dispatch, trusted AWS scheduler-origin evidence, source response bounds, content digest, mapping digest, version predecessor, and the explicit writer/storage authority.

Writer design requirements before any data collection:
1. **Private append-only** per-capture record (no overwrite/upsert of previous evidence); request/capture identity as immutable key, separate logical event/version identity, dedupe without losing first authentic occurrence. Content bytes remain private under reviewed retention/contractual permissions; hashes alone cannot reconstruct content.
2. Atomically bind content+mapping versions, normalized observed clock and immutable storage acknowledgement, or mark the acquisition `INCOMPLETE`; retries preserve original identity, never backdate or replace the first successful record.
3. Use bucket version ID, immutable retention controls (Object Lock where operator separately approves creation, retention and associated cost), exact SHA-256 and independently authenticated provider readback; an ordinary S3 VersionId, self-hash, local operator timestamp or CloudTrail log is not an independent clock attestation by itself. Storage of a digest is not proof of external first-seen.
4. A per-capture signed canonical manifest includes `schema_version`, `campaign_id`, `source_role`, `request_fingerprint`, `scheduled_at_utc`, `actual_capture_started_at_utc`, `response_received_at_utc`, `ledger_committed_at_utc`, `attempt`, `runtime_commit`, `object_version_id`, `content_sha256`, `link_mapping_sha256`, `predecessor_digest`, `observation_digest`, `independent_evidence_status`, and detailed failure/missingness status. Real source payload, symbols, connection strings, credentials, protected outcomes and model scores must never enter public PR artifacts.
5. Separately freeze AWS Scheduler CreateSchedule/Invoke provenance, verified role trust, first-write DynamoDB claim, signed GitHub dispatch and executed writer run/receipt; a successful DynamoDB claim alone remains insufficient. Configure/verify the Lambda `Invoke` data-event capture *before* the single noncounting diagnostic, followed by one-shot origin attribution. All AWS costs and mutations need separately scoped approval.
6. No open access to FMP/Mongo retention, redistribution or long-term archive assumed; keep FMP account rights issue #18 open. A 14-day successful scheduler campaign proves basic process adequacy, not all 60 days of authenticated history or enough independent histories to fit T.

## 4. Per-asset measurement and reconciliation

Given **frozen manifest** of asset decision candidates, produce privately, for each `(asset_id_asof,t)`:

- `raw_source_sightings`, `distinct_event_keys`, `available_content_versions`, `authenticated_asset_links`, `deduplicated_admissible_events`, `revisions_seen`, `reappearance_count`;
- `unknown_version_clock`, `unknown_link_clock`, `unknown_mapping_authority`, `left_truncated_capture_window`, `missing_provider_run`, `unknown_control_clock`, `uncertain_revision_predecessor` — explicit unresolved counts/reason bitsets, no hidden zeroes;
- `effective_age_hours = (t - max(version_observed_at,linked_at))` only for strictly admissible events; immutable interval summary (count/min/median/p90/max) and time bins **preregistered independently of outcomes**, not chosen after return comparisons;
- `provider_role`-specific counts and confidence in feed/capture completeness; never equate provider top-N API page to exhaustive market news;
- report trading decision days vs **NYSE session calendar** days, including market holidays/early closes and DST changes, with pinned calendar version. Weekend/holiday publications are retained at actual arrival time and first become admissible at the next eligible decision cutoff **if** clocks and source rules permit; never assign them to Friday or backdate them to the prior trading session.

Report on the **full common denominator**, including unknown, zero authenticated (only if window complete), short and long histories. Reconcile partition and aggregate counts exactly with frozen candidate manifest; show coverage by TRAIN/VALID/CALIBRATION/TEST, capture epoch and session kind, with confidentiality-safe public summaries only.

Candidate history categories inherit the existing contract: `UNKNOWN_AVAILABILITY`, `ZERO_AUTHENTICATED`, `ONE_TO_FOUR`, `FIVE_TO_NINETEEN`, `TWENTY_PLUS`. A mapping whose original `linked_at` is unknown is **not** `ZERO_AUTHENTICATED`. Do not change bin cutoffs to optimize retention.

## 5. Failure, release and scientific boundaries

- Missing event/link authority, left-truncated lookback, old writer/backfill without trustworthy link clock, ambiguous revision or control-clock mismatch -> `UNKNOWN_AVAILABILITY` or explicit `BLOCKED_*`, no synthetic positive age, no promotion to training.
- Inconsistent source totals, tampered manifest/digest, counter drift or duplicate logical identity -> fail closed; keep original bytes and audit reason privately, never cherry-pick a favorable re-run.
- No protected forward prices, labels, model fitting, calibration, features from future state, action selection, production MM1 or humanclause.com modifications in this design increment.
- Future scientific fit order: **B** simple authenticated history first, then **S**, **T** sequential Transformer, **O** order ablation against frozen **C0**, all using frozen MM1 policy and nominal/P10 interface; outcome-blind, sealed common cohorts and preregistered inference. Endpoint remains realized paired `Delta(T,C0)`, not a dashboard NAV.
- This document freezes no dataset, starts no campaign, and proves no first-seen. Next: code review / separate local shape audit / implement instrumented append-only adapter with adversarial and retention tests / approve AWS diagnostic then explicitly approve prospective v3 activation.

**Current indicators:** `schema_design_review_only=true`; `authenticated_per_asset_coverage=false`; `immutable_capture_deployed=false`; `g5_source_audit_satisfied=false`; `temporal_state_training_permitted=false`; `scientific_counting_permitted=false`; `outcome_access_permitted=false`; `mm1_execution_permitted=false`.
