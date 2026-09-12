"""Acceptance tests for Phase-IV human rights review v0."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from dtrm.phase4.human_rights_review import (
    CONTRACT_BLOB_SHA,
    CONTRACT_PATH,
    TRACKED_STATEMENT_SHA256,
    HumanRightsReviewError,
    canonical_statement_bytes,
    normalize_human_rights_review,
    review_human_rights,
    serialize_review,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = (
    ROOT / "research/contracts/DTRM_PHASE4_HUMAN_RIGHTS_REVIEW_STATEMENT_V0.json"
)
REPORT = (
    ROOT / "research/reports/DTRM_PHASE4_HUMAN_RIGHTS_REVIEW_SYNTHETIC_V0.json"
)
CLI = ROOT / "research/experiments/validate_phase4_human_rights_review.py"
MODULE = ROOT / "src/dtrm/phase4/human_rights_review.py"


@pytest.fixture
def payload() -> dict[str, object]:
    return json.loads(STATEMENT.read_text(encoding="utf-8"))


def _nested(payload: dict[str, object], field: str) -> dict[str, object]:
    value = payload[field]
    assert isinstance(value, dict)
    return value


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324


def _completed_payload(
    payload: dict[str, object], state: str
) -> dict[str, object]:
    candidate = deepcopy(payload)
    candidate["review_state"] = state
    candidate["review_date"] = "2026-09-12"
    classes = _nested(candidate, "evidence_classes_reviewed")
    classes["PROVIDER_WRITTEN_CLARIFICATION"] = True
    attestation = _nested(candidate, "reviewer_attestation")
    attestation["human_review_completed"] = True
    return candidate


def _fully_supported(payload: dict[str, object]) -> dict[str, object]:
    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_SUPPORTED"
    )
    for key in _nested(candidate, "rights_assessment"):
        _nested(candidate, "rights_assessment")[key] = "SUPPORTED"
    attestation = _nested(candidate, "reviewer_attestation")
    attestation["direct_support_confirmed"] = True
    attestation["contradiction_free"] = True
    return candidate


def test_tracked_pending_state_passes_engineering_and_stays_blocked(payload):
    result = review_human_rights(payload).to_dict()
    assert result["engineering_status"] == "PASS_HUMAN_RIGHTS_REVIEW_PROTOCOL"
    assert result["review_state"] == "PENDING_HUMAN_EVIDENCE"
    assert result["account_entitlement_status"] == "BLOCKED"
    assert result["storage_retention_rights_status"] == "BLOCKED"
    assert result["provider_semantics_probe_eligible"] is False
    assert result["activation_readiness_status"] == "BLOCKED"
    permissions = result["permissions"]
    assert isinstance(permissions, dict)
    assert permissions["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"
    assert all(
        permissions[field] is False
        for field in (
            "production_provider_access_permitted",
            "production_storage_mutation_permitted",
            "runtime_adapter_execution_permitted",
            "workflow_activation_permitted",
            "provider_semantics_live_probe_permitted",
            "history_construction_permitted",
            "temporal_state_fitting_permitted",
            "training_permitted",
            "outcome_access_permitted",
            "model_fitting_performed",
            "mm1_execution_permitted",
        )
    )


def test_contract_blob_binding_is_exact():
    assert _git_blob_sha((ROOT / CONTRACT_PATH).read_bytes()) == CONTRACT_BLOB_SHA


def test_tracked_statement_sha256_is_exact():
    assert hashlib.sha256(STATEMENT.read_bytes()).hexdigest() == TRACKED_STATEMENT_SHA256


def test_fully_supported_synthetic_policy_marks_rights_supported_but_not_operations(
    payload,
):
    candidate = _fully_supported(payload)
    result = review_human_rights(candidate).to_dict()
    assert result["review_state"] == "HUMAN_REVIEW_COMPLETED_SUPPORTED"
    assert result["account_entitlement_status"] == "SUPPORTED_BY_REVIEW"
    assert result["storage_retention_rights_status"] == "SUPPORTED_BY_REVIEW"
    assert result["provider_semantics_probe_eligible"] is True
    assert result["activation_readiness_status"] == "BLOCKED"
    permissions = result["permissions"]
    assert isinstance(permissions, dict)
    assert permissions["production_provider_access_permitted"] is False
    assert permissions["provider_semantics_live_probe_permitted"] is False
    assert permissions["production_storage_mutation_permitted"] is False


def test_unknown_or_not_supported_evidence_remains_blocked(payload):
    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_BLOCKED"
    )
    assessments = _nested(candidate, "rights_assessment")
    assessments["programmatic_endpoint_access"] = "SUPPORTED"
    assessments["exact_payload_storage"] = "NOT_SUPPORTED"
    result = review_human_rights(candidate).to_dict()
    assert result["account_entitlement_status"] == "BLOCKED"
    assert result["storage_retention_rights_status"] == "BLOCKED"
    assert result["provider_semantics_probe_eligible"] is False


def test_supported_state_requires_all_mandatory_positive_support(payload):
    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_SUPPORTED"
    )
    assessments = _nested(candidate, "rights_assessment")
    for key in assessments:
        assessments[key] = "SUPPORTED"
    assessments["storage_security_obligations_known"] = "UNKNOWN"
    attestation = _nested(candidate, "reviewer_attestation")
    attestation["direct_support_confirmed"] = True
    attestation["contradiction_free"] = True
    with pytest.raises(HumanRightsReviewError, match="mandatory positive support missing"):
        review_human_rights(candidate)


def test_supported_state_requires_direct_support_and_no_contradiction(payload):
    candidate = _fully_supported(payload)
    attestation = _nested(candidate, "reviewer_attestation")
    attestation["direct_support_confirmed"] = False
    with pytest.raises(HumanRightsReviewError, match="mandatory positive support missing"):
        review_human_rights(candidate)

    candidate = _fully_supported(payload)
    _nested(candidate, "reviewer_attestation")["contradiction_free"] = False
    with pytest.raises(HumanRightsReviewError, match="mandatory positive support missing"):
        review_human_rights(candidate)


def test_fully_positive_completed_review_cannot_be_mislabeled_blocked(payload):
    candidate = _fully_supported(payload)
    candidate["review_state"] = "HUMAN_REVIEW_COMPLETED_BLOCKED"
    with pytest.raises(HumanRightsReviewError, match="fully supported evidence"):
        review_human_rights(candidate)


def test_pending_state_cannot_claim_review_material(payload):
    candidate = deepcopy(payload)
    _nested(candidate, "evidence_classes_reviewed")["ACCOUNT_PLAN_SUMMARY"] = True
    with pytest.raises(HumanRightsReviewError, match="reviewed evidence forbidden"):
        review_human_rights(candidate)

    candidate = deepcopy(payload)
    candidate["review_date"] = "2026-09-12"
    with pytest.raises(HumanRightsReviewError, match="reviewed evidence forbidden"):
        review_human_rights(candidate)

    candidate = deepcopy(payload)
    _nested(candidate, "rights_assessment")["programmatic_endpoint_access"] = "SUPPORTED"
    with pytest.raises(HumanRightsReviewError, match="assessments must remain UNKNOWN"):
        review_human_rights(candidate)


def test_completed_review_requires_evidence_class_date_and_human_review(payload):
    candidate = deepcopy(payload)
    candidate["review_state"] = "HUMAN_REVIEW_COMPLETED_BLOCKED"
    with pytest.raises(HumanRightsReviewError, match="evidence class required"):
        review_human_rights(candidate)

    candidate = deepcopy(payload)
    candidate["review_state"] = "HUMAN_REVIEW_COMPLETED_BLOCKED"
    _nested(candidate, "evidence_classes_reviewed")["ACCOUNT_PLAN_SUMMARY"] = True
    with pytest.raises(HumanRightsReviewError, match="review date required"):
        review_human_rights(candidate)

    candidate["review_date"] = "2026-09-12"
    with pytest.raises(HumanRightsReviewError, match="human_review_completed required"):
        review_human_rights(candidate)


@pytest.mark.parametrize("assessment", ["YES", "NO", "MAYBE", True, 1, None])
def test_assessments_are_strict_three_state(payload, assessment):
    _nested(payload, "rights_assessment")["exact_payload_storage"] = assessment
    with pytest.raises(HumanRightsReviewError, match="invalid value"):
        review_human_rights(payload)


@pytest.mark.parametrize(
    "field",
    [
        "production_provider_access_permitted",
        "production_storage_mutation_permitted",
        "runtime_adapter_execution_permitted",
        "workflow_activation_permitted",
        "provider_semantics_live_probe_permitted",
        "history_construction_permitted",
        "temporal_state_fitting_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
        "mm1_execution_permitted",
    ],
)
def test_operational_permissions_cannot_be_promoted(payload, field):
    _nested(payload, "permissions")[field] = True
    with pytest.raises(HumanRightsReviewError, match="promotion forbidden"):
        review_human_rights(payload)


@pytest.mark.parametrize(
    "sensitive",
    [
        "apikey=secret",
        "api_key=secret",
        "Authorization: Bearer secret",
        "mongodb+srv://example.invalid/db",
        "Cookie: session=secret",
        "password=secret",
        "account_id=12345",
        "customer_id=12345",
        "invoice_number=12345",
        "order_number=12345",
        "billing_address=somewhere",
        "person@example.com",
        "-----BEGIN PRIVATE KEY-----",
    ],
)
def test_sensitive_material_is_rejected_without_echo(payload, sensitive):
    corrupted = deepcopy(payload)
    corrupted["provider_scope"] = sensitive
    with pytest.raises(HumanRightsReviewError) as exc_info:
        review_human_rights(corrupted)
    assert sensitive not in str(exc_info.value)


@pytest.mark.parametrize(
    "field",
    [
        "raw_contract_text",
        "order_form_text",
        "screenshot_content",
        "provider_payload",
        "account_email",
        "reviewer_name",
    ],
)
def test_private_material_fields_fail_closed(payload, field):
    payload[field] = "redacted"
    with pytest.raises(HumanRightsReviewError):
        review_human_rights(payload)


def test_redacted_digest_requires_lowercase_sha256_only_for_completed_review(payload):
    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_BLOCKED"
    )
    candidate["redacted_evidence_sha256"] = "a" * 64
    result = review_human_rights(candidate).to_dict()
    summary = result["review_summary"]
    assert isinstance(summary, dict)
    assert summary["has_redacted_evidence_digest"] is True

    candidate["redacted_evidence_sha256"] = "A" * 64
    with pytest.raises(HumanRightsReviewError, match="invalid SHA-256"):
        review_human_rights(candidate)


def test_raw_private_material_flags_are_forbidden(payload):
    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_BLOCKED"
    )
    attestation = _nested(candidate, "reviewer_attestation")
    attestation["raw_private_material_stored_in_repo"] = True
    with pytest.raises(HumanRightsReviewError, match="forbidden"):
        review_human_rights(candidate)

    candidate = _completed_payload(
        payload, "HUMAN_REVIEW_COMPLETED_BLOCKED"
    )
    _nested(candidate, "reviewer_attestation")[
        "secrets_or_identifiers_stored_in_repo"
    ] = True
    with pytest.raises(HumanRightsReviewError, match="forbidden"):
        review_human_rights(candidate)


def test_normalized_state_is_detached_and_canonical(payload):
    normalized = normalize_human_rights_review(payload)
    before = normalized.canonical_json
    _nested(payload, "rights_assessment")["exact_payload_storage"] = "SUPPORTED"
    assert normalized.canonical_json == before
    assert canonical_statement_bytes(normalized) == before.encode("utf-8")


def test_tracked_statement_is_canonical(payload):
    normalized = normalize_human_rights_review(payload)
    assert STATEMENT.read_bytes() == canonical_statement_bytes(normalized)


def test_tracked_report_reproduces_exactly(payload):
    assert REPORT.read_text(encoding="utf-8") == serialize_review(
        review_human_rights(payload)
    )


def test_new_review_code_has_no_live_io_or_secret_discovery():
    source = MODULE.read_text(encoding="utf-8").lower()
    cli_source = CLI.read_text(encoding="utf-8").lower()
    combined = source + cli_source
    for forbidden in (
        "import requests",
        "import httpx",
        "import pymongo",
        "mongo_client",
        "os.getenv",
        "os.environ",
        "dotenv",
        "urllib.request",
        "financialmodelingprep.com/stable/",
    ):
        assert forbidden not in combined


def test_cli_creates_exact_pending_report(tmp_path, capsys):
    module = runpy.run_path(str(CLI))
    output = tmp_path / "review.json"
    assert module["main"](["--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")
    stdout = capsys.readouterr().out
    assert '"review_state": "PENDING_HUMAN_EVIDENCE"' in stdout
    assert '"status": "succeeded"' in stdout


def test_cli_refuses_overwrite(tmp_path, capsys):
    module = runpy.run_path(str(CLI))
    output = tmp_path / "review.json"
    output.write_text("existing", encoding="utf-8")
    assert module["main"](["--output", str(output)]) == 1
    assert output.read_text(encoding="utf-8") == "existing"
    assert "OUTPUT_EXISTS" in capsys.readouterr().out


def test_cli_rejects_noncanonical_statement(tmp_path, capsys, payload):
    module = runpy.run_path(str(CLI))
    statement_path = tmp_path / "statement.json"
    statement_path.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "review.json"
    assert module["main"](
        ["--statement", str(statement_path), "--output", str(output)]
    ) == 1
    assert not output.exists()
    assert "INVALID_HUMAN_RIGHTS_REVIEW_STATEMENT" in capsys.readouterr().out


def test_cli_rejects_sensitive_input_without_echo(tmp_path, capsys, payload):
    module = runpy.run_path(str(CLI))
    secret = "person@example.com"
    payload["provider_scope"] = secret
    statement_path = tmp_path / "statement.json"
    statement_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "review.json"
    assert module["main"](
        ["--statement", str(statement_path), "--output", str(output)]
    ) == 1
    assert not output.exists()
    stdout = capsys.readouterr().out
    assert secret not in stdout
    assert "INVALID_HUMAN_RIGHTS_REVIEW_STATEMENT" in stdout
