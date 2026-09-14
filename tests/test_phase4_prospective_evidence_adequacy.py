from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import date, datetime, timedelta
from typing import cast

import pytest

from dtrm.phase4.prospective_evidence_adequacy import (
    ACTIVATION_SCHEMA,
    MAX_COMPLETION_LAG_MINUTES,
    MAX_RECORD_PUBLICATION_LAG_MINUTES,
    MAX_SCHEDULE_LAG_MINUTES,
    MIN_ACCEPTED_SLOTS,
    REQUEST_FINGERPRINT,
    TARGET_SLOTS,
    ActivationBinding,
    ProspectiveEvidenceAdequacyError,
    SlotAttempt,
    audit_evidence,
    expected_cron,
    expected_target,
    finalization_at,
)

_COMMIT = "a" * 40
_TREE = "b" * 40
_RAW = "c" * 64
_INDEX = "d" * 64
_ACTIVATION_ID = "synthetic-activation-v1"
_START_DAY = "2026-09-15"


def _activation_bytes(**overrides: object) -> bytes:
    payload: dict[str, object] = {
        "schema_version": ACTIVATION_SCHEMA,
        "activation_statement": _ACTIVATION_ID,
        "start_utc_day": _START_DAY,
        "backend_commit": _COMMIT,
        "backend_tree": _TREE,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "periodic_capture_activation_permitted": True,
    }
    payload.update(overrides)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _binding() -> ActivationBinding:
    statement = _activation_bytes()
    return ActivationBinding(
        statement_bytes=statement,
        trusted_activation_statement=_ACTIVATION_ID,
        trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
    )


def _attempt(
    binding: ActivationBinding,
    base_slot: int,
    **overrides: object,
) -> SlotAttempt:
    target = expected_target(binding, base_slot)
    values: dict[str, object] = {
        "slot": base_slot,
        "target_at_utc": target,
        "event_name": "schedule",
        "cron": expected_cron(base_slot),
        "run_id": 10_000 + base_slot,
        "run_attempt": 1,
        "started_at_utc": target + timedelta(minutes=5),
        "completed_at_utc": target + timedelta(minutes=10),
        "recorded_at_utc": target + timedelta(minutes=11),
        "repository_commit": binding.backend_commit,
        "repository_tree": binding.backend_tree,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "raw_artifact_sha256": _RAW,
        "temporal_index_sha256": _INDEX,
        "failure_code": None,
    }
    values.update(overrides)
    return SlotAttempt(
        slot=cast(int | None, values["slot"]),
        target_at_utc=cast(datetime | None, values["target_at_utc"]),
        event_name=cast(str, values["event_name"]),
        cron=cast(str | None, values["cron"]),
        run_id=cast(int, values["run_id"]),
        run_attempt=cast(int, values["run_attempt"]),
        started_at_utc=cast(datetime, values["started_at_utc"]),
        completed_at_utc=cast(datetime, values["completed_at_utc"]),
        recorded_at_utc=cast(datetime, values["recorded_at_utc"]),
        repository_commit=cast(str, values["repository_commit"]),
        repository_tree=cast(str, values["repository_tree"]),
        request_fingerprint_sha256=cast(str, values["request_fingerprint_sha256"]),
        raw_artifact_sha256=cast(str | None, values["raw_artifact_sha256"]),
        temporal_index_sha256=cast(str | None, values["temporal_index_sha256"]),
        failure_code=cast(str | None, values["failure_code"]),
    )


def _attempts_for_slots(
    binding: ActivationBinding,
    slots: tuple[int, ...],
) -> tuple[SlotAttempt, ...]:
    return tuple(_attempt(binding, slot) for slot in slots)


def _all_attempts(binding: ActivationBinding) -> tuple[SlotAttempt, ...]:
    return _attempts_for_slots(binding, tuple(range(TARGET_SLOTS)))


def _passing_48(binding: ActivationBinding) -> tuple[SlotAttempt, ...]:
    slots = tuple(range(MIN_ACCEPTED_SLOTS - 1)) + (TARGET_SLOTS - 1,)
    return _attempts_for_slots(binding, slots)


def _failing_47_with_boundaries(binding: ActivationBinding) -> tuple[SlotAttempt, ...]:
    slots = tuple(range(MIN_ACCEPTED_SLOTS - 2)) + (TARGET_SLOTS - 1,)
    return _attempts_for_slots(binding, slots)


def _final_clock(binding: ActivationBinding) -> datetime:
    return finalization_at(binding) + timedelta(seconds=1)


def _counts(report: dict[str, object]) -> dict[str, int]:
    return cast(dict[str, int], report["counts"])


def test_activation_binding_is_derived_from_verified_exact_bytes() -> None:
    binding = _binding()
    assert binding.activation_statement == _ACTIVATION_ID
    assert binding.start_utc_day == date(2026, 9, 15)
    assert binding.backend_commit == _COMMIT
    assert binding.backend_tree == _TREE
    assert (
        binding.activation_statement_sha256
        == hashlib.sha256(_activation_bytes()).hexdigest()
    )


def test_activation_bytes_wrong_trusted_digest_fail_closed() -> None:
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="digest mismatch"):
        ActivationBinding(
            statement_bytes=_activation_bytes(),
            trusted_activation_statement=_ACTIVATION_ID,
            trusted_activation_statement_sha256="0" * 64,
        )


def test_activation_bytes_wrong_trusted_identifier_fail_closed() -> None:
    statement = _activation_bytes()
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="identifier mismatch"):
        ActivationBinding(
            statement_bytes=statement,
            trusted_activation_statement="different-approved-statement",
            trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
        )


def test_activation_schema_extra_key_fails_closed() -> None:
    statement = _activation_bytes(unregistered="value")
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="schema mismatch"):
        ActivationBinding(
            statement_bytes=statement,
            trusted_activation_statement=_ACTIVATION_ID,
            trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
        )


def test_all_56_slots_pass_after_finalization() -> None:
    binding = _binding()
    report = audit_evidence(binding, _all_attempts(binding), _final_clock(binding))
    assert report["final_status"] == "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 56
    assert _counts(report)["MISSING"] == 0


def test_exactly_48_slots_pass_with_both_boundary_days() -> None:
    binding = _binding()
    report = audit_evidence(binding, _passing_48(binding), _final_clock(binding))
    assert report["final_status"] == "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 48
    assert _counts(report)["MISSING"] == 8
    assert report["first_day_accepted_slots"] == 4
    assert report["last_day_accepted_slots"] == 1


def test_48_slots_without_first_day_fail_after_finalization() -> None:
    binding = _binding()
    slots = tuple(range(4, 51)) + (55,)
    report = audit_evidence(
        binding,
        _attempts_for_slots(binding, slots),
        _final_clock(binding),
    )
    assert _counts(report)["ACCEPTED"] == 48
    assert report["first_day_accepted_slots"] == 0
    assert report["last_day_accepted_slots"] == 1
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"


def test_48_slots_without_last_day_fail_after_finalization() -> None:
    binding = _binding()
    report = audit_evidence(
        binding,
        _attempts_for_slots(binding, tuple(range(MIN_ACCEPTED_SLOTS))),
        _final_clock(binding),
    )
    assert _counts(report)["ACCEPTED"] == 48
    assert report["first_day_accepted_slots"] == 4
    assert report["last_day_accepted_slots"] == 0
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"


def test_47_slots_fail_even_with_boundary_days() -> None:
    binding = _binding()
    report = audit_evidence(
        binding,
        _failing_47_with_boundaries(binding),
        _final_clock(binding),
    )
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 47


def test_no_early_pass_before_publication_deadline() -> None:
    binding = _binding()
    report = audit_evidence(
        binding,
        _all_attempts(binding),
        finalization_at(binding) - timedelta(seconds=1),
    )
    assert report["final_status"] == "PENDING_INTERVAL"
    assert _counts(report)["ACCEPTED"] == 56


def test_old_start_and_completion_deadlines_are_still_pending() -> None:
    binding = _binding()
    target = expected_target(binding, TARGET_SLOTS - 1)
    for deadline in (
        target + timedelta(minutes=MAX_SCHEDULE_LAG_MINUTES),
        target + timedelta(minutes=MAX_COMPLETION_LAG_MINUTES),
    ):
        report = audit_evidence(binding, _all_attempts(binding), deadline)
        assert report["final_status"] == "PENDING_INTERVAL"


def test_manual_run_never_counts_toward_threshold() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    attempts[0] = replace(
        attempts[0],
        slot=None,
        target_at_utc=None,
        event_name="workflow_dispatch",
        cron=None,
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["ACCEPTED"] == 55
    assert _counts(report)["MISSING"] == 1
    assert report["ignored_nonscheduled_attempts"] == 1


def test_scheduled_rerun_never_counts_or_backfills() -> None:
    binding = _binding()
    attempts = _failing_47_with_boundaries(binding)
    target = expected_target(binding, 46)
    rerun = _attempt(
        binding,
        46,
        slot=None,
        target_at_utc=None,
        run_id=88_888,
        run_attempt=2,
        started_at_utc=target + timedelta(minutes=5),
        completed_at_utc=target + timedelta(minutes=10),
        recorded_at_utc=target + timedelta(minutes=11),
    )
    report = audit_evidence(binding, attempts + (rerun,), _final_clock(binding))
    assert _counts(report)["ACCEPTED"] == 47
    assert report["ignored_scheduled_reruns"] == 1
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"


def test_start_after_120_minutes_is_late() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 0)
    attempts[0] = replace(
        attempts[0],
        started_at_utc=target + timedelta(minutes=121),
        completed_at_utc=target + timedelta(minutes=130),
        recorded_at_utc=target + timedelta(minutes=131),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["LATE"] == 1
    assert _counts(report)["ACCEPTED"] == 55


def test_latest_start_completion_and_publication_are_accepted() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 55)
    attempts[55] = replace(
        attempts[55],
        started_at_utc=target + timedelta(minutes=120),
        completed_at_utc=target + timedelta(minutes=180),
        recorded_at_utc=target + timedelta(minutes=240),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["ACCEPTED"] == 56
    assert report["final_status"] == "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"


def test_record_after_publication_deadline_is_late() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 55)
    attempts[55] = replace(
        attempts[55],
        started_at_utc=target + timedelta(minutes=120),
        completed_at_utc=target + timedelta(minutes=180),
        recorded_at_utc=target + timedelta(minutes=241),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["LATE"] == 1
    assert _counts(report)["ACCEPTED"] == 55


def test_late_record_cannot_flip_final_fail_to_pass() -> None:
    binding = _binding()
    base = _failing_47_with_boundaries(binding)
    first_report = audit_evidence(binding, base, _final_clock(binding))
    assert first_report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    target = expected_target(binding, 46)
    late = _attempt(
        binding,
        46,
        started_at_utc=target + timedelta(minutes=120),
        completed_at_utc=target + timedelta(minutes=180),
        recorded_at_utc=target + timedelta(minutes=241),
    )
    later_report = audit_evidence(binding, base + (late,), _final_clock(binding))
    assert _counts(later_report)["ACCEPTED"] == 47
    assert _counts(later_report)["LATE"] == 1
    assert later_report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"


def test_run_over_60_minutes_is_late() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 0)
    attempts[0] = replace(
        attempts[0],
        started_at_utc=target + timedelta(minutes=120),
        completed_at_utc=target + timedelta(minutes=181),
        recorded_at_utc=target + timedelta(minutes=182),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["LATE"] == 1


def test_completion_before_start_is_contract_mismatch() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 0)
    attempts[0] = replace(
        attempts[0],
        started_at_utc=target + timedelta(minutes=5),
        completed_at_utc=target + timedelta(minutes=4),
        recorded_at_utc=target + timedelta(minutes=6),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 1


def test_record_before_completion_is_contract_mismatch() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    target = expected_target(binding, 0)
    attempts[0] = replace(
        attempts[0],
        completed_at_utc=target + timedelta(minutes=10),
        recorded_at_utc=target + timedelta(minutes=9),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 1


def test_failed_attempt_is_not_accepted() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    attempts[0] = replace(
        attempts[0],
        failure_code="INVALID_SOURCE_ARTIFACT",
        raw_artifact_sha256=None,
        temporal_index_sha256=None,
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["FAILED"] == 1


def test_duplicate_slot_is_not_counted_twice() -> None:
    binding = _binding()
    attempts = _all_attempts(binding) + (replace(_attempt(binding, 0), run_id=99_999),)
    report = audit_evidence(binding, attempts, _final_clock(binding))
    assert _counts(report)["DUPLICATE"] == 1
    assert _counts(report)["ACCEPTED"] == 55


def test_wrong_lineage_and_request_fingerprint_fail_closed() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    attempts[0] = replace(attempts[0], repository_commit="e" * 40)
    attempts[1] = replace(attempts[1], request_fingerprint_sha256="f" * 64)
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 2


def test_duplicate_run_id_across_first_attempt_slots_fails_closed() -> None:
    binding = _binding()
    attempts = list(_all_attempts(binding))
    attempts[1] = replace(attempts[1], run_id=attempts[0].run_id)
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 2
    assert _counts(report)["ACCEPTED"] == 54


def test_malformed_digest_is_rejected_before_audit() -> None:
    binding = _binding()
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="invalid sha256"):
        _attempt(binding, 0, raw_artifact_sha256="not-a-digest")


def test_invalid_run_attempt_is_rejected_before_audit() -> None:
    binding = _binding()
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="invalid run attempt"):
        _attempt(binding, 0, run_attempt=0)


def test_pass_report_preserves_all_downstream_prohibitions() -> None:
    binding = _binding()
    report = audit_evidence(binding, _passing_48(binding), _final_clock(binding))
    assert report["confirmatory_history_construction_permitted"] is False
    assert report["temporal_state_outcome_fitting_permitted"] is False
    assert report["outcome_access_permitted"] is False
    assert report["mm1_execution_permitted"] is False
    assert report["phase3_policy_mutation_permitted"] is False
    assert report["public_raw_provider_data_redistribution_permitted"] is False
    assert (
        report["maximum_record_publication_lag_minutes"]
        == MAX_RECORD_PUBLICATION_LAG_MINUTES
    )


def test_binding_end_day_is_exactly_14_utc_days_inclusive() -> None:
    binding = _binding()
    assert binding.end_utc_day == date(2026, 9, 28)
    assert expected_target(binding, 0).isoformat() == "2026-09-15T00:15:00+00:00"
    assert expected_target(binding, 55).isoformat() == "2026-09-28T18:15:00+00:00"
    assert finalization_at(binding).isoformat() == "2026-09-28T22:15:00+00:00"
