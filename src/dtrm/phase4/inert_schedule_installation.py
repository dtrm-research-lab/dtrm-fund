"""Fail-closed preregistration for inert Phase-IV schedule installation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_inert_schedule_installation_v1"
STATEMENT_SCHEMA = "dtrm.phase4.inert_schedule_installation.v1"
STATUS = "PREREGISTERED_INERT_SCHEDULE_INSTALLATION"
SCIENTIFIC_PARENT_COMMIT = "56952d9c9a6f00a79e8ee2e52765853be58edaae"
SCIENTIFIC_PARENT_TREE = "9ba1bd4f7565268af0f5c409d073fa7672bb58f8"
BACKEND_REPOSITORY = "tech-com-UA00001/theresistance-back"
DORMANT_BACKEND_COMMIT = "974a7a744642cc8268ca5972df4ef208f629ed2b"
DORMANT_BACKEND_TREE = "0edcbca9d38b3a35b9b6a7b5fbb32b04d67119c9"
WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v1.yml"
WORKFLOW_IDENTITY = "phase4_fmp_news_temporal_capture_v1"
DORMANT_WORKFLOW_BLOB = "5ab8f5b2c7ca9d89f4bf613355d97ad5f12ffc2b"
CRON = ("15 0 * * *", "15 6 * * *", "15 12 * * *", "15 18 * * *")
PROVIDER_ROLES = ("fmp_articles", "general_latest", "stock_latest")
REQUEST_FINGERPRINT = "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
ARM_VARIABLE = "PHASE4_PROSPECTIVE_CAPTURE_ARMED"
ARM_VALUE = "true"
ACTIVATION_B64_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_B64"
ACTIVATION_ID_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_ID"
ACTIVATION_SHA256_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_SHA256"
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


class InertScheduleInstallationError(ValueError):
    """The inert-schedule preregistration violates its frozen boundary."""


def _downstream_permissions() -> JsonObject:
    return {
        "confirmatory_history_construction_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
        "public_raw_provider_data_redistribution_permitted": False,
    }


def expected_statement() -> JsonObject:
    return {
        "schema_version": STATEMENT_SCHEMA,
        "graph": GRAPH,
        "scientific_parent": {
            "commit": SCIENTIFIC_PARENT_COMMIT,
            "tree": SCIENTIFIC_PARENT_TREE,
        },
        "backend_lineage": {
            "repository": BACKEND_REPOSITORY,
            "dormant_merge_commit": DORMANT_BACKEND_COMMIT,
            "dormant_merge_tree": DORMANT_BACKEND_TREE,
        },
        "workflow": {
            "path": WORKFLOW_PATH,
            "identity": WORKFLOW_IDENTITY,
            "dormant_blob_sha": DORMANT_WORKFLOW_BLOB,
            "cron": list(CRON),
            "schedule_installation_permitted": True,
            "schedule_default_armed": False,
            "arm_variable": ARM_VARIABLE,
            "arm_value": ARM_VALUE,
            "activation_statement_b64_variable": ACTIVATION_B64_VARIABLE,
            "activation_statement_id_variable": ACTIVATION_ID_VARIABLE,
            "activation_statement_sha256_variable": ACTIVATION_SHA256_VARIABLE,
        },
        "provider": {
            "roles": list(PROVIDER_ROLES),
            "request_fingerprint_sha256": REQUEST_FINGERPRINT,
        },
        "pre_activation_guards": {
            "scheduled_provider_access_permitted_when_unarmed": False,
            "scheduled_private_write_permitted_when_unarmed": False,
            "preactivation_schedule_runs_counting_eligible": False,
            "prospective_start_bound": False,
            "periodic_capture_activation_permitted": False,
        },
        "downstream_permissions": _downstream_permissions(),
        "status": STATUS,
    }


def _unique_object(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise InertScheduleInstallationError("statement contains duplicate JSON keys")
        result[key] = value
    return result


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
            raise InertScheduleInstallationError("statement contains forbidden secret material")


def _compare_exact(actual: object, expected: object, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise InertScheduleInstallationError(f"{label}: expected object")
        actual_obj = cast(JsonObject, actual)
        expected_obj = cast(JsonObject, expected)
        if set(actual_obj) != set(expected_obj):
            raise InertScheduleInstallationError(f"{label}: unexpected keys")
        for key in expected_obj:
            child = f"{label}.{key}" if label else key
            _compare_exact(actual_obj[key], expected_obj[key], child)
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise InertScheduleInstallationError(f"{label}: registered value mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            _compare_exact(left, right, f"{label}[{index}]")
        return
    if type(actual) is not type(expected) or actual != expected:
        raise InertScheduleInstallationError(f"{label}: registered value mismatch")


@dataclass(frozen=True, slots=True)
class VerifiedInertScheduleInstallation:
    canonical_json: str
    sha256: str


def verify_statement_bytes(statement_bytes: bytes) -> VerifiedInertScheduleInstallation:
    try:
        decoded = statement_bytes.decode("utf-8")
        payload = cast(object, json.loads(decoded, object_pairs_hook=_unique_object))
    except InertScheduleInstallationError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise InertScheduleInstallationError("invalid statement JSON") from None

    _assert_source_value_free(payload)
    expected = expected_statement()
    _compare_exact(payload, expected, "")
    canonical = (
        json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return VerifiedInertScheduleInstallation(canonical_json=canonical, sha256=digest)
