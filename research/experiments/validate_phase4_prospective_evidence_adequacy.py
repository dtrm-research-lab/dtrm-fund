from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, timedelta
from pathlib import Path
from typing import cast

from dtrm.phase4.prospective_evidence_adequacy import (
    ACTIVATION_SCHEMA,
    ADEQUACY_PREREGISTRATION,
    GRAPH,
    MAX_COMPLETION_LAG_MINUTES,
    MAX_RECORD_PUBLICATION_LAG_MINUTES,
    MAX_RUN_DURATION_MINUTES,
    MAX_SCHEDULE_LAG_MINUTES,
    MIN_ACCEPTED_SLOTS,
    MIN_FIRST_DAY_ACCEPTED_SLOTS,
    MIN_LAST_DAY_ACCEPTED_SLOTS,
    PROVIDER_ROLES,
    PROSPECTIVE_EVIDENCE_REGISTRATION,
    PROVIDER_RIGHTS_STATUS,
    REQUEST_FINGERPRINT,
    REVIEW_AMENDMENT,
    REVIEW_AMENDMENT_V2,
    REVIEW_AMENDMENT_V3,
    SCHEDULE_CRON,
    SCHEDULE_UTC,
    SCIENTIFIC_PARENT_INTEGRATION,
    TARGET_SLOTS,
    ActivationBinding,
    SlotAttempt,
    audit_evidence,
    expected_cron,
    expected_target,
    finalization_at,
)

JsonObject = dict[str, object]
_SYNTHETIC_ACTIVATION_STATEMENT = "synthetic-activation-v2"
_SYNTHETIC_COMMIT = "a" * 40
_SYNTHETIC_TREE = "b" * 40
_SYNTHETIC_WORKFLOW_BLOB = "e" * 40
_SYNTHETIC_CREDENTIAL_EVIDENCE = "f" * 64
_SYNTHETIC_WRITER_EVIDENCE = "1" * 64
_SYNTHETIC_START_UTC = "2026-09-15T00:00:00Z"
_SYNTHETIC_WORKFLOW_PATH = ".github/workflows/phase4-prospective-temporal-evidence-v1.yml"
_SYNTHETIC_WORKFLOW_IDENTITY = "phase4-prospective-temporal-evidence-v1"
_SYNTHETIC_SCHEMA_IDENTITY = "synthetic-prospective-schema-v1"


def _synthetic_activation_bytes() -> bytes:
    return json.dumps(
        {
            "schema_version": ACTIVATION_SCHEMA,
            "activation_statement": _SYNTHETIC_ACTIVATION_STATEMENT,
            "backend_commit": _SYNTHETIC_COMMIT,
            "backend_tree": _SYNTHETIC_TREE,
            "workflow_path": _SYNTHETIC_WORKFLOW_PATH,
            "workflow_blob_sha": _SYNTHETIC_WORKFLOW_BLOB,
            "workflow_identity": _SYNTHETIC_WORKFLOW_IDENTITY,
            "provider_roles": list(PROVIDER_ROLES),
            "request_fingerprint_sha256": REQUEST_FINGERPRINT,
            "provisioned_schema_identity": _SYNTHETIC_SCHEMA_IDENTITY,
            "credential_scope_status": "AUTHORIZED",
            "credential_scope_evidence_sha256": _SYNTHETIC_CREDENTIAL_EVIDENCE,
            "writer_authority_status": "AUTHORIZED",
            "writer_authority_evidence_sha256": _SYNTHETIC_WRITER_EVIDENCE,
            "prospective_start_utc": _SYNTHETIC_START_UTC,
            "periodic_capture_activation_permitted": True,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _expected_statement() -> JsonObject:
    return {
        "schema_version": "dtrm.phase4.prospective_evidence_adequacy_statement.v1",
        "graph": GRAPH,
        "scientific_parent_integration": SCIENTIFIC_PARENT_INTEGRATION,
        "prospective_evidence_registration": PROSPECTIVE_EVIDENCE_REGISTRATION,
        "adequacy_preregistration_commit": ADEQUACY_PREREGISTRATION,
        "review_amendment_commit": REVIEW_AMENDMENT,
        "review_amendment_v2_commit": REVIEW_AMENDMENT_V2,
        "review_amendment_v3_commit": REVIEW_AMENDMENT_V3,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "activation_binding": {
            "statement_schema": ACTIVATION_SCHEMA,
            "exact_statement_bytes_required": True,
            "trusted_reference_fields": [
                "activation_statement",
                "activation_statement_sha256",
            ],
            "required_statement_fields": [
                "backend_commit",
                "backend_tree",
                "workflow_path",
                "workflow_blob_sha",
                "workflow_identity",
                "provider_roles",
                "request_fingerprint_sha256",
                "provisioned_schema_identity",
                "credential_scope_status",
                "credential_scope_evidence_sha256",
                "writer_authority_status",
                "writer_authority_evidence_sha256",
                "prospective_start_utc",
                "periodic_capture_activation_permitted",
            ],
            "derived_fields": ["start_utc_day", "end_utc_day"],
        },
        "interval": {
            "utc_days": 14,
            "schedule_utc": list(SCHEDULE_UTC),
            "schedule_cron": list(SCHEDULE_CRON),
            "target_slots": TARGET_SLOTS,
            "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
            "minimum_first_day_accepted_slots": MIN_FIRST_DAY_ACCEPTED_SLOTS,
            "minimum_last_day_accepted_slots": MIN_LAST_DAY_ACCEPTED_SLOTS,
            "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
            "maximum_run_duration_minutes": MAX_RUN_DURATION_MINUTES,
            "maximum_completion_lag_minutes": MAX_COMPLETION_LAG_MINUTES,
            "maximum_record_publication_lag_minutes": MAX_RECORD_PUBLICATION_LAG_MINUTES,
            "maximum_total_record_lag_minutes": (
                MAX_COMPLETION_LAG_MINUTES + MAX_RECORD_PUBLICATION_LAG_MINUTES
            ),
            "missing_slots_are_not_backfilled": True,
            "early_stopping_permitted": False,
            "finalization_boundary_is_pending": True,
        },
        "accepted_event": "schedule",
        "accepted_run_attempt": 1,
        "manual_runs_count_toward_threshold": False,
        "scheduled_reruns_count_toward_threshold": False,
        "scheduled_rerun_target_provenance_required": True,
        "late_first_attempt_records_serialized": True,
        "late_records_partitioned_before_duplicate_resolution": True,
        "final_statuses": [
            "PENDING_INTERVAL",
            "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1",
            "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1",
        ],
        "slot_statuses": [
            "ACCEPTED",
            "MISSING",
            "FAILED",
            "LATE",
            "DUPLICATE",
            "CONTRACT_MISMATCH",
        ],
        "permissions": {
            "adequacy_auditor_implementation_permitted": True,
            "source_value_free_slot_record_implementation_permitted": True,
            "scheduled_workflow_configuration_permitted": True,
            "periodic_capture_activation_permitted": False,
            "confirmatory_history_construction_permitted": False,
            "temporal_state_outcome_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "phase3_policy_mutation_permitted": False,
            "public_raw_provider_data_redistribution_permitted": False,
        },
    }


def _load_and_validate_statement(path: Path) -> None:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if payload != _expected_statement():
        raise RuntimeError("PROSPECTIVE_EVIDENCE_ADEQUACY_STATEMENT_MISMATCH")


def _synthetic_binding() -> ActivationBinding:
    statement = _synthetic_activation_bytes()
    return ActivationBinding(
        statement_bytes=statement,
        trusted_activation_statement=_SYNTHETIC_ACTIVATION_STATEMENT,
        trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
    )


def _synthetic_attempt(binding: ActivationBinding, slot: int) -> SlotAttempt:
    target = expected_target(binding, slot)
    return SlotAttempt(
        slot=slot,
        target_at_utc=target,
        event_name="schedule",
        cron=expected_cron(slot),
        run_id=20_000 + slot,
        run_attempt=1,
        started_at_utc=target + timedelta(minutes=5),
        completed_at_utc=target + timedelta(minutes=10),
        recorded_at_utc=target + timedelta(minutes=11),
        repository_commit=binding.backend_commit,
        repository_tree=binding.backend_tree,
        request_fingerprint_sha256=REQUEST_FINGERPRINT,
        raw_artifact_sha256="c" * 64,
        temporal_index_sha256="d" * 64,
    )


def build_synthetic_report() -> JsonObject:
    binding = _synthetic_binding()
    accepted_slots = tuple(range(MIN_ACCEPTED_SLOTS - 1)) + (TARGET_SLOTS - 1,)
    attempts = tuple(_synthetic_attempt(binding, slot) for slot in accepted_slots)
    audit = audit_evidence(
        binding,
        attempts,
        finalization_at(binding) + timedelta(seconds=1),
    )
    counts = cast(dict[str, int], audit["counts"])
    return {
        "graph": GRAPH,
        "engineering_status": "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_AUDITOR_V1",
        "synthetic_final_status": cast(str, audit["final_status"]),
        "target_slots": TARGET_SLOTS,
        "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
        "minimum_first_day_accepted_slots": MIN_FIRST_DAY_ACCEPTED_SLOTS,
        "minimum_last_day_accepted_slots": MIN_LAST_DAY_ACCEPTED_SLOTS,
        "accepted_slots": counts["ACCEPTED"],
        "missing_slots": counts["MISSING"],
        "first_day_accepted_slots": cast(int, audit["first_day_accepted_slots"]),
        "last_day_accepted_slots": cast(int, audit["last_day_accepted_slots"]),
        "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
        "maximum_run_duration_minutes": MAX_RUN_DURATION_MINUTES,
        "maximum_completion_lag_minutes": MAX_COMPLETION_LAG_MINUTES,
        "maximum_record_publication_lag_minutes": MAX_RECORD_PUBLICATION_LAG_MINUTES,
        "maximum_total_record_lag_minutes": (
            MAX_COMPLETION_LAG_MINUTES + MAX_RECORD_PUBLICATION_LAG_MINUTES
        ),
        "activation_statement": binding.activation_statement,
        "activation_statement_sha256": binding.activation_statement_sha256,
        "prospective_start_utc": binding.prospective_start_utc
        .astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "workflow_path": binding.workflow_path,
        "workflow_blob_sha": binding.workflow_blob_sha,
        "workflow_identity": binding.workflow_identity,
        "provider_roles": list(binding.provider_roles),
        "provisioned_schema_identity": binding.provisioned_schema_identity,
        "credential_scope_status": binding.credential_scope_status,
        "credential_scope_evidence_sha256": binding.credential_scope_evidence_sha256,
        "writer_authority_status": binding.writer_authority_status,
        "writer_authority_evidence_sha256": binding.writer_authority_evidence_sha256,
        "review_amendment_commit": REVIEW_AMENDMENT,
        "review_amendment_v2_commit": REVIEW_AMENDMENT_V2,
        "review_amendment_v3_commit": REVIEW_AMENDMENT_V3,
        "start_utc_day": binding.start_utc_day.isoformat(),
        "end_utc_day": binding.end_utc_day.isoformat(),
        "finalization_at_utc": finalization_at(binding)
        .astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "accepted_run_attempt": 1,
        "manual_runs_count_toward_threshold": False,
        "scheduled_reruns_count_toward_threshold": False,
        "scheduled_rerun_target_provenance_required": True,
        "late_first_attempt_records": cast(int, audit["late_first_attempt_records"]),
        "late_records_partitioned_before_duplicate_resolution": True,
        "finalization_boundary_is_pending": True,
        "missing_slots_are_not_backfilled": True,
        "early_stopping_permitted": False,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "confirmatory_history_construction_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
        "public_raw_provider_data_redistribution_permitted": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--statement",
        type=Path,
        default=Path(
            "research/contracts/DTRM_PHASE4_PROSPECTIVE_EVIDENCE_ADEQUACY_STATEMENT_V1.json"
        ),
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    statement = cast(Path, args.statement)
    output = cast(Path, args.output)
    _load_and_validate_statement(statement)
    report = build_synthetic_report()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_AUDITOR_V1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
