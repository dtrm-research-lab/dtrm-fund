"""Synthetic unit/functional tests; no production source or configuration is used."""

from __future__ import annotations

import hashlib
import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from dtrm.phase4 import retrospective_salvage_io as io
from dtrm.phase4.retrospective_salvage import (
    AMENDMENT_COMMIT,
    BATCH_SIZE,
    CENSUS_CAP,
    CLIENT_TIMEOUT_MS,
    CONTRACT_SHA256,
    CURSOR_LIMIT,
    GRAPH,
    INITIAL_REGISTRATION_COMMIT,
    LAG_LABELS,
    PROJECTED_PATHS,
    SERVER_SELECTION_TIMEOUT_MS,
    SOCKET_TIMEOUT_MS,
    SalvageError,
    SyntheticObjectId,
    aggregate_rows,
    assess_decision,
    build_census_query_spec,
    build_salvage_report,
    normalize_synthetic_document,
    parse_audit_instant,
    parse_writer_manifest,
    serialize_salvage_report,
)
from dtrm.phase4.retrospective_salvage_io import (
    SalvageIOError,
    read_registered_census,
    run_synthetic_audit,
)
from dtrm.phase4.source_feasibility import IndexCounts, sanitize_indexes
from dtrm.phase4.source_metadata import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase4_retrospective_salvage_v0.json"
EXPECTED = ROOT / "research/reports/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_SYNTHETIC_V0.json"
CONTRACT = ROOT / "research/contracts/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_AUDIT_V0.md"
STARTED = datetime(2025, 2, 1, tzinfo=timezone.utc)


@pytest.fixture
def payload():
    return json.loads(FIXTURE.read_text())


@pytest.fixture
def report(payload):
    return run_synthetic_audit(payload)


@pytest.fixture
def writer(payload):
    return parse_writer_manifest(payload["writer_manifest"])


def oid_at(value: datetime, suffix: int = 1):
    timestamp = int(value.timestamp())
    return {"$oid": f"{timestamp:08x}{suffix:016x}"}


def row_at(value: datetime, provider_day: str | None = None):
    document = {"_id": oid_at(value), "text": "synthetic"}
    if provider_day is not None:
        document["raw"] = {"publishedDate": provider_day}
    return normalize_synthetic_document(document)


def bins(items):
    return {item.label: item.n for item in items}


def test_contract_binding_and_query_scope_are_fixed_and_fresh():
    assert hashlib.sha256(CONTRACT.read_bytes()).hexdigest() == CONTRACT_SHA256
    assert INITIAL_REGISTRATION_COMMIT == "b38b3fc1851e1f636240e7fa418da2dcc933db8d"
    assert AMENDMENT_COMMIT == "a1e7ce59d9e99a0b7d36d3989664508536dbb0ae"
    spec = build_census_query_spec()
    assert spec.projected_paths == PROJECTED_PATHS
    assert spec.cursor_limit == CURSOR_LIMIT == CENSUS_CAP + 1 == 250_001
    assert spec.batch_size == BATCH_SIZE == 500
    assert (spec.client_timeout_ms, spec.server_selection_timeout_ms, spec.socket_timeout_ms) == (
        CLIENT_TIMEOUT_MS,
        SERVER_SELECTION_TIMEOUT_MS,
        SOCKET_TIMEOUT_MS,
    ) == (180_000, 10_000, 30_000)
    assert spec.retry_reads is False
    query = spec.to_dict()
    assert query["count_filter"] == query["cursor_filter"] == {}
    assert query["sort"] == {"_id": 1}
    assert list(query["projection"]) == list(PROJECTED_PATHS)
    for forbidden in ("return", "target", "label", "price", "score", "$out", "$merge"):
        assert forbidden not in json.dumps(query).lower()
    query["cursor_limit"] = 1
    assert build_census_query_spec().cursor_limit == 250_001


def test_fixture_roundtrip_is_reproducible_order_invariant_and_blocked(payload, report):
    assert serialize_salvage_report(report) == EXPECTED.read_text()
    payload["documents"].reverse()
    payload["indexes"].reverse()
    reordered = run_synthetic_audit(payload)
    assert serialize_salvage_report(reordered) == EXPECTED.read_text()
    assert reordered["scientific_assessment"] == "RETROSPECTIVE_PROXY_PARTIAL"
    assert reordered["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for flag in (
        "decision_clock_authenticated",
        "snapshot_verified",
        "writer_runtime_evidence_authenticated",
        "live_bson_semantics_validated",
        "history_construction_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
        "production_source_accessed",
    ):
        assert reordered[flag] is False


def test_fixture_exact_aggregate_diagnostics(report):
    assert report["total_documents"] == 10
    assert report["object_ids"] == {
        "genuine": 9,
        "non_object_id": 1,
        "structurally_eligible": 9,
        "semantics": "synthetic_extended_json_not_live_bson_evidence",
        "utc_months": [
            {"label": "2024-12", "n": 1},
            {"label": "2025-01", "n": 7},
            {"label": "2025-02", "n": 1},
        ],
        "future_clock_anomalies": 1,
        "provider_day_lag_bins": [
            {"label": label, "n": n}
            for label, n in zip(LAG_LABELS, (1, 1, 1, 2, 1, 1, 0, 0, 2), strict=True)
        ],
    }
    assert report["urls"] == {
        "keyed_rows": 9,
        "unkeyed_rows": 1,
        "distinct_hashed_groups": 5,
        "singleton_groups": 1,
        "repeated_groups": 4,
        "repeated_groups_with_no_content_digest": 1,
        "repeated_groups_with_one_content_digest": 2,
        "repeated_groups_with_multiple_content_digests": 1,
        "repeated_group_size_bins": [
            {"label": "2", "n": 4},
            {"label": "3_5", "n": 0},
            {"label": "6_20", "n": 0},
            {"label": "gt_20", "n": 0},
        ],
    }
    assert report["matched_tickers"]["malformed_elements"] == 2
    assert report["matched_tickers"]["rows_with_exact_duplicates"] == 1
    assert report["dedupe_keys"] == {
        "missing": 1,
        "present": 9,
        "distinct_hashed_keys": 7,
        "repeated_key_groups": 2,
    }
    assert report["reconciliation"]["status"] == "PASS"
    assert set(report["reconciliation"].values()) >= {10, 14, "PASS"}


@pytest.mark.parametrize(
    "delta,expected",
    [
        (-400, "le_minus_2"),
        (-2, "le_minus_2"),
        (-1, "minus_1"),
        (0, "zero"),
        (1, "plus_1"),
        (2, "plus_2_7"),
        (7, "plus_2_7"),
        (8, "plus_8_30"),
        (30, "plus_8_30"),
        (31, "plus_31_365"),
        (365, "plus_31_365"),
        (366, "gt_365"),
    ],
)
def test_every_lag_boundary(delta, expected):
    provider = "2025-01-01"
    observation = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=delta)
    counts = aggregate_rows((row_at(observation, provider),), STARTED)
    assert bins(counts.lag_bins)[expected] == 1
    assert sum(bins(counts.lag_bins).values()) == 1


@pytest.mark.parametrize(
    "provider,parse",
    [
        ("2025-02-29", "invalid"),
        ("2025-13-01", "invalid"),
        ("not-a-date", "invalid"),
        ("", "invalid"),
        ("2024-02-29", "parsed"),
        ("2025-01-01 13:00:00", "parsed"),
        ("2025-01-01T13:00:00Z", "parsed"),
    ],
)
def test_provider_days_use_only_valid_leading_calendar_day(provider, parse):
    row = normalize_synthetic_document(
        {"_id": oid_at(STARTED), "raw": {"publishedDate": provider}}
    )
    assert row.provider_parse == parse
    assert row.provider_origin == "raw.publishedDate"


def test_provider_path_precedence_does_not_fall_through_invalid_string():
    row = normalize_synthetic_document(
        {
            "_id": oid_at(STARTED),
            "date": "2025-01-03",
            "raw": {"publishedDate": "invalid", "date": "2025-01-02"},
        }
    )
    assert row.provider_origin == "raw.publishedDate"
    assert row.provider_parse == "invalid"
    assert row.provider_day is None


def test_objectid_and_non_objectid_are_distinct_and_frozen():
    oid = SyntheticObjectId.parse("67810bc00000000000000001")
    assert oid.generation_time == datetime(2025, 1, 10, 12, tzinfo=timezone.utc)
    with pytest.raises(FrozenInstanceError):
        oid.hex_value = "0" * 24
    object_row = normalize_synthetic_document({"_id": {"$oid": oid.hex_value}})
    string_row = normalize_synthetic_document({"_id": oid.hex_value})
    counts = aggregate_rows((object_row, string_row), STARTED)
    assert (counts.genuine_object_ids, counts.non_object_ids) == (1, 1)


@pytest.mark.parametrize(
    "bad",
    [
        {"$oid": "abc"},
        {"$oid": "A" * 24},
        {"$oid": "z" * 24},
        {"$oid": "0" * 24, "extra": 1},
    ],
)
def test_invalid_extended_objectid_is_rejected(bad):
    with pytest.raises(SalvageError):
        normalize_synthetic_document({"_id": bad})


def test_future_clock_anomaly_is_strictly_after_five_minutes():
    rows = (
        row_at(STARTED + timedelta(minutes=5), None, ),
        row_at(STARTED + timedelta(minutes=5, seconds=1), None),
    )
    assert aggregate_rows(rows, STARTED).future_clock_anomalies == 1


def test_exact_utf8_hashing_has_no_semantic_normalization():
    composed = normalize_synthetic_document({"_id": 1, "text": "é"})
    decomposed = normalize_synthetic_document({"_id": 2, "text": "e\u0301"})
    assert composed.content_digest == hashlib.sha256("é".encode("utf-8")).hexdigest()
    assert composed.content_digest != decomposed.content_digest
    counts = aggregate_rows((composed, decomposed), STARTED)
    assert counts.distinct_content_digests == 2


def test_url_fragment_is_removed_but_other_components_are_not_normalized():
    first = normalize_synthetic_document(
        {"_id": 1, "raw": {"url": " https://Example.invalid/a?x=1#one "}}
    )
    same = normalize_synthetic_document(
        {"_id": 2, "raw": {"url": "https://Example.invalid/a?x=1#two"}}
    )
    changed_case = normalize_synthetic_document(
        {"_id": 3, "raw": {"url": "https://example.invalid/a?x=1"}}
    )
    changed_slash = normalize_synthetic_document(
        {"_id": 4, "raw": {"url": "https://Example.invalid/a/?x=1"}}
    )
    assert first.url_digest == same.url_digest
    assert first.url_digest not in {changed_case.url_digest, changed_slash.url_digest}


def test_url_and_source_id_precedence_remain_separate():
    row = normalize_synthetic_document(
        {
            "_id": 1,
            "raw": {
                "id": "first-id",
                "articleId": "second-id",
                "url": "https://first.invalid",
                "link": "https://second.invalid",
            },
        }
    )
    assert row.source_id_origin == "raw.id"
    assert row.source_id_states == ("present", "present", "missing")
    assert row.url_digest == hashlib.sha256(b"https://first.invalid").hexdigest()
    assert row.url_digest != hashlib.sha256(b"first-id").hexdigest()


@pytest.mark.parametrize("size,label", [(2, "2"), (3, "3_5"), (5, "3_5"), (6, "6_20"), (20, "6_20"), (21, "gt_20")])
def test_repeated_url_group_size_boundaries(size, label):
    rows = tuple(
        normalize_synthetic_document(
            {"_id": position, "text": f"version-{position}", "raw": {"url": "https://same.invalid"}}
        )
        for position in range(size)
    )
    counts = aggregate_rows(rows, STARTED)
    assert bins(counts.repeated_url_group_sizes)[label] == 1
    assert counts.repeated_url_groups_multiple_content == 1


def test_source_id_presence_distinguishes_null_missing_and_selected_origin():
    row = normalize_synthetic_document(
        {"_id": 1, "raw": {"id": None, "articleId": "", "article_id": "selected"}}
    )
    assert row.source_id_states == ("null", "present", "present")
    assert row.source_id_origin == "raw.article_id"


@pytest.mark.parametrize(
    "value,shape,length,malformed,duplicate",
    [
        (None, "non_array", None, 0, False),
        ([], "empty", None, 0, False),
        (["A"], "nonempty", "1", 0, False),
        (["A", "A", 4], "nonempty", "2_5", 1, True),
        (["A"] * 6, "nonempty", "6_20", 0, True),
        ([f"T{i}" for i in range(21)], "nonempty", "gt_20", 0, False),
    ],
)
def test_ticker_shapes_lengths_malformed_and_duplicates(value, shape, length, malformed, duplicate):
    row = normalize_synthetic_document({"_id": 1, "matched_tickers": value})
    assert (
        row.ticker_shape,
        row.ticker_length_bin,
        row.ticker_malformed_elements,
        row.ticker_has_duplicate,
    ) == (shape, length, malformed, duplicate)


def test_missing_tickers_and_missing_dedupe_are_not_null():
    missing = normalize_synthetic_document({"_id": 1})
    null = normalize_synthetic_document({"_id": 2, "dedupe_key": None})
    counts = aggregate_rows((missing, null), STARTED)
    assert missing.ticker_shape == "missing"
    assert (counts.dedupe_missing, counts.dedupe_present, counts.distinct_dedupe_keys) == (
        1,
        1,
        1,
    )


def test_decision_lattice_returns_exactly_one_state(payload, writer):
    rows = tuple(normalize_synthetic_document(item) for item in payload["documents"])
    counts = aggregate_rows(rows, STARTED)
    candidate = replace(
        writer,
        relevant_writers="bounded",
        deployed_intervals="bounded",
        later_mutation="absent",
        client_clock="bounded",
        runtime_immutability="supported",
        write_authority="bounded_exclusive",
    )
    assert assess_decision(counts, writer) == "RETROSPECTIVE_PROXY_PARTIAL"
    assert assess_decision(counts, candidate) == "RETROSPECTIVE_PROXY_CANDIDATE"
    for contradicted in (
        replace(candidate, id_assignment="external_unbounded"),
        replace(candidate, write_operations="mutating"),
        replace(candidate, write_operations="unknown"),
        replace(candidate, atomic_text_tickers="contradicted"),
        replace(candidate, atomic_text_tickers="unknown"),
        replace(candidate, later_mutation="present"),
        replace(candidate, client_clock="unbounded"),
        replace(candidate, runtime_immutability="contradicted"),
    ):
        assert assess_decision(counts, contradicted) == "RETROSPECTIVE_PROXY_CONTRADICTED"


def test_empty_and_no_objectid_censuses_are_contradicted(writer):
    empty = aggregate_rows((), STARTED)
    no_objectid = aggregate_rows((normalize_synthetic_document({"_id": "legacy"}),), STARTED)
    with pytest.raises(FrozenInstanceError):
        no_objectid.total_documents = 2
    assert assess_decision(empty, writer) == "RETROSPECTIVE_PROXY_CONTRADICTED"
    assert assess_decision(no_objectid, writer) == "RETROSPECTIVE_PROXY_CONTRADICTED"


def test_candidate_still_cannot_authenticate_or_train(payload, writer):
    candidate = replace(
        writer,
        relevant_writers="bounded",
        deployed_intervals="bounded",
        later_mutation="absent",
        client_clock="bounded",
        runtime_immutability="supported",
        write_authority="bounded_exclusive",
    )
    rows = tuple(normalize_synthetic_document(item) for item in payload["documents"])
    result = build_salvage_report(
        rows,
        sanitize_indexes(payload["indexes"]),
        candidate,
        STARTED,
        STARTED + timedelta(seconds=1),
        len(rows),
    )
    assert result["scientific_assessment"] == "RETROSPECTIVE_PROXY_CANDIDATE"
    assert result["scientific_status"] == "BLOCKED_DECISION_CLOCK_BINDING"
    for flag in (
        "decision_clock_authenticated",
        "snapshot_verified",
        "writer_runtime_evidence_authenticated",
        "live_bson_semantics_validated",
        "history_construction_permitted",
        "training_permitted",
    ):
        assert result[flag] is False


@pytest.mark.parametrize(
    "case",
    ["extra", "missing", "bad_mode", "bad_writer", "bad_operation", "bad_clock"],
)
def test_writer_manifest_rejects_unregistered_states(payload, case):
    manifest = payload["writer_manifest"]
    if case == "extra":
        manifest["conclusion"] = "candidate"
    elif case == "missing":
        del manifest["client_clock"]
    elif case == "bad_mode":
        manifest["mode"] = "live"
    elif case == "bad_writer":
        manifest["relevant_writers"] = "probably"
    elif case == "bad_operation":
        manifest["write_operations"] = "upsert_when_helpful"
    else:
        manifest["client_clock"] = "ignore_anomalies"
    with pytest.raises(SalvageError):
        parse_writer_manifest(manifest)


@pytest.mark.parametrize(
    "document",
    [
        {"_id": 1, "target": 1.0},
        {"_id": 1, "price": 20},
        {"_id": 1, "raw": {"url": "safe", "outcome": 1}},
        {"text": "missing id"},
    ],
)
def test_document_projection_rejects_outside_or_missing_keys(document):
    with pytest.raises(SalvageError):
        normalize_synthetic_document(document)


def test_report_hashes_and_aggregate_only_serialization(payload, report):
    evidence = {
        key: report[key]
        for key in (
            "total_documents",
            "field_types",
            "object_ids",
            "provider_days",
            "text",
            "urls",
            "source_ids",
            "matched_tickers",
            "dedupe_keys",
            "reconciliation",
            "indexes",
            "writer_findings",
        )
    }
    assert report["pipeline_sha256"] == canonical_sha256(build_census_query_spec().to_dict())
    assert report["writer_manifest_sha256"] == canonical_sha256(payload["writer_manifest"])
    assert report["evidence_sha256"] == canonical_sha256(evidence)
    encoded = serialize_salvage_report(report)
    for forbidden in (
        "Alpha exact text",
        "CONFIDENTIAL_SOURCE_ONE",
        "PRIVATE_PROVIDER_ID_ONE",
        "PRIVATE_DEDUPE_ONE",
        "https://news.invalid",
        "PRIVATE_LEGACY_ID",
        '"AAA"',
    ):
        assert forbidden not in encoded


def test_serializer_rejects_schema_expansion_promotion_and_credentials(report):
    expanded = {**report, "source_example": "secret"}
    with pytest.raises(SalvageError):
        serialize_salvage_report(expanded)
    promoted = {**report, "training_permitted": True}
    with pytest.raises(SalvageError):
        serialize_salvage_report(promoted)
    credential = deepcopy(report)
    credential["scientific_status"] = "mongodb+srv://private"
    with pytest.raises(SalvageError):
        serialize_salvage_report(credential)


@pytest.mark.parametrize(
    "value",
    ["2025-01-01", "", None, "2025-01-01T00:00:00", "invalid"],
)
def test_audit_instant_requires_valid_timezone(value):
    if value == "2025-01-01T00:00:00Z":
        pytest.fail("parameter is unexpectedly valid")
    with pytest.raises(SalvageError):
        parse_audit_instant(value, "audit")


def test_audit_interval_and_count_validation(payload, writer):
    rows = (normalize_synthetic_document(payload["documents"][0]),)
    indexes = IndexCounts(0, 0, 0, 0)
    with pytest.raises(SalvageError):
        build_salvage_report(rows, indexes, writer, STARTED, STARTED - timedelta(seconds=1), 1)
    for bad in (-1, True, CENSUS_CAP + 1):
        with pytest.raises(SalvageError):
            build_salvage_report(rows, indexes, writer, STARTED, STARTED, bad)


class Cursor:
    def __init__(self, values, fail_at=None, fail_close=False):
        self.values = values
        self.fail_at = fail_at
        self.fail_close = fail_close
        self.closed = False
        self.consumed = 0

    def __iter__(self):
        for position, value in enumerate(self.values):
            self.consumed += 1
            if position == self.fail_at:
                raise RuntimeError("mongodb://private-source-value")
            yield value

    def close(self):
        self.closed = True
        if self.fail_close:
            raise RuntimeError("private close detail")


class Port:
    def __init__(self, count, documents=(), indexes=(), failure=None):
        self.count = count
        self.row_cursor = Cursor(documents, 0 if failure == "rows" else None)
        self.index_cursor = Cursor(indexes, 0 if failure == "indexes" else None)
        self.failure = failure
        self.closed = False
        self.calls = []

    def exact_count(self, spec):
        self.calls.append(("count", spec))
        if self.failure == "count":
            raise RuntimeError("mongodb://private-count-error")
        return self.count

    def open_census(self, spec):
        self.calls.append(("census", spec))
        if self.failure == "open":
            raise RuntimeError("mongodb://private-open-error")
        return self.row_cursor

    def open_indexes(self, spec):
        self.calls.append(("indexes", spec))
        return self.index_cursor

    def close(self):
        self.closed = True


def test_preliminary_count_rejects_before_stream_and_closes(monkeypatch):
    monkeypatch.setattr(io, "CENSUS_CAP", 3)
    port = Port(4, documents=[{"_id": 1}])
    with pytest.raises(SalvageIOError, match="SOURCE_EXCEEDS_REGISTERED_BOUND"):
        read_registered_census(port)
    assert [name for name, _ in port.calls] == ["count"]
    assert port.closed


def test_cap_plus_one_rejects_race_with_bounded_consumption_and_closure(monkeypatch):
    monkeypatch.setattr(io, "CENSUS_CAP", 3)
    monkeypatch.setattr(io, "CURSOR_LIMIT", 4)
    port = Port(3, documents=[{"_id": i} for i in range(6)])
    with pytest.raises(SalvageIOError, match="SOURCE_EXCEEDS_REGISTERED_BOUND"):
        read_registered_census(port)
    assert port.row_cursor.consumed == 4
    assert port.row_cursor.closed and port.closed
    assert [name for name, _ in port.calls] == ["count", "census"]


def test_non_atomic_count_delta_is_retained_without_claiming_snapshot():
    port = Port(2, documents=[{"_id": 1}, {"_id": 2}, {"_id": 3}])
    result = read_registered_census(port)
    assert result.preliminary_count == 2
    assert len(result.documents) == 3
    assert port.row_cursor.closed and port.index_cursor.closed and port.closed


@pytest.mark.parametrize("failure", ["count", "open", "rows", "indexes"])
def test_boundary_redacts_failures_and_closes_every_open_resource(failure):
    port = Port(1, documents=[{"_id": 1}], indexes=[{"key": {"_id": 1}}], failure=failure)
    with pytest.raises(SalvageIOError, match="CENSUS_READ_FAILED") as error:
        read_registered_census(port)
    assert "private" not in str(error.value)
    assert port.closed
    if failure == "rows":
        assert port.row_cursor.closed
    if failure == "indexes":
        assert port.row_cursor.closed and port.index_cursor.closed


def test_index_catalog_consumption_is_bounded_and_closed(monkeypatch):
    monkeypatch.setattr(io, "INDEX_LIMIT", 3)
    port = Port(0, indexes=[{"key": {"_id": 1}}] * 5)
    with pytest.raises(SalvageIOError, match="INDEX_CATALOG_EXCEEDS_BOUND"):
        read_registered_census(port)
    assert port.index_cursor.consumed == 3
    assert port.index_cursor.closed and port.closed


def test_fixed_query_spec_reaches_every_port_call():
    port = Port(1, documents=[{"_id": 1}])
    read_registered_census(port)
    assert len(port.calls) == 3
    assert all(spec == build_census_query_spec() for _, spec in port.calls)


@pytest.fixture
def cli():
    path = ROOT / "research/experiments/run_phase4_retrospective_salvage.py"
    return runpy.run_path(str(path))["main"]


def test_cli_synthetic_roundtrip_has_no_live_mode(cli, tmp_path, capsys):
    output = tmp_path / "report.json"
    assert cli(["--synthetic-input", str(FIXTURE), "--output", str(output)]) == 0
    assert output.read_bytes() == EXPECTED.read_bytes()
    message = json.loads(capsys.readouterr().out)
    assert message == {
        "execution_mode": "synthetic",
        "graph": GRAPH,
        "scientific_assessment": "RETROSPECTIVE_PROXY_PARTIAL",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "status": "succeeded",
        "total_documents": 10,
    }
    with pytest.raises(SystemExit):
        cli(["--mongo", "--output", str(tmp_path / "forbidden.json")])


def test_cli_refuses_overwrite_and_symlink_before_read(cli, tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(cli.__globals__, "run_synthetic_audit", lambda value: pytest.fail("read"))
    output = tmp_path / "report.json"
    output.write_text("original")
    assert cli(["--synthetic-input", str(FIXTURE), "--output", str(output)]) == 1
    assert output.read_text() == "original"
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"
    output.unlink()
    output.symlink_to(tmp_path / "missing-target")
    assert cli(["--synthetic-input", str(FIXTURE), "--output", str(output)]) == 1
    assert output.is_symlink()


def test_cli_invalid_input_is_redacted_and_creates_no_report(cli, tmp_path, payload, capsys):
    payload["documents"][0]["outcome"] = "PRIVATE_OUTCOME_VALUE"
    source = tmp_path / "input.json"
    source.write_text(json.dumps(payload))
    output = tmp_path / "report.json"
    assert cli(["--synthetic-input", str(source), "--output", str(output)]) == 1
    message = capsys.readouterr().out
    assert json.loads(message)["error_code"] == "INVALID_SYNTHETIC_INPUT"
    assert "PRIVATE_OUTCOME_VALUE" not in message
    assert not output.exists()


def test_cli_nonfinite_json_and_missing_parent_fail_closed(cli, tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text('{"private": NaN}')
    output = tmp_path / "report.json"
    assert cli(["--synthetic-input", str(source), "--output", str(output)]) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "INVALID_SYNTHETIC_INPUT"
    assert cli(
        ["--synthetic-input", str(FIXTURE), "--output", str(tmp_path / "missing" / "report.json")]
    ) == 1
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_PARENT_MISSING"
