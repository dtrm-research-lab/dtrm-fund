"""Outcome-blind adequacy audit for Phase-IV prospective temporal evidence v1."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Literal

GRAPH = "phase4_prospective_evidence_adequacy_v1"
REPORT_SCHEMA = "dtrm.phase4.prospective_evidence_adequacy_report.v1"
SCIENTIFIC_PARENT_INTEGRATION = "ca7ef0570281f6a1143d7a93efae5d69edc2b8a4"
PROSPECTIVE_EVIDENCE_REGISTRATION = "243797ee398b43f6684ce7a43057711167ed79ba"
ADEQUACY_PREREGISTRATION = "835f5c6f01825abdaf9a3cc266f9ba1dfb24c55d"
REVIEW_AMENDMENT = "44d82ac66d283196d1077b799a012a693f9ead7e"
REQUEST_FINGERPRINT = "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
PROVIDER_RIGHTS_STATUS = "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"

SCHEDULE_UTC = ("00:15", "06:15", "12:15", "18:15")
SCHEDULE_CRON = ("15 0 * * *", "15 6 * * *", "15 12 * * *", "15 18 * * *")
TARGET_SLOTS = 56
MIN_ACCEPTED_SLOTS = 48
MIN_FIRST_DAY_ACCEPTED_SLOTS = 1
MIN_LAST_DAY_ACCEPTED_SLOTS = 1
MAX_SCHEDULE_LAG_MINUTES = 120
MAX_RUN_DURATION_MINUTES = 60
MAX_COMPLETION_LAG_MINUTES = 180

SlotStatus = Literal[
    "ACCEPTED",
    "MISSING",
    "FAILED",
    "LATE",
    "DUPLICATE",
    "CONTRACT_MISMATCH",
]
FinalStatus = Literal[
    "PENDING_INTERVAL",
    "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1",
    "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1",
]

_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ERROR_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")


class ProspectiveEvidenceAdequacyError(ValueError):
    """The metadata-only adequacy contract or evidence ledger is invalid."""


def _require_sha40(value: str, label: str) -> None:
    if _SHA40_RE.fullmatch(value) is None:
        raise ProspectiveEvidenceAdequacyError(f"{label}: invalid sha")


def _require_sha256(value: str, label: str) -> None:
    if _SHA256_RE.fullmatch(value) is None:
        raise ProspectiveEvidenceAdequacyError(f"{label}: invalid sha256")


def _require_utc(value: datetime, label: str) -> None:
    if value.utcoffset() != timedelta(0):
        raise ProspectiveEvidenceAdequacyError(f"{label}: expected UTC clock")


def _timestamp(value: datetime) -> str:
    _require_utc(value, "timestamp")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _require_identifier(value: str, label: str) -> None:
    if (
        not value
        or len(value) > 256
        or any(character in value for character in "\r\n\t")
    ):
        raise ProspectiveEvidenceAdequacyError(f"{label}: invalid identifier")


@dataclass(frozen=True, slots=True)
class ActivationBinding:
    """Exact source-value-free lineage fixed by the later activation statement."""

    activation_statement: str
    activation_statement_sha256: str
    start_utc_day: date
    backend_commit: str
    backend_tree: str

    def __post_init__(self) -> None:
        _require_identifier(self.activation_statement, "binding.activation_statement")
        _require_sha256(
            self.activation_statement_sha256,
            "binding.activation_statement_sha256",
        )
        if isinstance(self.start_utc_day, datetime):
            raise ProspectiveEvidenceAdequacyError("binding: expected UTC date")
        _require_sha40(self.backend_commit, "binding.backend_commit")
        _require_sha40(self.backend_tree, "binding.backend_tree")

    @property
    def end_utc_day(self) -> date:
        return self.start_utc_day + timedelta(days=13)


@dataclass(frozen=True, slots=True)
class SlotAttempt:
    """One source-value-free workflow attempt offered to the adequacy audit."""

    slot: int
    target_at_utc: datetime
    event_name: str
    cron: str | None
    run_id: int
    started_at_utc: datetime
    completed_at_utc: datetime
    repository_commit: str
    repository_tree: str
    request_fingerprint_sha256: str
    raw_artifact_sha256: str | None
    temporal_index_sha256: str | None
    failure_code: str | None = None

    def __post_init__(self) -> None:
        if type(self.slot) is not int or not 0 <= self.slot < TARGET_SLOTS:
            raise ProspectiveEvidenceAdequacyError("attempt: invalid slot")
        if not self.event_name:
            raise ProspectiveEvidenceAdequacyError("attempt: missing event")
        if type(self.run_id) is not int or self.run_id <= 0:
            raise ProspectiveEvidenceAdequacyError("attempt: invalid run id")
        _require_utc(self.target_at_utc, "attempt.target_at_utc")
        _require_utc(self.started_at_utc, "attempt.started_at_utc")
        _require_utc(self.completed_at_utc, "attempt.completed_at_utc")
        _require_sha40(self.repository_commit, "attempt.repository_commit")
        _require_sha40(self.repository_tree, "attempt.repository_tree")
        _require_sha256(self.request_fingerprint_sha256, "attempt.request_fingerprint")
        for label, digest in (
            ("attempt.raw_artifact", self.raw_artifact_sha256),
            ("attempt.temporal_index", self.temporal_index_sha256),
        ):
            if digest is not None:
                _require_sha256(digest, label)
        if (
            self.failure_code is not None
            and _ERROR_RE.fullmatch(self.failure_code) is None
        ):
            raise ProspectiveEvidenceAdequacyError("attempt: invalid failure code")


@dataclass(frozen=True, slots=True)
class SlotAssessment:
    slot: int
    target_at_utc: datetime
    status: SlotStatus
    run_id: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "slot": self.slot,
            "target_at_utc": _timestamp(self.target_at_utc),
            "status": self.status,
            "run_id": self.run_id,
        }


def expected_target(binding: ActivationBinding, slot: int) -> datetime:
    if type(slot) is not int or not 0 <= slot < TARGET_SLOTS:
        raise ProspectiveEvidenceAdequacyError("target: invalid slot")
    day_offset, clock_index = divmod(slot, len(SCHEDULE_UTC))
    hour_text, minute_text = SCHEDULE_UTC[clock_index].split(":")
    clock = time(int(hour_text), int(minute_text), tzinfo=UTC)
    return datetime.combine(binding.start_utc_day + timedelta(days=day_offset), clock)


def expected_cron(slot: int) -> str:
    if type(slot) is not int or not 0 <= slot < TARGET_SLOTS:
        raise ProspectiveEvidenceAdequacyError("cron: invalid slot")
    return SCHEDULE_CRON[slot % len(SCHEDULE_CRON)]


def finalization_at(binding: ActivationBinding) -> datetime:
    return expected_target(binding, TARGET_SLOTS - 1) + timedelta(
        minutes=MAX_COMPLETION_LAG_MINUTES
    )


def _classify_slot(
    *,
    binding: ActivationBinding,
    slot: int,
    attempts: tuple[SlotAttempt, ...],
    duplicate_run_ids: frozenset[int],
) -> SlotAssessment:
    target = expected_target(binding, slot)
    scheduled = tuple(item for item in attempts if item.event_name == "schedule")
    if not scheduled:
        return SlotAssessment(slot, target, "MISSING", None)
    if len(scheduled) != 1:
        return SlotAssessment(slot, target, "DUPLICATE", None)

    attempt = scheduled[0]
    if attempt.run_id in duplicate_run_ids:
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    if attempt.target_at_utc != target or attempt.cron != expected_cron(slot):
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    start_lag = attempt.started_at_utc - target
    if start_lag < timedelta(0):
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    if start_lag > timedelta(minutes=MAX_SCHEDULE_LAG_MINUTES):
        return SlotAssessment(slot, target, "LATE", attempt.run_id)
    run_duration = attempt.completed_at_utc - attempt.started_at_utc
    completion_lag = attempt.completed_at_utc - target
    if run_duration < timedelta(0):
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    if run_duration > timedelta(
        minutes=MAX_RUN_DURATION_MINUTES
    ) or completion_lag > timedelta(minutes=MAX_COMPLETION_LAG_MINUTES):
        return SlotAssessment(slot, target, "LATE", attempt.run_id)
    if (
        attempt.repository_commit != binding.backend_commit
        or attempt.repository_tree != binding.backend_tree
        or attempt.request_fingerprint_sha256 != REQUEST_FINGERPRINT
    ):
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    if attempt.failure_code is not None:
        return SlotAssessment(slot, target, "FAILED", attempt.run_id)
    if attempt.raw_artifact_sha256 is None or attempt.temporal_index_sha256 is None:
        return SlotAssessment(slot, target, "CONTRACT_MISMATCH", attempt.run_id)
    return SlotAssessment(slot, target, "ACCEPTED", attempt.run_id)


def audit_evidence(
    binding: ActivationBinding,
    attempts: tuple[SlotAttempt, ...],
    audit_clock_utc: datetime,
) -> dict[str, object]:
    """Classify all 56 registered slots without reading provider values or outcomes."""

    _require_utc(audit_clock_utc, "audit_clock_utc")
    by_slot: dict[int, list[SlotAttempt]] = {slot: [] for slot in range(TARGET_SLOTS)}
    scheduled_run_counts: dict[int, int] = {}
    ignored_nonscheduled = 0
    for attempt in attempts:
        by_slot[attempt.slot].append(attempt)
        if attempt.event_name == "schedule":
            scheduled_run_counts[attempt.run_id] = (
                scheduled_run_counts.get(attempt.run_id, 0) + 1
            )
        else:
            ignored_nonscheduled += 1
    duplicate_run_ids = frozenset(
        run_id for run_id, count in scheduled_run_counts.items() if count > 1
    )

    assessments = tuple(
        _classify_slot(
            binding=binding,
            slot=slot,
            attempts=tuple(by_slot[slot]),
            duplicate_run_ids=duplicate_run_ids,
        )
        for slot in range(TARGET_SLOTS)
    )
    counts: dict[str, int] = {
        status: sum(item.status == status for item in assessments)
        for status in (
            "ACCEPTED",
            "MISSING",
            "FAILED",
            "LATE",
            "DUPLICATE",
            "CONTRACT_MISMATCH",
        )
    }
    accepted = counts["ACCEPTED"]
    first_day_accepted = sum(
        item.status == "ACCEPTED" for item in assessments[: len(SCHEDULE_UTC)]
    )
    last_day_accepted = sum(
        item.status == "ACCEPTED" for item in assessments[-len(SCHEDULE_UTC) :]
    )
    finalize_at = finalization_at(binding)
    final_status: FinalStatus
    if audit_clock_utc < finalize_at:
        final_status = "PENDING_INTERVAL"
    elif (
        accepted >= MIN_ACCEPTED_SLOTS
        and first_day_accepted >= MIN_FIRST_DAY_ACCEPTED_SLOTS
        and last_day_accepted >= MIN_LAST_DAY_ACCEPTED_SLOTS
    ):
        final_status = "PASS_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    else:
        final_status = "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"

    return {
        "schema_version": REPORT_SCHEMA,
        "graph": GRAPH,
        "scientific_parent_integration": SCIENTIFIC_PARENT_INTEGRATION,
        "prospective_evidence_registration": PROSPECTIVE_EVIDENCE_REGISTRATION,
        "adequacy_preregistration_commit": ADEQUACY_PREREGISTRATION,
        "review_amendment_commit": REVIEW_AMENDMENT,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        "activation_statement": binding.activation_statement,
        "activation_statement_sha256": binding.activation_statement_sha256,
        "start_utc_day": binding.start_utc_day.isoformat(),
        "end_utc_day": binding.end_utc_day.isoformat(),
        "backend_commit": binding.backend_commit,
        "backend_tree": binding.backend_tree,
        "target_slots": TARGET_SLOTS,
        "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
        "minimum_first_day_accepted_slots": MIN_FIRST_DAY_ACCEPTED_SLOTS,
        "minimum_last_day_accepted_slots": MIN_LAST_DAY_ACCEPTED_SLOTS,
        "first_day_accepted_slots": first_day_accepted,
        "last_day_accepted_slots": last_day_accepted,
        "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
        "maximum_run_duration_minutes": MAX_RUN_DURATION_MINUTES,
        "maximum_completion_lag_minutes": MAX_COMPLETION_LAG_MINUTES,
        "finalization_at_utc": _timestamp(finalize_at),
        "audit_clock_utc": _timestamp(audit_clock_utc),
        "ignored_nonscheduled_attempts": ignored_nonscheduled,
        "counts": counts,
        "final_status": final_status,
        "slots": [item.to_dict() for item in assessments],
        "confirmatory_history_construction_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
        "public_raw_provider_data_redistribution_permitted": False,
    }


def canonical_audit_json(
    binding: ActivationBinding,
    attempts: tuple[SlotAttempt, ...],
    audit_clock_utc: datetime,
) -> str:
    return (
        json.dumps(
            audit_evidence(binding, attempts, audit_clock_utc),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
