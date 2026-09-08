# Bounded source feasibility audit

Contract: `research/contracts/DTRM_PHASE4_SOURCE_FEASIBILITY_V0.md`.
Registration: `bcee8fb45c8ca8f1f40ae3c48049ea67928d4c24`.

## What this validates

The audit reports type/presence at 17 fixed paths, date parse classes and UTC
year histograms for three date candidates, and four sanitized index counters.
Only the first 1000 records by ascending `_id` are sampled. This is not a census,
representative sample, sequence, immutable snapshot or approved decision clock.
Nested array paths retain Mongo dotted-path semantics, not per-element counts.
No document text, URL/identifier values, ticker values, index names or filter
values enter the report. No data/index write is implemented in the live adapter.

Missing/null remain distinct; numeric and ObjectId timestamps are never coerced.
An explicit timezone or successfully parsed date does not prove first observation.
An apparently suitable unique index does not prove historical enforcement.
Both reads can observe changing state; the report explicitly says not atomic.

## Configuration boundary

The live runner uses credentials already supplied to its process via `MONGO_URI`
or the inherited `db_password` convention. Alternatively pass an explicit dotenv
path; loading does not override environment variables. There is no implicit file
search and no credential display. Configuration on a user's Mac does not exist
automatically in the agent workspace or in GitHub Actions.

Do not paste credentials into chat, commit them, or include them in a report.
CI has no production configuration: its real-server tests use a fixed localhost
Mongo service and synthetic documents only. Setup writes are confined to that
disposable service; these tests never read an env file or a configured source URI.

## Reproduction

From the repository, with its isolated Python environment active:

```bash
export PYTHONPATH=src MYPYPATH=src PYTHONDONTWRITEBYTECODE=1
python -m pytest -q
python research/experiments/validate_phase4_source_preservation.py
audit_dir=$(mktemp -d)
python research/experiments/run_phase4_source_feasibility.py \
  --synthetic-input tests/fixtures/phase4_source_feasibility_v0.json \
  --output "$audit_dir/synthetic.json"
cmp "$audit_dir/synthetic.json" research/reports/DTRM_PHASE4_SOURCE_FEASIBILITY_SYNTHETIC_V0.json
```

Only when source configuration has been explicitly provided in the executing
environment, install `research/configs/phase4_source_audit_requirements.txt` and
run the live boundary with a new output path. For example, to use a repo-root
dotenv file already configured by the operator:

```bash
python research/experiments/run_phase4_source_feasibility.py \
  --mongo --env-file .env --output "$audit_dir/live.json"
```

Omit `--env-file` to use only process environment. The CLI refuses existing
outputs before connection. `MISSING_LOCAL_CREDENTIALS` means no source query was
made. Driver and protocol errors emit fixed codes and no successful report.
Any permission/network restriction remains a blocker, not a reason to broaden
credentials, namespaces, sample limits or source scope.

## Acceptance

Unit/functional tests, complete regressions, three synthetic evidence byte
comparisons, source preservation, lint, strict typing, wheel build and the
isolated real-Mongo CI job must pass before human integration review. Tests
skipped outside the dedicated Mongo CI job are not live-validation evidence.

Current source execution remains separately required. Even a successful live
report leaves `BLOCKED_SOURCE_AUDIT` and all training/history/outcome flags false.
A later approved addendum must establish clock semantics and baseline timing;
no day-level experiment or prospective collector change is approved here.
