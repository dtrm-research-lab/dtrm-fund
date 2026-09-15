from __future__ import annotations

import json
from pathlib import Path

import pytest

from dtrm.phase4.scheduled_revision_addendum import (
    BACKEND_DORMANT_ANCESTOR,
    BACKEND_MERGE_COMMIT,
    BACKEND_MERGE_TREE,
    CRON,
    PROVIDER_ROLES,
    REQUEST_FINGERPRINT,
    TARGET_SLOT_MAX,
    TARGET_SLOT_MIN,
    VALIDATED_PR_HEAD,
    WORKFLOW_BLOB,
    WORKFLOW_IDENTITY,
    WORKFLOW_PATH,
    ScheduledRevisionAddendumError,
    expected_statement,
    verify_statement_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = (
    ROOT / "research/contracts/DTRM_PHASE4_SCHEDULED_REVISION_ADDENDUM_STATEMENT_V1.json"
)
PROVENANCE = ROOT / "research/evidence/phase4_backend_scheduled_revision_provenance_v1.json"
EXPECTED_SHA256 = "98e245830a08b79423fc95c67033fa47aa066e00beaa1d4bf47f110e0ca93ac7"


def _bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")


def test_registered_statement_is_canonical_and_exact() -> None:
    verified = verify_statement_bytes(STATEMENT.read_bytes())
    assert verified.sha256 == EXPECTED_SHA256
    assert verified.canonical_json.encode("utf-8") == STATEMENT.read_bytes()


def test_independent_backend_git_object_evidence_gates_registered_revision() -> None:
    evidence = json.loads(PROVENANCE.read_text())
    assert evidence["source_kind"] == "independent_github_git_object_read"
    merge = evidence["merge_commit"]
    path = evidence["tree_path_evidence"]
    observed = evidence["workflow_observations"]
    assert merge["sha"] == BACKEND_MERGE_COMMIT
    assert merge["tree_sha"] == BACKEND_MERGE_TREE
    assert merge["parents"] == [BACKEND_DORMANT_ANCESTOR, VALIDATED_PR_HEAD]
    assert merge["github_signature_verified"] is True
    assert path["root_tree_sha"] == BACKEND_MERGE_TREE
    assert path["dot_github_tree_sha"] == "ac87a39269d0fd91c6054dbd1564f2e736fc3d82"
    assert path["workflows_tree_sha"] == "da6273f747db49470ba3b255eed8ec54818ea4cd"
    assert path["workflow_path"] == WORKFLOW_PATH
    assert path["workflow_mode"] == "100644"
    assert path["workflow_blob_sha"] == WORKFLOW_BLOB
    assert path["workflow_size_bytes"] == 5763
    assert observed["cron"] == list(CRON)
    assert observed["workflow_identity_argument"] == WORKFLOW_IDENTITY
    arm_expression = (
        "github.event_name == 'schedule' && "
        "vars.PHASE4_PROSPECTIVE_CAPTURE_ARMED == 'true'"
    )
    assert observed["scheduled_job_arm_expression"] == arm_expression
    assert observed["activation_preflight_before_provider_credential"] is True
    assert observed["provider_credential_step_scoped"] is True
    credential_before_preflight = observed[
        "provider_credential_present_in_checkout_setup_install_or_preflight"
    ]
    assert credential_before_preflight is False
    assert observed["rerun_attempt_forwarded_to_fail_closed_runner"] is True
    assert evidence["activation_authority"] is False


def test_exact_merged_backend_revision_and_workflow_are_bound() -> None:
    payload = expected_statement()
    backend = payload["backend_revision"]
    workflow = payload["workflow"]
    provider = payload["provider"]
    assert isinstance(backend, dict)
    assert isinstance(workflow, dict)
    assert isinstance(provider, dict)
    assert backend["merge_commit"] == BACKEND_MERGE_COMMIT
    assert backend["merge_tree"] == BACKEND_MERGE_TREE
    assert backend["dormant_ancestor_commit"] == BACKEND_DORMANT_ANCESTOR
    assert backend["validated_pr_head"] == VALIDATED_PR_HEAD
    assert workflow["path"] == WORKFLOW_PATH
    assert workflow["blob_sha"] == WORKFLOW_BLOB
    assert workflow["identity"] == WORKFLOW_IDENTITY
    assert workflow["cron"] == list(CRON)
    assert provider["roles"] == list(PROVIDER_ROLES)
    assert provider["request_fingerprint_sha256"] == REQUEST_FINGERPRINT


def test_revision_remains_unarmed_and_fail_closed() -> None:
    semantics = expected_statement()["runtime_semantics"]
    assert isinstance(semantics, dict)
    assert semantics["schedule_default_armed"] is False
    assert semantics["periodic_capture_activation_permitted"] is False
    assert semantics["prospective_start_bound"] is False
    assert semantics["credential_or_writer_authority_claimed"] is False
    assert semantics["activation_statement_provisioned"] is False
    assert semantics["provider_credential_available_during_checkout_setup_install_or_preflight"] is False
    assert semantics["provider_credential_scoped_only_to_post_verification_capture_step"] is True
    assert semantics["scheduled_side_effects_require_arm_and_exact_statement_verification"] is True
    assert semantics["scheduled_target_slot_min"] == TARGET_SLOT_MIN == 0
    assert semantics["scheduled_target_slot_max"] == TARGET_SLOT_MAX == 55
    assert semantics["scheduled_first_attempt_target_derived_from_runner_clock"] is True
    assert semantics["scheduled_rerun_target_derivation_from_rerun_clock_permitted"] is False
    assert semantics["scheduled_rerun_without_same_run_immutable_attempt1_provenance_fails_closed"] is True
    assert semantics["scheduled_rerun_counting_eligible"] is False
    assert semantics["manual_workflow_dispatch_counting_eligible"] is False
    assert semantics["scheduled_side_effects_permitted_after_final_slot"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("periodic_capture_activation_permitted", True),
        ("prospective_start_bound", True),
        ("credential_or_writer_authority_claimed", True),
        ("activation_statement_provisioned", True),
        ("provider_credential_available_during_checkout_setup_install_or_preflight", True),
        ("provider_credential_scoped_only_to_post_verification_capture_step", False),
        ("scheduled_side_effects_require_arm_and_exact_statement_verification", False),
        ("scheduled_rerun_target_derivation_from_rerun_clock_permitted", True),
        ("scheduled_rerun_without_same_run_immutable_attempt1_provenance_fails_closed", False),
        ("scheduled_rerun_counting_eligible", True),
        ("manual_workflow_dispatch_counting_eligible", True),
        ("scheduled_side_effects_permitted_after_final_slot", True),
        ("scheduled_target_slot_min", -1),
        ("scheduled_target_slot_max", 56),
    ],
)
def test_runtime_promotions_fail_closed(field: str, value: object) -> None:
    payload = expected_statement()
    semantics = payload["runtime_semantics"]
    assert isinstance(semantics, dict)
    semantics[field] = value
    with pytest.raises(ScheduledRevisionAddendumError):
        verify_statement_bytes(_bytes(payload))


def test_backend_or_workflow_drift_fails_closed() -> None:
    payload = expected_statement()
    backend = payload["backend_revision"]
    workflow = payload["workflow"]
    assert isinstance(backend, dict)
    assert isinstance(workflow, dict)
    backend["merge_commit"] = VALIDATED_PR_HEAD
    with pytest.raises(ScheduledRevisionAddendumError):
        verify_statement_bytes(_bytes(payload))

    payload = expected_statement()
    workflow = payload["workflow"]
    assert isinstance(workflow, dict)
    workflow["blob_sha"] = "0" * 40
    with pytest.raises(ScheduledRevisionAddendumError):
        verify_statement_bytes(_bytes(payload))


def test_duplicate_keys_and_secret_shaped_material_fail_closed() -> None:
    raw = STATEMENT.read_text()
    duplicated = raw.replace(
        '"schema_version": "dtrm.phase4.scheduled_revision_addendum.v1",',
        '"schema_version": "dtrm.phase4.scheduled_revision_addendum.v1",\n'
        '  "schema_version": "dtrm.phase4.scheduled_revision_addendum.v1",',
        1,
    )
    with pytest.raises(ScheduledRevisionAddendumError, match="duplicate JSON keys"):
        verify_statement_bytes(duplicated.encode("utf-8"))

    payload = expected_statement()
    workflow = payload["workflow"]
    assert isinstance(workflow, dict)
    workflow["arm_variable"] = "mongodb+srv://redacted.invalid"
    with pytest.raises(ScheduledRevisionAddendumError, match="forbidden secret material"):
        verify_statement_bytes(_bytes(payload))
