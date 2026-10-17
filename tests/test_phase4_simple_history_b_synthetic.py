"""Synthetic-only B mechanics, no authenticated history or model fitting."""

from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.simple_history_b_synthetic import (
    SyntheticBAssessment,
    SyntheticHistoryError,
    assess_synthetic_b_mechanics,
)


def fixture() -> dict:
    return {
        "schema_version": "dtrm.phase4.simple_history_fixture.v0",
        "dataset_role": "synthetic",
        "cases": [{
            "case_tag": "case_01",
            "decision_cutoff": "2026-10-14T10:00:00Z",
            "lookback_days": 2,
            "events": [
                {"event_tag": "event_01", "source_role": "fmp_articles",
                 "effective_available_at": "2026-10-12T10:00:00Z"},
                {"event_tag": "event_02", "source_role": "stock_latest",
                 "effective_available_at": "2026-10-14T09:59:00Z"},
                {"event_tag": "event_03", "source_role": "general_latest",
                 "effective_available_at": "2026-10-12T09:59:59Z"},
            ],
        }],
    }


def test_boundaries_role_counts_and_recency() -> None:
    frozen = assess_synthetic_b_mechanics(fixture())
    assert isinstance(frozen, SyntheticBAssessment)
    report = frozen.to_json()
    assert report["window_total"] == 2
    assert report["case_count"] == 1
    row = report["cases"][0]
    assert row["window_count"] == 2
    assert row["most_recent_age_seconds"] == 60
    assert row["role_counts"] == {"fmp_articles": 1, "general_latest": 0, "stock_latest": 1}
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for k in ("source_authenticated", "decision_clock_authenticated",
              "zero_history_authenticated", "g5_lookback_frozen",
              "history_construction_permitted", "model_fitting_permitted",
              "outcome_access_permitted", "mm1_execution_permitted",
              "scientific_counting_permitted"):
        assert report[k] is False


def test_empty_events_is_not_authenticated_zero_history() -> None:
    data = fixture()
    data["cases"][0]["events"] = []
    result = assess_synthetic_b_mechanics(data).to_json()
    assert result["cases"][0]["window_count"] == 0
    assert result["cases"][0]["most_recent_age_seconds"] is None
    assert result["zero_history_authenticated"] is False


def test_permutation_timezone_and_detached_input() -> None:
    data = fixture()
    other = copy.deepcopy(data["cases"][0])
    other["case_tag"] = "case_02"
    other["events"][0]["source_role"] = "general_latest"
    data["cases"].append(other)
    original = assess_synthetic_b_mechanics(data)
    changed = copy.deepcopy(data)
    changed["cases"].reverse()
    for case in changed["cases"]:
        case["decision_cutoff"] = "2026-10-14T12:00:00+02:00"
        case["events"][1]["effective_available_at"] = "2026-10-14T11:59:00+02:00"
        case["events"].reverse()
    assert original == assess_synthetic_b_mechanics(changed)
    data["cases"][0]["events"][0]["source_role"] = "stock_latest"
    assert original.to_json() != assess_synthetic_b_mechanics(data).to_json()
    assert original.to_json()["cases"][0]["role_counts"]["fmp_articles"] == 1


def test_immutable_frozen_and_detached_report() -> None:
    state = assess_synthetic_b_mechanics(fixture())
    with pytest.raises(FrozenInstanceError):
        state.window_total = 500
    with pytest.raises(FrozenInstanceError):
        state.cases[0].window_count = 500
    first = state.to_json()
    first["source_authenticated"] = True
    first["cases"][0]["role_counts"]["fmp_articles"] = 999
    assert state.to_json()["source_authenticated"] is False
    assert state.cases[0].role_counts == (1, 0, 1)


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(dataset_role="real"),
    lambda x: x.update(extra_price=1.2),
    lambda x: x["cases"].clear(),
    lambda x: x["cases"].append(copy.deepcopy(x["cases"][0])),
    lambda x: x["cases"][0].update(case_tag="MSFT"),
    lambda x: x["cases"][0].update(case_tag="case_00"),
    lambda x: x["cases"][0].update(lookback_days=0),
    lambda x: x["cases"][0].update(lookback_days=366),
    lambda x: x["cases"][0].update(lookback_days=True),
    lambda x: x["cases"][0].update(lookback_days=60.0),
    lambda x: x["cases"][0].update(decision_cutoff="2026-10-14"),
    lambda x: x["cases"][0].update(decision_cutoff="2026-10-14 10:00:00Z"),
    lambda x: x["cases"][0].update(decision_cutoff="2026-10-14T10:00:00-00:00"),
    lambda x: x["cases"][0].update(decision_cutoff="0001-01-01T00:00:00Z"),
    lambda x: x["cases"][0]["events"].append(copy.deepcopy(x["cases"][0]["events"][0])),
    lambda x: x["cases"][0]["events"][0].update(source_role="unknown_role"),
    lambda x: x["cases"][0]["events"][0].update(event_tag="AAPL"),
    lambda x: x["cases"][0]["events"][0].update(protected_outcome=3),
    lambda x: x["cases"][0]["events"][0].update(effective_available_at="2026-10-14T10:00:00Z"),
    lambda x: x["cases"][0]["events"][0].update(effective_available_at="2026-10-14T10:00:01Z"),
    lambda x: x["cases"][0]["events"][0].update(effective_available_at=None),
    lambda x: x["cases"][0]["events"][0].update(effective_available_at="9999-12-31T23:59:59-14:00"),
])
def test_invalid_or_unauthenticated_shape_fails_closed(mutation) -> None:
    data = fixture()
    mutation(data)
    with pytest.raises(SyntheticHistoryError, match="INVALID_PHASE4_SYNTHETIC_HISTORY"):
        assess_synthetic_b_mechanics(data)


def test_cross_day_utc_window_is_exact() -> None:
    data = fixture()
    data["cases"][0]["decision_cutoff"] = "2026-10-14T00:05:00Z"
    data["cases"][0]["lookback_days"] = 1
    data["cases"][0]["events"] = [
        {"event_tag": "event_04", "source_role": "general_latest",
         "effective_available_at": "2026-10-13T00:05:00Z"},
        {"event_tag": "event_05", "source_role": "stock_latest",
         "effective_available_at": "2026-10-13T00:04:59Z"},
    ]
    result = assess_synthetic_b_mechanics(data).to_json()
    assert result["cases"][0]["window_count"] == 1
    assert result["cases"][0]["most_recent_age_seconds"] == 86400
