"""Acceptance tests for the prospective deployment contract validator."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.prospective_deployment import (
    CONTRACT_PATH,
    CONTRACT_SHA256,
    PROTOCOLS,
    ProspectiveDeploymentError,
    canonical_manifest_bytes,
    normalize_deployment_manifest,
    run_deployment_review,
    serialize_deployment_review,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT / "research/contracts/DTRM_PHASE4_PROSPECTIVE_DEPLOYMENT_MANIFEST_V0.json"
)
REPORT = (
    ROOT / "research/reports/DTRM_PHASE4_PROSPECTIVE_DEPLOYMENT_SYNTHETIC_V0.json"
)


@pytest.fixture
def payload() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _nested(payload: dict[str, object], field: str) -> dict[str, object]:
    return payload[field]  # type: ignore[return-value]


def test_valid_manifest_is_accepted_but_scientifically_blocked(payload):
    result = run_deployment_review(payload).to_dict()
    assert result["engineering_status"] == "PASS_PROSPECTIVE_DEPLOYMENT_CONTRACT"
    assert result["scientific_status"] == "BLOCKED_PROSPECTIVE_DEPLOYMENT"
    assert result["implementation_permitted"] is True
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
        assert result[field] is False


def test_normalized_state_is_frozen_and_detached(payload):
    manifest = normalize_deployment_manifest(payload)
    with pytest.raises(FrozenInstanceError):
        manifest.target_writer.repository = "changed"
    _nested(payload, "target_writer")["repository"] = "changed"
    assert manifest.target_writer.repository == "tech-com-UA00001/theresistance-back"


def test_order_independent_sets_normalize_canonically(payload):
    expected = serialize_deployment_review(run_deployment_review(payload))
    protocols = payload["protocols"]
    assert isinstance(protocols, list)
    protocols.reverse()
    target_files = _nested(payload, "target_writer")["files"]
    assert isinstance(target_files, list)
    target_files.reverse()
    for field in ("runtime_allowed_operations", "runtime_forbidden_operations"):
        operations = _nested(payload, "storage")[field]
        assert isinstance(operations, list)
        operations.reverse()
    assert serialize_deployment_review(run_deployment_review(payload)) == expected


def test_contract_and_protocol_hashes_bind_registered_bytes():
    assert hashlib.sha256((ROOT / CONTRACT_PATH).read_bytes()).hexdigest() == (
        CONTRACT_SHA256
    )
    for _, path, digest, _ in PROTOCOLS:
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("repository", "other/repo"),
        ("repository_id", 1128196793),
        ("branch", "develop"),
        ("parent_commit", "0" * 40),
        ("parent_tree", "0" * 40),
    ],
)
def test_target_identity_is_exact(payload, field, value):
    _nested(payload, "target_writer")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="target_writer"):
        run_deployment_review(payload)


@pytest.mark.parametrize("field", ["path", "blob_sha", "role"])
def test_target_file_binding_is_exact(payload, field):
    files = _nested(payload, "target_writer")["files"]
    assert isinstance(files, list)
    files[0][field] = "0" * 40 if field == "blob_sha" else "changed"  # type: ignore[index]
    with pytest.raises(ProspectiveDeploymentError, match="target_writer.files"):
        run_deployment_review(payload)


@pytest.mark.parametrize("field", ["path", "sha256", "registration_commit"])
def test_contract_identity_is_exact(payload, field):
    contract = _nested(payload, "registered_contract")
    contract[field] = "0" * (64 if field == "sha256" else 40) if field != "path" else "changed"
    with pytest.raises(ProspectiveDeploymentError, match="contract"):
        run_deployment_review(payload)


@pytest.mark.parametrize("field", ["role", "path", "sha256", "registration_commit"])
def test_protocol_identity_is_exact(payload, field):
    protocols = payload["protocols"]
    assert isinstance(protocols, list)
    value = "0" * 64 if field == "sha256" else "0" * 40
    protocols[0][field] = value if field not in {"role", "path"} else "changed"  # type: ignore[index]
    with pytest.raises(ProspectiveDeploymentError, match="protocols"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("database", "other"),
        ("event_collection", "trumpNews"),
        ("run_collection", "trumpNews"),
        ("legacy_collection", "phase4ProspectiveNewsV0"),
        ("legacy_writer_permissions", "insert"),
        ("runtime_schema_mutation_permitted", True),
    ],
)
def test_storage_isolation_is_exact(payload, field, value):
    _nested(payload, "storage")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="storage"):
        run_deployment_review(payload)


@pytest.mark.parametrize("kind", ["allowed_add", "allowed_remove", "forbidden_remove"])
def test_operation_policy_is_exact(payload, kind):
    storage = _nested(payload, "storage")
    if kind == "allowed_add":
        storage["runtime_allowed_operations"].append("update")  # type: ignore[union-attr]
    elif kind == "allowed_remove":
        storage["runtime_allowed_operations"].pop()  # type: ignore[union-attr]
    else:
        storage["runtime_forbidden_operations"].pop()  # type: ignore[union-attr]
    with pytest.raises(ProspectiveDeploymentError, match="storage"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("read_concern", "local"),
        ("write_concern", "1"),
        ("journaled", False),
        ("manifest_inserted_last", False),
        ("all_or_nothing", False),
        ("zero_version_manifest_required", False),
    ],
)
def test_transaction_policy_fails_closed(payload, field, value):
    _nested(payload, "transaction")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="transaction"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("policy", "provider_clock"),
        ("completed_at_semantics", "after_acknowledgement"),
        ("workflow_completion_is_later_bound", False),
        ("authenticated", True),
    ],
)
def test_clock_policy_cannot_claim_authentication(payload, field, value):
    _nested(payload, "clock")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="clock"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("overlap_complete_utc_days", 6),
        ("include_current_partial_day", False),
        ("max_pages_per_role", 99),
        ("max_candidates_per_run", 25001),
        ("max_new_versions_per_run", 4999),
        ("max_payload_bytes_per_candidate", 1048575),
        ("bound_exhaustion_action", "truncate"),
    ],
)
def test_coverage_bounds_are_preregistered(payload, field, value):
    _nested(payload, "coverage")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="coverage"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("retain_through_phase4_evaluation", False),
        ("minimum_years_after_final_artifact", 4),
        ("licence_review_required_before_activation", False),
        ("conflict_action", "shorten_retention"),
    ],
)
def test_retention_cannot_be_weakened(payload, field, value):
    _nested(payload, "retention")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="retention"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("implementation_mode", "active"),
        ("credential_scope", "application_wide"),
        ("environment_inspection_permitted", True),
        ("provider_access_permitted", True),
        ("storage_access_permitted", True),
        ("workflow_enabled", True),
    ],
)
def test_runtime_remains_dormant_and_offline(payload, field, value):
    _nested(payload, "runtime")[field] = value
    with pytest.raises(ProspectiveDeploymentError, match="runtime"):
        run_deployment_review(payload)


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
def test_scientific_or_operational_promotions_are_rejected(payload, field):
    _nested(payload, "permissions")[field] = True
    with pytest.raises(ProspectiveDeploymentError, match="promotion forbidden"):
        run_deployment_review(payload)


def test_dormant_implementation_permission_is_required(payload):
    _nested(payload, "permissions")["implementation_permitted"] = False
    with pytest.raises(ProspectiveDeploymentError, match="required invariant"):
        run_deployment_review(payload)


def test_scientific_status_cannot_be_promoted(payload):
    _nested(payload, "permissions")["scientific_status"] = "READY"
    with pytest.raises(ProspectiveDeploymentError, match="scientific_status"):
        run_deployment_review(payload)


@pytest.mark.parametrize(
    "secret",
    [
        "mongodb://user:pass@example.invalid/db",
        "mongodb+srv://example.invalid",
        "Authorization: Bearer value",
        "-----BEGIN PRIVATE KEY-----",
    ],
)
def test_secret_material_is_rejected_without_echo(payload, secret):
    payload["unexpected"] = secret
    with pytest.raises(ProspectiveDeploymentError) as caught:
        run_deployment_review(payload)
    assert secret not in str(caught.value)


@pytest.mark.parametrize(
    "level",
    [
        "manifest",
        "registered_contract",
        "target_writer",
        "storage",
        "transaction",
        "clock",
        "coverage",
        "retention",
        "runtime",
        "permissions",
    ],
)
def test_extra_keys_fail_at_every_object_boundary(payload, level):
    target = payload if level == "manifest" else _nested(payload, level)
    target["target_return"] = 1
    with pytest.raises(ProspectiveDeploymentError, match="unexpected keys"):
        run_deployment_review(payload)


def test_tracked_manifest_is_canonical(payload):
    manifest = normalize_deployment_manifest(payload)
    assert canonical_manifest_bytes(manifest) == MANIFEST.read_bytes()


def test_tracked_synthetic_report_reproduces_exactly(payload):
    actual = serialize_deployment_review(run_deployment_review(payload))
    assert actual.encode() == REPORT.read_bytes()


@pytest.fixture
def cli():
    script = ROOT / "research/experiments/validate_phase4_prospective_deployment.py"
    return runpy.run_path(str(script))["main"]


def test_cli_creates_exact_report(cli, tmp_path, capsys):
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 0
    assert output.read_bytes() == REPORT.read_bytes()
    status = json.loads(capsys.readouterr().out)
    assert status["engineering_status"] == "PASS_PROSPECTIVE_DEPLOYMENT_CONTRACT"
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
    assert json.loads(stdout)["error_code"] == "INVALID_DEPLOYMENT_MANIFEST"
    assert secret not in stdout
    assert not output.exists()


def test_cli_rejects_noncanonical_manifest(cli, tmp_path, capsys):
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    input_path = tmp_path / "noncanonical.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == (
        "INVALID_DEPLOYMENT_MANIFEST"
    )
    assert not output.exists()


def test_cli_rejects_nonfinite_json(cli, tmp_path, capsys):
    input_path = tmp_path / "bad.json"
    input_path.write_text('{"value": NaN}', encoding="utf-8")
    output = tmp_path / "review.json"
    assert cli(["--manifest", str(input_path), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "INVALID_JSON_INPUT"
    assert not output.exists()


def test_cli_requires_existing_output_parent(cli, tmp_path, capsys):
    output = tmp_path / "missing" / "review.json"
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == (
        "OUTPUT_PARENT_MISSING"
    )
    assert not output.exists()


@pytest.mark.parametrize("kind", ["file", "symlink"])
def test_cli_refuses_existing_output(cli, tmp_path, capsys, kind):
    output = tmp_path / "review.json"
    if kind == "file":
        output.write_text("preserve", encoding="utf-8")
    else:
        target = tmp_path / "target.json"
        target.write_text("preserve", encoding="utf-8")
        output.symlink_to(target)
    assert cli(["--manifest", str(MANIFEST), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"
    assert output.read_text(encoding="utf-8") == "preserve"
