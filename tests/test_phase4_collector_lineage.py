"""Fail-closed checks for the registered collector-lineage evidence graph."""

import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from dtrm.phase4.collector_lineage import (
    EXPECTED_FINDINGS,
    LineageEvidenceError,
    canonical_manifest_bytes,
    parse_collector_lineage_evidence,
    validate_report_binding,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/reports/DTRM_PHASE4_COLLECTOR_LINEAGE_EVIDENCE_V0.json"
REPORT = ROOT / "research/reports/DTRM_PHASE4_COLLECTOR_LINEAGE_AUDIT_V0.md"


@pytest.fixture
def payload():
    return json.loads(MANIFEST.read_text())


def test_manifest_is_canonical_complete_immutable_and_report_bound(payload):
    audit = parse_collector_lineage_evidence(payload)
    assert len(audit.sources) == 2
    assert len(audit.findings) == len(EXPECTED_FINDINGS) == 12
    assert canonical_manifest_bytes(audit) == MANIFEST.read_bytes()
    validate_report_binding(audit, REPORT.read_text())
    with pytest.raises(FrozenInstanceError):
        audit.findings[0].status = "UNRESOLVED"


def test_input_order_does_not_change_canonical_state(payload):
    expected = canonical_manifest_bytes(parse_collector_lineage_evidence(payload))
    payload["inspection"]["sources"].reverse()
    for source in payload["inspection"]["sources"]:
        source["files"].reverse()
    payload["findings"].reverse()
    for finding in payload["findings"]:
        finding["evidence"].reverse()
    assert canonical_manifest_bytes(parse_collector_lineage_evidence(payload)) == expected


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("commit", "0" * 40),
        ("tree_sha", "1" * 40),
        ("tree_entry_count", 1),
        ("recursive_tree_complete", False),
        ("role", "new_role"),
    ],
)
def test_source_identity_mutations_fail(payload, field, bad):
    payload["inspection"]["sources"][0][field] = bad
    with pytest.raises(LineageEvidenceError):
        parse_collector_lineage_evidence(payload)


@pytest.mark.parametrize("case", ["path", "blob", "duplicate", "missing", "repository"])
def test_selected_file_boundary_fails_closed(payload, case):
    source = payload["inspection"]["sources"][0]
    if case == "path":
        source["files"][0]["path"] = ".env"
    elif case == "blob":
        source["files"][0]["blob_sha"] = "0" * 40
    elif case == "duplicate":
        source["files"][1] = deepcopy(source["files"][0])
    elif case == "missing":
        source["files"].pop()
    else:
        source["repository"] = "unregistered/repository"
    with pytest.raises(LineageEvidenceError):
        parse_collector_lineage_evidence(payload)


@pytest.mark.parametrize(
    "case",
    ["unknown", "status", "duplicate", "missing", "empty_evidence", "bad_range", "bad_citation"],
)
def test_finding_and_citation_boundary_fails_closed(payload, case):
    finding = payload["findings"][0]
    if case == "unknown":
        finding["finding_id"] = "F99_POST_OUTCOME_DISCOVERY"
    elif case == "status":
        finding["status"] = "UNRESOLVED"
    elif case == "duplicate":
        payload["findings"][1] = deepcopy(finding)
    elif case == "missing":
        payload["findings"].pop()
    elif case == "empty_evidence":
        finding["evidence"] = []
    elif case == "bad_range":
        finding["evidence"][0]["line_end"] = 1
    else:
        finding["evidence"][0]["blob_sha"] = "0" * 40
    with pytest.raises(LineageEvidenceError):
        parse_collector_lineage_evidence(payload)


@pytest.mark.parametrize(
    "field",
    [
        "training_permitted",
        "outcome_access_permitted",
        "history_construction_permitted",
        "model_fitting_performed",
        "true_observed_vintage_history_authenticated",
    ],
)
def test_scientific_promotion_flags_fail(payload, field):
    payload["decision"][field] = True
    with pytest.raises(LineageEvidenceError, match="scientific promotion"):
        parse_collector_lineage_evidence(payload)


@pytest.mark.parametrize(
    "secret",
    [
        "mongodb+srv://user:secret@example.invalid/data",
        "https://example.invalid/feed?apikey=secret",
        "Authorization: Bearer secret",
        "-----BEGIN PRIVATE KEY-----",
    ],
)
def test_credential_shaped_material_fails_without_echo(payload, secret):
    payload["findings"][0]["statement"] = secret
    with pytest.raises(LineageEvidenceError) as error:
        parse_collector_lineage_evidence(payload)
    assert secret not in str(error.value)


def test_report_must_contain_every_bound_identity(payload):
    audit = parse_collector_lineage_evidence(payload)
    report = REPORT.read_text().replace(audit.sources[0].tree_sha, "removed-tree")
    with pytest.raises(LineageEvidenceError, match="missing 1 bound identities"):
        validate_report_binding(audit, report)


@pytest.fixture
def cli():
    script = ROOT / "research/experiments/validate_phase4_collector_lineage.py"
    return runpy.run_path(str(script))["main"]


def test_cli_accepts_exact_evidence_and_reports_hashes(cli, capsys):
    assert cli(["--manifest", str(MANIFEST), "--report", str(REPORT)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["engineering_status"] == "PASS_STATIC_EVIDENCE_BOUNDARY"
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert result["finding_count"] == 12
    assert len(result["manifest_sha256"]) == len(result["report_sha256"]) == 64


def test_cli_rejects_noncanonical_manifest(cli, payload, tmp_path, capsys):
    path = tmp_path / "noncanonical.json"
    path.write_text(json.dumps(payload))
    assert cli(["--manifest", str(path), "--report", str(REPORT)]) == 1
    assert json.loads(capsys.readouterr().out)["error"] == (
        "manifest is not canonically serialized"
    )
