"""Real Mongo semantics on the disposable CI service, synthetic records only.

Never reads configured credentials or an env file. Fixture writes require both
the explicit integration opt-in and GitHub Actions. The destination is literal
localhost:27017; this module is skipped everywhere else.
"""

import json
import os
import runpy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from dtrm.phase4.source_feasibility import build_feasibility_report
from dtrm.phase4.source_feasibility_io import fetch_feasibility

ENABLED = os.environ.get("PHASE4_SYNTHETIC_MONGO") == "1" and os.environ.get("GITHUB_ACTIONS") == "true"
pytestmark = pytest.mark.skipif(not ENABLED, reason="requires isolated CI Mongo service")
URI = "mongodb://127.0.0.1:27017/?directConnection=true"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def mongo():
    # An absent driver in the explicitly enabled CI job must fail, not skip.
    import pymongo
    client = pymongo.MongoClient(URI, serverSelectionTimeoutMS=10000)
    collection = client["trumpMinMax"]["trumpNews"]
    if collection.count_documents({}) != 0:
        client.close()
        pytest.fail("refuse to modify nonempty fixture collection")
    try:
        yield pymongo, collection
    finally:
        # Only the literal local disposable CI service; never a production target.
        collection.drop()
        client.close()


def test_real_mongo_fixture_matches_synthetic_report_and_cli(mongo, tmp_path, monkeypatch):
    pymongo, col = mongo
    col.insert_many([
        {"_id": 1, "date": "2025-01-01T00:00:00Z", "dedupe_key": "one", "raw": {
            "id": "one", "url": "https://example.invalid/one",
            "publishedDate": "2025-01-01T00:00:00Z", "date": None}},
        {"_id": 2, "date": "2025-01-02", "dedupe_key": "two", "raw": {
            "id": "two", "url": "https://example.invalid/two", "publishedDate": "2025-01-02 12:00:00"}},
        {"_id": 3, "date": "not a date"},
    ])
    col.create_index("date")
    col.create_index("dedupe_key", unique=True, sparse=True)
    counts, indexes = fetch_feasibility(pymongo.MongoClient, URI)
    expected = json.loads((ROOT / "research/reports/DTRM_PHASE4_SOURCE_FEASIBILITY_SYNTHETIC_V0.json").read_text())
    assert build_feasibility_report(counts, indexes, "synthetic") == expected
    monkeypatch.setenv("MONGO_URI", URI)
    monkeypatch.delenv("db_password", raising=False)
    cli = runpy.run_path(str(ROOT / "research/experiments/run_phase4_source_feasibility.py"))["main"]
    output = tmp_path / "isolated-server.json"
    assert cli(["--mongo", "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["evidence_sha256"] == expected["evidence_sha256"]
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert col.count_documents({}) == 3


def test_real_mongo_date_types_arrays_and_utc_year(mongo):
    pymongo, col = mongo
    values = [
        {}, {"date": None}, {"date": 1735689600000}, {"date": "invalid"},
        {"date": datetime(2025, 1, 1, tzinfo=timezone.utc)},
        {"date": "2025-01-01T00:30:00+01:00"},
        {"date": "2025-01-01"}, {"date": "2025-01-01 12:00:00"},
        {"date": ["2025-01-01"]},
    ]
    for i, doc in enumerate(values):
        doc.update(_id=i, raw=[{"id": "nested", "publishedDate": "2025-01-01"}])
    col.insert_many(values)
    counts, indexes = fetch_feasibility(pymongo.MongoClient, URI)
    actual = {(b.kind, b.year): b.n for b in counts.dates[0].bins}
    assert actual == {("missing", None): 1, ("null", None): 1,
                      ("non_date_type", None): 2, ("invalid_string", None): 1,
                      ("bson_date", "2025"): 1, ("explicit_timezone_string", "2024"): 1,
                      ("date_only_string", "2025"): 1, ("naive_string", "2025"): 1}
    assert counts.fields[2].types[0].bson_type == "array"
    assert counts.dates[1].bins[0].kind == "non_date_type"
    assert indexes.total == 1


def test_real_mongo_cap_and_partial_index_not_qualified(mongo):
    pymongo, col = mongo
    col.insert_many([{"_id": i, "date": "2025-01-01"} for i in range(1000)]
                    + [{"_id": 1000, "date": "2026-01-01", "raw": {"first_seen_at": "must not appear"}}])
    col.create_index("dedupe_key", unique=True, partialFilterExpression={"dedupe_key": {"$exists": True}})
    counts, indexes = fetch_feasibility(pymongo.MongoClient, URI)
    assert counts.sampled_documents == 1000
    assert {(b.kind, b.year, b.n) for b in counts.dates[0].bins} == {("date_only_string", "2025", 1000)}
    assert counts.fields[10].types[0].bson_type == "missing"
    assert indexes.dedupe_ascending == 1
    assert indexes.dedupe_unique_sparse_unqualified == 0
    assert col.count_documents({}) == 1001
