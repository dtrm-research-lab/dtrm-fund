# Phase IV — Source-authenticated history coverage and decision-clock acquisition design v0

**2026-10-14 — CONTRACT-ONLY / DRAFT_FOR_REVIEW, before any implementation, provider-value read or model fitting.** Review corrections preregistered in `DTRM_PHASE4_AUTHENTICATED_COVERAGE_REVIEW_ADDENDUM_V1.md`.

Research branch parent: `research/phase4-temporal-state`. Governing contracts: `DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md`, `DTRM_PHASE4_EVENT_ONTOLOGY_V0.md`, `DTRM_PHASE4_PROSPECTIVE_CAPTURE_PROTOCOL_V0.md`, `DTRM_PHASE4_PROSPECTIVE_TEMPORAL_EVIDENCE_V1.md` and `DTRM_PHASE4_PROSPECTIVE_CAMPAIGN_V3_OPERATIONAL_REPLACEMENT_V0.md`. This proposal is a **preregistered design for a later source audit** and does not resolve or replace any existing freeze.

## 1. Research question and observed feasibility constraint

Question: does a historically admissible event-state representation T produce higher **realized** Top-K mean than the frozen C0 control, with the **same exact Phase-III/MM1 policy**, in inherited Phase-II target units?

Available Phase-IV source-audit findings are negative for authentic retrospective state:

- 2026-09-08, 1,000 bounded Mongo samples lacked observed vintage, first-seen, and ticker-link availability fields at the registered paths.
- 2026-09-10, full registered retrospective source census found **63,873 current rows**, 63,873 BSON ObjectIds, 34,173 same-calendar-day ObjectId/provider-day diagnostic matches and substantial later-date deltas, but insufficient writer/clock/mutation provenance to authenticate `as-of` histories. Classification **RETROSPECTIVE_PROXY_PARTIAL / BLOCKED_SOURCE_AUDIT**.
- Existing capture v1 / 14-day, 56-slot campaign is a **collector-process adequacy** contract, not an automatic declaration of enough history, labels, longitudinal coverage, training independence or confirmatory outcomes.

**Result:** No current retrospective rows may be silently counted as authenticated past observations, no selection of favorable test periods or 20+ thresholds, no training or opening protected forward outcomes in this increment. An empty observed sample is **not** automatically an authenticated zero-history candidate.

## 2. Eligibility: the machine's recorded information, not publication dates

For logical news observation `e` and asset association `a`, an admissible historical version `v` at prospective decision cutoff `t` must provide:

1. Exact registered collector/provider request role and stable logical identity, with specified fallback URL identity; content vintage bytes/digest and complete immutable revision chain relative to a verifiable ledger head.
2. A trustworthy `version_observed_at` anchored to run response-received clock; a separately trustworthy `linked_at` for the asset mapping/vintage, no backdating from publication dates or prior version first-seen.
3. The effective candidate-observation availability `A(e,v,a) = max(version_observed_at(v), linked_at(v,a))` must be **strictly earlier** than the explicitly registered decision UTC cutoff. An equality/tie is **UNRESOLVED** absent an independently verified sequential watermark; future/unknown must never count as earlier.
4. The mapping version, asset identity, point-in-time universe membership and permission to use the source as of `t` must be supported. A present ticker list or current asset symbol is not proof of historical mapping.
5. A complete, ordered vintage view as of `t`: revisions of the same logical source observation collapse to **one** event, selecting the latest *proven* version available before `t`. Missing predecessor/late modification/ambiguous version observation blocks authentication; do not elect the most favorable or current text.
6. The current candidate event is not included in its own prior history. Comparisons C0/S/B/T/O may have current-event information only as specified by the common frozen information protocol.

Timestamp precedence is **observed version/link availability**, not provider `published_at`, Mongo `ObjectId` creation, URL appearance, nominal Scheduler trigger time, GitHub workflow clock or an inferred midnight. Any of those may be diagnostic-only and cannot reclassify UNKNOWN as BEFORE_CUTOFF.

## 3. Provenance evidence and trust boundaries

A later privately governed collection/acquisition must establish all of:

- Frozen source fingerprint, exact code/tree/run/workflow, request roles `fmp_articles`, `general_latest`, `stock_latest`, domain identity, append-only writer and controlled retention. The three roles are **not** pooled as though they were a single provider/source clock.
- Actual source response-received time bracket and durable acknowledgement time, aligned with the prospective capture protocol, plus timestamp precision, clock synchronization/error and exact decision schedule.
- Independent Scheduler→Lambda→DynamoDB claim→GitHub authenticated dispatch origin gate and accepted run-artifact lineage when using v3. Synthetic HMAC validity or self-hashed post-hoc S3 evidence does not prove AWS causality.
- Version bytes private under authorized rights, SHA-256, logical source identity, predecessor lineage, mapping digest, asset-link availability, duplicate/reappearance records and bounded capture-window omissions.
- Immutable ledger chaining and explicit **coverage completeness** from a documented start. A small number of successful runs demonstrates snapshots, **not** completeness of a historical lookback window or an exhaustive market news feed; bounded top-40 pages are not a market census. The history lookback `L` is an independent, outcome-blind binding: it is **not** inherited from the 60-calendar-day future target horizon.
- An audited independent price/pre-event beta and inherited baseline prediction availability at the **same** cutoff; if the inherited frozen Phase-II control used a same-day price not known then, mark the proposed comparison `BLOCKED_CONTROL_CLOCK_MISMATCH` rather than changing Phase III.

If any trust boundary is unproven, report it as `UNKNOWN` or `BLOCKED`. Retrospective ObjectId chronology may only be considered in an **explicitly labeled exploratory** branch after a separate provenance addendum and never substitute for clean Phase-IV confirmation.

## 4. Observational coverage assessment, before choosing a model

Before acquisition, preregister a deterministic candidate-inclusion rule, decision grid/cutoffs, point-in-time universe and mapping authority without seeing outcomes. Before **any history-bin or sufficiency calculation**, independently freeze the exact complete candidate manifest, its digest, decision cutoffs, history lookback `L`, truncation rules and source coverage start; if real candidates are discovered prospectively, their identities may be finalized under the predetermined rule **after capture but before bin assessment**. Unknown `L` means unresolved coverage, never an implicit 60-day window. These choices cannot be changed after observing the bins. For every frozen common candidate identity `(news_id, ticker, version, t)`, evaluate whether a bounded historical ledger and asset-links are eligible at t. Preserve all candidates, including those without usable history.

Return exactly one logical category per candidate:

| Category | Meaning | Scientific handling |
|---|---|---|
| `UNKNOWN_AVAILABILITY` | Any materially needed vintage/link/decision-clock/coverage property unresolved | Report unknown; never treat as history 0 |
| `ZERO_AUTHENTICATED` | 0 prior events under a demonstrably complete, preregistered observation window | Retain candidate; not excluded |
| `ONE_TO_FOUR` | 1–4 distinct eligible logical events | Retain candidate |
| `FIVE_TO_NINETEEN` | 5–19 eligible logical events | Retain candidate |
| `TWENTY_PLUS` | ≥20 eligible logical events | Retain candidate |

These bins match the separately reviewed **synthetic-only** arithmetic-preflight contract (#35) descriptively; they **do not** establish a minimum sequence length, sample sufficiency, statistical power or training permission. The private stage must distinguish a genuinely covered window from left-truncated history. Under incomplete coverage, an observed count of 0 is **UNKNOWN_AVAILABILITY**, not `ZERO_AUTHENTICATED`.

### Denominators and missingness

Any sanitized aggregate-only report shall include:

- Total prespecified common candidates; eligible-known vs unknown; unknown reasons split into vintage, link, clock, mapping/universe, retained evidence, coverage/left-truncation and control incompatibility.
- History-count bin totals with exact reconciliation to the **full** denominator, no dropping candidates.
- Distinct logical-event count vs raw sightings, revisions, and role-specific provenance; no deduplication by future market outcomes.
- Per-cohort and source role metadata, but **no tickers, titles, source URLs, source values, text, embeddings, model scores, protected prices/targets, secrets or individual decision timestamps in public/PR artifacts**. Keep sensitive details in a privately controlled, hashed evidence bundle as applicable.
- Start/end of independently observed capture in privately authenticated records, run failures, missing target slots, duplicates, log gaps, revision uncertainties and retention guarantees. A digest proves byte identity, not independent authenticity.

The report may state `ENGINEERING_COVERAGE_ARITHMETIC_PASS` for internally consistent counters while permanently asserting `source_sufficiency_certified=false` until all separate G5 gates are satisfied. No aggregation of source-authority ambiguity into a misleading single PASS.

## 5. Decision clock / shared control and outcome exposure

Before even a scientific coverage acquisition can be promoted into source readiness, freeze and independently validate:

1. Prospective decision `t` (timezone, schedule, ties and execution/target-entry instant); nominal UTC collector slots `00:15/06:15/12:15/18:15` are **not** automatically trading decision cutoffs.
2. Frozen control state inputs C0, pre-event beta and pricing dependencies, calibration and target model units relative to `t`; report any incompatibility, **do not alter frozen MM1**.
3. Historical universe/ticker mapping and common candidate membership independent of representation, guarded against survivorship and post-outcome exclusions.
4. TRAIN, VALID, CALIBRATION and untouched confirmatory blocks, an explicit **exposure ledger** for all earlier viewed cohorts V2–V6, and shared-history/ticker/time dependencies.
5. Purging/embargo using the inherited **60-calendar-day** forward outcome with **five-day price tolerance** and exact label-availability interval; do not interpret 14 days of prospective capture as matured 60-day labels.
6. Exact treatment of unavailable labels/zero-history/short-history and full-K infeasibility; any exclusion, imputation or fallback must be registered before unsealing confirmatory targets.
7. Registered paired cohort-level inference, clusters/blocks, confidence-interval procedure, multiple contrasts and no winner-selection by observed score.

## 6. Downstream model attribution (not implemented now)

C0: frozen original Phase-II probabilistic snapshot into frozen MM1. S: matched refitted snapshot without admissible sequence; B: prespecified simple summaries of the **same allowed** history, implemented before T. T: Transformer/sequential state with same candidate universe, time fence, development budget and calibrated nominal/P10 MM1 interface. O: same history content with explicit order/time structure ablated, with residual time cues documented. No new MM1 thresholds, rho/tau, exact-K, fallback, tie-breaking or evaluation metric.

Primary endpoint: realized paired `Delta(T,C0)` of selected Top-K target-model units; T–S/B/O have strictly secondary attribution roles. A zero/null/negative or infeasible result must be reportable. A science paper may describe engineering methodology independently of a positive investment return.

## 7. Preregistered execution sequence and decision statuses

**Step A — current permitted scope:** review this contract against existing prospective capture and Stage-0 science, syntactic checks, frozen-source preservation, current-head CI. No source access or AWS modifications.

**Step B — still unauthorized:** preregister specific *source-authority assessment* protocol, timestamps, retention, role-specific coverage and exact clock. Acquire genuine provider/artifact identity and rights evidence under separate approvals and no protected outcomes.

**Step C — blocked on Step B and operational G2/G3/G4:** first freeze the exact complete candidate manifest and SHA-256, externally justified decision cutoffs, lookback `L`, truncation and coverage-start rules **without inspecting counts, labels or outcomes**; only then derive source-value-free per-cutoff coverage bins from authenticated prospective ledger, reconcile each bin to the locked denominator, and publish sanitized completeness + unknowns with private evidence chain. Do not reinterpret 14-day operational success as model readiness. When `L` is unbound, coverage sufficiency remains `UNKNOWN_AVAILABILITY`/`UNRESOLVED_LOOKBACK`.

**Step D — separately approved after source sufficiency:** freeze full G5 data/statistical addenda, partitions, labels, preprocessing, model budgets and confirmatory exposure **without modifying Step C's locked cohort or history windows**; implement B, S, T, O in the registered order using only development information.

**Step E — strictly after frozen actions and outcomes matured:** paired out-of-sample realized evaluation and replication, then G8 paper/release decision. Inherited production MM1 and humanclause.com remain unchanged throughout unless separately governed.

Flags now: `source_authenticated=false`, `decision_clock_bound=false`, `historical_coverage_confirmed=false`, `g5_complete=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `scientific_counting_permitted=false`, `mm1_execution_permitted=false`, `aws_deployment_permitted=false`.

**Scientific value of this contract:** it separates *getting usable historical evidence* from *testing the temporal representation hypothesis*, preventing infrastructure PASS, source-window partial coverage or arbitrary model depth thresholds from being misreported as realized decision value. No source value or experimental outcome was observed when writing it.
