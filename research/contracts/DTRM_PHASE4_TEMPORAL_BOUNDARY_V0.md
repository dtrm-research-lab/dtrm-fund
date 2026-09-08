# Phase IV temporal boundary v0 — proposed contract

Date: 2026-09-08. Status: DRAFT_FOR_REVIEW; specification only.
Base: approved integration `f5148f2f6787d3282c04a357e59d32ed3c515ba8`.
Parent: original Phase-IV v0.1 contract, preserved byte for byte.

> The machine searches. The human defines the game.
>
> The next frontier in AI decision-making may not be better prediction,
> but better use of what the machine already knows.

## Scope and stage boundary

This increment specifies a future synthetic availability verifier and its
acceptance matrix. It implements no firewall, clock adapter, history selection,
feature construction, fit, policy execution, or evaluation. Stage 1 is not
closed. Review and source/clock bindings must precede Stage-2 implementation.
The separate source-feasibility PR #4 remains unmerged and is not a dependency
or an accepted source of scientific evidence for this contract.

The user prohibits agent access to secrets and environment configuration.
Do not inspect their presence or contents, load dotenv files, connect to the
production source, or seek alternative credentials. Agent validation uses
explicit synthetic fixtures only. Any later real audit is operator-run outside
this environment; share only the preregistered sanitized aggregate report.
This restriction supersedes earlier suggestions to configure live access here.

The future verifier will answer only whether declared availability metadata
passes a proposed cutoff rule. It cannot authenticate that metadata. Neither
a synthetic PASS nor complete timestamp fields establish historical readiness.

## Proposed clock semantics, not a real decision schedule

A proposed cutoff is an explicit timezone-aware instant. Normalize equivalent
instants to UTC without rounding. Date-only, naive, absent and malformed
cutoffs fail; never infer midnight, exchange close, UTC or an execution time.
The experiment's calendar, timezone, decision schedule and target entry timing
remain unbound. No proposed synthetic convention licenses a day-level study.

For a version and one of its recorded asset links, reuse the ontology's
availability definition: `max(version_observed_at, linked_at)` when both are
known. Missing either produces UNKNOWN, never an inferred time. Publication,
occurrence, logical first-seen, ObjectId creation, present audit time and
historical replay time cannot substitute for either availability clock.

Proposed conservative comparison: availability strictly before cutoff passes
the metadata check; availability after cutoff is AFTER_CUTOFF; equality is
AT_CUTOFF_UNRESOLVED. Tied timestamps alone cannot prove which operation was
visible first. Admitting equality would require a separately reviewed binding
to an authenticated sequence/watermark, never lexical IDs or input order.
This proposal resolves no real-data tie using synthetic outcomes.

Each version is checked separately. An old logical first-seen cannot backdate
a revision. The verifier must not select a latest version, treat revisions as
independent candidates, or silently keep an earlier version when a later
revision has unknown availability. Actual as-of revision and mapping selection
requires a later registered history rule and authenticated archives.

An observation without links produces an explicit NO_ASSET_LINK diagnostic.
It is not an empty accepted history. Unknowns, ties and future observations
remain visible in the complete review output; no candidate is dropped and no
common cohort or capacity K is computed by this graph.

## Future graph definition

The proposed input envelope has exactly `schema_version`, `cutoff`, `batch`.
Version: `dtrm.phase4.temporal_boundary_input.v0`. The embedded batch follows
the existing event ontology unchanged and must declare `dataset_role=synthetic`.
An unaudited or purportedly approved batch fails this synthetic-only entrypoint.
No feature values, model artifacts, prices, credentials or labels are accepted.

| Node | Typed input and immutable output | Invariant and failure | Permitted side effects |
| --- | --- | --- | --- |
| Envelope normalizer | JSON object to UTC cutoff and existing EventBatch | Exact keys; synthetic role; existing schema checks; fixed error code on invalid input | None |
| Revision validator | EventBatch to validated EventBatch | Reuse complete-chain invariants; no repair, imputation or inferred order | None |
| Availability assessor | Cutoff and validated batch to tuple of diagnostics | One diagnostic per version/link, or explicit linkless diagnostic; BEFORE_CUTOFF, AFTER_CUTOFF, AT_CUTOFF_UNRESOLVED, UNKNOWN_AVAILABILITY, NO_ASSET_LINK | None |
| Review serializer | Immutable assessment to deterministic JSON | Canonical identity/ticker ordering; counts reconcile; no admitted history; permanent scientific blocks | None |
| Synthetic CLI | Explicit fixture path to new report path | Fail without successful report on any invalid node; refuse existing paths/symlinks and overwrite; fixed redacted errors | Read named fixture, exclusively create named report only |

Domain state uses frozen dataclasses and tuples, not mutable dictionaries held
inside state. Normalization validates before construction. Public graph entry
revalidates input; callers cannot bypass the boundary by asserting approval.
Serialization may allocate fresh dictionaries without exposing mutable state.
The canonical digest binds normalized cutoff and full normalized input, not
just passing rows; a digest establishes identity, not timestamp authenticity.
Repeated runs and permutations of events/links produce identical report bytes.

Every successful report must state:

- `engineering_status=PASS_SYNTHETIC_TEMPORAL_BOUNDARY` means protocol execution,
  not that every diagnostic is BEFORE_CUTOFF.
- `scientific_status=BLOCKED_SOURCE_AUDIT` and `source_authenticated=false`.
- `decision_clock_bound=false`, `history_construction_permitted=false`,
  `training_permitted=false`, `outcome_access_permitted=false`.

The CLI has no Mongo mode, dotenv option, credential discovery or network
adapter. It cannot consume a real report as an approved source binding.

## Unresolved real-data bindings and promotion blockers

| Binding | Evidence and decision required before relevant implementation/use |
| --- | --- |
| Exact content vintage | Archived bytes plus authenticated version observation and revision lineage; schema/digest syntax alone is insufficient |
| Mapping and universe | Historically available asset links, mapping versions and universe membership; current tickers cannot be backfilled silently |
| Decision clock | Explicit schedule, timezone, precision, tie/watermark semantics, and relationship to target entry; no default midnight or same-day-close assumption |
| Frozen control compatibility | Provenance of every baseline input, including pre-event beta and its price dependencies, against the same cutoff; a violation blocks Phase IV, never edits Phase III |
| Price/derived data | Separately approved ontology, exact vintages and availability of every dependency, corrections and corporate actions; current feature computation does not prove historical availability |
| Exposure and coverage | Audited source coverage and exposure ledger; V2–V6 are consumed evidence, not a fresh confirmatory cohort |
| History and common cohort | Current-event treatment, version selection, lookback, truncation, empty/short histories and missingness fixed before outputs; no outcome-based row exclusion |
| Partition and fitting | Explicit temporal partitions, label-availability purge/embargo and shared-history dependence; no held-out tokenizer, normalization, pretraining or calibration fits |
| Evaluation | Frozen statistical addendum and action/cohort commitment before protected target release; no outcome-driven retuning |

These are requirements, not authenticated facts or executable adapters. A later
review must bind them with outcome-blind evidence before declaring the relevant
gate closed. Prospective collection, alternate sources or a changed estimand
require separate approval; absence of archives cannot justify fabricated clocks.

## Validation plan and next permitted operation

The companion acceptance matrix fixes expected cases before implementation.
Contract-only checks now: consistency with the existing ontology and Stage-0
boundaries, scoped lint/type checks, existing unit/functional/regression suite,
reproduction of existing synthetic evidence, source preservation, disposable
wheel build, and current-head CI. Existing tests do not test this unimplemented
verifier; no new firewall test pass is claimed.

After human review, preserve this registration commit as an ancestor. Complete
the required Stage-1 source/clock bindings before implementing the Stage-2
firewall. The next outcome-blind work may resolve those bindings or refine a
separately versioned proposal; it may not train B/S/T/O or access targets.
