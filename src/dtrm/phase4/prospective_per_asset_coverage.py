"""Synthetic-only temporal admission preflight; never a trusted source/vintage verifier.

Design anchor: research/contracts/DTRM_PHASE4_PER_ASSET_PROSPECTIVE_COVERAGE_AND_CAPTURE_CLOCK_V0.md
No Mongo, AWS, file, clock reading, stock prices, model fitting or MM1 execution.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

SOURCE_ROLES = frozenset(("fmp_articles", "general_latest", "stock_latest"))
BINS = ("UNKNOWN_AVAILABILITY", "ZERO_AUTHENTICATED", "ONE_TO_FOUR",
        "FIVE_TO_NINETEEN", "TWENTY_PLUS")
SCHEMA_VERSION = "dtrm.phase4.per_asset_coverage_synthetic_preflight.v0"


class CoverageContractError(ValueError):
    """Redacted fixed error, never echoes original source identity or payload."""


@dataclass(frozen=True, slots=True)
class SyntheticLinkSighting:
    """Caller-provided *synthetic* source/link facts; booleans confer NO AWS trust."""

    logical_event_id: str
    content_version_id: str
    source_role: str
    version_observed_at: datetime | None
    linked_at: datetime | None
    ledger_committed_at: datetime | None
    source_provenance_supported: bool
    mapping_provenance_supported: bool


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise CoverageContractError("INVALID_UTC_CLOCK")
    if value.utcoffset() is None:
        raise CoverageContractError("INVALID_UTC_CLOCK")
    return value.astimezone(timezone.utc)


def _require_text(value: object) -> None:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise CoverageContractError("INVALID_SYNTHETIC_IDENTITY")


def classify_synthetic_asset_history(
    *,
    cutoff_utc: datetime,
    lookback_start_utc: datetime | None,
    complete_capture_window_claimed: bool,
    sightings: Sequence[SyntheticLinkSighting],
) -> dict[str, object]:
    """Fail-closed descriptive mechanics; never certify availability or training.

    The exact candidate manifest, chronology, true source provenance and NYSE
    decision schedule must be independently frozen before any real-data use.
    A caller-supplied True is NOT a trust root.
    """
    cutoff = _utc(cutoff_utc)
    start = _utc(lookback_start_utc)
    if cutoff is None or (start is not None and start >= cutoff):
        raise CoverageContractError("INVALID_DECISION_OR_LOOKBACK_CLOCK")
    if type(complete_capture_window_claimed) is not bool:
        raise CoverageContractError("INVALID_CAPTURE_COMPLETENESS")
    if not isinstance(sightings, (list, tuple)) or len(sightings) > 10000:
        raise CoverageContractError("INVALID_SYNTHETIC_SIGHTINGS")

    reasons: set[str] = set()
    if start is None:
        reasons.add("UNRESOLVED_LOOKBACK")
    if not complete_capture_window_claimed:
        reasons.add("INCOMPLETE_CAPTURE_WINDOW")

    by_event: dict[str, list[tuple[str, str, datetime]]] = {}
    unresolved_events: set[str] = set()
    raw_count = 0
    for rec in sightings:
        if not isinstance(rec, SyntheticLinkSighting):
            raise CoverageContractError("INVALID_SYNTHETIC_SIGHTINGS")
        _require_text(rec.logical_event_id)
        _require_text(rec.content_version_id)
        if rec.source_role not in SOURCE_ROLES:
            raise CoverageContractError("INVALID_SOURCE_ROLE")
        if type(rec.source_provenance_supported) is not bool or type(
            rec.mapping_provenance_supported
        ) is not bool:
            raise CoverageContractError("INVALID_SYNTHETIC_PROVENANCE_FLAG")
        observed = _utc(rec.version_observed_at)
        linked = _utc(rec.linked_at)
        committed = _utc(rec.ledger_committed_at)
        raw_count += 1
        # A supported future-only version/link never belonged to this cutoff.
        # Do not let its missing sibling fields contaminate earlier event history.
        if (
            (rec.source_provenance_supported and observed is not None and observed > cutoff)
            or (rec.mapping_provenance_supported and linked is not None and linked > cutoff)
        ):
            continue
        if not rec.source_provenance_supported:
            reasons.add("UNKNOWN_SOURCE_PROVENANCE")
        if not rec.mapping_provenance_supported:
            reasons.add("UNKNOWN_MAPPING_PROVENANCE")
        if observed is None:
            reasons.add("UNKNOWN_VERSION_CLOCK")
        if linked is None:
            reasons.add("UNKNOWN_LINK_CLOCK")
        if committed is None:
            reasons.add("UNKNOWN_COMMIT_CLOCK")
        if observed is None or linked is None or committed is None:
            unresolved_events.add(rec.logical_event_id)
            continue
        if committed < max(observed, linked):
            reasons.add("UNRESOLVED_LEDGER_ORDER")
            unresolved_events.add(rec.logical_event_id)
            continue
        if not rec.source_provenance_supported or not rec.mapping_provenance_supported:
            unresolved_events.add(rec.logical_event_id)
            continue
        effective = max(observed, linked, committed)
        if effective == cutoff:
            reasons.add("UNRESOLVED_CUTOFF_TIE")
            unresolved_events.add(rec.logical_event_id)
            continue
        if effective > cutoff:
            continue
        if start is None or effective < start:
            continue
        by_event.setdefault(rec.logical_event_id, []).append(
            (rec.content_version_id, rec.source_role, effective)
        )

    role_counts: Counter[str] = Counter()
    known_ages_hours: list[float] = []
    for event_id, versions in by_event.items():
        if event_id in unresolved_events:
            reasons.add("UNRESOLVED_DUPLICATE_OR_REVISION")
            continue
        # Genuine revision sequence + cross-role identity must be verified by
        # separate authenticated ledger. Never elect a favorable version here.
        if len(versions) != 1:
            reasons.add("UNRESOLVED_DUPLICATE_OR_REVISION")
            continue
        _, role, effective = versions[0]
        role_counts[role] += 1
        known_ages_hours.append(round((cutoff - effective).total_seconds() / 3600, 6))

    known_count = len(known_ages_hours)
    if reasons:
        category = "UNKNOWN_AVAILABILITY"
    elif known_count == 0:
        category = "ZERO_AUTHENTICATED"
    elif known_count < 5:
        category = "ONE_TO_FOUR"
    elif known_count < 20:
        category = "FIVE_TO_NINETEEN"
    else:
        category = "TWENTY_PLUS"
    assert category in BINS

    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_role": "synthetic_only",
        "engineering_status": "SYNTHETIC_ADMISSION_RULES_APPLIED",
        "history_category_structural_only": category,
        "raw_synthetic_sightings": raw_count,
        "structurally_admissible_distinct_events": known_count,
        "structural_roles": {role: role_counts[role] for role in sorted(SOURCE_ROLES)},
        "known_age_min_hours": min(known_ages_hours) if known_ages_hours else None,
        "known_age_max_hours": max(known_ages_hours) if known_ages_hours else None,
        "uncertainties": sorted(reasons),
        "source_authenticated": False,
        "mapping_authenticated": False,
        "actual_capture_window_authenticated": False,
        "scientific_counting_permitted": False,
        "temporal_state_training_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
    }
