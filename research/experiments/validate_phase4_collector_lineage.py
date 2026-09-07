"""Validate the pinned Phase-IV collector-lineage manifest and report."""

import argparse
import hashlib
import json
from pathlib import Path

from dtrm.phase4.collector_lineage import (
    AUDIT_ID,
    LineageEvidenceError,
    canonical_manifest_bytes,
    parse_collector_lineage_evidence,
    validate_report_binding,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT / "research/reports/DTRM_PHASE4_COLLECTOR_LINEAGE_EVIDENCE_V0.json"
)
DEFAULT_REPORT = ROOT / "research/reports/DTRM_PHASE4_COLLECTOR_LINEAGE_AUDIT_V0.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    try:
        manifest_bytes = args.manifest.read_bytes()
        payload = json.loads(manifest_bytes)
        audit = parse_collector_lineage_evidence(payload)
        if manifest_bytes != canonical_manifest_bytes(audit):
            raise LineageEvidenceError("manifest is not canonically serialized")
        report_bytes = args.report.read_bytes()
        report = report_bytes.decode("utf-8")
        validate_report_binding(audit, report)
    except (json.JSONDecodeError, LineageEvidenceError, OSError, UnicodeError) as exc:
        print(
            json.dumps(
                {
                    "audit_id": AUDIT_ID,
                    "status": "failed",
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "audit_id": AUDIT_ID,
                "engineering_status": "PASS_STATIC_EVIDENCE_BOUNDARY",
                "finding_count": len(audit.findings),
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
                "scientific_status": "BLOCKED_SOURCE_AUDIT",
                "status": "succeeded",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
