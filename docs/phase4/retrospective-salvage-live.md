# Retrospective-salvage live adapter v0

Registration: `13625046e8b258f085fab59966a31937786a5eec`.
Contract integration: `d11b9cff62e656cb64664d126e48dca9381ffc7e` (PR #9).

This adapter implements the user-local read boundary only. It neither proves
historical availability nor permits history construction, training or MM1.
The pinned static writer findings still contain material unknowns; the accepted
assessment can only be PARTIAL or CONTRADICTED.

## Operator-only execution after implementation review and integration

Do not execute this command in an agent session or against production in CI.
The operator uses their existing local configuration, without sharing it.

```bash
python -m pip install -r research/configs/phase4_source_audit_requirements.txt
export PYTHONPATH=src
live_audit_dir=$(mktemp -d)
python research/experiments/run_phase4_retrospective_salvage_live.py \
  --output "$live_audit_dir/phase4-retrospective-salvage-live.json"
```

Only if needed, add `--env-file` with an explicitly named local regular file.
No dotenv is discovered automatically, and existing variables take precedence.
Do not pass credentials on the command line. No URI, username or password is
printed. The inherited namespace is fixed; URI configuration does not change
the collection queried.

The entrypoint reads the exact count, streams the fixed projection with the
250,001-row stop, reduces rows immediately and sanitizes the index catalog.
Majority concern is requested without automatic fallback. All reads remain
non-atomic. A resource or validation failure yields a fixed error code, not an
accepted partial report. Output bytes are prepared in a temporary aggregate-only
file and published by exclusive hard link, so failed writes do not publish a
truncated report or overwrite an existing target.

Share only the successful aggregate file and its SHA-256. Inspect the output
locally for unintended disclosure before sharing. A token scan is a secondary
check, not proof of privacy; schema validation is the primary boundary.

```bash
shasum -a 256 "$live_audit_dir/phase4-retrospective-salvage-live.json"
grep -Ein 'mongodb|password|passwd|credential|secret|token|username|mongo_uri' \
  "$live_audit_dir/phase4-retrospective-salvage-live.json"
```

The scan should print no matching lines (grep exit 1 is expected for no matches).
If the shell variable is lost, use the actual saved path; do not substitute a
root-relative guessed path or rerun the source census just to recover a hash.

## Test provenance

Unit tests inject synthetic environment mappings and fake clients. Real BSON
classification is exercised without a connection. Functional Mongo tests run
only with the dedicated CI flags against the exact literal localhost URI;
their reports set `production_source_accessed=false` and
`live_adapter.isolated_test=true`. Fixture writes belong only to test setup.

The four earlier synthetic reports, including the synthetic salvage CLI, remain
byte-identical. Live report hashes intentionally differ because BSON semantics,
majority read concern and execution metadata are explicitly bound.
