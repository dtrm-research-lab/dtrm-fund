"""Phase IV read-only structural census: invented aggregate groups, never real rows."""

from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.matched_tickers_shape_audit import (
    CENSUS_CAP,
    ShapeAssessment,
    ShapeAuditError,
    build_shape_pipeline,
    normalize_shape_counts,
)


def fake_aggregate() -> dict:
    return {
        "containers": [{"kind": "array", "n": 4}, {"kind": "missing", "n": 1}],
        "elements": [
            {"kind": "string", "n": 2,
             "ticker": "not_object", "symbol": "not_object", "name": "not_object",
             "score": "not_object", "confidence": "not_object"},
            {"kind": "object", "n": 3,
             "ticker": "string", "symbol": "missing", "name": "missing",
             "score": "double", "confidence": "missing"},
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
    lambda x: x["elements"][1].update(n=5000001),
    lambda x: x["elements"][1].update(n=0),
    lambda x: x["elements"][0].update(content="private"),
    lambda x: x["elements"].clear(),
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
