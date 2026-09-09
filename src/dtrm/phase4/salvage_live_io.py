"""Operator-only Mongo transport. Importing this module reads no configuration."""

from __future__ import annotations

import hashlib
import importlib
import json
import logging
import os
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Iterator, Protocol, cast
from urllib.parse import quote

from dtrm.phase4 import retrospective_salvage as domain
from dtrm.phase4.retrospective_salvage_io import (
    CursorPort,
    SalvageIOError,
    read_registered_census,
)
from dtrm.phase4.salvage_live_report import LiveSalvageReport
from dtrm.phase4.source_feasibility import sanitize_indexes
from dtrm.phase4.source_metadata import COLLECTION, DATABASE, MetadataError

LOCAL_URI = "mongodb://127.0.0.1:27017/?directConnection=true"
Importer = Callable[[str], ModuleType]


def configured_uri(
    env_file: Path | None, env: Mapping[str, str] | None = None,
    importer: Importer = importlib.import_module,
) -> tuple[str, bool]:
    """Resolve only named operator configuration; tests inject an empty/fake mapping."""
    variables = os.environ if env is None else env
    if variables.get("GITHUB_ACTIONS") == "true":
        if env_file is not None or variables.get("PHASE4_SYNTHETIC_MONGO") != "1":
            raise SalvageIOError("LIVE_SOURCE_FORBIDDEN_IN_CI")
        if variables.get("MONGO_URI") != LOCAL_URI:
            raise SalvageIOError("LIVE_SOURCE_FORBIDDEN_IN_CI")
        return LOCAL_URI, True
    if env_file is not None:
        if env_file.is_symlink() or not env_file.is_file():
            raise SalvageIOError("INVALID_ENV_FILE")
        try:
            importer("dotenv").load_dotenv(dotenv_path=env_file, override=False)
        except Exception:
            raise SalvageIOError("ENV_LOAD_FAILED") from None
    uri = variables.get("MONGO_URI")
    if uri:
        return uri, False
    password = variables.get("db_password")
    if not password:
        raise SalvageIOError("MISSING_LOCAL_CREDENTIALS")
    return (
        "mongodb+srv://UrtziFM:" + quote(password, safe="")
        + "@pcmoneytest.qvnkw.mongodb.net/?retryWrites=true&w=majority&appName=PCMoneyTest",
        False,
    )


class BSONCodec:
    """Driver-bound type classifier; no connections, environment or file access."""

    def __init__(self, importer: Importer = importlib.import_module) -> None:
        self.bson = importer("bson")
        self.json_util = importer("bson.json_util")

    def type_name(self, value: object) -> str:
        # First element's wire type distinguishes e.g. Int64(1) from int32(1).
        wire = self.bson.BSON.encode({"v": value})
        names = {
            1: "double", 2: "string", 3: "object", 4: "array", 5: "binData",
            7: "objectId", 8: "bool", 9: "date", 10: "null", 11: "regex",
            12: "dbPointer", 13: "javascript", 15: "javascriptWithScope",
            16: "int", 17: "timestamp", 18: "long", 19: "decimal",
            127: "maxKey", 255: "minKey",
        }
        if wire[4] not in names:
            raise domain.SalvageError("unsupported BSON type")
        return names[wire[4]]

    def dedupe_digest(self, value: object) -> str:
        # Preserve existing JSON-compatible hashing; extended BSON stays type-tagged.
        kind = self.type_name(value)
        try:
            encoded = json.dumps({"bson_type": kind, "value": value}, sort_keys=True,
                                 separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError):
            encoded = self.json_util.dumps(
                {"bson_type": kind, "value": value},
                json_options=self.json_util.CANONICAL_JSON_OPTIONS,
                sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def normalize(self, value: object) -> domain.SalvageRow:
        if not isinstance(value, dict) or "_id" not in value:
            raise domain.SalvageError("invalid projected document")
        identifier = value["_id"]
        # Never parse an Extended-JSON wrapper in live data.
        instant = identifier.generation_time if isinstance(identifier, self.bson.ObjectId) else None
        return domain.normalize_projected_document(value, self.type_name, instant, self.dedupe_digest)


class CollectionPort(Protocol):
    def with_options(self, **kwargs: object) -> CollectionPort: ...
    def count_documents(self, query: dict[str, object]) -> int: ...
    def find(self, query: dict[str, object], **kwargs: object) -> CursorPort: ...
    def list_indexes(self) -> CursorPort: ...


class DatabasePort(Protocol):
    def __getitem__(self, name: str) -> CollectionPort: ...


class ClientPort(Protocol):
    def __getitem__(self, name: str) -> DatabasePort: ...
    def close(self) -> None: ...


class FactoryPort(Protocol):
    def __call__(self, uri: str, **kwargs: object) -> ClientPort: ...


class MongoCensusPort:
    def __init__(self, collection: CollectionPort) -> None:
        self.collection = collection

    def exact_count(self, spec: domain.CensusQuerySpec) -> int:
        del spec
        return self.collection.count_documents({})

    def open_census(self, spec: domain.CensusQuerySpec) -> CursorPort:
        return self.collection.find(
            {}, projection={path: 1 for path in spec.projected_paths},
            sort=[(spec.sort_path, spec.sort_direction)], limit=spec.cursor_limit,
            batch_size=spec.batch_size,
        )

    def open_indexes(self, spec: domain.CensusQuerySpec) -> CursorPort:
        del spec
        return self.collection.list_indexes()

    def close(self) -> None:
        # The outer boundary owns and closes the client, including setup failures.
        pass


@contextmanager
def quiet_driver() -> Iterator[None]:
    """Suppress third-party debug logs that may include connection/source details."""
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        yield
    finally:
        logging.disable(previous)


def fetch_live_audit(
    factory: FactoryPort, uri: str, read_concern: object, codec: BSONCodec,
    isolated_test: bool = False, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> LiveSalvageReport:
    """Injected read boundary; caller must resolve configuration before entering."""
    if isolated_test and uri != LOCAL_URI:
        raise SalvageIOError("LIVE_SOURCE_FORBIDDEN_IN_CI")
    with quiet_driver():
        try:
            started = clock()
            reducer = domain.SalvageReducer(started)
            client = factory(uri, timeoutMS=domain.CLIENT_TIMEOUT_MS,
                             serverSelectionTimeoutMS=domain.SERVER_SELECTION_TIMEOUT_MS,
                             socketTimeoutMS=domain.SOCKET_TIMEOUT_MS, retryReads=False)
            try:
                collection = client[DATABASE][COLLECTION].with_options(read_concern=read_concern)
                census = read_registered_census(
                    MongoCensusPort(collection), lambda row: reducer.add(codec.normalize(row)),
                )
                counts = reducer.finish()
                if counts.total_documents != census.census_count:
                    raise domain.SalvageError("census count mismatch")
                indexes = sanitize_indexes(list(census.indexes))
            finally:
                try:
                    client.close()
                except Exception:
                    raise SalvageIOError("RESOURCE_CLOSE_FAILED") from None
            report = LiveSalvageReport(counts, indexes, started, clock(),
                                       census.preliminary_count, isolated_test)
            report.to_dict()
            return report
        except SalvageIOError:
            raise
        except (domain.SalvageError, MetadataError):
            raise SalvageIOError("INVALID_LIVE_RESPONSE") from None
        except Exception:
            raise SalvageIOError("MONGO_READ_FAILED") from None


def run_live_audit(
    env_file: Path | None, env: Mapping[str, str] | None = None,
    importer: Importer = importlib.import_module,
) -> LiveSalvageReport:
    with quiet_driver():
        uri, isolated = configured_uri(env_file, env, importer)
        try:
            factory = cast(FactoryPort, importer("pymongo").MongoClient)
            concern = importer("pymongo.read_concern").ReadConcern("majority")
            codec = BSONCodec(importer)
        except Exception:
            raise SalvageIOError("DRIVER_IMPORT_FAILED") from None
        return fetch_live_audit(factory, uri, concern, codec, isolated_test=isolated)
