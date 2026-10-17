# Phase IV — simple-history B synthetic mechanics v0

**2026-10-14 | CONTRACT REGISTERED BEFORE IMPLEMENTATION | SYNTHETIC_ONLY.**

Parent scientific integration `3c9c7a2443213c991bba4cb621b97d9a56b3dd6c` in `research/phase4-temporal-state`. Inherits Stage-0 original v0.1, #35 (history unknown != zero), #36 (cohort/partitions/lookback fixed before coverage), #37 (C0 frozen clock risk), #38 (shared decision-clock syntax and chronological admission). Phase III/MM1 production and 157 inherited files must remain bit-identical.

## Purpose and interpretation

The trial eventually requires C0 (frozen snapshot), S (refitted matched snapshot), **B (simple event-history summary)**, T (sequential Transformer) and O (time/order ablation) with the same frozen MM1 policy. A B scaffold must exist and be tested before T so added model complexity cannot be declared necessary without comparison to an inexpensive history baseline.

This increment **does not fit B, select a real history, create candidate cohorts, authenticate a provider observation clock, open outcomes, or authorize a policy run**. It tests only deterministic count/recency arithmetic on fictional, explicitly synthetic event records. No real source adapter and no learned weights.

## Input fixture contract

In-memory Python dict only: exact `schema_version=dtrm.phase4.simple_history_fixture.v0`, `dataset_role=synthetic`, `cases` list, 1–64.

Each case contains exact `case_tag` (`case_01`…`case_64`, unique), `decision_cutoff` (UTC or offset-aware full second-resolution ISO timestamp with optional <=6-digit fraction), `lookback_days` (explicit *integer* in [1,365], no default and **not** a registered final G5 lookback), and `events` (0–64).

Each invented event contains exact `event_tag` (`event_01`…`event_64`, unique per case), `source_role` exactly one of `fmp_articles`, `general_latest`, `stock_latest`, and `effective_available_at` (full explicit timezone-aware ISO instant). `effective_available_at` is the *synthetic* max of version/link/mapping availability that would only be justified by a later real provenance audit; this module never authenticates that claim.

No ticker, URL, event text, embedding, sentiment, price, score, portfolio, return, calibration, protected target, external digest, credentials or arbitrary real identifier. Reject extra keys and bool/float for lookback. Empty synthetic events are **not** evidence for authenticated historical zero.

## Pure graph and admissibility

1. Exact key/role/tag validation, UTC normalization, fail-closed on naïve/ambiguous `-00:00`, unsupported date-only/imprecise timestamps, timestamp normalization overflow. No file, network or environment I/O.
2. Every supplied event must have `effective_available_at < decision_cutoff`. An equal/future event fails the whole fixture instead of being silently dropped. Input already-eligible hypothetical histories still require an external source-authority gate in real research.
3. Define observation window **[cutoff - lookback_days calendar days, cutoff)** in UTC. Exclude events strictly earlier than window start. Events exactly at window start are included. The caller cannot select another L after inspecting counts without creating a new experiment.
4. De-duplicate by unique synthetic event_tag; incompatible duplicates fail. Count only one event per tag irrespective of role. Aggregate by the three fixed roles **separately**, never pooling source clocks for evidence-authentication purposes.
5. Derive per-case frozen state with `window_count`, three per-role integer counts, and `most_recent_age_seconds` (floor of positive time delta) or null for zero invented events. This is a mechanics proof, **not an accepted B feature specification**; no decay constants, embeddings, model training or parameter search.
6. Serialize a fresh canonical report containing sorted synthetic cases, aggregate counts and a SHA-256 of the fully normalized synthetic fixture, invariant under case/event permutation and equivalent UTC offsets. No direct input references in state or report.
7. Every synthetic PASS must hardcode `scientific_status=BLOCKED_SOURCE_AUDIT`, `source_authenticated=false`, `decision_clock_authenticated=false`, `zero_history_authenticated=false`, `g5_lookback_frozen=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`.

## Acceptance and boundaries

Tests must cover: exact window boundaries and UTC crossing; empty vs unknown source sufficiency; mixed fixed provider roles; duplicate tags; future/equal instant rejection; timezone and order invariance; invalid types, real-world-like tags, unwanted outcome fields and precision failures; frozen detached result and all false scientific gates. Strict mypy, scoped Ruff, full inherited tests, source preservation, reproducible build, review and separate human PR merge authorization remain required.

**Later steps, separately registered and authorized:** establish genuine incoming source-vintage/asset-link/price first-availability; freeze exact prospective cutoff/candidate/partition and independent `L` before coverage; establish C0 clock compatibility and provider rights; only then choose the final B feature recipe and matched S/T/O model budgets, with label maturity 60 calendar days plus inherited five-day tolerance. No synthetic B counts become a scientific result.
