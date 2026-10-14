"""Pure, synthetic-only shared-cutoff news/price ordering probe for Phase IV.

No authentic source, baseline price cache, external I/O or scientific permissions.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, NoReturn, cast

SCHEMA = "dtrm.phase4.shared_cutoff_fixture.v0"
CASE_TAGS = frozenset(f"case_{i:02d}" for i in range(1, 65))
PRICE_TAGS = frozenset(f"price_{i:02d}" for i in range(1, 21))
TIMING = frozenset(("BEFORE", "AT_CUTOFF", "AFTER", "UNKNOWN"))
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


class SharedCutoffError(ValueError):
    """Sanitized invalid synthetic metadata boundary."""


def _reject() -> NoReturn:
    raise SharedCutoffError("INVALID_SYNTHETIC_SHARED_CUTOFF_FIXTURE")


def _exact(value: Any, keys: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject()
    return cast(dict[str, Any], value)


def _instant(value: Any, *, required: bool = False) -> datetime | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value or value.strip() != value:
        _reject()
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _reject()
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        _reject()
    return timestamp.astimezone(timezone.utc)


def _date_only(value: Any) -> str:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        _reject()
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _reject()
    if parsed.isoformat() != value:
        _reject()
    return value


def _utc(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value is not None else None


def _status(value: datetime | None, cutoff: datetime) -> str:
    if value is None:
        return "UNKNOWN"
    if value < cutoff:
        return "BEFORE"
    if value > cutoff:
        return "AFTER"
    return "AT_CUTOFF"


@dataclass(frozen=True, slots=True)
class PriceClockAssessment:
    dependency_tag: str
    first_availability: str
    vintage_availability: str

    def to_json(self) -> dict[str, str]:
        return {
            "dependency_tag": self.dependency_tag,
            "first_availability": self.first_availability,
            "vintage_availability": self.vintage_availability,
        }


@dataclass(frozen=True, slots=True)
class CaseClockAssessment:
    case_tag: str
    news_version: str
    news_link: str
    mapping: str
    price_dependencies: tuple[PriceClockAssessment, ...]
    conclusion: str

    def to_json(self) -> dict[str, Any]:
        return {
            "case_tag": self.case_tag,
            "news_version": self.news_version,
            "news_link": self.news_link,
            "mapping": self.mapping,
            "price_dependencies": [p.to_json() for p in self.price_dependencies],
            "conclusion": self.conclusion,
        }


@dataclass(frozen=True, slots=True)
class SharedCutoffAssessment:
    input_sha256: str
    cases: tuple[CaseClockAssessment, ...]
    synthetic_all_before: int

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": "dtrm.phase4.shared_cutoff_report.v0",
            "engineering_status": "PASS_SYNTHETIC_SHARED_CUTOFF_ORDERING",
            "scientific_status": "BLOCKED_CONTROL_CLOCK_ATTESTATION",
            "source_authenticated": False,
            "clock_authenticated": False,
            "dependency_completeness_authenticated": False,
            "history_construction_permitted": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "scientific_counting_permitted": False,
            "input_sha256": self.input_sha256,
            "case_count": len(self.cases),
            "synthetic_all_before": self.synthetic_all_before,
            "synthetic_blocked": len(self.cases) - self.synthetic_all_before,
            "cases": [c.to_json() for c in self.cases],
        }


def assess_shared_cutoff(fixture: Any) -> SharedCutoffAssessment:
    """Validate only invented metadata and compare normalized instants."""
    document = _exact(fixture, frozenset(("schema_version", "dataset_role", "cases")))
    if document["schema_version"] != SCHEMA or document["dataset_role"] != "synthetic":
        _reject()
    cases = document["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 64:
        _reject()
    typed: list[CaseClockAssessment] = []
    canon: list[dict[str, Any]] = []
    seen: set[str] = set()
    successes = 0
    for raw_case in cases:
        item = _exact(raw_case, frozenset((
            "case_tag", "decision_cutoff", "news_version_observed_at",
            "news_linked_at", "mapping_available_at", "price_dependencies",
        )))
        tag = item["case_tag"]
        if not isinstance(tag, str) or tag not in CASE_TAGS or tag in seen:
            _reject()
        seen.add(tag)
        cutoff = _instant(item["decision_cutoff"], required=True)
        if cutoff is None:
            _reject()
        news = _instant(item["news_version_observed_at"])
        link = _instant(item["news_linked_at"])
        mapping = _instant(item["mapping_available_at"])
        prices = item["price_dependencies"]
        if not isinstance(prices, list) or not 1 <= len(prices) <= 20:
            _reject()
        price_nodes: list[PriceClockAssessment] = []
        price_canon: list[dict[str, Any]] = []
        seen_prices: set[str] = set()
        for raw_price in prices:
            price = _exact(raw_price, frozenset((
                "dependency_tag", "price_session_date",
                "price_first_available_at", "price_vintage_available_at",
            )))
            name = price["dependency_tag"]
            if not isinstance(name, str) or name not in PRICE_TAGS or name in seen_prices:
                _reject()
            seen_prices.add(name)
            session_day = _date_only(price["price_session_date"])
            first = _instant(price["price_first_available_at"])
            vintage = _instant(price["price_vintage_available_at"])
            price_nodes.append(PriceClockAssessment(
                dependency_tag=name,
                first_availability=_status(first, cutoff),
                vintage_availability=_status(vintage, cutoff),
            ))
            price_canon.append({
                "dependency_tag": name,
                "price_session_date": session_day,
                "price_first_available_at": _utc(first),
                "price_vintage_available_at": _utc(vintage),
            })
        price_nodes.sort(key=lambda x: x.dependency_tag)
        price_canon.sort(key=lambda x: x["dependency_tag"])
        snews = _status(news, cutoff)
        slink = _status(link, cutoff)
        smapping = _status(mapping, cutoff)
        all_before = all(x == "BEFORE" for x in (snews, slink, smapping)) and all(
            p.first_availability == "BEFORE" and p.vintage_availability == "BEFORE"
            for p in price_nodes
        )
        if all_before:
            successes += 1
        typed.append(CaseClockAssessment(
            case_tag=tag,
            news_version=snews,
            news_link=slink,
            mapping=smapping,
            price_dependencies=tuple(price_nodes),
            conclusion="SYNTHETIC_ALL_BEFORE" if all_before else "SYNTHETIC_BLOCKED",
        ))
        canon.append({
            "case_tag": tag, "decision_cutoff": _utc(cutoff),
            "news_version_observed_at": _utc(news),
            "news_linked_at": _utc(link),
            "mapping_available_at": _utc(mapping),
            "price_dependencies": price_canon,
        })
    typed.sort(key=lambda x: x.case_tag)
    canon.sort(key=lambda x: x["case_tag"])
    normalized = {"schema_version": SCHEMA, "dataset_role": "synthetic", "cases": canon}
    digest = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return SharedCutoffAssessment(
        input_sha256=digest, cases=tuple(typed), synthetic_all_before=successes
    )
