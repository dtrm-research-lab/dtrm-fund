"""Pure sample diagnostics; no authenticated decision clock or source promotion."""

from dataclasses import dataclass
from typing import cast

from dtrm.phase4.source_metadata import (
    BSON_TYPES,
    COLLECTION,
    DATABASE,
    SAMPLE_LIMIT,
    ExecutionMode,
    FieldCounts,
    MetadataError,
    TypeCount,
    canonical_sha256,
)

GRAPH = "phase4_source_feasibility_v0"
PATHS = (
    "raw", "dedupe_key", "raw.id", "raw.articleId", "raw.article_id", "raw.url",
    "raw.link", "raw.newsUrl", "raw.publishedDate", "raw.date", "raw.first_seen_at",
    "raw.observed_at", "raw.updated_at", "raw.version_id", "raw.content_sha256",
    "raw.mapping_version", "raw.linked_at",
)
DATE_PATHS = ("date", "raw.publishedDate", "raw.date")
PARSED = frozenset({"bson_date", "explicit_timezone_string", "date_only_string", "naive_string"})
UNPARSED = frozenset({"missing", "null", "non_date_type", "invalid_string"})


def build_feasibility_pipeline() -> list[dict[str, object]]:
    projection: dict[str, object] = {"_id": 0}
    facets: dict[str, object] = {"sample": [{"$count": "n"}]}
    for i, path in enumerate(PATHS):
        projection[f"f{i}"] = {"$type": f"${path}"}
        facets[f"f{i}"] = [{"$group": {"_id": f"$f{i}", "n": {"$sum": 1}}}]
    for i, path in enumerate(DATE_PATHS):
        projection[f"q{i}"] = f"${path}"
        value = f"$q{i}"
        facets[f"d{i}"] = [
            {"$project": {
                "t": {"$type": value},
                "s": {"$cond": [{"$eq": [{"$type": value}, "string"]}, value, ""]},
                "v": {"$convert": {"input": {"$cond": [
                    {"$in": [{"$type": value}, ["string", "date"]]}, value, None,
                ]}, "to": "date", "onError": None, "onNull": None}},
            }},
            {"$project": {
                "year": {"$dateToString": {"date": "$v", "format": "%Y", "onNull": None}},
                "kind": {"$switch": {"branches": [
                    {"case": {"$eq": ["$t", "missing"]}, "then": "missing"},
                    {"case": {"$eq": ["$t", "null"]}, "then": "null"},
                    {"case": {"$eq": ["$t", "date"]}, "then": "bson_date"},
                    {"case": {"$ne": ["$t", "string"]}, "then": "non_date_type"},
                    {"case": {"$eq": ["$v", None]}, "then": "invalid_string"},
                    {"case": {"$regexMatch": {"input": "$s", "regex":
                        r"^\d{4}-\d{2}-\d{2}$"}}, "then": "date_only_string"},
                    {"case": {"$regexMatch": {"input": "$s", "regex":
                        r"(Z|[+-]\d{2}:?\d{2})$"}}, "then": "explicit_timezone_string"},
                ], "default": "naive_string"}},
            }},
            {"$group": {"_id": {"kind": "$kind", "year": "$year"}, "n": {"$sum": 1}}},
        ]
    return [{"$sort": {"_id": 1}}, {"$limit": SAMPLE_LIMIT},
            {"$project": projection}, {"$facet": facets}]


def exact(value: object, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise MetadataError("unexpected diagnostic keys")
    return cast(dict[str, object], value)


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise MetadataError("expected diagnostic list")
    return value


def count(value: object, low: int = 1, high: int = SAMPLE_LIMIT) -> int:
    if type(value) is not int or not low <= value <= high:
        raise MetadataError("invalid diagnostic count")
    return value


@dataclass(frozen=True, slots=True)
class DateBin:
    kind: str
    year: str | None
    n: int


@dataclass(frozen=True, slots=True)
class DateCounts:
    path: str
    bins: tuple[DateBin, ...]


@dataclass(frozen=True, slots=True)
class FeasibilityCounts:
    sampled_documents: int
    fields: tuple[FieldCounts, ...]
    dates: tuple[DateCounts, ...]

    def to_dict(self) -> dict[str, object]:
        return {"sampled_documents": self.sampled_documents,
                "fields": [{"path": f.field, "types": [
                    {"type": b.bson_type, "n": b.count} for b in f.types
                ]} for f in self.fields],
                "date_diagnostics": [{"path": d.path, "bins": [
                    {"kind": b.kind, "year": b.year, "n": b.n} for b in d.bins
                ]} for d in self.dates]}


def normalize_feasibility(value: object) -> FeasibilityCounts:
    item = exact(value, {"sample"} | {f"f{i}" for i in range(len(PATHS))}
                 | {f"d{i}" for i in range(len(DATE_PATHS))})
    sample = sequence(item["sample"])
    if len(sample) > 1:
        raise MetadataError("invalid sample cardinality")
    total = count(exact(sample[0], {"n"})["n"]) if sample else 0
    fields: list[FieldCounts] = []
    for i, path in enumerate(PATHS):
        types: list[TypeCount] = []
        for raw in sequence(item[f"f{i}"]):
            entry = exact(raw, {"_id", "n"})
            kind = entry["_id"]
            if not isinstance(kind, str) or kind not in BSON_TYPES:
                raise MetadataError("invalid BSON type")
            types.append(TypeCount(kind, count(entry["n"])))
        if len({b.bson_type for b in types}) != len(types) or sum(b.count for b in types) != total:
            raise MetadataError("type counts do not reconcile")
        fields.append(FieldCounts(path, tuple(sorted(types, key=lambda b: b.bson_type))))
    dates: list[DateCounts] = []
    for i, path in enumerate(DATE_PATHS):
        bins: list[DateBin] = []
        for raw in sequence(item[f"d{i}"]):
            entry = exact(raw, {"_id", "n"})
            identity = exact(entry["_id"], {"kind", "year"})
            kind, year = identity["kind"], identity["year"]
            if not isinstance(kind, str) or kind not in PARSED | UNPARSED:
                raise MetadataError("invalid date class")
            if kind in PARSED:
                if (not isinstance(year, str) or len(year) != 4 or not year.isascii()
                        or not year.isdigit() or not 1 <= int(year) <= 9999):
                    raise MetadataError("invalid diagnostic year")
            elif year is not None:
                raise MetadataError("unparsed date has a year")
            bins.append(DateBin(kind, year, count(entry["n"])))
        if len({(b.kind, b.year) for b in bins}) != len(bins) or sum(b.n for b in bins) != total:
            raise MetadataError("date counts do not reconcile")
        if path in PATHS:
            expected: dict[str, int] = {}
            for b in fields[PATHS.index(path)].types:
                group = b.bson_type if b.bson_type in {"string", "date", "missing", "null"} else "other"
                expected[group] = expected.get(group, 0) + b.count
            observed: dict[str, int] = {}
            for d in bins:
                group = ("string" if d.kind.endswith("string") else "date" if d.kind == "bson_date"
                         else "other" if d.kind == "non_date_type" else d.kind)
                observed[group] = observed.get(group, 0) + d.n
            if observed != expected:
                raise MetadataError("date classes disagree with BSON types")
        dates.append(DateCounts(path, tuple(sorted(bins, key=lambda b: (b.kind, b.year or "")))))
    return FeasibilityCounts(total, tuple(fields), tuple(dates))


@dataclass(frozen=True, slots=True)
class IndexCounts:
    total: int
    date_ascending: int
    dedupe_ascending: int
    dedupe_unique_sparse_unqualified: int

    def to_dict(self) -> dict[str, object]:
        return {"total": self.total, "date_ascending": self.date_ascending,
                "dedupe_ascending": self.dedupe_ascending,
                "dedupe_unique_sparse_unqualified": self.dedupe_unique_sparse_unqualified}


def sanitize_indexes(value: object) -> IndexCounts:
    indexes = sequence(value)
    if len(indexes) > 64:
        raise MetadataError("index catalog exceeds bound")
    dates = dedupes = qualified = 0
    for raw in indexes:
        if not isinstance(raw, dict) or not isinstance(raw.get("key"), dict) or not raw["key"]:
            raise MetadataError("malformed index catalog")
        for flag in ("unique", "sparse", "hidden"):
            if flag in raw and type(raw[flag]) is not bool:
                raise MetadataError("malformed index flag")
        key = raw["key"]
        date_match = len(key) == 1 and type(key.get("date")) is int and key.get("date") == 1
        dedupe_match = len(key) == 1 and type(key.get("dedupe_key")) is int and key.get("dedupe_key") == 1
        dates += date_match
        dedupes += dedupe_match
        qualified += (dedupe_match and raw.get("unique") is True and raw.get("sparse") is True
                      and raw.get("hidden", False) is False and not any(
                          k in raw for k in ("partialFilterExpression", "collation", "expireAfterSeconds", "buildUUID")))
    return IndexCounts(len(indexes), dates, dedupes, qualified)


def build_feasibility_report(
    counts: FeasibilityCounts, indexes: IndexCounts, mode: ExecutionMode,
) -> dict[str, object]:
    if mode not in ("synthetic", "live_mongo"):
        raise MetadataError("invalid execution mode")
    evidence = {**counts.to_dict(), "indexes": indexes.to_dict()}
    return {"schema_version": "dtrm.phase4.source_feasibility.v0", "graph": GRAPH,
            "execution_mode": mode, "engineering_status": "PASS_DIAGNOSTIC_SCHEMA",
            "scientific_status": "BLOCKED_SOURCE_AUDIT", "training_permitted": False,
            "outcome_access_permitted": False, "history_construction_permitted": False,
            "snapshot_verified": False, "decision_clock_authenticated": False,
            "source": {"database": DATABASE, "collection": COLLECTION},
            "selection": {"limit": SAMPLE_LIMIT, "sort": "ascending_id_not_event_time",
                          "representative": False, "coverage_scope": "sample_only"},
            "date_year_semantics": "diagnostic_UTC_conversion_not_availability",
            "index_semantics": "current_definitions_not_historical_enforcement",
            "reads_atomic": False, "pipeline_sha256": canonical_sha256(build_feasibility_pipeline()),
            "evidence_sha256": canonical_sha256(evidence), **evidence}
