from __future__ import annotations

import json

import pytest

from dtrm.phase4.postmerge_activation_binding import (
    ACTIVATION_SCHEMA,
    BACKEND_COMMIT,
    BACKEND_TREE,
    PROVIDER_ROLES,
    READINESS_STATUS,
    REQUEST_FINGERPRINT_SHA256,
    SCIENTIFIC_PARENT_COMMIT,
    SCIENTIFIC_PARENT_TREE,
    WORKFLOW_BLOB_SHA,
    WORKFLOW_IDENTITY,
    WORKFLOW_PATH,
    PostMergeBindingError,
    expected_statement,
    readiness_review,
    verify_statement_bytes,
)


def _statement_bytes(**activation_overrides: object) -> bytes:
    payload = expected_statement()
    activation = payload["activation_contract"]
    assert isinstance(activation, dict)
    activation.update(activation_overrides)
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def test_postmerge_binding_pins_exact_verified_backend_and_workflow() -> None:
    binding = verify_statement_bytes(_statement_bytes())
    review = readiness_review(binding)

    assert review["readiness_status"] == READINESS_STATUS
    assert review["fixed_bindings"] == {
        "scientific_parent_commit": SCIENTIFIC_PARENT_COMMIT,
        "scientific_parent_tree": SCIENTIFIC_PARENT_TREE,
        "backend_commit": BACKEND_COMMIT,
        "backend_tree": BACKEND_TREE,
        "workflow_path": WORKFLOW_PATH,
        "workflow_blob_sha": WORKFLOW_BLOB_SHA,
        "workflow_identity": WORKFLOW_IDENTITY,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT_SHA256,
        "provider_roles": list(PROVIDER_ROLES),
    }


def test_readiness_is_fail_closed_without_operational_authority() -> None:
    binding = verify_statement_bytes(_statement_bytes())
    review = readiness_review(binding)

    assert review["remaining_gates"] == {
        "provisioned_schema_identity": False,
        "credential_scope_authorized": False,
        "writer_authority_authorized": False,
        "prospective_start_registered": False,
        "human_activation_authorized": False,
    }
    assert review["workflow_state"] == {
        "workflow_dispatch_present": True,
        "schedule_present": False,
    }
    assert review["activation"] == {
        "schema_version": ACTIVATION_SCHEMA,
        "periodic_capture_activation_permitted": False,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provisioned_schema_identity", "phase4-prospective-evidence-v1"),
        ("credential_scope_status", "AUTHORIZED"),
        ("credential_scope_evidence_sha256", "a" * 64),
        ("writer_authority_status", "AUTHORIZED"),
        ("writer_authority_evidence_sha256", "b" * 64),
        ("prospective_start_utc", "2026-09-15T00:00:00Z"),
        ("human_activation_authorized", True),
        ("periodic_capture_activation_permitted", True),
    ],
)
def test_readiness_statement_cannot_promote_activation_fields(
    field: str, value: object
) -> None:
    with pytest.raises(PostMergeBindingError):
        verify_statement_bytes(_statement_bytes(**{field: value}))


def test_duplicate_json_keys_fail_closed() -> None:
    raw = _statement_bytes().decode("utf-8")
    duplicated = raw.replace(
        '"schema_version": "dtrm.phase4.postmerge_activation_binding_readiness.v1",',
        '"schema_version": "dtrm.phase4.postmerge_activation_binding_readiness.v1",\n'
        '  "schema_version": "dtrm.phase4.postmerge_activation_binding_readiness.v1",',
        1,
    )
    with pytest.raises(PostMergeBindingError, match="duplicate JSON keys"):
        verify_statement_bytes(duplicated.encode("utf-8"))


def test_secret_shaped_material_is_rejected_without_echo() -> None:
    raw = _statement_bytes().decode("utf-8")
    contaminated = raw.replace(
        '"UNVERIFIED"',
        '"mongodb+srv://redacted.example.invalid"',
        1,
    )
    with pytest.raises(PostMergeBindingError, match="forbidden secret material"):
        verify_statement_bytes(contaminated.encode("utf-8"))


def test_canonical_round_trip_is_deterministic() -> None:
    first = verify_statement_bytes(_statement_bytes())
    second = verify_statement_bytes(first.canonical_json.encode("utf-8"))

    assert first == second
    assert len(first.sha256) == 64
