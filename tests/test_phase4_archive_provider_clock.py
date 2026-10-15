"""Synthetic-only negative tests for the archived provider-clock readback."""
from __future__ import annotations

import copy
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from dtrm.phase4 import archive_provider_clock as clock


def _fixture(monkeypatch: pytest.MonkeyPatch) -> tuple[bytes, dict[int, object]]:
    rows: list[dict[str, object]] = []
    pages: dict[int, object] = {}
    for i in range(21):
        run = 10000 + i
        aid = 20000 + i
        created = f"2026-10-{i + 1:02d}T01:15:00Z"
        rows.append(
            {
                "asof": f"2026-09-{i + 1:02d}",
                "run_id": run,
                "artifact_id": aid,
                "artifact_created_at_utc": created,
            }
        )
        pages[run] = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": aid,
                    "name": f"daily-ranking-{run}",
                    "workflow_run": {"id": run},
                    "created_at": created,
                    "expired": False,
                    "expires_at": "2026-12-01T00:00:00Z",
                }
            ],
        }
    manifest = {
        "schema_version": clock.MANIFEST_SCHEMA,
        "repository": clock.BACKEND_REPO,
        "source_completeness_authenticated": False,
        "model_fitting_permitted": False,
        "archives": rows,
    }
    raw = (json.dumps(manifest, sort_keys=True) + "\n").encode()
    monkeypatch.setattr(clock, "MANIFEST_GIT_BLOB_SHA1", clock._git_blob_sha1(raw))
    return raw, pages


def test_synthetic_exact_metadata_match_without_science_promotion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw, pages = _fixture(monkeypatch)
    result = clock.verify_provider_clock(raw, pages, "2026-10-22T00:00:00Z")
    assert result.status == "PASS_PROVIDER_METADATA_MATCH"
    assert result.scientific_status == "BLOCKED_SOURCE_AUDIT"
    assert result.verified_archives == 21
    assert result.distinct_runs == 21
    assert result.earliest_expiry_at_utc == "2026-12-01T00:00:00Z"
    assert not result.historical_first_seen_authenticated
    assert not result.historical_absence_authenticated
    assert not result.source_completeness_authenticated
    assert not result.price_clock_authenticated
    assert not result.model_fitting_permitted
    assert not result.mm1_execution_permitted
    assert not result.scientific_counting_permitted
    assert "10000" not in json.dumps(asdict(result))


@pytest.mark.parametrize(
    "alteration",
    [
        "wrong_timestamp",
        "wrong_artifact",
        "wrong_name",
        "wrong_run",
        "expired",
        "past_expiry",
        "truncated_page",
        "ambiguous_artifact",
        "missing_page",
        "additional_page",
        "naive_time",
    ],
)
def test_fail_closed_for_inconsistent_provider_receipt(
    monkeypatch: pytest.MonkeyPatch, alteration: str
) -> None:
    raw, pages = _fixture(monkeypatch)
    pages = copy.deepcopy(pages)
    first = pages[10000]
    assert isinstance(first, dict)
    item = first["artifacts"][0]
    if alteration == "wrong_timestamp":
        item["created_at"] = "2026-10-01T01:15:01Z"
    elif alteration == "wrong_artifact":
        item["id"] = 99999
    elif alteration == "wrong_name":
        item["name"] = "daily-ranking-99999"
    elif alteration == "wrong_run":
        item["workflow_run"] = {"id": 99999}
    elif alteration == "expired":
        item["expired"] = True
    elif alteration == "past_expiry":
        item["expires_at"] = "2026-10-10T00:00:00Z"
    elif alteration == "truncated_page":
        first["total_count"] = 2
    elif alteration == "ambiguous_artifact":
        first["artifacts"].append(copy.deepcopy(item))
        first["total_count"] = 2
    elif alteration == "missing_page":
        del pages[10000]
    elif alteration == "additional_page":
        pages[99999] = {"total_count": 0, "artifacts": []}
    else:
        item["created_at"] = "2026-10-01T01:15:00"
    with pytest.raises(clock.ClockAttestationError, match=clock.FAILURE):
        clock.verify_provider_clock(raw, pages, "2026-10-22T00:00:00Z")


def test_modified_manifest_is_rejected_before_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw, pages = _fixture(monkeypatch)
    changed = raw.replace(b"2026-09-01", b"2026-09-02")
    assert changed != raw
    with pytest.raises(clock.ClockAttestationError, match=clock.FAILURE):
        clock.verify_provider_clock(changed, pages, "2026-10-22T00:00:00Z")


def test_strict_timestamp_clock_and_expiry_tie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw, pages = _fixture(monkeypatch)
    with pytest.raises(clock.ClockAttestationError):
        clock.verify_provider_clock(raw, pages, "2026-12-01T00:00:00Z")
    with pytest.raises(clock.ClockAttestationError):
        clock.verify_provider_clock(raw, pages, "2026-10-22T00:00:00-00:00")


def test_cli_fails_without_writing_output_on_bad_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw, pages = _fixture(monkeypatch)
    src = tmp_path / "source.json"
    src.write_bytes(raw)
    directory = tmp_path / "receipts"
    directory.mkdir()
    for run, page in pages.items():
        (directory / f"{run}.json").write_text(json.dumps(page), encoding="utf-8")
    tampered = json.loads((directory / "10000.json").read_text(encoding="utf-8"))
    tampered["artifacts"][0]["name"] = "changed"
    (directory / "10000.json").write_text(json.dumps(tampered), encoding="utf-8")
    output = tmp_path / "result.json"
    ret = clock.main(
        [
            "--manifest", str(src),
            "--pages-dir", str(directory),
            "--inspected-at-utc", "2026-10-22T00:00:00Z",
            "--output", str(output),
        ]
    )
    assert ret == 2
    assert not output.exists()


def test_cli_produces_only_redacted_aggregate_on_synthetic_readback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    raw, pages = _fixture(monkeypatch)
    src = tmp_path / "source.json"
    src.write_bytes(raw)
    directory = tmp_path / "receipts"
    directory.mkdir()
    for run, page in pages.items():
        (directory / f"{run}.json").write_text(json.dumps(page), encoding="utf-8")
    output = tmp_path / "result.json"
    ret = clock.main(
        [
            "--manifest", str(src),
            "--pages-dir", str(directory),
            "--inspected-at-utc", "2026-10-22T00:00:00Z",
            "--output", str(output),
        ]
    )
    assert ret == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["verified_archives"] == 21
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert "10000" not in output.read_text(encoding="utf-8")
