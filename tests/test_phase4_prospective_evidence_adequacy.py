from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta
from typing import cast

import pytest

from dtrm.phase4.prospective_evidence_adequacy import (
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


def _binding() -> ActivationBinding:
    return ActivationBinding(
        start_utc_day=date(2026, 9, 15),
        backend_commit=_COMMIT,
        backend_tree=_TREE,
    )


def _attempt(binding: ActivationBinding, slot: int, **overrides: object) -> SlotAttempt:
    values: dict[str, object] = {
        "slot": slot,
        "target_at_utc": expected_target(binding, slot),
        "event_name": "schedule",
        "cron": expected_cron(slot),
        "run_id": 10_000 + slot,
        "started_at_utc": expected_target(binding, slot) + timedelta(minutes=5),
        "repository_commit": binding.backend_commit,
        "repository_tree": binding.backend_tree,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "raw_artifact_sha256": _RAW,
        "temporal_index_sha256": _INDEX,
        "failure_code": None,
    }
    values.update(overrides)
    return SlotAttempt(
        slot=cast(int, values["slot"]),
        target_at_utc=cast(datetime, values["target_at_utc"]),
        event_name=cast(str, values["event_name"]),
        cron=cast(str | None, values["cron"]),
        run_id=cast(int, values["run_id"]),
        started_at_utc=cast(datetime, values["started_at_utc"]),
        repository_commit=cast(str, values["repository_commit"]),
        repository_tree=cast(str, values["repository_tree"]),
        request_fingerprint_sha256=cast(str, values["request_fingerprint_sha256"]),
        raw_artifact_sha256=cast(str | None, values["raw_artifact_sha256"]),
        temporal_index_sha256=cast(str | None, values["temporal_index_sha256"]),
        failure_code=cast(str | None, values["failure_code"]),
    )


def _attempts(
    binding: ActivationBinding,
    count: int = TARGET_SLOTS,
) -> tuple[SlotAttempt, ...]:
    return tuple(_attempt(binding, slot) for slot in range(count))


def _final_clock(binding: ActivationBinding) -> datetime:
    return finalization_at(binding) + timedelta(seconds=1)


def _counts(report: dict[str, object]) -> dict[str, int]:
    return cast(dict[str, int], report["counts"])


def test_all_56_slots_pass_after_finalization() -> None:
    binding = _binding()
    report = audit_evidence(binding, _attempts(binding), _final_clock(binding))
    assert report["final_status"] == "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 56
    assert _counts(report)["MISSING"] == 0


def test_exactly_48_slots_pass_without_backfill() -> None:
    binding = _binding()
    report = audit_evidence(
        binding, _attempts(binding, MIN_ACCEPTED_SLOTS), _final_clock(binding)
    )
    assert report["final_status"] == "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 48
    assert _counts(report)["MISSING"] == 8


def test_47_slots_fail_after_finalization() -> None:
    binding = _binding()
    report = audit_evidence(
        binding, _attempts(binding, MIN_ACCEPTED_SLOTS - 1), _final_clock(binding)
    )
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert _counts(report)["ACCEPTED"] == 47


def test_no_early_pass_before_finalization_clock() -> None:
    binding = _binding()
    report = audit_evidence(
        binding,
        _attempts(binding),
        finalization_at(binding) - timedelta(seconds=1),
    )
    assert report["final_status"] == "PENDING_INTERVAL"
    assert _counts(report)["ACCEPTED"] == 56


def test_manual_run_never_counts_toward_threshold() -> None:
    binding = _binding()
    attempts = list(_attempts(binding))
    attempts[0] = replace(attempts[0], event_name="workflow_dispatch", cron=None)
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["ACCEPTED"] == 55
    assert _counts(report)["MISSING"] == 1
    assert report["ignored_nonscheduled_attempts"] == 1


def test_late_attempt_is_not_accepted() -> None:
    binding = _binding()
    attempts = list(_attempts(binding))
    attempts[0] = replace(
        attempts[0],
        started_at_utc=expected_target(binding, 0) + timedelta(minutes=121),
    )
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["LATE"] == 1
    assert _counts(report)["ACCEPTED"] == 55


def test_failed_attempt_is_not_accepted() -> None:
    binding = _binding()
    attempts = list(_attempts(binding))
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
    attempts = _attempts(binding) + (replace(_attempt(binding, 0), run_id=99_999),)
    report = audit_evidence(binding, attempts, _final_clock(binding))
    assert _counts(report)["DUPLICATE"] == 1
    assert _counts(report)["ACCEPTED"] == 55


def test_wrong_lineage_and_request_fingerprint_fail_closed() -> None:
    binding = _binding()
    attempts = list(_attempts(binding))
    attempts[0] = replace(attempts[0], repository_commit="e" * 40)
    attempts[1] = replace(attempts[1], request_fingerprint_sha256="f" * 64)
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 2


def test_duplicate_run_id_across_slots_fails_closed() -> None:
    binding = _binding()
    attempts = list(_attempts(binding))
    attempts[1] = replace(attempts[1], run_id=attempts[0].run_id)
    report = audit_evidence(binding, tuple(attempts), _final_clock(binding))
    assert _counts(report)["CONTRACT_MISMATCH"] == 2
    assert _counts(report)["ACCEPTED"] == 54


def test_malformed_digest_is_rejected_before_audit() -> None:
    binding = _binding()
    with pytest.raises(ProspectiveEvidenceAdequacyError, match="invalid sha256"):
        _attempt(binding, 0, raw_artifact_sha256="not-a-digest")


def test_binding_end_day_is_exactly_14_utc_days_inclusive() -> None:
    binding = _binding()
    assert binding.end_utc_day == date(2026, 9, 28)
    assert expected_target(binding, 0).isoformat() == "2026-09-15T00:15:00+00:00"
    assert expected_target(binding, 55).isoformat() == "2026-09-28T18:15:00+00:00"
    assert finalization_at(binding).isoformat() == "2026-09-28T20:15:00+00:00"
