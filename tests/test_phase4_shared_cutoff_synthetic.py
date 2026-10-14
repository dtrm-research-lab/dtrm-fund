"""Synthetic-only Phase IV shared-cutoff proof-boundary tests."""

from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.shared_cutoff_synthetic import (
    SharedCutoffAssessment,
    SharedCutoffError,
    assess_shared_cutoff,
)


def fixture() -> dict:
    return {
        "schema_version": "dtrm.phase4.shared_cutoff_fixture.v0",
        "dataset_role": "synthetic",
        "cases": [{
            "case_tag": "case_01",
            "decision_cutoff": "2026-10-14T10:00:00Z",
            "news_version_observed_at": "2026-10-14T09:00:00Z",
            "news_linked_at": "2026-10-14T09:30:00Z",
            "mapping_available_at": "2026-10-14T08:00:00Z",
            "price_dependencies": [{
                "dependency_tag": "price_01",
                "price_session_date": "2026-10-14",
                "price_first_available_at": "2026-10-14T09:40:00Z",
                "price_vintage_available_at": "2026-10-14T09:50:00Z",
            }],
        }],
    }


def _result(raw: dict) -> dict:
    return assess_shared_cutoff(raw).to_json()


def test_before_is_only_synthetic_not_real_authorization() -> None:
    state = assess_shared_cutoff(fixture())
    report = state.to_json()
    assert isinstance(state, SharedCutoffAssessment)
    assert state.cases[0].conclusion == "SYNTHETIC_ALL_BEFORE"
    assert report["engineering_status"] == "PASS_SYNTHETIC_SHARED_CUTOFF_ORDERING"
    assert report["scientific_status"] == "BLOCKED_CONTROL_CLOCK_ATTESTATION"
    assert report["case_count"] == 1
    assert report["synthetic_all_before"] == 1
    for field in (
        "source_authenticated",
        "clock_authenticated",
        "dependency_completeness_authenticated",
        "history_construction_permitted",
        "model_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "scientific_counting_permitted",
    ):
        assert report[field] is False


@pytest.mark.parametrize("path", [
    ("news_version_observed_at", "2026-10-14T10:00:00Z", "AT_CUTOFF"),
    ("news_linked_at", "2026-10-14T10:01:00Z", "AFTER"),
    ("mapping_available_at", None, "UNKNOWN"),
])
def test_news_link_mapping_clocks_fail_closed(path) -> None:
    field, value, state = path
    case = fixture()
    case["cases"][0][field] = value
    report = _result(case)
    assert report["cases"][0]["conclusion"] == "SYNTHETIC_BLOCKED"
    key = {"news_version_observed_at": "news_version", "news_linked_at": "news_link", "mapping_available_at": "mapping"}[field]
    assert report["cases"][0][key] == state


@pytest.mark.parametrize("field,value,expected", [
    ("price_first_available_at", "2026-10-14T10:30:00Z", "AFTER"),
    ("price_first_available_at", "2026-10-14T10:00:00Z", "AT_CUTOFF"),
    ("price_first_available_at", None, "UNKNOWN"),
    ("price_vintage_available_at", "2026-10-14T10:15:00Z", "AFTER"),
    ("price_vintage_available_at", None, "UNKNOWN"),
])
def test_price_date_does_not_authenticate_close(field, value, expected) -> None:
    case = fixture()
    case["cases"][0]["price_dependencies"][0][field] = value
    report = _result(case)
    price = report["cases"][0]["price_dependencies"][0]
    assert report["cases"][0]["conclusion"] == "SYNTHETIC_BLOCKED"
    assert price["first_availability" if field == "price_first_available_at" else "vintage_availability"] == expected
    assert report["synthetic_all_before"] == 0


def test_all_declared_price_dependencies_must_pass() -> None:
    case = fixture()
    later_price = copy.deepcopy(case["cases"][0]["price_dependencies"][0])
    later_price["dependency_tag"] = "price_02"
    later_price["price_vintage_available_at"] = "2026-10-14T10:00:01Z"
    case["cases"][0]["price_dependencies"].append(later_price)
    result = _result(case)
    assert result["cases"][0]["conclusion"] == "SYNTHETIC_BLOCKED"
    assert result["cases"][0]["price_dependencies"][1]["vintage_availability"] == "AFTER"


def test_timezone_normalization_and_permutation_invariant() -> None:
    initial = fixture()
    initial["cases"].append(copy.deepcopy(initial["cases"][0]))
    initial["cases"][1]["case_tag"] = "case_02"
    initial["cases"][1]["price_dependencies"][0]["dependency_tag"] = "price_02"
    a = _result(initial)
    changed = copy.deepcopy(initial)
    changed["cases"].reverse()
    changed["cases"][0]["decision_cutoff"] = "2026-10-14T12:00:00+02:00"
    changed["cases"][0]["news_version_observed_at"] = "2026-10-14T11:00:00+02:00"
    changed["cases"][0]["price_dependencies"][0]["price_first_available_at"] = "2026-10-14T11:40:00+02:00"
    b = _result(changed)
    assert a == b


def test_immutable_state_and_detached_report() -> None:
    raw = fixture()
    frozen = assess_shared_cutoff(raw)
    raw["cases"][0]["price_dependencies"][0]["price_first_available_at"] = None
    assert frozen.cases[0].conclusion == "SYNTHETIC_ALL_BEFORE"
    with pytest.raises(FrozenInstanceError):
        frozen.synthetic_all_before = 999
    serialized = frozen.to_json()
    serialized["source_authenticated"] = True
    serialized["cases"][0]["conclusion"] = "FAKE"
    assert frozen.to_json()["source_authenticated"] is False
    assert frozen.cases[0].conclusion == "SYNTHETIC_ALL_BEFORE"


@pytest.mark.parametrize("mutation", [
    lambda data: data.update(dataset_role="unaudited"),
    lambda data: data.update(schema_version="unsupported"),
    lambda data: data.update(protected_target=2.0),
    lambda data: data["cases"][0].update(case_tag="aapl"),
    lambda data: data["cases"][0].update(case_tag="case_00"),
    lambda data: data["cases"][0].update(case_tag="case_65"),
    lambda data: data["cases"][0].update(decision_cutoff="2026-10-14"),
    lambda data: data["cases"][0].update(decision_cutoff="2026-10-14T10:00:00"),
    lambda data: data["cases"][0].update(decision_cutoff=True),
    lambda data: data["cases"][0].update(news_linked_at="2026-99-14T11:00:00Z"),
    lambda data: data["cases"][0].update(news_linked_at="2026-10-14T09:00:00"),
    lambda data: data["cases"][0]["price_dependencies"][0].update(price_session_date="2026-02-30"),
    lambda data: data["cases"][0]["price_dependencies"][0].update(price_session_date="2026-10-14T00:00:00Z"),
    lambda data: data["cases"][0]["price_dependencies"][0].update(dependency_tag="tsla"),
    lambda data: data["cases"][0]["price_dependencies"][0].update(close=200.0),
    lambda data: data["cases"][0]["price_dependencies"].clear(),
    lambda data: data["cases"].clear(),
    lambda data: data["cases"].append(copy.deepcopy(data["cases"][0])),
    lambda data: data["cases"][0]["price_dependencies"].append(copy.deepcopy(data["cases"][0]["price_dependencies"][0])),
])
def test_malformed_fixtures_fail_closed(mutation) -> None:
    raw = fixture()
    mutation(raw)
    with pytest.raises(SharedCutoffError, match="INVALID_SYNTHETIC_SHARED_CUTOFF_FIXTURE"):
        assess_shared_cutoff(raw)
