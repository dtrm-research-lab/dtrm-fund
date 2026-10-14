"""Dormant CLI tests: fake assessment only, absolutely no Mongo source connection."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from dtrm.phase4.matched_tickers_shape_audit import normalize_shape_counts

_RUNNER_PATH = (
    Path(__file__).resolve().parents[1]
    / "research" / "experiments" / "run_phase4_matched_tickers_shape_audit.py"
)
_SPEC = importlib.util.spec_from_file_location("phase4_matched_shape_cli", _RUNNER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
cli = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cli)


def fake_report():
    return normalize_shape_counts(
        {"containers": [{"kind": "array", "n": 1}], "elements": []},
        counted_documents=1,
    )


def test_cli_stages_aggregate_only_report_without_live_access(
    tmp_path, monkeypatch, capsys
) -> None:
    def no_mongo(_env_file):
        return fake_report()

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    outfile = tmp_path / "report.json"
    assert cli.main(["--output", str(outfile)]) == 0
    report = json.loads(outfile.read_text(encoding="ascii"))
    assert report["document_count"] == 1
    assert report["asset_mapping_authenticated"] is False
    summary = json.loads(capsys.readouterr().out)
    assert set(summary) == {
        "aggregate_sha256", "graph", "status", "scientific_status", "documents", "elements"
    }
    assert summary["status"] == "succeeded"
    assert list(tmp_path.glob(".phase4-shape-*")) == []


def test_cli_never_overwrites_existing_report(tmp_path, monkeypatch, capsys) -> None:
    def no_mongo(_env_file):
        raise AssertionError("must preflight before opening Mongo connection")

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    outfile = tmp_path / "report.json"
    outfile.write_text("previous evidence", encoding="utf-8")
    assert cli.main(["--output", str(outfile)]) == 1
    assert outfile.read_text(encoding="utf-8") == "previous evidence"
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"


def test_atomic_publish_never_clobbers_external_file(tmp_path) -> None:
    outfile = tmp_path / "report.json"
    outfile.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        cli.publish_exclusively(outfile, b"replacement")
    assert outfile.read_bytes() == b"original"
    assert list(tmp_path.glob(".phase4-shape-*")) == []


def test_cli_symlink_is_rejected_before_mongo(tmp_path, monkeypatch, capsys) -> None:
    def no_mongo(_env_file):
        raise AssertionError("must preflight before connecting")

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    target = tmp_path / "existing.json"
    target.write_bytes(b"original")
    symlink = tmp_path / "result.json"
    symlink.symlink_to(target)
    assert cli.main(["--output", str(symlink)]) == 1
    assert target.read_bytes() == b"original"
    assert json.loads(capsys.readouterr().out)["error_code"] == "OUTPUT_EXISTS"
