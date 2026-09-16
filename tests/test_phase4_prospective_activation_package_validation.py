from __future__ import annotations

import json
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reports/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_PACKAGE_VALIDATION_V1.json"

VALIDATED_HEAD = "eadbbb2b64eeb158c9b5f8bceb3ae44b385753de"
VALIDATED_TREE = "01b7d2742514e8bd14d954d9e40a860a52ede3e9"
STATEMENT_ID = "phase4-prospective-capture-2026-09-18-v1"
STATEMENT_SHA256 = "540a46f4b80e73cb776596936fd2d30fdf7d74d8a64d2c6ed2bd565deb8ed2b1"


def _load() -> dict[str, object]:
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def test_validation_binds_exact_implementation_and_ci_runs() -> None:
    report = _load()
    validated = cast(dict[str, object], report["validated_implementation"])
    assert validated == {"commit": VALIDATED_HEAD, "tree": VALIDATED_TREE}

    ci = cast(dict[str, object], report["ci_evidence"])
    assert ci == {
        "phase4_evidence_adequacy_v1_gates": {"conclusion": "success", "run_id": 35064689005},
        "phase4_gates": {"conclusion": "success", "run_id": 35064688990},
        "phase4_temporal_evidence_v1_gates": {"conclusion": "success", "run_id": 35064689050},
        "tests": {"conclusion": "success", "run_id": 35064689074},
    }


def test_validation_records_required_quality_gates() -> None:
    quality = cast(dict[str, object], _load()["quality_evidence"])
    assert quality["source_preservation_before"] == "PASS"
    assert quality["source_preservation_after"] == "PASS"
    assert quality["inherited_source_files"] == 157
    assert quality["ruff_scoped"] == "PASS"
    assert quality["mypy_strict"] == "PASS"
    assert quality["mypy_source_files"] == 41
    assert quality["pytest_passed"] == 1116
    assert quality["pytest_skipped"] == 6
    assert quality["synthetic_phase4_evidence_reproductions"] == "PASS"
    assert quality["collector_lineage_findings"] == 12
    assert quality["disposable_wheel_build"] == "PASS"
    assert quality["synthetic_mongo"] == "PASS"


def test_validation_does_not_grant_operational_or_scientific_activation() -> None:
    report = _load()
    package = cast(dict[str, object], report["activation_package"])
    assert package["activation_statement_id"] == STATEMENT_ID
    assert package["activation_statement_sha256"] == STATEMENT_SHA256
    assert package["prospective_start_utc"] == "2026-09-18T00:00:00Z"
    assert package["first_slot_utc"] == "2026-09-18T00:15:00Z"
    assert package["status"] == "PREPARED_NOT_PROVISIONED_NOT_ARMED"

    boundary = cast(dict[str, object], report["operational_boundary"])
    assert boundary["statement_prepared"] is True
    assert boundary["provider_rights_status"] == "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"
    for key in (
        "statement_provisioned",
        "arm_variable_set_to_true",
        "human_activation_authorized",
        "campaign_started",
        "operational_activation_effective",
        "provider_access_performed_by_this_validation",
    ):
        assert boundary[key] is False

    permissions = cast(dict[str, object], report["downstream_permissions"])
    assert all(value is False for value in permissions.values())
    assert report["validation_status"] == "PASS_PREPARED_ACTIVATION_PACKAGE_VALIDATION"
