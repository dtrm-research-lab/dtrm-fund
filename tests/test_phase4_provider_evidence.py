"""Acceptance tests for the Phase-IV provider evidence audit."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from dtrm.phase4.provider_evidence_audit import (
    CONTRACT_PATH,
    CONTRACT_SHA256,
    ProviderEvidenceError,
    canonical_manifest_bytes,
    normalize_provider_evidence_manifest,
    review_manifest,
    serialize_review,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/contracts/DTRM_PHASE4_PROVIDER_EVIDENCE_MANIFEST_V0.json"
REPORT = ROOT / "research/reports/DTRM_PHASE4_PROVIDER_EVIDENCE_SYNTHETIC_V0.json"


@pytest.fixture
def payload() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _nested(payload: dict[str, object], field: str) -> dict[str, object]:
    return payload[field]  # type: ignore[return-value]


def test_valid_manifest_passes_documentary_gates_but_stays_blocked(payload):
    result = review_manifest(payload).to_dict()
    assert result["engineering_status"] == "PASS_PROVIDER_EVIDENCE_AUDIT"
    assert result["documentary_endpoint_identity_status"] == "PASS"
    assert result["documentary_pagination_parameter_status"] == "PASS"
    assert result["provider_request_semantics_status"] == "BLOCKED"
    assert result["account_entitlement_status"] == "BLOCKED"
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
            "history_construction_permitted",
            "temporal_state_fitting_permitted",
            "training_permitted",
            "outcome_access_permitted",
            "model_fitting_performed",
            "mm1_execution_permitted",
        )
    )


def test_contract_hash_binds_registered_bytes():
    assert hashlib.sha256((ROOT / CONTRACT_PATH).read_bytes()).hexdigest() == (
        CONTRACT_SHA256
    )


def test_unordered_evidence_sets_normalize_canonically(payload):
    expected = serialize_review(review_manifest(payload))
    for field in ("sources", "endpoints", "unresolved_gates"):
        value = payload[field]
        assert isinstance(value, list)
        value.reverse()
    assert serialize_review(review_manifest(payload)) == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("url", "https://example.invalid/docs"),
        ("observed_on", "2026-09-11"),
        ("authority", "THIRD_PARTY"),
        ("snapshot_immutable", True),
    ],
)
def test_public_source_binding_is_exact(payload, field, value):
    sources = payload["sources"]
    assert isinstance(sources, list)
    sources[0][field] = value  # type: ignore[index]
    with pytest.raises(ProviderEvidenceError, match="sources"):
        review_manifest(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("endpoint", "https://example.invalid/news"),
        ("example_query", "?page=1&limit=20"),
        ("latest_feed_documented", False),
        ("page_parameter_documented", False),
        ("limit_parameter_documented", False),
    ],
)
def test_endpoint_documentary_facts_are_exact(payload, field, value):
    endpoints = payload["endpoints"]
    assert isinstance(endpoints, list)
    endpoints[0][field] = value  # type: ignore[index]
    with pytest.raises(ProviderEvidenceError, match="endpoints"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "date_window_equivalent_documented",
        "ordering_stability_documented",
        "terminal_page_rule_documented",
        "short_page_exhaustion_documented",
        "empty_page_exhaustion_documented",
        "repeated_page_exhaustion_documented",
        "revision_semantics_documented",
        "late_arrival_semantics_documented",
        "decision_interval_completeness_documented",
        "provider_observation_clock_authenticated",
        "live_probe_permitted",
    ],
)
def test_provider_semantics_cannot_be_promoted(payload, field):
    _nested(payload, "semantics")[field] = True
    with pytest.raises(ProviderEvidenceError, match="promotion forbidden"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "account_entitlement_evidence_present",
        "exact_payload_storage_authorized",
        "research_retention_authorized",
        "redistribution_authorized",
        "termination_retention_authorized",
    ],
)
def test_account_rights_cannot_be_promoted(payload, field):
    _nested(payload, "rights")[field] = True
    with pytest.raises(ProviderEvidenceError, match="promotion forbidden"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "account_or_order_scope_required_by_public_terms",
        "personal_copy_download_requires_prior_approval",
        "display_redistribution_specific_agreement_required",
        "stored_data_security_controls_required",
        "termination_deletion_obligation_documented",
    ],
)
def test_public_terms_findings_cannot_be_weakened(payload, field):
    _nested(payload, "rights")[field] = False
    with pytest.raises(ProviderEvidenceError, match="registered value mismatch"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "production_provider_access_permitted",
        "production_storage_mutation_permitted",
        "runtime_adapter_execution_permitted",
        "workflow_activation_permitted",
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
    with pytest.raises(ProviderEvidenceError, match="promotion forbidden"):
        review_manifest(payload)


def test_scientific_status_cannot_be_promoted(payload):
    _nested(payload, "permissions")["scientific_status"] = "READY"
    with pytest.raises(ProviderEvidenceError, match="registered value mismatch"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "secret",
    [
        "apikey=secret-value",
        "Authorization: Bearer secret-value",
        "mongodb+srv://user:secret@example.invalid/db",
        "Cookie: session=secret",
        "-----BEGIN PRIVATE KEY-----",
    ],
)
def test_secret_material_is_rejected_without_echo(payload, secret):
    payload["unexpected"] = secret
    with pytest.raises(ProviderEvidenceError) as caught:
        review_manifest(payload)
    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    "level",
    ["manifest", "registered_contract", "semantics", "rights", "permissions"],
)
def test_extra_keys_fail_closed(payload, level):
    target = payload if level == "manifest" else _nested(payload, level)
    target["extra"] = False
    with pytest.raises(ProviderEvidenceError, match="unexpected keys"):
        review_manifest(payload)


def test_tracked_manifest_is_canonical(payload):
    normalized = normalize_provider_evidence_manifest(payload)
    assert canonical_manifest_bytes(normalized) == MANIFEST.read_bytes()


def test_tracked_report_reproduces_exactly(payload):
    actual = serialize_review(review_manifest(payload))
    assert actual.encode() == REPORT.read_bytes()


@pytest.fixture
def cli():
    script = ROOT / "research/experiments/validate_phase4_provider_evidence.py"
    return runpy.run_path(str(script))["main"]


def test_cli_creates_exact_report(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 0
    assert output.read_bytes() == REPORT.read_bytes()
    status = json.loads(capsys.readouterr().out)
    assert status["engineering_status"] == "PASS_PROVIDER_EVIDENCE_AUDIT"
    assert status["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"


def test_cli_rejects_noncanonical_manifest(cli, payload, tmp_path, capsys):
    input_path = tmp_path / "manifest.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    status = json.loads(capsys.readouterr().out)
    assert status["error_code"] == "INVALID_PROVIDER_EVIDENCE_MANIFEST"
    assert not output.exists()


def test_cli_rejects_secret_without_echo(cli, payload, tmp_path, capsys):
    secret = "apikey=do-not-print"
    bad = deepcopy(payload)
    bad["unexpected"] = secret
    input_path = tmp_path / "bad.json"
    input_path.write_text(json.dumps(bad), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    stdout = capsys.readouterr().out
    assert secret not in stdout
    assert json.loads(stdout)["error_code"] == "INVALID_PROVIDER_EVIDENCE_MANIFEST"
    assert not output.exists()


def test_cli_refuses_overwrite(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    output.write_text("occupied", encoding="utf-8")
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 1
    status = json.loads(capsys.readouterr().out)
    assert status["error_code"] == "OUTPUT_EXISTS"
    assert output.read_text(encoding="utf-8") == "occupied"
