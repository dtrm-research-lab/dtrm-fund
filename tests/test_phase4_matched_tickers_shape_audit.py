"""Phase IV read-only structural census: invented aggregate groups, never real rows."""

from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.matched_tickers_shape_audit import (
    CENSUS_CAP,
    NAMESPACE,
    ShapeAssessment,
    ShapeAuditError,
    build_shape_pipeline,
    normalize_shape_counts,
    pipeline_sha256,
)


def fake_aggregate() -> dict:
    return {
        "containers": [{"kind": "array", "n": 4}, {"kind": "missing", "n": 1}],
        "elements": [
            {"kind": "string", "n": 2,
             "ticker": "not_object", "symbol": "not_object", "name": "not_object",
             "score": "not_object", "confidence": "not_object", "match_type": "not_object"},
            {"kind": "object", "n": 3,
             "ticker": "string", "symbol": "missing", "name": "missing",
             "score": "double", "confidence": "missing", "match_type": "string"},
        ],
    }


def test_pipeline_is_fixed_bounded_and_aggregate_only() -> None:
    pipeline = build_shape_pipeline()
    assert pipeline[0] == {"$limit": CENSUS_CAP + 1}
    encoded = str(pipeline)
    assert "$facet" in encoded and "$unwind" in encoded and "$group" in encoded
    assert "$type" in encoded and "matched_tickers" in encoded
    assert all(x not in encoded for x in ("$out", "$merge", "$lookup", "$where", "$function", "$sample"))
    assert "content" not in encoded and "text" not in encoded
    assert "title" not in encoded and "target_model" not in encoded


def test_aggregate_only_deterministic_counts_and_negative_authority() -> None:
    result = normalize_shape_counts(fake_aggregate(), counted_documents=5)
    assert isinstance(result, ShapeAssessment)
    report = result.to_json()
    assert report["document_count"] == 5
    assert report["element_count"] == 5
    assert len(report["elements"]) == 2
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for key in (
        "asset_mapping_authenticated", "vintage_authenticated",
        "decision_clock_authenticated", "history_construction_permitted",
        "model_fitting_permitted", "outcome_access_permitted", "mm1_execution_permitted",
    ):
        assert report[key] is False


def test_permutation_and_mutation_proof() -> None:
    raw = fake_aggregate()
    frozen = normalize_shape_counts(raw, counted_documents=5)
    shuffled = fake_aggregate()
    shuffled["containers"].reverse()
    shuffled["elements"].reverse()
    assert frozen == normalize_shape_counts(shuffled, counted_documents=5)
    raw["containers"][0]["n"] = 999
    assert frozen.to_json()["document_count"] == 5
    with pytest.raises(FrozenInstanceError):
        frozen.elements_count = 900
    report = frozen.to_json()
    report["asset_mapping_authenticated"] = True
    report["elements"][0]["n"] = 999
    assert frozen.to_json()["asset_mapping_authenticated"] is False
    assert all(group.n != 999 for group in frozen.elements)


def test_empty_collection_not_a_source_proof() -> None:
    result = normalize_shape_counts({"containers": [], "elements": []}, counted_documents=0)
    assert result.to_json()["document_count"] == 0
    assert result.to_json()["asset_mapping_authenticated"] is False


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(token="not-permitted"),
    lambda x: x["containers"].append(copy.deepcopy(x["containers"][0])),
    lambda x: x["containers"][0].update(kind="SECRET"),
    lambda x: x["containers"][0].update(n=True),
    lambda x: x["containers"][0].update(n=0),
    lambda x: x["containers"][0].update(n=250001),
    lambda x: x["containers"][0].update(actual_ticker="TSLA"),
    lambda x: x["elements"].append(copy.deepcopy(x["elements"][0])),
    lambda x: x["elements"][0].update(kind="UNKNOWN_KIND"),
    lambda x: x["elements"][0].update(ticker="string"),
    lambda x: x["elements"][1].update(ticker="not_object"),
    lambda x: x["elements"][1].update(name="AAPL"),
    lambda x: x["elements"][1].update(match_type="keyword"),
    lambda x: x["elements"][1].update(n=5000001),
    lambda x: x["elements"][1].update(n=0),
    lambda x: x["elements"][0].update(content="private"),
    lambda x: x["containers"].clear(),
])
def test_rejects_unknown_values_or_inconsistent_shapes(mutation) -> None:
    data = fake_aggregate()
    mutation(data)
    with pytest.raises(ShapeAuditError, match="INVALID_MATCHED_TICKERS_SHAPE_AGGREGATE"):
        normalize_shape_counts(data, counted_documents=5)


@pytest.mark.parametrize("n", [True, -1, 6, CENSUS_CAP + 1])
def test_rejects_bad_preliminary_count(n: int) -> None:
    with pytest.raises(ShapeAuditError):
        normalize_shape_counts(fake_aggregate(), counted_documents=n)


def test_aggregate_with_only_empty_arrays_is_valid_but_not_authenticated() -> None:
    evidence = {
        "containers": [{"kind": "array", "n": 3}],
        "elements": [],
    }
    state = normalize_shape_counts(evidence, counted_documents=3)
    assert state.elements_count == 0
    assert state.to_json()["asset_mapping_authenticated"] is False


def test_source_expected_object_shape_is_structural_only() -> None:
    report = normalize_shape_counts(fake_aggregate(), counted_documents=5).to_json()
    groups = report["elements"]
    structured = [group for group in groups if group["kind"] == "object"]
    assert len(structured) == 1
    assert structured[0]["ticker"] == "string"
    assert structured[0]["match_type"] == "string"
    assert structured[0]["n"] == 3
    assert "keyword" not in str(report)
    assert report["asset_mapping_authenticated"] is False


def test_report_digest_commits_to_fixed_source_and_pipeline() -> None:
    import hashlib
    import json

    report = normalize_shape_counts(fake_aggregate(), counted_documents=5).to_json()
    assert report["source_namespace"] == NAMESPACE == "trumpMinMax.trumpNews"
    assert report["pipeline_sha256"] == pipeline_sha256()
    evidence = {
        "source_namespace": report["source_namespace"],
        "pipeline_sha256": report["pipeline_sha256"],
        "document_count": report["document_count"],
        "element_count": report["element_count"],
        "containers": report["containers"],
        "elements": report["elements"],
    }
    def digest(data):
        return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=True).encode("ascii")).hexdigest()
    assert digest(evidence) == report["sanitized_evidence_sha256"]
    assert digest({**evidence, "source_namespace": "other.database"}) != report["sanitized_evidence_sha256"]
    assert digest({**evidence, "pipeline_sha256": "0" * 64}) != report["sanitized_evidence_sha256"]
