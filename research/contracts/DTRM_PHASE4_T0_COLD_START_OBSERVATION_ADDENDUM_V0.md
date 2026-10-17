# Phase IV — conservative T0 cold-start observation policy v0

**2026-10-16, preregistered before implementing the first live snapshot writer.** Synthetic/test-only contract extension to PR #48. No real source acquisition, AWS write or 56-slot activation. Prior Stage-0 science, timeline, IAM evidence, rights and outcome seals remain unchanged.

## Scientific motivation

The current Mongo archive is a present-time source with known string-typed `ticker` and `match_type` link attributes, but no authenticated historical first-link evidence. Retroactively admitting historical snapshots from Mongo publication dates is not permitted. We can nonetheless begin an honestly *prospective* historical record at a new observation epoch `T0`, even for records published long before T0, when an independently authorized recorder observes their exact source **version and link at T0**.

This converts historic-looking archive *content* into a new prospective observation at T0, **not** a reconstruction of what anyone knew on the publication date.

## T0 observation vs original writer clock

- `publisher_published_at`: independent descriptive metadata, never reconstructed clock.
- `original_source_created_at` / `original_link_created_at`: UNKNOWN unless genuinely independently available from source writer log/receipt; do not synthesize.
- `first_attested_version_observed_at`: *our* first independently attested prospective source/content snapshot observation, no earlier than actual capture receipt bracket.
- `first_attested_link_observed_at`: *our* first independent prospective observation of the particular link+mapping version as part of the same snapshot; **not** the moment the link was first created at the original backend.
- `ledger_committed_at`: post-capture storage/provider acknowledgement and independently frozen receipt; real eligibility must honor precise trusted watermark/ordering. Conservative policy requires both capture and commit complete before a decision can treat the snapshot as available; `max(first_attested_version_observed_at,first_attested_link_observed_at,ledger_committed_at)<decision_cutoff`. An exact cutoff tie fails.
- `T0` is itself an interval/verified provider receipt, not a user-chosen midnight or backdated nominal target slot. A one-time majority Mongo census with before/after counts is **not** a transactionally consistent frozen T0 snapshot; an instrumented, atomic/append-only capture and independently authenticated provider/writer receipt is needed first.

This policy may produce defensible **post-T0** available history for decisions after actual attestation, but it does **not** prove source feed completeness before T0, absence of other missing articles or enough authenticated lookback. The difference between original `linked_at` and conservatively attested `link_observed_at` is always explicitly retained in names, provenance and status. If a later true writer-clock record is found, append a new provenance version rather than silently replacing the original T0 admission; never use hindsight for previously frozen actions.

## Longitudinal feasibility and leakage

1. First independently governed immutable T0 snapshot fixes an explicit `coverage_started_at` lower bound, clock precision/error, mapping authority and frozen source-role coverage; events published before T0 are allowed only with post-T0 observed vintage and no implied prior historical availability.
2. Append new source/content revisions and matched-ticker changes with separate authentic link clocks at T1,T2,..., never overwrite T0. Store encrypted original payload or contractually permitted lossless evidence; SHA alone cannot reconstruct training input. Keep role-specific limits/truncation/failed requests.
3. Until a registered lookback L is fully covered from T0, `UNKNOWN_AVAILABILITY`/left truncation applies to candidates lacking complete histories; a reported zero from T0 is not a history-wide authenticated zero. Avoid post-outcome cohort filtering.
4. Future source coverage can be described empirically before model fitting, but eligibility classification requires frozen manifest/decision grid/splits and separate G5 approval. Capture transport process adequacy at 14 days and 56 slots never proves a complete lookback L.
5. The current MM1 live ranking, 60-day forward target with five-day price tolerance, calibration/interface, provider rights and protected outcomes remain untouched.

## Operational order (requires separate authorizations)

A. Review/redact this policy and implement synthetic receipt/clock and append-only tests; no live Mongo/AWS.
B. Prepare private T0 recorder, actual producer and storage attestation, retained payload policy and read-only source snapshot. Review with source rights/security/retention, then authorize each real operation explicitly.
C. After accepted noncounting EventBridge CloudTrail provenance, bind signed GitHub writer/run/receipt; launch future 56-slot v3 only by separate activation.
D. Freeze per-asset common manifest, historical lookback/splits and admissibility, then assess coverage; fit/evaluate only after full G5 and prospective outcomes.

**Current status:** `t0_source_snapshot_recorded=false`, `original_link_time_authenticated=false`, `historical_first_seen_authenticated=false`, `source_complete_lookback=false`, `temporal_state_training_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`.
