"""Fail-closed validator for the prepared Phase-IV activation package."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from typing import cast

GRAPH = "phase4_prospective_activation_package_v1"
PACKAGE_SCHEMA = "dtrm.phase4.prospective_activation_package.v1"
ACTIVATION_SCHEMA = "dtrm.phase4.prospective_activation_statement.v2"
STATUS = "PREPARED_NOT_PROVISIONED_NOT_ARMED"

SCIENTIFIC_PARENT_COMMIT = "dcd60c90d866cb43683934f9a174c057aea70717"
SCIENTIFIC_PARENT_TREE = "a95ac8b96bfac8736ae7ea70ae5407c5fe8dedf6"
BACKEND_COMMIT = "bf844932f8bb3e6773c329a45135fd754c6d8342"
BACKEND_TREE = "c090c3cb41165ee513de812dec562f497407df62"
WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v1.yml"
WORKFLOW_BLOB_SHA = "0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22"
WORKFLOW_IDENTITY = "phase4_fmp_news_temporal_capture_v1"
PROVIDER_ROLES = ("fmp_articles", "general_latest", "stock_latest")
REQUEST_FINGERPRINT_SHA256 = "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
SLOT_SCHEMA = "dtrm.phase4.prospective_temporal_slot.v1"
CREDENTIAL_SCOPE_EVIDENCE_SHA256 = "e1203bb38fd1c03448d5d622bceb791f3a1bc5ad325fa89e566889c6b37cbdf3"
WRITER_AUTHORITY_EVIDENCE_SHA256 = "f4b9d64046b6529a94313734d77f8766320c8a00b5047d0968ab0d2bdfa21390"
ACTIVATION_STATEMENT_ID = "phase4-prospective-capture-2026-09-18-v1"
PROSPECTIVE_START_UTC = "2026-09-18T00:00:00Z"
FIRST_SLOT_UTC = "2026-09-18T00:15:00Z"
LAST_SLOT_UTC = "2026-10-01T18:15:00Z"
EARLIEST_FINALIZATION_UTC = "2026-10-01T22:15:00Z"
TARGET_DAYS = 14
TARGET_SLOTS = 56
MINIMUM_ACCEPTED_SLOTS = 48

FORBIDDEN_SECRET_FRAGMENTS = (
    "mongodb://",
    "mongodb+srv://",
    "apikey=",
    "api_key=",
    "authorization:",
    "bearer ",
    "-----begin private key-----",
)

JsonObject = dict[str, object]


class ProspectiveActivationPackageError(ValueError):
    """The prepared activation package violates the frozen boundary."""


def _unique_object(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise ProspectiveActivationPackageError("duplicate JSON key")
        result[key] = value
    return result


def _reject_non_finite(_value: str) -> object:
    raise ProspectiveActivationPackageError("non-finite JSON value")


def _load_exact(data: bytes) -> JsonObject:
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_non_finite,
        )
    except ProspectiveActivationPackageError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise ProspectiveActivationPackageError("invalid JSON") from None
    if not isinstance(value, dict):
        raise ProspectiveActivationPackageError("expected JSON object")
    return cast(JsonObject, value)


def _walk_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return tuple(
            text
            for key, nested in mapping.items()
            for text in (*_walk_strings(key), *_walk_strings(nested))
        )
    if isinstance(value, list):
        return tuple(text for item in value for text in _walk_strings(item))
    return ()


def _assert_source_value_free(value: object) -> None:
    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_SECRET_FRAGMENTS):
            raise ProspectiveActivationPackageError("forbidden secret-shaped material")


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def expected_activation_statement() -> JsonObject:
    return {
        "schema_version": ACTIVATION_SCHEMA,
        "activation_statement": ACTIVATION_STATEMENT_ID,
        "backend_commit": BACKEND_COMMIT,
        "backend_tree": BACKEND_TREE,
        "workflow_path": WORKFLOW_PATH,
        "workflow_blob_sha": WORKFLOW_BLOB_SHA,
        "workflow_identity": WORKFLOW_IDENTITY,
        "provider_roles": list(PROVIDER_ROLES),
        "request_fingerprint_sha256": REQUEST_FINGERPRINT_SHA256,
        "provisioned_schema_identity": SLOT_SCHEMA,
        "credential_scope_status": "AUTHORIZED",
        "credential_scope_evidence_sha256": CREDENTIAL_SCOPE_EVIDENCE_SHA256,
        "writer_authority_status": "AUTHORIZED",
        "writer_authority_evidence_sha256": WRITER_AUTHORITY_EVIDENCE_SHA256,
        "prospective_start_utc": PROSPECTIVE_START_UTC,
        "periodic_capture_activation_permitted": True,
    }


def expected_package(statement_sha256: str) -> JsonObject:
    return {
        "schema_version": PACKAGE_SCHEMA,
        "graph": GRAPH,
        "scientific_parent": {
            "commit": SCIENTIFIC_PARENT_COMMIT,
            "tree": SCIENTIFIC_PARENT_TREE,
        },
        "activation_statement": {
            "path": "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2.json",
            "id": ACTIVATION_STATEMENT_ID,
            "sha256": statement_sha256,
            "schema_version": ACTIVATION_SCHEMA,
        },
        "campaign_window": {
            "prospective_start_utc": PROSPECTIVE_START_UTC,
            "first_slot_utc": FIRST_SLOT_UTC,
            "last_slot_utc": LAST_SLOT_UTC,
            "earliest_finalization_utc": EARLIEST_FINALIZATION_UTC,
            "target_days": TARGET_DAYS,
            "target_slots": TARGET_SLOTS,
            "minimum_accepted_slots": MINIMUM_ACCEPTED_SLOTS,
            "first_day_acceptance_required": True,
            "last_day_acceptance_required": True,
            "backfill_permitted": False,
            "early_stopping_permitted": False,
            "counting_attempt": 1,
        },
        "operational_state": {
            "statement_prepared": True,
            "statement_provisioned": False,
            "arm_variable_set_to_true": False,
            "human_activation_authorized": False,
            "campaign_started": False,
            "operational_activation_effective": False,
        },
        "downstream_permissions": {
            "confirmatory_history_construction_permitted": False,
            "temporal_state_outcome_fitting_permitted": False,
            "outcome_access_permitted": False,
            "mm1_execution_permitted": False,
            "phase3_policy_mutation_permitted": False,
            "public_raw_provider_data_redistribution_permitted": False,
        },
        "status": STATUS,
    }


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ProspectiveActivationPackageError("timestamp must be canonical UTC")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        raise ProspectiveActivationPackageError("invalid UTC timestamp") from None
    canonical = parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if canonical != value:
        raise ProspectiveActivationPackageError("timestamp must be canonical UTC")
    return parsed


@dataclass(frozen=True, slots=True)
class VerifiedProspectiveActivationPackage:
    statement_sha256: str
    package_sha256: str


def verify_package(
    *, statement_bytes: bytes, package_bytes: bytes
) -> VerifiedProspectiveActivationPackage:
    statement = _load_exact(statement_bytes)
    package = _load_exact(package_bytes)
    _assert_source_value_free(statement)
    _assert_source_value_free(package)

    expected_statement = expected_activation_statement()
    if statement != expected_statement or statement_bytes != _canonical_bytes(expected_statement):
        raise ProspectiveActivationPackageError("activation statement mismatch")

    statement_sha256 = hashlib.sha256(statement_bytes).hexdigest()
    expected_package_value = expected_package(statement_sha256)
    if package != expected_package_value or package_bytes != _canonical_bytes(expected_package_value):
        raise ProspectiveActivationPackageError("activation package mismatch")

    start = _parse_utc(PROSPECTIVE_START_UTC)
    first_slot = _parse_utc(FIRST_SLOT_UTC)
    last_slot = _parse_utc(LAST_SLOT_UTC)
    earliest_finalization = _parse_utc(EARLIEST_FINALIZATION_UTC)

    slot_zero = datetime.combine(start.date(), time(0, 15, tzinfo=UTC))
    if start >= slot_zero or first_slot != slot_zero:
        raise ProspectiveActivationPackageError("start is not strictly before slot zero")
    if last_slot != first_slot + timedelta(days=13, hours=18):
        raise ProspectiveActivationPackageError("last slot mismatch")
    if earliest_finalization != last_slot + timedelta(hours=4):
        raise ProspectiveActivationPackageError("finalization boundary mismatch")

    return VerifiedProspectiveActivationPackage(
        statement_sha256=statement_sha256,
        package_sha256=hashlib.sha256(package_bytes).hexdigest(),
    )
