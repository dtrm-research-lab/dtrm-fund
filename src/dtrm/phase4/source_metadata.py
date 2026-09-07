"""Pure, bounded metadata inventory; never authenticates temporal provenance."""

import hashlib
import json
from dataclasses import dataclass
from typing import Literal, cast

DATABASE = "trumpMinMax"
COLLECTION = "trumpNews"
SAMPLE_LIMIT = 1000
FIELDS = (
    "_id", "date", "matched_tickers", "published_at", "publishedDate",
    "first_seen_at", "firstSeenAt", "version_observed_at", "observed_at",
    "ingested_at", "fetched_at", "created_at", "updated_at", "version_id",
    "supersedes_version_id", "content_sha256", "linked_at", "mapping_version", "asset_links",
)
BSON_TYPES = frozenset({
    "double", "string", "object", "array", "binData", "undefined", "objectId",
    "bool", "date", "null", "regex", "dbPointer", "javascript", "symbol",
    "javascriptWithScope", "int", "timestamp", "long", "decimal", "minKey", "maxKey", "missing",
})
ExecutionMode = Literal["synthetic", "live_mongo"]


class MetadataError(ValueError):
    """Aggregate counters violate the registered boundary."""


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_metadata_pipeline() -> list[dict[str, object]]:
    projection: dict[str, object] = {"_id": 0}
    facets: dict[str, object] = {"sample": [{"$count": "n"}]}
    for index, field in enumerate(FIELDS):
        key = f"f{index}"
        projection[key] = {"$type": f"${field}"}
        facets[key] = [{"$group": {"_id": f"${key}", "n": {"$sum": 1}}}]
    return [{"$sort": {"_id": 1}}, {"$limit": SAMPLE_LIMIT},
            {"$project": projection}, {"$facet": facets}]


@dataclass(frozen=True, slots=True)
class TypeCount:
    bson_type: str
    count: int


@dataclass(frozen=True, slots=True)
class FieldCounts:
    field: str
    types: tuple[TypeCount, ...]


@dataclass(frozen=True, slots=True)
class MetadataCounts:
    sampled_documents: int
    fields: tuple[FieldCounts, ...]

    def to_dict(self) -> dict[str, object]:
        return {"sampled_documents": self.sampled_documents, "fields": [
            {"field": field.field, "types": [
                {"type": item.bson_type, "count": item.count} for item in field.types
            ]} for field in self.fields
        ]}


def _object(value: object, expected: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise MetadataError("unexpected aggregate keys")
    return cast(dict[str, object], value)


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise MetadataError("aggregate bins must be lists")
    return value


def _count(value: object) -> int:
    if type(value) is not int or not 1 <= value <= SAMPLE_LIMIT:
        raise MetadataError("invalid aggregate count")
    return value


def normalize_metadata_counts(value: object) -> MetadataCounts:
    item = _object(value, {"sample"} | {f"f{i}" for i in range(len(FIELDS))})
    sample = _list(item["sample"])
    if len(sample) > 1:
        raise MetadataError("invalid sample cardinality")
    total = _count(_object(sample[0], {"n"})["n"]) if sample else 0
    fields: list[FieldCounts] = []
    for index, field in enumerate(FIELDS):
        bins: list[TypeCount] = []
        for raw_bin in _list(item[f"f{index}"]):
            entry = _object(raw_bin, {"_id", "n"})
            kind = entry["_id"]
            if not isinstance(kind, str) or kind not in BSON_TYPES:
                raise MetadataError("unrecognized BSON type")
            bins.append(TypeCount(kind, _count(entry["n"])))
        if len({b.bson_type for b in bins}) != len(bins):
            raise MetadataError("duplicate BSON type bin")
        if sum(b.count for b in bins) != total:
            raise MetadataError("field counts disagree with sample count")
        fields.append(FieldCounts(field, tuple(sorted(bins, key=lambda b: b.bson_type))))
    return MetadataCounts(total, tuple(fields))


def build_metadata_report(counts: MetadataCounts, mode: ExecutionMode) -> dict[str, object]:
    if mode not in ("synthetic", "live_mongo"):
        raise MetadataError("unsupported execution mode")
    normalized = counts.to_dict()
    return {
        "schema_version": "dtrm.phase4.source_metadata_inventory.v0",
        "graph": "phase4_source_metadata_inventory_v0",
        "execution_mode": mode,
        "engineering_status": "PASS_METADATA_COUNTERS_SCHEMA",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "training_permitted": False, "outcome_access_permitted": False,
        "source": {"database": DATABASE, "collection": COLLECTION},
        "selection": {"sort": "ascending_id_not_event_time", "limit": SAMPLE_LIMIT,
                      "representative": False, "exhaustiveness": "not_established"},
        "snapshot_verified": False, "timestamp_semantics_verified": False,
        "nested_metadata_inspected": False,
        "pipeline_sha256": canonical_sha256(build_metadata_pipeline()),
        "counts_sha256": canonical_sha256(normalized),
        **normalized,
    }
