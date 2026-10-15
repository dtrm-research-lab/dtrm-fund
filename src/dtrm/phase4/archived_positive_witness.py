"""Offline, aggregate-only positive witness comparison of sealed ranking archives.

No Mongo, network, secret, price, outcome, model or production operations.
The caller owns private ZIP bytes; no article IDs or tickers leave the reducer.
"""

from __future__ import annotations

import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from io import BytesIO
from typing import Any, NoReturn, cast
from zipfile import BadZipFile, ZipFile

MAX_ZIP_BYTES = 10 * 1024 * 1024
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024
ROOT = "ranking_news_evidence/"
HEX_SHA = re.compile(r"[a-f0-9]{64}\Z")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


class ArchivedWitnessError(ValueError):
    """Fixed error with no embedded source or private provider identifiers."""


def _reject() -> NoReturn:
    raise ArchivedWitnessError("INVALID_PHASE4_ARCHIVED_WITNESS")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(value: object) -> str:
    if not isinstance(value, str) or not HEX_SHA.fullmatch(value):
        _reject()
    return value


def _id(value: object) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 120 or not value.strip():
        _reject()
    return value


def _json(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_FILE_BYTES:
        _reject()

    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, value in pairs:
            if key in output:
                _reject()
            output[key] = value
        return output

    def invalid_constant(_value: str) -> NoReturn:
        _reject()

    try:
        result = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=unique_pairs,
            parse_constant=invalid_constant,
        )
    except (UnicodeError, ValueError, TypeError, RecursionError):
        _reject()
    if not isinstance(result, dict):
        _reject()
    return cast(dict[str, Any], result)


def _date(value: object) -> date:
    if not isinstance(value, str) or not DATE.fullmatch(value):
        _reject()
    try:
        return date.fromisoformat(value)
    except ValueError:
        _reject()


def _created(value: object) -> datetime:
    if not isinstance(value, str) or value.endswith("-00:00"):
        _reject()
    try:
        time = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if time.tzinfo is None or time.utcoffset() is None:
            _reject()
        return time.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        _reject()


def _sealed_read(z: ZipFile, name: str) -> bytes:
    try:
        content = z.read(name)
        receipt = z.read(name + ".sha256").decode("ascii").strip()
    except (KeyError, OSError, UnicodeError, RuntimeError, BadZipFile, ValueError, zlib.error):
        _reject()
    if _hash(content) != _sha(receipt):
        _reject()
    return content


@dataclass(frozen=True, slots=True)
class _Archive:
    run_id: int
    zip_sha256: str
    created_at: datetime
    asof: date
    family_sha256: str
    snapshots: tuple[tuple[str, tuple[tuple[str, str, tuple[str, ...]], ...]], ...]


def _read_archive(
    raw: bytes,
    *,
    run_id: int,
    expected_zip_sha256: str,
    artifact_created_at: str,
) -> _Archive:
    if type(run_id) is not int or run_id <= 0:
        _reject()
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_ZIP_BYTES:
        _reject()
    expected = _sha(expected_zip_sha256)
    if _hash(raw) != expected:
        _reject()
    created_at = _created(artifact_created_at)
    try:
        with ZipFile(BytesIO(raw)) as z:
            names = z.namelist()
            files = z.infolist()
            if (
                len(names) != len(set(names))
                or len(names) > 100
                or any(
                    p.startswith("/") or ".." in p.split("/") or "\\" in p
                    for p in names
                )
                or sum(f.file_size for f in files) > MAX_UNCOMPRESSED_BYTES
                or any(f.file_size > MAX_FILE_BYTES for f in files)
            ):
                _reject()
            manifest = _json(_sealed_read(z, ROOT + "daily_news_freeze_manifest_v1.json"))
            asof = _date(manifest.get("asOf"))
            family = _sha(manifest.get("familyManifestSha256"))
            news = _sha(manifest.get("sourceNewsSha256"))
            if manifest.get("schemaVersion") != "1.0":
                _reject()
            bundles: list[tuple[str, tuple[tuple[str, str, tuple[str, ...]], ...]]] = []
            for days in (2, 5):
                tag = f"{days}d"
                filename = ROOT + f"daily_news_candidates_{tag}_v1.json"
                payload = _sealed_read(z, filename)
                if _hash(payload) != _sha(manifest.get(f"candidate{tag}Sha256")):
                    _reject()
                doc = _json(payload)
                if (
                    doc.get("schemaVersion") != "1.0"
                    or doc.get("provider") != "financial-modeling-prep"
                    or doc.get("windowDays") != days
                    or doc.get("asOfDate") != asof.isoformat()
                    or doc.get("familyManifestSha256") != family
                    or doc.get("sourceNewsSha256") != news
                ):
                    _reject()
                items = doc.get("items")
                if not isinstance(items, list) or not 0 <= len(items) <= 500:
                    _reject()
                if type(manifest.get(f"candidate{tag}Count")) is not int or len(items) != manifest[f"candidate{tag}Count"]:
                    _reject()
                typed: list[tuple[str, str, tuple[str, ...]]] = []
                seen: set[str] = set()
                for item in items:
                    if not isinstance(item, dict):
                        _reject()
                    aid = _id(item.get("fmpArticleId"))
                    if aid in seen:
                        _reject()
                    seen.add(aid)
                    text = _sha(item.get("textSha256"))
                    values = item.get("tickers")
                    if (
                        not isinstance(values, list) or not 1 <= len(values) <= 12
                        or any(
                            not isinstance(v, str) or not v.strip() or v != v.strip()
                            or len(v) > 24 for v in values
                        )
                        or len(set(values)) != len(values)
                    ):
                        _reject()
                    typed.append((aid, text, tuple(sorted(values))))
                bundles.append((tag, tuple(sorted(typed))))
    except (BadZipFile, EOFError, OSError, RuntimeError, OverflowError, ValueError, zlib.error):
        _reject()
    return _Archive(run_id, expected, created_at, asof, family, tuple(bundles))


@dataclass(frozen=True, slots=True)
class WindowWitness:
    window: str
    earlier_count: int
    later_count: int
    earlier_potentially_truncated: bool
    later_potentially_truncated: bool
    shared_article_ids: int
    shared_exact_text_versions: int
    articles_with_unchanged_ticker_set: int
    stable_article_ticker_links: int
    changed_link_set_on_exact_text: int
    later_only_pairs_on_shared_text: int
    earlier_only_pairs_on_shared_text: int

    def to_json(self) -> dict[str, object]:
        return {
            "window": self.window,
            "earlier_count": self.earlier_count,
            "later_count": self.later_count,
            "earlier_potentially_truncated": self.earlier_potentially_truncated,
            "later_potentially_truncated": self.later_potentially_truncated,
            "shared_article_ids": self.shared_article_ids,
            "shared_exact_text_versions": self.shared_exact_text_versions,
            "articles_with_unchanged_ticker_set": self.articles_with_unchanged_ticker_set,
            "stable_article_ticker_links": self.stable_article_ticker_links,
            "changed_link_set_on_exact_text": self.changed_link_set_on_exact_text,
            "later_only_pairs_on_shared_text": self.later_only_pairs_on_shared_text,
            "earlier_only_pairs_on_shared_text": self.earlier_only_pairs_on_shared_text,
        }


@dataclass(frozen=True, slots=True)
class ArchivedWitnessAssessment:
    early_run_id: int
    late_run_id: int
    early_zip_sha256: str
    late_zip_sha256: str
    early_created_at: str
    late_created_at: str
    early_asof: str
    late_asof: str
    family_sha256: str
    windows: tuple[WindowWitness, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "schema_version": "dtrm.phase4.archived_positive_witness_report.v0",
            "engineering_status": "PASS_ARCHIVED_POSITIVE_WITNESS_COMPARISON",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "witness_type": "POSITIVE_SHARED_FROZEN_REPRESENTATION",
            "nonobserved_link_state": "UNKNOWN_NOT_OBSERVED_IN_SELECTED_EXPORT",
            "snapshot_metadata_independently_authenticated": False,
            "original_link_first_seen_authenticated": False,
            "absence_authenticated": False,
            "source_completeness_authenticated": False,
            "price_clock_authenticated": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "scientific_counting_permitted": False,
            "early_run_id": self.early_run_id,
            "late_run_id": self.late_run_id,
            "early_zip_sha256": self.early_zip_sha256,
            "late_zip_sha256": self.late_zip_sha256,
            "early_created_at": self.early_created_at,
            "late_created_at": self.late_created_at,
            "early_asof": self.early_asof,
            "late_asof": self.late_asof,
            "family_sha256": self.family_sha256,
            "windows": [w.to_json() for w in self.windows],
        }


def compare_archived_positive_witnesses(
    early_zip: bytes,
    late_zip: bytes,
    *,
    early_run_id: int,
    late_run_id: int,
    early_sha256: str,
    late_sha256: str,
    early_artifact_created_at: str,
    late_artifact_created_at: str,
) -> ArchivedWitnessAssessment:
    """Compute positive archived overlap, never historical source nonexistence."""
    early = _read_archive(
        early_zip, run_id=early_run_id, expected_zip_sha256=early_sha256,
        artifact_created_at=early_artifact_created_at,
    )
    late = _read_archive(
        late_zip, run_id=late_run_id, expected_zip_sha256=late_sha256,
        artifact_created_at=late_artifact_created_at,
    )
    if (
        early.run_id == late.run_id or early.created_at >= late.created_at
        or early.asof >= late.asof or early.family_sha256 != late.family_sha256
    ):
        _reject()
    results: list[WindowWitness] = []
    for (tag_a, vals_a), (tag_b, vals_b) in zip(early.snapshots, late.snapshots, strict=True):
        if tag_a != tag_b:
            _reject()
        a = {aid: (text, set(tickers)) for aid, text, tickers in vals_a}
        b = {aid: (text, set(tickers)) for aid, text, tickers in vals_b}
        common = a.keys() & b.keys()
        same = [key for key in common if a[key][0] == b[key][0]]
        exact = sum(a[key][1] == b[key][1] for key in same)
        stable = sum(len(a[key][1] & b[key][1]) for key in same)
        changed = [key for key in same if a[key][1] != b[key][1]]
        results.append(WindowWitness(
            window=tag_a, earlier_count=len(a), later_count=len(b),
            earlier_potentially_truncated=len(a) == 500,
            later_potentially_truncated=len(b) == 500,
            shared_article_ids=len(common), shared_exact_text_versions=len(same),
            articles_with_unchanged_ticker_set=exact,
            stable_article_ticker_links=stable,
            changed_link_set_on_exact_text=len(changed),
            later_only_pairs_on_shared_text=sum(len(b[x][1] - a[x][1]) for x in changed),
            earlier_only_pairs_on_shared_text=sum(len(a[x][1] - b[x][1]) for x in changed),
        ))
    return ArchivedWitnessAssessment(
        early.run_id, late.run_id, early.zip_sha256, late.zip_sha256,
        early.created_at.isoformat(), late.created_at.isoformat(),
        early.asof.isoformat(), late.asof.isoformat(), early.family_sha256,
        tuple(results),
    )
