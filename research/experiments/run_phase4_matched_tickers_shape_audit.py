"""Operator-only read-only structural metadata census. NEVER run in CI against production."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import NoReturn

from dtrm.phase4.matched_tickers_shape_io import (
    ShapeAuditIOError,
    operator_local_shape_audit,
)


class RedactedParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        del message
        raise ShapeAuditIOError("INVALID_ARGUMENTS")


def publish_exclusively(output: Path, data: bytes) -> None:
    """Stage and fsync aggregate bytes, then publish by no-clobber hardlink."""
    staged: str | None = None
    fd: int | None = None
    published = False
    try:
        fd, staged = tempfile.mkstemp(prefix=".phase4-shape-", dir=output.parent)
        with os.fdopen(fd, "wb") as stream:
            fd = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staged, output)
        published = True
    finally:
        if fd is not None:
            os.close(fd)
        if staged is not None:
            try:
                os.unlink(staged)
            except OSError:
                if not published:
                    raise


def _emit(payload: dict[str, object]) -> None:
    """Console notification never overrides authoritative on-disk evidence."""
    try:
        print(json.dumps(payload, sort_keys=True))
    except (OSError, ValueError):
        pass


def main(argv: list[str] | None = None) -> int:
    try:
        parser = RedactedParser(description=__doc__, allow_abbrev=False)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--env-file", type=Path)
        args = parser.parse_args(argv)
        if args.output.is_symlink() or args.output.exists():
            raise ShapeAuditIOError("OUTPUT_EXISTS")
        if not args.output.parent.is_dir():
            raise ShapeAuditIOError("OUTPUT_PARENT_MISSING")
        assessment = operator_local_shape_audit(args.env_file)
        content = (json.dumps(
            assessment.to_json(), sort_keys=True, indent=2, ensure_ascii=True,
        ) + "\n").encode("ascii")
        publish_exclusively(args.output, content)
        _emit({
            "graph": "phase4_matched_tickers_shape_audit_v0",
            "status": "succeeded",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "documents": assessment.documents,
            "elements": assessment.elements_count,
            "aggregate_sha256": assessment.sha256,
        })
        return 0
    except ShapeAuditIOError as exc:
        reason = str(exc)
        known = {
            "INVALID_ARGUMENTS", "OUTPUT_EXISTS", "OUTPUT_PARENT_MISSING",
            "SOURCE_CONFIGURATION_BLOCKED", "LIVE_SOURCE_FORBIDDEN_IN_CI",
            "DRIVER_IMPORT_FAILED", "SOURCE_COUNT_OUT_OF_BOUNDS",
            "INVALID_AGGREGATE_SHAPE", "INVALID_AGGREGATE_CARDINALITY",
            "READ_ONLY_AGGREGATE_FAILED", "MONGO_READ_FAILED",
        }
        error = reason if reason in known else "SHAPE_AUDIT_FAILED"
    except KeyboardInterrupt:
        error = "AUDIT_INTERRUPTED"
    except Exception:
        error = "SHAPE_AUDIT_FAILED"
    _emit({
        "graph": "phase4_matched_tickers_shape_audit_v0",
        "status": "failed",
        "error_code": error,
    })
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
