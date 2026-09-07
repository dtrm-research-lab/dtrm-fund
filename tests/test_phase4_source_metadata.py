"""Source inventory contracts using synthetic counters and an injected transport."""

import json
import runpy
from copy import deepcopy
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

import pytest

from dtrm.phase4 import source_metadata_io
from dtrm.phase4.source_metadata import (
    FIELDS,
    MetadataError,
    build_metadata_pipeline,
    build_metadata_report,
    normalize_metadata_counts,
)
from dtrm.phase4.source_metadata_io import MetadataIOError, fetch_metadata_counts

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase4_source_metadata_aggregate_v0.json"


@pytest.fixture
def raw():
    return json.loads(FIXTURE.read_text())


def test_pipeline_returns_only_registered_types_with_no_write_or_value_stages():
    pipeline = build_metadata_pipeline()
    assert [next(iter(stage)) for stage in pipeline] == ["$sort", "$limit", "$project", "$facet"]
    assert pipeline[:2] == [{"$sort": {"_id": 1}}, {"$limit": 1000}]
    projection = pipeline[2]["$project"]
    assert projection["_id"] == 0
    assert {value["$type"] for key, value in projection.items() if key != "_id"} == {
        "$_id", "$date", "$matched_tickers", "$published_at", "$publishedDate",
        "$first_seen_at", "$firstSeenAt", "$version_observed_at", "$observed_at",
        "$ingested_at", "$fetched_at", "$created_at", "$updated_at", "$version_id",
        "$supersedes_version_id", "$content_sha256", "$linked_at", "$mapping_version", "$asset_links",
    }
    for key, value in projection.items():
        if key != "_id":
            assert set(value) == {"$type"}
    pipeline[0]["$sort"]["_id"] = -1
    assert build_metadata_pipeline()[0] == {"$sort": {"_id": 1}}


def test_missing_and_null_are_distinct_and_report_is_deterministic(raw):
    counts = normalize_metadata_counts(raw)
    seen = next(f for f in counts.fields if f.field == "first_seen_at")
    assert [(b.bson_type, b.count) for b in seen.types] == [("missing", 2), ("null", 1)]
    expected = build_metadata_report(counts, "synthetic")
    for value in raw.values():
        value.reverse()
    assert build_metadata_report(normalize_metadata_counts(raw), "synthetic") == expected
    assert expected["sampled_documents"] == 3
    assert expected["selection"]["exhaustiveness"] == "not_established"


def test_counts_are_immutable_and_detached(raw):
    counts = normalize_metadata_counts(raw)
    with pytest.raises(FrozenInstanceError):
        counts.fields[0].types[0].count = 20
    raw["f0"][0]["n"] = 1000
    assert counts.fields[0].types[0].count == 3


@pytest.mark.parametrize("kind", ["date", "missing"])
def test_apparently_complete_or_all_missing_metadata_cannot_promote(raw, kind):
    for key in raw:
        if key != "sample":
            raw[key] = [{"_id": kind, "n": 3}]
    report = build_metadata_report(normalize_metadata_counts(raw), "live_mongo")
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert report["training_permitted"] is False
    assert report["outcome_access_permitted"] is False
    assert report["timestamp_semantics_verified"] is False
    assert report["snapshot_verified"] is False


def test_empty_evidence_remains_blocked(raw):
    report = build_metadata_report(normalize_metadata_counts({key: [] for key in raw}), "synthetic")
    assert report["sampled_documents"] == 0
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"


@pytest.mark.parametrize("bad_count", [True, False, -1, 0, 1001, 3.0, "3", None])
def test_invalid_counts_fail(raw, bad_count):
    raw["f0"][0]["n"] = bad_count
    with pytest.raises(MetadataError):
        normalize_metadata_counts(raw)


@pytest.mark.parametrize("case", ["extra", "missing", "type", "duplicate", "total", "sample", "bin", "list"])
def test_corrupt_aggregate_boundary_fails(raw, case):
    if case == "extra":
        raw["target_model"] = 0.9
    elif case == "missing":
        del raw["f0"]
    elif case == "type":
        raw["f0"][0]["_id"] = "actual source value"
    elif case == "duplicate":
        raw["f0"].append(deepcopy(raw["f0"][0]))
    elif case == "total":
        raw["f0"][0]["n"] = 2
    elif case == "sample":
        raw["sample"].append({"n": 3})
    elif case == "bin":
        raw["f0"][0]["value"] = "must never be returned"
    elif case == "list":
        raw["f0"] = None
    with pytest.raises(MetadataError):
        normalize_metadata_counts(raw)


class FakeClient:
    def __init__(self, response, fail=False):
        self.response = response
        self.fail = fail
        self.closed = False
        self.names = []
        self.calls = []

    def __getitem__(self, name):
        self.names.append(name)
        return self

    def aggregate(self, pipeline, **kwargs):
        self.calls.append((pipeline, kwargs))
        if self.fail:
            raise RuntimeError("mongodb://private-password@private-host/source")
        return self.response

    def close(self):
        self.closed = True


@pytest.mark.parametrize("fail", [False, True])
def test_transport_bounds_namespace_one_read_closure_and_error_redaction(raw, fail):
    client = FakeClient([raw], fail)
    options = {}

    def factory(uri, **kwargs):
        options.update(kwargs)
        return client

    if fail:
        with pytest.raises(MetadataIOError) as error:
            fetch_metadata_counts(factory, "local-test-uri")
        assert str(error.value) == "MONGO_READ_FAILED"
    else:
        assert fetch_metadata_counts(factory, "local-test-uri").sampled_documents == 3
    assert client.closed
    assert client.names == ["trumpMinMax", "trumpNews"]
    assert len(client.calls) == 1
    assert client.calls[0][1] == {"maxTimeMS": 20000, "allowDiskUse": False}
    assert options == {"timeoutMS": 60000, "serverSelectionTimeoutMS": 10000,
                       "socketTimeoutMS": 20000, "retryReads": False}


def test_invalid_server_response_is_closed_and_rejected(raw):
    client = FakeClient([raw, raw])
    with pytest.raises(MetadataIOError, match="INVALID_AGGREGATE_RESPONSE"):
        fetch_metadata_counts(lambda *a, **k: client, "local-test-uri")
    assert client.closed


@pytest.fixture
def cli():
    return runpy.run_path(str(ROOT / "research/experiments/run_phase4_source_metadata_audit.py"))["main"]


def test_synthetic_cli_never_connects_and_reproduces_report(cli, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("synthetic mode attempted Mongo access")
    monkeypatch.setitem(cli.__globals__, "run_mongo_inventory", forbidden)
    output = tmp_path / "review.json"
    assert cli(["--synthetic-input", str(FIXTURE), "--output", str(output)]) == 0
    expected = ROOT / "research/reports/DTRM_PHASE4_SOURCE_METADATA_SYNTHETIC_V0.json"
    assert output.read_bytes() == expected.read_bytes()


def test_cli_refuses_overwrite_before_connecting(cli, tmp_path, monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        pytest.fail("existing output triggered Mongo access")
    monkeypatch.setitem(cli.__globals__, "run_mongo_inventory", forbidden)
    output = tmp_path / "review.json"
    output.write_text("original evidence")
    assert cli(["--mongo", "--output", str(output)]) == 1
    assert output.read_text() == "original evidence"
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"


def test_invalid_input_creates_no_report(cli, raw, tmp_path, capsys):
    raw["secret"] = "do not echo"
    source = tmp_path / "input.json"
    source.write_text(json.dumps(raw))
    output = tmp_path / "review.json"
    assert cli(["--synthetic-input", str(source), "--output", str(output)]) == 1
    assert not output.exists()
    assert "do not echo" not in capsys.readouterr().out


def test_live_mode_records_audit_times_not_source_times(cli, raw, tmp_path, monkeypatch):
    monkeypatch.setitem(cli.__globals__, "run_mongo_inventory",
                        lambda env_file: normalize_metadata_counts(raw))
    output = tmp_path / "review.json"
    assert cli(["--mongo", "--output", str(output)]) == 0
    report = json.loads(output.read_text())
    assert report["execution_mode"] == "live_mongo"
    assert report["audit_started_at"] <= report["audit_completed_at"]
    assert report["timestamp_semantics_verified"] is False
    assert len(report["fields"]) == len(FIELDS)


def test_missing_credentials_fail_before_driver_import(monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.delenv("db_password", raising=False)
    def forbidden(name):
        pytest.fail("missing credentials imported a driver")
    monkeypatch.setattr(source_metadata_io.importlib, "import_module", forbidden)
    with pytest.raises(MetadataIOError, match="MISSING_LOCAL_CREDENTIALS"):
        source_metadata_io.run_mongo_inventory(None)


def test_existing_password_convention_encodes_reserved_characters(raw, monkeypatch):
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.setenv("db_password", "p@ss:/%")
    client = FakeClient([raw])
    received = []
    def factory(uri, **kwargs):
        received.append(uri)
        return client
    monkeypatch.setattr(source_metadata_io.importlib, "import_module",
                        lambda name: SimpleNamespace(MongoClient=factory))
    assert source_metadata_io.run_mongo_inventory(None).sampled_documents == 3
    assert "p%40ss%3A%2F%25@" in received[0]


def test_explicit_env_file_does_not_override_environment(raw, tmp_path, monkeypatch):
    monkeypatch.setenv("MONGO_URI", "local-test-uri")
    env_file = tmp_path / "connection.env"
    env_file.write_text("# synthetic configuration")
    calls = []
    client = FakeClient([raw])
    def loader(**kwargs):
        calls.append(kwargs)
        return True
    def module(name):
        if name == "dotenv":
            return SimpleNamespace(load_dotenv=loader)
        return SimpleNamespace(MongoClient=lambda *a, **k: client)
    monkeypatch.setattr(source_metadata_io.importlib, "import_module", module)
    source_metadata_io.run_mongo_inventory(env_file)
    assert calls == [{"dotenv_path": env_file, "override": False}]
