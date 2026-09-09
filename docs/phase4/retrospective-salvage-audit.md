# Retrospective salvage audit: synthetic implementation

Contract:
`research/contracts/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_AUDIT_V0.md`.
The reviewed contract entered the Phase-IV branch at merge commit
`92006f523fd100719e93f837ce5c697ae9a65e83`.

## Scope of this increment

This increment implements and tests the deterministic graph without a
production connector. It accepts one allowlisted Extended-JSON fixture, passes
documents through an injectable census boundary, immediately reduces source
values to aggregates, assesses exactly one registered proxy state, and writes
one canonical aggregate-only JSON report.

The nodes are:

1. fixed query specification;
2. census boundary with preliminary-count and cap-plus-one enforcement;
3. projected-row normalization into immutable ephemeral state;
4. order-invariant aggregation;
5. categorical synthetic writer-manifest validation;
6. fixed decision lattice;
7. aggregate-only report serialization;
8. no-overwrite synthetic CLI.

An Extended-JSON object of the exact form `{"$oid": "<24 lowercase hex>"}`
simulates ObjectId generation-time semantics. It is never represented as live
BSON evidence. For this audit only, the structurally eligible count is the
number of those ObjectId-shaped rows. It is not a training-eligibility rule and
does not exclude malformed content, URL or ticker rows from the census.

All exact texts, URLs, identifiers, ticker values, ObjectIds and row-level
digests remain transient. The report contains only registered counters and
categorical writer findings. Publication days remain diagnostics and never
become availability times.

## Synthetic reproduction

From the repository environment:

```bash
export PYTHONPATH=src MYPYPATH=src PYTHONDONTWRITEBYTECODE=1
python research/experiments/run_phase4_retrospective_salvage.py \
  --synthetic-input tests/fixtures/phase4_retrospective_salvage_v0.json \
  --output /tmp/phase4-retrospective-salvage.json
cmp /tmp/phase4-retrospective-salvage.json \
  research/reports/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_SYNTHETIC_V0.json
```

The tracked fixture deliberately returns `RETROSPECTIVE_PROXY_PARTIAL` because
several writer/runtime categories are unknown. That is a synthetic decision
lattice exercise, not a conclusion about the source collection.

## Deliberately absent live boundary

There is no `--mongo` option, PyMongo import, environment lookup, dotenv loader
or production URI construction in this increment. Consequently it cannot read
the user's source or secrets, and it cannot produce a live scientific report.
The contract's live-configuration, real-BSON, majority-read and isolated-Mongo
tests remain pending a separate reviewed connector increment. They are not
claimed as passed here.

No result from this synthetic graph authenticates a decision clock, permits
history construction or training, accesses outcomes, or changes frozen
Phase III/MM1. A later live adapter and operator execution require a new bounded
delivery cycle while retaining this contract ancestry.
