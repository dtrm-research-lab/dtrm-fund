from __future__ import annotations

import json
from pathlib import Path

import pytest

from dtrm.phase4.inert_schedule_installation import (
    ARM_VALUE,
    ARM_VARIABLE,
    CRON,
    DORMANT_BACKEND_COMMIT,
    DORMANT_WORKFLOW_BLOB,
    InertScheduleInstallationError,
    expected_statement,
    verify_statement_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = ROOT / "research/contracts/DTRM_PHASE4_INERT_SCHEDULE_INSTALLATION_STATEMENT_V1.json"
EXPECTED_SHA256 = "9cd7f66c028ba6b61088c0639a8360fbac6e1e939ee33f72c877f6b2ea9e8df2"


def _bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")


def test_registered_statement_is_canonical_and_exact() -> None:
    verified = verify_statement_bytes(STATEMENT.read_bytes())
    assert verified.sha256 == EXPECTED_SHA256
    assert verified.canonical_json.encode("utf-8") == STATEMENT.read_bytes()


def test_schedule_installation_is_distinct_from_capture_activation() -> None:
    payload = expected_statement()
    workflow = payload["workflow"]
    guards = payload["pre_activation_guards"]
    assert isinstance(workflow, dict)
    assert isinstance(guards, dict)
    assert workflow["cron"] == list(CRON)
    assert workflow["schedule_installation_permitted"] is True
    assert workflow["schedule_default_armed"] is False
    assert workflow["arm_variable"] == ARM_VARIABLE
    assert workflow["arm_value"] == ARM_VALUE
    assert guards["periodic_capture_activation_permitted"] is False
    assert guards["scheduled_provider_access_permitted_when_unarmed"] is False
    assert guards["scheduled_private_write_permitted_when_unarmed"] is False
    assert guards["scheduled_side_effects_permitted_before_statement_verification"] is False
    assert guards["scheduled_artifact_upload_permitted_before_statement_verification"] is False
    assert guards["scheduled_failure_record_permitted_before_statement_verification"] is False
    assert guards["scheduled_counting_decision_permitted_before_statement_verification"] is False
    assert guards["preactivation_schedule_runs_counting_eligible"] is False
    assert guards["prospective_start_bound"] is False


def test_dormant_lineage_remains_frozen() -> None:
    payload = expected_statement()
    backend = payload["backend_lineage"]
    workflow = payload["workflow"]
    assert isinstance(backend, dict)
    assert isinstance(workflow, dict)
    assert backend["dormant_merge_commit"] == DORMANT_BACKEND_COMMIT
    assert workflow["dormant_blob_sha"] == DORMANT_WORKFLOW_BLOB


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("workflow", "schedule_default_armed", True),
        ("workflow", "arm_value", "TRUE"),
        ("pre_activation_guards", "periodic_capture_activation_permitted", True),
        ("pre_activation_guards", "scheduled_provider_access_permitted_when_unarmed", True),
        ("pre_activation_guards", "scheduled_private_write_permitted_when_unarmed", True),
        (
            "pre_activation_guards",
            "scheduled_side_effects_permitted_before_statement_verification",
            True,
        ),
        (
            "pre_activation_guards",
            "scheduled_artifact_upload_permitted_before_statement_verification",
            True,
        ),
        (
            "pre_activation_guards",
            "scheduled_failure_record_permitted_before_statement_verification",
            True,
        ),
        (
            "pre_activation_guards",
            "scheduled_counting_decision_permitted_before_statement_verification",
            True,
        ),
        ("pre_activation_guards", "preactivation_schedule_runs_counting_eligible", True),
        ("pre_activation_guards", "prospective_start_bound", True),
    ],
)
def test_preactivation_promotions_fail_closed(section: str, field: str, value: object) -> None:
    payload = expected_statement()
    nested = payload[section]
    assert isinstance(nested, dict)
    nested[field] = value
    with pytest.raises(InertScheduleInstallationError):
        verify_statement_bytes(_bytes(payload))


def test_cron_drift_fails_closed() -> None:
    payload = expected_statement()
    workflow = payload["workflow"]
    assert isinstance(workflow, dict)
    workflow["cron"] = ["0 0 * * *"]
    with pytest.raises(InertScheduleInstallationError):
        verify_statement_bytes(_bytes(payload))


def test_duplicate_keys_fail_closed() -> None:
    raw = STATEMENT.read_text()
    duplicated = raw.replace(
        '"schema_version": "dtrm.phase4.inert_schedule_installation.v1",',
        '"schema_version": "dtrm.phase4.inert_schedule_installation.v1",\n'
        '  "schema_version": "dtrm.phase4.inert_schedule_installation.v1",',
        1,
    )
    with pytest.raises(InertScheduleInstallationError, match="duplicate JSON keys"):
        verify_statement_bytes(duplicated.encode("utf-8"))


def test_secret_shaped_material_fails_closed() -> None:
    payload = expected_statement()
    workflow = payload["workflow"]
    assert isinstance(workflow, dict)
    workflow["arm_variable"] = "mongodb+srv://redacted.invalid"
    with pytest.raises(InertScheduleInstallationError, match="forbidden secret material"):
        verify_statement_bytes(_bytes(payload))
