"""Read-only Mongo transport for registered type counters; no source values returned."""

import importlib
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import quote

from dtrm.phase4.source_metadata import (
    COLLECTION,
    DATABASE,
    MetadataCounts,
    MetadataError,
    build_metadata_pipeline,
    normalize_metadata_counts,
)


class MetadataIOError(RuntimeError):
    """Fixed public error code; never includes driver exception text."""


class CollectionPort(Protocol):
    def aggregate(self, pipeline: list[dict[str, object]], **kwargs: object) -> Iterable[object]: ...


class DatabasePort(Protocol):
    def __getitem__(self, name: str) -> CollectionPort: ...


class ClientPort(Protocol):
    def __getitem__(self, name: str) -> DatabasePort: ...
    def close(self) -> None: ...


class ClientFactory(Protocol):
    def __call__(self, uri: str, **kwargs: object) -> ClientPort: ...


def fetch_metadata_counts(factory: ClientFactory, uri: str) -> MetadataCounts:
    """One fixed aggregate. Injected transport permits tests without database access."""
    try:
        client = factory(uri, timeoutMS=60000, serverSelectionTimeoutMS=10000,
                         socketTimeoutMS=20000, retryReads=False)
        try:
            response = list(client[DATABASE][COLLECTION].aggregate(
                build_metadata_pipeline(), maxTimeMS=20000, allowDiskUse=False,
            ))
            if len(response) != 1:
                raise MetadataError("expected one aggregate result")
            return normalize_metadata_counts(response[0])
        finally:
            client.close()
    except MetadataError:
        raise MetadataIOError("INVALID_AGGREGATE_RESPONSE") from None
    except Exception:
        raise MetadataIOError("MONGO_READ_FAILED") from None


def run_mongo_inventory(env_file: Path | None) -> MetadataCounts:
    if env_file is not None:
        if not env_file.is_file():
            raise MetadataIOError("ENV_FILE_NOT_FOUND")
        try:
            loader = cast(Callable[..., bool], importlib.import_module("dotenv").load_dotenv)
            loader(dotenv_path=env_file, override=False)
        except Exception:
            raise MetadataIOError("ENV_LOAD_FAILED") from None
    uri = os.environ.get("MONGO_URI")
    if not uri:
        password = os.environ.get("db_password")
        if not password:
            raise MetadataIOError("MISSING_LOCAL_CREDENTIALS")
        # Same source connection convention as the frozen builder; never log this value.
        uri = (f"mongodb+srv://UrtziFM:{quote(password, safe='')}@pcmoneytest.qvnkw.mongodb.net/"
               "?retryWrites=true&w=majority&appName=PCMoneyTest")
    try:
        factory = cast(ClientFactory, importlib.import_module("pymongo").MongoClient)
    except ImportError:
        raise MetadataIOError("MISSING_PYMONGO") from None
    return fetch_metadata_counts(factory, uri)
