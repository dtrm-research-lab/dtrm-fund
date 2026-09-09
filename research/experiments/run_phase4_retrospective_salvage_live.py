"""User-local registered audit. Do not execute against production in agent or CI sessions."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import NoReturn

from dtrm.phase4.retrospective_salvage import GRAPH
from dtrm.phase4.retrospective_salvage_io import SalvageIOError
from dtrm.phase4.salvage_live_io import run_live_audit
from dtrm.phase4.salvage_live_report import serialize_live_report


class RedactedParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        del message
        raise SalvageIOError("INVALID_ARGUMENTS")


def publish_report(output: Path, encoded: str) -> None:
    """Publish complete aggregate bytes exclusively; failed writes leave no report."""
    descriptor, temporary = tempfile.mkstemp(prefix=".salvage-aggregate-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)  # Atomic exclusive creation, never replaces a target.
    finally:
        os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = RedactedParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        if args.output.exists() or args.output.is_symlink():
            raise SalvageIOError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise SalvageIOError("OUTPUT_PARENT_MISSING")
        report = run_live_audit(args.env_file)
        encoded = serialize_live_report(report)
        publish_report(args.output, encoded)
        print(json.dumps({"graph": GRAPH, "status": "succeeded",
                          "scientific_status": "BLOCKED_SOURCE_AUDIT",
                          "scientific_assessment": report.to_dict()["scientific_assessment"],
                          "total_documents": report.counts.total_documents}, sort_keys=True))
        return 0
    except SalvageIOError as exc:
        # Only locally defined fixed codes may reach the public boundary.
        code = str(exc)
        allowed = {
            "INVALID_ARGUMENTS", "OUTPUT_EXISTS", "OUTPUT_PARENT_MISSING", "INVALID_ENV_FILE",
            "ENV_LOAD_FAILED", "MISSING_LOCAL_CREDENTIALS", "LIVE_SOURCE_FORBIDDEN_IN_CI",
            "DRIVER_IMPORT_FAILED", "RESOURCE_CLOSE_FAILED", "INVALID_SOURCE_COUNT",
            "SOURCE_EXCEEDS_REGISTERED_BOUND", "INDEX_CATALOG_EXCEEDS_BOUND",
            "CENSUS_READ_FAILED", "INVALID_LIVE_RESPONSE", "MONGO_READ_FAILED",
        }
        error = code if code in allowed else "LIVE_AUDIT_FAILED"
    except KeyboardInterrupt:
        error = "AUDIT_INTERRUPTED"
    except Exception:
        error = "LIVE_AUDIT_FAILED"
    print(json.dumps({"graph": GRAPH, "status": "failed", "error_code": error}, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
