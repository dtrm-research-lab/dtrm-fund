"""Deterministic ontology review graph; no external I/O or scientific promotion."""

import hashlib
import json
from dataclasses import dataclass

from dtrm.phase4.events import (
    DatasetRole,
    EventBatch,
    OntologyError,
    normalize_observations,
    timestamp,
    validate_revision_chains,
)

GRAPH_ID = "phase4_event_ontology_v0"
NODES = ("normalize_observations", "validate_revision_chains", "assess_metadata_completeness")


class GraphFailure(OntologyError):
    def __init__(self, node: str, cause: OntologyError) -> None:
        self.node = node
        super().__init__(str(cause))


@dataclass(frozen=True, slots=True)
class LinkAvailability:
    source: str
    source_event_id: str
    version_id: str
    ticker: str
    available_at: str | None

    def to_dict(self) -> dict[str, object]:
        return {"source": self.source, "source_event_id": self.source_event_id,
                "version_id": self.version_id, "ticker": self.ticker,
                "available_at": self.available_at}


@dataclass(frozen=True, slots=True)
class OntologyReview:
    dataset_role: DatasetRole
    canonical_batch_sha256: str
    version_count: int
    logical_event_count: int
    links: tuple[LinkAvailability, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "dtrm.phase4.ontology_review.v0", "graph": GRAPH_ID,
            "completed_nodes": list(NODES), "dataset_role": self.dataset_role,
            "engineering_status": "PASS_ONTOLOGY_SCHEMA",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "training_permitted": False, "outcome_access_permitted": False,
            "canonical_batch_sha256": self.canonical_batch_sha256,
            "version_count": self.version_count, "logical_event_count": self.logical_event_count,
            "asset_link_count": len(self.links),
            "unknown_availability_count": sum(link.available_at is None for link in self.links),
            "links": [link.to_dict() for link in self.links],
        }


def assess_metadata_completeness(batch: EventBatch) -> OntologyReview:
    canonical = json.dumps(batch.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    links = tuple(
        LinkAvailability(*event.identity, link.ticker, timestamp(event.availability(link)))
        for event in batch.events for link in event.asset_links
    )
    return OntologyReview(
        batch.dataset_role, hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        len(batch.events), len({event.identity[:2] for event in batch.events}), links,
    )


def run_ontology_review(payload: object) -> OntologyReview:
    try:
        batch = normalize_observations(payload)
    except OntologyError as exc:
        raise GraphFailure(NODES[0], exc) from exc
    try:
        batch = validate_revision_chains(batch)
    except OntologyError as exc:
        raise GraphFailure(NODES[1], exc) from exc
    return assess_metadata_completeness(batch)
