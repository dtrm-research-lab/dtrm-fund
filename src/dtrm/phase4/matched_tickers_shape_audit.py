"""Aggregate-only BSON type census of matched_tickers. No driver or source values."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, NoReturn, cast

CENSUS_CAP = 250_000
ELEMENT_CAP = 5_000_000
GROUP_CAP = 128
FIELDS = ("ticker", "symbol", "name", "score", "confidence", "match_type")
BSON_TYPES = frozenset((
    "double", "string", "object", "array", "binData", "undefined", "objectId",
    "bool", "date", "null", "regex", "dbPointer", "javascript", "symbol",
    "javascriptWithScope", "int", "timestamp", "long", "decimal",
    "maxKey", "minKey", "missing",
))


class ShapeAuditError(ValueError):
    """Sanitized error with no provider values."""


def _reject() -> NoReturn:
    raise ShapeAuditError("INVALID_MATCHED_TICKERS_SHAPE_AGGREGATE")


def build_shape_pipeline() -> list[dict[str, Any]]:
    """A fixed read-only aggregation; the driver sees type counts, never values."""
    shapes = {
        field: {"$cond": [
            {"$eq": [{"$type": "$items"}, "object"]},
            {"$type": "$items." + field},
            "not_object",
        ]}
        for field in FIELDS
    }
    grouped = {"kind": "$kind", **{field: "$" + field for field in FIELDS}}
    output = {"_id": 0, "kind": "$_id.kind", "n": 1}
    output.update({field: "$_id." + field for field in FIELDS})
    return [
        {"$limit": CENSUS_CAP + 1},
        {"$project": {
            "container_kind": {"$type": "$matched_tickers"},
            "items": {"$cond": [{"$isArray": "$matched_tickers"}, "$matched_tickers", []]},
        }},
        {"$facet": {
            "containers": [
                {"$group": {"_id": "$container_kind", "n": {"$sum": 1}}},
                {"$project": {"_id": 0, "kind": "$_id", "n": 1}},
                {"$limit": len(BSON_TYPES) + 1},
            ],
            "elements": [
                {"$unwind": "$items"},
                {"$project": {"kind": {"$type": "$items"}, **shapes}},
                {"$group": {"_id": grouped, "n": {"$sum": 1}}},
                {"$project": output},
                {"$limit": GROUP_CAP + 1},
            ],
        }},
    ]


def _exact(value: object, keys: frozenset[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject()
    return cast(dict[str, object], value)


def _count(value: object, maximum: int) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        _reject()
    return value


@dataclass(frozen=True, slots=True)
class ShapeGroup:
    kind: str
    n: int
    fields: tuple[str, str, str, str, str, str] | None = None

    def to_json(self) -> dict[str, object]:
        value: dict[str, object] = {"kind": self.kind, "n": self.n}
        if self.fields is not None:
            value.update(dict(zip(FIELDS, self.fields, strict=True)))
        return value


@dataclass(frozen=True, slots=True)
class ShapeAssessment:
    """Immutable group counts, not authentic asset mappings."""

    sha256: str
    documents: int
    elements_count: int
    containers: tuple[ShapeGroup, ...]
    elements: tuple[ShapeGroup, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "schema_version": "dtrm.phase4.matched_tickers_shape_report.v0",
            "engineering_status": "PASS_AGGREGATE_SHAPE_SCHEMA",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "data_scope": "aggregate_only_non_atomic_census",
            "asset_mapping_authenticated": False,
            "vintage_authenticated": False,
            "decision_clock_authenticated": False,
            "history_construction_permitted": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "document_count": self.documents,
            "element_count": self.elements_count,
            "sanitized_evidence_sha256": self.sha256,
            "containers": [g.to_json() for g in self.containers],
            "elements": [g.to_json() for g in self.elements],
        }


def normalize_shape_counts(raw: object, *, counted_documents: int) -> ShapeAssessment:
    """Validate only type labels and aggregate counters, with exact allowlists."""
    if type(counted_documents) is not int or not 0 <= counted_documents <= CENSUS_CAP:
        _reject()
    root = _exact(raw, frozenset(("containers", "elements")))
    cs = root["containers"]
    es = root["elements"]
    if not isinstance(cs, list) or len(cs) > len(BSON_TYPES):
        _reject()
    if not isinstance(es, list) or len(es) > GROUP_CAP:
        _reject()
    containers: list[ShapeGroup] = []
    elements: list[ShapeGroup] = []
    seen: set[str] = set()
    distinct: set[tuple[str, ...]] = set()
    doc_total = 0
    element_total = 0
    for raw_group in cs:
        group = _exact(raw_group, frozenset(("kind", "n")))
        kind = group["kind"]
        if not isinstance(kind, str) or kind not in BSON_TYPES or kind in seen:
            _reject()
        seen.add(kind)
        n = _count(group["n"], CENSUS_CAP)
        doc_total += n
        containers.append(ShapeGroup(kind, n))
    if doc_total != counted_documents:
        _reject()
    for raw_group in es:
        group = _exact(raw_group, frozenset(("kind", "n", *FIELDS)))
        kind = group["kind"]
        if not isinstance(kind, str) or kind not in BSON_TYPES:
            _reject()
        values = tuple(group[field] for field in FIELDS)
        if any(not isinstance(x, str) for x in values):
            _reject()
        if kind == "object":
            if any(x not in BSON_TYPES for x in values):
                _reject()
        elif values != ("not_object",) * len(FIELDS):
            _reject()
        identity = (kind, *(cast(str, x) for x in values))
        if identity in distinct:
            _reject()
        distinct.add(identity)
        n = _count(group["n"], ELEMENT_CAP)
        element_total += n
        if element_total > ELEMENT_CAP:
            _reject()
        elements.append(ShapeGroup(kind, n, cast(tuple[str, str, str, str, str, str], values)))
    if element_total and "array" not in seen:
        _reject()
    containers.sort(key=lambda x: x.kind)
    elements.sort(key=lambda x: (x.kind, x.fields or ()))
    evidence = {
        "document_count": counted_documents,
        "element_count": element_total,
        "containers": [x.to_json() for x in containers],
        "elements": [x.to_json() for x in elements],
    }
    sha = hashlib.sha256(
        json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return ShapeAssessment(sha, counted_documents, element_total, tuple(containers), tuple(elements))
