"""Inventory registered metadata types, using synthetic counters or local Mongo access."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dtrm.phase4.source_metadata import (
    MetadataError,
    build_metadata_report,
    normalize_metadata_counts,
)
from dtrm.phase4.source_metadata_io import MetadataIOError, run_mongo_inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--synthetic-input", type=Path)
    mode.add_argument("--mongo", action="store_true")
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
            counts = run_mongo_inventory(args.env_file)
            report = build_metadata_report(counts, "live_mongo")
            report["audit_started_at"] = started
            report["audit_completed_at"] = datetime.now(timezone.utc).isoformat()
        else:
            raw = json.loads(args.synthetic_input.read_text(encoding="utf-8"))
            report = build_metadata_report(normalize_metadata_counts(raw), "synthetic")
        encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded)
    except MetadataIOError as exc:
        error = str(exc)
    except (MetadataError, ValueError):
        error = "INVALID_METADATA_INPUT"
    except OSError:
        error = "FILE_IO_FAILED"
    else:
        print(json.dumps({"graph": report["graph"], "status": "succeeded",
                          "scientific_status": report["scientific_status"],
                          "sampled_documents": report["sampled_documents"]}))
        return 0
    print(json.dumps({"graph": "phase4_source_metadata_inventory_v0",
                      "status": "failed", "error_code": error}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
