"""Injectable census boundary; this increment contains no production connector."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from itertools import islice
from typing import Protocol, cast

from dtrm.phase4.retrospective_salvage import (
    CENSUS_CAP,
    CURSOR_LIMIT,
    INDEX_LIMIT,
    CensusQuerySpec,
    SalvageError,
    SalvageReducer,
    SalvageReport,
    build_census_query_spec,
    build_salvage_report_from_counts,
    normalize_synthetic_document,
    parse_audit_instant,
    parse_writer_manifest,
)
from dtrm.phase4.source_feasibility import sanitize_indexes
from dtrm.phase4.source_metadata import MetadataError


class SalvageIOError(RuntimeError):
    """Fixed public boundary error; never contains source or driver text."""


class CursorPort(Protocol):
    def __iter__(self) -> Iterator[object]: ...
    def close(self) -> None: ...


class CensusPort(Protocol):
    def exact_count(self, spec: CensusQuerySpec) -> int: ...
    def open_census(self, spec: CensusQuerySpec) -> CursorPort: ...
    def open_indexes(self, spec: CensusQuerySpec) -> CursorPort: ...
    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class CensusRead:
    preliminary_count: int
    census_count: int
    indexes: tuple[object, ...]


def _close(resource: CursorPort | CensusPort) -> None:
    try:
        resource.close()
    except Exception:
        raise SalvageIOError("RESOURCE_CLOSE_FAILED") from None


def read_registered_census(port: CensusPort, consume: Callable[[object], None]) -> CensusRead:
    """Enforce both the preliminary cap and cap-plus-one stream boundary."""

    spec = build_census_query_spec()
    try:
        preliminary_count = port.exact_count(spec)
        if type(preliminary_count) is not int or preliminary_count < 0:
            raise SalvageIOError("INVALID_SOURCE_COUNT")
        if preliminary_count > CENSUS_CAP:
            raise SalvageIOError("SOURCE_EXCEEDS_REGISTERED_BOUND")

        row_cursor = port.open_census(spec)
        try:
            census_count = 0
            for position, document in enumerate(islice(row_cursor, CURSOR_LIMIT), start=1):
                if position == CURSOR_LIMIT:
                    raise SalvageIOError("SOURCE_EXCEEDS_REGISTERED_BOUND")
                consume(document)
                census_count = position
        finally:
            _close(row_cursor)

        index_cursor = port.open_indexes(spec)
        try:
            indexes = tuple(islice(index_cursor, INDEX_LIMIT))
            if len(indexes) == INDEX_LIMIT:
                raise SalvageIOError("INDEX_CATALOG_EXCEEDS_BOUND")
        finally:
            _close(index_cursor)
        return CensusRead(preliminary_count, census_count, indexes)
    except (SalvageIOError, SalvageError):
        raise
    except Exception:
        raise SalvageIOError("CENSUS_READ_FAILED") from None
    finally:
        _close(port)


class _MemoryCursor:
    def __init__(self, values: Sequence[object]) -> None:
        self._values = values
        self.closed = False

    def __iter__(self) -> Iterator[object]:
        return iter(self._values)

    def close(self) -> None:
        self.closed = True


class SyntheticCensusPort:
    """In-memory fixture port; never imports a database driver or reads configuration."""

    def __init__(self, documents: Sequence[object], indexes: Sequence[object]) -> None:
        self._documents = tuple(documents)
        self._indexes = tuple(indexes)
        self.closed = False

    def exact_count(self, spec: CensusQuerySpec) -> int:
        del spec
        return len(self._documents)

    def open_census(self, spec: CensusQuerySpec) -> CursorPort:
        del spec
        return _MemoryCursor(self._documents)

    def open_indexes(self, spec: CensusQuerySpec) -> CursorPort:
        del spec
        return _MemoryCursor(self._indexes)

    def close(self) -> None:
        self.closed = True


def _sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise SalvageError(f"{label}: expected list")
    return value


def run_synthetic_audit(value: object) -> SalvageReport:
    """Execute the graph against one exact, non-production fixture schema."""

    if not isinstance(value, dict) or set(value) != {
        "audit_started_at",
        "audit_completed_at",
        "documents",
        "indexes",
        "writer_manifest",
    }:
        raise SalvageError("synthetic fixture: unexpected keys")
    item = cast(dict[str, object], value)
    started = parse_audit_instant(item["audit_started_at"], "audit_started_at")
    completed = parse_audit_instant(item["audit_completed_at"], "audit_completed_at")
    documents = _sequence(item["documents"], "documents")
    indexes = _sequence(item["indexes"], "indexes")
    writer = parse_writer_manifest(item["writer_manifest"])
    reducer = SalvageReducer(started)
    census = read_registered_census(
        SyntheticCensusPort(documents, indexes),
        lambda document: reducer.add(normalize_synthetic_document(document)),
    )
    try:
        sanitized_indexes = sanitize_indexes(list(census.indexes))
    except MetadataError:
        raise SalvageError("invalid sanitized index catalog") from None
    counts = reducer.finish()
    if census.census_count != counts.total_documents:
        raise SalvageError("streamed census count does not reconcile")
    return build_salvage_report_from_counts(
        counts,
        sanitized_indexes,
        writer,
        started,
        completed,
        census.preliminary_count,
    )
