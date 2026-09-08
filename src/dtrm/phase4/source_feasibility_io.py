"""Explicit read-only transport; only bounded sanitized metadata leaves this boundary."""

import importlib
import os
from collections.abc import Callable, Iterator
from itertools import islice
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import quote

from dtrm.phase4.source_feasibility import (
    FeasibilityCounts,
    IndexCounts,
    build_feasibility_pipeline,
    normalize_feasibility,
    sanitize_indexes,
)
from dtrm.phase4.source_metadata import COLLECTION, DATABASE, MetadataError
from dtrm.phase4.source_metadata_io import MetadataIOError


class CursorPort(Protocol):
    def __iter__(self) -> Iterator[object]: ...
    def close(self) -> None: ...


class CollectionPort(Protocol):
    def aggregate(self, pipeline: list[dict[str, object]], **kwargs: object) -> CursorPort: ...
    def list_indexes(self) -> CursorPort: ...


class DatabasePort(Protocol):
    def __getitem__(self, name: str) -> CollectionPort: ...


class ClientPort(Protocol):
    def __getitem__(self, name: str) -> DatabasePort: ...
    def close(self) -> None: ...


class FactoryPort(Protocol):
    def __call__(self, uri: str, **kwargs: object) -> ClientPort: ...


def read_bounded(cursor: CursorPort, limit: int) -> list[object]:
    try:
        return list(islice(cursor, limit))
    finally:
        cursor.close()


def fetch_feasibility(factory: FactoryPort, uri: str) -> tuple[FeasibilityCounts, IndexCounts]:
    try:
        client = factory(uri, timeoutMS=60000, serverSelectionTimeoutMS=10000,
                         socketTimeoutMS=20000, retryReads=False)
        try:
            collection = client[DATABASE][COLLECTION]
            response = read_bounded(collection.aggregate(
                build_feasibility_pipeline(), maxTimeMS=20000, allowDiskUse=False,
            ), 2)
            if len(response) != 1:
                raise MetadataError("expected one diagnostic result")
            counts = normalize_feasibility(response[0])
            indexes = sanitize_indexes(read_bounded(collection.list_indexes(), 65))
            return counts, indexes
        finally:
            client.close()
    except MetadataError:
        raise MetadataIOError("INVALID_DIAGNOSTIC_RESPONSE") from None
    except Exception:
        raise MetadataIOError("MONGO_READ_FAILED") from None


def configured_uri(env_file: Path | None) -> str:
    if env_file is not None:
        if not env_file.is_file():
            raise MetadataIOError("ENV_FILE_NOT_FOUND")
        try:
            loader = cast(Callable[..., bool], importlib.import_module("dotenv").load_dotenv)
            loader(dotenv_path=env_file, override=False)
        except Exception:
            raise MetadataIOError("ENV_LOAD_FAILED") from None
    uri = os.environ.get("MONGO_URI")
    if uri:
        return uri
    password = os.environ.get("db_password")
    if not password:
        raise MetadataIOError("MISSING_LOCAL_CREDENTIALS")
    return (f"mongodb+srv://UrtziFM:{quote(password, safe='')}@pcmoneytest.qvnkw.mongodb.net/"
            "?retryWrites=true&w=majority&appName=PCMoneyTest")


def run_mongo_feasibility(env_file: Path | None) -> tuple[FeasibilityCounts, IndexCounts]:
    uri = configured_uri(env_file)
    try:
        factory = cast(FactoryPort, importlib.import_module("pymongo").MongoClient)
    except ImportError:
        raise MetadataIOError("MISSING_PYMONGO") from None
    return fetch_feasibility(factory, uri)
