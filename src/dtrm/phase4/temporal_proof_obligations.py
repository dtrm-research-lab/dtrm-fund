"""Synthetic-only Phase IV source-availability proof-obligation firewall.

This is an untrusted claim-shape analysis, NOT an external clock/rights verifier.
All scientific authority and model-fitting permissions remain permanently false.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Sequence

UTC_RE = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$")
TAG_RE = re.compile(r"^case_[a-z0-9_]{1,24}$")
FAMILY_RE = re.compile(r"^family_[a-z0-9_]{1,24}$")
ERROR = "BLOCKED_TEMPORAL_PROOF_INPUT"

ArchiveStatus = Literal["PRIOR_ARCHIVED_POSITIVE", "NO_PRE_CUTOFF_ARCHIVE"]
ProofStatus = Literal[
    "SYNTHETIC_PROOF_SHAPE_COMPLETE", "FUTURE_CLAIM", "INCOMPLETE_PROOF"
]


class ProofObligationError(ValueError):
    """Fixed error: never echo source claims, times or identifiers."""


def _stop() -> None:
    raise ProofObligationError(ERROR)


def _utc(value: str) -> datetime:
    if type(value) is not str or UTC_RE.fullmatch(value) is None:
        _stop()
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        _stop()
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _stop()
    return parsed.replace(tzinfo=timezone.utc)


@dataclass(frozen=True, slots=True)
class AvailabilityClaims:
    """Four hypothetical arrival clocks. Booleans are NOT real provider proof."""

    source_version_at: str | None
    link_mapping_at: str | None
    derived_state_at: str | None
    price_vintage_at: str | None
    source_receipt: bool = False
    link_receipt: bool = False
    derived_receipt: bool = False
    price_receipt: bool = False


@dataclass(frozen=True, slots=True)
class SyntheticWitness:
    case_tag: str
    family_tag: str
    decision_at: str
    published_at: str | None
    archived_positive_at: str | None
    claims: AvailabilityClaims


@dataclass(frozen=True, slots=True)
class ProofAssessment:
    case_tag: str
    family_tag: str
    archived_witness: ArchiveStatus
    proof_shape: ProofStatus
    historical_absence: Literal["UNKNOWN"] = "UNKNOWN"
    original_first_seen_authenticated: bool = False
    real_source_admission_permitted: bool = False


def assess_synthetic_witness(witness: SyntheticWitness) -> ProofAssessment:
    """Separate documented archive presence from hypothetical proof completeness."""
    if (
        type(witness) is not SyntheticWitness
        or TAG_RE.fullmatch(witness.case_tag) is None
        or FAMILY_RE.fullmatch(witness.family_tag) is None
        or type(witness.claims) is not AvailabilityClaims
    ):
        _stop()
    cutoff = _utc(witness.decision_at)
    if witness.published_at is not None:
        _utc(witness.published_at)
    prior_archive = (
        witness.archived_positive_at is not None
        and _utc(witness.archived_positive_at) < cutoff
    )
    clocks = (
        witness.claims.source_version_at,
        witness.claims.link_mapping_at,
        witness.claims.derived_state_at,
        witness.claims.price_vintage_at,
    )
    receipts = (
        witness.claims.source_receipt,
        witness.claims.link_receipt,
        witness.claims.derived_receipt,
        witness.claims.price_receipt,
    )
    if any(type(x) is not bool for x in receipts):
        _stop()
    if any(time is None and receipt for time, receipt in zip(clocks, receipts)):
        _stop()
    arrivals = tuple(_utc(time) if time is not None else None for time in clocks)
    # A future-claimed dependency takes precedence over missing evidence.
    if any(time is not None and time >= cutoff for time in arrivals):
        status: ProofStatus = "FUTURE_CLAIM"
    elif any(time is None for time in arrivals) or not all(receipts):
        status = "INCOMPLETE_PROOF"
    else:
        # The receipts here are synthetic assertions, not cryptographic authority.
        status = "SYNTHETIC_PROOF_SHAPE_COMPLETE"
    return ProofAssessment(
        case_tag=witness.case_tag,
        family_tag=witness.family_tag,
        archived_witness=(
            "PRIOR_ARCHIVED_POSITIVE" if prior_archive else "NO_PRE_CUTOFF_ARCHIVE"
        ),
        proof_shape=status,
    )


def build_synthetic_report(
    witnesses: Sequence[SyntheticWitness],
) -> dict[str, object]:
    """Aggregate closed fictional examples; never produce source-level admission."""
    if not 1 <= len(witnesses) <= 64:
        _stop()
    assessed = tuple(assess_synthetic_witness(w) for w in witnesses)
    if len({s.case_tag for s in assessed}) != len(assessed):
        _stop()
    by_case: list[dict[str, str]] = [
        {
            "case_tag": x.case_tag,
            "family_tag": x.family_tag,
            "archived_witness": x.archived_witness,
            "proof_shape": x.proof_shape,
            "historical_absence": x.historical_absence,
        }
        for x in sorted(assessed, key=lambda x: x.case_tag)
    ]
    return {
        "schema_version": "dtrm.phase4.temporal_proof_obligations.synthetic.v0",
        "dataset_role": "synthetic_fictional_noncounting",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "source_metadata_independently_authenticated": False,
        "historical_first_seen_authenticated": False,
        "negative_history_authenticated": False,
        "source_completeness_authenticated": False,
        "price_clock_authenticated": False,
        "rights_authenticated": False,
        "real_source_admission_permitted": False,
        "history_construction_permitted": False,
        "model_fitting_permitted": False,
        "outcomes_access_permitted": False,
        "mm1_execution_permitted": False,
        "scientific_counting_permitted": False,
        "sample_count": len(assessed),
        "prior_archived_positive_count": sum(
            s.archived_witness == "PRIOR_ARCHIVED_POSITIVE" for s in assessed
        ),
        "synthetic_shape_complete_count": sum(
            s.proof_shape == "SYNTHETIC_PROOF_SHAPE_COMPLETE" for s in assessed
        ),
        "future_claim_count": sum(
            s.proof_shape == "FUTURE_CLAIM" for s in assessed
        ),
        "unknown_historical_absence_count": len(assessed),
        "cases": by_case,
    }
