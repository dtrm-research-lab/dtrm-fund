# Phase IV event ontology v0

Date: 2026-09-07. Status: specified before schema implementation.
Parent: `DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md`.
Scope: news observation/version and its asset links; no model or dataset promotion.

## Scientific entities

An event in this first ontology means a **version of a news observation**, not a verified occurrence in the world. A single observation can concern several assets. The observation, its text version, and each asset link have distinct identities and availability evidence.

| Entity | Identity | Meaning |
| --- | --- | --- |
| Logical news observation | `(source, source_event_id)` | The same source record across revisions |
| Observed version | `(source, source_event_id, version_id)` | One immutable content vintage; bound by `content_sha256` |
| Asset link | Version identity plus canonical `ticker` | An association under a recorded `mapping_version` |
| Future model candidate | Inherited `(news_id, ticker)` plus an explicit vintage selection | Not constructed by this increment; several revisions must not become independent selections |

Tickers are identifiers under a mapping, not proof of permanent issuer identity. The mapping history and frozen universe still require source audit. The current event and earlier history will be separated in the later sequence contract.

## JSON boundary

The batch has exactly `schema_version`, `dataset_role`, and `events`. Its version is `dtrm.phase4.event_batch.v0`; role is `synthetic` or `unaudited`. Neither role qualifies a dataset for confirmation. Every observation contains exactly these fields; nullable values remain explicit:

| Field | Type and rule |
| --- | --- |
| `source` | `fmp_news`; no additional source family in v0 |
| `source_event_id`, `version_id` | Nonempty strings without surrounding whitespace |
| `content_sha256` | Lowercase hexadecimal SHA-256 of the exact archived text bytes; structural validation does not verify those bytes |
| `published_at` | ISO instant with timezone, ISO calendar date, or null, according to `publication_precision` |
| `publication_precision` | `instant`, `day`, or `unknown`; unknown requires null |
| `occurred_at` | Optional timezone-aware instant for an asserted real-world occurrence; never substitutes for availability |
| `first_seen_at` | Optional first observation time of the logical record, timezone-aware |
| `version_observed_at` | Optional observation time of this exact content version, timezone-aware |
| `supersedes_version_id` | Null for the original version; otherwise predecessor version in the same logical record |
| `asset_links` | List of exact objects: `ticker`, `mapping_version`, `linked_at` |

Tickers must already be canonical uppercase symbols; v0 does not silently normalize aliases. `linked_at` is nullable or a timezone-aware instant recording when this association was available. Empty asset-link lists are preserved as source observations rather than silently discarded.

Unknown fields are rejected at every structural object boundary. This excludes undeclared labels, forward returns, scores, credentials, and free-form metadata containers. Content is referenced by digest, not loaded or embedded here.

## Clock and revision semantics

- Preserve publication precision. A day-only date must never be converted into a known midnight timestamp. UTC normalization is permitted only for timezone-aware instants.
- If both logical `first_seen_at` and `version_observed_at` exist, the version cannot predate first observation. Known first-observation values must agree across versions.
- A linked version's derived availability is `max(version_observed_at, linked_at)` only when both are present. Otherwise it is unknown. The logical first-seen time must never backdate a later text revision or ticker association.
- This derived value is metadata, not verified eligibility. The graph cannot authenticate the timestamp evidence, bytes, source clock, or mapping.
- The batch includes complete revision chains for its logical records. Reject duplicate identities, missing predecessors, cycles, multiple roots, forks, and known version times that move backwards along a chain. Disconnected incremental extracts require reconciliation before this validator, not guessed parent links.
- Deterministic sorting is by scientific identity and link ticker. It makes serialization reproducible; it does not claim an intraday event order when timestamps are absent or tied.
- Later history selection must reconstruct the version available at the declared decision cutoff and must not treat each edit as independent evidence. That selection and its leakage tests belong to Stage 2.

## Graph contract

| Node | Input → output | Failure and side effects |
| --- | --- | --- |
| `normalize_observations` | Exact JSON batch → immutable typed batch | Schema/time/identity errors raise `OntologyError`; no I/O |
| `validate_revision_chains` | Typed observations → same validated batch | Broken or ambiguous lineage fails; no correction or I/O |
| `assess_metadata_completeness` | Valid batch → immutable review with counts, canonical digest and unknown-availability identities | Missing availability is reported, not imputed; no I/O |

The review is serializable and deterministic. It always reports `scientific_status=BLOCKED_SOURCE_AUDIT`, `training_permitted=false`, and `outcome_access_permitted=false`, even when every structural metadata field is present. It can only return `engineering_status=PASS_ONTOLOGY_SCHEMA` after all three nodes succeed.

The CLI is the sole file boundary: read one user-specified JSON batch, run the pure graph, and create one new review file without overwriting an existing file. No connector, secret, network, model artifact, frozen decision file, or outcome is accessed.

## Required acceptance cases before PR

Accept an explicit synthetic observation with complete metadata; preserve day precision and unknown availability; respect late version and link availability; normalize equivalent timezone-aware instants; retain observations without links; serialize identically after input-order changes. Reject extra target fields at each boundary, naive instants, malformed digests, duplicate links/versions, broken/cyclic/forked revisions, and chronologically inconsistent known observation times. Verify immutability, truthful blocked scientific status, CLI no-overwrite behavior, and preservation of every inherited tracked file.

## Source capability audit: inspected evidence only

The frozen V6 builder projects `_id`, `date`, `text`, and `matched_tickers`, then constructs `date_dt` from `str(raw_date)[:10]`. Its frozen candidate rows contain only `news_id`, `ticker`, and `date_dt`.

| Needed by temporal representation | Evidence in the inspected frozen projection |
| --- | --- |
| Source observation identity and asset matches | Present |
| Calendar event date | Present; source time is reduced to day granularity |
| First-seen / exact version observation time | Not projected |
| Revision identity and archived content vintage | No explicit per-version provenance in the projection |
| Asset-link availability and mapping version | Not projected |
| Point-in-time universe history | Frozen Phase-II universe is referenced; historical membership evidence remains to be audited |

This is a finding about the **inspected projection**, not proof that the database or vendor lacks additional information. Existing candidate files cannot themselves establish intraday order or exact historical availability. No Phase-III result is revised by this finding.

Source: `research/experiments/build_phase3_mm1_v6_exante_artifacts.py` at `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`; Git blob `0b4a2d61715ba6d3dc497118a98a5aa48e765f42`. No live MongoDB/FMP query or Phase-IV outcome access was made.

## Remaining Stage-1 exit conditions

Before claiming real-data readiness, inventory the actual source metadata and vintage evidence; bind the decision clock against baseline beta/price availability; bind the universe and mapping history; record coverage and previously consumed data; resolve history window and empty-history rules without outcomes. Then preregister and implement Stage 2. This schema increment alone does not close those gates.
