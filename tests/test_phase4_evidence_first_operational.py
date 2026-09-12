from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from dtrm.phase4.evidence_first_operational import (
    CONTRACT_BLOB_SHA,
    CONTRACT_PATH,
    EvidenceFirstOperationalError,
    build_evidence_first_report,
    canonical_report_json,
    normalize_evidence_first_operational,
)

ROOT = Path(__file__).resolve().parents[1]
STATEMENT_PATH = ROOT / "research/contracts/DTRM_PHASE4_EVIDENCE_FIRST_OPERATIONAL_STATEMENT_V0.json"
REPORT_PATH = ROOT / "research/reports/DTRM_PHASE4_EVIDENCE_FIRST_OPERATIONAL_SYNTHETIC_V0.json"


def _statement() -> dict[str, object]:
    return json.loads(STATEMENT_PATH.read_text(encoding="utf-8"))


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    framed = f"blob {len(payload)}\0".encode() + payload
    return hashlib.sha1(framed).hexdigest()


def test_registered_contract_blob_is_exact() -> None:
    assert _git_blob_sha(ROOT / CONTRACT_PATH) == CONTRACT_BLOB_SHA


def test_canonical_statement_validates_and_reproduces_report() -> None:
    statement = _statement()
    state = normalize_evidence_first_operational(statement)
    assert state.to_dict() == statement
    assert canonical_report_json(statement) == REPORT_PATH.read_text(encoding="utf-8")


def test_report_keeps_rights_deferred_while_capture_is_authorized() -> None:
    report = build_evidence_first_report(normalize_evidence_first_operational(_statement()))
    assert report["scientific_evidence_status"] == "AUTHORIZED_PROSPECTIVE_EVIDENCE_CAPTURE"
    assert report["provider_rights_status"] == "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"
    permissions = report["permissions"]
    assert isinstance(permissions, dict)
    assert permissions["live_provider_probe_permitted"] is True
    assert permissions["private_raw_evidence_capture_permitted"] is True
    assert permissions["private_raw_evidence_processing_permitted"] is True
    assert permissions["public_raw_provider_data_redistribution_permitted"] is False


@pytest.mark.parametrize(
    "permission",
    [
        "confirmatory_history_construction_permitted",
        "temporal_state_outcome_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "phase3_policy_mutation_permitted",
    ],
)
def test_later_scientific_permissions_cannot_be_promoted(permission: str) -> None:
    statement = _statement()
    permissions = statement["permissions"]
    assert isinstance(permissions, dict)
    permissions[permission] = True
    with pytest.raises(EvidenceFirstOperationalError, match="registered value mismatch"):
        normalize_evidence_first_operational(statement)


def test_provider_rights_cannot_be_silently_promoted() -> None:
    statement = _statement()
    statement["provider_rights_status"] = "SUPPORTED"
    with pytest.raises(EvidenceFirstOperationalError, match="registered value mismatch"):
        normalize_evidence_first_operational(statement)


def test_public_raw_redistribution_cannot_be_enabled() -> None:
    statement = _statement()
    permissions = statement["permissions"]
    assert isinstance(permissions, dict)
    permissions["public_raw_provider_data_redistribution_permitted"] = True
    with pytest.raises(EvidenceFirstOperationalError, match="registered value mismatch"):
        normalize_evidence_first_operational(statement)


def test_registered_provider_roles_are_exact() -> None:
    statement = _statement()
    roles = statement["provider_roles"]
    assert isinstance(roles, dict)
    roles["stock_latest"] = "https://example.invalid"
    with pytest.raises(EvidenceFirstOperationalError, match="registered value mismatch"):
        normalize_evidence_first_operational(statement)


def test_safety_bounds_are_fixed() -> None:
    statement = _statement()
    bounds = statement["safety_bounds"]
    assert isinstance(bounds, dict)
    bounds["max_pages_per_role"] = 101
    with pytest.raises(EvidenceFirstOperationalError, match="registered value mismatch"):
        normalize_evidence_first_operational(statement)


def test_extra_keys_fail_closed() -> None:
    statement = _statement()
    statement["unregistered"] = True
    with pytest.raises(EvidenceFirstOperationalError, match="unexpected keys"):
        normalize_evidence_first_operational(statement)


@pytest.mark.parametrize(
    "sensitive_value",
    [
        "mongodb://user:secret@host/db",
        "api_key=secret",
        "Authorization: Bearer secret",
        "researcher@example.com",
    ],
)
def test_sensitive_material_is_rejected_without_echo(sensitive_value: str) -> None:
    statement = _statement()
    statement["provider_scope"] = sensitive_value
    with pytest.raises(EvidenceFirstOperationalError) as exc_info:
        normalize_evidence_first_operational(statement)
    assert sensitive_value not in str(exc_info.value)


def test_normalized_state_is_detached_from_input_mutation() -> None:
    statement = _statement()
    original = copy.deepcopy(statement)
    state = normalize_evidence_first_operational(statement)
    statement["provider_scope"] = "mutated"
    assert state.to_dict() == original
