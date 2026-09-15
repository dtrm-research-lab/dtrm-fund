from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "research/reports/DTRM_PHASE4_SCHEDULED_REVISION_VALIDATION_V1.json"
VALIDATED_HEAD = "c99188e5d4bcf7859cd253bb3d8ff03a13fb644f"


def test_scheduled_revision_validation_record_is_bounded_and_non_authorizing() -> None:
    evidence = json.loads(VALIDATION.read_text(encoding="utf-8"))

    assert evidence["schema_version"] == "dtrm.phase4.scheduled_revision_validation.v1"
    assert evidence["validated_feature_head"] == VALIDATED_HEAD
    assert evidence["pull_request"] == 24
    assert evidence["validation_scope"] == "scheduled_revision_addendum_v1"

    ci = evidence["remote_ci"]
    assert ci == {
        "tests": {
            "run_id": 34963178260,
            "head_sha": VALIDATED_HEAD,
            "conclusion": "success",
        },
        "phase4_gates": {
            "run_id": 34963178258,
            "head_sha": VALIDATED_HEAD,
            "conclusion": "success",
        },
        "temporal_evidence_gates": {
            "run_id": 34963178200,
            "head_sha": VALIDATED_HEAD,
            "conclusion": "success",
        },
        "evidence_adequacy_gates": {
            "run_id": 34963178082,
            "head_sha": VALIDATED_HEAD,
            "conclusion": "success",
        },
    }

    quality = evidence["quality_evidence"]
    assert quality["source_preservation_before"] == "PASS_SOURCE_PRESERVATION"
    assert quality["source_preservation_after"] == "PASS_SOURCE_PRESERVATION"
    assert quality["verified_inherited_files"] == 157
    assert quality["scoped_ruff"] == "PASS"
    assert quality["strict_mypy"] == "PASS"
    assert quality["strict_mypy_source_files"] == 40
    assert quality["deterministic_and_inherited_pytest"] == {
        "passed": 1108,
        "skipped": 6,
    }
    assert quality["synthetic_phase4_evidence_reproductions"] == "PASS"
    assert quality["collector_lineage_findings"] == 12
    assert quality["disposable_wheel_build"] == "PASS"
    assert quality["synthetic_mongo"] == "PASS"

    boundary = evidence["scientific_boundary"]
    assert boundary == {
        "prospective_start_bound": False,
        "periodic_capture_activation_permitted": False,
        "activation_statement_provisioned": False,
        "credential_or_writer_authority_claimed": False,
        "provider_access_performed_by_this_validation": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
        "activation_authority": False,
    }
