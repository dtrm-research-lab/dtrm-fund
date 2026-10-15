"""Small fictional ZIP fixtures; no private articles or authentic ticker values."""

from __future__ import annotations

import hashlib
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from research.experiments.derive_phase4_archived_time_state_inventory_v0 import (
    ArchiveCensusError,
    census_aggregate_only,
)

FAMILY = hashlib.sha256(b"fixed fictional family").hexdigest()


def _serialize(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True) + "\n").encode("utf-8")


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _zip(asof: str, *, ticker: str = "FAKE", root: str = "ranking_news_evidence/") -> bytes:
    source = _digest(asof.encode())
    archive = BytesIO()
    manifest = {
        "schemaVersion": "1.0",
        "asOf": asof,
        "familyManifestSha256": FAMILY,
        "sourceNewsSha256": source,
    }
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as z:
        for days in (2, 5):
            doc = {
                "schemaVersion": "1.0",
                "asOfDate": asof,
                "provider": "financial-modeling-prep",
                "familyManifestSha256": FAMILY,
                "sourceNewsSha256": source,
                "windowDays": days,
                "items": [{
                    "fmpArticleId": "fictional-secret-id",
                    "textSha256": _digest(b"fictional-version"),
                    "tickers": [ticker],
                    "headline": "private fake headline",
                    "sourceUrl": "https://test.invalid/hidden",
                    "text": "private fictional text",
                }],
            }
            encoded = _serialize(doc)
            filename = root + f"daily_news_candidates_{days}d_v1.json"
            z.writestr(filename, encoded)
            z.writestr(filename + ".sha256", _digest(encoded) + "\n")
            manifest[f"candidate{days}dCount"] = 1
            manifest[f"candidate{days}dSha256"] = _digest(encoded)
        encoded_manifest = _serialize(manifest)
        filename = root + "daily_news_freeze_manifest_v1.json"
        z.writestr(filename, encoded_manifest)
        z.writestr(filename + ".sha256", _digest(encoded_manifest) + "\n")
    return archive.getvalue()


def _setup(folder: Path, *, second_ticker: str = "FAKE") -> dict:
    objects = [
        ("2026-10-12", 1, 101, "2026-10-13T10:00:00Z", _zip("2026-10-12")),
        ("2026-10-13", 2, 102, "2026-10-14T10:00:00Z",
         _zip("2026-10-13", ticker=second_ticker, root="Outputs/ranking_news_evidence/")),
    ]
    manifest = {
        "schema_version": "dtrm.phase4.archived_source_manifest.v0",
        "dataset_role": "exploratory_aggregate_source_manifest",
        "repository": "tech-com-UA00001/theresistance-back",
        "workflow": "DTRM daily ranking",
        "archives": [],
    }
    for asof, run_id, aid, created, blob in objects:
        (folder / f"{aid}.zip").write_bytes(blob)
        manifest["archives"].append({
            "asof": asof,
            "run_id": run_id,
            "artifact_id": aid,
            "artifact_created_at_utc": created,
            "zip_sha256": _digest(blob),
            "family_sha256": FAMILY,
            "source_news_sha256": _digest(asof.encode()),
        })
    return manifest


def test_reproducible_positive_only_private_aggregate(tmp_path: Path) -> None:
    manifest = _setup(tmp_path)
    result = census_aggregate_only(manifest, tmp_path)
    assert result["snapshot_count"] == 2
    assert result["unique_selected_positive_triples_union"] == 1
    assert result["unique_selected_positive_triples_2d"] == 1
    assert result["same_family_adjacent_count"] == 1
    assert result["same_family_sum_repeated_links_2d"] == 1
    assert result["5d_capped_count"] == 0
    assert result["source_completeness_authenticated"] is False
    assert result["model_fitting_permitted"] is False
    printed = json.dumps(result)
    assert "fictional-secret-id" not in printed
    assert "FAKE" not in printed
    assert "private" not in printed


def test_changed_link_is_only_changed_representation(tmp_path: Path) -> None:
    manifest = _setup(tmp_path, second_ticker="NEW_FAKE")
    result = census_aggregate_only(manifest, tmp_path)
    assert result["unique_selected_positive_triples_union"] == 2
    assert result["same_family_sum_repeated_links_2d"] == 0
    assert result["adjacent"][0]["2d_changed_link_sets"] == 1
    assert result["absence_authenticated"] is False


def test_archive_digest_change_rejected(tmp_path: Path) -> None:
    manifest = _setup(tmp_path)
    manifest["archives"][0]["zip_sha256"] = "0" * 64
    with pytest.raises(ArchiveCensusError):
        census_aggregate_only(manifest, tmp_path)


def test_archive_family_drift_rejected(tmp_path: Path) -> None:
    manifest = _setup(tmp_path)
    manifest["archives"][1]["family_sha256"] = "1" * 64
    with pytest.raises(ArchiveCensusError):
        census_aggregate_only(manifest, tmp_path)


def test_missing_zip_rejected(tmp_path: Path) -> None:
    manifest = _setup(tmp_path)
    (tmp_path / "102.zip").unlink()
    with pytest.raises(ArchiveCensusError):
        census_aggregate_only(manifest, tmp_path)


def test_input_manifest_identity_rejected(tmp_path: Path) -> None:
    manifest = _setup(tmp_path)
    manifest["repository"] = "different/unknown"
    with pytest.raises(ArchiveCensusError):
        census_aggregate_only(manifest, tmp_path)
