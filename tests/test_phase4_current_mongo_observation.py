"""Source-only current Mongo coverage pilot: synthetic and no live credentials."""
from __future__ import annotations

import json
import runpy
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

from dtrm.phase4.current_mongo_observation import (
    MAX_ROWS,
    ObservationError,
    ObservedWindowReducer,
)

START = datetime(2026, 10, 15, 20, 0, 0, tzinfo=timezone.utc)
ID1 = bytes.fromhex("000000000000000000000001")
ID2 = bytes.fromhex("000000000000000000000002")
ID3 = bytes.fromhex("000000000000000000000003")


def test_window_day_buckets_shape_counters_and_nonpromotion() -> None:
    collector = ObservedWindowReducer(START)
    collector.add(ID1, "2026-08-16", "old", ["AAA"], b"legacy")
    collector.add(ID2, "2026-10-15T01:25:00", "now", [{"ticker": "AAA"}], b"present")
    collector.add(ID3, "2026-10-16", "future", [], b"future")
    result = collector.finish(initial_count=3, final_count=3, completed_at=START)
    assert result["status"] == "PASS_CURRENT_MONGO_WINDOW_OBSERVATION"
    assert result["source_rows"] == 3
    assert result["currently_present_in_publication_window"] == 1
    assert result["currently_present_before_window"] == 1
    assert result["currently_present_after_window"] == 1
    assert result["publication_window_utc_day"] == {
        "from": "2026-08-17", "through": "2026-10-15"
    }
    shapes = result["ticker_element_shape_rows"]
    assert shapes == {
        "empty": 1, "string_only": 1, "object_only": 1,
        "mixed_or_other": 0,
    }
    daily = result["daily_publication_day_counts"]
    assert isinstance(daily, list) and len(daily) == 60
    assert sum(item["currently_present_rows"] for item in daily) == 1
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for name in (
        "atomic_mongo_snapshot_authenticated",
        "historical_source_first_seen_authenticated",
        "historical_link_first_seen_authenticated",
        "source_complete_60day_history_authenticated",
        "temporal_state_training_permitted",
        "outcomes_access_permitted",
        "mm1_execution_permitted",
        "aws_activated",
    ):
        assert result[name] is False
    encoded = json.dumps(result)
    for raw in ('"AAA"', '"legacy"', '"present"', '"future"', '"ticker": "AAA"'):
        assert raw not in encoded


def test_raw_bson_nested_mapping_looks_like_a_ticker_object() -> None:
    reducer = ObservedWindowReducer(START)
    # PyMongo RawBSONDocument is a Mapping, not necessarily an exact dict.
    reducer.add(
        ID1, "2026-10-14", "fictional",
        [MappingProxyType({"opaque": "fake"})], b"synthetic-bson",
    )
    report = reducer.finish(
        initial_count=1, final_count=1, completed_at=START,
    )
    assert report["ticker_element_shape_rows"]["object_only"] == 1


def test_memoryview_raw_bson_is_converted_at_transport_boundary() -> None:
    reducer = ObservedWindowReducer(START)
    raw = memoryview(b"synthetic-bson-larger-than-4kb" * 150)
    # The operator-only adapter converts item.raw using bytes(item.raw).
    reducer.add(ID1, "2026-10-14", "fictional", [], bytes(raw))
    report = reducer.finish(
        initial_count=1, final_count=1, completed_at=START,
    )
    assert report["source_rows"] == 1
    assert len(report["ordered_projected_bson_stream_sha256"]) == 64


def test_digest_is_bound_to_exact_ordered_projected_bson_bytes() -> None:
    def run(payload: bytes) -> str:
        collector = ObservedWindowReducer(START)
        collector.add(ID1, "2026-10-14", "synthetic", [1, "x"], payload)
        result = collector.finish(initial_count=1, final_count=1, completed_at=START)
        assert result["ticker_element_shape_rows"]["mixed_or_other"] == 1
        value = result["ordered_projected_bson_stream_sha256"]
        assert isinstance(value, str)
        return value

    assert run(b"raw-a") == run(b"raw-a")
    assert run(b"raw-a") != run(b"raw-b")


@pytest.mark.parametrize("date_value", [
    None, True, "yesterday", "2026-02-30",
    "2026-10-15/00:00:00", "2026-10-15junk", "",
])
def test_invalid_source_day_fails_closed(date_value: object) -> None:
    collector = ObservedWindowReducer(START)
    with pytest.raises(ObservationError, match="BLOCKED_CURRENT_MONGO_OBSERVATION"):
        collector.add(ID1, date_value, "x", [], b"x")


@pytest.mark.parametrize("bad_id", [b"", b"short", b"1234567890123", "notbytes"])
def test_non_objectid_binary_fails_closed(bad_id: object) -> None:
    collector = ObservedWindowReducer(START)
    with pytest.raises(ObservationError, match="BLOCKED_CURRENT_MONGO_OBSERVATION"):
        collector.add(bad_id, "2026-10-14", "x", [], b"x")  # type: ignore[arg-type]


def test_sort_duplicate_and_census_size_boundaries() -> None:
    collector = ObservedWindowReducer(START)
    collector.add(ID2, "2026-10-14", "x", [], b"x")
    with pytest.raises(ObservationError):
        collector.add(ID1, "2026-10-14", "x", [], b"x")
    with pytest.raises(ObservationError):
        collector.add(ID2, "2026-10-14", "x", [], b"x")
    collector.total = MAX_ROWS
    with pytest.raises(ObservationError):
        collector.add(ID3, "2026-10-14", "x", [], b"x")


@pytest.mark.parametrize("bad", ["", 1, None, [], True])
def test_invalid_text_fails_closed(bad: object) -> None:
    collector = ObservedWindowReducer(START)
    with pytest.raises(ObservationError):
        collector.add(ID1, "2026-10-14", bad, [], b"x")


def test_negative_counts_and_reverse_clock_cannot_finish() -> None:
    collector = ObservedWindowReducer(START)
    collector.add(ID1, "2026-10-15", "x", [], b"x")
    with pytest.raises(ObservationError):
        collector.finish(initial_count=1, final_count=2, completed_at=START)
    with pytest.raises(ObservationError):
        collector.finish(initial_count=True, final_count=1, completed_at=START)
    earlier = START.replace(hour=18)
    with pytest.raises(ObservationError):
        collector.finish(initial_count=1, final_count=1, completed_at=earlier)


def test_rejects_naive_capture_clock() -> None:
    with pytest.raises(ObservationError):
        ObservedWindowReducer(datetime(2026, 10, 15, 12))


def test_private_publish_refuses_existing_output(tmp_path: Path) -> None:
    script = (Path(__file__).resolve().parents[1] / "research" / "experiments"
              / "run_phase4_current_mongo_observed_window_v0.py")
    scope = runpy.run_path(str(script), run_name="phase4_test_only")
    write = scope["_write_exclusive"]
    output = tmp_path / "private.json"
    write(output, b"safe aggregate\n")
    assert output.read_bytes() == b"safe aggregate\n"
    with pytest.raises(ObservationError):
        write(output, b"overwrite")
    assert output.read_bytes() == b"safe aggregate\n"
    assert output.stat().st_mode & 0o077 == 0


def test_operator_runner_does_not_contact_mongo_inside_ci(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    script = (Path(__file__).resolve().parents[1] / "research" / "experiments"
              / "run_phase4_current_mongo_observed_window_v0.py")
    scope = runpy.run_path(str(script), run_name="phase4_test_only")
    main = scope["main"]
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    output = tmp_path / "should-not-exist.json"
    assert main(["--output", str(output)]) == 1
    assert not output.exists()
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed"
    assert result["error_code"] == "BLOCKED_CURRENT_MONGO_OBSERVATION"
