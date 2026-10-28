"""Read-only synthetic G4.9a fixture replay; outputs mechanical results, not science outcomes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from g49a_mechanism import _canonical, run_suite, verify_report

BASE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = BASE / "g49a_synthetic_cases.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="G4.9a offline scripted mechanism smoke test")
    ap.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    if set(fixture) != {"schema_version", "disclosure", "cases"}:
        raise ValueError("Unexpected fixture envelope")
    if fixture["schema_version"] != "dtrm.ic.g4_9a.fixture.v1":
        raise ValueError("Wrong fixture schema")
    if fixture["disclosure"] != "SYNTHETIC_SCRIPTS_NOT_HUMAN_PARTICIPANTS":
        raise ValueError("Fixture must explicitly disclose synthetic scripted controllers")

    report = run_suite(fixture["cases"])
    verify_report(report, fixture["cases"])

    if report["common_hard_guard_breaches"] != 0:
        raise RuntimeError("Hard-guard violation: FAIL")
    if report["matched_policy_invariant_checks"] != report["case_count"] * 3:
        raise RuntimeError("Matched policy parity failure: FAIL")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("G49A_SYNTHETIC_SOFTWARE_MECHANISM_SMOKE_PASS")
    print(f"PROTOCOL_COMMIT={report['protocol_commit']}")
    print(f"FIXTURE_SHA256={report['case_sha256']}")
    print(f"REPORT_SHA256={report['report_sha256']}")
    print(f"SCENARIOS={report['case_count']} ROWS={report['row_count']}")
    print(f"MATCHED_POLICY_ASSERTIONS={report['matched_policy_invariant_checks']}")
    print(f"HARD_GUARD_BREACHES={report['common_hard_guard_breaches']}")
    for arm, counts in report["status_counts"].items():
        print(f"ARM={arm} COUNTS={_canonical(counts)} CHECKS={report['total_logical_checks'][arm]}")
    print("SCOPE=SYNTHETIC_SCRIPTED_CONTROLLERS_NO_ACTUAL_HUMANS_NO_REAL_RETURNS")
    print("NONINFERIORITY=NOT_TESTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
