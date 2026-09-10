# Phase IV retrospective-salvage live interpretation v0

Date: 2026-09-10  
Status: `RETROSPECTIVE_PROXY_PARTIAL` / `BLOCKED_SOURCE_AUDIT`  
Canonical report SHA-256:
`e061be9a0dea615d87178903d87d997564befc9062341e0be0b096ba31d650cd`

## Decision

The live census succeeds as engineering evidence and rejects neither the
existence of a useful insertion chronology nor the prospective Phase-IV
research question. It does **not** authenticate the historical state that the
machine knew at a decision cutoff. The confirmatory temporal-state path cannot
advance to history construction, a representation baseline, a Transformer,
outcomes or MM1.

The precommitted lattice selects `RETROSPECTIVE_PROXY_PARTIAL`: all 63,873
documents carry genuine BSON ObjectIds and the pinned writer evidence supports
Mongo-default IDs, insert-only writes and atomic text/ticker construction, but
relevant-writer completeness, deployed intervals, later mutation, client
clock, runtime immutability and exclusive write authority remain unknown. The
adapter was deliberately unable to promote these unknowns from database
structure alone.

This is a source-feasibility result, not a result for the primary hypothesis.
No outcome, price, target, model score or Phase-III decision was accessed.

## Accepted observations

| Observation | Result | Scientific meaning |
| --- | ---: | --- |
| Current collection census | 63,873 | Complete within the registered cap; not an atomic historical snapshot |
| Count/cursor delta | 0 | No observed count drift during the 12.86-second read |
| Genuine BSON ObjectIds | 63,873 (100%) | A deterministic insertion-time-bearing universe exists structurally |
| Future ObjectId anomalies | 0 | No ObjectId time later than audit start |
| Provider-day parse | 63,873 (100%) | Calendar-day diagnostics are complete, but are not availability evidence |
| ObjectId/provider day equal | 34,173 (53.50%) | About half were inserted on the provider calendar day |
| Inserted 1–30 days later | 10,965 (17.17%) | Material delayed ingestion exists |
| Inserted 31–365 days later | 18,735 (29.33%) | Large retrospective backfill makes publication day unsafe as an observation clock |
| Nonempty text | 63,873 (100%) | Text is structurally available in the current rows |
| Distinct text digests | 62,527 | Exact current text is not one-to-one with rows |
| URL-keyed rows | 63,873 (100%) | URL grouping covers the census |
| Repeated URL groups | 160 | Repeated current URLs exist; one group has multiple content digests |
| Present dedupe keys | 34,035 (53.29%) | Current dedupe identity covers only part of the collection |
| Missing dedupe keys | 29,838 (46.71%) | Current index definitions cannot establish historical uniqueness for these rows |
| Nonempty ticker arrays | 63,873 (100%) | Every row has an outer association container |
| Malformed ticker elements | 405,565 | The v0 string-element ontology does not describe a large part of the actual nested representation |

The 405,565 value is an element count, not a row count; this audit intentionally
does not emit the raw elements or enough information to compute a malformed
row fraction. It therefore cannot support an exclusion rule or a claim that
every ticker association is invalid. It does establish that the current
string-array assumption is insufficient and must not be silently normalized.

## What the machine may have known

The ObjectId generation time is evidence of when Mongo generated an identifier,
not authenticated proof of when every relevant writer made the exact text and
ticker association available to the frozen decision process. If writer/runtime
provenance were later bounded, the ObjectId time could support a conservative
development-only availability proxy: old articles would enter no earlier than
their supported insertion time plus a preregistered safety margin. The provider
day must never move them earlier.

That condition is not met in v0. In particular, the current collection exposes
neither version-observation timestamps nor association timestamps, and a
present row cannot prove absence of later mutation. The headline conclusion is
therefore:

> The current database contains a substantial insertion chronology, but not an
> authenticated reconstruction of the machine's historical information set.

## Outcome-blind fork

The confirmatory answer to “does historical representation improve the frozen
robust policy?” must use a prospective immutable event collector. That is the
scientifically clean path and remains independent of model outcomes.

One optional retrospective branch remains permissible only as exploratory or
development evidence. Before it can construct even that chronology, a new
preregistration must bind:

1. an aggregate-only element-shape audit for `matched_tickers`, without values;
2. all relevant writers and their deployed intervals;
3. later-mutation/runtime-immutability and write-authority evidence;
4. ObjectId safety margin, same-time ties and revision collapse;
5. ticker association semantics and immutable event identity.

Failure to close those items routes the retrospective branch to
`CONTRADICTED`; it does not relax the confirmatory estimand. No representation
baseline or Transformer is authorized by this report.

## Evidence identity

The operator ran the integrated read-only adapter locally and reported
`NO_SENSITIVE_PATTERN`. The transferred terminal rendering was parsed and
reserialized with the registered canonical JSON settings; the resulting 10,553
bytes reproduce the operator SHA-256 exactly. Pipeline, writer-manifest and
aggregate-evidence hashes were recomputed successfully. The agent made no
production connection.
