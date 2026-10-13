"""Synthetic evidence that v3 transport must not be counted by the v1 auditor.

This file does NOT validate a v3 campaign or authorize FMP, outcomes or MM1.
"""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import pytest

from dtrm.phase4.prospective_evidence_adequacy import (
    ACTIVATION_SCHEMA,
    PROVIDER_ROLES,
    REQUEST_FINGERPRINT,
    ActivationBinding,
    ProspectiveEvidenceAdequacyError,
    SlotAttempt,
    audit_evidence,
    expected_target,
    finalization_at,
)

_ID = "synthetic-noncounting-v3-transport"
_START = "2026-11-01T00:00:00Z"
_SOURCE_SHA = "c" * 64
_INDEX_SHA = "d" * 64


def _binding() -> ActivationBinding:
    statement = json.dumps(
        {
            "schema_version": ACTIVATION_SCHEMA,
            "activation_statement": _ID,
            "backend_commit": "a" * 40,
            "backend_tree": "b" * 40,
            "workflow_path": ".github/workflows/phase4-prospective-temporal-evidence-v1.yml",
            "workflow_blob_sha": "e" * 40,
            "workflow_identity": "phase4-prospective-temporal-evidence-v1",
            "provider_roles": list(PROVIDER_ROLES),
            "request_fingerprint_sha256": REQUEST_FINGERPRINT,
            "provisioned_schema_identity": "synthetic-temporal-schema",
            "credential_scope_status": "AUTHORIZED",
            "credential_scope_evidence_sha256": "f" * 64,
            "writer_authority_status": "AUTHORIZED",
            "writer_authority_evidence_sha256": "1" * 64,
            "prospective_start_utc": _START,
            "periodic_capture_activation_permitted": True,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return ActivationBinding(
        statement_bytes=statement,
        trusted_activation_statement=_ID,
        trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
    )


def _diagnostic_attempt(binding: ActivationBinding) -> SlotAttempt:
    target = expected_target(binding, 0)
    return SlotAttempt(
        slot=None,
        target_at_utc=None,
        event_name="repository_dispatch",
        cron=None,
        workflow_path=None,
        workflow_blob_sha=None,
        workflow_identity=None,
        run_id=10001,
        run_attempt=1,
        started_at_utc=target + timedelta(seconds=17),
        completed_at_utc=target + timedelta(seconds=30),
        recorded_at_utc=target + timedelta(seconds=31),
        repository_commit=binding.backend_commit,
        repository_tree=binding.backend_tree,
        request_fingerprint_sha256=REQUEST_FINGERPRINT,
        raw_artifact_sha256=_SOURCE_SHA,
        temporal_index_sha256=_INDEX_SHA,
    )


def test_v3_repository_dispatch_is_noncounting_under_unmodified_v1_auditor() -> None:
    binding = _binding()
    diagnostic = _diagnostic_attempt(binding)
    after_window = finalization_at(binding) + timedelta(seconds=1)
    report = audit_evidence(binding, (diagnostic,), after_window)
    assert report["ignored_nonscheduled_attempts"] == 1
    assert report["counts"]["ACCEPTED"] == 0
    assert report["counts"]["MISSING"] == 56
    assert report["final_status"] == "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
    assert report["minimum_accepted_slots"] == 48
    assert report["minimum_first_day_accepted_slots"] == 1
    assert report["minimum_last_day_accepted_slots"] == 1
    for flag in (
        "confirmatory_history_construction_permitted",
        "temporal_state_outcome_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "phase3_policy_mutation_permitted",
        "public_raw_provider_data_redistribution_permitted",
    ):
        assert report[flag] is False


def test_v3_diagnostic_does_not_close_interval_early() -> None:
    binding = _binding()
    diagnostic = _diagnostic_attempt(binding)
    pending = audit_evidence(binding, (diagnostic,), finalization_at(binding))
    assert pending["final_status"] == "PENDING_INTERVAL"
    assert pending["ignored_nonscheduled_attempts"] == 1


def test_v3_dispatch_cannot_smuggle_target_fields_into_v1_slot() -> None:
    binding = _binding()
    diagnostic = _diagnostic_attempt(binding)
    target = expected_target(binding, 0)
    with pytest.raises(
        ProspectiveEvidenceAdequacyError, match="non-counting target mismatch"
    ):
        SlotAttempt(
            slot=0,
            target_at_utc=target,
            event_name=diagnostic.event_name,
            cron=None,
            workflow_path=None,
            workflow_blob_sha=None,
            workflow_identity=None,
            run_id=diagnostic.run_id,
            run_attempt=diagnostic.run_attempt,
            started_at_utc=diagnostic.started_at_utc,
            completed_at_utc=diagnostic.completed_at_utc,
            recorded_at_utc=diagnostic.recorded_at_utc,
            repository_commit=diagnostic.repository_commit,
            repository_tree=diagnostic.repository_tree,
            request_fingerprint_sha256=diagnostic.request_fingerprint_sha256,
            raw_artifact_sha256=diagnostic.raw_artifact_sha256,
            temporal_index_sha256=diagnostic.temporal_index_sha256,
        )
