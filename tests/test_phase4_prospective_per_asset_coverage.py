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
    commit_time: datetime | None = T - timedelta(hours=2),
    source_ok: bool = True,
    mapping_ok: bool = True,
    version: str = "v1",
    role: str = "fmp_articles",
) -> SyntheticLinkSighting:
    return SyntheticLinkSighting(
        name, version, role, version_time, link_time, commit_time, source_ok, mapping_ok
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
    r = classify([sight(link_time=T + timedelta(seconds=1), commit_time=T + timedelta(seconds=2))])
    assert r["history_category_structural_only"] == "ZERO_AUTHENTICATED"


def test_exact_cutoff_tie_is_unresolved_not_previous_information() -> None:
    r = classify([sight(link_time=T, commit_time=T)])
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
        sight(version="v2", link_time=T - timedelta(hours=1), commit_time=T - timedelta(hours=1)),
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


def test_t0_snapshot_does_not_backdate_old_news() -> None:
    t0 = T - timedelta(hours=1)
    # An old publication date is not part of the synthetic verified clock.
    # The *first attested* version and link observation is T0.
    record = sight(version_time=t0, link_time=t0, commit_time=t0 + timedelta(minutes=3))
    at_t0 = classify([record], cutoff=t0, complete=False)
    after_t0 = classify(
        [record], cutoff=t0 + timedelta(minutes=4), complete=False
    )
    assert at_t0["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert at_t0["structurally_admissible_distinct_events"] == 0
    assert after_t0["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert after_t0["structurally_admissible_distinct_events"] == 1
    assert "INCOMPLETE_CAPTURE_WINDOW" in after_t0["uncertainties"]
    assert after_t0["source_authenticated"] is False
    assert after_t0["temporal_state_training_permitted"] is False

def test_t0_uncommitted_is_unknown_no_positive_age() -> None:
    r = classify([sight(commit_time=None)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["UNKNOWN_COMMIT_CLOCK"]
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None


def test_t0_commit_exactly_at_cutoff_is_not_admissible() -> None:
    r = classify([sight(commit_time=T)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["UNRESOLVED_CUTOFF_TIE"]
    assert r["structurally_admissible_distinct_events"] == 0


def test_t0_commit_after_cutoff_cannot_be_admitted() -> None:
    r = classify([sight(commit_time=T + timedelta(seconds=1))])
    assert r["history_category_structural_only"] == "ZERO_AUTHENTICATED"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None


def test_bad_ledger_time_order_is_unknown_not_positive() -> None:
    r = classify([sight(commit_time=T - timedelta(hours=4))])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["uncertainties"] == ["UNRESOLVED_LEDGER_ORDER"]
    assert r["known_age_max_hours"] is None
    assert r["structurally_admissible_distinct_events"] == 0


def test_untrusted_provenance_never_emits_positive_age_or_role_count() -> None:
    r = classify([sight(source_ok=False, mapping_ok=False)])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None
    assert r["known_age_max_hours"] is None
    assert all(value == 0 for value in r["structural_roles"].values())


def test_ledger_commit_latest_in_age_calculation() -> None:
    r = classify([sight(commit_time=T - timedelta(minutes=30))])
    assert r["history_category_structural_only"] == "ONE_TO_FOUR"
    assert r["known_age_min_hours"] == 0.5
    assert r["known_age_max_hours"] == 0.5


def test_synthetic_flags_never_become_real_provenance() -> None:
    r = classify([sight(source_ok=True, mapping_ok=True)])
    assert r["source_authenticated"] is False
    assert r["mapping_authenticated"] is False
    assert r["scientific_counting_permitted"] is False


def test_invalid_sibling_suppresses_positive_event_counts_and_ages() -> None:
    r = classify([
        sight(version="v1"),
        sight(version="v2", link_time=None),
    ])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert "UNKNOWN_LINK_CLOCK" in r["uncertainties"]
    assert "UNRESOLVED_DUPLICATE_OR_REVISION" in r["uncertainties"]
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None
    assert r["known_age_max_hours"] is None
    assert all(n == 0 for n in r["structural_roles"].values())


def test_unauthorized_sibling_suppresses_entire_logical_event() -> None:
    r = classify([
        sight(version="v1"),
        sight(version="v2", mapping_ok=False),
    ])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None
    assert "UNKNOWN_MAPPING_PROVENANCE" in r["uncertainties"]


def test_cutoff_tied_sibling_quarantines_earlier_version() -> None:
    r = classify([
        sight(version="v1"),
        sight(version="v2", link_time=T, commit_time=T),
    ])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_max_hours"] is None
    assert "UNRESOLVED_CUTOFF_TIE" in r["uncertainties"]


def test_demonstrably_future_sibling_does_not_backdate_or_invalidate_v1() -> None:
    r = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=T + timedelta(seconds=2),
            link_time=T + timedelta(seconds=2),
            commit_time=T + timedelta(seconds=2),
        ),
    ])
    assert r["history_category_structural_only"] == "ONE_TO_FOUR"
    assert r["structurally_admissible_distinct_events"] == 1
    assert r["known_age_min_hours"] == 2


def test_future_only_source_sibling_with_missing_link_commit_is_ignored_asof() -> None:
    r = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=T + timedelta(seconds=1),
            link_time=None,
            commit_time=None,
        ),
    ])
    assert r["history_category_structural_only"] == "ONE_TO_FOUR"
    assert r["structurally_admissible_distinct_events"] == 1
    assert r["known_age_min_hours"] == 2
    assert r["uncertainties"] == []


def test_future_only_link_sibling_with_missing_version_commit_is_ignored_asof() -> None:
    r = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=None,
            link_time=T + timedelta(seconds=1),
            commit_time=None,
        ),
    ])
    assert r["history_category_structural_only"] == "ONE_TO_FOUR"
    assert r["structurally_admissible_distinct_events"] == 1
    assert r["known_age_min_hours"] == 2
    assert r["uncertainties"] == []


def test_untrusted_future_only_source_clock_does_not_resolve_sibling() -> None:
    r = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=T + timedelta(seconds=1),
            link_time=None,
            commit_time=None,
            source_ok=False,
        ),
    ])
    assert r["history_category_structural_only"] == "UNKNOWN_AVAILABILITY"
    assert r["structurally_admissible_distinct_events"] == 0
    assert r["known_age_min_hours"] is None
    assert "UNKNOWN_SOURCE_PROVENANCE" in r["uncertainties"]
    assert "UNRESOLVED_DUPLICATE_OR_REVISION" in r["uncertainties"]


def test_future_version_does_not_change_earlier_asof_report() -> None:
    earlier = classify([sight(version="v1")])
    with_future = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=T + timedelta(seconds=1),
            link_time=None,
            commit_time=None,
        ),
    ])
    assert with_future == earlier
    assert with_future["raw_synthetic_sightings"] == 1


def test_future_link_does_not_change_earlier_asof_report() -> None:
    earlier = classify([sight(version="v1")])
    with_future = classify([
        sight(version="v1"),
        sight(
            version="v2",
            version_time=None,
            link_time=T + timedelta(seconds=1),
            commit_time=None,
        ),
    ])
    assert with_future == earlier
    assert with_future["raw_synthetic_sightings"] == 1
