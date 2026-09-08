"""Audit fixed nested metadata, sample date-year classes and sanitized index counters."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dtrm.phase4.source_feasibility import (
    GRAPH,
    build_feasibility_report,
    exact,
    normalize_feasibility,
    sanitize_indexes,
)
from dtrm.phase4.source_feasibility_io import run_mongo_feasibility
from dtrm.phase4.source_metadata import MetadataError
from dtrm.phase4.source_metadata_io import MetadataIOError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--synthetic-input", type=Path)
    modes.add_argument("--mongo", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.env_file is not None and not args.mongo:
        parser.error("--env-file requires --mongo")
    try:
        if args.output.exists() or args.output.is_symlink():
            raise MetadataIOError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise MetadataIOError("OUTPUT_PARENT_MISSING")
        if args.mongo:
            started = datetime.now(timezone.utc).isoformat()
            counts, indexes = run_mongo_feasibility(args.env_file)
            report = build_feasibility_report(counts, indexes, "live_mongo")
            report.update(audit_started_at=started,
                          audit_completed_at=datetime.now(timezone.utc).isoformat())
        else:
            payload = exact(json.loads(args.synthetic_input.read_text(encoding="utf-8")),
                            {"aggregate", "indexes"})
            report = build_feasibility_report(normalize_feasibility(payload["aggregate"]),
                                              sanitize_indexes(payload["indexes"]), "synthetic")
        encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded)
    except MetadataIOError as exc:
        error = str(exc)
    except (MetadataError, ValueError):
        error = "INVALID_DIAGNOSTIC_INPUT"
    except OSError:
        error = "FILE_IO_FAILED"
    else:
        print(json.dumps({"graph": GRAPH, "status": "succeeded",
                          "scientific_status": "BLOCKED_SOURCE_AUDIT",
                          "sampled_documents": counts.sampled_documents if args.mongo
                          else report["sampled_documents"]}))
        return 0
    print(json.dumps({"graph": GRAPH, "status": "failed", "error_code": error}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
