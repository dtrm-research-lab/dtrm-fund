"""Pure retrospective-salvage graph for aggregate-only synthetic evidence."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Literal, cast

from dtrm.phase4.source_feasibility import IndexCounts
from dtrm.phase4.source_metadata import COLLECTION, DATABASE, canonical_sha256

GRAPH = "phase4_retrospective_salvage_v0"
SCHEMA_VERSION = "dtrm.phase4.retrospective_salvage.v0"
CONTRACT_PATH = "research/contracts/DTRM_PHASE4_RETROSPECTIVE_SALVAGE_AUDIT_V0.md"
CONTRACT_SHA256 = "331ad4aaa2a60d4f2a3d172963e71052873d5942a475d4d3aa600d05495286f6"
INITIAL_REGISTRATION_COMMIT = "b38b3fc1851e1f636240e7fa418da2dcc933db8d"
INITIAL_CONTRACT_SHA256 = "e9ed93bcd39181f2037227eee39690b9259753a686b3f9e89614243f41d8e5c9"
AMENDMENT_COMMIT = "a1e7ce59d9e99a0b7d36d3989664508536dbb0ae"

CENSUS_CAP = 250_000
CURSOR_LIMIT = CENSUS_CAP + 1
BATCH_SIZE = 500
INDEX_LIMIT = 65
CLIENT_TIMEOUT_MS = 180_000
SERVER_SELECTION_TIMEOUT_MS = 10_000
SOCKET_TIMEOUT_MS = 30_000

PROJECTED_PATHS = (
    "_id",
    "date",
    "text",
    "source",
    "matched_tickers",
    "dedupe_key",
    "raw.id",
    "raw.articleId",
    "raw.article_id",
    "raw.url",
    "raw.link",
    "raw.newsUrl",
    "raw.publishedDate",
    "raw.date",
)
TOP_LEVEL_PATHS = frozenset(
    {"_id", "date", "text", "source", "matched_tickers", "dedupe_key", "raw"}
)
RAW_PATHS = frozenset(path.removeprefix("raw.") for path in PROJECTED_PATHS if path.startswith("raw."))
PROVIDER_PATHS = ("raw.publishedDate", "raw.date", "date")
URL_PATHS = ("raw.url", "raw.link", "raw.newsUrl")
SOURCE_ID_PATHS = ("raw.id", "raw.articleId", "raw.article_id")
LAG_LABELS = (
    "le_minus_2",
    "minus_1",
    "zero",
    "plus_1",
    "plus_2_7",
    "plus_8_30",
    "plus_31_365",
    "gt_365",
    "provider_day_unknown",
)
TICKER_LENGTH_LABELS = ("1", "2_5", "6_20", "gt_20")
URL_GROUP_LABELS = ("2", "3_5", "6_20", "gt_20")

DecisionState = Literal[
    "RETROSPECTIVE_PROXY_CONTRADICTED",
    "RETROSPECTIVE_PROXY_PARTIAL",
    "RETROSPECTIVE_PROXY_CANDIDATE",
]

_LEADING_DAY = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_MISSING = object()
_FORBIDDEN_REPORT_FRAGMENTS = (
    "mongodb+srv://",
    "authorization: bearer",
    "-----begin private key-----",
)


class SalvageError(ValueError):
    """Input or state violates the preregistered salvage boundary."""


@dataclass(frozen=True, slots=True)
class SyntheticObjectId:
    """Explicit Extended-JSON stand-in; never treated as live BSON evidence."""

    hex_value: str

    @classmethod
    def parse(cls, value: object) -> SyntheticObjectId:
        if not isinstance(value, str) or len(value) != 24:
            raise SalvageError("invalid synthetic ObjectId")
        lowered = value.lower()
        if value != lowered or any(char not in "0123456789abcdef" for char in value):
            raise SalvageError("invalid synthetic ObjectId")
        return cls(value)

    @property
    def generation_time(self) -> datetime:
        return datetime.fromtimestamp(int(self.hex_value[:8], 16), tz=timezone.utc)


@dataclass(frozen=True, slots=True)
class CensusQuerySpec:
    database: str
    collection: str
    projected_paths: tuple[str, ...]
    sort_path: str
    sort_direction: int
    cursor_limit: int
    batch_size: int
    client_timeout_ms: int
    server_selection_timeout_ms: int
    socket_timeout_ms: int
    retry_reads: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "namespace": {"database": self.database, "collection": self.collection},
            "count_filter": {},
            "cursor_filter": {},
            "projection": {path: 1 for path in self.projected_paths},
            "sort": {self.sort_path: self.sort_direction},
            "cursor_limit": self.cursor_limit,
            "batch_size": self.batch_size,
            "client_timeout_ms": self.client_timeout_ms,
            "server_selection_timeout_ms": self.server_selection_timeout_ms,
            "socket_timeout_ms": self.socket_timeout_ms,
            "retry_reads": self.retry_reads,
            "read_concern": "majority_preferred_without_source_mutation",
        }


def build_census_query_spec() -> CensusQuerySpec:
    """Return a fresh, fixed query specification without opening a connection."""

    return CensusQuerySpec(
        DATABASE,
        COLLECTION,
        PROJECTED_PATHS,
        "_id",
        1,
        CURSOR_LIMIT,
        BATCH_SIZE,
        CLIENT_TIMEOUT_MS,
        SERVER_SELECTION_TIMEOUT_MS,
        SOCKET_TIMEOUT_MS,
        False,
    )


@dataclass(frozen=True, slots=True)
class CountBin:
    label: str
    n: int

    def to_dict(self) -> dict[str, object]:
        return {"label": self.label, "n": self.n}


@dataclass(frozen=True, slots=True)
class PathTypeCounts:
    path: str
    bins: tuple[CountBin, ...]

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "types": [item.to_dict() for item in self.bins]}


@dataclass(frozen=True, slots=True)
class SourceIdPathCounts:
    path: str
    missing: int
    null: int
    present: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "missing": self.missing,
            "null": self.null,
            "present": self.present,
        }


@dataclass(frozen=True, slots=True)
class SalvageRow:
    field_types: tuple[str, ...]
    id_time: datetime | None
    provider_day: date | None
    provider_origin: str
    provider_parse: str
    text_class: str
    content_digest: str | None
    url_digest: str | None
    source_id_states: tuple[str, ...]
    source_id_origin: str
    ticker_shape: str
    ticker_length_bin: str | None
    ticker_malformed_elements: int
    ticker_has_duplicate: bool
    dedupe_digest: str | None


@dataclass(frozen=True, slots=True)
class WriterManifest:
    mode: str
    relevant_writers: str
    deployed_intervals: str
    id_assignment: str
    write_operations: str
    atomic_text_tickers: str
    later_mutation: str
    client_clock: str
    runtime_immutability: str
    write_authority: str

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "relevant_writers": self.relevant_writers,
            "deployed_intervals": self.deployed_intervals,
            "id_assignment": self.id_assignment,
            "write_operations": self.write_operations,
            "atomic_text_tickers": self.atomic_text_tickers,
            "later_mutation": self.later_mutation,
            "client_clock": self.client_clock,
            "runtime_immutability": self.runtime_immutability,
            "write_authority": self.write_authority,
        }


@dataclass(frozen=True, slots=True)
class SalvageCounts:
    total_documents: int
    field_types: tuple[PathTypeCounts, ...]
    genuine_object_ids: int
    non_object_ids: int
    object_id_months: tuple[CountBin, ...]
    future_clock_anomalies: int
    lag_bins: tuple[CountBin, ...]
    provider_origins: tuple[CountBin, ...]
    provider_parse: tuple[CountBin, ...]
    text_classes: tuple[CountBin, ...]
    distinct_content_digests: int
    url_keyed: int
    url_unkeyed: int
    distinct_url_groups: int
    singleton_url_groups: int
    repeated_url_groups: int
    repeated_url_groups_no_content: int
    repeated_url_groups_one_content: int
    repeated_url_groups_multiple_content: int
    repeated_url_group_sizes: tuple[CountBin, ...]
    source_id_paths: tuple[SourceIdPathCounts, ...]
    source_id_origins: tuple[CountBin, ...]
    ticker_shapes: tuple[CountBin, ...]
    ticker_length_bins: tuple[CountBin, ...]
    ticker_malformed_elements: int
    ticker_rows_with_duplicates: int
    dedupe_missing: int
    dedupe_present: int
    distinct_dedupe_keys: int
    repeated_dedupe_groups: int

    def to_dict(self) -> dict[str, object]:
        total = self.total_documents
        return {
            "total_documents": total,
            "field_types": [item.to_dict() for item in self.field_types],
            "object_ids": {
                "genuine": self.genuine_object_ids,
                "non_object_id": self.non_object_ids,
                "structurally_eligible": self.genuine_object_ids,
                "semantics": "synthetic_extended_json_not_live_bson_evidence",
                "utc_months": [item.to_dict() for item in self.object_id_months],
                "future_clock_anomalies": self.future_clock_anomalies,
                "provider_day_lag_bins": [item.to_dict() for item in self.lag_bins],
            },
            "provider_days": {
                "origins": [item.to_dict() for item in self.provider_origins],
                "parse": [item.to_dict() for item in self.provider_parse],
                "semantics": "diagnostic_calendar_day_not_availability",
            },
            "text": {
                "classes": [item.to_dict() for item in self.text_classes],
                "distinct_exact_utf8_sha256": self.distinct_content_digests,
            },
            "urls": {
                "keyed_rows": self.url_keyed,
                "unkeyed_rows": self.url_unkeyed,
                "distinct_hashed_groups": self.distinct_url_groups,
                "singleton_groups": self.singleton_url_groups,
                "repeated_groups": self.repeated_url_groups,
                "repeated_groups_with_no_content_digest": self.repeated_url_groups_no_content,
                "repeated_groups_with_one_content_digest": self.repeated_url_groups_one_content,
                "repeated_groups_with_multiple_content_digests": (
                    self.repeated_url_groups_multiple_content
                ),
                "repeated_group_size_bins": [
                    item.to_dict() for item in self.repeated_url_group_sizes
                ],
            },
            "source_ids": {
                "paths": [item.to_dict() for item in self.source_id_paths],
                "first_nonempty_string_origin": [
                    item.to_dict() for item in self.source_id_origins
                ],
                "mixed_with_url_identity": False,
            },
            "matched_tickers": {
                "shapes": [item.to_dict() for item in self.ticker_shapes],
                "length_bins": [item.to_dict() for item in self.ticker_length_bins],
                "malformed_elements": self.ticker_malformed_elements,
                "rows_with_exact_duplicates": self.ticker_rows_with_duplicates,
            },
            "dedupe_keys": {
                "missing": self.dedupe_missing,
                "present": self.dedupe_present,
                "distinct_hashed_keys": self.distinct_dedupe_keys,
                "repeated_key_groups": self.repeated_dedupe_groups,
            },
            "reconciliation": {
                "status": "PASS",
                "total_documents": total,
                "field_paths_reconciled": len(self.field_types),
                "object_id_rows": self.genuine_object_ids + self.non_object_ids,
                "provider_origin_rows": sum(item.n for item in self.provider_origins),
                "provider_parse_rows": sum(item.n for item in self.provider_parse),
                "text_rows": sum(item.n for item in self.text_classes),
                "url_rows": self.url_keyed + self.url_unkeyed,
                "ticker_rows": sum(item.n for item in self.ticker_shapes),
                "dedupe_rows": self.dedupe_missing + self.dedupe_present,
            },
        }


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise SalvageError(f"{label}: expected object")
    return cast(dict[str, object], value)


def _exact_mapping(value: object, keys: set[str], label: str) -> dict[str, object]:
    item = _mapping(value, label)
    if set(item) != keys:
        raise SalvageError(f"{label}: unexpected keys")
    return item


def _path_value(document: Mapping[str, object], path: str) -> object:
    current: object = document
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _bson_type(value: object) -> str:
    if value is _MISSING:
        return "missing"
    if isinstance(value, SyntheticObjectId):
        return "objectId"
    if value is None:
        return "null"
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int" if -(2**31) <= value < 2**31 else "long"
    if type(value) is float:
        return "double"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, datetime):
        return "date"
    raise SalvageError("unsupported projected value type")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_value_digest(value: object) -> str:
    try:
        encoded = json.dumps(
            {"bson_type": _bson_type(value), "value": value},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        raise SalvageError("dedupe key cannot be deterministically hashed") from None
    return _sha256_text(encoded)


def _provider_day(document: Mapping[str, object]) -> tuple[date | None, str, str]:
    for path in PROVIDER_PATHS:
        value = _path_value(document, path)
        if type(value) is str:
            match = _LEADING_DAY.match(value)
            if match is None:
                return None, path, "invalid"
            try:
                return date.fromisoformat(match.group(1)), path, "parsed"
            except ValueError:
                return None, path, "invalid"
    return None, "none", "no_string"


def _first_nonempty_string(
    document: Mapping[str, object], paths: Sequence[str]
) -> tuple[str | None, str]:
    for path in paths:
        value = _path_value(document, path)
        if type(value) is str and value.strip():
            return value.strip(), path
    return None, "none"


def _ticker_observation(value: object) -> tuple[str, str | None, int, bool]:
    if value is _MISSING:
        return "missing", None, 0, False
    if not isinstance(value, list):
        return "non_array", None, 0, False
    if not value:
        return "empty", None, 0, False
    size = len(value)
    if size == 1:
        length_bin = "1"
    elif size <= 5:
        length_bin = "2_5"
    elif size <= 20:
        length_bin = "6_20"
    else:
        length_bin = "gt_20"
    valid = [item for item in value if type(item) is str and bool(item.strip())]
    malformed = size - len(valid)
    duplicate = len(valid) != len(set(valid))
    return "nonempty", length_bin, malformed, duplicate


def normalize_synthetic_document(value: object) -> SalvageRow:
    """Normalize one allowlisted Extended-JSON row without retaining source values."""

    item = _mapping(value, "document")
    if "_id" not in item or not set(item) <= TOP_LEVEL_PATHS:
        raise SalvageError("document: missing _id or unexpected projected key")
    raw = item.get("raw", _MISSING)
    if isinstance(raw, dict) and not set(raw) <= RAW_PATHS:
        raise SalvageError("document.raw: unexpected projected key")

    document = dict(item)
    raw_id = document["_id"]
    if isinstance(raw_id, dict) and set(raw_id) == {"$oid"}:
        document["_id"] = SyntheticObjectId.parse(raw_id["$oid"])
    elif isinstance(raw_id, dict) and "$oid" in raw_id:
        raise SalvageError("invalid synthetic ObjectId wrapper")

    identifier = document["_id"]
    id_time = identifier.generation_time if isinstance(identifier, SyntheticObjectId) else None
    return normalize_projected_document(document, _bson_type, id_time, _canonical_value_digest)


def normalize_projected_document(
    value: object,
    type_name: Callable[[object], str],
    id_time: datetime | None,
    dedupe_hash: Callable[[object], str],
) -> SalvageRow:
    """Shared deterministic derivations with explicit transport type semantics."""

    document = _mapping(value, "document")
    if "_id" not in document or not set(document) <= TOP_LEVEL_PATHS:
        raise SalvageError("document: missing _id or unexpected projected key")
    raw = document.get("raw", _MISSING)
    if isinstance(raw, dict) and not set(raw) <= RAW_PATHS:
        raise SalvageError("document.raw: unexpected projected key")
    field_types = tuple(
        "missing" if (item := _path_value(document, path)) is _MISSING else type_name(item)
        for path in PROJECTED_PATHS
    )
    provider_day, provider_origin, provider_parse = _provider_day(document)

    text = _path_value(document, "text")
    if text is _MISSING:
        text_class, content_digest = "missing", None
    elif text is None:
        text_class, content_digest = "null", None
    elif type(text) is str:
        text_class = "string_empty" if text == "" else "string_nonempty"
        content_digest = _sha256_text(text)
    else:
        text_class, content_digest = "non_string", None

    url, _ = _first_nonempty_string(document, URL_PATHS)
    if url is not None:
        url = url.split("#", 1)[0]
    url_digest = _sha256_text(url) if url is not None else None

    source_states: list[str] = []
    for path in SOURCE_ID_PATHS:
        source_value = _path_value(document, path)
        source_states.append(
            "missing" if source_value is _MISSING else "null" if source_value is None else "present"
        )
    _, source_origin = _first_nonempty_string(document, SOURCE_ID_PATHS)

    ticker_shape, ticker_length, malformed, duplicate = _ticker_observation(
        _path_value(document, "matched_tickers")
    )
    dedupe = _path_value(document, "dedupe_key")
    dedupe_digest = None if dedupe is _MISSING else dedupe_hash(dedupe)
    return SalvageRow(
        field_types,
        id_time,
        provider_day,
        provider_origin,
        provider_parse,
        text_class,
        content_digest,
        url_digest,
        tuple(source_states),
        source_origin,
        ticker_shape,
        ticker_length,
        malformed,
        duplicate,
        dedupe_digest,
    )


def parse_audit_instant(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value or value != value.strip():
        raise SalvageError(f"{label}: expected timezone-aware timestamp")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else ""))
    except ValueError:
        raise SalvageError(f"{label}: invalid timestamp") from None
    if parsed.tzinfo is None:
        raise SalvageError(f"{label}: timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def _fixed_bins(counter: Counter[str], labels: Sequence[str]) -> tuple[CountBin, ...]:
    return tuple(CountBin(label, counter[label]) for label in labels)


def _lag_label(delta: int) -> str:
    if delta <= -2:
        return "le_minus_2"
    if delta == -1:
        return "minus_1"
    if delta == 0:
        return "zero"
    if delta == 1:
        return "plus_1"
    if delta <= 7:
        return "plus_2_7"
    if delta <= 30:
        return "plus_8_30"
    if delta <= 365:
        return "plus_31_365"
    return "gt_365"


def _group_size_label(size: int) -> str:
    if size == 2:
        return "2"
    if size <= 5:
        return "3_5"
    if size <= 20:
        return "6_20"
    return "gt_20"


class SalvageReducer:
    """Consume normalized rows one at a time and retain aggregate state only."""

    def __init__(self, audit_started_at: datetime) -> None:
        if audit_started_at.tzinfo is None:
            raise SalvageError("audit_started_at must include timezone")
        self.started = audit_started_at.astimezone(timezone.utc)
        self.total = 0
        self.field_counters = [Counter[str]() for _ in PROJECTED_PATHS]
        self.month_counts: Counter[str] = Counter()
        self.lag_counts: Counter[str] = Counter()
        self.provider_origins: Counter[str] = Counter()
        self.provider_parse: Counter[str] = Counter()
        self.text_classes: Counter[str] = Counter()
        self.content_digests: set[str] = set()
        self.url_group_sizes: Counter[str] = Counter()
        self.url_group_contents: dict[str, set[str]] = {}
        self.source_path_states = [Counter[str]() for _ in SOURCE_ID_PATHS]
        self.source_origins: Counter[str] = Counter()
        self.ticker_shapes: Counter[str] = Counter()
        self.ticker_lengths: Counter[str] = Counter()
        self.dedupe_groups: Counter[str] = Counter()
        self.genuine = 0
        self.future = 0
        self.malformed = 0
        self.duplicate_rows = 0
        self.dedupe_missing = 0

    def add(self, row: SalvageRow) -> None:
        """Reduce one row without retaining the row or any raw projected document."""

        self.total += 1
        if self.total > CENSUS_CAP:
            raise SalvageError("census exceeds registered bound")
        if len(row.field_types) != len(PROJECTED_PATHS):
            raise SalvageError("row field types do not match projection")
        for counter, kind in zip(self.field_counters, row.field_types, strict=True):
            counter[kind] += 1
        if row.id_time is not None:
            self.genuine += 1
            id_time = row.id_time.astimezone(timezone.utc)
            self.month_counts[id_time.strftime("%Y-%m")] += 1
            if id_time > self.started + timedelta(minutes=5):
                self.future += 1
            self.lag_counts[
                "provider_day_unknown"
                if row.provider_day is None
                else _lag_label((id_time.date() - row.provider_day).days)
            ] += 1
        self.provider_origins[row.provider_origin] += 1
        self.provider_parse[row.provider_parse] += 1
        self.text_classes[row.text_class] += 1
        if row.content_digest is not None:
            self.content_digests.add(row.content_digest)
        if row.url_digest is not None:
            self.url_group_sizes[row.url_digest] += 1
            if row.content_digest is not None:
                self.url_group_contents.setdefault(row.url_digest, set()).add(
                    row.content_digest
                )
        for counter, state in zip(self.source_path_states, row.source_id_states, strict=True):
            counter[state] += 1
        self.source_origins[row.source_id_origin] += 1
        self.ticker_shapes[row.ticker_shape] += 1
        if row.ticker_length_bin is not None:
            self.ticker_lengths[row.ticker_length_bin] += 1
        self.malformed += row.ticker_malformed_elements
        self.duplicate_rows += int(row.ticker_has_duplicate)
        if row.dedupe_digest is None:
            self.dedupe_missing += 1
        else:
            self.dedupe_groups[row.dedupe_digest] += 1

    def finish(self) -> SalvageCounts:
        """Freeze and reconcile the aggregate state."""

        total = self.total
        repeated_size_counts: Counter[str] = Counter()
        singleton_groups = repeated_groups = no_content = one_content = multiple_content = 0
        for url_digest, size in self.url_group_sizes.items():
            if size == 1:
                singleton_groups += 1
                continue
            repeated_groups += 1
            repeated_size_counts[_group_size_label(size)] += 1
            distinct_count = len(self.url_group_contents.get(url_digest, ()))
            if distinct_count == 0:
                no_content += 1
            elif distinct_count == 1:
                one_content += 1
            else:
                multiple_content += 1

        fields = tuple(
            PathTypeCounts(path, tuple(CountBin(kind, n) for kind, n in sorted(counter.items())))
            for path, counter in zip(PROJECTED_PATHS, self.field_counters, strict=True)
        )
        source_paths = tuple(
            SourceIdPathCounts(path, counter["missing"], counter["null"], counter["present"])
            for path, counter in zip(SOURCE_ID_PATHS, self.source_path_states, strict=True)
        )
        result = SalvageCounts(
            total,
            fields,
            self.genuine,
            total - self.genuine,
            tuple(CountBin(month, n) for month, n in sorted(self.month_counts.items())),
            self.future,
            _fixed_bins(self.lag_counts, LAG_LABELS),
            _fixed_bins(self.provider_origins, (*PROVIDER_PATHS, "none")),
            _fixed_bins(self.provider_parse, ("parsed", "invalid", "no_string")),
            _fixed_bins(
                self.text_classes,
                ("missing", "null", "string_empty", "string_nonempty", "non_string"),
            ),
            len(self.content_digests),
            sum(self.url_group_sizes.values()),
            total - sum(self.url_group_sizes.values()),
            len(self.url_group_sizes),
            singleton_groups,
            repeated_groups,
            no_content,
            one_content,
            multiple_content,
            _fixed_bins(repeated_size_counts, URL_GROUP_LABELS),
            source_paths,
            _fixed_bins(self.source_origins, (*SOURCE_ID_PATHS, "none")),
            _fixed_bins(self.ticker_shapes, ("missing", "non_array", "empty", "nonempty")),
            _fixed_bins(self.ticker_lengths, TICKER_LENGTH_LABELS),
            self.malformed,
            self.duplicate_rows,
            self.dedupe_missing,
            total - self.dedupe_missing,
            len(self.dedupe_groups),
            sum(1 for n in self.dedupe_groups.values() if n > 1),
        )
        _validate_reconciliation(result)
        return result


def aggregate_rows(rows: Iterable[SalvageRow], audit_started_at: datetime) -> SalvageCounts:
    """Stream ephemeral rows into order-invariant, aggregate-only counters."""

    reducer = SalvageReducer(audit_started_at)
    for row in rows:
        reducer.add(row)
    return reducer.finish()


def _validate_reconciliation(counts: SalvageCounts) -> None:
    total = counts.total_documents
    if any(sum(item.n for item in path.bins) != total for path in counts.field_types):
        raise SalvageError("field type counts do not reconcile")
    totals = (
        counts.genuine_object_ids + counts.non_object_ids,
        sum(item.n for item in counts.provider_origins),
        sum(item.n for item in counts.provider_parse),
        sum(item.n for item in counts.text_classes),
        counts.url_keyed + counts.url_unkeyed,
        sum(item.n for item in counts.ticker_shapes),
        counts.dedupe_missing + counts.dedupe_present,
    )
    if any(value != total for value in totals):
        raise SalvageError("aggregate counters do not reconcile")
    if counts.genuine_object_ids != sum(item.n for item in counts.lag_bins):
        raise SalvageError("ObjectId lag counters do not reconcile")
    if counts.repeated_url_groups != (
        counts.repeated_url_groups_no_content
        + counts.repeated_url_groups_one_content
        + counts.repeated_url_groups_multiple_content
    ):
        raise SalvageError("URL version counters do not reconcile")


def parse_writer_manifest(value: object) -> WriterManifest:
    keys = {
        "mode",
        "relevant_writers",
        "deployed_intervals",
        "id_assignment",
        "write_operations",
        "atomic_text_tickers",
        "later_mutation",
        "client_clock",
        "runtime_immutability",
        "write_authority",
    }
    item = _exact_mapping(value, keys, "writer_manifest")
    policies = {
        "mode": {"synthetic_only"},
        "relevant_writers": {"bounded", "unknown"},
        "deployed_intervals": {"bounded", "unknown"},
        "id_assignment": {"mongo_default", "external_unbounded", "unknown"},
        "write_operations": {"insert_only", "mutating", "unknown"},
        "atomic_text_tickers": {"supported", "contradicted", "unknown"},
        "later_mutation": {"absent", "present", "unknown"},
        "client_clock": {"bounded", "unbounded", "unknown"},
        "runtime_immutability": {"supported", "contradicted", "unknown"},
        "write_authority": {"bounded_exclusive", "unknown"},
    }
    for key in keys:
        raw = item[key]
        if not isinstance(raw, str) or raw not in policies[key]:
            raise SalvageError(f"writer_manifest.{key}: unsupported state")
    return WriterManifest(
        cast(str, item["mode"]),
        cast(str, item["relevant_writers"]),
        cast(str, item["deployed_intervals"]),
        cast(str, item["id_assignment"]),
        cast(str, item["write_operations"]),
        cast(str, item["atomic_text_tickers"]),
        cast(str, item["later_mutation"]),
        cast(str, item["client_clock"]),
        cast(str, item["runtime_immutability"]),
        cast(str, item["write_authority"]),
    )


def assess_decision(counts: SalvageCounts, writer: WriterManifest) -> DecisionState:
    """Apply the fixed exactly-one-state decision lattice."""

    if counts.genuine_object_ids == 0:
        return "RETROSPECTIVE_PROXY_CONTRADICTED"
    contradicted = (
        writer.id_assignment == "external_unbounded"
        or writer.write_operations != "insert_only"
        or writer.atomic_text_tickers != "supported"
        or writer.later_mutation == "present"
        or writer.client_clock == "unbounded"
        or writer.runtime_immutability == "contradicted"
    )
    if contradicted:
        return "RETROSPECTIVE_PROXY_CONTRADICTED"
    candidate = (
        writer.relevant_writers == "bounded"
        and writer.deployed_intervals == "bounded"
        and writer.id_assignment == "mongo_default"
        and writer.later_mutation == "absent"
        and writer.client_clock == "bounded"
        and writer.runtime_immutability == "supported"
        and writer.write_authority == "bounded_exclusive"
    )
    return "RETROSPECTIVE_PROXY_CANDIDATE" if candidate else "RETROSPECTIVE_PROXY_PARTIAL"


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class SalvageReport:
    """Immutable report state whose nested payload and hashes are derived afresh."""

    counts: SalvageCounts
    indexes: IndexCounts
    writer: WriterManifest
    audit_started_at: datetime
    audit_completed_at: datetime
    preliminary_count: int

    def __getitem__(self, key: str) -> object:
        """Expose a fresh derived value for read-only reporting consumers."""

        return self.to_dict()[key]

    @property
    def scientific_assessment(self) -> DecisionState:
        return assess_decision(self.counts, self.writer)

    @property
    def scientific_status(self) -> str:
        return (
            "BLOCKED_DECISION_CLOCK_BINDING"
            if self.scientific_assessment == "RETROSPECTIVE_PROXY_CANDIDATE"
            else "BLOCKED_SOURCE_AUDIT"
        )

    def to_dict(self) -> dict[str, object]:
        evidence = {
            **self.counts.to_dict(),
            "indexes": self.indexes.to_dict(),
            "writer_findings": self.writer.to_dict(),
        }
        total = self.counts.total_documents
        return {
            "schema_version": SCHEMA_VERSION,
            "graph": GRAPH,
            "execution_mode": "synthetic",
            "engineering_status": "PASS_SYNTHETIC_AUDIT_SCHEMA",
            "scientific_assessment": self.scientific_assessment,
            "assessment_semantics": "synthetic_lattice_exercise_not_source_evidence",
            "scientific_status": self.scientific_status,
            "decision_clock_authenticated": False,
            "snapshot_verified": False,
            "writer_runtime_evidence_authenticated": False,
            "live_bson_semantics_validated": False,
            "history_construction_permitted": False,
            "training_permitted": False,
            "outcome_access_permitted": False,
            "model_fitting_performed": False,
            "production_source_accessed": False,
            "registered_contract": {
                "path": CONTRACT_PATH,
                "initial_registration_commit": INITIAL_REGISTRATION_COMMIT,
                "initial_sha256": INITIAL_CONTRACT_SHA256,
                "amendment_commit": AMENDMENT_COMMIT,
                "sha256": CONTRACT_SHA256,
            },
            "source": {"database": DATABASE, "collection": COLLECTION},
            "selection": {
                "preliminary_count": self.preliminary_count,
                "census_count": total,
                "count_cursor_delta": total - self.preliminary_count,
                "registered_cap": CENSUS_CAP,
                "cursor_limit": CURSOR_LIMIT,
                "sort": "ascending_id_not_event_time",
                "projection": list(PROJECTED_PATHS),
                "reads_atomic": False,
                "complete_within_registered_bound": True,
            },
            "audit_metadata": {
                "started_at": _iso_utc(self.audit_started_at),
                "completed_at": _iso_utc(self.audit_completed_at),
                "source_availability_semantics": False,
            },
            "pipeline_sha256": canonical_sha256(build_census_query_spec().to_dict()),
            "writer_manifest_sha256": canonical_sha256(self.writer.to_dict()),
            "evidence_sha256": canonical_sha256(evidence),
            **evidence,
        }


def build_salvage_report_from_counts(
    counts: SalvageCounts,
    indexes: IndexCounts,
    writer: WriterManifest,
    audit_started_at: datetime,
    audit_completed_at: datetime,
    preliminary_count: int,
) -> SalvageReport:
    """Validate and freeze one report assembled from streamed aggregate counts."""

    if type(preliminary_count) is not int or not 0 <= preliminary_count <= CENSUS_CAP:
        raise SalvageError("invalid preliminary count")
    if audit_started_at.tzinfo is None or audit_completed_at.tzinfo is None:
        raise SalvageError("invalid audit interval")
    started = audit_started_at.astimezone(timezone.utc)
    completed = audit_completed_at.astimezone(timezone.utc)
    if completed < started:
        raise SalvageError("invalid audit interval")
    if counts.total_documents > CENSUS_CAP:
        raise SalvageError("census exceeds registered bound")
    _validate_reconciliation(counts)
    return SalvageReport(counts, indexes, writer, started, completed, preliminary_count)


def build_salvage_report(
    rows: Iterable[SalvageRow],
    indexes: IndexCounts,
    writer: WriterManifest,
    audit_started_at: datetime,
    audit_completed_at: datetime,
    preliminary_count: int,
) -> SalvageReport:
    counts = aggregate_rows(rows, audit_started_at)
    return build_salvage_report_from_counts(
        counts, indexes, writer, audit_started_at, audit_completed_at, preliminary_count
    )


def serialize_salvage_report(report: SalvageReport) -> str:
    if type(report) is not SalvageReport:
        raise SalvageError("serializer requires immutable SalvageReport")
    encoded = json.dumps(report.to_dict(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    lowered = encoded.lower()
    if any(fragment in lowered for fragment in _FORBIDDEN_REPORT_FRAGMENTS):
        raise SalvageError("report contains forbidden credential material")
    return encoded
