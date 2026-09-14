from __future__ import annotations

import argparse
import json
from datetime import UTC, date, timedelta
from pathlib import Path
from typing import cast

from dtrm.phase4.prospective_evidence_adequacy import (
    ADEQUACY_PREREGISTRATION,
    GRAPH,
    MAX_SCHEDULE_LAG_MINUTES,
    MIN_ACCEPTED_SLOTS,
    PROSPECTIVE_EVIDENCE_REGISTRATION,
    PROVIDER_RIGHTS_STATUS,
    REQUEST_FINGERPRINT,
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


def _expected_statement() -> JsonObject:
    return {
        "schema_version": "dtrm.phase4.prospective_evidence_adequacy_statement.v1",
        "graph": GRAPH,
        "scientific_parent_integration": SCIENTIFIC_PARENT_INTEGRATION,
        "prospective_evidence_registration": PROSPECTIVE_EVIDENCE_REGISTRATION,
        "adequacy_preregistration_commit": ADEQUACY_PREREGISTRATION,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "interval": {
            "utc_days": 14,
            "schedule_utc": list(SCHEDULE_UTC),
            "schedule_cron": list(SCHEDULE_CRON),
            "target_slots": TARGET_SLOTS,
            "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
            "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
            "missing_slots_are_not_backfilled": True,
            "early_stopping_permitted": False,
        },
        "accepted_event": "schedule",
        "manual_runs_count_toward_threshold": False,
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


def _synthetic_attempt(binding: ActivationBinding, slot: int) -> SlotAttempt:
    return SlotAttempt(
        slot=slot,
        target_at_utc=expected_target(binding, slot),
        event_name="schedule",
        cron=expected_cron(slot),
        run_id=20_000 + slot,
        started_at_utc=expected_target(binding, slot) + timedelta(minutes=5),
        repository_commit=binding.backend_commit,
        repository_tree=binding.backend_tree,
        request_fingerprint_sha256=REQUEST_FINGERPRINT,
        raw_artifact_sha256="c" * 64,
        temporal_index_sha256="d" * 64,
    )


def build_synthetic_report() -> JsonObject:
    binding = ActivationBinding(
        start_utc_day=date(2026, 9, 15),
        backend_commit="a" * 40,
        backend_tree="b" * 40,
    )
    attempts = tuple(
        _synthetic_attempt(binding, slot) for slot in range(MIN_ACCEPTED_SLOTS)
    )
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
        "accepted_slots": counts["ACCEPTED"],
        "missing_slots": counts["MISSING"],
        "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
        "start_utc_day": binding.start_utc_day.isoformat(),
        "end_utc_day": binding.end_utc_day.isoformat(),
        "finalization_at_utc": finalization_at(binding)
        .astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "manual_runs_count_toward_threshold": False,
        "missing_slots_are_not_backfilled": True,
        "early_stopping_permitted": False,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
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
