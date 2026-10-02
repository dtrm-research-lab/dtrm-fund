"""Outcome-blind decisive closure proof for Phase-IV campaign v2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

TARGET_SLOTS = 56
MIN_ACCEPTED_SLOTS = 48
MAX_SCHEDULE_LAG_MINUTES = 120
MAX_SCHEDULE_LAG_MICROSECONDS = MAX_SCHEDULE_LAG_MINUTES * 60 * 1_000_000
EXPECTED_FINAL_STATUS = "FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1"
EXPECTED_ACTIVATION = "phase4-prospective-capture-2026-09-18-v2"
EXPECTED_ACTIVATION_SHA256 = (
    "5625b8930f5c6aefd9aa6193c5211c74ec61d96a4d88ea72307c42bbe654dbd5"
)
EXPECTED_WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v1.yml"
EXPECTED_WORKFLOW_BLOB = "a79ec00ec5761f5fb8cc8a6c017be8bbe7eb75c3"
EXPECTED_WORKFLOW_IDENTITY = "phase4_fmp_news_temporal_capture_v1"
EXPECTED_REPOSITORY_COMMIT = "bf844932f8bb3e6773c329a45135fd754c6d8342"
EXPECTED_REPOSITORY_TREE = "c090c3cb41165ee513de812dec562f497407df62"
EXPECTED_REQUEST_FINGERPRINT = (
    "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
)


class CampaignV2ClosureError(ValueError):
    """Closure evidence or statement does not prove the frozen failure."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CampaignV2ClosureError("expected object")
    return value


def validate_decisive_failure(
    evidence: dict[str, Any],
    statement: dict[str, Any],
    *,
    evidence_bytes: bytes,
) -> None:
    if evidence.get("campaign_activation_statement") != EXPECTED_ACTIVATION:
        raise CampaignV2ClosureError("activation mismatch")
    if evidence.get("campaign_activation_statement_sha256") != EXPECTED_ACTIVATION_SHA256:
        raise CampaignV2ClosureError("activation digest mismatch")

    frozen = evidence.get("frozen_adequacy_rule")
    if frozen != {
        "maximum_schedule_lag_minutes": MAX_SCHEDULE_LAG_MINUTES,
        "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
        "target_slots": TARGET_SLOTS,
    }:
        raise CampaignV2ClosureError("frozen adequacy rule mismatch")

    lineage = evidence.get("frozen_lineage")
    expected_lineage = {
        "repository_commit": EXPECTED_REPOSITORY_COMMIT,
        "repository_tree": EXPECTED_REPOSITORY_TREE,
        "request_fingerprint_sha256": EXPECTED_REQUEST_FINGERPRINT,
        "workflow_blob_sha": EXPECTED_WORKFLOW_BLOB,
        "workflow_identity": EXPECTED_WORKFLOW_IDENTITY,
        "workflow_path": EXPECTED_WORKFLOW_PATH,
    }
    if lineage != expected_lineage:
        raise CampaignV2ClosureError("lineage mismatch")

    records = evidence.get("records")
    if not isinstance(records, list) or len(records) < 1:
        raise CampaignV2ClosureError("missing records")

    seen_slots: set[int] = set()
    late_count = 0
    for record in records:
        if not isinstance(record, dict):
            raise CampaignV2ClosureError("invalid record")
        slot = record.get("target_slot")
        if type(slot) is not int or not 0 <= slot < TARGET_SLOTS:
            raise CampaignV2ClosureError("invalid slot")
        if slot in seen_slots:
            raise CampaignV2ClosureError("duplicate observed slot")
        seen_slots.add(slot)
        if record.get("github_run_attempt") != 1:
            raise CampaignV2ClosureError("non-first attempt")
        lag = record.get("start_lag_microseconds")
        if type(lag) is not int or lag <= MAX_SCHEDULE_LAG_MICROSECONDS:
            raise CampaignV2ClosureError("record does not prove lateness")
        late_count += 1

    maximum_possible = TARGET_SLOTS - late_count
    if maximum_possible >= MIN_ACCEPTED_SLOTS:
        raise CampaignV2ClosureError("failure is not mathematically decisive")

    proof = evidence.get("observed_proof")
    if not isinstance(proof, dict):
        raise CampaignV2ClosureError("missing proof")
    if proof.get("records_late_over_120_minutes") != late_count:
        raise CampaignV2ClosureError("late-count mismatch")
    if proof.get("maximum_possible_accepted_slots_after_observed_late_slots") != maximum_possible:
        raise CampaignV2ClosureError("maximum-possible mismatch")
    if proof.get("minimum_required_accepted_slots") != MIN_ACCEPTED_SLOTS:
        raise CampaignV2ClosureError("minimum-required mismatch")

    digest = hashlib.sha256(evidence_bytes).hexdigest()
    if statement.get("decisive_failure_evidence_sha256") != digest:
        raise CampaignV2ClosureError("evidence digest mismatch")
    if statement.get("campaign_activation_statement") != EXPECTED_ACTIVATION:
        raise CampaignV2ClosureError("statement activation mismatch")
    if statement.get("campaign_activation_statement_sha256") != EXPECTED_ACTIVATION_SHA256:
        raise CampaignV2ClosureError("statement activation digest mismatch")
    if statement.get("observed_late_slots_proven") != late_count:
        raise CampaignV2ClosureError("statement late-count mismatch")
    if statement.get("maximum_possible_accepted_slots") != maximum_possible:
        raise CampaignV2ClosureError("statement maximum-possible mismatch")
    if statement.get("final_status") != EXPECTED_FINAL_STATUS:
        raise CampaignV2ClosureError("final status mismatch")
    if statement.get("outcome_blind") is not True:
        raise CampaignV2ClosureError("closure must remain outcome-blind")

    forbidden_true = (
        "retroactive_backfill_permitted",
        "threshold_relaxation_permitted",
        "confirmatory_history_construction_permitted",
        "temporal_state_outcome_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "phase3_policy_mutation_permitted",
        "public_raw_provider_data_redistribution_permitted",
    )
    if any(statement.get(key) is not False for key in forbidden_true):
        raise CampaignV2ClosureError("forbidden permission enabled")


def validate_files(evidence_path: Path, statement_path: Path) -> None:
    evidence_bytes = evidence_path.read_bytes()
    evidence = _load_json(evidence_path)
    statement = _load_json(statement_path)
    validate_decisive_failure(evidence, statement, evidence_bytes=evidence_bytes)
