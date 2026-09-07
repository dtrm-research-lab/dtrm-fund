"""Immutable news-vintage ontology, specified before implementation."""

import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Literal, cast

SCHEMA_VERSION = "dtrm.phase4.event_batch.v0"
DatasetRole = Literal["synthetic", "unaudited"]
Precision = Literal["instant", "day", "unknown"]


class OntologyError(ValueError):
    """The supplied batch violates an explicit ontology invariant."""


def _object(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise OntologyError(f"{label}: expected exactly {sorted(fields)}")
    return cast(dict[str, object], value)


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise OntologyError(f"{label}: expected nonempty trimmed string")
    return value


def _optional_text(value: object, label: str) -> str | None:
    return None if value is None else _text(value, label)


def _instant(value: object, label: str) -> datetime | None:
    if value is None:
        return None
    text = _text(value, label)
    try:
        if "T" not in text:
            raise ValueError("instant requires a time")
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("instant requires timezone")
    except ValueError as exc:
        raise OntologyError(f"{label}: expected timezone-aware ISO instant") from exc
    return parsed.astimezone(timezone.utc)


def timestamp(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat().replace("+00:00", "Z")


def _publication(value: object, precision: object) -> tuple[str | None, Precision]:
    if precision == "unknown" and value is None:
        return None, "unknown"
    if precision == "instant" and value is not None:
        return timestamp(_instant(value, "published_at")), "instant"
    if precision == "day":
        text = _text(value, "published_at")
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                raise ValueError("calendar date required")
            return date.fromisoformat(text).isoformat(), "day"
        except ValueError as exc:
            raise OntologyError("published_at: invalid calendar date") from exc
    raise OntologyError("published_at and publication_precision are inconsistent")


@dataclass(frozen=True, slots=True)
class AssetLink:
    ticker: str
    mapping_version: str
    linked_at: datetime | None

    def to_dict(self) -> dict[str, object]:
        return {"ticker": self.ticker, "mapping_version": self.mapping_version,
                "linked_at": timestamp(self.linked_at)}


@dataclass(frozen=True, slots=True)
class EventObservation:
    source: str
    source_event_id: str
    version_id: str
    content_sha256: str
    published_at: str | None
    publication_precision: Precision
    occurred_at: datetime | None
    first_seen_at: datetime | None
    version_observed_at: datetime | None
    supersedes_version_id: str | None
    asset_links: tuple[AssetLink, ...]

    @property
    def identity(self) -> tuple[str, str, str]:
        return self.source, self.source_event_id, self.version_id

    def availability(self, link: AssetLink) -> datetime | None:
        if self.version_observed_at is None or link.linked_at is None:
            return None
        return max(self.version_observed_at, link.linked_at)

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source, "source_event_id": self.source_event_id,
            "version_id": self.version_id, "content_sha256": self.content_sha256,
            "published_at": self.published_at,
            "publication_precision": self.publication_precision,
            "occurred_at": timestamp(self.occurred_at),
            "first_seen_at": timestamp(self.first_seen_at),
            "version_observed_at": timestamp(self.version_observed_at),
            "supersedes_version_id": self.supersedes_version_id,
            "asset_links": [link.to_dict() for link in self.asset_links],
        }


@dataclass(frozen=True, slots=True)
class EventBatch:
    dataset_role: DatasetRole
    events: tuple[EventObservation, ...]

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": SCHEMA_VERSION, "dataset_role": self.dataset_role,
                "events": [event.to_dict() for event in self.events]}


def _link(value: object) -> AssetLink:
    item = _object(value, {"ticker", "mapping_version", "linked_at"}, "asset_link")
    ticker = _text(item["ticker"], "ticker")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{0,14}", ticker):
        raise OntologyError("ticker: expected canonical uppercase symbol")
    return AssetLink(ticker, _text(item["mapping_version"], "mapping_version"),
                     _instant(item["linked_at"], "linked_at"))


def _event(value: object) -> EventObservation:
    item = _object(value, {
        "source", "source_event_id", "version_id", "content_sha256", "published_at",
        "publication_precision", "occurred_at", "first_seen_at", "version_observed_at",
        "supersedes_version_id", "asset_links",
    }, "event")
    if item["source"] != "fmp_news":
        raise OntologyError("source: only fmp_news is in the v0 scope")
    digest = _text(item["content_sha256"], "content_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise OntologyError("content_sha256: expected lowercase SHA-256")
    published_at, precision = _publication(item["published_at"], item["publication_precision"])
    first_seen = _instant(item["first_seen_at"], "first_seen_at")
    observed = _instant(item["version_observed_at"], "version_observed_at")
    if first_seen is not None and observed is not None and observed < first_seen:
        raise OntologyError("version observation precedes logical first observation")
    raw_links = item["asset_links"]
    if not isinstance(raw_links, list):
        raise OntologyError("asset_links: expected list")
    links = tuple(sorted((_link(link) for link in raw_links), key=lambda link: link.ticker))
    if len({link.ticker for link in links}) != len(links):
        raise OntologyError("duplicate ticker link within one version")
    return EventObservation(
        "fmp_news", _text(item["source_event_id"], "source_event_id"),
        _text(item["version_id"], "version_id"), digest, published_at, precision,
        _instant(item["occurred_at"], "occurred_at"), first_seen, observed,
        _optional_text(item["supersedes_version_id"], "supersedes_version_id"), links,
    )


def normalize_observations(value: object) -> EventBatch:
    item = _object(value, {"schema_version", "dataset_role", "events"}, "batch")
    if item["schema_version"] != SCHEMA_VERSION:
        raise OntologyError("unsupported batch schema_version")
    role = item["dataset_role"]
    if role not in ("synthetic", "unaudited"):
        raise OntologyError("dataset_role cannot declare scientific approval")
    raw_events = item["events"]
    if not isinstance(raw_events, list) or not raw_events:
        raise OntologyError("events: expected nonempty list")
    events = tuple(sorted((_event(event) for event in raw_events), key=lambda e: e.identity))
    if len({event.identity for event in events}) != len(events):
        raise OntologyError("duplicate version identity")
    return EventBatch(role, events)


def validate_revision_chains(batch: EventBatch) -> EventBatch:
    groups: dict[tuple[str, str], dict[str, EventObservation]] = {}
    for event in batch.events:
        groups.setdefault(event.identity[:2], {})[event.version_id] = event
    for versions in groups.values():
        first_seen = {e.first_seen_at for e in versions.values() if e.first_seen_at is not None}
        if len(first_seen) > 1:
            raise OntologyError("inconsistent logical first_seen_at across versions")
        roots = [e.version_id for e in versions.values() if e.supersedes_version_id is None]
        if len(roots) != 1:
            raise OntologyError("revision chain must have exactly one root")
        successor: dict[str, str] = {}
        for event in versions.values():
            parent_id = event.supersedes_version_id
            if parent_id is None:
                continue
            if parent_id not in versions:
                raise OntologyError("missing predecessor in complete revision batch")
            if parent_id in successor:
                raise OntologyError("forked revision chain")
            parent = versions[parent_id]
            if (parent.version_observed_at is not None
                    and event.version_observed_at is not None
                    and event.version_observed_at < parent.version_observed_at):
                raise OntologyError("revision observation times move backwards")
            successor[parent_id] = event.version_id
        visited: set[str] = set()
        current: str | None = roots[0]
        while current is not None:
            if current in visited:
                raise OntologyError("cyclic revision chain")
            visited.add(current)
            current = successor.get(current)
        if len(visited) != len(versions):
            raise OntologyError("disconnected or cyclic revision chain")
    return batch
