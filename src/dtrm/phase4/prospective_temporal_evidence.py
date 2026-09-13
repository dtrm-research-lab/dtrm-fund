"""Pure Phase-IV prospective temporal evidence v1 contract and transition graph."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_prospective_temporal_evidence_v1"
STATEMENT_SCHEMA = "dtrm.phase4.prospective_temporal_evidence.v1"
REPORT_SCHEMA = "dtrm.phase4.prospective_temporal_evidence_report.v1"
ENGINEERING_STATUS = "PASS_PROSPECTIVE_TEMPORAL_EVIDENCE_V1"
SCIENTIFIC_STATUS = "REGISTERED_REPEATED_SOURCE_EVIDENCE"
PROVIDER_RIGHTS_STATUS = "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"

PARENT_INTEGRATION = "281ab0ce2de40128f2d2c8258cfff94fc91d8695"
REGISTRATION_COMMIT = "243797ee398b43f6684ce7a43057711167ed79ba"
FIRST_LIVE_BACKEND_COMMIT = "79e8d3da1a337141f9097f0b79d45d2de78878c0"
FIRST_LIVE_RUN = 34777031881
FIRST_ARTIFACT_DIGEST = (
    "sha256:661d8b9b701af85655a14ad49f54dd9c48634ff83411fe0cd8ed94f50b8644b5"
)
REQUEST_FINGERPRINT = "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"

ROLES = ("fmp_articles", "general_latest", "stock_latest")
SCHEDULE_UTC = ("00:15", "06:15", "12:15", "18:15")
TARGET_SLOTS = 56
MIN_ACCEPTED_SLOTS = 48
MAX_ROLE_ITEMS = 40
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ORDER_KEY_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

JsonObject = dict[str, object]


class ProspectiveTemporalEvidenceError(ValueError):
    """The v1 evidence contract or transition input is invalid."""


def _expected_request_plan() -> JsonObject:
    return {
        "labels": ["page0_a", "page1", "page0_b"],
        "limit": 20,
        "snapshot_labels": ["page0_a", "page1"],
        "max_role_items": MAX_ROLE_ITEMS,
        "request_fingerprint_sha256": REQUEST_FINGERPRINT,
    }


def _expected_permissions() -> JsonObject:
    return {
        "synthetic_transition_classifier_permitted": True,
        "backend_index_builder_implementation_permitted": True,
        "scheduled_workflow_configuration_permitted": True,
        "periodic_capture_activation_permitted": False,
        "confirmatory_history_construction_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
        "public_raw_provider_data_redistribution_permitted": False,
    }


def _expected_anchor() -> JsonObject:
    return {
        "parent_integration": PARENT_INTEGRATION,
        "registration_commit": REGISTRATION_COMMIT,
        "first_live_backend_commit": FIRST_LIVE_BACKEND_COMMIT,
        "first_live_run": FIRST_LIVE_RUN,
        "first_artifact_digest": FIRST_ARTIFACT_DIGEST,
    }


def _expected_interval() -> JsonObject:
    return {
        "schedule_utc": list(SCHEDULE_UTC),
        "target_slots": TARGET_SLOTS,
        "minimum_accepted_slots": MIN_ACCEPTED_SLOTS,
        "missing_slots_are_not_backfilled": True,
        "early_stopping_permitted": False,
    }


def _require_exact_object(value: object, expected: JsonObject, label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ProspectiveTemporalEvidenceError(f"{label}: expected object")
    mapping = cast(JsonObject, value)
    if set(mapping) != set(expected):
        raise ProspectiveTemporalEvidenceError(f"{label}: unexpected keys")
    for key, expected_value in expected.items():
        actual = mapping[key]
        if type(actual) is not type(expected_value) or actual != expected_value:
            raise ProspectiveTemporalEvidenceError(f"{label}.{key}: registered value mismatch")
    return dict(mapping)


@dataclass(frozen=True, slots=True)
class NormalizedTemporalEvidenceStatement:
    canonical_json: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json.encode("utf-8")).hexdigest()

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


def normalize_statement(payload: object) -> NormalizedTemporalEvidenceStatement:
    if not isinstance(payload, dict):
        raise ProspectiveTemporalEvidenceError("statement: expected object")
    root = cast(JsonObject, payload)
    expected_keys = {
        "schema_version",
        "graph",
        "scientific_status",
        "provider_rights_status",
        "roles",
        "anchor",
        "interval",
        "request_plan",
        "identity_policy",
        "permissions",
    }
    if set(root) != expected_keys:
        raise ProspectiveTemporalEvidenceError("statement: unexpected keys")
    fixed = {
        "schema_version": STATEMENT_SCHEMA,
        "graph": GRAPH,
        "scientific_status": SCIENTIFIC_STATUS,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "identity_policy": "exact_url_sha256_fragment_removed_only",
    }
    for key, value in fixed.items():
        if root[key] != value:
            raise ProspectiveTemporalEvidenceError(f"{key}: registered value mismatch")
    if root["roles"] != list(ROLES):
        raise ProspectiveTemporalEvidenceError("roles: registered value mismatch")
    _require_exact_object(root["anchor"], _expected_anchor(), "anchor")
    _require_exact_object(root["interval"], _expected_interval(), "interval")
    _require_exact_object(root["request_plan"], _expected_request_plan(), "request_plan")
    _require_exact_object(root["permissions"], _expected_permissions(), "permissions")
    canonical = json.dumps(root, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return NormalizedTemporalEvidenceStatement(canonical)


@dataclass(frozen=True, slots=True)
class SnapshotEntry:
    source_event_id: str
    payload_sha256: str
    content_sha256: str
    title_sha256: str
    provider_order_key: str | None = None

    def __post_init__(self) -> None:
        for value in (
            self.source_event_id,
            self.payload_sha256,
            self.content_sha256,
            self.title_sha256,
        ):
            if SHA256_RE.fullmatch(value) is None:
                raise ProspectiveTemporalEvidenceError("entry: invalid sha256")
        if self.provider_order_key is not None and ORDER_KEY_RE.fullmatch(
            self.provider_order_key
        ) is None:
            raise ProspectiveTemporalEvidenceError("entry: invalid provider order key")


@dataclass(frozen=True, slots=True)
class RoleSnapshot:
    role: str
    slot: int
    entries: tuple[SnapshotEntry, ...]

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ProspectiveTemporalEvidenceError("snapshot: invalid role")
        if type(self.slot) is not int or self.slot < 0:
            raise ProspectiveTemporalEvidenceError("snapshot: invalid slot")
        if len(self.entries) > MAX_ROLE_ITEMS:
            raise ProspectiveTemporalEvidenceError("snapshot: too many entries")
        identities = tuple(entry.source_event_id for entry in self.entries)
        if len(set(identities)) != len(identities):
            raise ProspectiveTemporalEvidenceError("snapshot: duplicate logical identity")


@dataclass(frozen=True, slots=True)
class TransitionAssessment:
    role: str
    previous_slot: int
    current_slot: int
    previous_count: int
    current_count: int
    retained_count: int
    new_to_ledger_count: int
    reappeared_count: int
    window_absent_count: int
    payload_revision_candidate_count: int
    narrative_revision_candidate_count: int
    metadata_revision_candidate_count: int
    title_revision_candidate_count: int
    rank_changed_count: int
    publication_backfill_candidate_count: int
    publication_order_violation_count: int
    publication_unknown_count: int
    absolute_rank_delta_sum: int
    comparable_rank_pairs: int
    inversion_count: int
    inversion_rate: float

    def to_dict(self) -> JsonObject:
        return {
            "role": self.role,
            "previous_slot": self.previous_slot,
            "current_slot": self.current_slot,
            "previous_count": self.previous_count,
            "current_count": self.current_count,
            "retained_count": self.retained_count,
            "new_to_ledger_count": self.new_to_ledger_count,
            "reappeared_count": self.reappeared_count,
            "window_absent_count": self.window_absent_count,
            "payload_revision_candidate_count": self.payload_revision_candidate_count,
            "narrative_revision_candidate_count": self.narrative_revision_candidate_count,
            "metadata_revision_candidate_count": self.metadata_revision_candidate_count,
            "title_revision_candidate_count": self.title_revision_candidate_count,
            "rank_changed_count": self.rank_changed_count,
            "publication_backfill_candidate_count": self.publication_backfill_candidate_count,
            "publication_order_violation_count": self.publication_order_violation_count,
            "publication_unknown_count": self.publication_unknown_count,
            "absolute_rank_delta_sum": self.absolute_rank_delta_sum,
            "comparable_rank_pairs": self.comparable_rank_pairs,
            "inversion_count": self.inversion_count,
            "inversion_rate": self.inversion_rate,
        }


def _publication_diagnostics(
    previous: RoleSnapshot,
    current: RoleSnapshot,
    new_to_ledger: set[str],
) -> tuple[int, int, int]:
    previous_keys: list[str] = []
    for entry in previous.entries:
        if entry.provider_order_key is not None:
            previous_keys.append(entry.provider_order_key)
    oldest_previous = min(previous_keys) if previous_keys else None
    backfills = sum(
        1
        for entry in current.entries
        if entry.source_event_id in new_to_ledger
        and entry.provider_order_key is not None
        and oldest_previous is not None
        and entry.provider_order_key < oldest_previous
    )
    violations = 0
    unknown = 0
    prior_key: str | None = None
    for entry in current.entries:
        key = entry.provider_order_key
        if key is None:
            unknown += 1
            prior_key = None
            continue
        if prior_key is not None and key > prior_key:
            violations += 1
        prior_key = key
    return backfills, violations, unknown


def _inversion_metrics(
    previous: RoleSnapshot, current: RoleSnapshot, retained: set[str]
) -> tuple[int, int, float]:
    previous_order = [
        entry.source_event_id
        for entry in previous.entries
        if entry.source_event_id in retained
    ]
    current_rank = {
        entry.source_event_id: rank
        for rank, entry in enumerate(current.entries)
        if entry.source_event_id in retained
    }
    inversions = 0
    pairs = 0
    for left_index, left_id in enumerate(previous_order):
        for right_id in previous_order[left_index + 1 :]:
            pairs += 1
            if current_rank[left_id] > current_rank[right_id]:
                inversions += 1
    rate = 0.0 if pairs == 0 else inversions / pairs
    return pairs, inversions, rate


def compare_snapshots(
    previous: RoleSnapshot,
    current: RoleSnapshot,
    historical_seen: frozenset[str],
) -> TransitionAssessment:
    if previous.role != current.role:
        raise ProspectiveTemporalEvidenceError("transition: role mismatch")
    if current.slot <= previous.slot:
        raise ProspectiveTemporalEvidenceError("transition: non-increasing slot")

    prev_by_id = {entry.source_event_id: entry for entry in previous.entries}
    curr_by_id = {entry.source_event_id: entry for entry in current.entries}
    prev_ids = set(prev_by_id)
    curr_ids = set(curr_by_id)
    retained = prev_ids & curr_ids
    new_to_ledger = curr_ids - historical_seen
    reappeared = (curr_ids & historical_seen) - prev_ids
    window_absent = prev_ids - curr_ids

    payload_revisions = 0
    narrative_revisions = 0
    metadata_revisions = 0
    title_revisions = 0
    rank_changed = 0
    rank_delta_sum = 0
    prev_rank = {entry.source_event_id: index for index, entry in enumerate(previous.entries)}
    curr_rank = {entry.source_event_id: index for index, entry in enumerate(current.entries)}
    for identity in retained:
        before = prev_by_id[identity]
        after = curr_by_id[identity]
        payload_changed = before.payload_sha256 != after.payload_sha256
        content_changed = before.content_sha256 != after.content_sha256
        title_changed = before.title_sha256 != after.title_sha256
        if payload_changed:
            payload_revisions += 1
        if content_changed:
            narrative_revisions += 1
        if payload_changed and not content_changed:
            metadata_revisions += 1
        if title_changed:
            title_revisions += 1
        delta = abs(curr_rank[identity] - prev_rank[identity])
        rank_delta_sum += delta
        if delta:
            rank_changed += 1

    pairs, inversions, inversion_rate = _inversion_metrics(previous, current, retained)
    backfills, order_violations, publication_unknown = _publication_diagnostics(
        previous, current, new_to_ledger
    )

    return TransitionAssessment(
        role=current.role,
        previous_slot=previous.slot,
        current_slot=current.slot,
        previous_count=len(previous.entries),
        current_count=len(current.entries),
        retained_count=len(retained),
        new_to_ledger_count=len(new_to_ledger),
        reappeared_count=len(reappeared),
        window_absent_count=len(window_absent),
        payload_revision_candidate_count=payload_revisions,
        narrative_revision_candidate_count=narrative_revisions,
        metadata_revision_candidate_count=metadata_revisions,
        title_revision_candidate_count=title_revisions,
        rank_changed_count=rank_changed,
        publication_backfill_candidate_count=backfills,
        publication_order_violation_count=order_violations,
        publication_unknown_count=publication_unknown,
        absolute_rank_delta_sum=rank_delta_sum,
        comparable_rank_pairs=pairs,
        inversion_count=inversions,
        inversion_rate=inversion_rate,
    )


def build_registration_report(
    statement: NormalizedTemporalEvidenceStatement,
    synthetic_transition: TransitionAssessment,
) -> JsonObject:
    return {
        "schema_version": REPORT_SCHEMA,
        "graph": GRAPH,
        "engineering_status": ENGINEERING_STATUS,
        "scientific_status": SCIENTIFIC_STATUS,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "statement_sha256": statement.sha256,
        "roles": list(ROLES),
        "interval": _expected_interval(),
        "request_plan": _expected_request_plan(),
        "anchor": _expected_anchor(),
        "permissions": _expected_permissions(),
        "synthetic_transition": synthetic_transition.to_dict(),
    }


def canonical_report_json(
    statement_payload: object,
    previous: RoleSnapshot,
    current: RoleSnapshot,
    historical_seen: frozenset[str],
) -> str:
    statement = normalize_statement(statement_payload)
    transition = compare_snapshots(previous, current, historical_seen)
    return json.dumps(
        build_registration_report(statement, transition),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"
