from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research/evidence/phase4_v3_repository_dispatch_diagnostic_evidence_v1.json"
STATEMENT = ROOT / "research/contracts/DTRM_PHASE4_V3_REPOSITORY_DISPATCH_DIAGNOSTIC_V1.json"
RUN_DIR = (
    ROOT
    / "research/evidence/phase4_v3_repository_dispatch_diagnostic_run_37005569048"
)
ARCHIVE = RUN_DIR / "phase4-v3-dispatch-diagnostic-37005569048-1.zip"
ARTIFACT_ENTRY = RUN_DIR / "dispatch_diagnostic.json"
DIAGNOSTIC_STATEMENT = RUN_DIR / "diagnostic_statement.json"
API_PROVENANCE = RUN_DIR / "github_api_provenance.json"

EXPECTED_REPOSITORY = "tech-com-UA00001/theresistance-back"
EXPECTED_REPOSITORY_ID = 1128196792
EXPECTED_WORKFLOW_ID = 372997917
EXPECTED_WORKFLOW_NAME = "Phase IV FMP temporal dispatch v3 dormant"
EXPECTED_WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v3.yml"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_committed_v3_dispatch_diagnostic_is_bound_and_noncounting() -> None:
    evidence_bytes = EVIDENCE.read_bytes()
    evidence = json.loads(evidence_bytes)
    statement = json.loads(STATEMENT.read_text(encoding="utf-8"))

    assert hashlib.sha256(evidence_bytes).hexdigest() == statement["diagnostic_evidence_sha256"]
    assert _sha256(ARCHIVE) == statement["diagnostic_artifact_archive_sha256"]
    assert _sha256(ARTIFACT_ENTRY) == statement["diagnostic_artifact_entry_sha256"]
    assert _sha256(DIAGNOSTIC_STATEMENT) == statement["diagnostic_campaign_statement_sha256"]
    assert _sha256(API_PROVENANCE) == statement["diagnostic_api_provenance_sha256"]

    artifact_entry_bytes = ARTIFACT_ENTRY.read_bytes()
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.namelist() == ["dispatch_diagnostic.json"]
        assert archive.read("dispatch_diagnostic.json") == artifact_entry_bytes

    artifact = json.loads(artifact_entry_bytes)
    diagnostic_statement = json.loads(DIAGNOSTIC_STATEMENT.read_text(encoding="utf-8"))
    api_provenance = json.loads(API_PROVENANCE.read_text(encoding="utf-8"))

    assert api_provenance["repository_full_name"] == EXPECTED_REPOSITORY
    assert api_provenance["repository_id"] == EXPECTED_REPOSITORY_ID
    assert api_provenance["workflow_id"] == EXPECTED_WORKFLOW_ID
    assert api_provenance["workflow_name"] == EXPECTED_WORKFLOW_NAME
    assert api_provenance["workflow_path"] == EXPECTED_WORKFLOW_PATH
    assert api_provenance["run_api_url"] == (
        f"https://api.github.com/repos/{EXPECTED_REPOSITORY}/actions/runs/37005569048"
    )
    assert api_provenance["workflow_url"] == (
        f"https://api.github.com/repos/{EXPECTED_REPOSITORY}/actions/workflows/{EXPECTED_WORKFLOW_ID}"
    )
    assert api_provenance["workflow_path"] == artifact["workflow_path"]

    assert api_provenance["artifact_archive_sha256"] == statement["diagnostic_artifact_archive_sha256"]
    assert api_provenance["artifact_entry_sha256"] == statement["diagnostic_artifact_entry_sha256"]
    assert api_provenance["artifact_entry_size_in_bytes"] == len(artifact_entry_bytes)
    assert api_provenance["artifact_size_in_bytes"] == ARCHIVE.stat().st_size
    assert api_provenance["artifact_id"] == evidence["artifact_id"]
    assert api_provenance["artifact_name"] == evidence["artifact_name"]
    assert f"sha256:{api_provenance['artifact_archive_sha256']}" == evidence["artifact_digest"]
    assert api_provenance["github_run_id"] == artifact["github_run_id"] == evidence["github_run_id"]
    assert api_provenance["github_run_attempt"] == artifact["github_run_attempt"] == 1
    assert api_provenance["conclusion"] == evidence["github_run_conclusion"] == "success"
    assert api_provenance["head_sha"] == artifact["repository_commit"]

    assert diagnostic_statement["statement_id"] == artifact["campaign_statement"]
    assert _sha256(DIAGNOSTIC_STATEMENT) == artifact["campaign_statement_sha256"]
    assert diagnostic_statement["target_slot"] == artifact["target_slot"] == evidence["target_slot"]
    assert diagnostic_statement["target_at_utc"] == artifact["target_at_utc"] == evidence["target_at_utc"]
    assert diagnostic_statement["backend_merge"] == artifact["repository_commit"]
    assert diagnostic_statement["backend_tree"] == artifact["repository_tree"]
    assert diagnostic_statement["workflow_blob_sha"] == artifact["workflow_blob_sha"]

    assert evidence["status"] == "PASS_REPOSITORY_DISPATCH_DIAGNOSTIC_V1"
    assert statement["diagnostic_status"] == evidence["status"]
    assert statement["repository_dispatch_transport_diagnostic_satisfied"] is True
    assert artifact["event_name"] == evidence["event_name"] == "repository_dispatch"
    assert artifact["event_type"] == evidence["event_type"] == "phase4_fmp_news_temporal_capture_v3"
    assert artifact["start_lag_microseconds"] == evidence["start_lag_microseconds"]
    assert artifact["dispatch_lag_microseconds"] == evidence["dispatch_lag_microseconds"]
    assert artifact["start_lag_microseconds"] <= statement["frozen_start_lag_limit_microseconds"]
    assert evidence["within_frozen_start_lag_bound"] is True
    assert artifact["workflow_blob_sha"] == statement["workflow_blob_sha"]
    assert artifact["repository_commit"] == statement["workflow_repository_commit"]
    assert artifact["repository_tree"] == statement["workflow_repository_tree"]

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
        assert artifact[key] is False
        assert evidence[key] is False
