"""Bounded, privacy-safe present-day Mongo publication-window observation.

A present-day source census is NOT a historical availability proof or snapshot.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import NoReturn

GRAPH = "phase4_current_mongo_observed_window_v0"
MAX_ROWS = 250_000
MAX_PROJECTED_BSON_BYTES = 1_048_576
LEADING_DAY = re.compile(r"^(\\d{4}-\\d{2}-\\d{2})(?:$|T|\\s)")
STATUS = "PASS_CURRENT_MONGO_WINDOW_OBSERVATION"


class ObservationError(ValueError):
    """Fixed input error, never include source values."""


def _fail() -> NoReturn:
    raise ObservationError("BLOCKED_CURRENT_MONGO_OBSERVATION")


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _fail()
    return value.astimezone(timezone.utc)


def _day(value: object) -> date:
    if not isinstance(value, str):
        _fail()
    match = LEADING_DAY.match(value)
    if match is None:
        _fail()
    try:
        result = date.fromisoformat(match.group(1))
    except ValueError:
        _fail()
    return result


class ObservedWindowReducer:
    """Pure ordered projected-BSON digest and publication-day/shape counters."""

    def __init__(self, started_at: datetime) -> None:
        self.started = _utc(started_at)
        self.first_day = self.started.date() - timedelta(days=59)
        self.last_day = self.started.date()
        self.total = 0
        self.within = 0
        self.older = 0
        self.future = 0
        self.daily: Counter[str] = Counter()
        self.ticker_shape: Counter[str] = Counter()
        self._prior_id: bytes | None = None
        self._digest = hashlib.sha256()

    def add(self, identifier: bytes, published: object, text: object,
            tickers: object, raw_projected_bson: bytes) -> None:
        if not isinstance(identifier, bytes) or len(identifier) != 12:
            _fail()
        if self._prior_id is not None and identifier <= self._prior_id:
            _fail()
        if (not isinstance(raw_projected_bson, bytes)
                or not 0 < len(raw_projected_bson) <= MAX_PROJECTED_BSON_BYTES):
            _fail()
        if not isinstance(text, str) or not text.strip():
            _fail()
        if not isinstance(tickers, list):
            _fail()
        if self.total >= MAX_ROWS:
            _fail()
        publication = _day(published)
        if publication < self.first_day:
            self.older += 1
        elif publication > self.last_day:
            self.future += 1
        else:
            self.within += 1
            self.daily[publication.isoformat()] += 1
        if not tickers:
            shape = "empty"
        elif all(type(value) is str for value in tickers):
            shape = "string_only"
        elif all(type(value) is dict for value in tickers):
            shape = "object_only"
        else:
            shape = "mixed_or_other"
        self.ticker_shape[shape] += 1
        self._digest.update(len(raw_projected_bson).to_bytes(8, "big"))
        self._digest.update(raw_projected_bson)
        self.total += 1
        self._prior_id = identifier

    def finish(self, *, initial_count: int, final_count: int,
               completed_at: datetime) -> dict[str, object]:
        completed = _utc(completed_at)
        if (type(initial_count) is not int or type(final_count) is not int
                or self.total != initial_count or self.total != final_count
                or not 0 <= self.total <= MAX_ROWS or completed < self.started):
            _fail()
        first = self.first_day
        daily = [
            {"published_day": (first + timedelta(days=i)).isoformat(),
             "currently_present_rows": self.daily.get((first + timedelta(days=i)).isoformat(), 0)}
            for i in range(60)
        ]
        return {
            "graph": GRAPH,
            "status": STATUS,
            "execution_mode": "operator_live_mongo",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "source": "current_mongo_legacy_collection",
            "observed_between_utc": {
                "started": self.started.isoformat().replace("+00:00", "Z"),
                "completed": completed.isoformat().replace("+00:00", "Z"),
            },
            "publication_window_utc_day": {
                "from": self.first_day.isoformat(),
                "through": self.last_day.isoformat(),
            },
            "source_rows": self.total,
            "currently_present_in_publication_window": self.within,
            "currently_present_before_window": self.older,
            "currently_present_after_window": self.future,
            "ticker_element_shape_rows": {
                key: self.ticker_shape.get(key, 0)
                for key in ("empty", "string_only", "object_only", "mixed_or_other")
            },
            "daily_publication_day_counts": daily,
            "ordered_projected_bson_stream_sha256": self._digest.hexdigest(),
            "count_before_after_consistent": True,
            "atomic_mongo_snapshot_authenticated": False,
            "historical_source_first_seen_authenticated": False,
            "historical_link_first_seen_authenticated": False,
            "source_complete_60day_history_authenticated": False,
            "temporal_state_training_permitted": False,
            "outcomes_access_permitted": False,
            "mm1_execution_permitted": False,
            "aws_activated": False,
        }
