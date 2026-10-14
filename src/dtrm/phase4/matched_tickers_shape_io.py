"""Operator-local optional Mongo read boundary for aggregate-only shape taxonomy.

Importing this module never discovers credentials or connects to a source.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterator, Mapping
from itertools import islice
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast

from dtrm.phase4.matched_tickers_shape_audit import (
    CENSUS_CAP,
    ShapeAssessment,
    ShapeAuditError,
    build_shape_pipeline,
    normalize_shape_counts,
)
from dtrm.phase4.retrospective_salvage_io import SalvageIOError
from dtrm.phase4.salvage_live_io import LOCAL_URI, configured_uri, quiet_driver
from dtrm.phase4.source_metadata import COLLECTION, DATABASE

Importer = Callable[[str], ModuleType]


class ShapeAuditIOError(RuntimeError):
    """A fixed code, never a driver exception or source value."""


class CursorPort(Protocol):
    def __iter__(self) -> Iterator[object]: ...
    def close(self) -> None: ...


class CollectionPort(Protocol):
    def count_documents(self, query: dict[str, object], **kwargs: object) -> int: ...
    def aggregate(self, pipeline: list[dict[str, object]], **kwargs: object) -> CursorPort: ...


class DatabasePort(Protocol):
    def __getitem__(self, name: str) -> CollectionPort: ...


class ClientPort(Protocol):
    def __getitem__(self, name: str) -> DatabasePort: ...
    def close(self) -> None: ...


class FactoryPort(Protocol):
    def __call__(self, uri: str, **kwargs: object) -> ClientPort: ...


def analyze_injected_collection(collection: CollectionPort) -> ShapeAssessment:
    """Never fetch documents: the driver receives only two arrays of type groups."""
    try:
        n = collection.count_documents({}, maxTimeMS=60_000)
        if type(n) is not int or n < 0 or n > CENSUS_CAP:
            raise ShapeAuditIOError("SOURCE_COUNT_OUT_OF_BOUNDS")
        cursor = collection.aggregate(
            build_shape_pipeline(), maxTimeMS=60_000, allowDiskUse=False
        )
        try:
            rows = list(islice(cursor, 2))
        finally:
            cursor.close()
        if len(rows) != 1:
            raise ShapeAuditIOError("INVALID_AGGREGATE_CARDINALITY")
        return normalize_shape_counts(rows[0], counted_documents=n)
    except ShapeAuditIOError:
        raise
    except ShapeAuditError:
        raise ShapeAuditIOError("INVALID_AGGREGATE_SHAPE") from None
    except Exception:
        raise ShapeAuditIOError("READ_ONLY_AGGREGATE_FAILED") from None


def operator_local_shape_audit(
    env_file: Path | None, env: Mapping[str, str] | None = None,
    importer: Importer = importlib.import_module,
) -> ShapeAssessment:
    """No production access in CI; one fixed majority-read MongoDB query."""
    with quiet_driver():
        try:
            uri, isolated = configured_uri(env_file, env, importer)
        except SalvageIOError:
            raise ShapeAuditIOError("SOURCE_CONFIGURATION_BLOCKED") from None
        if isolated and uri != LOCAL_URI:
            raise ShapeAuditIOError("LIVE_SOURCE_FORBIDDEN_IN_CI")
        try:
            mongo = importer("pymongo")
            concern = importer("pymongo.read_concern").ReadConcern("majority")
            factory = cast(FactoryPort, mongo.MongoClient)
        except Exception:
            raise ShapeAuditIOError("DRIVER_IMPORT_FAILED") from None
        try:
            client = factory(
                uri, timeoutMS=90_000, serverSelectionTimeoutMS=10_000,
                socketTimeoutMS=70_000, retryReads=False,
            )
            try:
                collection = client[DATABASE][COLLECTION].with_options(read_concern=concern)
                report = analyze_injected_collection(collection)
            finally:
                client.close()
            return report
        except ShapeAuditIOError:
            raise
        except Exception:
            raise ShapeAuditIOError("MONGO_READ_FAILED") from None
