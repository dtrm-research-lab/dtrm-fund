"""Unit and functional cases; no production source is accessed."""

import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

import pytest

from dtrm.phase4 import source_feasibility_io as io
from dtrm.phase4.source_feasibility import (
    DATE_PATHS,
    PATHS,
    build_feasibility_pipeline,
    build_feasibility_report,
    normalize_feasibility,
    sanitize_indexes,
)
from dtrm.phase4.source_metadata import MetadataError
from dtrm.phase4.source_metadata_io import MetadataIOError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase4_source_feasibility_v0.json"
EXPECTED = ROOT / "research/reports/DTRM_PHASE4_SOURCE_FEASIBILITY_SYNTHETIC_V0.json"


@pytest.fixture
def payload():
    return json.loads(FIXTURE.read_text())


def test_pipeline_scope_and_freshness():
    p = build_feasibility_pipeline()
    assert p[:2] == [{"$sort": {"_id": 1}}, {"$limit": 1000}]
    assert list(p[2]["$project"]) == ["_id", *[f"f{i}" for i in range(17)], "q0", "q1", "q2"]
    assert {v["$type"] for k, v in p[2]["$project"].items() if k.startswith("f")} == {
        f"${path}" for path in PATHS}
    assert [p[2]["$project"][f"q{i}"] for i in range(3)] == [f"${p}" for p in DATE_PATHS]
    for token in ("$out", "$merge", "$lookup", "$function", "$text", "$where"):
        assert token not in json.dumps(p)
    p[1]["$limit"] = 100000
    assert build_feasibility_pipeline()[1] == {"$limit": 1000}


def test_roundtrip_order_immutable_and_blocked(payload):
    counts = normalize_feasibility(payload["aggregate"])
    indexes = sanitize_indexes(payload["indexes"])
    report = build_feasibility_report(counts, indexes, "synthetic")
    assert json.dumps(report, sort_keys=True, indent=2) + "\n" == EXPECTED.read_text()
    for bins in payload["aggregate"].values():
        bins.reverse()
    payload["indexes"].reverse()
    assert build_feasibility_report(normalize_feasibility(payload["aggregate"]),
                                    sanitize_indexes(payload["indexes"]), "synthetic") == report
    with pytest.raises(FrozenInstanceError):
        counts.sampled_documents = 0
    payload["aggregate"]["sample"][0]["n"] = 42
    assert counts.sampled_documents == 3
    for mode in ("synthetic", "live_mongo"):
        result = build_feasibility_report(counts, indexes, mode)
        assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
        for flag in ("training_permitted", "outcome_access_permitted", "snapshot_verified",
                     "decision_clock_authenticated", "history_construction_permitted", "reads_atomic"):
            assert result[flag] is False


def test_empty_sample(payload):
    result = normalize_feasibility({key: [] for key in payload["aggregate"]})
    assert result.sampled_documents == 0
    assert sanitize_indexes([]).total == 0


@pytest.mark.parametrize("bad", [True, False, -1, 0, 1001, 3.0, "3", None])
def test_bad_counts(payload, bad):
    payload["aggregate"]["f0"][0]["n"] = bad
    with pytest.raises(MetadataError):
        normalize_feasibility(payload["aggregate"])


@pytest.mark.parametrize("case", ["extra", "missing", "duplicate", "total", "bson", "sample", "list",
                                  "class", "year", "year_null", "unparsed_year", "date_duplicate", "cross_type"])
def test_bad_schema(payload, case):
    a = payload["aggregate"]
    if case == "extra":
        a["private_outcome"] = 123
    elif case == "missing":
        del a["f0"]
    elif case == "duplicate":
        a["f3"] = [{"_id": "missing", "n": 1}, {"_id": "missing", "n": 2}]
    elif case == "total":
        a["f3"][0]["n"] = 2
    elif case == "bson":
        a["f3"][0]["_id"] = "secret value"
    elif case == "sample":
        a["sample"].append({"n": 3})
    elif case == "list":
        a["f3"] = None
    elif case == "class":
        a["d0"][0]["_id"]["kind"] = "approved_availability"
    elif case == "year":
        a["d0"][0]["_id"]["year"] = "0000"
    elif case == "year_null":
        a["d0"][0]["_id"]["year"] = None
    elif case == "unparsed_year":
        a["d0"][2]["_id"]["year"] = "2025"
    elif case == "date_duplicate":
        a["d0"][1] = deepcopy(a["d0"][0])
    else:
        a["d1"][0]["_id"]["kind"] = "bson_date"
    with pytest.raises(MetadataError):
        normalize_feasibility(a)


@pytest.mark.parametrize("option,value", [("hidden", True), ("partialFilterExpression", {"secret": "value"}),
                                         ("collation", {"locale": "en"}), ("expireAfterSeconds", 60),
                                         ("buildUUID", "synthetic")])
def test_index_restrictions_and_redaction(payload, option, value):
    payload["indexes"][2][option] = value
    result = sanitize_indexes(payload["indexes"]).to_dict()
    assert result["dedupe_ascending"] == 1
    assert result["dedupe_unique_sparse_unqualified"] == 0
    for token in ("synthetic", "secret", "locale", "name", "key"):
        assert token not in json.dumps(result)


@pytest.mark.parametrize("bad", [[{}], [{"key": {}}], [{"key": {"date": 1}, "unique": "true"}],
                                 [{"key": {"date": 1}}] * 65])
def test_invalid_catalog(bad):
    with pytest.raises(MetadataError):
        sanitize_indexes(bad)


def test_compound_and_boolean_direction_not_counted():
    result = sanitize_indexes([{"key": {"date": True}}, {"key": {"dedupe_key": 1, "date": 1}}])
    assert result.date_ascending == result.dedupe_ascending == 0


class Cursor:
    def __init__(self, values, fail=False):
        self.values, self.fail, self.closed = values, fail, False

    def __iter__(self):
        if self.fail:
            raise RuntimeError("mongodb://secret@host")
        return iter(self.values)

    def close(self):
        self.closed = True


class Client:
    def __init__(self, payload, failure=None):
        self.aggregate_cursor = Cursor([payload["aggregate"]], failure == "aggregate")
        self.index_cursor = Cursor(payload["indexes"], failure == "indexes")
        self.closed = False
        self.names, self.calls = [], []

    def __getitem__(self, name):
        self.names.append(name)
        return self

    def aggregate(self, pipeline, **kwargs):
        self.calls.append((pipeline, kwargs))
        return self.aggregate_cursor

    def list_indexes(self):
        self.calls.append("list_indexes")
        return self.index_cursor

    def close(self):
        self.closed = True


@pytest.mark.parametrize("failure", [None, "aggregate", "indexes", "invalid"])
def test_read_transport_and_closure(payload, failure):
    if failure == "invalid":
        payload["aggregate"]["secret"] = "value"
    client = Client(payload, failure)
    options = {}

    def factory(uri, **kwargs):
        options.update(kwargs)
        return client

    if failure:
        with pytest.raises(MetadataIOError) as err:
            io.fetch_feasibility(factory, "test-uri")
        assert str(err.value) in {"MONGO_READ_FAILED", "INVALID_DIAGNOSTIC_RESPONSE"}
    else:
        counts, indexes = io.fetch_feasibility(factory, "test-uri")
        assert counts.sampled_documents == indexes.total == 3
    assert client.closed and client.aggregate_cursor.closed
    assert client.names == ["trumpMinMax", "trumpNews"]
    assert client.calls[0] == (build_feasibility_pipeline(), {"maxTimeMS": 20000, "allowDiskUse": False})
    if failure not in ("aggregate", "invalid"):
        assert client.index_cursor.closed and client.calls[1] == "list_indexes"
    else:
        assert len(client.calls) == 1
    assert options == {"timeoutMS": 60000, "serverSelectionTimeoutMS": 10000,
                       "socketTimeoutMS": 20000, "retryReads": False}


def test_transport_caps_catalog_consumption(payload):
    client = Client(payload)
    client.index_cursor.values = [{"key": {"date": 1}}] * 65
    with pytest.raises(MetadataIOError, match="INVALID_DIAGNOSTIC_RESPONSE"):
        io.fetch_feasibility(lambda *a, **k: client, "test")
    assert client.index_cursor.closed and client.closed


def test_missing_credentials_precede_driver_import(monkeypatch):
    for key in ("MONGO_URI", "db_password"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(io.importlib, "import_module", lambda name: pytest.fail("unexpected import"))
    with pytest.raises(MetadataIOError, match="MISSING_LOCAL_CREDENTIALS"):
        io.run_mongo_feasibility(None)


def test_explicit_dotenv_no_override(tmp_path, monkeypatch):
    path = tmp_path / "config.env"
    path.write_text("# synthetic only")
    calls = []
    monkeypatch.setenv("MONGO_URI", "synthetic-uri")
    monkeypatch.setattr(io.importlib, "import_module", lambda name: SimpleNamespace(
        load_dotenv=lambda **kwargs: calls.append(kwargs)))
    assert io.configured_uri(path) == "synthetic-uri"
    assert calls == [{"dotenv_path": path, "override": False}]


def test_password_encoding(monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.setenv("db_password", "p@ss:/%")
    assert "p%40ss%3A%2F%25@" in io.configured_uri(None)


@pytest.fixture
def cli():
    return runpy.run_path(str(ROOT / "research/experiments/run_phase4_source_feasibility.py"))["main"]


def test_cli_synthetic_no_connection(cli, tmp_path, monkeypatch):
    monkeypatch.setitem(cli.__globals__, "run_mongo_feasibility", lambda *a: pytest.fail("live call"))
    output = tmp_path / "report.json"
    assert cli(["--synthetic-input", str(FIXTURE), "--output", str(output)]) == 0
    assert output.read_bytes() == EXPECTED.read_bytes()


def test_cli_no_overwrite_before_connect(cli, tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(cli.__globals__, "run_mongo_feasibility", lambda *a: pytest.fail("live call"))
    output = tmp_path / "report.json"
    output.write_text("original")
    assert cli(["--mongo", "--output", str(output)]) == 1
    assert output.read_text() == "original"
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"


def test_cli_invalid_input_redacted(cli, tmp_path, payload, capsys):
    payload["aggregate"]["secret"] = "do not echo"
    source, output = tmp_path / "input.json", tmp_path / "report.json"
    source.write_text(json.dumps(payload))
    assert cli(["--synthetic-input", str(source), "--output", str(output)]) == 1
    assert not output.exists()
    assert "do not echo" not in capsys.readouterr().out


def test_cli_audit_times_are_not_source_clocks(cli, tmp_path, payload, monkeypatch):
    monkeypatch.setitem(cli.__globals__, "run_mongo_feasibility", lambda *a: (
        normalize_feasibility(payload["aggregate"]), sanitize_indexes(payload["indexes"])))
    output = tmp_path / "report.json"
    assert cli(["--mongo", "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["audit_started_at"] <= result["audit_completed_at"]
    assert result["decision_clock_authenticated"] is False
