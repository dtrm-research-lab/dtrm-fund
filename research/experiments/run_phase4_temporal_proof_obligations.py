"""Run a fixed, fictional Phase-IV temporal proof-obligation diagnostic.

No arbitrary source inputs, data files, AWS, FMP, Mongo, prices or models.
"""
from __future__ import annotations

import json

from dtrm.phase4.temporal_proof_obligations import (
    AvailabilityClaims,
    SyntheticWitness,
    build_synthetic_report,
)

CUTOFF = "2026-10-15T00:00:00Z"
PRIOR = "2026-10-14T20:00:00Z"
FUTURE = "2026-10-15T00:00:01Z"
PUBLISHED = "2026-10-13T10:00:00Z"
FAMILY = "family_fictional_x"


def fixed_fictional_witnesses() -> tuple[SyntheticWitness, ...]:
    """The only permitted dataset. Source values are fictional case tags."""
    missing = AvailabilityClaims(None, None, None, None)
    complete = AvailabilityClaims(
        PRIOR, PRIOR, PRIOR, PRIOR, True, True, True, True,
    )
    delayed_link = AvailabilityClaims(
        PRIOR, CUTOFF, PRIOR, PRIOR, True, True, True, True,
    )
    return (
        SyntheticWitness(
            "case_publication_only", FAMILY, CUTOFF, PUBLISHED, FUTURE, missing,
        ),
        SyntheticWitness(
            "case_archive_prior", FAMILY, CUTOFF, PUBLISHED, PRIOR, missing,
        ),
        SyntheticWitness(
            "case_future_link", FAMILY, CUTOFF, PUBLISHED, PRIOR, delayed_link,
        ),
        SyntheticWitness(
            "case_shape_complete", FAMILY, CUTOFF, PUBLISHED, PRIOR, complete,
        ),
        SyntheticWitness(
            "case_unknown_absence", "family_fictional_y",
            CUTOFF, PUBLISHED, None, missing,
        ),
    )


def main() -> int:
    report = build_synthetic_report(fixed_fictional_witnesses())
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
