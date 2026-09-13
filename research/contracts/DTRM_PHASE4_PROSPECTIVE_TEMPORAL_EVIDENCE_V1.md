# Phase IV Prospective Temporal Evidence v1

Date: 2026-09-13. Status: REGISTERED_BEFORE_REPEATED_CAPTURE.
Parent integration: `281ab0ce2de40128f2d2c8258cfff94fc91d8695`.
First live-probe backend commit: `79e8d3da1a337141f9097f0b79d45d2de78878c0`.
First live run: `34777031881`.
First artifact digest: `sha256:661d8b9b701af85655a14ad49f54dd9c48634ff83411fe0cd8ed94f50b8644b5`.

## Purpose

This registration defines the first repeated prospective evidence interval for Phase IV. It asks whether a bounded FMP news observation window behaves consistently enough over time to support a later outcome-blind event-history representation.

This increment is source characterization only. Confirmatory history construction, Temporal State fitting, protected outcomes, MM1 execution/evaluation and Phase-III mutation remain blocked. Provider-rights status remains `DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT`; raw provider material is not publicly redistributed.

The first live run established only short-window feasibility: nine registered observations succeeded, each requested page returned 20 items, repeated page zero was stable within the run, and page-zero/page-one fingerprints did not overlap. Those observations do not alter the fixed design below.

## Fixed interval

After separate human activation approval:

- roles remain exactly `fmp_articles`, `general_latest`, `stock_latest`;
- each run remains exactly `page0_a`, `page1`, `page0_b`, each with `limit=20`;
- nominal UTC slots are `00:15`, `06:15`, `12:15`, `18:15`;
- slot 1 is the first scheduled opportunity strictly after activation;
- the primary interval is exactly 56 scheduled opportunities (14 days x 4);
- the first live run above is a pre-window predecessor only and does not reduce the 56-slot target;
- failed scheduled opportunities remain missing; there is no ad-hoc backfill or replacement;
- collection cannot stop early because observations appear favorable or unfavorable.

The interval is `ADEQUATE_FOR_TEMPORAL_SOURCE_AUDIT` only after slot 56 and only if at least 48 slots were accepted, the first and last UTC days each contain an accepted slot, every accepted slot uses the registered request plan/fingerprint and exact code lineage, and no accepted slot accesses outcomes or MM1. Otherwise it is `INCOMPLETE_PROSPECTIVE_INTERVAL`; thresholds are not relaxed.

## Identity and version evidence

No explicit provider event identifier was present in the first live evidence. The whole interval therefore freezes the existing conservative fallback:

- take `link` for `fmp_articles` and `url` for the two latest-news roles;
- remove URL fragment only;
- do not normalize host, path, case, slash, query or encoding;
- `source_event_id = sha256(exact_fragment_stripped_url_utf8)`;
- `identity_method = exact_url_sha256`.

For every item, derive:

- `payload_sha256`: canonical full-item JSON SHA-256 (sorted keys, compact separators, UTF-8, no NaN);
- `content_sha256`: exact UTF-8 `content` (`fmp_articles`) or `text` (latest-news roles), no trimming;
- `title_sha256`: exact UTF-8 title, no trimming.

Source values remain in the restricted evidence artifact. Repository-tracked reports expose only digests, counts, fixed role names, clocks, ranks and aggregate diagnostics.

## Snapshot definition

One accepted run creates one ordered snapshot per role from `page0_a` followed by `page1`, maximum 40 positions. `page0_b` is a same-run stability check and is not appended. Duplicate logical identities inside a role snapshot fail closed.

A restricted snapshot index records per position: logical identity, the three digests, exact provider publication string, observation clocks, page and rank. Provider publication strings are not authenticated availability clocks; they may be used only for within-role ordering diagnostics when comparable.

## Transition taxonomy

For consecutive accepted snapshots of one role:

- `retained`: present in both;
- `new_to_ledger`: present now and never seen earlier in that role ledger;
- `reappeared`: present now, absent immediately before, but seen earlier;
- `window_absent`: present before and absent now;
- `payload_revision_candidate`: retained identity with changed payload digest;
- `narrative_revision_candidate`: retained identity with changed content digest;
- `metadata_revision_candidate`: payload changed while content did not;
- `title_revision_candidate`: retained identity with changed title digest;
- `rank_changed`: retained identity changed rank.

`window_absent` is never called deletion because the observed feed is a bounded top-40 window.

For retained identities compute rank deltas and deterministic pairwise inversion rate. A `publication_backfill_candidate` is a `new_to_ledger` item whose comparable provider publication string is strictly earlier than the oldest comparable string in the immediately previous snapshot. This is only a late-arrival diagnostic. Adjacent increases in comparable publication strings are `publication_order_violation`; unknown/non-comparable strings are counted separately and not imputed.

## Final longitudinal report

After slot 56 report separately by role: accepted/missing slots; observed positions; unique identities; new/reappeared/window-absent counts; payload/narrative/metadata/title revision counts; publication-backfill candidates; publication-order violations; retained-count, absolute-rank-delta and inversion-rate summaries; same-run page-zero stability failures; page-zero/page-one overlap; first/last accepted observation clocks; and exact run/artifact lineage.

There is no minimum revision, backfill, reorder or novelty rate required for scientific success. Zero revisions is valid evidence. The purpose is characterization, not manufacturing a temporal effect. Roles remain separate and cannot be collapsed into one homogeneous provider clock.

## Activation boundary

Before periodic collection can be activated, implementation must provide a deterministic synthetic snapshot/transition classifier, a backend derived-index builder for the existing raw artifact shape, append-only slot lineage, exact scheduled-workflow configuration, fail-closed malformed/duplicate handling, green quality/security/regression gates, repository-specific human merge approval, and a separate human activation approval.

Merging implementation does not activate periodic capture.
