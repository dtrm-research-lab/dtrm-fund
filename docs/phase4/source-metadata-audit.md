# Local source metadata inventory

This follows `research/contracts/DTRM_PHASE4_SOURCE_METADATA_AUDIT_V0.md`, registered at `c6bdb927f16aea1919b4c5c219c9c21dca544147`. It inventories up to 1,000 current records from `trumpMinMax.trumpNews` in ascending `_id` order. It returns only type counts for the 19 registered top-level metadata candidates. This sample is not representative or an event chronology.

## Local read

Use the existing Python 3.11 virtual environment from the repository root. Install only the optional transport dependencies; installing the project in editable mode can rewrite inherited tracked packaging metadata.

```bash
source .venv/bin/activate
export PYTHONPATH=src
export PYTHONDONTWRITEBYTECODE=1
python -m pip install -r research/configs/phase4_source_audit_requirements.txt
phase4_audit_dir=$(mktemp -d)
python research/experiments/run_phase4_source_metadata_audit.py \
  --mongo --env-file .env \
  --output "$phase4_audit_dir/source-metadata.json"
cat "$phase4_audit_dir/source-metadata.json"
```

The explicitly named dotenv file must be your existing source configuration; replace its path if it is elsewhere. If `MONGO_URI` or the inherited `db_password` is already exported in your environment, omit `--env-file`. Environment variables take precedence. Credentials and raw database exception messages are not printed. Share the resulting inventory JSON for review; connection configuration is not part of the evidence report.

The CLI refuses to overwrite an existing report before connecting. `MISSING_LOCAL_CREDENTIALS`, `ENV_FILE_NOT_FOUND`, `MISSING_PYMONGO`, `MONGO_READ_FAILED`, or `INVALID_AGGREGATE_RESPONSE` means this operation did not produce accepted evidence. Connection failures need local connection/access diagnosis; they are not a scientific finding about the source.

## Synthetic verification

This mode needs no database connection or transport dependency:

```bash
phase4_check_dir=$(mktemp -d)
python research/experiments/run_phase4_source_metadata_audit.py \
  --synthetic-input tests/fixtures/phase4_source_metadata_aggregate_v0.json \
  --output "$phase4_check_dir/source-metadata.json"
cmp "$phase4_check_dir/source-metadata.json" \
  research/reports/DTRM_PHASE4_SOURCE_METADATA_SYNTHETIC_V0.json
```

The Phase-IV workflow runs this comparison together with strict typing, lint, the full test suite, the original ontology comparison, source preservation, and a disposable wheel build. Adapter tests use an injected fake transport; only a successful local Mongo run exercises the actual server.

## Reading the evidence

- `missing` and `null` are distinct; both fail to supply a usable value.
- `date` and `string` describe storage types only. They do not authenticate publication/observation meaning, precision, or historical availability.
- `array` and `object` do not reveal nested contents. Missing top-level candidates do not exclude alternate or nested provenance metadata.
- `sampled_documents=0` is empty evidence, not readiness.
- `audit_started_at` and `audit_completed_at` are execution times, not news availability times.
- `pipeline_sha256` binds the fixed query; `counts_sha256` binds its normalized counters. Neither is a hash of the raw database snapshot.

Every successful report remains `BLOCKED_SOURCE_AUDIT`. Next inspect collector/writer provenance, archived versions and mappings, source coverage, and price-cache timestamp conventions. These observations must support a separately registered decision-clock binding before constructing histories or entering Stage 2.
