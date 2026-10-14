"""Synthetic-only Phase IV history-coverage arithmetic; never authenticates sources."""

from __future__ import annotations

import hashlib
import json
import re
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
TAG_RE = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")


class PreflightError(ValueError):
    """Fail-closed without exposing input data."""


def _reject() -> None:
    raise PreflightError("INVALID_SYNTHETIC_HISTORY_FIXTURE")


def _exact_keys(value: Any, keys: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _reject()
    return cast(dict[str, Any], value)


def _strict_counter(value: Any, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value <= MAX_CANDIDATES:
        _reject()
    return cast(int, value)


def assess_synthetic_coverage(fixture: Any) -> dict[str, Any]:
    """Check arithmetic of *synthetic* disjoint count bins, never raw events."""
    document = _exact_keys(fixture, frozenset(("schema_version", "dataset_role", "cohorts")))
    if document["schema_version"] != SCHEMA or document["dataset_role"] != "synthetic":
        _reject()
    cohorts = document["cohorts"]
    if not isinstance(cohorts, list) or not 1 <= len(cohorts) <= MAX_COHORTS:
        _reject()

    canonical: list[dict[str, Any]] = []
    seen: set[str] = set()
    grand = {key: 0 for key in BINS}
    total = 0
    for item in cohorts:
        cohort = _exact_keys(item, frozenset(("cohort_tag", "candidate_count", "bins")))
        tag = cohort["cohort_tag"]
        if not isinstance(tag, str) or not TAG_RE.fullmatch(tag) or tag in seen:
            _reject()
        seen.add(tag)
        n = _strict_counter(cohort["candidate_count"], minimum=1)
        raw_bins = _exact_keys(cohort["bins"], frozenset(BINS))
        counts = {key: _strict_counter(raw_bins[key]) for key in BINS}
        if sum(counts.values()) != n:
            _reject()
        total += n
        if total > MAX_CANDIDATES:
            _reject()
        for key in BINS:
            grand[key] += counts[key]
        canonical.append({"cohort_tag": tag, "candidate_count": n, "bins": counts})
    canonical.sort(key=lambda item: item["cohort_tag"])
    normalized = {"schema_version": SCHEMA, "dataset_role": "synthetic", "cohorts": canonical}
    digest = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return {
        "schema_version": "dtrm.phase4.history_sufficiency_report.v0",
        "engineering_status": "PASS_SYNTHETIC_HISTORY_COUNTERS",
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "source_authenticated": False,
        "history_construction_permitted": False,
        "training_permitted": False,
        "outcome_access_permitted": False,
        "scientific_counting_permitted": False,
        "input_sha256": digest,
        "cohort_count": len(canonical),
        "candidate_total": total,
        "bins_total": grand,
        "cohorts": canonical,
    }


def run_cli(argv: list[str] | None = None) -> int:
    """Separate local file boundary with exclusive output creation."""
    import argparse

    parser = argparse.ArgumentParser(description="Synthetic-only Phase IV arithmetic checker")
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # Never follow an existing output path, including symlinks.
        if args.output.is_symlink() or args.output.exists():
            raise PreflightError("OUTPUT_EXISTS")
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        result = assess_synthetic_coverage(fixture)
        encoded = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
        with args.output.open("xb") as handle:
            handle.write(encoded)
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, PreflightError) and str(exc) == "OUTPUT_EXISTS":
            parser.error("OUTPUT_EXISTS")
        parser.error("INVALID_SYNTHETIC_HISTORY_FIXTURE_OR_IO")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
