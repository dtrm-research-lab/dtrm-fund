"""Offline, positive-only archived first-witness coverage over SHA-pinned ZIPs.

No market outcomes, source text, asset/article identifiers or provider URLs
may leave this module. A positive archive witness is not original link first-seen.
"""
from __future__ import annotations

import hashlib
import json
import lzma
import re
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, NoReturn, Sequence, cast
from zipfile import BadZipFile, ZipFile

CANONICAL_MANIFEST_BLOB_SHA1 = "eb7c91b462ddb822835c20fc126492bfcae5eea0"
ROOTS = ("ranking_news_evidence/", "Outputs/ranking_news_evidence/")
CUTOFFS = (
    "2026-09-19T00:00:00Z",
    "2026-10-01T00:00:00Z",
    "2026-10-10T00:00:00Z",
    "2026-10-15T00:00:00Z",
)
MAX_ZIP_BYTES = 10_000_000
MAX_MEMBER_BYTES = 8_000_000
MAX_TOTAL_UNCOMPRESSED_BYTES = 20_000_000
_SHA = re.compile(r"^[a-f0-9]{64}$")
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ERROR = "REPRODUCTION_NOT_CONFIRMED"
_FREEZE = "daily_news_freeze_manifest_v1.json"
_CANDIDATES = ("daily_news_candidates_2d_v1.json", "daily_news_candidates_5d_v1.json")
_EVIDENCE = {_FREEZE, *_CANDIDATES, *[n + ".sha256" for n in (_FREEZE, *_CANDIDATES)]}

# Frozen descriptive replication targets, not a fresh preregistered finding.
_FAMILY_TARGETS = {
    "bfe784a3e76f80d35350121556fd943af3914ae277c9ace0846d9096f55a99a3":
        (4, 8248, 4834, 13082),
    "ee19badac6ccd5e86343f458e56275dec6e638b91d2465a9eebfc981503b1787":
        (8, 14604, 10787, 25391),
    "debddfd23c420d3a5aedd642edef90e4a5d6eb2e27e3ddb7d0e4140ac1420891":
        (9, 16116, 10775, 26891),
}
_CUTOFF_TARGETS = ((3, 6783), (11, 21350), (18, 33994), (21, 38968))

PrivateTriple = tuple[str, str, str]


class CoverageError(ValueError):
    """Deliberately constant output; never include sensitive source values."""


def _reject() -> NoReturn:
    raise CoverageError(ERROR)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hex(value: object) -> str:
    if not isinstance(value, str) or _SHA.fullmatch(value) is None:
        _reject()
    return value


def _utc(value: object) -> datetime:
    if not isinstance(value, str) or _UTC.fullmatch(value) is None:
        _reject()
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        _reject()
    if dt.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _reject()
    return dt.replace(tzinfo=timezone.utc)


def _json(raw: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                _reject()
            obj[key] = value
        return obj

    def constant(_: str) -> NoReturn:
        _reject()

    try:
        obj = json.loads(raw, object_pairs_hook=unique, parse_constant=constant)
    except (ValueError, UnicodeError, TypeError, RecursionError):
        _reject()
    if not isinstance(obj, dict):
        _reject()
    return cast(dict[str, Any], obj)


@dataclass(frozen=True)
class Snapshot:
    """Contains private triples ONLY in volatile memory; never serialize it."""

    family_sha256: str
    created_at: str
    asof: str
    artifact_id: int
    positives: frozenset[PrivateTriple]


def verify_canonical_manifest(raw: bytes) -> list[dict[str, Any]]:
    if len(raw) > 256_000:
        _reject()
    header = b"blob " + str(len(raw)).encode("ascii") + b"\x00"
    if hashlib.sha1(header + raw).hexdigest() != CANONICAL_MANIFEST_BLOB_SHA1:
        _reject()
    m = _json(raw)
    if (
        m.get("schema_version") != "dtrm.phase4.archived_source_manifest.v0"
        or m.get("dataset_role") != "exploratory_aggregate_source_manifest"
        or m.get("repository") != "tech-com-UA00001/theresistance-back"
        or m.get("workflow") != "DTRM daily ranking"
        or m.get("source_completeness_authenticated") is not False
        or m.get("model_fitting_permitted") is not False
    ):
        _reject()
    rows = m.get("archives")
    if not isinstance(rows, list) or len(rows) != 21:
        _reject()
    if not all(isinstance(x, dict) for x in rows):
        _reject()
    converted = cast(list[dict[str, Any]], rows)
    ids: set[int] = set()
    runs: set[int] = set()
    times: set[str] = set()
    for row in converted:
        run = row.get("run_id")
        aid = row.get("artifact_id")
        clock = row.get("artifact_created_at_utc")
        if (
            type(run) is not int or run <= 0 or run in runs
            or type(aid) is not int or aid <= 0 or aid in ids
            or not isinstance(clock, str) or clock in times
        ):
            _reject()
        _utc(clock)
        _hex(row.get("zip_sha256"))
        _hex(row.get("family_sha256"))
        _hex(row.get("source_news_sha256"))
        runs.add(run)
        ids.add(aid)
        times.add(clock)
    return converted


def _positive_items(body: dict[str, Any]) -> frozenset[PrivateTriple]:
    items = body.get("items")
    if not isinstance(items, list) or len(items) > 500:
        _reject()
    seen_ids: set[str] = set()
    positives: set[PrivateTriple] = set()
    for item in items:
        if not isinstance(item, dict):
            _reject()
        aid = item.get("fmpArticleId")
        text_digest = _hex(item.get("textSha256"))
        tickers = item.get("tickers")
        if (
            not isinstance(aid, str) or not aid.strip()
            or len(aid) > 120 or aid in seen_ids
            or not isinstance(tickers, list)
            or not 1 <= len(tickers) <= 12
        ):
            _reject()
        seen_ids.add(aid)
        set_tickers: set[str] = set()
        for ticker in tickers:
            if (
                not isinstance(ticker, str)
                or not ticker.strip()
                or ticker != ticker.strip()
                or len(ticker) > 24
                or ticker in set_tickers
            ):
                _reject()
            set_tickers.add(ticker)
            positives.add((aid, text_digest, ticker))
    return frozenset(positives)


def _sealed(z: ZipFile, root: str, leaf: str) -> tuple[dict[str, Any], bytes]:
    raw = z.read(root + leaf)
    receipt = z.read(root + leaf + ".sha256").decode("ascii").strip()
    if len(raw) > MAX_MEMBER_BYTES or _digest(raw) != _hex(receipt):
        _reject()
    return _json(raw), raw


def read_one_archive(directory: Path, row: dict[str, Any]) -> Snapshot:
    """Read one original ZIP with bounded I/O; reject all ambiguities."""
    aid = row.get("artifact_id")
    asof = row.get("asof")
    created = row.get("artifact_created_at_utc")
    if type(aid) is not int or aid <= 0 or not isinstance(asof, str):
        _reject()
    dt = _utc(created)
    try:
        if datetime.strptime(asof, "%Y-%m-%d").strftime("%Y-%m-%d") != asof:
            _reject()
    except ValueError:
        _reject()
    archive_path = directory / f"{aid}.zip"
    if (
        archive_path.is_symlink() or not archive_path.is_file()
        or not 0 < archive_path.stat().st_size <= MAX_ZIP_BYTES
    ):
        _reject()
    raw = archive_path.read_bytes()
    if _digest(raw) != _hex(row.get("zip_sha256")):
        _reject()
    family = _hex(row.get("family_sha256"))
    source = _hex(row.get("source_news_sha256"))
    try:
        with ZipFile(BytesIO(raw)) as z:
            infos = z.infolist()
            names = [x.filename for x in infos]
            if (
                len(names) != len(set(names)) or len(names) > 100
                or sum(x.file_size for x in infos) > MAX_TOTAL_UNCOMPRESSED_BYTES
                or any(
                    x.file_size > MAX_MEMBER_BYTES or x.filename.startswith("/")
                    or "\\" in x.filename or ".." in x.filename.split("/")
                    for x in infos
                )
            ):
                _reject()
            possible = [r for r in ROOTS if r + _FREEZE in names]
            if len(possible) != 1:
                _reject()
            root = possible[0]
            exact_evidence_names = {root + leaf for leaf in _EVIDENCE}
            alternate_root = next(r for r in ROOTS if r != root)
            for name in names:
                basename = name.rsplit("/", 1)[-1]
                if basename in _EVIDENCE and name not in exact_evidence_names:
                    _reject()
                if name.startswith(alternate_root):
                    _reject()
            freeze, _ = _sealed(z, root, _FREEZE)
            if (
                freeze.get("schemaVersion") != "1.0" or freeze.get("asOf") != asof
                or freeze.get("familyManifestSha256") != family
                or freeze.get("sourceNewsSha256") != source
            ):
                _reject()
            full: set[PrivateTriple] = set()
            for days, leaf in zip((2, 5), _CANDIDATES):
                body, encoded = _sealed(z, root, leaf)
                positives = _positive_items(body)
                count = body["items"]
                if (
                    body.get("schemaVersion") != "1.0"
                    or body.get("provider") != "financial-modeling-prep"
                    or body.get("windowDays") != days
                    or body.get("asOfDate") != asof
                    or body.get("familyManifestSha256") != family
                    or body.get("sourceNewsSha256") != source
                    or freeze.get(f"candidate{days}dCount") != len(count)
                    or freeze.get(f"candidate{days}dSha256") != _digest(encoded)
                ):
                    _reject()
                full.update(positives)
    except (OSError, ValueError, KeyError, UnicodeError, RuntimeError, BadZipFile,
            EOFError, zlib.error, lzma.LZMAError, RecursionError):
        _reject()
    return Snapshot(family, dt.strftime("%Y-%m-%dT%H:%M:%SZ"), asof, aid,
                    frozenset(full))


def _family_summary(snapshots: Sequence[Snapshot]) -> dict[str, int]:
    seen: set[PrivateTriple] = set()
    appearances = 0
    repeated = 0
    for snap in sorted(snapshots, key=lambda s: s.created_at):
        appearances += len(snap.positives)
        repeated += len(snap.positives & seen)
        seen.update(snap.positives)
    return {
        "admitted_snapshots": len(snapshots),
        "distinct_positive_representations": len(seen),
        "captured_positive_appearances": appearances,
        "repeat_positive_appearances": repeated,
    }


def calculate_coverage(snapshots: Sequence[Snapshot]) -> dict[str, Any]:
    """Pure positive-only reducer; no cross-family source-state merging."""
    if len(snapshots) < 1 or len({s.artifact_id for s in snapshots}) != len(snapshots):
        _reject()
    groups: dict[str, list[Snapshot]] = {}
    for snap in snapshots:
        _hex(snap.family_sha256)
        _utc(snap.created_at)
        groups.setdefault(snap.family_sha256, []).append(snap)
    families = []
    global_distinct: set[PrivateTriple] = set()
    for family in sorted(groups):
        snaps = sorted(groups[family], key=lambda s: s.created_at)
        summary = _family_summary(snaps)
        families.append({"family_sha256": family, **summary})
        for snap in snaps:
            global_distinct.update(snap.positives)

    cuts = []
    for cutoff in CUTOFFS:
        detail = []
        for family in sorted(groups):
            eligible = [
                s for s in groups[family] if _utc(s.created_at) < _utc(cutoff)
            ]
            detail.append({"family_sha256": family, **_family_summary(eligible)})
        cuts.append({
            "cutoff_utc": cutoff,
            "admitted_snapshots": sum(cast(int, d["admitted_snapshots"]) for d in detail),
            "family_summed_distinct_positive": sum(
                cast(int, d["distinct_positive_representations"]) for d in detail
            ),
            "family_summed_capture_appearances": sum(
                cast(int, d["captured_positive_appearances"]) for d in detail
            ),
            "family_summed_repeat_appearances": sum(
                cast(int, d["repeat_positive_appearances"]) for d in detail
            ),
            "families": detail,
        })
    return {
        "schema_version": "dtrm.phase4.archived_first_witness_reproduction.v1",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "source_manifest_git_blob_sha1": CANONICAL_MANIFEST_BLOB_SHA1,
        "metadata_independently_authenticated": False,
        "original_link_first_seen_authenticated": False,
        "historical_absence_authenticated": False,
        "source_completeness_authenticated": False,
        "price_clock_authenticated": False,
        "model_fitting_permitted": False,
        "outcomes_access_permitted": False,
        "mm1_execution_permitted": False,
        "scientific_counting_permitted": False,
        "source_archive_count": len(snapshots),
        "family_count": len(groups),
        "family_summed_distinct_positive": sum(
            f["distinct_positive_representations"] for f in families
        ),
        "globally_deduplicated_positive_representations": len(global_distinct),
        "families": families,
        "cutoffs": cuts,
    }


def verify_original_coverage_targets(report: dict[str, Any]) -> None:
    """Reproduce old descriptive figures; never retune them after results."""
    if (
        report["source_archive_count"] != 21 or report["family_count"] != 3
        or report["family_summed_distinct_positive"] != 38968
        or report["globally_deduplicated_positive_representations"] != 36440
    ):
        _reject()
    families = report["families"]
    if len(families) != len(_FAMILY_TARGETS):
        _reject()
    for f in families:
        target = _FAMILY_TARGETS.get(f["family_sha256"])
        if target is None or (
            f["admitted_snapshots"],
            f["distinct_positive_representations"],
            f["repeat_positive_appearances"],
            f["captured_positive_appearances"],
        ) != target:
            _reject()
    cuts = report["cutoffs"]
    if len(cuts) != 4:
        _reject()
    for row, expected in zip(cuts, _CUTOFF_TARGETS):
        if (row["admitted_snapshots"],
            row["family_summed_distinct_positive"]) != expected:
            _reject()
    report["reproduction_status"] = "PASS_CANONICAL_FIRST_WITNESS_COVERAGE_REPRODUCED"
