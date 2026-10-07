from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATEMENT = ROOT / "research/contracts/DTRM_PHASE4_V3_SCHEDULER_ARCHITECTURE_V0.json"


def _statement() -> dict[str, object]:
    return json.loads(STATEMENT.read_text(encoding="utf-8"))


def test_v3_scheduler_architecture_preserves_frozen_campaign_geometry() -> None:
    statement = _statement()
    assert statement["external_scheduler"] == "AWS_EVENTBRIDGE_SCHEDULER"
    assert statement["schedule_expression_type"] == "ONE_TIME_AT"
    assert statement["schedule_cardinality"] == 56
    assert statement["frozen_target_slots"] == 56
    assert statement["frozen_minimum_accepted_slots"] == 48
    assert statement["frozen_target_clocks_utc"] == ["00:15", "06:15", "12:15", "18:15"]
    assert statement["frozen_start_lag_limit_minutes"] == 120
    assert statement["schedule_timezone"] == "UTC"
    assert statement["schedule_flexible_time_window"] == "OFF"
    assert statement["no_backfill"] is True
    assert statement["no_early_stopping"] is True


def test_v3_scheduler_architecture_fails_closed_on_duplicates() -> None:
    statement = _statement()
    assert statement["scheduler_delivery_assumption"] == (
        "AT_LEAST_ONCE_REQUIRES_FAIL_CLOSED_IDEMPOTENCY"
    )
    assert statement["idempotency_store"] == "AWS_DYNAMODB_CONDITIONAL_PUT"
    assert statement["duplicate_policy"] == (
        "FIRST_DURABLE_SLOT_CLAIM_PRECEDES_GITHUB_POST_ALL_LATER_INVOCATIONS_FAIL_CLOSED"
    )
    assert statement["github_dispatch_post_attempts_per_target_max"] == 1
    assert statement["dispatch_id_semantics"] == (
        "DETERMINISTIC_PER_CAMPAIGN_STATEMENT_TARGET_SLOT_AND_TARGET_UTC"
    )


def test_v3_scheduler_architecture_is_implementation_only_and_nonactivating() -> None:
    statement = _statement()
    assert statement["implementation_permitted"] is True
    assert statement["aws_region_bound"] is False
    assert statement["resource_arns_bound"] is False
    assert statement["campaign_scheduler_identity_bound"] is False
    assert statement["campaign_start_bound"] is False
    assert statement["real_scheduler_diagnostic_permitted"] is False
    assert statement["activation_permitted"] is False
    assert statement["counting_capture_permitted"] is False
    assert statement["provider_access_performed_by_scheduler"] is False
    assert statement["outcome_access_permitted"] is False
    assert statement["temporal_state_outcome_fitting_permitted"] is False
    assert statement["mm1_execution_permitted"] is False
    assert statement["phase3_policy_mutation_permitted"] is False
    assert statement["public_raw_provider_data_redistribution_permitted"] is False
    assert statement["confirmatory_history_construction_permitted"] is False
    assert statement["scientific_status"] == (
        "BLOCKED_SCHEDULER_PROVISIONING_AND_IDENTITY_BINDING"
    )


def test_v3_scheduler_architecture_keeps_existing_github_boundary() -> None:
    statement = _statement()
    assert statement["github_repository"] == "tech-com-UA00001/theresistance-back"
    assert statement["dispatch_event_type"] == "phase4_fmp_news_temporal_capture_v3"
    assert statement["github_workflow_identity"] == "phase4_fmp_news_temporal_capture_v3"
    assert statement["github_workflow_path"] == (
        ".github/workflows/phase4_fmp_news_temporal_capture_v3.yml"
    )
    assert statement["dispatch_authentication"] == "HMAC_SHA256_SHARED_SECRET"
    assert statement["secret_storage"] == "AWS_SECRETS_MANAGER"
    assert statement["lambda_role"] == "SOURCE_VALUE_FREE_DISPATCHER_ONLY"
