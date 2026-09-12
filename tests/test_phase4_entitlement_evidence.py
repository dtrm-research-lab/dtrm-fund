"""Acceptance tests for Phase-IV entitlement evidence intake v0."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from dtrm.phase4.entitlement_evidence_intake import (
    CONTRACT_BLOB_SHA,
    CONTRACT_PATH,
    TRACKED_MANIFEST_SHA256,
    EntitlementEvidenceError,
    canonical_statement_bytes,
    normalize_entitlement_evidence,
    review_entitlement_evidence,
    serialize_review,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = (
    ROOT / "research/contracts/DTRM_PHASE4_ENTITLEMENT_EVIDENCE_STATEMENT_V0.json"
)
REPORT = (
    ROOT / "research/reports/DTRM_PHASE4_ENTITLEMENT_EVIDENCE_SYNTHETIC_V0.json"
)
CLI = ROOT / "research/experiments/validate_phase4_entitlement_evidence.py"
MODULE = ROOT / "src/dtrm/phase4/entitlement_evidence_intake.py"


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


def test_tracked_no_evidence_state_passes_engineering_and_stays_blocked(payload):
    result = review_entitlement_evidence(payload).to_dict()
    assert result["engineering_status"] == "PASS_ENTITLEMENT_EVIDENCE_INTAKE"
    assert result["evidence_state"] == "NO_EVIDENCE"
    assert result["account_entitlement_status"] == "BLOCKED"
    assert result["storage_retention_rights_status"] == "BLOCKED"
    assert result["human_rights_review_required"] is True
    assert result["provider_semantics_probe_permitted"] is False
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
    assert hashlib.sha256(STATEMENT.read_bytes()).hexdigest() == TRACKED_MANIFEST_SHA256


def test_unverified_sanitized_evidence_is_structurally_accepted_but_cannot_authorize(
    payload,
):
    payload["evidence_state"] = "EVIDENCE_PRESENT_UNVERIFIED"
    classes = _nested(payload, "evidence_classes")
    classes["written_provider_clarification"] = True
    payload["evidence_date"] = "2026-09-12"
    answers = _nested(payload, "answers")
    answers["programmatic_registered_news_access"] = "YES"
    answers["exact_payload_storage"] = "YES"
    answers["retention_through_phase4_evaluation"] = "YES"

    result = review_entitlement_evidence(payload).to_dict()
    assert result["evidence_state"] == "EVIDENCE_PRESENT_UNVERIFIED"
    assert result["account_entitlement_status"] == "BLOCKED"
    assert result["storage_retention_rights_status"] == "BLOCKED"
    assert result["provider_semantics_probe_permitted"] is False
    summary = result["evidence_summary"]
    assert isinstance(summary, dict)
    assert summary["evidence_class_count"] == 1
    assert summary["yes_count"] == 3
    assert summary["unknown_count"] == 5


def test_human_verified_state_is_forbidden_in_this_increment(payload):
    payload["evidence_state"] = "HUMAN_VERIFIED_EVIDENCE_PRESENT"
    with pytest.raises(EntitlementEvidenceError, match="promotion or value forbidden"):
        review_entitlement_evidence(payload)


@pytest.mark.parametrize(
    "field",
    [
        "human_review_completed",
        "review_artifact_registered",
        "contradiction_free",
    ],
)
def test_reviewer_attestation_cannot_be_promoted(payload, field):
    _nested(payload, "reviewer_attestation")[field] = True
    with pytest.raises(EntitlementEvidenceError, match="promotion forbidden"):
        review_entitlement_evidence(payload)


def test_reviewed_on_cannot_be_set_in_intake_v0(payload):
    _nested(payload, "reviewer_attestation")["reviewed_on"] = "2026-09-12"
    with pytest.raises(EntitlementEvidenceError, match="promotion forbidden"):
        review_entitlement_evidence(payload)


def test_no_evidence_cannot_carry_evidence_class(payload):
    _nested(payload, "evidence_classes")["account_plan_summary"] = True
    with pytest.raises(EntitlementEvidenceError, match="evidence material forbidden"):
        review_entitlement_evidence(payload)


def test_no_evidence_answers_must_remain_unknown(payload):
    _nested(payload, "answers")["exact_payload_storage"] = "YES"
    with pytest.raises(EntitlementEvidenceError, match="answers must remain UNKNOWN"):
        review_entitlement_evidence(payload)


def test_unverified_evidence_requires_class_and_date(payload):
    payload["evidence_state"] = "EVIDENCE_PRESENT_UNVERIFIED"
    with pytest.raises(EntitlementEvidenceError, match="evidence class required"):
        review_entitlement_evidence(payload)

    _nested(payload, "evidence_classes")["provider_licensing_statement"] = True
    with pytest.raises(EntitlementEvidenceError, match="evidence date required"):
        review_entitlement_evidence(payload)


@pytest.mark.parametrize("answer", ["MAYBE", "TRUE", "yes", 1, None])
def test_answers_are_three_state_only(payload, answer):
    _nested(payload, "answers")["exact_payload_storage"] = answer
    with pytest.raises(EntitlementEvidenceError, match="invalid answer"):
        review_entitlement_evidence(payload)


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
def test_operational_and_scientific_permissions_cannot_be_promoted(payload, field):
    _nested(payload, "permissions")[field] = True
    with pytest.raises(EntitlementEvidenceError, match="promotion forbidden"):
        review_entitlement_evidence(payload)


@pytest.mark.parametrize(
    "sensitive",
    [
        "apikey=secret",
        "api_key=secret",
        "Authorization: Bearer secret",
        "mongodb+srv://example.invalid/db",
        "Cookie: session=secret",
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
    with pytest.raises(EntitlementEvidenceError) as exc_info:
        review_entitlement_evidence(corrupted)
    assert sensitive not in str(exc_info.value)


@pytest.mark.parametrize(
    "field",
    ["raw_contract_text", "screenshot_content", "account_email", "provider_payload"],
)
def test_raw_or_identifying_extra_fields_fail_closed(payload, field):
    payload[field] = "redacted"
    with pytest.raises(EntitlementEvidenceError, match="unexpected keys"):
        review_entitlement_evidence(payload)


def test_redacted_digest_is_allowed_only_as_lowercase_sha256_for_unverified(payload):
    payload["evidence_state"] = "EVIDENCE_PRESENT_UNVERIFIED"
    _nested(payload, "evidence_classes")["order_form_or_subscription_terms"] = True
    payload["evidence_date"] = "2026-09-12"
    payload["redacted_evidence_sha256"] = "a" * 64
    result = review_entitlement_evidence(payload).to_dict()
    summary = result["evidence_summary"]
    assert isinstance(summary, dict)
    assert summary["has_redacted_evidence_digest"] is True

    payload["redacted_evidence_sha256"] = "A" * 64
    with pytest.raises(EntitlementEvidenceError, match="invalid SHA-256"):
        review_entitlement_evidence(payload)


def test_normalized_state_is_detached_and_canonical(payload):
    normalized = normalize_entitlement_evidence(payload)
    before = normalized.canonical_json
    _nested(payload, "answers")["exact_payload_storage"] = "YES"
    assert normalized.canonical_json == before
    assert canonical_statement_bytes(normalized) == before.encode("utf-8")


def test_tracked_statement_is_canonical(payload):
    normalized = normalize_entitlement_evidence(payload)
    assert STATEMENT.read_bytes() == canonical_statement_bytes(normalized)


def test_tracked_report_reproduces_exactly(payload):
    assert REPORT.read_text(encoding="utf-8") == serialize_review(
        review_entitlement_evidence(payload)
    )


def test_new_intake_code_has_no_live_io_or_secret_discovery():
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


def test_cli_creates_exact_blocked_report(tmp_path, capsys):
    module = runpy.run_path(str(CLI))
    output = tmp_path / "review.json"
    assert module["main"](["--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")
    stdout = capsys.readouterr().out
    assert '"evidence_state": "NO_EVIDENCE"' in stdout
    assert '"status": "succeeded"' in stdout


def test_cli_refuses_overwrite(tmp_path, capsys):
    module = runpy.run_path(str(CLI))
    output = tmp_path / "review.json"
    output.write_text("existing", encoding="utf-8")
    assert module["main"](["--output", str(output)]) == 1
    assert output.read_text(encoding="utf-8") == "existing"
    stdout = capsys.readouterr().out
    assert "OUTPUT_EXISTS" in stdout


def test_cli_rejects_noncanonical_statement(tmp_path, capsys, payload):
    module = runpy.run_path(str(CLI))
    statement = tmp_path / "statement.json"
    statement.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "review.json"
    assert module["main"](["--statement", str(statement), "--output", str(output)]) == 1
    assert not output.exists()
    stdout = capsys.readouterr().out
    assert "INVALID_ENTITLEMENT_EVIDENCE_STATEMENT" in stdout


def test_cli_rejects_sensitive_input_without_echo(tmp_path, capsys, payload):
    module = runpy.run_path(str(CLI))
    secret = "person@example.com"
    payload["provider_scope"] = secret
    statement = tmp_path / "statement.json"
    statement.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "review.json"
    assert module["main"](["--statement", str(statement), "--output", str(output)]) == 1
    assert not output.exists()
    stdout = capsys.readouterr().out
    assert secret not in stdout
    assert "INVALID_ENTITLEMENT_EVIDENCE_STATEMENT" in stdout
