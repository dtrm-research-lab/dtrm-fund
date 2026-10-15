"""One-shot, operator-local and read-only current-Mongo 60-day observation.

Never execute in CI. No raw news, symbol, URL, Mongo URI or AWS upload.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn

from dtrm.phase4.current_mongo_observation import (
    GRAPH, MAX_ROWS, ObservationError, ObservedWindowReducer,
)
from dtrm.phase4.salvage_live_io import configured_uri, quiet_driver
from dtrm.phase4.source_metadata import COLLECTION, DATABASE


class _RedactedParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        del message
        raise ObservationError("INVALID_ARGUMENTS")


def _write_exclusive(destination: Path, data: bytes) -> None:
    parent = destination.parent
    if destination.is_symlink() or destination.exists() or not parent.is_dir():
        raise ObservationError("INVALID_PRIVATE_OUTPUT")
    info = parent.stat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o022 or parent.is_symlink()):
        raise ObservationError("INVALID_PRIVATE_OUTPUT")
    descriptor, temp = tempfile.mkstemp(prefix=".phase4-current-window-", dir=parent)
    published = False
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, destination)  # Never overwrite previous observations.
        published = True
    finally:
        try:
            os.unlink(temp)
        except OSError:
            if not published:
                raise ObservationError("INVALID_PRIVATE_OUTPUT") from None


def _observe(env_file: Path | None) -> dict[str, object]:
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI") == "true":
        raise ObservationError("LIVE_SOURCE_FORBIDDEN_IN_CI")
    with quiet_driver():
        uri, isolated = configured_uri(env_file)
        if isolated:
            raise ObservationError("LIVE_SOURCE_FORBIDDEN_IN_CI")
        driver = importlib.import_module("pymongo")
        bson = importlib.import_module("bson")
        raw_bson = importlib.import_module("bson.raw_bson")
        codec = importlib.import_module("bson.codec_options")
        concern = importlib.import_module("pymongo.read_concern")
        started = datetime.now(timezone.utc)
        reducer = ObservedWindowReducer(started)
        client = driver.MongoClient(
            uri, timeoutMS=180000, serverSelectionTimeoutMS=10000,
            socketTimeoutMS=30000, retryReads=False,
        )
        try:
            collection = client[DATABASE][COLLECTION].with_options(
                read_concern=concern.ReadConcern("majority"),
            )
            initial = collection.count_documents({})
            if type(initial) is not int or not 0 <= initial <= MAX_ROWS:
                raise ObservationError("SOURCE_OUTSIDE_REGISTERED_LIMIT")
            raw_collection = collection.with_options(
                codec_options=codec.CodecOptions(
                    document_class=raw_bson.RawBSONDocument,
                )
            )
            cursor = raw_collection.find(
                {}, projection={"_id": 1, "date": 1, "text": 1,
                                "matched_tickers": 1},
                sort=[("_id", 1)], limit=MAX_ROWS + 1, batch_size=500,
            )
            try:
                for item in cursor:
                    oid = item.get("_id")
                    if not isinstance(oid, bson.ObjectId):
                        raise ObservationError("INVALID_SOURCE_DOCUMENT")
                    reducer.add(
                        oid.binary, item.get("date"), item.get("text"),
                        item.get("matched_tickers"), item.raw,
                    )
            finally:
                cursor.close()
            final = collection.count_documents({})
            completed = datetime.now(timezone.utc)
        finally:
            client.close()
        return reducer.finish(initial_count=initial, final_count=final,
                              completed_at=completed)


def main(argv: list[str] | None = None) -> int:
    parser = _RedactedParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        if args.output.is_symlink() or args.output.exists():
            raise ObservationError("INVALID_PRIVATE_OUTPUT")
        if not args.output.parent.is_dir():
            raise ObservationError("INVALID_PRIVATE_OUTPUT")
        result = _observe(args.env_file)
        encoded = (json.dumps(result, sort_keys=True, indent=2,
                              separators=(",", ": "), ensure_ascii=True,
                              allow_nan=False) + "\n").encode("utf-8")
        _write_exclusive(args.output, encoded)
        print(json.dumps({
            "graph": GRAPH,
            "status": result["status"],
            "source_rows": result["source_rows"],
            "currently_present_in_publication_window":
                result["currently_present_in_publication_window"],
            "ordered_projected_bson_stream_sha256":
                result["ordered_projected_bson_stream_sha256"],
            "scientific_status": result["scientific_status"],
        }, sort_keys=True))
        return 0
    except (KeyboardInterrupt, Exception):
        print(json.dumps({"graph": GRAPH, "status": "failed",
                          "error_code": "BLOCKED_CURRENT_MONGO_OBSERVATION"},
                         sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
