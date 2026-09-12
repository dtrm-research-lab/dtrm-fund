#!/usr/bin/env python3
"""Validate the Phase-IV evidence-first operational amendment v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dtrm.phase4.evidence_first_operational import (
    EvidenceFirstOperationalError,
    canonical_report_json,
)

DEFAULT_STATEMENT = Path(
    "research/contracts/DTRM_PHASE4_EVIDENCE_FIRST_OPERATIONAL_STATEMENT_V0.json"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--statement", type=Path, default=DEFAULT_STATEMENT)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("EVIDENCE_FIRST_OUTPUT_EXISTS")
    try:
        payload = json.loads(args.statement.read_text(encoding="utf-8"))
        report = canonical_report_json(payload)
    except (OSError, json.JSONDecodeError, EvidenceFirstOperationalError) as exc:
        raise SystemExit("EVIDENCE_FIRST_VALIDATION_FAILED") from exc
    args.output.write_text(report, encoding="utf-8")
    print("PASS_EVIDENCE_FIRST_OPERATIONAL_AMENDMENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
