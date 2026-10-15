"""Fictional fixtures only; all real article and ticker values stay private."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from dtrm.phase4.archived_first_witness_coverage import (
    ERROR,
    CoverageError,
    PrivateTriple,
    Snapshot,
    calculate_coverage,
    read_one_archive,
    verify_canonical_manifest,
    verify_original_coverage_targets,
)

F1 = hashlib.sha256(b"fictional family 1").hexdigest()
F2 = hashlib.sha256(b"fictional family 2").hexdigest()
ARTICLE = "private-fake-id"
TICKER = "PRIVATE_FAKE_TICKER"
VINTAGE = hashlib.sha256(b"private fictional news vintage").hexdigest()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ser(x: object) -> bytes:
    return (json.dumps(x, sort_keys=True) + "\n").encode()


def _zip(asof: str, family: str, root: str = "ranking_news_evidence/") -> bytes:
    source = _sha(asof.encode())
    freeze: dict[str, object] = {
        "schemaVersion": "1.0",
        "asOf": asof,
        "familyManifestSha256": family,
        "sourceNewsSha256": source,
    }
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as z:
        for days in (2, 5):
            body = {
                "schemaVersion": "1.0",
                "asOfDate": asof,
                "provider": "financial-modeling-prep",
                "windowDays": days,
                "familyManifestSha256": family,
                "sourceNewsSha256": source,
                "items": [{
                    "fmpArticleId": ARTICLE,
                    "textSha256": VINTAGE,
                    "tickers": [TICKER],
                    "text": "secret fictional news text",
                    "sourceUrl": "https://test.invalid/private-source",
                }],
            }
            raw = _ser(body)
            leaf = f"daily_news_candidates_{days}d_v1.json"
            z.writestr(root + leaf, raw)
            z.writestr(root + leaf + ".sha256", _sha(raw))
            freeze[f"candidate{days}dCount"] = 1
            freeze[f"candidate{days}dSha256"] = _sha(raw)
        raw = _ser(freeze)
        z.writestr(root + "daily_news_freeze_manifest_v1.json", raw)
        z.writestr(root + "daily_news_freeze_manifest_v1.json.sha256", _sha(raw))
    return stream.getvalue()


def _row(folder: Path, *, bad_archive_sha: bool = False) -> dict[str, object]:
    blob = _zip("2026-09-15", F1)
    (folder / "101.zip").write_bytes(blob)
    return {
        "artifact_id": 101,
        "run_id": 1,
        "asof": "2026-09-15",
        "artifact_created_at_utc": "2026-09-16T01:00:00Z",
        "family_sha256": F1,
        "source_news_sha256": _sha(b"2026-09-15"),
        "zip_sha256": "0" * 64 if bad_archive_sha else _sha(blob),
    }


def test_reader_accepts_sha_sealed_fictional_positive_only_zip(
    tmp_path: Path,
) -> None:
    row = _row(tmp_path)
    witness = read_one_archive(tmp_path, row)
    assert witness.family_sha256 == F1
    assert len(witness.positives) == 1
    result = calculate_coverage([witness])
    emitted = json.dumps(result)
    assert ARTICLE not in emitted
    assert TICKER not in emitted
    assert "private fictional news text" not in emitted
    assert "test.invalid" not in emitted
    assert result["historical_absence_authenticated"] is False
    assert result["model_fitting_permitted"] is False


def test_reader_rejects_changed_original_zip_hash(tmp_path: Path) -> None:
    with pytest.raises(CoverageError, match=ERROR):
        read_one_archive(tmp_path, _row(tmp_path, bad_archive_sha=True))


def test_reader_allows_observed_legacy_root(tmp_path: Path) -> None:
    blob = _zip("2026-09-15", F1, "Outputs/ranking_news_evidence/")
    (tmp_path / "101.zip").write_bytes(blob)
    row = _row(tmp_path)
    (tmp_path / "101.zip").write_bytes(blob)
    row["zip_sha256"] = _sha(blob)
    assert len(read_one_archive(tmp_path, row).positives) == 1


def test_family_cutoffs_exclude_exact_clock_ties_and_never_merge_families() -> None:
    a: PrivateTriple = (ARTICLE, VINTAGE, TICKER)
    b: PrivateTriple = ("second-fake-id", VINTAGE, "BETA_FAKE")
    snapshots = [
        Snapshot(F1, "2026-09-18T01:00:00Z", "2026-09-17", 1, frozenset({a})),
        Snapshot(F1, "2026-09-19T00:00:00Z", "2026-09-18", 2, frozenset({a, b})),
        Snapshot(F2, "2026-09-19T01:00:00Z", "2026-09-18", 3, frozenset({a})),
    ]
    r = calculate_coverage(snapshots[::-1])
    assert r["globally_deduplicated_positive_representations"] == 2
    assert r["family_summed_distinct_positive"] == 3
    assert r["cutoffs"][0]["admitted_snapshots"] == 1
    assert r["cutoffs"][0]["family_summed_distinct_positive"] == 1
    assert r["cutoffs"][1]["admitted_snapshots"] == 3
    assert r["cutoffs"][1]["family_summed_distinct_positive"] == 3
    f1 = next(x for x in r["families"] if x["family_sha256"] == F1)
    assert f1["distinct_positive_representations"] == 2
    assert f1["captured_positive_appearances"] == 3
    assert f1["repeat_positive_appearances"] == 1
    assert ARTICLE not in json.dumps(r)
    assert TICKER not in json.dumps(r)
    assert r["metadata_independently_authenticated"] is False
    assert r["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    with pytest.raises(CoverageError):
        verify_original_coverage_targets(r)


def test_exact_canonical_source_metadata_copy_is_pinned() -> None:
    path = (
        Path(__file__).resolve().parents[1] / "research" / "evidence"
        / "DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json"
    )
    rows = verify_canonical_manifest(path.read_bytes())
    assert len(rows) == 21
    assert len({row["artifact_id"] for row in rows}) == 21
    with pytest.raises(CoverageError):
        verify_canonical_manifest(path.read_bytes() + b"\n")


def test_cli_two_zip_input_never_publishes_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    cli_file = (
        Path(__file__).resolve().parents[1] / "research" / "experiments"
        / "run_phase4_archived_first_witness_coverage_v1.py"
    )
    spec = importlib.util.spec_from_file_location("phase4_first_witness_cli", cli_file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    row = _row(tmp_path)
    manifest_path = tmp_path / "synthetic_manifest.json"
    manifest_path.write_bytes(_ser({"archives": [row]}))
    output = tmp_path / "result.json"
    status = module.main([
        "--manifest", str(manifest_path),
        "--archive-dir", str(tmp_path),
        "--output", str(output),
    ])
    assert status != 0
    assert not output.exists()
    assert ERROR in capsys.readouterr().err


def test_nested_shadow_evidence_rejected_even_inside_valid_root(
    tmp_path: Path,
) -> None:
    row = _row(tmp_path)
    original = (tmp_path / "101.zip").read_bytes()
    out = BytesIO()
    with ZipFile(BytesIO(original)) as src:
        with ZipFile(out, "w", compression=ZIP_DEFLATED) as dst:
            for item in src.infolist():
                dst.writestr(item.filename, src.read(item.filename))
            dst.writestr(
                "ranking_news_evidence/hidden/daily_news_candidates_2d_v1.json",
                b"{}",
            )
    shadow = out.getvalue()
    (tmp_path / "101.zip").write_bytes(shadow)
    row["zip_sha256"] = _sha(shadow)
    with pytest.raises(CoverageError, match=ERROR):
        read_one_archive(tmp_path, row)
