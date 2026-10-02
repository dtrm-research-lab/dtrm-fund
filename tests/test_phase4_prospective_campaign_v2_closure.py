from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from dtrm.phase4.prospective_campaign_v2_closure import (
    CampaignV2ClosureError,
    validate_decisive_failure,
    validate_files,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "research/evidence/phase4_prospective_campaign_v2_decisive_failure_v1.json"
)
STATEMENT = (
    ROOT
    / "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAMPAIGN_V2_CLOSURE_STATEMENT_V1.json"
)


def _payloads() -> tuple[dict[str, object], dict[str, object], bytes]:
    evidence_bytes = EVIDENCE.read_bytes()
    evidence = json.loads(evidence_bytes)
    statement = json.loads(STATEMENT.read_text(encoding="utf-8"))
    return evidence, statement, evidence_bytes


def _rebind_mutated_evidence(
    evidence: dict[str, object], statement: dict[str, object]
) -> tuple[bytes, dict[str, object]]:
    evidence_bytes = (
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    rebound = copy.deepcopy(statement)
    rebound["decisive_failure_evidence_sha256"] = hashlib.sha256(
        evidence_bytes
    ).hexdigest()
    return evidence_bytes, rebound


def test_committed_closure_is_valid() -> None:
    validate_files(EVIDENCE, STATEMENT)


def test_relaxing_a_late_record_fails_closed() -> None:
    evidence, statement, _ = _payloads()
    mutated = copy.deepcopy(evidence)
    records = mutated["records"]
    assert isinstance(records, list)
    record = records[0]
    assert isinstance(record, dict)
    record["start_lag_microseconds"] = 120 * 60 * 1_000_000
    mutated_bytes, rebound_statement = _rebind_mutated_evidence(mutated, statement)
    with pytest.raises(CampaignV2ClosureError, match="does not prove lateness"):
        validate_decisive_failure(
            mutated, rebound_statement, evidence_bytes=mutated_bytes
        )


def test_threshold_tamper_fails_closed() -> None:
    evidence, statement, _ = _payloads()
    mutated = copy.deepcopy(evidence)
    frozen = mutated["frozen_adequacy_rule"]
    assert isinstance(frozen, dict)
    frozen["minimum_accepted_slots"] = 14
    mutated_bytes, rebound_statement = _rebind_mutated_evidence(mutated, statement)
    with pytest.raises(CampaignV2ClosureError, match="frozen adequacy rule mismatch"):
        validate_decisive_failure(
            mutated, rebound_statement, evidence_bytes=mutated_bytes
        )


def test_statement_must_bind_exact_evidence_digest() -> None:
    evidence, statement, evidence_bytes = _payloads()
    mutated_statement = copy.deepcopy(statement)
    mutated_statement["decisive_failure_evidence_sha256"] = "0" * 64
    assert hashlib.sha256(evidence_bytes).hexdigest() != "0" * 64
    with pytest.raises(CampaignV2ClosureError, match="evidence digest mismatch"):
        validate_decisive_failure(evidence, mutated_statement, evidence_bytes=evidence_bytes)


def test_evidence_object_must_match_bound_bytes() -> None:
    evidence, statement, evidence_bytes = _payloads()
    mutated = copy.deepcopy(evidence)
    mutated["source_kind"] = "tampered"
    with pytest.raises(CampaignV2ClosureError, match="evidence bytes mismatch"):
        validate_decisive_failure(mutated, statement, evidence_bytes=evidence_bytes)


def test_outcome_access_cannot_be_unlocked() -> None:
    evidence, statement, evidence_bytes = _payloads()
    mutated_statement = copy.deepcopy(statement)
    mutated_statement["outcome_access_permitted"] = True
    with pytest.raises(CampaignV2ClosureError, match="forbidden permission enabled"):
        validate_decisive_failure(evidence, mutated_statement, evidence_bytes=evidence_bytes)
