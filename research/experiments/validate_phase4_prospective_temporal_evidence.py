"""Validate the registered Phase-IV prospective temporal evidence v1 contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import cast

from dtrm.phase4.prospective_temporal_evidence import (
    RoleSnapshot,
    SnapshotEntry,
    canonical_report_json,
)

STATEMENT_PATH = Path(
    "research/contracts/DTRM_PHASE4_PROSPECTIVE_TEMPORAL_EVIDENCE_STATEMENT_V1.json"
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _synthetic_transition_inputs() -> tuple[RoleSnapshot, RoleSnapshot, frozenset[str]]:
    previous = RoleSnapshot(
        role="general_latest",
        slot=0,
        entries=(
            SnapshotEntry(
                _sha("a"),
                _sha("payload-a-v1"),
                _sha("content-a-v1"),
                _sha("title-a-v1"),
                "2026-09-13 15:00:00",
            ),
            SnapshotEntry(
                _sha("b"),
                _sha("payload-b-v1"),
                _sha("content-b-v1"),
                _sha("title-b-v1"),
                "2026-09-13 14:00:00",
            ),
            SnapshotEntry(
                _sha("c"),
                _sha("payload-c-v1"),
                _sha("content-c-v1"),
                _sha("title-c-v1"),
                "2026-09-13 13:00:00",
            ),
        ),
    )
    current = RoleSnapshot(
        role="general_latest",
        slot=1,
        entries=(
            SnapshotEntry(
                _sha("d"),
                _sha("payload-d-v1"),
                _sha("content-d-v1"),
                _sha("title-d-v1"),
                "2026-09-13 12:00:00",
            ),
            SnapshotEntry(
                _sha("b"),
                _sha("payload-b-v2"),
                _sha("content-b-v1"),
                _sha("title-b-v2"),
                "2026-09-13 14:00:00",
            ),
            SnapshotEntry(
                _sha("a"),
                _sha("payload-a-v2"),
                _sha("content-a-v2"),
                _sha("title-a-v1"),
                "2026-09-13 15:00:00",
            ),
            SnapshotEntry(
                _sha("x"),
                _sha("payload-x-v1"),
                _sha("content-x-v1"),
                _sha("title-x-v1"),
                None,
            ),
        ),
    )
    historical_seen = frozenset({_sha("a"), _sha("b"), _sha("c"), _sha("x")})
    return previous, current, historical_seen


def _load_statement() -> object:
    value = cast(object, json.loads(STATEMENT_PATH.read_text(encoding="utf-8")))
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = cast(Path, args.output)
    if output.exists() or output.is_symlink():
        raise SystemExit("OUTPUT_ALREADY_EXISTS")

    previous, current, historical_seen = _synthetic_transition_inputs()
    report = canonical_report_json(
        _load_statement(), previous, current, historical_seen
    )
    output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
