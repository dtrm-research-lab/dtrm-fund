"""Synthetic-only Phase IV history-coverage arithmetic; never authenticates sources."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

SCHEMA = "dtrm.phase4.history_sufficiency_fixture.v0"
BINS = (
    "unknown_availability",
    "zero",
    "one_to_four",
    "five_to_nineteen",
    "twenty_plus",
)
MAX_COHORTS = 64
MAX_CANDIDATES = 1_000_000
SYNTHETIC_TAGS = frozenset(f"case_{number:02d}" for number in range(1, MAX_COHORTS + 1))
BinCounts = tuple[int, int, int, int, int]


class PreflightError(ValueError):
    """Fail-closed without exposing input data."""


def _reject() -> None:
    raise PreflightError("INVALID_SYNTHETIC_HISTORY_FIXTURE")


@dataclass(frozen=True, slots=True)
class SyntheticCohort:
    """Immutable aggregate for an invented synthetic case, never a real ticker."""

    cohort_tag: str
    candidate_count: int
    bin_counts: BinCounts

    def to_json(self) -> dict[str, Any]:
        """Allocate fresh serializable values; do not expose internal mutable state."""
        return {
            "cohort_tag": self.cohort_tag,
            "candidate_count": self.candidate_count,
            "bins": dict(zip(BINS, self.bin_counts, strict=True)),
        }


@dataclass(frozen=True, slots=True)
class SyntheticCoverageAssessment:
    """Immutable domain result; constant scientific non-authorizations."""

    input_sha256: str
    cohorts: tuple[SyntheticCohort, ...]
    candidate_total: int
    grand_counts: BinCounts

    def to_json(self) -> dict[str, Any]:
        """Serialization belongs to the outer boundary, not the domain state."""
        return {
            "schema_version": "dtrm.phase4.history_sufficiency_report.v0",
            "engineering_status": "PASS_SYNTHETIC_HISTORY_COUNTERS",
            "scientific_status": "BLOCKED_SOURCE_AUDIT",
            "source_authenticated": False,
            "history_construction_permitted": False,
            "training_permitted": False,
            "outcome_access_permitted": False,
            "scientific_counting_permitted": False,
            "input_sha256": self.input_sha256,
            "cohort_count": len(self.cohorts),
            "candidate_total": self.candidate_total,
            "bins_total": dict(zip(BINS, self.grand_counts, strict=True)),
            "cohorts": [cohort.to_json() for cohort in self.cohorts],
        }


def _exact_keys(value: Any, keys: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject()
    return cast(dict[str, Any], value)


def _strict_counter(value: Any, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value <= MAX_CANDIDATES:
        _reject()
    return cast(int, value)


def _unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys before nested fields can be silently collapsed."""
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            _reject()
        obj[key] = value
    return obj


def assess_synthetic_coverage(fixture: Any) -> SyntheticCoverageAssessment:
    """Check synthetic count arithmetic. No as-of historical claim is made."""
    document = _exact_keys(fixture, frozenset(("schema_version", "dataset_role", "cohorts")))
    if document["schema_version"] != SCHEMA or document["dataset_role"] != "synthetic":
        _reject()
    cohorts = document["cohorts"]
    if not isinstance(cohorts, list) or not 1 <= len(cohorts) <= MAX_COHORTS:
        _reject()

    canonical: list[SyntheticCohort] = []
    seen: set[str] = set()
    grand = [0] * len(BINS)
    total = 0
    for item in cohorts:
        cohort = _exact_keys(item, frozenset(("cohort_tag", "candidate_count", "bins")))
        tag = cohort["cohort_tag"]
        if not isinstance(tag, str) or tag not in SYNTHETIC_TAGS or tag in seen:
            _reject()
        seen.add(tag)
        n = _strict_counter(cohort["candidate_count"], minimum=1)
        raw_bins = _exact_keys(cohort["bins"], frozenset(BINS))
        counts = cast(BinCounts, tuple(_strict_counter(raw_bins[key]) for key in BINS))
        if sum(counts) != n:
            _reject()
        total += n
        if total > MAX_CANDIDATES:
            _reject()
        for index, count in enumerate(counts):
            grand[index] += count
        canonical.append(SyntheticCohort(tag, n, counts))
    canonical.sort(key=lambda item: item.cohort_tag)
    state = tuple(canonical)
    normalized = {
        "schema_version": SCHEMA,
        "dataset_role": "synthetic",
        "cohorts": [cohort.to_json() for cohort in state],
    }
    digest = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return SyntheticCoverageAssessment(
        input_sha256=digest,
        cohorts=state,
        candidate_total=total,
        grand_counts=cast(BinCounts, tuple(grand)),
    )


def run_cli(argv: list[str] | None = None) -> int:
    """Separate local file boundary with exclusive output creation."""
    import argparse

    parser = argparse.ArgumentParser(description="Synthetic-only Phase IV arithmetic checker")
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # "xb" prevents replacing a file even across a time-of-check race.
        if args.output.is_symlink() or args.output.exists():
            raise PreflightError("OUTPUT_EXISTS")
        fixture = json.loads(
            args.fixture.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object_pairs,
        )
        result = assess_synthetic_coverage(fixture)
        encoded = (json.dumps(result.to_json(), sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode(
            "utf-8"
        )
        # Stage in the same directory; publish only fully flushed bytes.
        # An atomic hard link will never overwrite an existing destination.
        temp_path: Path | None = None
        staged_fd: int | None = None
        try:
            fd, temp_name = tempfile.mkstemp(
                prefix=".phase4-history-", suffix=".tmp", dir=args.output.parent
            )
            staged_fd = fd
            temp_path = Path(temp_name)
            with os.fdopen(fd, "wb") as handle:
                staged_fd = None
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temp_path, args.output)
        finally:
            if staged_fd is not None:
                os.close(staged_fd)
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, PreflightError) and str(exc) == "OUTPUT_EXISTS":
            parser.error("OUTPUT_EXISTS")
        parser.error("INVALID_SYNTHETIC_HISTORY_FIXTURE_OR_IO")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
