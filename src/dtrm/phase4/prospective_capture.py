"""Pure conformance graph for the registered prospective capture protocol."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, cast

GRAPH = "phase4_prospective_capture_protocol_v0"
BUNDLE_SCHEMA = "dtrm.phase4.prospective_capture_bundle.v0"
REPORT_SCHEMA = "dtrm.phase4.prospective_capture_review.v0"
PROTOCOL_PATH = "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAPTURE_PROTOCOL_V0.md"
PROTOCOL_SHA256 = "a343f076a9713b5e1b037cf83ecc864d9bc4308a9592bef0dabeafa00617e629"
BINDING_PATH = (
    "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAPTURE_SYNTHETIC_BINDING_V0.md"
)
BINDING_SHA256 = "0ec92acb50d3011063db595e6bc026b99bd9847f8d6e4dcc080ab5266ea65e31"
PROTOCOL_REGISTRATION_COMMIT = "85c02cca5a477b6c68b43dbac35d517e58f66518"
SYNTHETIC_BINDING_COMMIT = "d058b02fcf2e28c4987954876433b6efa695ab06"
NODES = (
    "normalize_envelope",
    "reconcile_counters",
    "validate_versions",
    "validate_links",
    "validate_ledger",
    "serialize_audit",
)

IdentityMethod = Literal["provider_id", "exact_url_sha256"]


class ProspectiveCaptureError(ValueError):
    """The synthetic bundle violates a registered protocol invariant."""


def _object(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ProspectiveCaptureError(f"{label}: unexpected keys")
    return cast(dict[str, object], value)


def _text(value: object, label: str, *, maximum: int = 512) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
    ):
        raise ProspectiveCaptureError(f"{label}: invalid text")
    return value


def _sha(value: object, label: str) -> str:
    text = _text(value, label, maximum=64)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ProspectiveCaptureError(f"{label}: invalid SHA-256")
    return text


def _optional_sha(value: object, label: str) -> str | None:
    return None if value is None else _sha(value, label)


def _instant(value: object, label: str) -> datetime:
    text = _text(value, label, maximum=40)
    try:
        if "T" not in text:
            raise ValueError("time required")
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timezone required")
    except ValueError as exc:
        raise ProspectiveCaptureError(f"{label}: invalid UTC instant") from exc
    return parsed.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _count(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProspectiveCaptureError(f"{label}: invalid count")
    return value


@dataclass(frozen=True, slots=True)
class CollectorIdentity:
    collector_id: str
    repository: str
    commit: str
    source: str
    mapping_version: str
    clock_policy: str

    def to_dict(self) -> dict[str, object]:
        return {
            "collector_id": self.collector_id,
            "repository": self.repository,
            "commit": self.commit,
            "source": self.source,
            "mapping_version": self.mapping_version,
            "clock_policy": self.clock_policy,
        }


@dataclass(frozen=True, slots=True)
class CaptureRun:
    run_id: str
    started_at: datetime
    response_received_at: datetime
    completed_at: datetime
    request_fingerprint_sha256: str
    observed_candidates: int
    new_versions: int
    repeat_sightings: int
    rejected_candidates: int

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "started_at": _timestamp(self.started_at),
            "response_received_at": _timestamp(self.response_received_at),
            "completed_at": _timestamp(self.completed_at),
            "request_fingerprint_sha256": self.request_fingerprint_sha256,
            "observed_candidates": self.observed_candidates,
            "new_versions": self.new_versions,
            "repeat_sightings": self.repeat_sightings,
            "rejected_candidates": self.rejected_candidates,
        }


@dataclass(frozen=True, slots=True)
class CaptureLink:
    ticker: str
    mapping_version: str
    linked_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "ticker": self.ticker,
            "mapping_version": self.mapping_version,
            "linked_at": _timestamp(self.linked_at),
        }


@dataclass(frozen=True, slots=True)
class CaptureRecord:
    sequence_no: int
    run_id: str
    source_event_id: str
    identity_method: IdentityMethod
    version_id: str
    supersedes_version_id: str | None
    payload_sha256: str
    content_sha256: str
    version_observed_at: datetime
    first_seen_at: datetime
    asset_links: tuple[CaptureLink, ...]
    previous_record_sha256: str | None
    record_sha256: str

    def hash_input_dict(self) -> dict[str, object]:
        result = self.to_dict()
        del result["record_sha256"]
        return result

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence_no": self.sequence_no,
            "run_id": self.run_id,
            "source_event_id": self.source_event_id,
            "identity_method": self.identity_method,
            "version_id": self.version_id,
            "supersedes_version_id": self.supersedes_version_id,
            "payload_sha256": self.payload_sha256,
            "content_sha256": self.content_sha256,
            "version_observed_at": _timestamp(self.version_observed_at),
            "first_seen_at": _timestamp(self.first_seen_at),
            "asset_links": [link.to_dict() for link in self.asset_links],
            "previous_record_sha256": self.previous_record_sha256,
            "record_sha256": self.record_sha256,
        }


@dataclass(frozen=True, slots=True)
class CaptureBundle:
    collector: CollectorIdentity
    previous_ledger_head_sha256: str | None
    run: CaptureRun
    records: tuple[CaptureRecord, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": BUNDLE_SCHEMA,
            "dataset_role": "synthetic",
            "collector": self.collector.to_dict(),
            "previous_ledger_head_sha256": self.previous_ledger_head_sha256,
            "run": self.run.to_dict(),
            "records": [record.to_dict() for record in self.records],
        }


@dataclass(frozen=True, slots=True)
class CaptureAssessment:
    collector: CollectorIdentity
    run: CaptureRun
    canonical_bundle_sha256: str
    record_count: int
    logical_event_count: int
    asset_link_count: int
    input_ledger_head_sha256: str | None
    output_ledger_head_sha256: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "registered_protocol": {
                "path": PROTOCOL_PATH,
                "sha256": PROTOCOL_SHA256,
                "registration_commit": PROTOCOL_REGISTRATION_COMMIT,
            },
            "registered_synthetic_binding": {
                "path": BINDING_PATH,
                "sha256": BINDING_SHA256,
                "registration_commit": SYNTHETIC_BINDING_COMMIT,
                "prior_version_state": "empty_tuple",
            },
            "completed_nodes": list(NODES),
            "dataset_role": "synthetic",
            "collector": self.collector.to_dict(),
            "run": self.run.to_dict(),
            "canonical_bundle_sha256": self.canonical_bundle_sha256,
            "counts": {
                "record_count": self.record_count,
                "logical_event_count": self.logical_event_count,
                "asset_link_count": self.asset_link_count,
            },
            "input_ledger_head_sha256": self.input_ledger_head_sha256,
            "output_ledger_head_sha256": self.output_ledger_head_sha256,
            "engineering_status": "PASS_SYNTHETIC_PROSPECTIVE_CAPTURE_PROTOCOL",
            "scientific_status": "BLOCKED_PROSPECTIVE_DEPLOYMENT",
            "source_authenticated": False,
            "collector_deployed": False,
            "clock_authenticated": False,
            "coverage_authenticated": False,
            "history_construction_permitted": False,
            "training_permitted": False,
            "outcome_access_permitted": False,
            "model_fitting_performed": False,
        }


def _collector(value: object) -> CollectorIdentity:
    item = _object(
        value,
        {
            "collector_id",
            "repository",
            "commit",
            "source",
            "mapping_version",
            "clock_policy",
        },
        "collector",
    )
    collector_id = _text(item["collector_id"], "collector_id", maximum=64)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", collector_id):
        raise ProspectiveCaptureError("collector_id: invalid identifier")
    repository = _text(item["repository"], "repository", maximum=160)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ProspectiveCaptureError("repository: invalid slug")
    commit = _text(item["commit"], "commit", maximum=40)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ProspectiveCaptureError("commit: invalid Git identity")
    if item["source"] != "fmp_news":
        raise ProspectiveCaptureError("source: unsupported")
    if item["clock_policy"] != "utc_runner_bracket_v0":
        raise ProspectiveCaptureError("clock_policy: unsupported")
    return CollectorIdentity(
        collector_id,
        repository,
        commit,
        "fmp_news",
        _sha(item["mapping_version"], "mapping_version"),
        "utc_runner_bracket_v0",
    )


def _run(value: object) -> CaptureRun:
    item = _object(
        value,
        {
            "run_id",
            "started_at",
            "response_received_at",
            "completed_at",
            "request_fingerprint_sha256",
            "observed_candidates",
            "new_versions",
            "repeat_sightings",
            "rejected_candidates",
        },
        "run",
    )
    run_id = _text(item["run_id"], "run_id", maximum=36)
    try:
        if str(uuid.UUID(run_id)) != run_id:
            raise ValueError("noncanonical UUID")
    except ValueError as exc:
        raise ProspectiveCaptureError("run_id: invalid UUID") from exc
    started = _instant(item["started_at"], "started_at")
    received = _instant(item["response_received_at"], "response_received_at")
    completed = _instant(item["completed_at"], "completed_at")
    if not started <= received <= completed:
        raise ProspectiveCaptureError("run: clock order violation")
    return CaptureRun(
        run_id,
        started,
        received,
        completed,
        _sha(item["request_fingerprint_sha256"], "request_fingerprint_sha256"),
        _count(item["observed_candidates"], "observed_candidates"),
        _count(item["new_versions"], "new_versions"),
        _count(item["repeat_sightings"], "repeat_sightings"),
        _count(item["rejected_candidates"], "rejected_candidates"),
    )


def _link(value: object) -> CaptureLink:
    item = _object(value, {"ticker", "mapping_version", "linked_at"}, "asset_link")
    ticker = _text(item["ticker"], "ticker", maximum=15)
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{0,14}", ticker):
        raise ProspectiveCaptureError("ticker: invalid canonical symbol")
    return CaptureLink(
        ticker,
        _sha(item["mapping_version"], "link mapping_version"),
        _instant(item["linked_at"], "linked_at"),
    )


def _record(value: object) -> CaptureRecord:
    item = _object(
        value,
        {
            "sequence_no",
            "run_id",
            "source_event_id",
            "identity_method",
            "version_id",
            "supersedes_version_id",
            "payload_sha256",
            "content_sha256",
            "version_observed_at",
            "first_seen_at",
            "asset_links",
            "previous_record_sha256",
            "record_sha256",
        },
        "record",
    )
    sequence = _count(item["sequence_no"], "sequence_no")
    if sequence == 0:
        raise ProspectiveCaptureError("sequence_no: must start at one")
    method = item["identity_method"]
    if method not in ("provider_id", "exact_url_sha256"):
        raise ProspectiveCaptureError("identity_method: unsupported")
    source_event_id = _text(item["source_event_id"], "source_event_id")
    if method == "exact_url_sha256" and not re.fullmatch(
        r"[0-9a-f]{64}", source_event_id
    ):
        raise ProspectiveCaptureError("source_event_id: URL identity must be SHA-256")
    raw_links = item["asset_links"]
    if not isinstance(raw_links, list):
        raise ProspectiveCaptureError("asset_links: expected list")
    links = tuple(sorted((_link(link) for link in raw_links), key=lambda link: link.ticker))
    if len({link.ticker for link in links}) != len(links):
        raise ProspectiveCaptureError("asset_links: duplicate ticker")
    return CaptureRecord(
        sequence,
        _text(item["run_id"], "record run_id", maximum=36),
        source_event_id,
        method,
        _sha(item["version_id"], "version_id"),
        _optional_sha(item["supersedes_version_id"], "supersedes_version_id"),
        _sha(item["payload_sha256"], "payload_sha256"),
        _sha(item["content_sha256"], "content_sha256"),
        _instant(item["version_observed_at"], "version_observed_at"),
        _instant(item["first_seen_at"], "first_seen_at"),
        links,
        _optional_sha(item["previous_record_sha256"], "previous_record_sha256"),
        _sha(item["record_sha256"], "record_sha256"),
    )


def normalize_capture_bundle(value: object) -> CaptureBundle:
    item = _object(
        value,
        {
            "schema_version",
            "dataset_role",
            "collector",
            "previous_ledger_head_sha256",
            "run",
            "records",
        },
        "bundle",
    )
    if item["schema_version"] != BUNDLE_SCHEMA:
        raise ProspectiveCaptureError("bundle: unsupported schema")
    if item["dataset_role"] != "synthetic":
        raise ProspectiveCaptureError("bundle: synthetic role required")
    raw_records = item["records"]
    if not isinstance(raw_records, list):
        raise ProspectiveCaptureError("records: expected list")
    records = tuple(sorted((_record(record) for record in raw_records), key=lambda r: r.sequence_no))
    return CaptureBundle(
        _collector(item["collector"]),
        _optional_sha(item["previous_ledger_head_sha256"], "previous ledger head"),
        _run(item["run"]),
        records,
    )


def reconcile_counters(bundle: CaptureBundle) -> None:
    run = bundle.run
    if run.observed_candidates != (
        run.new_versions + run.repeat_sightings + run.rejected_candidates
    ):
        raise ProspectiveCaptureError("run: candidate counters do not reconcile")
    if run.new_versions != len(bundle.records):
        raise ProspectiveCaptureError("run: new_versions does not match records")


def expected_version_id(source_event_id: str, content_sha256: str) -> str:
    value = f"fmp_news\0{source_event_id}\0{content_sha256}".encode()
    return hashlib.sha256(value).hexdigest()


def validate_versions(bundle: CaptureBundle) -> None:
    if len({record.version_id for record in bundle.records}) != len(bundle.records):
        raise ProspectiveCaptureError("records: duplicate version identity")
    groups: dict[str, list[CaptureRecord]] = {}
    for record in bundle.records:
        if record.run_id != bundle.run.run_id:
            raise ProspectiveCaptureError("record: run identity mismatch")
        if record.version_observed_at != bundle.run.response_received_at:
            raise ProspectiveCaptureError("record: observation clock mismatch")
        if record.version_id != expected_version_id(
            record.source_event_id, record.content_sha256
        ):
            raise ProspectiveCaptureError("record: derived version identity mismatch")
        groups.setdefault(record.source_event_id, []).append(record)

    for versions in groups.values():
        if len({record.identity_method for record in versions}) != 1:
            raise ProspectiveCaptureError("revision chain: identity method changed")
        by_id = {record.version_id: record for record in versions}
        roots = [record for record in versions if record.supersedes_version_id is None]
        if len(roots) != 1:
            raise ProspectiveCaptureError("revision chain: exactly one root required")
        root = roots[0]
        if any(record.first_seen_at != root.version_observed_at for record in versions):
            raise ProspectiveCaptureError("revision chain: inconsistent first_seen_at")
        successors: dict[str, str] = {}
        for record in versions:
            predecessor = record.supersedes_version_id
            if predecessor is None:
                continue
            if predecessor not in by_id:
                raise ProspectiveCaptureError("revision chain: external predecessor forbidden")
            if predecessor in successors:
                raise ProspectiveCaptureError("revision chain: fork")
            successors[predecessor] = record.version_id
        visited: set[str] = set()
        current: CaptureRecord | None = root
        prior_time: datetime | None = None
        while current is not None:
            if current.version_id in visited:
                raise ProspectiveCaptureError("revision chain: cycle")
            if prior_time is not None and current.version_observed_at < prior_time:
                raise ProspectiveCaptureError("revision chain: time moved backwards")
            visited.add(current.version_id)
            prior_time = current.version_observed_at
            successor = successors.get(current.version_id)
            current = None if successor is None else by_id[successor]
        if len(visited) != len(versions):
            raise ProspectiveCaptureError("revision chain: disconnected")


def validate_links(bundle: CaptureBundle) -> None:
    for record in bundle.records:
        for link in record.asset_links:
            if link.mapping_version != bundle.collector.mapping_version:
                raise ProspectiveCaptureError("asset_link: mapping identity mismatch")
            if not record.version_observed_at <= link.linked_at <= bundle.run.completed_at:
                raise ProspectiveCaptureError("asset_link: clock outside admitted range")


def _canonical_compact(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def expected_record_sha256(record: CaptureRecord) -> str:
    return hashlib.sha256(_canonical_compact(record.hash_input_dict())).hexdigest()


def validate_ledger(bundle: CaptureBundle) -> str | None:
    previous = bundle.previous_ledger_head_sha256
    for expected_sequence, record in enumerate(bundle.records, start=1):
        if record.sequence_no != expected_sequence:
            raise ProspectiveCaptureError("ledger: nonconsecutive sequence")
        if record.previous_record_sha256 != previous:
            raise ProspectiveCaptureError("ledger: previous head mismatch")
        if record.record_sha256 != expected_record_sha256(record):
            raise ProspectiveCaptureError("ledger: record hash mismatch")
        previous = record.record_sha256
    return previous


def assess_capture_bundle(bundle: CaptureBundle) -> CaptureAssessment:
    reconcile_counters(bundle)
    validate_versions(bundle)
    validate_links(bundle)
    output_head = validate_ledger(bundle)
    canonical = _canonical_compact(bundle.to_dict())
    return CaptureAssessment(
        bundle.collector,
        bundle.run,
        hashlib.sha256(canonical).hexdigest(),
        len(bundle.records),
        len({record.source_event_id for record in bundle.records}),
        sum(len(record.asset_links) for record in bundle.records),
        bundle.previous_ledger_head_sha256,
        output_head,
    )


def run_prospective_capture_review(value: object) -> CaptureAssessment:
    bundle = normalize_capture_bundle(value)
    return assess_capture_bundle(bundle)


def serialize_capture_review(review: CaptureAssessment) -> str:
    return json.dumps(
        review.to_dict(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
