"""Immutable aggregate-only live audit state; no configuration or driver access."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
from typing import cast

from dtrm.phase4 import retrospective_salvage as domain
from dtrm.phase4.source_feasibility import IndexCounts
from dtrm.phase4.source_metadata import canonical_sha256

REGISTRATION = "13625046e8b258f085fab59966a31937786a5eec"
CONTRACT_PATH = "research/contracts/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_LIVE_ADAPTER_V0.md"
CONTRACT_SHA256 = "f98ce5e5d22810618571725d1645806729da358ff7622a7c47150cdc3e5cfcad"
BSON_TYPES = frozenset({
    "missing", "null", "objectId", "string", "bool", "int", "long", "double",
    "object", "array", "date", "binData", "decimal", "timestamp", "regex",
    "javascript", "javascriptWithScope", "minKey", "maxKey", "dbPointer",
})
_LABELS = BSON_TYPES | frozenset({
    *domain.PROJECTED_PATHS, *domain.LAG_LABELS, *domain.TICKER_LENGTH_LABELS,
    *domain.URL_GROUP_LABELS, "none", "parsed", "invalid", "no_string",
    "string_empty", "string_nonempty", "non_string", "non_array", "empty", "nonempty",
})


def fixed_writer() -> domain.WriterManifest:
    return domain.WriterManifest(
        "registered_static_evidence_v0", "unknown", "unknown", "mongo_default",
        "insert_only", "supported", "unknown", "unknown", "unknown", "unknown",
    )


def live_query_spec() -> dict[str, object]:
    spec = domain.build_census_query_spec().to_dict()
    spec["read_concern"] = "majority"
    return spec


def _validate_aggregate(value: object) -> None:
    """Reject mutable containers and arbitrary strings even in constructed states."""
    if type(value) is int and value >= 0:
        return
    if type(value) is str and (value in _LABELS or re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value)):
        return
    if type(value) is tuple:
        for item in value:
            _validate_aggregate(item)
        return
    if type(value) in (
        domain.SalvageCounts, domain.PathTypeCounts, domain.CountBin,
        domain.SourceIdPathCounts, IndexCounts,
    ):
        assert is_dataclass(value) and not isinstance(value, type)
        for field in fields(value):
            _validate_aggregate(getattr(value, field.name))
        return
    raise domain.SalvageError("invalid immutable aggregate state")


@dataclass(frozen=True, slots=True)
class LiveSalvageReport:
    counts: domain.SalvageCounts
    indexes: IndexCounts
    started: datetime
    completed: datetime
    preliminary_count: int
    isolated_test: bool = False

    def to_dict(self) -> dict[str, object]:
        if type(self.counts) is not domain.SalvageCounts or type(self.indexes) is not IndexCounts:
            raise domain.SalvageError("invalid aggregate types")
        if type(self.isolated_test) is not bool:
            raise domain.SalvageError("invalid execution context")
        _validate_aggregate(self.counts)
        _validate_aggregate(self.indexes)
        if tuple(item.path for item in self.counts.field_types) != domain.PROJECTED_PATHS:
            raise domain.SalvageError("field paths mismatch")
        for item in self.counts.field_types:
            labels = tuple(b.label for b in item.bins)
            if labels != tuple(sorted(set(labels))) or not set(labels) <= BSON_TYPES:
                raise domain.SalvageError("invalid field type bins")
        expected_bins = (
            (self.counts.lag_bins, domain.LAG_LABELS),
            (self.counts.provider_origins, (*domain.PROVIDER_PATHS, "none")),
            (self.counts.provider_parse, ("parsed", "invalid", "no_string")),
            (self.counts.text_classes,
             ("missing", "null", "string_empty", "string_nonempty", "non_string")),
            (self.counts.repeated_url_group_sizes, domain.URL_GROUP_LABELS),
            (self.counts.source_id_origins, (*domain.SOURCE_ID_PATHS, "none")),
            (self.counts.ticker_shapes, ("missing", "non_array", "empty", "nonempty")),
            (self.counts.ticker_length_bins, domain.TICKER_LENGTH_LABELS),
        )
        if any(tuple(b.label for b in bins) != labels for bins, labels in expected_bins):
            raise domain.SalvageError("registered bins mismatch")
        if tuple(p.path for p in self.counts.source_id_paths) != domain.SOURCE_ID_PATHS:
            raise domain.SalvageError("source ID paths mismatch")
        if any(p.missing + p.null + p.present != self.counts.total_documents
               for p in self.counts.source_id_paths):
            raise domain.SalvageError("source ID counts mismatch")
        months = tuple(b.label for b in self.counts.object_id_months)
        if months != tuple(sorted(set(months))) or any(
            re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month) is None for month in months
        ):
            raise domain.SalvageError("invalid month bins")
        if sum(b.n for b in self.counts.object_id_months) != self.counts.genuine_object_ids:
            raise domain.SalvageError("ObjectId months mismatch")
        if not (self.indexes.dedupe_unique_sparse_unqualified <= self.indexes.dedupe_ascending
                <= self.indexes.total < domain.INDEX_LIMIT):
            raise domain.SalvageError("invalid index counts")
        if self.indexes.date_ascending > self.indexes.total:
            raise domain.SalvageError("invalid date index count")
        base = domain.build_salvage_report_from_counts(
            self.counts, self.indexes, fixed_writer(), self.started, self.completed,
            self.preliminary_count,
        )
        if base.scientific_assessment == "RETROSPECTIVE_PROXY_CANDIDATE":
            raise domain.SalvageError("candidate forbidden in adapter v0")
        result = base.to_dict()
        object_ids = dict(cast(dict[str, object], result["object_ids"]))
        object_ids["semantics"] = "bson_generation_time_not_authenticated_availability"
        result["object_ids"] = object_ids
        result.update(
            execution_mode="live_mongo",
            engineering_status="PASS_LIVE_AUDIT_SCHEMA",
            assessment_semantics="live_source_aggregate_audit_not_decision_clock_evidence",
            production_source_accessed=not self.isolated_test,
            live_bson_semantics_validated=True,
            pipeline_sha256=canonical_sha256(live_query_spec()),
        )
        result["live_adapter"] = {
            "path": CONTRACT_PATH, "registration_commit": REGISTRATION,
            "sha256": CONTRACT_SHA256, "requested_read_concern": "majority",
            "isolated_test": self.isolated_test,
        }
        evidence = {key: result[key] for key in (
            *self.counts.to_dict(), "indexes", "writer_findings",
        )}
        result["evidence_sha256"] = canonical_sha256(evidence)
        return result


def serialize_live_report(report: LiveSalvageReport) -> str:
    if type(report) is not LiveSalvageReport:
        raise domain.SalvageError("immutable live report required")
    return json.dumps(report.to_dict(), sort_keys=True, indent=2, ensure_ascii=False,
                      allow_nan=False) + "\n"
