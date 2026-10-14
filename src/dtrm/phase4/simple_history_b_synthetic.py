"""Phase IV B: deterministic *synthetic-only* history summary mechanics.

This is not an authenticated dataset, an approved representation recipe,
a trained B arm, or a model/market decision.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, NoReturn, cast

SCHEMA = "dtrm.phase4.simple_history_fixture.v0"
CASE_TAGS = frozenset(f"case_{i:02d}" for i in range(1, 65))
EVENT_TAGS = frozenset(f"event_{i:02d}" for i in range(1, 65))
ROLES = ("fmp_articles", "general_latest", "stock_latest")
ROLE_SET = frozenset(ROLES)
INSTANT_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z"
)


class SyntheticHistoryError(ValueError):
    """Input rejected without echoing any submitted value."""


def _reject() -> NoReturn:
    raise SyntheticHistoryError("INVALID_PHASE4_SYNTHETIC_HISTORY")


def _exact(value: Any, keys: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject()
    return cast(dict[str, Any], value)


def _instant(value: Any) -> datetime:
    if not isinstance(value, str) or not INSTANT_RE.fullmatch(value) or value.endswith("-00:00"):
        _reject()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            _reject()
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        _reject()


def _utc(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class SyntheticBCase:
    """A purely invented case with no authenticated histories."""

    case_tag: str
    lookback_days: int
    window_count: int
    role_counts: tuple[int, int, int]
    most_recent_age_seconds: int | None

    def to_json(self) -> dict[str, Any]:
        return {
            "case_tag": self.case_tag,
            "lookback_days": self.lookback_days,
            "window_count": self.window_count,
            "role_counts": dict(zip(ROLES, self.role_counts, strict=True)),
            "most_recent_age_seconds": self.most_recent_age_seconds,
        }


@dataclass(frozen=True, slots=True)
class SyntheticBAssessment:
    """Frozen, detached output; positive scientific flags are impossible."""

    input_sha256: str
    cases: tuple[SyntheticBCase, ...]
    window_total: int

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": "dtrm.phase4.simple_history_mechanics_report.v0",
            "engineering_status": "PASS_SYNTHETIC_B_MECHANICS",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "source_authenticated": False,
            "decision_clock_authenticated": False,
            "zero_history_authenticated": False,
            "g5_lookback_frozen": False,
            "history_construction_permitted": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "scientific_counting_permitted": False,
            "input_sha256": self.input_sha256,
            "case_count": len(self.cases),
            "window_total": self.window_total,
            "cases": [case.to_json() for case in self.cases],
        }


def assess_synthetic_b_mechanics(fixture: Any) -> SyntheticBAssessment:
    """Validate invented event times and count strictly historical events."""
    document = _exact(fixture, frozenset(("schema_version", "dataset_role", "cases")))
    if document["schema_version"] != SCHEMA or document["dataset_role"] != "synthetic":
        _reject()
    cases = document["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 64:
        _reject()
    typed: list[SyntheticBCase] = []
    canonical: list[dict[str, Any]] = []
    seen_cases: set[str] = set()
    total = 0
    for raw_case in cases:
        case = _exact(raw_case, frozenset(("case_tag", "decision_cutoff", "lookback_days", "events")))
        case_tag = case["case_tag"]
        if not isinstance(case_tag, str) or case_tag not in CASE_TAGS or case_tag in seen_cases:
            _reject()
        seen_cases.add(case_tag)
        days = case["lookback_days"]
        if type(days) is not int or not 1 <= days <= 365:
            _reject()
        lookback_days = cast(int, days)
        cutoff = _instant(case["decision_cutoff"])
        try:
            start = cutoff - timedelta(days=lookback_days)
        except OverflowError:
            _reject()
        raw_events = case["events"]
        if not isinstance(raw_events, list) or len(raw_events) > 64:
            _reject()
        seen_events: set[str] = set()
        normalized_events: list[dict[str, str]] = []
        counts = {role: 0 for role in ROLES}
        newest: datetime | None = None
        for raw_event in raw_events:
            event = _exact(raw_event, frozenset(("event_tag", "source_role", "effective_available_at")))
            tag = event["event_tag"]
            role = event["source_role"]
            if not isinstance(tag, str) or tag not in EVENT_TAGS or tag in seen_events:
                _reject()
            if not isinstance(role, str) or role not in ROLE_SET:
                _reject()
            seen_events.add(tag)
            instant = _instant(event["effective_available_at"])
            if instant >= cutoff:
                _reject()
            normalized_events.append({
                "event_tag": tag, "source_role": role, "effective_available_at": _utc(instant)
            })
            if instant >= start:
                counts[role] += 1
                if newest is None or instant > newest:
                    newest = instant
        normalized_events.sort(key=lambda item: item["event_tag"])
        window_count = sum(counts.values())
        total += window_count
        age: int | None = None
        if newest is not None:
            delta = cutoff - newest
            age = delta.days * 86400 + delta.seconds
        typed.append(SyntheticBCase(
            case_tag=case_tag,
            lookback_days=lookback_days,
            window_count=window_count,
            role_counts=cast(tuple[int, int, int], tuple(counts[role] for role in ROLES)),
            most_recent_age_seconds=age,
        ))
        canonical.append({
            "case_tag": case_tag, "decision_cutoff": _utc(cutoff),
            "lookback_days": lookback_days, "events": normalized_events
        })
    canonical.sort(key=lambda item: item["case_tag"])
    typed.sort(key=lambda item: item.case_tag)
    digest = hashlib.sha256(
        json.dumps(
            {"schema_version": SCHEMA, "dataset_role": "synthetic", "cases": canonical},
            sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()
    return SyntheticBAssessment(input_sha256=digest, cases=tuple(typed), window_total=total)
