"""Offline, read-only GitHub archival capture-clock metadata attestation.

Only verifies a separately retrieved provider listing against the exact fixed
non-sensitive 21-source manifest. Never authenticates original link first-seen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

MANIFEST_GIT_BLOB_SHA1 = "eb7c91b462ddb822835c20fc126492bfcae5eea0"
BACKEND_REPO = "tech-com-UA00001/theresistance-back"
MANIFEST_SCHEMA = "dtrm.phase4.archived_source_manifest.v0"
FAILURE = "BLOCKED_ARCHIVE_PROVIDER_METADATA_MISMATCH"
_CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_FILE_RE = re.compile(r"^[1-9][0-9]*\.json$")


class ClockAttestationError(ValueError):
    """Fixed, source-free fail-closed error."""


@dataclass(frozen=True)
class ClockReadback:
    status: str
    scientific_status: str
    canonical_manifest_git_blob_sha1: str
    independently_rechecked_capture_clocks: bool
    verified_archives: int
    distinct_runs: int
    earliest_expiry_at_utc: str
    historical_first_seen_authenticated: bool = False
    historical_absence_authenticated: bool = False
    source_completeness_authenticated: bool = False
    price_clock_authenticated: bool = False
    model_fitting_permitted: bool = False
    outcomes_access_permitted: bool = False
    mm1_execution_permitted: bool = False
    scientific_counting_permitted: bool = False


def _reject() -> None:
    raise ClockAttestationError(FAILURE)


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        _reject()
    return value


def _integer(value: object) -> int:
    if type(value) is not int or value <= 0:
        _reject()
    return value


def _utc(value: object) -> datetime:
    if not isinstance(value, str) or not _CLOCK_RE.fullmatch(value):
        _reject()
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        _reject()
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _reject()
    return parsed.replace(tzinfo=timezone.utc)


def _git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


def verify_provider_clock(
    manifest_raw: bytes,
    pages: Mapping[int, object],
    inspected_at_utc: str,
) -> ClockReadback:
    """Pure exact-identity comparison; no I/O and no mutable caller output."""
    checked = _utc(inspected_at_utc)
    if _git_blob_sha1(manifest_raw) != MANIFEST_GIT_BLOB_SHA1:
        _reject()
    try:
        manifest = _object(json.loads(manifest_raw))
    except (ValueError, UnicodeError, TypeError):
        _reject()
    if (
        manifest.get("schema_version") != MANIFEST_SCHEMA
        or manifest.get("repository") != BACKEND_REPO
        or manifest.get("source_completeness_authenticated") is not False
        or manifest.get("model_fitting_permitted") is not False
    ):
        _reject()
    archives = manifest.get("archives")
    if not isinstance(archives, list) or len(archives) != 21:
        _reject()

    entries: dict[int, dict[str, object]] = {}
    artifact_ids: set[int] = set()
    for item in archives:
        row = _object(item)
        run = _integer(row.get("run_id"))
        artifact_id = _integer(row.get("artifact_id"))
        if run in entries or artifact_id in artifact_ids:
            _reject()
        if not isinstance(row.get("asof"), str):
            _reject()
        _utc(row.get("artifact_created_at_utc"))
        entries[run] = row
        artifact_ids.add(artifact_id)
    if set(pages.keys()) != set(entries.keys()):
        _reject()

    expiries: list[datetime] = []
    for run, row in sorted(entries.items()):
        body = _object(pages[run])
        total = body.get("total_count")
        artifacts = body.get("artifacts")
        if type(total) is not int or not isinstance(artifacts, list) or total != len(artifacts):
            _reject()
        exact = [a for a in artifacts if isinstance(a, dict) and a.get("id") == row["artifact_id"]]
        if len(exact) != 1:
            _reject()
        artifact = _object(exact[0])
        source_run = _object(artifact.get("workflow_run"))
        if (
            artifact.get("id") != row["artifact_id"]
            or artifact.get("name") != f"daily-ranking-{run}"
            or source_run.get("id") != run
            or artifact.get("created_at") != row["artifact_created_at_utc"]
            or artifact.get("expired") is not False
        ):
            _reject()
        created = _utc(artifact.get("created_at"))
        expiry = _utc(artifact.get("expires_at"))
        if expiry <= checked or expiry <= created:
            _reject()
        expiries.append(expiry)

    return ClockReadback(
        status="PASS_PROVIDER_METADATA_MATCH",
        scientific_status="BLOCKED_SOURCE_AUDIT",
        canonical_manifest_git_blob_sha1=MANIFEST_GIT_BLOB_SHA1,
        independently_rechecked_capture_clocks=True,
        verified_archives=len(archives),
        distinct_runs=len(entries),
        earliest_expiry_at_utc=min(expiries).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _read_limited(path: Path) -> bytes:
    if not path.is_file() or path.stat().st_size > 1_000_000:
        _reject()
    return path.read_bytes()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline provider metadata clock check")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pages-dir", type=Path, required=True)
    parser.add_argument("--inspected-at-utc", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or not args.pages_dir.is_dir():
            _reject()
        manifest_raw = _read_limited(args.manifest)
        filenames = sorted(args.pages_dir.glob("*.json"))
        if len(filenames) != 21 or not all(_FILE_RE.fullmatch(p.name) for p in filenames):
            _reject()
        pages: dict[int, object] = {}
        for path in filenames:
            pages[int(path.stem)] = json.loads(_read_limited(path))
        result = verify_provider_clock(manifest_raw, pages, args.inspected_at_utc)
        report = json.dumps(asdict(result), sort_keys=True, indent=2) + "\n"
        with args.output.open("x", encoding="utf-8") as target:
            target.write(report)
        print(result.status)
        return 0
    except (ClockAttestationError, OSError, UnicodeError, ValueError, TypeError):
        print(FAILURE, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
