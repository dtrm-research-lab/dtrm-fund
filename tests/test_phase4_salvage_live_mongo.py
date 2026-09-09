"""Registered literal-localhost synthetic server tests; no production configuration."""

import os
import runpy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from dtrm.phase4 import retrospective_salvage as domain
from dtrm.phase4 import retrospective_salvage_io as census_io
from dtrm.phase4 import salvage_live_io as io
from dtrm.phase4.salvage_live_report import serialize_live_report

ENABLED = os.environ.get("PHASE4_SYNTHETIC_MONGO") == "1" and os.environ.get("GITHUB_ACTIONS") == "true"
pytestmark = pytest.mark.skipif(not ENABLED, reason="requires isolated CI Mongo service")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def mongo():
    import pymongo
    client = pymongo.MongoClient(io.LOCAL_URI, serverSelectionTimeoutMS=10000)
    collection = client["trumpMinMax"]["trumpNews"]
    if collection.count_documents({}) != 0:
        client.close()
        pytest.fail("refuse nonempty synthetic collection")
    try:
        yield pymongo, collection
    finally:
        collection.drop()
        client.close()


def test_real_census_projection_bson_and_no_mutation(mongo):
    from bson import ObjectId
    from pymongo.read_concern import ReadConcern
    pymongo, col = mongo
    identifier = ObjectId("67810bc00000000000000001")
    rows = [
        {"_id": identifier, "text": "PRIVATE_TEXT", "matched_tickers": ["PRIVATE_TICKER"],
         "date": "2025-01-10", "raw": {"url": "https://private.invalid", "excluded": "PRIVATE_RAW"},
         "outcome": "PRIVATE_OUTCOME"},
        {"_id": "legacy", "date": datetime(2025, 1, 10, tzinfo=timezone.utc)},
    ]
    col.insert_many(rows)
    before = list(col.find().sort("_id", 1))
    report = io.fetch_live_audit(pymongo.MongoClient, io.LOCAL_URI, ReadConcern("majority"),
                                 io.BSONCodec(), isolated_test=True,
                                 clock=lambda: datetime(2025, 2, 1, tzinfo=timezone.utc))
    projected = dict(rows[0])
    del projected["outcome"]
    projected["raw"] = {"url": "https://private.invalid"}
    expected = domain.aggregate_rows(
        map(io.BSONCodec().normalize, [projected, rows[1]]), report.started,
    )
    assert report.counts == expected
    assert report.counts.genuine_object_ids == 1
    assert "PRIVATE" not in serialize_live_report(report)
    assert list(col.find().sort("_id", 1)) == before


def test_real_local_cli_equivalence_and_blocked_state(mongo, tmp_path, monkeypatch):
    from bson import ObjectId
    _, col = mongo
    col.insert_one({"_id": ObjectId("67810bc00000000000000001"), "text": "synthetic"})
    # Explicit synthetic mapping. Never load or enumerate ambient source configuration.
    env = {"GITHUB_ACTIONS": "true", "PHASE4_SYNTHETIC_MONGO": "1", "MONGO_URI": io.LOCAL_URI}
    entry = runpy.run_path(str(ROOT / "research/experiments/run_phase4_retrospective_salvage_live.py"))
    run = entry["main"]
    monkeypatch.setitem(run.__globals__, "run_live_audit", lambda path: io.run_live_audit(path, env))
    output = tmp_path / "aggregate.json"
    assert run(["--output", str(output)]) == 0
    import json
    result = json.loads(output.read_text())
    assert result["scientific_assessment"] == "RETROSPECTIVE_PROXY_PARTIAL"
    assert result["training_permitted"] is False
    assert result["production_source_accessed"] is False
    assert result["live_adapter"]["requested_read_concern"] == "majority"
    assert col.count_documents({}) == 1


def test_real_preliminary_cap_and_sparse_index(mongo, monkeypatch):
    from pymongo.read_concern import ReadConcern
    pymongo, col = mongo
    col.insert_many([{"_id": i} for i in range(4)])
    col.create_index("dedupe_key", unique=True, sparse=True)
    report = io.fetch_live_audit(pymongo.MongoClient, io.LOCAL_URI, ReadConcern("majority"),
                                 io.BSONCodec(), isolated_test=True)
    assert report.indexes.dedupe_unique_sparse_unqualified == 1
    assert report.counts.dedupe_missing == 4
    monkeypatch.setattr(census_io, "CENSUS_CAP", 3)
    with pytest.raises(io.SalvageIOError, match="SOURCE_EXCEEDS_REGISTERED_BOUND"):
        io.fetch_live_audit(pymongo.MongoClient, io.LOCAL_URI, ReadConcern("majority"),
                            io.BSONCodec(), isolated_test=True)
    assert col.count_documents({}) == 4
