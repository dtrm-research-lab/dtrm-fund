# Temporal boundary acceptance matrix v0

Specification only; no cases below have been implemented or executed as new
tests. Parent: `research/contracts/DTRM_PHASE4_TEMPORAL_BOUNDARY_V0.md`.
All hypothetical instants and identities must be synthetic. No real source
access, secret/environment inspection or current production date is needed.

## Future unit and functional cases

| ID | Synthetic case | Required result |
| --- | --- | --- |
| TB01 | Version and link strictly before cutoff | BEFORE_CUTOFF; scientific and training gates remain blocked |
| TB02 | Early publication, version observed after cutoff | AFTER_CUTOFF; publication does not rescue it |
| TB03 | Early version, link first available after cutoff | AFTER_CUTOFF |
| TB04 | Late version, early link | AFTER_CUTOFF; use maximum of both clocks |
| TB05 | Either or both availability clocks absent | UNKNOWN_AVAILABILITY, including when publication/first-seen is known |
| TB06 | Derived availability equals cutoff exactly | AT_CUTOFF_UNRESOLVED; no guessed operation order |
| TB07 | One microsecond before/after cutoff | BEFORE_CUTOFF / AFTER_CUTOFF, without rounding |
| TB08 | Equivalent explicit offsets cross UTC calendar day | Identical normalized assessment and digest |
| TB09 | Naive, date-only, missing or malformed cutoff | Reject envelope before assessment |
| TB10 | Publication day-only or unknown, availability known | Preserve publication precision; assess declared availability only |
| TB11 | Root early, later revision observed after cutoff | Distinct diagnostics; no as-of selection and no independent candidates |
| TB12 | Unknown revision time between known revisions | Unknown stays unknown; existing backwards-chain rejection still applies |
| TB13 | Equal revision times with lexical IDs reversed | No inferred chronological tie resolution |
| TB14 | Multiple links with different availability | One diagnostic per link; no transfer of another ticker's time |
| TB15 | No asset links | NO_ASSET_LINK, not silent disappearance |
| TB16 | Duplicate identities/links, fork, cycle, missing predecessor | Existing ontology rejects before accepted review |
| TB17 | Unknown fields including labels or arbitrary metadata | Reject at every envelope/batch/event/link boundary |
| TB18 | Unaudited/approved role or forged permission fields | Reject; synthetic-only graph cannot promote inputs |
| TB19 | Permute event/link input order | Byte-identical canonical report and digest |
| TB20 | Modify any valid input, including a future observation | Digest binds complete normalized input, not passing subset |
| TB21 | Attempt mutation of returned state | Frozen state rejects mutation; no mutable nested members |
| TB22 | All rows pass, all fail, mixed and linkless batches | Counts reconcile; no history, cohort, K or policy output; blocks always false |
| TB23 | Complete CLI run on synthetic fixture | New deterministic report; expected bytes match; no network/environment access |
| TB24 | Existing file, symlink or invalid parent as output | Refuse without overwrite or successful report |
| TB25 | Invalid JSON/schema or I/O failure with sensitive sentinel | Fixed redacted error; no raw input/exception echo or successful report |

## Later firewall obligations, explicitly not covered by this verifier

| ID | Later separately registered test | Required safety property |
| --- | --- | --- |
| LF01 | Feature uses same-day close arriving after decision | Block feature/cohort readiness, not repair frozen control |
| LF02 | Beta or derived feature depends on later/corrected prices | Validate every dependency's approved vintage and availability |
| LF03 | Revised ticker link or historical universe backfill | Do not use a later mapping before its authenticated availability |
| LF04 | Unlabelled holdout passed to tokenizer or pretraining | Reject fitting access; absence of labels is not permission |
| LF05 | Overlapping forward label windows or shared histories | Apply registered purge/embargo and dependence rules, not random row splitting |
| LF06 | Empty history or missing provenance affects one arm | Apply preregistered common-cohort rule; never silently shrink K |
| LF07 | Outcome access before frozen actions/manifest | Reject evaluation transition |

The later rows remain obligations, not implemented controls. Passing TB01–TB25
would not close LF01–LF07 or authenticate production data.
