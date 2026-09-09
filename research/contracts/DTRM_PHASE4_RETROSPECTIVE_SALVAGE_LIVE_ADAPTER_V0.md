# Phase IV retrospective-salvage live adapter v0

Date: 2026-09-09. Status: REGISTERED_BEFORE_IMPLEMENTATION_OR_LIVE_EXECUTION.
Parent integration: `a8bf5353f4fa46ad59d66faa980a1004276f97a8`.

## Purpose and inherited scientific boundary

This addendum binds the local read-only adapter that may execute the already
registered retrospective-salvage audit against
`trumpMinMax.trumpNews`. It does not alter the audit estimand, projection,
derivations, decision lattice or permission rules in
`DTRM_PHASE4_RETROSPECTIVE_SALVAGE_AUDIT_V0.md`. That contract, the original
Phase-IV contract and frozen Phase III/MM1 remain unchanged.

This increment exists only to transport an exact live census through the
reviewed pure graph. It cannot construct event history, select a date window,
exclude inconvenient observations, access prices/outcomes/targets/scores,
fit a representation, execute MM1 or test the Phase-IV treatment hypothesis.
PRAGMA remains architectural inspiration only.

The user is the sole production operator. Agent and CI environments must not
inspect production environment-variable presence or contents, read a
production dotenv file, connect to the production source or seek alternative
credentials. CI may connect only to its explicit disposable localhost Mongo
service containing synthetic records.

## Fixed delivery graph

| Node | Input to output | Invariants | Permitted side effects |
| --- | --- | --- | --- |
| CLI preflight | explicit paths to validated request | separate live entrypoint; output parent exists; output absent and not a symlink | argument parsing and path metadata only |
| local configuration | optional explicit dotenv path to opaque URI | fixed keys and precedence; no value logging; resolve before driver import | optional no-override dotenv load; environment reads in the user's process only |
| driver boundary | opaque URI to bounded client/collection | exact namespace, fixed timeouts, retry reads disabled, majority read concern | open and close one Mongo client |
| exact counter | empty filter to preliminary integer | stop above registered cap; no partial report | one `count_documents` read |
| census cursor | fixed projection/sort to projected documents | cap-plus-one enforcement; stream one row at a time; always close | one `find` cursor read |
| row reducer | projected document to frozen counters | normalize and reduce before requesting the next row; no raw census retention | none |
| index boundary | current catalog to sanitized counters | at most 65 entries consumed; no names/options/values leave sanitizer | one `list_indexes` read |
| assessment | counts plus frozen writer findings to one state | existing lattice unchanged; candidate unreachable in this adapter v0 | none |
| live report | frozen live state to canonical JSON | aggregate-only allowlist; recomputed hashes; scientific permissions false | exclusive creation of one new report |

Failure before the last node produces no accepted report. Domain outputs remain
frozen typed state. Mongo/PyMongo, dotenv, filesystem and clock access remain
at explicit I/O boundaries.

## Exact entrypoint and configuration contract

Implementation must add a separate entrypoint:

```text
research/experiments/run_phase4_retrospective_salvage_live.py
  --output <new-json-path>
  [--env-file <explicit-regular-file>]
```

The synthetic entrypoint and its tracked output must remain byte-identical.
There is no URI, username, password or token command-line argument. The output
preflight occurs before configuration or driver access. `--env-file` is never
implicit: when supplied it must exist, be a regular non-symlink file and be
loaded with `python-dotenv` using `override=false`. No parent-directory search,
default `.env` discovery or repository scan is allowed.

Only these ambient keys may configure the source:

1. `MONGO_URI`, used as one opaque complete URI when nonempty;
2. otherwise `db_password`, URL-escaped and inserted into the already used
   fixed source template for user `UrtziFM`, host
   `pcmoneytest.qvnkw.mongodb.net` and application `PCMoneyTest`.

If both exist, `MONGO_URI` has fixed precedence and `db_password` is not read.
No other environment key may supply source identity or credentials. Missing
configuration fails as `MISSING_LOCAL_CREDENTIALS` before PyMongo import.
Dotenv and driver import/load failures use fixed codes. Configuration values,
paths, driver exception text and connection details never appear in stdout,
stderr, logs, tracebacks or the report.

When `GITHUB_ACTIONS=true`, the configured entrypoint must fail closed as
`LIVE_SOURCE_FORBIDDEN_IN_CI` unless the explicit synthetic-Mongo opt-in is set
and the URI is the literal registered localhost test URI. CI must delete any
production-named variables before its test and must never load an env file.

## Fixed Mongo transport

The production namespace is exactly `trumpMinMax.trumpNews`. The adapter must
request collection read concern `majority`; it does not silently downgrade or
retry with a weaker concern. A successful operation records that majority was
requested and the read completed, not that count and cursor formed an atomic
snapshot. `reads_atomic` and `snapshot_verified` remain false.

The client settings are fixed:

- `timeoutMS=180000`;
- `serverSelectionTimeoutMS=10000`;
- `socketTimeoutMS=30000`;
- `retryReads=false`.

The exact preliminary operation is `count_documents({})`, bounded by the
registered client operation timeout. A non-integer/negative count, malformed
response or count above 250,000 fails without a report. No estimated count is
allowed.

The census operation is one `find` with empty filter, ascending `_id` sort,
batch size 500, cursor limit 250,001 and this inclusion projection only:

`_id`, `date`, `text`, `source`, `matched_tickers`, `dedupe_key`, `raw.id`,
`raw.articleId`, `raw.article_id`, `raw.url`, `raw.link`, `raw.newsUrl`,
`raw.publishedDate`, `raw.date`.

The implementation must build that projection from the already frozen
`PROJECTED_PATHS`; it must not maintain a divergent copy. A 250,001st observed
row fails as `SOURCE_EXCEEDS_REGISTERED_BOUND`, irrespective of the preliminary
count. Each row is normalized and reduced before the cursor advances. The
adapter must never materialize raw documents, normalized rows or per-row
digests as a complete census. Only aggregate counters, distinct hashes and
hashed group summaries required by the registered reducer may persist in
memory.

After cursor exhaustion, one `list_indexes` cursor may be consumed through the
existing sanitizer, with the existing 65-entry cap. Index catalog overflow or
invalid metadata fails without a report. Count, row and index cursors plus the
client close on success and on every failure. Close failures are redacted and
fail closed.

No adapter code path may call insert, update, replace, delete, bulk write,
create/drop collection, create/drop index, rename, transaction write,
`$out`, `$merge`, server-side JavaScript or an unrestricted aggregation.
Read preference, authentication and TLS are supplied by the opaque URI/driver;
the adapter does not weaken them.

## Frozen writer/runtime findings for adapter v0

The live CLI accepts no writer manifest or scientific-state override. Adapter
v0 binds the already reviewed static evidence to these exact findings:

| Field | Fixed value |
| --- | --- |
| mode | `registered_static_evidence_v0` |
| relevant_writers | `unknown` |
| deployed_intervals | `unknown` |
| id_assignment | `mongo_default` |
| write_operations | `insert_only` |
| atomic_text_tickers | `supported` |
| later_mutation | `unknown` |
| client_clock | `unknown` |
| runtime_immutability | `unknown` |
| write_authority | `unknown` |

`mongo_default`, `insert_only` and `supported` describe only the pinned visible
collector path. The unknown fields preserve the absence of authenticated
deployment/exclusive-writer/runtime evidence. No operator declaration, current
database shape, coverage percentage, convenient interval or CLI parameter may
upgrade them.

Consequently, adapter v0 cannot emit `RETROSPECTIVE_PROXY_CANDIDATE`:

- a nonempty deterministic ObjectId-bearing census with no contradiction from
  the fixed manifest returns `RETROSPECTIVE_PROXY_PARTIAL`;
- an empty/no-genuine-ObjectId census or another existing contradiction returns
  `RETROSPECTIVE_PROXY_CONTRADICTED`;
- any attempted candidate result is an implementation error and no report is
  accepted.

A future candidate assessment would require a separate preregistered,
repository-bound runtime/writer evidence increment. It cannot amend this live
result after seeing downstream performance.

## Live report schema and scientific interpretation

The accepted output is the existing aggregate-only retrospective-salvage
schema, constructed from immutable typed state and serialized canonically. It
may differ from the synthetic report only in registered live metadata,
aggregate counts, sanitized index counters, fixed writer mode/findings and their
derived hashes. Specifically:

- `execution_mode=live_mongo`;
- `engineering_status=PASS_LIVE_AUDIT_SCHEMA`;
- `assessment_semantics=live_source_aggregate_audit_not_decision_clock_evidence`;
- `production_source_accessed=true` only after the complete accepted read;
- audit start/end are UTC instants of this execution, not source availability;
- requested read concern is reported categorically, with
  `reads_atomic=false` and the count/cursor delta retained;
- the pipeline, fixed writer manifest and aggregate evidence hashes are
  recomputed during serialization.

No raw or exact text, URL, identifier, ticker, ObjectId, provider date,
timestamp, per-row digest, index name, URI, username, credential, environment
value or source exception is permitted in the output. The serializer must
reject mutable mappings and schema expansion just as the reviewed synthetic
implementation does.

For every accepted state:

- `decision_clock_authenticated=false`;
- `snapshot_verified=false`;
- `writer_runtime_evidence_authenticated=false`;
- `live_bson_semantics_validated=true` means only that real BSON types passed
  the tested normalizer; it is not a decision-clock promotion;
- `history_construction_permitted=false`;
- `training_permitted=false`;
- `outcome_access_permitted=false`;
- `model_fitting_performed=false`.

`RETROSPECTIVE_PROXY_PARTIAL` remains `BLOCKED_SOURCE_AUDIT` and supports only
the already declared exploratory/prospective fork. No representation baseline
or Transformer may start from it. `CONTRADICTED` selects the prospective path.

## Required implementation tests and gates

Before implementation review, tests must establish:

1. missing configuration fails before PyMongo import;
2. explicit dotenv loading is no-override, regular-file-only and never
   automatic;
3. URI precedence and fallback escaping without printing either value;
4. CI rejects every nonliteral-localhost source and env-file use;
5. exact namespace, majority read concern, timeouts and `retryReads=false`;
6. exact count/filter/projection/sort/limit/batch settings;
7. preliminary-cap and cap-plus-one rejection with bounded consumption;
8. normalize-and-reduce-before-next behavior and absence of census retention;
9. real BSON ObjectId generation-time semantics, non-ObjectId handling,
   projection exclusion and equality with the pure graph on disposable Mongo;
10. index sanitization/cap, close-on-success and close-on-every-failure;
11. structural absence of write operations and unchanged disposable source;
12. fixed redacted errors for count, cursor, index, concern, driver and close
    failures;
13. no-overwrite, symlink, missing-parent and exclusive-create behavior;
14. immutable live report, full nested validation, recomputed hashes and
    forbidden-value rejection;
15. candidate state rejection and all scientific permissions remaining false;
16. synthetic entrypoint/report byte preservation.

Functional Mongo tests use Mongo 7.0.14 on literal
`mongodb://127.0.0.1:27017/?directConnection=true`, gated by both
`PHASE4_SYNTHETIC_MONGO=1` and `GITHUB_ACTIONS=true`. Fixture creation and
cleanup belong only to test setup/teardown, never the adapter.

Regression gates are: scoped Ruff, strict mypy, all unit/functional/inherited
tests, all prior synthetic reproductions and evidence validators, disposable
wheel build, source preservation before/after, current-head GitHub CI and human
review. The implementation commit must descend from the reviewed registration
commit; it must embed that commit SHA and this file's SHA-256.

After a reviewed implementation is integrated, the user may run exactly one
live census and share only the canonical JSON file plus its SHA-256 and a
case-insensitive forbidden-token scan with no matches. The agent does not run
or request access to the user's secrets.

## Current authorization

This increment registers the live-adapter boundary only. It authorizes contract
validation and human review, but no adapter implementation, live Mongo query,
history construction, prospective collector mutation, outcome access, model
fit, Transformer, MM1 execution or scientific promotion. No outcome-driven
retuning.
