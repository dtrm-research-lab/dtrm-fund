# Phase IV retrospective salvage audit v0

Date: 2026-09-08. Status: REGISTERED_BEFORE_IMPLEMENTATION_OR_NEW_QUERY.
Parent integration: `1912cc9685ad7cfaa584c031dd330a46cdac053c`.

## Purpose and non-negotiable boundary

This is the final outcome-blind attempt to determine whether a limited portion
of the existing news collection can support a conservative retrospective
availability proxy. It does not test whether temporal representation works.
It must not optimize sample coverage, model performance or MM1 decisions.

The candidate proxy is the generation instant embedded in a Mongo `ObjectId`.
The audit asks whether that instant is supportable, in this specific collection
and writer lineage, as evidence close to document insertion. `ObjectId` is not
declared an observation clock by registration. It remains inadmissible unless
the registered evidence gates support it, and any later use requires a distinct
decision-clock binding with a conservative safety margin.

Phase III/MM1 and the original Phase-IV contract remain byte-identical. The
audit cannot construct histories, create candidates, fit representations,
access outcomes/prices/targets/scores, run MM1, or promote a dataset. PRAGMA is
architectural inspiration only.

The user alone executes any live database command. Agent and CI environments
must not inspect secret/environment presence or contents, load a production
dotenv, connect to the source, or seek alternate credentials. Synthetic CI may
write only to its disposable localhost Mongo service. A live output shared for
review contains aggregates only.

## Prior evidence fixed before this audit

The registered live feasibility report is fixed by SHA-256
`0c0c633cd7eb9fef439788db894795f02edcfb10a844eb3f192a1c4b5d7d2995`.
Its 1,000 ascending-`_id` sample establishes only that every sampled `_id` was
an ObjectId; `date` was a naive string; and the registered observation,
revision, digest and mapping/link-availability fields were absent. The sample
was nonrepresentative and did not inspect ObjectId timestamps or individual
source values.

The pinned static collector evidence is
`tech-com-UA00001/theresistance-back@7a8107e4451891535366acaf766348785ccc157b`,
collector blob `700e831db5c1d196a8e7c2c1dc6d10148237e710`.
It shows insert-only intent, no explicit persisted observation clock, a broad
unkeyed fallback after insert failure, atomic construction of text and ticker
matches within one document, and no overlap when advancing beyond the maximum
stored event date. Static evidence does not authenticate deployed versions,
exclusive writers, successful runs, server state or absence of manual changes.

These facts and limitations cannot be revised in response to the new audit.

## Fixed live read scope

Source is exactly `trumpMinMax.trumpNews`. First obtain an exact document count
with an empty filter. If it exceeds 250,000, stop with
`SOURCE_EXCEEDS_REGISTERED_BOUND`; do not emit a partial scientific report.
Otherwise stream a complete `_id`-ascending census with a fixed projection:

`_id`, `date`, `text`, `source`, `matched_tickers`, `dedupe_key`, `raw.id`,
`raw.articleId`, `raw.article_id`, `raw.url`, `raw.link`, `raw.newsUrl`,
`raw.publishedDate`, `raw.date`.

No other field is read. In particular, no return, target, label, price, beta,
model score, rank, calibration, guardrail or decision artifact is permitted.
Raw text, URLs, identifiers, tickers, ObjectIds, exact timestamps and per-row
digests may transit process memory only. They must never appear in stdout,
errors, logs or the output report.

Production access is read-only: no create/drop collection, write, update,
replace, delete, index mutation, aggregation output stage or server-side
function. Use majority-preferred read concern only if already supported without
changing the source; otherwise record the actual read concern and keep
`snapshot_atomic=false`. Count and cursor reads are not silently called atomic.
The implementation must set a 180-second client operation bound, 10-second
server-selection bound, 30-second socket bound, `retryReads=false`, batch size
500 and close the cursor/client on every path. It may load only an explicitly
named dotenv with `override=false`; fixed redacted error codes only.

Record audit start/end instants as audit metadata, never source availability.

## Exact derivations and aggregate-only output

All local transformations are deterministic and versioned. Unicode text is
hashed as its exact stored UTF-8 string with SHA-256; no semantic normalization.
A content digest is used only for aggregate equality and is never emitted.

For URL identity choose the first nonempty trimmed string in this fixed order:
`raw.url`, `raw.link`, `raw.newsUrl`. Remove an exact URI fragment beginning
with `#`; do not rewrite scheme, host, query, case or trailing slash. Hash the
result immediately and never persist or emit it. If no URL exists, the record
is `unkeyed`; source IDs are counted separately and are not silently mixed with
URL identity.

Provider calendar day is diagnostic only. Choose the first string in this
order: `raw.publishedDate`, `raw.date`, `date`. Accept only a valid leading
`YYYY-MM-DD`; preserve which path supplied it. Do not interpret the remaining
time, assume a timezone or substitute the day for availability.

For a genuine BSON ObjectId derive its embedded UTC second `id_time`. It is
only a candidate generation time. Emit counts by UTC calendar month and these
calendar-day deltas `date(id_time) - provider_day`:

`le_minus_2`, `minus_1`, `zero`, `plus_1`, `plus_2_7`, `plus_8_30`,
`plus_31_365`, `gt_365`, `provider_day_unknown`.

Also count ObjectIds later than `audit_started_at + 5 minutes`; this is a fixed
clock-anomaly diagnostic, not an automatic correction. Never emit an exact
ObjectId timestamp or exact provider date.

The report contains only:

- total census count and exact type/missing counters for fixed projected paths;
- ObjectId validity, UTC month counts, future-anomaly count and fixed day-lag
  bins;
- provider-day origin/parse counters;
- text type/missing/empty counters and number of distinct in-memory content
  digests;
- URL keyed/unkeyed counts; distinct hashed URL groups; singleton/repeated URL
  groups; repeated groups with one versus multiple exact content digests; and
  bounded group-size bins `2`, `3_5`, `6_20`, `gt_20`;
- source-ID presence counters by registered path, never values;
- `matched_tickers` missing/non-array/empty/nonempty, malformed-element,
  duplicate-within-row and fixed length bins `1`, `2_5`, `6_20`, `gt_20`;
- dedupe-key missing/present, distinct hashed keys and repeated-key groups;
- current sanitized index counters already defined by source-feasibility v0;
- complete reconciliation totals, schema/pipeline/evidence hashes and all
  scientific blockers.

No top values, examples, min/max exact dates, row identities, source strings,
URLs, tickers, texts or digests are emitted. Unknowns remain explicit.

## Writer and runtime evidence boundary

Database aggregates cannot prove immutability. A separate immutable manifest
must bind every evidence item used to assess writer provenance:

1. Complete Git history, bounded to commits reachable from the already pinned
   backend commit, for paths/code references that write `trumpNews`; search for
   insert/update/replace/upsert/delete/bulk-write and explicit `_id` assignment.
2. The already pinned Agent API tree for any independent news writer.
3. Optional operator-supplied workflow/run evidence containing only repository,
   workflow name, run ID, head SHA, event, timestamps, conclusion and artifact
   digest/identity. No logs, secrets, source rows or model outputs.
4. An operator declaration, if supportable, listing other applications or
   humans with write authority during a stated interval. Absence of such a
   declaration is recorded as unknown, never inferred as exclusivity.

Commit time and workflow schedule are not document observation times. Runtime
evidence may delimit an interval in which a writer was deployed; it cannot
backdate a document or repair absent vintages.

## Precommitted decision states

The audit returns exactly one of these scientific assessments. Engineering
schema success is reported separately.

### `RETROSPECTIVE_PROXY_CONTRADICTED`

Required if any relevant evidenced writer mutates/replaces existing news rows,
assigns externally prepared ObjectIds without a bound generation event, or if
the collection evidence cannot distinguish inserted content/ticker state from
later mutation. The main Phase-IV confirmatory path must be prospective.

### `RETROSPECTIVE_PROXY_PARTIAL`

Required when insert-only and atomic document construction are supported and a
deterministic ObjectId-bearing subset exists, but deployed-version coverage,
exclusive-writer evidence, client-clock provenance, or immutable runtime state
remains materially unknown. This may justify a later preregistered exploratory
or development-only chronology. It does not justify confirmatory history under
the original “machine already knew” claim.

### `RETROSPECTIVE_PROXY_CANDIDATE`

Permitted only if all relevant writers and deployed intervals are bounded;
they generate no explicit `_id`, use insert-only operations for this collection,
construct exact text and `matched_tickers` before one acknowledged insertion,
and no evidence indicates later mutation or an unbounded client clock. The data
census must expose a deterministic structurally eligible subset and all anomaly
counts. This status supports only a later decision-clock/source binding.

Even `RETROSPECTIVE_PROXY_CANDIDATE` leaves
`decision_clock_authenticated=false`, `history_construction_permitted=false`,
`training_permitted=false`, `outcome_access_permitted=false` and
`scientific_status=BLOCKED_DECISION_CLOCK_BINDING`. A later addendum must bind
the eligible interval/subset, a conservative post-ObjectId safety margin,
same-time ties, content/URL revision collapse, ticker semantics, frozen-control
price/beta availability, history window, partitions and exposure ledger before
any history is constructed.

Backfills do not invalidate insertion time: an old article becomes eligible no
earlier than the supported insertion proxy plus the later fixed safety margin.
Publication day never moves availability earlier. Malformed/unknown rows are
counted and remain in the audit universe; any later eligibility exclusion must
be bound before outcomes and cannot change after seeing model performance.

No coverage percentage or convenient date window upgrades a decision state.
Sample size/power is evaluated later under a frozen, outcome-blind statistical
addendum. If evidence is insufficient, report partial/contradicted rather than
relaxing provenance requirements.

## Graph contract for later implementation

| Node | Input to immutable output | Invariants and failure | Side effects |
| --- | --- | --- | --- |
| fixed query builder | constants to count/projection specs | exact namespace, cap, sort and allowlist | none |
| census boundary | explicit local configuration to streamed projected rows | cap before stream; close resources; redacted failures | registered reads only |
| row normalizer | projected row to typed ephemeral observation | exact keys/types; no inference or correction | none |
| aggregate reducer | typed stream to frozen counters | deterministic, reconciling, bounded hashed grouping | none |
| writer manifest validator | exact evidence manifest to frozen findings | allowlisted repositories/commits/fields; no runtime claims from schedules | none |
| decision assessor | counters and findings to one fixed state | decision rules above; permission flags always false | none |
| report serializer | immutable assessment to canonical JSON | aggregate-only allowlist; identity hashes; credential/value rejection | none |
| CLI | synthetic fixture or explicit local live mode to new file | refuse overwrite/symlink; exclusive creation after validation | named read and one report create |

Domain state uses frozen dataclasses/tuples. I/O stays at boundaries. Failure
produces no accepted report. Reordering input rows cannot change output bytes.

## Required tests before review of an implementation

Unit tests must cover every lag boundary, invalid calendar days, naive/full
timestamps, ObjectId/non-ObjectId values, future clock anomalies, exact UTF-8
hashing, URL fragment removal and non-normalization, source-ID precedence,
content/URL version aggregates, ticker shape/duplicates, dedupe aggregation,
reconciliation, immutability, ordering and all three decision states.

Functional tests must cover cap-before-stream, bounded cursor consumption,
closure on every failure, missing configuration before driver import, explicit
dotenv/no override, redacted exceptions, no-overwrite/symlink defenses,
aggregate-only serialization and absence of forbidden source values. An
isolated CI Mongo service may test BSON ObjectId/date semantics and the exact
projection with synthetic rows only; it must reject production configuration.

Regression gates are scoped Ruff, strict mypy, complete inherited tests, all
prior synthetic reproductions and evidence validators, disposable package
build, preservation before/after, current-head CI and human review. The user
runs the eventual live command and shares only its sanitized JSON plus SHA-256.

## Current authorization

This commit registers the audit design only. It authorizes no implementation,
new live query or external writer change until reviewed as a preserved ancestor.
The next permitted operation is contract validation and human review. No
outcome-driven retuning.
