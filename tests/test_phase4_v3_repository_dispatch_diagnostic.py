from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research/evidence/phase4_v3_repository_dispatch_diagnostic_evidence_v1.json"
STATEMENT = ROOT / "research/contracts/DTRM_PHASE4_V3_REPOSITORY_DISPATCH_DIAGNOSTIC_V1.json"


def test_committed_v3_dispatch_diagnostic_is_bound_and_noncounting() -> None:
    evidence_bytes = EVIDENCE.read_bytes()
    evidence = json.loads(evidence_bytes)
    statement = json.loads(STATEMENT.read_text(encoding="utf-8"))

    assert hashlib.sha256(evidence_bytes).hexdigest() == statement["diagnostic_evidence_sha256"]
    assert evidence["status"] == "PASS_REPOSITORY_DISPATCH_DIAGNOSTIC_V1"
    assert statement["diagnostic_status"] == evidence["status"]
    assert statement["repository_dispatch_transport_diagnostic_satisfied"] is True
    assert evidence["event_name"] == "repository_dispatch"
    assert evidence["event_type"] == "phase4_fmp_news_temporal_capture_v3"
    assert evidence["github_run_attempt"] == 1
    assert evidence["github_run_conclusion"] == "success"
    assert evidence["start_lag_microseconds"] <= evidence["frozen_start_lag_limit_microseconds"]
    assert evidence["within_frozen_start_lag_bound"] is True
    assert evidence["workflow_blob_sha"] == statement["workflow_blob_sha"]
    assert evidence["repository_commit"] == statement["workflow_repository_commit"]
    assert evidence["repository_tree"] == statement["workflow_repository_tree"]

    assert evidence["scheduler_role"] == "DIAGNOSTIC_ONLY_NOT_CAMPAIGN_SCHEDULER"
    assert statement["scheduler_identity_for_campaign_bound"] is False
    assert statement["campaign_scheduler_readiness_satisfied"] is False
    assert statement["activation_permitted"] is False
    assert statement["scientific_counting_permitted"] is False

    for key in (
        "provider_access_performed",
        "counting_eligible",
        "outcome_access_permitted",
        "temporal_state_outcome_fitting_permitted",
        "phase3_policy_mutation_permitted",
        "public_raw_provider_data_redistribution_permitted",
    ):
        assert evidence[key] is False
