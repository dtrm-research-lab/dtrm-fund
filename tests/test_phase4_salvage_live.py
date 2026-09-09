"""Live-adapter tests using injected configuration/clients, never operator secrets."""

import ast
import hashlib
import importlib
import json
import logging
import runpy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

import pytest

from dtrm.phase4 import retrospective_salvage as domain
from dtrm.phase4 import retrospective_salvage_io as census_io
from dtrm.phase4 import salvage_live_io as io
from dtrm.phase4.retrospective_salvage_io import SalvageIOError
from dtrm.phase4.salvage_live_report import (
    CONTRACT_PATH,
    CONTRACT_SHA256,
    REGISTRATION,
    serialize_live_report,
)

ROOT = Path(__file__).resolve().parents[1]
STARTED = datetime(2025, 2, 1, tzinfo=timezone.utc)
CLI = ROOT / "research/experiments/run_phase4_retrospective_salvage_live.py"


def forbidden_import(name):
    pytest.fail(f"unexpected import: {name}")


def test_registration_identity():
    assert REGISTRATION == "13625046e8b258f085fab59966a31937786a5eec"
    assert hashlib.sha256((ROOT / CONTRACT_PATH).read_bytes()).hexdigest() == CONTRACT_SHA256


def test_missing_configuration_before_import():
    with pytest.raises(SalvageIOError, match="MISSING_LOCAL_CREDENTIALS"):
        io.run_live_audit(None, env={}, importer=forbidden_import)


def test_uri_precedence_does_not_read_fallback():
    class Config(dict):
        def get(self, key, default=None):
            assert key != "db_password"
            return super().get(key, default)
    assert io.configured_uri(None, Config(MONGO_URI="synthetic-uri")) == ("synthetic-uri", False)


def test_fallback_escapes_password():
    result, isolated = io.configured_uri(None, {"db_password": "a/@:$ ?"})
    assert "a%2F%40%3A%24%20%3F" in result
    assert not isolated


@pytest.mark.parametrize("env", [
    {"GITHUB_ACTIONS": "true"},
    {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1"},
    {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1", "MONGO_URI": "private"},
    {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1", "MONGO_URI": io.LOCAL_URI + "&x=1"},
])
def test_ci_fails_before_import(env):
    with pytest.raises(SalvageIOError, match="LIVE_SOURCE_FORBIDDEN_IN_CI"):
        io.run_live_audit(None, env=env, importer=forbidden_import)


def test_ci_literal_allowlist_and_envfile_refusal(tmp_path):
    env = {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1", "MONGO_URI": io.LOCAL_URI}
    assert io.configured_uri(None, env) == (io.LOCAL_URI, True)
    with pytest.raises(SalvageIOError, match="LIVE_SOURCE_FORBIDDEN_IN_CI"):
        io.configured_uri(tmp_path / "do-not-read", env, forbidden_import)


def test_explicit_dotenv_without_override(tmp_path):
    source = tmp_path / "synthetic.env"
    source.write_text("MONGO_URI=not-used\n")
    module = ModuleType("dotenv")
    calls = []
    module.load_dotenv = lambda **kw: calls.append(kw)
    assert io.configured_uri(source, {"MONGO_URI": "existing"}, lambda name: module)[0] == "existing"
    assert calls == [{"dotenv_path": source, "override": False}]


@pytest.mark.parametrize("kind", ["missing", "directory", "symlink"])
def test_bad_envfile_before_loader(tmp_path, kind):
    source = tmp_path / "synthetic.env"
    if kind == "directory":
        source.mkdir()
    elif kind == "symlink":
        source.symlink_to(tmp_path / "absent")
    with pytest.raises(SalvageIOError, match="INVALID_ENV_FILE"):
        io.configured_uri(source, {}, forbidden_import)


def test_import_and_loader_errors_are_redacted(tmp_path):
    def failing(name):
        raise RuntimeError("PRIVATE_DETAIL")
    with pytest.raises(SalvageIOError, match="DRIVER_IMPORT_FAILED"):
        io.run_live_audit(None, {"MONGO_URI": "synthetic"}, failing)
    source = tmp_path / "synthetic.env"
    source.write_text("")
    with pytest.raises(SalvageIOError, match="ENV_LOAD_FAILED"):
        io.configured_uri(source, {}, failing)


class Cursor:
    def __init__(self, rows, failure=None):
        self.rows = rows
        self.failure = failure
        self.closed = False
        self.consumed = 0

    def __iter__(self):
        for row in self.rows:
            if self.failure == "iterate":
                raise RuntimeError("PRIVATE_CURSOR")
            self.consumed += 1
            yield row

    def close(self):
        self.closed = True
        if self.failure == "close":
            raise RuntimeError("PRIVATE_CLOSE")


class Client:
    def __init__(self, rows, failure=None, count=None):
        self.calls = []
        self.closed = False
        self.failure = failure
        self.count = len(rows) if count is None else count
        self.rows = Cursor(rows, "iterate" if failure == "rows" else
                           "close" if failure == "row_close" else None)
        self.indexes = Cursor([{"key": {"_id": 1}}], "iterate" if failure == "indexes" else None)

    def __getitem__(self, name):
        self.calls.append(("namespace", name))
        return self

    def with_options(self, **kwargs):
        self.calls.append(("options", kwargs))
        if self.failure == "options":
            raise RuntimeError("PRIVATE_OPTIONS")
        return self

    def count_documents(self, query):
        self.calls.append(("count", query))
        if self.failure == "count":
            raise RuntimeError("PRIVATE_COUNT")
        return self.count

    def find(self, query, **kwargs):
        self.calls.append(("find", query, kwargs))
        return self.rows

    def list_indexes(self):
        self.calls.append(("indexes",))
        return self.indexes

    def close(self):
        self.closed = True
        if self.failure == "client_close":
            raise RuntimeError("PRIVATE_CLIENT")


class SyntheticCodec:
    normalize = staticmethod(domain.normalize_synthetic_document)


def read_fake(client):
    def factory(uri, **kwargs):
        assert uri == io.LOCAL_URI
        assert kwargs == dict(timeoutMS=180000, serverSelectionTimeoutMS=10000,
                              socketTimeoutMS=30000, retryReads=False)
        return client
    return io.fetch_live_audit(factory, io.LOCAL_URI, "majority-test", SyntheticCodec(),
                              isolated_test=True, clock=lambda: STARTED)


@pytest.fixture
def report():
    return read_fake(Client([{"_id": {"$oid": "67810bc00000000000000001"},
                              "text": "PRIVATE_TEXT", "raw": {"url": "PRIVATE_URL"}}]))


def test_exact_transport_and_all_closures():
    client = Client([{"_id": 1}])
    report = read_fake(client)
    assert client.calls[:3] == [
        ("namespace", "trumpMinMax"), ("namespace", "trumpNews"),
        ("options", {"read_concern": "majority-test"}),
    ]
    assert client.calls[3] == ("count", {})
    assert client.calls[4] == ("find", {}, {
        "projection": {path: 1 for path in domain.PROJECTED_PATHS},
        "sort": [("_id", 1)], "limit": 250001, "batch_size": 500,
    })
    assert client.rows.closed and client.indexes.closed and client.closed
    assert report.to_dict()["scientific_assessment"] == "RETROSPECTIVE_PROXY_CONTRADICTED"


@pytest.mark.parametrize("failure", ["options", "count", "rows", "indexes", "row_close", "client_close"])
def test_failure_paths_close_and_redact(failure):
    client = Client([{"_id": 1}], failure)
    with pytest.raises(SalvageIOError) as caught:
        read_fake(client)
    assert "PRIVATE" not in str(caught.value)
    assert client.closed
    if failure in ("rows", "indexes", "row_close"):
        assert client.rows.closed
    if failure == "indexes":
        assert client.indexes.closed


def test_preliminary_and_cursor_caps(monkeypatch):
    monkeypatch.setattr(census_io, "CENSUS_CAP", 2)
    monkeypatch.setattr(census_io, "CURSOR_LIMIT", 3)
    over = Client([{"_id": i} for i in range(4)])
    with pytest.raises(SalvageIOError, match="SOURCE_EXCEEDS_REGISTERED_BOUND"):
        read_fake(over)
    assert over.rows.consumed == 0 and over.closed
    race = Client([{"_id": i} for i in range(5)], count=2)
    with pytest.raises(SalvageIOError, match="SOURCE_EXCEEDS_REGISTERED_BOUND"):
        read_fake(race)
    assert race.rows.consumed == 3 and race.rows.closed and race.closed


def test_live_report_immutable_recomputed_and_blocked(report):
    value = report.to_dict()
    assert value["scientific_assessment"] == "RETROSPECTIVE_PROXY_PARTIAL"
    assert value["live_bson_semantics_validated"] is True
    assert value["production_source_accessed"] is False
    for key in ("training_permitted", "history_construction_permitted", "outcome_access_permitted",
                "writer_runtime_evidence_authenticated", "snapshot_verified", "decision_clock_authenticated"):
        assert value[key] is False
    assert "PRIVATE" not in serialize_live_report(report)
    value["source"]["leak"] = "PRIVATE"
    value["evidence_sha256"] = "wrong"
    with pytest.raises(domain.SalvageError):
        serialize_live_report(value)
    assert "PRIVATE" not in serialize_live_report(report)
    with pytest.raises(FrozenInstanceError):
        report.preliminary_count = 10


def test_report_rejects_nested_source_injection(report):
    bad = replace(report.counts, object_id_months=(domain.CountBin("PRIVATE", 1),))
    with pytest.raises(domain.SalvageError):
        serialize_live_report(replace(report, counts=bad))


def test_quiet_driver_restores_logging():
    previous = logging.root.manager.disable
    with pytest.raises(RuntimeError), io.quiet_driver():
        assert logging.root.manager.disable == logging.CRITICAL
        raise RuntimeError()
    assert logging.root.manager.disable == previous


def test_cli_no_overwrite_preflight_and_redacted_arguments(tmp_path, capsys):
    entry = runpy.run_path(str(CLI))
    main = entry["main"]
    main.__globals__["run_live_audit"] = lambda *args: pytest.fail("configuration accessed")
    output = tmp_path / "exists.json"
    output.write_text("original")
    assert main(["--output", str(output)]) == 1
    assert output.read_text() == "original"
    assert main(["--output", str(tmp_path / "missing" / "out.json")]) == 1
    assert main(["--uri", "PRIVATE_TOKEN"]) == 1
    captured = capsys.readouterr()
    assert "PRIVATE_TOKEN" not in captured.out + captured.err


def test_cli_roundtrip_and_partial_write_never_published(tmp_path, monkeypatch, report, capsys):
    entry = runpy.run_path(str(CLI))
    entry["main"].__globals__["run_live_audit"] = lambda *args: report
    output = tmp_path / "report.json"
    assert entry["main"](["--output", str(output)]) == 0
    assert output.read_text() == serialize_live_report(report)
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded"
    def fail_sync(fd):
        raise OSError("PRIVATE_DISK")
    monkeypatch.setattr(entry["os"], "fsync", fail_sync)
    target = tmp_path / "failed.json"
    assert entry["main"](["--output", str(target)]) == 1
    assert not target.exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["report.json"]


def test_bson_objectid_not_extended_json():
    bson = pytest.importorskip("bson")
    codec = io.BSONCodec()
    identifier = bson.ObjectId("67810bc00000000000000001")
    actual = codec.normalize({"_id": identifier})
    assert actual.id_time == identifier.generation_time
    assert actual.field_types[0] == "objectId"
    impostor = codec.normalize({"_id": {"$oid": str(identifier)}})
    assert impostor.id_time is None and impostor.field_types[0] == "object"


@pytest.mark.parametrize("type_name,value_name", [
    ("long", "int64"), ("decimal", "decimal128"), ("binData", "binary"),
    ("timestamp", "timestamp"), ("date", "date"), ("regex", "regex"),
])
def test_extended_bson_counted_and_hashed(type_name, value_name):
    bson = pytest.importorskip("bson")
    values = {
        "int64": bson.Int64(1), "decimal128": bson.Decimal128("1.2"),
        "binary": bson.Binary(b"private"), "timestamp": bson.Timestamp(1, 2),
        "date": STARTED, "regex": bson.Regex("private"),
    }
    codec = io.BSONCodec()
    value = values[value_name]
    assert codec.type_name(value) == type_name
    row = codec.normalize({"_id": 1, "dedupe_key": value})
    assert row.field_types[5] == type_name
    assert len(row.dedupe_digest) == 64


def test_real_fixture_normalization_matches_synthetic():
    bson = pytest.importorskip("bson")
    payload = json.loads((ROOT / "tests/fixtures/phase4_retrospective_salvage_v0.json").read_text())
    codec = io.BSONCodec()
    for document in payload["documents"]:
        synthetic = domain.normalize_synthetic_document(document)
        live = dict(document)
        if isinstance(live["_id"], dict):
            live["_id"] = bson.ObjectId(live["_id"]["$oid"])
        assert codec.normalize(live) == synthetic


def test_driver_loading_uses_majority_with_injected_modules():
    pytest.importorskip("bson")
    pymongo = ModuleType("pymongo")
    client = Client([{"_id": 1}])
    pymongo.MongoClient = lambda *args, **kwargs: client
    concerns = ModuleType("pymongo.read_concern")
    concerns.ReadConcern = lambda value: value
    def importer(name):
        if name == "pymongo":
            return pymongo
        if name == "pymongo.read_concern":
            return concerns
        return importlib.import_module(name)
    result = io.run_live_audit(None, {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1",
                                     "MONGO_URI": io.LOCAL_URI}, importer)
    assert ("options", {"read_concern": "majority"}) in client.calls
    assert result.isolated_test


def test_bson_code_is_not_plain_string():
    bson = pytest.importorskip("bson")
    row = io.BSONCodec().normalize({"_id": 1, "text": bson.Code("private"),
                                    "raw": {"url": bson.Code("private"),
                                            "publishedDate": bson.Code("2025-01-01")},
                                    "matched_tickers": [bson.Code("private")]})
    assert row.text_class == "non_string"
    assert row.content_digest is None and row.url_digest is None
    assert row.provider_day is None
    assert row.ticker_malformed_elements == 1


def test_transport_has_no_write_calls_and_hashes_recompute(report):
    tree = ast.parse((ROOT / "src/dtrm/phase4/salvage_live_io.py").read_text())
    calls = {node.func.attr for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert not calls & {"insert_one", "insert_many", "update_one", "update_many", "replace_one",
                        "delete_one", "delete_many", "bulk_write", "create_index", "drop", "aggregate"}
    value = json.loads(serialize_live_report(report))
    evidence = {key: value[key] for key in (*report.counts.to_dict(), "indexes", "writer_findings")}
    from dtrm.phase4.source_metadata import canonical_sha256
    assert value["evidence_sha256"] == canonical_sha256(evidence)
