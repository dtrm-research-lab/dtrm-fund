"""Acceptance tests for the Phase-IV prospective activation-readiness gate."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.prospective_activation_readiness import (
    CONTRACT_PATH,
    CONTRACT_SHA256,
    WRITER_FILES,
    ActivationReadinessError,
    canonical_manifest_bytes,
    normalize_readiness_manifest,
    review_manifest,
    serialize_review,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_READINESS_MANIFEST_V0.json"
)
REPORT = (
    ROOT
    / "research/reports/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_READINESS_SYNTHETIC_V0.json"
)


@pytest.fixture
def payload() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _nested(payload: dict[str, object], field: str) -> dict[str, object]:
    value = payload[field]
    assert isinstance(value, dict)
    return value


def test_valid_manifest_passes_engineering_but_remains_blocked(payload):
    result = review_manifest(payload).to_dict()
    assert result["engineering_status"] == "PASS_PROSPECTIVE_ACTIVATION_READINESS_REVIEW"
    assert result["readiness_status"] == "BLOCKED"
    permissions = result["permissions"]
    assert isinstance(permissions, dict)
    assert permissions["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"
    for field in (
        "activation_permitted",
        "production_source_access_permitted",
        "production_storage_mutation_permitted",
        "source_authenticated",
        "clock_authenticated",
        "coverage_authenticated",
        "history_construction_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
    ):
        assert permissions[field] is False


def test_normalized_manifest_is_frozen_and_detached(payload):
    normalized = normalize_readiness_manifest(payload)
    with pytest.raises(FrozenInstanceError):
        normalized.canonical_json = "changed"
    _nested(payload, "dormant_writer")["merge_commit"] = "0" * 40
    restored = normalized.to_dict()
    writer = restored["dormant_writer"]
    assert isinstance(writer, dict)
    assert writer["merge_commit"] == "e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5"


def test_unordered_bindings_normalize_canonically(payload):
    expected = canonical_manifest_bytes(normalize_readiness_manifest(payload))
    files = _nested(payload, "dormant_writer")["files"]
    roles = _nested(payload, "provider")["roles"]
    assert isinstance(files, list)
    assert isinstance(roles, list)
    files.reverse()
    roles.reverse()
    assert canonical_manifest_bytes(normalize_readiness_manifest(payload)) == expected


def test_contract_hash_binds_registered_bytes():
    assert hashlib.sha256((ROOT / CONTRACT_PATH).read_bytes()).hexdigest() == CONTRACT_SHA256


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("repository", "other/repo"),
        ("repository_id", 1),
        ("branch", "develop"),
        ("merge_commit", "0" * 40),
        ("merge_tree", "0" * 40),
        ("validated_feature_head", "0" * 40),
        ("pinned_parent", "0" * 40),
    ],
)
def test_integrated_writer_identity_is_exact(payload, field, value):
    _nested(payload, "dormant_writer")[field] = value
    with pytest.raises(ActivationReadinessError, match="dormant_writer"):
        review_manifest(payload)


@pytest.mark.parametrize("field", ["role", "path", "blob_sha"])
def test_integrated_writer_file_binding_is_exact(payload, field):
    files = _nested(payload, "dormant_writer")["files"]
    assert isinstance(files, list)
    first = files[0]
    assert isinstance(first, dict)
    first[field] = "0" * 40 if field == "blob_sha" else "changed"
    with pytest.raises(ActivationReadinessError, match="dormant_writer.files"):
        review_manifest(payload)


def test_all_expected_writer_bindings_are_present(payload):
    files = _nested(payload, "dormant_writer")["files"]
    assert isinstance(files, list)
    assert len(files) == len(WRITER_FILES) == 6


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observed_on", "2026-09-11"),
        ("documentation_url", "https://example.invalid"),
        ("endpoint_identity_status", "AUTHENTICATED"),
        ("page_limit_example_documented", False),
        ("request_semantics_authenticated", True),
        ("bounded_exhaustion_authenticated", True),
    ],
)
def test_provider_evidence_cannot_overclaim_semantics(payload, field, value):
    _nested(payload, "provider")[field] = value
    with pytest.raises(ActivationReadinessError, match="provider"):
        review_manifest(payload)


@pytest.mark.parametrize("field", ["role", "endpoint"])
def test_provider_role_binding_is_exact(payload, field):
    roles = _nested(payload, "provider")["roles"]
    assert isinstance(roles, list)
    first = roles[0]
    assert isinstance(first, dict)
    first[field] = "changed"
    with pytest.raises(ActivationReadinessError, match="provider.roles"):
        review_manifest(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("account_specific_evidence_present", True),
        ("public_terms_account_or_order_scope", False),
        ("public_terms_copy_download_restriction_without_prior_approval", False),
        ("licence_retention_authorized", True),
        ("exact_payload_storage_authorized", True),
        ("retain_through_phase4_evaluation", False),
        ("proposed_minimum_years_after_final_artifact", 4),
    ],
)
def test_licence_gate_remains_conservative(payload, field, value):
    _nested(payload, "licence")[field] = value
    with pytest.raises(ActivationReadinessError, match="licence"):
        review_manifest(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("database", "other"),
        ("event_collection", "trumpNews"),
        ("run_collection", "trumpNews"),
        ("legacy_collection", "phase4ProspectiveNewsV0"),
        ("storage_schema_provisioned", True),
        ("runtime_schema_mutation_permitted", True),
    ],
)
def test_storage_gate_cannot_claim_provisioning(payload, field, value):
    _nested(payload, "storage")[field] = value
    with pytest.raises(ActivationReadinessError, match="storage"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "least_privilege_credential_provisioned",
        "writer_authority_enumerated",
        "secret_material_permitted",
    ],
)
def test_authority_gate_cannot_be_promoted(payload, field):
    _nested(payload, "authority")[field] = True
    with pytest.raises(ActivationReadinessError, match="authority"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "runtime_adapter_validated",
        "workflow_activation_ready",
        "workflow_enabled",
        "prospective_start_registered",
    ],
)
def test_runtime_gate_cannot_be_promoted(payload, field):
    _nested(payload, "runtime")[field] = True
    with pytest.raises(ActivationReadinessError, match="runtime"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "field",
    [
        "activation_permitted",
        "production_source_access_permitted",
        "production_storage_mutation_permitted",
        "source_authenticated",
        "clock_authenticated",
        "coverage_authenticated",
        "history_construction_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
    ],
)
def test_scientific_and_operational_promotions_are_rejected(payload, field):
    _nested(payload, "permissions")[field] = True
    with pytest.raises(ActivationReadinessError, match="promotion forbidden"):
        review_manifest(payload)


def test_readiness_and_scientific_status_cannot_be_promoted(payload):
    permissions = _nested(payload, "permissions")
    permissions["readiness_status"] = "READY"
    with pytest.raises(ActivationReadinessError, match="readiness_status"):
        review_manifest(payload)
    permissions["readiness_status"] = "BLOCKED"
    permissions["scientific_status"] = "READY"
    with pytest.raises(ActivationReadinessError, match="scientific_status"):
        review_manifest(payload)


@pytest.mark.parametrize(
    "secret",
    [
        "mongodb://user:pass@example.invalid/db",
        "mongodb+srv://example.invalid",
        "https://example.invalid?apikey=secret",
        "api_key=secret",
        "Authorization: Bearer secret",
        "bearer secret",
        "-----BEGIN PRIVATE KEY-----",
    ],
)
def test_secret_material_is_rejected_without_echo(payload, secret):
    payload["unexpected"] = secret
    with pytest.raises(ActivationReadinessError) as caught:
        review_manifest(payload)
    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    "level",
    [
        "manifest",
        "registered_contract",
        "dormant_writer",
        "provider",
        "licence",
        "storage",
        "authority",
        "runtime",
        "permissions",
    ],
)
def test_extra_keys_fail_at_every_object_boundary(payload, level):
    target = payload if level == "manifest" else _nested(payload, level)
    target["target_return"] = 1
    with pytest.raises(ActivationReadinessError, match="unexpected keys"):
        review_manifest(payload)


def test_tracked_manifest_is_canonical(payload):
    assert canonical_manifest_bytes(normalize_readiness_manifest(payload)) == MANIFEST.read_bytes()


def test_tracked_synthetic_report_reproduces_exactly(payload):
    assert serialize_review(review_manifest(payload)).encode() == REPORT.read_bytes()


def test_new_readiness_code_has_no_live_io_or_secret_discovery():
    paths = (
        ROOT / "src/dtrm/phase4/prospective_activation_readiness.py",
        ROOT / "research/experiments/validate_phase4_prospective_activation_readiness.py",
    )
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for forbidden in (
        "import requests",
        "from requests",
        "import pymongo",
        "from pymongo",
        "os.getenv",
        "os.environ",
        "load_dotenv",
        "mongo_uri",
        "fmp_api_key",
        "socket",
    ):
        assert forbidden not in combined


@pytest.fixture
def cli():
    script = (
        ROOT
        / "research/experiments/validate_phase4_prospective_activation_readiness.py"
    )
    return runpy.run_path(str(script))["main"]


def test_cli_creates_exact_blocked_report(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 0
    assert output.read_bytes() == REPORT.read_bytes()
    status = json.loads(capsys.readouterr().out)
    assert status["engineering_status"] == "PASS_PROSPECTIVE_ACTIVATION_READINESS_REVIEW"
    assert status["readiness_status"] == "BLOCKED"
    assert status["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"


def test_cli_rejects_secret_input_without_echo_or_output(cli, tmp_path, capsys):
    bad = deepcopy(json.loads(MANIFEST.read_text(encoding="utf-8")))
    secret = "mongodb+srv://user:password@example.invalid"
    bad["unexpected"] = secret
    input_path = tmp_path / "bad.json"
    input_path.write_text(json.dumps(bad), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    stdout = capsys.readouterr().out
    assert json.loads(stdout)["error_code"] == "INVALID_ACTIVATION_READINESS_MANIFEST"
    assert secret not in stdout
    assert not output.exists()


def test_cli_rejects_noncanonical_manifest(cli, tmp_path, capsys):
    input_path = tmp_path / "manifest.json"
    input_path.write_text(json.dumps(json.loads(MANIFEST.read_text())), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == (
        "INVALID_ACTIVATION_READINESS_MANIFEST"
    )
    assert not output.exists()


def test_cli_refuses_to_overwrite(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    output.write_text("occupied", encoding="utf-8")
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"
    assert output.read_text(encoding="utf-8") == "occupied"
