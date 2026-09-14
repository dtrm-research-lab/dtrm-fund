from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from dtrm.phase4.prospective_temporal_evidence import (
    FIRST_ARTIFACT_DIGEST,
    FIRST_LIVE_BACKEND_COMMIT,
    FIRST_LIVE_RUN,
    GRAPH,
    MIN_ACCEPTED_SLOTS,
    PARENT_INTEGRATION,
    PROVIDER_RIGHTS_STATUS,
    REGISTRATION_COMMIT,
    REPORT_SCHEMA,
    ROLES,
    SCHEDULE_UTC,
    SCIENTIFIC_STATUS,
    STATEMENT_SCHEMA,
    TARGET_SLOTS,
    ProspectiveTemporalEvidenceError,
    RoleSnapshot,
    SnapshotEntry,
    canonical_report_json,
    compare_snapshots,
    normalize_statement,
)

STATEMENT_PATH = Path(
    "research/contracts/DTRM_PHASE4_PROSPECTIVE_TEMPORAL_EVIDENCE_STATEMENT_V1.json"
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _entry(
    identity: str,
    payload: str,
    content: str,
    title: str,
    order_key: str | None,
) -> SnapshotEntry:
    return SnapshotEntry(
        _sha(identity),
        _sha(payload),
        _sha(content),
        _sha(title),
        order_key,
    )


def _statement() -> dict[str, object]:
    return json.loads(STATEMENT_PATH.read_text(encoding="utf-8"))


def test_statement_is_exact_and_blocks_activation() -> None:
    normalized = normalize_statement(_statement())
    data = normalized.to_dict()
    assert data["schema_version"] == STATEMENT_SCHEMA
    assert data["graph"] == GRAPH
    assert data["scientific_status"] == SCIENTIFIC_STATUS
    assert data["provider_rights_status"] == PROVIDER_RIGHTS_STATUS
    assert data["roles"] == list(ROLES)
    assert data["interval"] == {
        "schedule_utc": list(SCHEDULE_UTC),
        "target_slots": TARGET_SLOTS,
        "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
        "missing_slots_are_not_backfilled": True,
        "early_stopping_permitted": False,
    }
    permissions = data["permissions"]
    assert isinstance(permissions, dict)
    assert permissions["periodic_capture_activation_permitted"] is False
    assert permissions["outcome_access_permitted"] is False
    assert permissions["mm1_execution_permitted"] is False


def test_statement_anchor_is_bound_to_first_live_evidence() -> None:
    anchor = _statement()["anchor"]
    assert anchor == {
        "parent_integration": PARENT_INTEGRATION,
        "registration_commit": REGISTRATION_COMMIT,
        "first_live_backend_commit": FIRST_LIVE_BACKEND_COMMIT,
        "first_live_run": FIRST_LIVE_RUN,
        "first_artifact_digest": FIRST_ARTIFACT_DIGEST,
    }


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("interval", "target_slots"), 55),
        (("interval", "minimum_accepted_slots"), 47),
        (("permissions", "periodic_capture_activation_permitted"), True),
        (("permissions", "outcome_access_permitted"), True),
        (("request_plan", "limit"), 100),
        (("identity_policy",), "provider_id"),
    ],
)
def test_statement_rejects_silent_retuning(
    path: tuple[str, ...], value: object
) -> None:
    payload = deepcopy(_statement())
    cursor: object = payload
    for key in path[:-1]:
        assert isinstance(cursor, dict)
        cursor = cursor[key]
    assert isinstance(cursor, dict)
    cursor[path[-1]] = value
    with pytest.raises(ProspectiveTemporalEvidenceError):
        normalize_statement(payload)


def test_snapshot_rejects_duplicate_identity() -> None:
    entry = _entry("a", "p", "c", "t", None)
    with pytest.raises(ProspectiveTemporalEvidenceError, match="duplicate"):
        RoleSnapshot("general_latest", 1, (entry, entry))


def test_snapshot_rejects_invalid_digest_and_order_key() -> None:
    with pytest.raises(ProspectiveTemporalEvidenceError, match="sha256"):
        SnapshotEntry("not-a-digest", _sha("p"), _sha("c"), _sha("t"))
    with pytest.raises(ProspectiveTemporalEvidenceError, match="order key"):
        _entry("a", "p", "c", "t", "2026-09-13T10:00:00Z")


def test_transition_taxonomy_is_deterministic() -> None:
    previous = RoleSnapshot(
        "general_latest",
        0,
        (
            _entry("a", "pa1", "ca1", "ta1", "2026-09-13 15:00:00"),
            _entry("b", "pb1", "cb1", "tb1", "2026-09-13 14:00:00"),
            _entry("c", "pc1", "cc1", "tc1", "2026-09-13 13:00:00"),
        ),
    )
    current = RoleSnapshot(
        "general_latest",
        1,
        (
            _entry("d", "pd1", "cd1", "td1", "2026-09-13 12:00:00"),
            _entry("b", "pb2", "cb1", "tb2", "2026-09-13 14:00:00"),
            _entry("a", "pa2", "ca2", "ta1", "2026-09-13 15:00:00"),
            _entry("x", "px1", "cx1", "tx1", None),
        ),
    )
    historical_seen = frozenset({_sha("a"), _sha("b"), _sha("c"), _sha("x")})
    result = compare_snapshots(previous, current, historical_seen)
    assert result.retained_count == 2
    assert result.new_to_ledger_count == 1
    assert result.reappeared_count == 1
    assert result.window_absent_count == 1
    assert result.payload_revision_candidate_count == 2
    assert result.narrative_revision_candidate_count == 1
    assert result.metadata_revision_candidate_count == 1
    assert result.title_revision_candidate_count == 1
    assert result.rank_changed_count == 1
    assert result.publication_backfill_candidate_count == 1
    assert result.publication_order_violation_count == 2
    assert result.publication_unknown_count == 1
    assert result.absolute_rank_delta_sum == 2
    assert result.comparable_rank_pairs == 1
    assert result.inversion_count == 1
    assert result.inversion_rate == 1.0


def test_window_absence_is_not_encoded_as_deletion() -> None:
    previous = RoleSnapshot(
        "stock_latest",
        1,
        (_entry("a", "p1", "c1", "t1", "2026-09-13 15:00:00"),),
    )
    current = RoleSnapshot("stock_latest", 2, ())
    result = compare_snapshots(previous, current, frozenset({_sha("a")}))
    report = result.to_dict()
    assert report["window_absent_count"] == 1
    assert "deletion" not in json.dumps(report).lower()


def test_inversion_rate_handles_no_comparable_pairs() -> None:
    previous = RoleSnapshot(
        "fmp_articles", 0, (_entry("a", "p", "c", "t", None),)
    )
    current = RoleSnapshot(
        "fmp_articles", 1, (_entry("a", "p", "c", "t", None),)
    )
    result = compare_snapshots(previous, current, frozenset({_sha("a")}))
    assert result.comparable_rank_pairs == 0
    assert result.inversion_count == 0
    assert result.inversion_rate == 0.0


def test_transition_rejects_role_or_slot_mismatch() -> None:
    entry = _entry("a", "p", "c", "t", None)
    with pytest.raises(ProspectiveTemporalEvidenceError, match="role mismatch"):
        compare_snapshots(
            RoleSnapshot("fmp_articles", 0, (entry,)),
            RoleSnapshot("general_latest", 1, (entry,)),
            frozenset({_sha("a")}),
        )
    with pytest.raises(ProspectiveTemporalEvidenceError, match="non-increasing"):
        compare_snapshots(
            RoleSnapshot("fmp_articles", 2, (entry,)),
            RoleSnapshot("fmp_articles", 2, (entry,)),
            frozenset({_sha("a")}),
        )


def test_transition_rejects_history_that_omits_previous_snapshot() -> None:
    entry = _entry("a", "p", "c", "t", None)
    previous = RoleSnapshot("general_latest", 1, (entry,))
    current = RoleSnapshot("general_latest", 2, (entry,))
    with pytest.raises(
        ProspectiveTemporalEvidenceError,
        match="previous snapshot missing from historical ledger",
    ):
        compare_snapshots(previous, current, frozenset())


def test_report_is_aggregate_only_and_deterministic() -> None:
    previous = RoleSnapshot(
        "general_latest",
        0,
        (_entry("a", "p1", "c1", "t1", "2026-09-13 15:00:00"),),
    )
    current = RoleSnapshot(
        "general_latest",
        1,
        (_entry("a", "p2", "c2", "t1", "2026-09-13 15:00:00"),),
    )
    report_a = canonical_report_json(
        _statement(), previous, current, frozenset({_sha("a")})
    )
    report_b = canonical_report_json(
        deepcopy(_statement()), previous, current, frozenset({_sha("a")})
    )
    assert report_a == report_b
    parsed = json.loads(report_a)
    assert parsed["schema_version"] == REPORT_SCHEMA
    assert parsed["permissions"]["outcome_access_permitted"] is False
    assert "http" not in report_a.lower()
    assert "title-a" not in report_a
