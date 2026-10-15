"""Fully synthetic archived witness tests; no real news/tickers are checked in."""

from __future__ import annotations

import hashlib
import json
import lzma
import zlib
from dataclasses import FrozenInstanceError
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from dtrm.phase4.archived_positive_witness import (
    ArchivedWitnessError,
    compare_archived_positive_witnesses,
)

FAMILY = hashlib.sha256(b"family").hexdigest()


def _dump(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")


def _article(article_id: str, *, tickers: list[str], text: str = "original") -> dict:
    return {
        "fmpArticleId": article_id,
        "textSha256": hashlib.sha256(text.encode()).hexdigest(),
        "tickers": tickers,
        "headline": "synthetic secret headline must not appear",
        "text": "synthetic confidential content must not appear",
        "sourceUrl": "https://example.invalid/private-test",
    }


def _zip(asof: str, articles: list[dict], *, family: str = FAMILY,
         root: str = "ranking_news_evidence/") -> bytes:
    news_sha = hashlib.sha256(asof.encode()).hexdigest()
    manifest = {
        "schemaVersion": "1.0",
        "asOf": asof,
        "familyManifestSha256": family,
        "sourceNewsSha256": news_sha,
    }
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as z:
        for window in (2, 5):
            doc = {
                "schemaVersion": "1.0",
                "asOfDate": asof,
                "familyManifestSha256": family,
                "sourceNewsSha256": news_sha,
                "provider": "financial-modeling-prep",
                "windowDays": window,
                "items": articles,
            }
            raw = _dump(doc)
            basename = root + f"daily_news_candidates_{window}d_v1.json"
            digest = hashlib.sha256(raw).hexdigest()
            manifest[f"candidate{window}dCount"] = len(articles)
            manifest[f"candidate{window}dSha256"] = digest
            z.writestr(basename, raw)
            z.writestr(basename + ".sha256", digest + "\n")
        raw_manifest = _dump(manifest)
        filename = root + "daily_news_freeze_manifest_v1.json"
        z.writestr(filename, raw_manifest)
        z.writestr(filename + ".sha256", hashlib.sha256(raw_manifest).hexdigest() + "\n")
    return output.getvalue()


def _compare(first: bytes, second: bytes, *, late_id: int = 2):
    return compare_archived_positive_witnesses(
        first, second, early_run_id=1, late_run_id=late_id,
        early_sha256=hashlib.sha256(first).hexdigest(),
        late_sha256=hashlib.sha256(second).hexdigest(),
        early_artifact_created_at="2026-10-13T03:11:15Z",
        late_artifact_created_at="2026-10-14T01:24:19Z",
    )


def test_exact_archive_witnesses_and_no_source_value_in_report() -> None:
    pre = _zip("2026-10-12", [
        _article("private-article-alpha", tickers=["FAKE1", "FAKE2"]),
        _article("private-article-beta", tickers=["FAKE3"]),
    ])
    post = _zip("2026-10-13", [
        _article("private-article-alpha", tickers=["FAKE1", "FAKE4"]),
        _article("private-article-beta", tickers=["FAKE3"]),
    ])
    state = _compare(pre, post)
    report = state.to_json()
    assert report["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    assert len(report["windows"]) == 2
    for window in report["windows"]:
        assert window["shared_article_ids"] == 2
        assert window["shared_exact_text_versions"] == 2
        assert window["articles_with_unchanged_ticker_set"] == 1
        assert window["stable_article_ticker_links"] == 2
        assert window["changed_link_set_on_exact_text"] == 1
        assert window["later_only_pairs_on_shared_text"] == 1
        assert window["earlier_only_pairs_on_shared_text"] == 1
        assert window["earlier_potentially_truncated"] is False
        assert window["later_potentially_truncated"] is False
    encoded = json.dumps(report)
    for secret in ("private-article-", "FAKE", "synthetic secret", "private-test"):
        assert secret not in encoded
    for gate in (
        "snapshot_metadata_independently_authenticated",
        "original_link_first_seen_authenticated",
        "absence_authenticated",
        "source_completeness_authenticated",
        "price_clock_authenticated",
        "model_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "scientific_counting_permitted",
    ):
        assert report[gate] is False


def test_text_revision_is_not_same_vintage() -> None:
    first = _zip("2026-10-12", [_article("same-id", tickers=["T1"], text="old")])
    second = _zip("2026-10-13", [_article("same-id", tickers=["T1"], text="new")])
    result = _compare(first, second).to_json()["windows"][0]
    assert result["shared_article_ids"] == 1
    assert result["shared_exact_text_versions"] == 0
    assert result["stable_article_ticker_links"] == 0


def test_absence_from_later_selected_export_is_never_negative_evidence() -> None:
    pre = _zip("2026-10-12", [_article("present-earlier", tickers=["T1"])])
    post = _zip("2026-10-13", [_article("different-later", tickers=["T2"])])
    result = _compare(pre, post).to_json()
    assert result["windows"][0]["shared_article_ids"] == 0
    assert result["absence_authenticated"] is False
    assert result["nonobserved_link_state"] == "UNKNOWN_NOT_OBSERVED_IN_SELECTED_EXPORT"


def test_inmemory_state_is_immutable_and_report_detached() -> None:
    source = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    later = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    frozen = _compare(source, later)
    with pytest.raises(FrozenInstanceError):
        frozen.early_run_id = 123
    public = frozen.to_json()
    public["windows"][0]["stable_article_ticker_links"] = 900
    public["source_completeness_authenticated"] = True
    assert frozen.to_json()["source_completeness_authenticated"] is False
    assert frozen.to_json()["windows"][0]["stable_article_ticker_links"] == 1


def test_rejects_changed_zip_bytes() -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    second = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with pytest.raises(ArchivedWitnessError, match="INVALID_PHASE4_ARCHIVED_WITNESS"):
        compare_archived_positive_witnesses(
            first, second, early_run_id=1, late_run_id=2,
            early_sha256="0" * 64,
            late_sha256=hashlib.sha256(second).hexdigest(),
            early_artifact_created_at="2026-10-13T03:11:15Z",
            late_artifact_created_at="2026-10-14T01:24:19Z",
        )


@pytest.mark.parametrize("change", [
    lambda x: _zip("2026-10-12", [_article("x", tickers=["T1"])]),
    lambda x: _zip("2026-10-13", [_article("x", tickers=["T1"]), _article("x", tickers=["T1"])]),
    lambda x: _zip("2026-10-13", [_article("x", tickers=["T1", "T1"])]),
])
def test_fail_closed_on_family_date_duplicate_id_or_ticker(change) -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    bad = change(first)
    with pytest.raises(ArchivedWitnessError):
        _compare(first, bad)


def test_identical_run_ids_are_not_independent_witnesses() -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    later = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with pytest.raises(ArchivedWitnessError):
        _compare(first, later, late_id=1)


def test_corrupted_digest_or_duplicate_zip_entry_rejected() -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    second = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(second)) as z:
        files = {name: z.read(name) for name in z.namelist()}
    receipt = "ranking_news_evidence/daily_news_candidates_2d_v1.json.sha256"
    files[receipt] = b"f" * 64
    out = BytesIO()
    with ZipFile(out, "w") as z:
        for name, value in files.items():
            z.writestr(name, value)
    with pytest.raises(ArchivedWitnessError):
        _compare(first, out.getvalue())


@pytest.mark.parametrize("bad_ticker", ["   ", " X", "X ", "\t", "\n"])
def test_whitespace_ticker_never_becomes_positive_witness(bad_ticker: str) -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    later = _zip("2026-10-13", [_article("x", tickers=[bad_ticker])])
    with pytest.raises(ArchivedWitnessError, match="INVALID_PHASE4_ARCHIVED_WITNESS"):
        _compare(early, later)


@pytest.mark.parametrize("broken", [
    lambda: zlib.error("synthetic inflate exception containing private content"),
    lambda: ValueError("synthetic invalid compressed bytes"),
])
def test_member_read_decompression_errors_are_fixed_domain_errors(monkeypatch, broken) -> None:
    before = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    after = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    original = ZipFile.read

    def fail_selected_member(self, name, *args, **kwargs):
        if name == "ranking_news_evidence/daily_news_candidates_2d_v1.json":
            raise broken()
        return original(self, name, *args, **kwargs)

    monkeypatch.setattr(ZipFile, "read", fail_selected_member)
    with pytest.raises(ArchivedWitnessError, match="^INVALID_PHASE4_ARCHIVED_WITNESS$"):
        _compare(before, after)


def test_corrupt_member_with_matching_new_zip_digest_is_rejected() -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    later = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(later)) as z:
        item = z.getinfo("ranking_news_evidence/daily_news_candidates_2d_v1.json")
        offset = item.header_offset
    local_name_bytes = int.from_bytes(later[offset + 26:offset + 28], "little")
    extra_bytes = int.from_bytes(later[offset + 28:offset + 30], "little")
    payload_offset = offset + 30 + local_name_bytes + extra_bytes
    corrupted = bytearray(later)
    corrupted[payload_offset + 2] ^= 0xFF
    with pytest.raises(ArchivedWitnessError, match="^INVALID_PHASE4_ARCHIVED_WITNESS$"):
        _compare(early, bytes(corrupted))


def test_two_pinned_real_archive_roots_are_valid_with_same_family() -> None:
    early = _zip("2026-10-12", [_article("same", tickers=["T1", "T2"])],
                 root="Outputs/ranking_news_evidence/")
    late = _zip("2026-10-13", [_article("same", tickers=["T1", "T2"])])
    result = _compare(early, late).to_json()
    assert result["windows"][0]["stable_article_ticker_links"] == 2
    assert result["scientific_status"] == "BLOCKED_SOURCE_AUDIT"


def test_two_roots_in_one_archive_are_rejected() -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    late = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(late)) as z:
        entries = [(name, z.read(name)) for name in z.namelist()]
    out = BytesIO()
    with ZipFile(out, "w") as z:
        for name, value in entries:
            z.writestr(name, value)
        z.writestr(
            "Outputs/ranking_news_evidence/daily_news_freeze_manifest_v1.json",
            b"{}",
        )
    with pytest.raises(ArchivedWitnessError):
        _compare(early, out.getvalue())


def test_archive_with_mixed_roots_is_rejected() -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    late = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(late)) as z:
        entries = [(name, z.read(name)) for name in z.namelist()]
    out = BytesIO()
    with ZipFile(out, "w") as z:
        for name, value in entries:
            if name.endswith("daily_news_candidates_5d_v1.json.sha256"):
                name = "Outputs/" + name
            z.writestr(name, value)
    with pytest.raises(ArchivedWitnessError):
        _compare(early, out.getvalue())


def test_distinct_frozen_family_is_a_no_witness_block_not_corruption() -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    second = _zip("2026-10-13", [_article("x", tickers=["T1"])], family="f" * 64)
    report = _compare(first, second).to_json()
    assert report["engineering_status"] == "BLOCKED_FAMILY_LINEAGE_MISMATCH"
    assert report["family_sha256"] == FAMILY
    assert report["late_family_sha256"] == "f" * 64
    assert report["windows"] == []
    assert report["witness_type"] == "NO_COMPARABLE_WITNESS"
    assert report["scientific_counting_permitted"] is False
    assert report["original_link_first_seen_authenticated"] is False
    assert report["model_fitting_permitted"] is False
    assert report["outcome_access_permitted"] is False
    assert report["mm1_execution_permitted"] is False


def test_unrecognized_second_complete_evidence_root_is_rejected() -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    later = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(later)) as z:
        entries = [(name, z.read(name)) for name in z.namelist()]
    out = BytesIO()
    with ZipFile(out, "w") as z:
        for name, value in entries:
            z.writestr(name, value)
            z.writestr("unknown/" + name, value)
    with pytest.raises(ArchivedWitnessError, match="INVALID_PHASE4_ARCHIVED_WITNESS"):
        _compare(early, out.getvalue())


def test_shadow_evidence_at_zip_top_level_is_rejected() -> None:
    early = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    late = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(late)) as z:
        entries = [(name, z.read(name)) for name in z.namelist()]
    out = BytesIO()
    with ZipFile(out, "w") as z:
        for name, value in entries:
            z.writestr(name, value)
            z.writestr(name.split("/")[-1], value)
    with pytest.raises(ArchivedWitnessError, match="INVALID_PHASE4_ARCHIVED_WITNESS"):
        _compare(early, out.getvalue())


def test_lzma_decompressor_error_is_fail_closed(monkeypatch) -> None:
    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    second = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    original_read = ZipFile.read

    def fail_lzma(self, name, *args, **kwargs):
        if name == "ranking_news_evidence/daily_news_candidates_2d_v1.json":
            raise lzma.LZMAError("sensitive fake decompression content")
        return original_read(self, name, *args, **kwargs)

    monkeypatch.setattr(ZipFile, "read", fail_lzma)
    with pytest.raises(ArchivedWitnessError, match="^INVALID_PHASE4_ARCHIVED_WITNESS$"):
        _compare(first, second)


def test_corrupted_lzma_zip_member_with_valid_outer_digest_rejected() -> None:
    from zipfile import ZIP_LZMA

    first = _zip("2026-10-12", [_article("x", tickers=["T1"])])
    raw = _zip("2026-10-13", [_article("x", tickers=["T1"])])
    with ZipFile(BytesIO(raw)) as original:
        entries = [(name, original.read(name)) for name in original.namelist()]
    compressed = BytesIO()
    with ZipFile(compressed, "w", compression=ZIP_LZMA) as archive:
        for name, value in entries:
            archive.writestr(name, value)
    valid_lzma = compressed.getvalue()
    assert _compare(first, valid_lzma).to_json()["windows"][0]["stable_article_ticker_links"] == 1
    with ZipFile(BytesIO(valid_lzma)) as archive:
        item = archive.getinfo("ranking_news_evidence/daily_news_candidates_2d_v1.json")
        offset = item.header_offset
    name_size = int.from_bytes(valid_lzma[offset + 26:offset + 28], "little")
    extra_size = int.from_bytes(valid_lzma[offset + 28:offset + 30], "little")
    payload_start = offset + 30 + name_size + extra_size
    damaged = bytearray(valid_lzma)
    damaged[payload_start + 12] ^= 0xFF
    with pytest.raises(ArchivedWitnessError, match="^INVALID_PHASE4_ARCHIVED_WITNESS$"):
        _compare(first, bytes(damaged))
