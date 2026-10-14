# Phase IV shared-cutoff source/price metadata probe v0

**Date: 2026-10-14. Status: REGISTERED BEFORE IMPLEMENTATION.** Base: `research/phase4-temporal-state` merge `beb8aa5a22a84c05c7e4f7f217718e23a092fc6e`; governing original Stage-0 contract and merged PRs #35/#36/#37. Additive only: Phase III/MM1, its 157 inherited files, its price cache, its realized targets and humanclause.com remain untouched.

## Research question and distinction

A legitimate comparison of temporal representation T against frozen C0 must not confuse an object's economic date with the first instant its exact version was available to the machine. The frozen C0 builders truncate observed news dates to calendar day and filter prices with nominal date `<= event_date`. This is a **clock proof gap**, not proof of historical leakage. We need a testable, pure **synthetic-only** shared-cutoff protocol before accepting any real source evidence.

**The synthetic clock probe never authenticates metadata** and never promotes any real news, price history, source ledger, model fit, action or outcome. It does not implement Stage-2 history selection, reconstruct V5/V6, change MM1, assess stock performance or authorize AWS.

## Exact synthetic schema

One envelope with precisely `schema_version="dtrm.phase4.shared_cutoff_fixture.v0"`, `dataset_role="synthetic"`, and `cases` (1–64). Every case must have these exact keys:

- `case_tag`: closed `case_01`–`case_64` vocabulary (unique).
- `decision_cutoff`: timezone-aware full ISO instant; accepted only when unambiguous and normalized to UTC; naive, date-only, invalid, NaN, booleans fail.
- `news_version_observed_at`, `news_linked_at`, `mapping_available_at`: timezone-aware ISO instants or null.
- `price_dependencies`: nonempty list of 1–20 exact objects. Each has `dependency_tag` from closed `price_01`–`price_20`, unique inside its case; `price_session_date` exact YYYY-MM-DD string; `price_first_available_at` and `price_vintage_available_at` as timezone-aware instants or null. **Price session date is never parsed as a time and never used for admissibility.**

All fields are invented metadata: no source URL, ticker, provider role, actual price, score, return, portfolio action, target or secret can enter. Duplicate JSON keys at a later transport boundary must be rejected before calling this pure graph; v0 has **no file/JSON reader**.

## Pure, fail-closed graph

1. Exact schema, counts, identifiers and timezone-aware instant validation. Reject extra/missing keys, same ID duplicates, malformed date, invalid types, and contradictory fields. Freeze typed domain state in dataclasses/tuples and detach mutable input.
2. For each node, compute *synthetic ordering only*: `BEFORE` if its known instant is strictly earlier than cutoff, `AT_CUTOFF` if equal, `AFTER` if later, `UNKNOWN` if absent. Comparing equivalent ISO offsets must yield identical results.
3. **News association:** both exact content-version and asset-link observation must be `BEFORE`; mapping separately must be `BEFORE`. Missing any proof remains `UNKNOWN`, never admitted by a known earlier provider publication date.
4. **C0 prices:** each required synthetic price dependency has BOTH first-availability and exact-vintage availability timestamps. Both must be `BEFORE`, and every declared dependency must pass; any equality/after/unknown yields `SYNTHETIC_BLOCKED`. Future Stage-1 audit must independently prove that the declared dependency set equals **all actual** frozen C0 beta/price inputs. This pure fixture cannot prove such completeness.
5. A case gets `SYNTHETIC_ALL_BEFORE` only if **all** news, link, mapping and price clocks are `BEFORE`; otherwise `SYNTHETIC_BLOCKED`. Carry detailed node statuses and per-dependency statuses so one late dependency never disappears in an aggregate. Total case counts reconcile.
6. Produce immutable assessment and fresh JSON serialization. Report `engineering_status=PASS_SYNTHETIC_SHARED_CUTOFF_ORDERING` solely for parsed/validated synthetic arithmetic. Hardcode `scientific_status=BLOCKED_CONTROL_CLOCK_ATTESTATION`, `source_authenticated=false`, `clock_authenticated=false`, `dependency_completeness_authenticated=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`. No boolean/report allows promoting true.
7. No filesystem, environment, cloud, network, Mongo, FMP, pricing API, model or protected result I/O at all in this increment.

## Test vectors and acceptance

- Same `price_session_date` with one available-before-cutoff and one available-after-cutoff changes outcome; session date alone does not.
- News content before cutoff but asset link after cutoff -> blocked; metadata version observed after first-seen does not backdate it.
- A price first available before cutoff but revised vintage available after cutoff -> blocked.
- Unknown link, missing price time, equal-cutoff event/price -> blocked, never silently count as zero.
- All metadata strictly before cutoff -> synthetic ordering pass, with scientific authority **still false**.
- ISO equivalent timezone offsets invariant; naive/invalid date precision rejects; duplicate identifiers, extra protected outcome keys, boolean time and malformed schema reject.
- Caller mutation of source dictionary or JSON report cannot change frozen state. Permuting case order and dependency order yields identical report.
- Scoped lint, strict mypy, full Phase-IV regression, preserved 157 original inherited Git blob files, package build and current-head CI, with human review before merge. No implementation until this contract commit exists.

## Exit and future real evidence needed

A separate, later operator-authorized source-vintage/clock proof is required: exact decision UTC cutoff, independent first-seen/append-only news version/link/point-in-time mapping proof, price-session market clock and earliest exact price-vintage availability, all frozen C0 beta price dependencies and the downloaded cache's historical reconstruction, immutable manifest of candidate/cohort/training partitions and lookback `L` fixed before any coverage metrics, rights/writer/retention attestation and dispatch provenance. A date-only Mongo field or price cache file is never enough.

If independent evidence later contradicts the proposed shared cutoff, the **new comparison** is blocked as `BLOCKED_CONTROL_CLOCK_MISMATCH`; do not retroactively alter, refit or condemn frozen Phase III/MM1 based on this synthetic probe. The candidate C0/S/B/T/O study, labels at 60 calendar days + five-day tolerance, and real-data confirmations remain gated.
