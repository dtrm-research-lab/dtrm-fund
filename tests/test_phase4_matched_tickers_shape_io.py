"""Read-only type-only Mongo transport and shape audit injection tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from dtrm.phase4.matched_tickers_shape_audit import build_shape_pipeline
from dtrm.phase4.matched_tickers_shape_io import (
    ShapeAuditIOError,
    analyze_injected_collection,
)


def aggregate() -> dict:
    return {
        "containers": [{"kind": "array", "n": 3}],
        "elements": [{
            "kind": "object", "ticker": "string", "symbol": "missing",
            "name": "missing", "score": "missing", "confidence": "missing",
            "match_type": "string", "n": 5,
        }],
    }


class FakeCursor:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows
        self.closed = False

    def __iter__(self) -> Iterator[object]:
        return iter(self.rows)

    def close(self) -> None:
        self.closed = True


class FakeCollection:
    def __init__(self, rows: list[object] | None = None, count: int = 3) -> None:
        self.rows = [aggregate()] if rows is None else rows
        self.count = count
        self.calls: list[tuple[str, object]] = []
        self.cursor = FakeCursor(self.rows)

    def count_documents(self, query: dict[str, object], **kwargs: object) -> int:
        self.calls.append(("count", (query, kwargs)))
        return self.count

    def aggregate(self, pipeline: list[dict[str, object]], **kwargs: object) -> FakeCursor:
        self.calls.append(("aggregate", (pipeline, kwargs)))
        return self.cursor


def test_fixed_read_only_driver_calls() -> None:
    source = FakeCollection()
    report = analyze_injected_collection(source)
    assert report.documents == 3
    assert report.elements_count == 5
    assert source.cursor.closed
    assert source.calls == [
        ("count", ({}, {"maxTimeMS": 60_000})),
        ("aggregate", (build_shape_pipeline(), {"maxTimeMS": 60_000, "allowDiskUse": False})),
    ]
    assert report.to_json()["asset_mapping_authenticated"] is False


def test_oversize_aborts_before_aggregate() -> None:
    source = FakeCollection(count=250001)
    with pytest.raises(ShapeAuditIOError, match="SOURCE_COUNT_OUT_OF_BOUNDS"):
        analyze_injected_collection(source)
    assert len(source.calls) == 1


@pytest.mark.parametrize("response, count", [
    ([], 3),
    ([aggregate(), aggregate()], 3),
    ([{"containers": [], "elements": []}], 3),
    ([{"containers": [{"kind": "array", "n": 3}], "elements": [{"kind": "object", "n": 1, "ticker": "AAPL"}]}], 3),
])
def test_malformed_or_drifting_census_fails_with_redacted_error(response, count) -> None:
    source = FakeCollection(rows=response, count=count)
    with pytest.raises(ShapeAuditIOError) as error:
        analyze_injected_collection(source)
    assert str(error.value) in ("INVALID_AGGREGATE_SHAPE", "INVALID_AGGREGATE_CARDINALITY")
    assert source.cursor.closed


def test_cursor_close_is_required_even_on_error() -> None:
    class BrokenCursor(FakeCursor):
        def __iter__(self) -> Iterator[object]:
            raise RuntimeError("secret source values must stay redacted")

    source = FakeCollection()
    source.cursor = BrokenCursor([aggregate()])
    with pytest.raises(ShapeAuditIOError) as error:
        analyze_injected_collection(source)
    assert str(error.value) == "READ_ONLY_AGGREGATE_FAILED"
    assert source.cursor.closed
