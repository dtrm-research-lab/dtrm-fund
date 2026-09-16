from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "research/evidence/phase4_operational_authority_evidence_v1.json"
STATEMENT_PATH = ROOT / "research/contracts/DTRM_PHASE4_OPERATIONAL_AUTHORITY_STATEMENT_V1.json"
VALIDATION_PATH = ROOT / "research/reports/DTRM_PHASE4_OPERATIONAL_AUTHORITY_VALIDATION_V1.json"

SCIENTIFIC_PARENT = "28b4e787c7b208d810245deda1b37d7881ab50e9"
IMPLEMENTATION_HEAD = "4fafb102ceaa9f9e50ec9987a68bf826f2d21a4d"
BACKEND_COMMIT = "bf844932f8bb3e6773c329a45135fd754c6d8342"
WORKFLOW_BLOB = "0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22"
SLOT_SCHEMA = "dtrm.phase4.prospective_temporal_slot.v1"
RUN_ID = 35001927608
ARTIFACT_ID = 10409798325
ARTIFACT_DIGEST = "f42fc8bc1d23bf1a42b312b577dead856605fedc2dfc7c43b69edecca1f6c16e"
CREDENTIAL_EVIDENCE_SHA256 = "e1203bb38fd1c03448d5d622bceb791f3a1bc5ad325fa89e566889c6b37cbdf3"
WRITER_EVIDENCE_SHA256 = "f4b9d64046b6529a94313734d77f8766320c8a00b5047d0968ab0d2bdfa21390"
STATEMENT_SHA256 = "1ed3703f2fbcc730b9c6ad1e100fb6522e62e9a872f121b0f5d6a678cec294b9"
EXPECTED_WORKFLOWS = {
    "Phase IV temporal evidence v1 gates": 35003014458,
    "Phase IV evidence adequacy v1 gates": 35003014461,
    "Tests": 35003014470,
    "Phase IV gates": 35003014466,
}


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_operational_authority_evidence_binds_exact_noncounting_run() -> None:
    evidence = _load(EVIDENCE_PATH)
    statement = _load(STATEMENT_PATH)

    assert cast(dict[str, object], evidence["scientific_parent"])["commit"] == SCIENTIFIC_PARENT
    runtime = cast(dict[str, object], evidence["backend_runtime"])
    assert runtime["commit"] == BACKEND_COMMIT
    assert runtime["workflow_blob_sha"] == WORKFLOW_BLOB
    assert runtime["slot_schema_identity"] == SLOT_SCHEMA

    run = cast(dict[str, object], evidence["diagnostic_run"])
    assert run["github_run_id"] == RUN_ID
    assert run["artifact_id"] == ARTIFACT_ID
    assert run["artifact_digest_sha256"] == ARTIFACT_DIGEST
    assert run["diagnostic_conclusion"] == "success"
    assert run["scheduled_capture_conclusion"] == "skipped"
    assert run["temporal_index_periodic_capture_activation_permitted"] is False

    registered_run = cast(dict[str, object], statement["diagnostic_run"])
    assert registered_run["github_run_id"] == RUN_ID
    assert registered_run["artifact_id"] == ARTIFACT_ID
    assert registered_run["artifact_digest_sha256"] == ARTIFACT_DIGEST
    assert registered_run["scheduled_capture_conclusion"] == "skipped"


def test_authority_digests_are_independent_and_start_remains_unbound() -> None:
    evidence = _load(EVIDENCE_PATH)
    statement = _load(STATEMENT_PATH)

    credential = evidence["credential_scope_evidence"]
    writer = evidence["writer_authority_evidence"]
    assert _canonical_sha256(credential) == CREDENTIAL_EVIDENCE_SHA256
    assert _canonical_sha256(writer) == WRITER_EVIDENCE_SHA256

    candidate = cast(dict[str, object], statement["activation_candidate"])
    assert candidate["schema_version"] == "dtrm.phase4.prospective_activation_statement.v2"
    assert candidate["provisioned_schema_identity"] == SLOT_SCHEMA
    assert candidate["credential_scope_status"] == "AUTHORIZED"
    assert candidate["credential_scope_evidence_sha256"] == CREDENTIAL_EVIDENCE_SHA256
    assert candidate["writer_authority_status"] == "AUTHORIZED"
    assert candidate["writer_authority_evidence_sha256"] == WRITER_EVIDENCE_SHA256
    assert candidate["prospective_start_utc"] is None
    assert candidate["human_activation_authorized"] is False
    assert candidate["periodic_capture_activation_permitted"] is False

    assert statement["readiness_status"] == "AUTHORIZED_AUTHORITY_EVIDENCE_START_UNBOUND"
    assert statement["provider_rights_status"] == "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"
    assert all(
        permission is False
        for permission in cast(dict[str, object], statement["downstream_permissions"]).values()
    )


def test_authority_evidence_is_source_value_free_and_statement_digest_is_frozen() -> None:
    evidence_text = EVIDENCE_PATH.read_text(encoding="utf-8")
    statement_bytes = STATEMENT_PATH.read_bytes()
    combined = (evidence_text + statement_bytes.decode("utf-8")).lower()

    for forbidden in (
        "mongodb://",
        "mongodb+srv://",
        "apikey=",
        "api_key=",
        "authorization:",
        "bearer ",
        "-----begin private key-----",
    ):
        assert forbidden not in combined

    evidence = _load(EVIDENCE_PATH)
    credential = cast(dict[str, object], evidence["credential_scope_evidence"])
    assert credential["credential_value_observed"] is False
    assert credential["credential_value_persisted"] is False
    assert credential["checkout_setup_install_exposed_to_provider_credential"] is False
    assert credential["scheduled_activation_preflight_exposed_to_provider_credential"] is False

    writer = cast(dict[str, object], evidence["writer_authority_evidence"])
    assert writer["counting_writer_boundary"] == "github_actions_private_artifact"
    assert writer["diagnostic_run_is_counting_eligible"] is False
    assert writer["mongo_write_performed"] is False
    assert writer["legacy_news_namespace_mutation_performed"] is False
    assert writer["public_raw_provider_data_redistribution_permitted"] is False

    assert hashlib.sha256(statement_bytes).hexdigest() == STATEMENT_SHA256


def test_validation_record_binds_exact_head_checks_and_remains_nonactivating() -> None:
    validation = _load(VALIDATION_PATH)

    assert validation["schema_version"] == "dtrm.phase4.operational_authority_validation.v1"
    assert validation["status"] == "PASS_OPERATIONAL_AUTHORITY_EVIDENCE_VALIDATION"
    assert validation["implementation_head"] == IMPLEMENTATION_HEAD
    assert validation["pr_number"] == 25

    workflows = cast(list[object], validation["workflow_runs"])
    observed = {
        cast(dict[str, object], item)["name"]: cast(dict[str, object], item)["run_id"]
        for item in workflows
    }
    assert observed == EXPECTED_WORKFLOWS
    assert all(cast(dict[str, object], item)["conclusion"] == "success" for item in workflows)

    quality = cast(dict[str, object], validation["quality"])
    assert quality == {
        "disposable_wheel_build": "PASS",
        "mypy_strict": "PASS",
        "mypy_source_files": 40,
        "phase4_gate_pytest_passed": 1112,
        "phase4_gate_pytest_skipped": 6,
        "ruff_scoped": "PASS",
        "synthetic_mongo": "PASS",
        "tests_workflow_passed": 1098,
        "tests_workflow_skipped": 20,
    }

    preservation = cast(dict[str, object], validation["source_preservation"])
    assert preservation["before_validation"] == "PASS_SOURCE_PRESERVATION"
    assert preservation["after_validation"] == "PASS_SOURCE_PRESERVATION"
    assert preservation["verified_inherited_files"] == 157

    boundary = cast(dict[str, object], validation["authority_boundary"])
    assert boundary["prospective_start_utc"] is None
    assert boundary["human_activation_authorized"] is False
    assert boundary["periodic_capture_activation_permitted"] is False
    assert boundary["scientific_permissions_all_false"] is True
    assert boundary["provider_rights_status"] == "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"
