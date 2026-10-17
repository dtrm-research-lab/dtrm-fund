"""Closed synthetic-only positive archive ledger, never real source time state."""

from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError

import pytest

from dtrm.phase4.archived_positive_ledger import (
    PositiveLedgerError,
    build_synthetic_positive_ledger,
)

FAMILY_A = "a" * 64
FAMILY_B = "b" * 64
ZIP_A = "1" * 64
ZIP_B = "2" * 64


def fixture() -> dict:
    return {
        "schema_version": "dtrm.phase4.archived_positive_ledger_fixture.v0",
        "dataset_role": "synthetic",
        "snapshots": [
            {
                "snapshot_tag": "snapshot_01",
                "family_sha256": FAMILY_A,
                "artifact_sha256": ZIP_A,
                "artifact_created_at": "2026-10-13T03:11:15Z",
                "positive_link_tags": ["link_01", "link_02"],
            },
            {
                "snapshot_tag": "snapshot_02",
                "family_sha256": FAMILY_A,
                "artifact_sha256": ZIP_B,
                "artifact_created_at": "2026-10-14T01:24:19Z",
                "positive_link_tags": ["link_01"],
            },
        ],
        "cutoffs": [
            "2026-10-13T03:11:15Z",
            "2026-10-13T03:11:16Z",
            "2026-10-14T01:24:19Z",
            "2026-10-14T01:24:20Z",
        ],
    }


def test_strict_cutoffs_and_positive_repetition() -> None:
    outcome = build_synthetic_positive_ledger(fixture()).to_json()
    rows = outcome["cutoffs"]
    assert [row["known_positive_archive_representations"] for row in rows] == [0, 2, 2, 2]
    assert [row["per_family"][0]["available_snapshot_count"] for row in rows] == [0, 1, 1, 2]
    assert [row["per_family"][0]["positive_witness_appearances"] for row in rows] == [0, 2, 2, 3]
    assert rows[-1]["per_family"][0]["most_recent_witness_age_seconds"] == 1
    assert rows[1]["per_family"][0]["most_recent_witness_age_seconds"] == 1
    assert rows[0]["per_family"][0]["most_recent_witness_age_seconds"] is None
    assert outcome["unknown_absence_cannot_be_inferred"] is True
    assert outcome["scientific_status"] == "BLOCKED_SOURCE_AUDIT"
    for gate in (
        "github_metadata_independently_authenticated",
        "original_link_first_seen_authenticated",
        "source_completeness_authenticated",
        "historical_absence_authenticated",
        "g5_lookback_frozen",
        "model_fitting_permitted",
        "outcome_access_permitted",
        "mm1_execution_permitted",
        "scientific_counting_permitted",
    ):
        assert outcome[gate] is False


def test_family_isolation_prevents_pseudo_unique_global_count() -> None:
    data = fixture()
    extra = copy.deepcopy(data["snapshots"][0])
    extra.update(
        snapshot_tag="snapshot_03", family_sha256=FAMILY_B,
        artifact_created_at="2026-10-13T04:00:00Z",
        positive_link_tags=["link_01"],
    )
    data["snapshots"].append(extra)
    data["cutoffs"] = ["2026-10-14T03:00:00Z"]
    row = build_synthetic_positive_ledger(data).to_json()["cutoffs"][0]
    assert len(row["per_family"]) == 2
    assert row["known_positive_archive_representations"] == 3
    assert row["cross_family_total_semantics"] == "SUM_OF_FAMILY_SPECIFIC_POSITIVE_COUNTS"


def test_unknown_missingness_does_not_become_zero_history() -> None:
    data = fixture()
    data["snapshots"][0]["positive_link_tags"] = []
    data["snapshots"][1]["positive_link_tags"] = []
    row = build_synthetic_positive_ledger(data).to_json()["cutoffs"][-1]
    assert row["known_positive_archive_representations"] == 0
    assert row["per_family"][0]["positive_witness_appearances"] == 0
    assert row["per_family"][0]["zero_witness_semantics"] == (
        "ZERO_WITNESSED_NOT_AUTHENTICATED_ZERO_HISTORY"
    )


def test_future_only_snapshots_cannot_leak_into_past_cutoff() -> None:
    data = fixture()
    data["cutoffs"] = ["2026-10-12T23:59:59Z"]
    result = build_synthetic_positive_ledger(data).to_json()["cutoffs"][0]
    assert result["known_positive_archive_representations"] == 0
    assert result["per_family"][0]["available_snapshot_count"] == 0


def test_timezone_permutation_and_immutable_output() -> None:
    data = fixture()
    base = build_synthetic_positive_ledger(data)
    other = copy.deepcopy(data)
    other["snapshots"].reverse()
    other["cutoffs"].reverse()
    other["snapshots"][0]["artifact_created_at"] = "2026-10-14T03:24:19+02:00"
    assert base == build_synthetic_positive_ledger(other)
    with pytest.raises(FrozenInstanceError):
        base.family_count = 99
    report = base.to_json()
    report["cutoffs"][0]["per_family"][0]["positive_witness_appearances"] = 99
    report["source_completeness_authenticated"] = True
    assert base.to_json()["source_completeness_authenticated"] is False
    assert base.to_json()["cutoffs"][0]["per_family"][0]["positive_witness_appearances"] == 0
    assert "link_01" not in str(base.to_json())
    assert "snapshot_01" not in str(base.to_json())


@pytest.mark.parametrize("mutation", [
    lambda x: x.update(dataset_role="real"),
    lambda x: x.update(returns=0.1),
    lambda x: x["snapshots"].clear(),
    lambda x: x["cutoffs"].clear(),
    lambda x: x["snapshots"].append(copy.deepcopy(x["snapshots"][0])),
    lambda x: x["snapshots"][0].update(snapshot_tag="tickerAAPL"),
    lambda x: x["snapshots"][0].update(snapshot_tag="snapshot_00"),
    lambda x: x["snapshots"][0].update(family_sha256="A" * 64),
    lambda x: x["snapshots"][0].update(artifact_sha256="invalid"),
    lambda x: x["snapshots"][0].update(artifact_created_at="2026-10-13"),
    lambda x: x["snapshots"][0].update(artifact_created_at="2026-10-13T03:11:15-00:00"),
    lambda x: x["snapshots"][0].update(artifact_created_at="0001-01-01T00:00:00+14:00"),
    lambda x: x["snapshots"][0].update(positive_link_tags=["  "]),
    lambda x: x["snapshots"][0].update(positive_link_tags=["link_01", "link_01"]),
    lambda x: x["snapshots"][0].update(positive_link_tags=["AAPL"]),
    lambda x: x["cutoffs"].append("2026-10-13T05:11:15+02:00"),
    lambda x: x["snapshots"][1].update(artifact_created_at="2026-10-13T03:11:15Z"),
    lambda x: x["snapshots"][0].update(source_url="https://private.invalid"),
])
def test_all_untrusted_or_invalid_input_fail_closed(mutation) -> None:
    bad = fixture()
    mutation(bad)
    with pytest.raises(PositiveLedgerError, match="^INVALID_PHASE4_SYNTHETIC_ARCHIVE_LEDGER$"):
        build_synthetic_positive_ledger(bad)
