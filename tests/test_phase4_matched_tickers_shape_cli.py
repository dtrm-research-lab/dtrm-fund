"""Dormant CLI tests: fake assessment only, absolutely no Mongo source connection."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
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
    tmp_path, monkeypatch, capfd
) -> None:
    def no_mongo(_env_file):
        return fake_report()

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    outfile = tmp_path / "report.json"
    assert cli.main(["--output", str(outfile)]) == 0
    report = json.loads(outfile.read_text(encoding="ascii"))
    assert report["document_count"] == 1
    assert report["asset_mapping_authenticated"] is False
    summary = json.loads(capfd.readouterr().out)
    assert set(summary) == {
        "aggregate_sha256", "graph", "status", "scientific_status", "documents", "elements"
    }
    assert summary["status"] == "succeeded"
    assert list(tmp_path.glob(".phase4-shape-*")) == []


def test_cli_never_overwrites_existing_report(tmp_path, monkeypatch, capfd) -> None:
    def no_mongo(_env_file):
        raise AssertionError("must preflight before opening Mongo connection")

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    outfile = tmp_path / "report.json"
    outfile.write_text("previous evidence", encoding="utf-8")
    assert cli.main(["--output", str(outfile)]) == 1
    assert outfile.read_text(encoding="utf-8") == "previous evidence"
    assert json.loads(capfd.readouterr().out)["error_code"] == "OUTPUT_EXISTS"


def test_atomic_publish_never_clobbers_external_file(tmp_path) -> None:
    outfile = tmp_path / "report.json"
    outfile.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        cli.publish_exclusively(outfile, b"replacement")
    assert outfile.read_bytes() == b"original"
    assert list(tmp_path.glob(".phase4-shape-*")) == []


def test_cli_symlink_is_rejected_before_mongo(tmp_path, monkeypatch, capfd) -> None:
    def no_mongo(_env_file):
        raise AssertionError("must preflight before connecting")

    monkeypatch.setattr(cli, "operator_local_shape_audit", no_mongo)
    target = tmp_path / "existing.json"
    target.write_bytes(b"original")
    symlink = tmp_path / "result.json"
    symlink.symlink_to(target)
    assert cli.main(["--output", str(symlink)]) == 1
    assert target.read_bytes() == b"original"
    assert json.loads(capfd.readouterr().out)["error_code"] == "OUTPUT_EXISTS"


def test_post_publish_unlink_failure_preserves_success(tmp_path, monkeypatch, capfd) -> None:
    """Published report is authoritative even if staging cleanup is interrupted."""
    original_unlink = cli.os.unlink

    def fail_unlink(path, *args, **kwargs):
        if str(path).endswith(".tmp") or ".phase4-shape-" in str(path):
            raise OSError("simulated sensitive stage cleanup exception")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(cli.os, "unlink", fail_unlink)
    monkeypatch.setattr(cli, "operator_local_shape_audit", lambda _env_file: fake_report())
    output = tmp_path / "final.json"
    assert cli.main(["--output", str(output)]) == 0
    assert json.loads(output.read_text())["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert json.loads(capfd.readouterr().out)["status"] == "succeeded"
    # An orphan stage may remain; cleanup is a private operator concern only.


def test_success_status_stdout_failure_is_advisory(tmp_path, monkeypatch) -> None:
    def no_stdout(*_args, **_kwargs):
        raise BrokenPipeError("simulated terminal closed")

    monkeypatch.setattr(cli, "operator_local_shape_audit", lambda _env_file: fake_report())
    monkeypatch.setattr(cli, "_write_status", no_stdout)
    output = tmp_path / "published.json"
    assert cli.main(["--output", str(output)]) == 0
    assert json.loads(output.read_text())["asset_mapping_authenticated"] is False


def test_failure_status_stdout_failure_is_redacted_and_nonthrowing(tmp_path, monkeypatch) -> None:
    def no_stdout(*_args, **_kwargs):
        raise OSError("simulated terminal failure")

    monkeypatch.setattr(cli, "_write_status", no_stdout)
    output = tmp_path / "does-not-exist" / "report.json"
    assert cli.main(["--output", str(output)]) == 1
    assert not output.exists()


def test_publish_stage_fsync_error_creates_no_final(tmp_path, monkeypatch) -> None:
    def fail_fsync(_fd):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(cli.os, "fsync", fail_fsync)
    output = tmp_path / "not-published.json"
    with pytest.raises(OSError):
        cli.publish_exclusively(output, b"synthetic")
    assert not output.exists()
    assert list(tmp_path.glob(".phase4-shape-*")) == []


def test_real_closed_stdout_pipe_cannot_reclassify_published_report(tmp_path) -> None:
    """An actual EPIPE at OS fd 1 must not cause interpreter-exit failure 120."""
    outfile = tmp_path / "published.json"
    script = (
        "import importlib.util, pathlib; "
        "p = pathlib.Path(" + repr(str(_RUNNER_PATH)) + "); "
        "spec = importlib.util.spec_from_file_location('operator_cli_probe', p); "
        "mod = importlib.util.module_from_spec(spec); "
        "spec.loader.exec_module(mod); "
        "out = pathlib.Path(" + repr(str(outfile)) + "); "
        "mod.publish_exclusively(out, b'{\"scientific_status\":\"BLOCKED_SOURCE_AUDIT\"}'); "
        "mod._emit({'status':'succeeded'}); "
    )
    read_fd, write_fd = os.pipe()
    os.close(read_fd)  # Make child stdout an actual pipe with no reader.
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            stdout=write_fd,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
            env={**os.environ, "PYTHONPATH": str(_RUNNER_PATH.parents[2] / "src")},
        )
    finally:
        os.close(write_fd)
    assert result.returncode == 0
    assert result.stderr == b""
    assert json.loads(outfile.read_text())["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
