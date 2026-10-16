"""No source, provider or model access: synthetic observed/link clock tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from dtrm.phase4.prospective_per_asset_coverage import (
    CoverageContractError,
    SyntheticLinkSighting,
    classify_synthetic_asset_history,
)

T = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
START = T - timedelta(days=7)


def sight(
    name: str = "synthetic-event",
    *,
    version_time: datetime | None = T - timedelta(hours=3),
    link_time: datetime | None = T - timedelta(hours=2),
    source_ok: bool = True,
    mapping_ok: bool = True,
    version: str = "v1",
    role: str = "fmp_articles",
) -> SyntheticLinkSighting:
    return SyntheticLinkSighting(
        name, version, role, version_time, link_time, source_ok, mapping_ok
    )


def classify(
    records: list[SyntheticLinkSighting],
    *,
    cutoff: datetime = T,
    lookback: datetime | None = START,
    complete: bool = True,
) -> dict[str, object]:
    return classify_synthetic_asset_history(
        cutoff_utc=cutoff,
        lookback_start_utc=lookback,
        complete_capture_window_claimed=complete,
        sightings=records,
    )


def test_unknown_zero_is_not_trusted_without_complete_window() -> None:
    r = classify([], complete=False)
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["INCOMPLETE_CAPTURE_WINDOW"]
    assert r["temporal_state_training_permitted"] is False
    assert r["source_authenticated"] is False
    assert r["actual_capture_window_authenticated"] is False


def test_known_zero_only_structural_not_authentication() -> None:
    r = classify([])
    assert r["history_category_structural_only"] == "ZERO_AUTHENTICATED"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["source_authenticated"] is False


def test_link_time_dominates_version_clock_and_age() -> None:
    r = classify([sight()])
    assert r["history_category_structural_only"] == "ONE_TO_FOUR"
    assert r["structurally_admissible_distinct_events"] == 1
    assert r["known_age_min_hours"] == 2
    assert r["known_age_max_hours"] == 2


def test_future_link_cannot_retroactively_admit_past_content() -> None:
    r = classify([sight(link_time=T + timedelta(seconds=1))])
    assert r["history_category_structural_only"] == "ZERO_AUTHENTICATED"


def test_exact_cutoff_tie_is_unresolved_not_previous_information() -> None:
    r = classify([sight(link_time=T)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["UNRESOLVED_CUTOFF_TIE"]


def test_missing_link_is_unknown_not_empty_history() -> None:
    r = classify([sight(link_time=None)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["UNKNOWN_LINK_CLOCK"]


def test_missing_version_clock_is_unknown() -> None:
    r = classify([sight(version_time=None)])
    assert r["uncertainties"] == ["UNKNOWN_VERSION_CLOCK"]


def test_unverified_mapping_or_source_is_unknown() -> None:
    r = classify([sight(source_ok=False, mapping_ok=False)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == [
        "UNKNOWN_MAPPING_PROVENANCE", "UNKNOWN_SOURCE_PROVENANCE"
    ]


def test_duplicate_or_revision_without_trusted_chain_not_double_counted() -> None:
    r = classify([
        sight(version="v1"),
        sight(version="v2", link_time=T - timedelta(hours=1)),
    ])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["uncertainties"] == ["UNRESOLVED_DUPLICATE_OR_REVISION"]


def test_pinned_window_required_and_no_implicit_sixty_day_lookback() -> None:
    r = classify([sight()], lookback=None)
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert "UNRESOLVED_LOOKBACK" in r["uncertainties"]


@pytest.mark.parametrize(
    ("n", "bucket"),
    [
        (1, "ONE_TO_FOUR"),
        (4, "ONE_TO_FOUR"),
        (5, "FIVE_TO_NINETEEN"),
        (19, "FIVE_TO_NINETEEN"),
        (20, "TWENTY_PLUS"),
    ],
)
def test_preregistered_history_bins(n: int, bucket: str) -> None:
    r = classify([sight(name=f"synthetic-{i}") for i in range(n)])
    assert r["history_category_structural_only"] == bucket
    assert r["structurally_admissible_distinct_events"] == n


@pytest.mark.parametrize("clock", [T.replace(tzinfo=None), None])
def test_invalid_naive_or_missing_decision_clock(clock: datetime | None) -> None:
    with pytest.raises(CoverageContractError, match="INVALID_"):
        classify_synthetic_asset_history(
            cutoff_utc=clock,  # type: ignore[arg-type]
            lookback_start_utc=START,
            complete_capture_window_claimed=True,
            sightings=[],
        )


def test_no_source_values_or_ticker_identities_appear_in_report() -> None:
    r = classify([sight(name="synthetic-sensitive-identity")])
    s = repr(r)
    assert "synthetic-sensitive-identity" not in s
    assert "source_authenticated': False" in s


def test_market_calendar_not_inferred_from_capture_slot() -> None:
    r = classify([sight()])
    assert not any(
        "session" in key or "market_day" in key or "calendar" in key
        for key in r
    )
