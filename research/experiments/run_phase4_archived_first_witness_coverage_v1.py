"""Offline-only exact-source first-witness coverage reproduction.

Use against the user's private SHA-pinned 21 original ZIP archive backups.
Writes only an aggregate, no article, ticker, URL, text, score or outcome.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from dtrm.phase4.archived_first_witness_coverage import (
    ERROR,
    CoverageError,
    _reject,
    calculate_coverage,
    read_one_archive,
    verify_canonical_manifest,
    verify_original_coverage_targets,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    staged: str | None = None
    try:
        if (
            os.path.lexists(args.output)
            or args.manifest.is_symlink()
            or not args.manifest.is_file()
            or not args.archive_dir.is_dir()
        ):
            _reject()
        rows = verify_canonical_manifest(args.manifest.read_bytes())
        snapshots = [read_one_archive(args.archive_dir, row) for row in rows]
        report = calculate_coverage(snapshots)
        verify_original_coverage_targets(report)
        content = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
        # Stage, flush, fsync, then publish atomically without replacing an existing result.
        fd, staged = tempfile.mkstemp(
            dir=args.output.parent, prefix=f".{args.output.name}.", suffix=".tmp"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as target:
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        os.link(staged, args.output)
    except (CoverageError, OSError, ValueError, TypeError, RecursionError):
        try:
            print(ERROR, file=sys.stderr)
        except (OSError, ValueError):
            pass
        return 2
    finally:
        if staged is not None:
            try:
                os.unlink(staged)
            except OSError:
                pass
    # No print error may overturn an already completed atomic publication.
    try:
        print("PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED")
    except (OSError, ValueError):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
