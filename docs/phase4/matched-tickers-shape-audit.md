# Phase IV — matched-tickers source shape audit (operator-only)

Status: **dormant, contract-only authorization for implementation**, not authorized for real Mongo execution or scientific promotion. Governing contract: `research/contracts/DTRM_PHASE4_MATCHED_TICKERS_SHAPE_AUDIT_V0.md`.

The previous frozen retrospective source audit counted 405,565 `matched_tickers` elements incompatible with the *string-only* metadata ontology. This diagnostic performs **one bounded, server-side, type-only aggregation**, never reads ticker values into the CLI, and does not recalculate that frozen audit. Its classification may be compared descriptively with the earlier result, but it cannot retroactively change the earlier evidence and is **not** evidence of first-seen, content vintage or mapping availability.

## Before any operator live execution

Requires **separate, explicit user authorization** after PR review/merge, rights check and confirmation that the existing local Mongo read credentials are available. No AWS, FMP, MM1, protected target, run activation or humanclause.com workflow is involved. Never run this against production in CI or in an agent session. Only the operator runs it locally using the read-only identity, and inspects the report **before sharing**.

Requirements: use the existing Phase-IV source audit Python environment; the same `research/configs/phase4_source_audit_requirements.txt` as the already-registered retrospective census. No new permissions should be added solely for this audit.

Once separately authorized, from repository root on the operator Mac:

```bash
python -m pip install -r research/configs/phase4_source_audit_requirements.txt
export PYTHONPATH=src
RUN_DIR="$(mktemp -d)"
PYTHONPATH=src python research/experiments/run_phase4_matched_tickers_shape_audit.py \
  --output "$RUN_DIR/phase4-matched-tickers-shape.json"

# Check the exact output locally without sharing credentials or source values:
shasum -a 256 "$RUN_DIR/phase4-matched-tickers-shape.json"
python -m json.tool "$RUN_DIR/phase4-matched-tickers-shape.json"
```

If the required local configuration is only in an explicitly named dotenv file, add `--env-file /actual/private/path.env`. It is never auto-discovered. Do not include URI, username, password or any token in command-line arguments or chat. Operator should never paste environment variables. Only schema-approved grouped BSON type labels, counts and corresponding output digest are shareable after manual inspection. The operator may choose to share just the report's SHA-256 and sanitized counts.

## Safe default / failure behavior

- Importing or testing the audit opens no connections or reads environment.
- Live CLI refuses existing outputs and symlinks before configuring Mongo. It writes canonical aggregate JSON to an exclusive temporary file, fsyncs and publishes without overwrite.
- The transport uses the inherited credential resolver with production access forbidden from GitHub Actions; reads fixed namespace `trumpMinMax.trumpNews` with requested majority read concern, count plus one bounded `$facet` query, 60s query cap and no disk spill.
- The query only returns grouped *types*; it does not return original record values, raw tickers or text. Its fixed allowlisted nested field candidates do **not** establish correct issuer mapping.
- The response remains `BLOCKED_SOURCE_AUDIT`; no clock, vintage, history, training, outcomes or MM1 permission can change because this audit succeeds.
- Counts are not an atomic snapshot and may fail on concurrent ingestion drift or if Mongo type shapes exceed the preregistered group cap. No retry/backfill/looser query is authorized by failure.
- Human inspection is mandatory before transferring any report. Type-only grouping can be safely discussed; never share secrets or original Mongo documents.

Scientific next step: use verified aggregate structural results to propose a **new, outcome-blind mapping ontology**, then separate evidence for **when** any such mappings became available. Source structure does not establish availability; retrospective ObjectId-generation time remains only a partial proxy. The prospective 14-day/56-slot transport campaign and AWS activation remain independently blocked.
