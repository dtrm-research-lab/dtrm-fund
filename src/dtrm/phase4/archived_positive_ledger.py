"""Synthetic-only, positive archive observation ledger; no real source admission.

A selected archived witness establishes positive representation by its capture
instant, NEVER historical source first-seen or proof of absence from a ZIP.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import NoReturn, cast

SCHEMA = "dtrm.phase4.archived_positive_ledger_fixture.v0"
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
CLOCK_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z"
)
SNAPSHOT_TAGS = frozenset(f"snapshot_{n:02d}" for n in range(1, 65))
LINK_TAGS = frozenset(f"link_{n:02d}" for n in range(1, 65))


class PositiveLedgerError(ValueError):
    """Fixed fail-closed domain error; no private or original source values."""


def _reject() -> NoReturn:
    raise PositiveLedgerError("INVALID_PHASE4_SYNTHETIC_ARCHIVE_LEDGER")


def _sha(value: object) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        _reject()
    return value


def _clock(value: object) -> datetime:
    if (
        not isinstance(value, str) or not CLOCK_RE.fullmatch(value)
        or value.endswith("-00:00")
    ):
        _reject()
    try:
        time = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if time.tzinfo is None or time.utcoffset() is None:
            _reject()
        return time.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        _reject()


def _iso(clock: datetime) -> str:
    return clock.isoformat().replace("+00:00", "Z")


def _exact(data: object, keys: frozenset[str]) -> dict[str, object]:
    if not isinstance(data, dict) or set(data) != keys:
        _reject()
    return cast(dict[str, object], data)


@dataclass(frozen=True, slots=True)
class _Witness:
    family_sha256: str
    observed_at: datetime
    links: frozenset[str]


@dataclass(frozen=True, slots=True)
class FamilyState:
    family_sha256: str
    available_snapshot_count: int
    positive_witness_appearances: int
    witnessed_distinct_link_tags: int
    most_recent_witness_age_seconds: int | None

    def to_json(self) -> dict[str, object]:
        return {
            "family_sha256": self.family_sha256,
            "available_snapshot_count": self.available_snapshot_count,
            "positive_witness_appearances": self.positive_witness_appearances,
            "witnessed_distinct_link_tags": self.witnessed_distinct_link_tags,
            "most_recent_witness_age_seconds": self.most_recent_witness_age_seconds,
            "nonobserved_link_state": "UNKNOWN_SELECTED_EXPORT",
            "zero_witness_semantics": "ZERO_WITNESSED_NOT_AUTHENTICATED_ZERO_HISTORY",
        }


@dataclass(frozen=True, slots=True)
class CutoffState:
    decision_cutoff: str
    known_positive_archive_representations: int
    per_family: tuple[FamilyState, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "decision_cutoff": self.decision_cutoff,
            "known_positive_archive_representations": (
                self.known_positive_archive_representations
            ),
            "cross_family_total_semantics": "SUM_OF_FAMILY_SPECIFIC_POSITIVE_COUNTS",
            "per_family": [state.to_json() for state in self.per_family],
        }


@dataclass(frozen=True, slots=True)
class SyntheticPositiveLedger:
    snapshots_seen: int
    family_count: int
    states: tuple[CutoffState, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "schema_version": "dtrm.phase4.archived_positive_ledger_report.v0",
            "engineering_status": "PASS_SYNTHETIC_POSITIVE_ARCHIVE_LEDGER_MECHANICS",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "dataset_role": "synthetic_only",
            "github_metadata_independently_authenticated": False,
            "original_link_first_seen_authenticated": False,
            "source_completeness_authenticated": False,
            "historical_absence_authenticated": False,
            "unknown_absence_cannot_be_inferred": True,
            "g5_lookback_frozen": False,
            "model_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "scientific_counting_permitted": False,
            "snapshots_seen": self.snapshots_seen,
            "family_count": self.family_count,
            "cutoffs": [state.to_json() for state in self.states],
        }


def build_synthetic_positive_ledger(raw: object) -> SyntheticPositiveLedger:
    """Only report counts of strictly earlier *positive archival representation*."""
    doc = _exact(raw, frozenset(("schema_version", "dataset_role", "snapshots", "cutoffs")))
    if doc["schema_version"] != SCHEMA or doc["dataset_role"] != "synthetic":
        _reject()
    snapshots = doc["snapshots"]
    raw_cutoffs = doc["cutoffs"]
    if (
        not isinstance(snapshots, list) or not 1 <= len(snapshots) <= 64
        or not isinstance(raw_cutoffs, list) or not 1 <= len(raw_cutoffs) <= 64
    ):
        _reject()
    seen_tags: set[str] = set()
    seen_times: set[datetime] = set()
    witnessed: list[_Witness] = []
    for obj in snapshots:
        row = _exact(
            obj,
            frozenset((
                "snapshot_tag", "family_sha256", "artifact_sha256",
                "artifact_created_at", "positive_link_tags",
            )),
        )
        tag = row["snapshot_tag"]
        if (
            not isinstance(tag, str) or tag not in SNAPSHOT_TAGS
            or tag in seen_tags
        ):
            _reject()
        seen_tags.add(tag)
        family = _sha(row["family_sha256"])
        _sha(row["artifact_sha256"])
        observed = _clock(row["artifact_created_at"])
        if observed in seen_times:
            _reject()
        seen_times.add(observed)
        links = row["positive_link_tags"]
        if not isinstance(links, list) or len(links) > 64:
            _reject()
        if any(not isinstance(link, str) or link not in LINK_TAGS for link in links):
            _reject()
        normalized = frozenset(cast(list[str], links))
        if len(normalized) != len(links):
            _reject()
        witnessed.append(_Witness(family, observed, normalized))
    cutoffs = [_clock(c) for c in raw_cutoffs]
    if len(set(cutoffs)) != len(cutoffs):
        _reject()
    families = sorted({w.family_sha256 for w in witnessed})
    result: list[CutoffState] = []
    for cutoff in sorted(cutoffs):
        per_family: list[FamilyState] = []
        for family in families:
            available = [
                row for row in witnessed
                if row.family_sha256 == family and row.observed_at < cutoff
            ]
            unique: set[str] = set()
            latest_nonempty: datetime | None = None
            appearances = 0
            for snapshot in available:
                unique.update(snapshot.links)
                appearances += len(snapshot.links)
                if snapshot.links and (
                    latest_nonempty is None or snapshot.observed_at > latest_nonempty
                ):
                    latest_nonempty = snapshot.observed_at
            age = None
            if latest_nonempty is not None:
                delta = cutoff - latest_nonempty
                age = delta.days * 86400 + delta.seconds
            per_family.append(FamilyState(
                family, len(available), appearances, len(unique), age,
            ))
        result.append(CutoffState(
            _iso(cutoff),
            sum(row.witnessed_distinct_link_tags for row in per_family),
            tuple(per_family),
        ))
    return SyntheticPositiveLedger(
        len(witnessed), len(families), tuple(result),
    )
