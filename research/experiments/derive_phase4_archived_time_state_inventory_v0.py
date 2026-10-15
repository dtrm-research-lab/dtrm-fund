"""Reproduce Phase IV positive archived witness aggregates offline from private ZIPs.

Each private ZIP is named <artifact_id>.zip in --archive-dir. No source values
are printed, written, committed, or used as financial outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zlib
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, NoReturn, cast
from zipfile import BadZipFile, ZipFile

CANONICAL_SOURCE_MANIFEST_GIT_BLOB_SHA1 = "eb7c91b462ddb822835c20fc126492bfcae5eea0"
MAX_ZIP = 10 * 1024 * 1024
MAX_ENTRY = 8 * 1024 * 1024
MAX_TOTAL = 20 * 1024 * 1024
ROOTS = ("ranking_news_evidence/", "Outputs/ranking_news_evidence/")
HEXDIGEST = re.compile(r"[0-9a-f]{64}\Z")


class ArchiveCensusError(ValueError):
    """A fixed, source-value-free error."""


def _stop() -> NoReturn:
    raise ArchiveCensusError("INVALID_ARCHIVED_RANKING_CENSUS")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_check(raw: Any) -> str:
    if not isinstance(raw, str) or not HEXDIGEST.fullmatch(raw):
        _stop()
    return raw


def _json(raw: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        answer: dict[str, Any] = {}
        for k, v in pairs:
            if k in answer:
                _stop()
            answer[k] = v
        return answer

    def constant(_: str) -> NoReturn:
        _stop()

    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=constant)
    except (UnicodeError, TypeError, ValueError, RecursionError):
        _stop()
    if not isinstance(obj, dict):
        _stop()
    return cast(dict[str, Any], obj)


def _sealed(z: ZipFile, root: str, filename: str) -> dict[str, Any]:
    try:
        data = z.read(root + filename)
        receipt = z.read(root + filename + ".sha256").decode("ascii").strip()
    except (KeyError, OSError, ValueError, UnicodeError, RuntimeError, BadZipFile, zlib.error):
        _stop()
    if _sha(data) != _sha_check(receipt) or len(data) > MAX_ENTRY:
        _stop()
    return _json(data)


def _positive_items(doc: dict[str, Any]) -> dict[str, tuple[str, set[str]]]:
    items = doc.get("items")
    if not isinstance(items, list) or len(items) > 500:
        _stop()
    result: dict[str, tuple[str, set[str]]] = {}
    for item in items:
        if not isinstance(item, dict):
            _stop()
        aid = item.get("fmpArticleId")
        text = item.get("textSha256")
        ticker_values = item.get("tickers")
        if (
            not isinstance(aid, str) or not aid.strip() or len(aid) > 120
            or aid in result
            or not isinstance(ticker_values, list)
            or not 1 <= len(ticker_values) <= 12
            or any(
                not isinstance(t, str) or not t.strip() or t.strip() != t
                or len(t) > 24
                for t in ticker_values
            )
            or len(set(ticker_values)) != len(ticker_values)
        ):
            _stop()
        result[aid] = (_sha_check(text), set(ticker_values))
    return result


def _read_one(folder: Path, entry: dict[str, Any]) -> dict[str, Any]:
    run_id = entry.get("run_id")
    artifact_id = entry.get("artifact_id")
    asof = entry.get("asof")
    created = entry.get("artifact_created_at_utc")
    if (
        type(run_id) is not int or run_id <= 0 or type(artifact_id) is not int
        or artifact_id <= 0 or not isinstance(asof, str)
        or not isinstance(created, str) or not created.endswith("Z")
    ):
        _stop()
    try:
        date.fromisoformat(asof)
        datetime.fromisoformat(created.replace("Z", "+00:00"))
    except ValueError:
        _stop()
    path = folder / f"{artifact_id}.zip"
    try:
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_ZIP:
            _stop()
        raw = path.read_bytes()
        if _sha(raw) != _sha_check(entry.get("zip_sha256")):
            _stop()
        with ZipFile(path) as z:
            names = z.namelist()
            if (
                len(names) != len(set(names)) or len(names) > 100
                or any("\\" in name or name.startswith("/") or ".." in name.split("/") for name in names)
                or sum(i.file_size for i in z.infolist()) > MAX_TOTAL
                or any(i.file_size > MAX_ENTRY for i in z.infolist())
            ):
                _stop()
            roots = [
                root for root in ROOTS
                if root + "daily_news_freeze_manifest_v1.json" in names
            ]
            if len(roots) != 1:
                _stop()
            root = roots[0]
            if any(name.startswith(other) for name in names for other in ROOTS if other != root):
                _stop()
            freeze = _sealed(z, root, "daily_news_freeze_manifest_v1.json")
            family = _sha_check(entry.get("family_sha256"))
            news_sha = _sha_check(entry.get("source_news_sha256"))
            if (
                freeze.get("asOf") != asof or freeze.get("schemaVersion") != "1.0"
                or freeze.get("familyManifestSha256") != family
                or freeze.get("sourceNewsSha256") != news_sha
            ):
                _stop()
            pairs: dict[int, dict[str, tuple[str, set[str]]]] = {}
            for days in (2, 5):
                body = _sealed(z, root, f"daily_news_candidates_{days}d_v1.json")
                snapshot = _positive_items(body)
                if (
                    body.get("asOfDate") != asof
                    or body.get("schemaVersion") != "1.0"
                    or body.get("provider") != "financial-modeling-prep"
                    or body.get("windowDays") != days
                    or body.get("familyManifestSha256") != family
                    or body.get("sourceNewsSha256") != news_sha
                    or freeze.get(f"candidate{days}dCount") != len(snapshot)
                ):
                    _stop()
                # Verify the digest declared in the frozen manifest, not only its sidecar.
                raw_candidate = z.read(root + f"daily_news_candidates_{days}d_v1.json")
                if _sha(raw_candidate) != _sha_check(freeze.get(f"candidate{days}dSha256")):
                    _stop()
                pairs[days] = snapshot
    except (OSError, ValueError, BadZipFile, EOFError, RuntimeError, zlib.error):
        _stop()
    return {
        "asof": asof, "run_id": run_id, "artifact_id": artifact_id,
        "artifact_created_at_utc": created,
        "family_sha256": family,
        "zip_sha256": entry["zip_sha256"],
        "source_news_sha256": news_sha,
        "candidate2dCount": len(pairs[2]),
        "candidate5dCount": len(pairs[5]),
        "_private_pairs": pairs,
    }


def census_aggregate_only(manifest: dict[str, Any], archive_dir: Path) -> dict[str, Any]:
    if (
        manifest.get("schema_version") != "dtrm.phase4.archived_source_manifest.v0"
        or manifest.get("dataset_role") != "exploratory_aggregate_source_manifest"
        or manifest.get("repository") != "tech-com-UA00001/theresistance-back"
        or manifest.get("workflow") != "DTRM daily ranking"
    ):
        _stop()
    archives = manifest.get("archives")
    if not isinstance(archives, list) or not 1 <= len(archives) <= 100:
        _stop()
    rows = [_read_one(archive_dir, row) if isinstance(row, dict) else _stop() for row in archives]
    rows.sort(key=lambda row: row["asof"])
    if len({row["asof"] for row in rows}) != len(rows):
        _stop()
    if len({row["artifact_id"] for row in rows}) != len(rows):
        _stop()
    family_counts = Counter(row["family_sha256"] for row in rows)
    distinct: dict[int, set[tuple[str, str, str]]] = {2: set(), 5: set()}
    for row in rows:
        for days in (2, 5):
            for aid, (text_sha, tickers) in row["_private_pairs"][days].items():
                distinct[days].update((aid, text_sha, ticker) for ticker in tickers)
    adjacent: list[dict[str, object]] = []
    for old, new in zip(rows, rows[1:]):
        same_family = old["family_sha256"] == new["family_sha256"]
        result: dict[str, object] = {
            "from_asof": old["asof"], "to_asof": new["asof"],
            "same_family": same_family,
        }
        for days in (2, 5):
            a = old["_private_pairs"][days]
            b = new["_private_pairs"][days]
            same = [
                key for key in (a.keys() & b.keys())
                if a[key][0] == b[key][0]
            ]
            result[f"{days}d_stable_links"] = sum(
                len(a[key][1] & b[key][1]) for key in same
            )
            result[f"{days}d_changed_link_sets"] = sum(
                a[key][1] != b[key][1] for key in same
            )
        adjacent.append(result)
    def summed(days: int) -> int:
        return sum(
            cast(int, row[f"{days}d_stable_links"])
            for row in adjacent if row["same_family"]
        )
    return {
        "schema_version": "dtrm.phase4.archived_time_state_inventory_reproduction.v0",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "data_scope": "exploratory_positive_selected_archives",
        "snapshot_metadata_independently_authenticated": False,
        "historical_first_seen_authenticated": False,
        "absence_authenticated": False,
        "source_completeness_authenticated": False,
        "model_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "scientific_counting_permitted": False,
        "snapshot_count": len(rows),
        "family_groups": [
            {"family_sha256": f, "snapshots": n}
            for f, n in sorted(family_counts.items())
        ],
        "asof_first": rows[0]["asof"],
        "asof_last": rows[-1]["asof"],
        "5d_capped_count": sum(row["candidate5dCount"] == 500 for row in rows),
        "2d_capped_count": sum(row["candidate2dCount"] == 500 for row in rows),
        "unique_selected_positive_triples_2d": len(distinct[2]),
        "unique_selected_positive_triples_5d": len(distinct[5]),
        "unique_selected_positive_triples_union": len(distinct[2] | distinct[5]),
        "same_family_adjacent_count": sum(row["same_family"] for row in adjacent),
        "same_family_sum_repeated_links_2d": summed(2),
        "same_family_sum_repeated_links_5d": summed(5),
        "adjacent": adjacent,
    }


def verify_canonical_source_manifest(raw: bytes) -> None:
    """Git-blob-pin every historical source identity before any private ZIP I/O."""
    if len(raw) > 256_000:
        _stop()
    # Git object header terminates with a NUL byte, not the characters backslash-zero.
    header = b"blob " + str(len(raw)).encode("ascii") + b"\\x00"
    if hashlib.sha1(header + raw).hexdigest() != CANONICAL_SOURCE_MANIFEST_GIT_BLOB_SHA1:
        _stop()
    doc = _json(raw)
    if not isinstance(doc.get("archives"), list) or len(doc["archives"]) != 21:
        _stop()


def verify_canonical_aggregate(report: dict[str, Any]) -> None:
    """Only the canonical 21-capture aggregate may be called reproduced."""
    required = {
        "snapshot_count": 21,
        "asof_first": "2026-09-15",
        "asof_last": "2026-10-13",
        "2d_capped_count": 13,
        "5d_capped_count": 21,
        "same_family_adjacent_count": 18,
        "unique_selected_positive_triples_union": 36440,
        "same_family_sum_repeated_links_2d": 22348,
        "same_family_sum_repeated_links_5d": 26396,
    }
    if any(report.get(key) != val for key, val in required.items()):
        _stop()
    family_groups = report.get("family_groups")
    if (
        not isinstance(family_groups, list) or len(family_groups) != 3
        or sorted(row.get("snapshots") for row in family_groups if isinstance(row, dict))
        != [4, 8, 9]
    ):
        _stop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        if args.manifest.is_symlink() or not args.manifest.is_file():
            _stop()
        data = args.manifest.read_bytes()
        verify_canonical_source_manifest(data)
        manifest = _json(data)
        report = census_aggregate_only(manifest, args.archive_dir)
        verify_canonical_aggregate(report)
        report["reproduction_status"] = "PASS_CANONICAL_21_SOURCE_AGGREGATE_REPRODUCED"
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0
    except (ArchiveCensusError, OSError, ValueError, BadZipFile, EOFError, zlib.error):
        print('{"error_code":"REPRODUCTION_NOT_CONFIRMED","status":"failed"}')
        return 1


if __name__ == "__main__":
    sys.exit(main())
