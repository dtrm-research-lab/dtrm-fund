"""Fail-closed post-merge binding readiness for Phase-IV prospective activation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_postmerge_activation_binding_readiness_v1"
STATEMENT_SCHEMA = "dtrm.phase4.postmerge_activation_binding_readiness.v1"
REPORT_SCHEMA = "dtrm.phase4.postmerge_activation_binding_readiness_review.v1"
ACTIVATION_SCHEMA = "dtrm.phase4.prospective_activation_statement.v2"

SCIENTIFIC_PARENT_COMMIT = "6e5b73b971a26db28c10802852bc82d38b0b8b61"
SCIENTIFIC_PARENT_TREE = "caafe2951dfd004245cba0f0a140bfd1c2748e07"
BACKEND_REPOSITORY = "tech-com-UA00001/theresistance-back"
BACKEND_COMMIT = "974a7a744642cc8268ca5972df4ef208f629ed2b"
BACKEND_TREE = "0edcbca9d38b3a35b9b6a7b5fbb32b04d67119c9"
WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v1.yml"
WORKFLOW_BLOB_SHA = "5ab8f5b2c7ca9d89f4bf613355d97ad5f12ffc2b"
WORKFLOW_IDENTITY = "phase4_fmp_news_temporal_capture_v1"
REQUEST_FINGERPRINT_SHA256 = (
    "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
)
PROVIDER_ROLES = ("fmp_articles", "general_latest", "stock_latest")

READINESS_STATUS = "BLOCKED_AUTHORITY_AND_START_BINDING"
UNVERIFIED = "UNVERIFIED"
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


class PostMergeBindingError(ValueError):
    """The post-merge readiness statement violates its preregistered boundary."""


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
    """Return the exact source-value-free post-merge readiness statement."""

    return {
        "schema_version": STATEMENT_SCHEMA,
        "graph": GRAPH,
        "scientific_parent": {
            "commit": SCIENTIFIC_PARENT_COMMIT,
            "tree": SCIENTIFIC_PARENT_TREE,
        },
        "backend": {
            "repository": BACKEND_REPOSITORY,
            "merge_commit": BACKEND_COMMIT,
            "merge_tree": BACKEND_TREE,
        },
        "workflow": {
            "path": WORKFLOW_PATH,
            "blob_sha": WORKFLOW_BLOB_SHA,
            "identity": WORKFLOW_IDENTITY,
            "workflow_dispatch_present": True,
            "schedule_present": False,
        },
        "provider": {
            "roles": list(PROVIDER_ROLES),
            "request_fingerprint_sha256": REQUEST_FINGERPRINT_SHA256,
        },
        "activation_contract": {
            "schema_version": ACTIVATION_SCHEMA,
            "provisioned_schema_identity": None,
            "credential_scope_status": UNVERIFIED,
            "credential_scope_evidence_sha256": None,
            "writer_authority_status": UNVERIFIED,
            "writer_authority_evidence_sha256": None,
            "prospective_start_utc": None,
            "human_activation_authorized": False,
            "periodic_capture_activation_permitted": False,
        },
        "downstream_permissions": _downstream_permissions(),
        "readiness_status": READINESS_STATUS,
    }


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise PostMergeBindingError("statement contains duplicate JSON keys")
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
            raise PostMergeBindingError("statement contains forbidden secret material")


def _compare_exact(actual: object, expected: object, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise PostMergeBindingError(f"{label}: expected object")
        actual_object = cast(JsonObject, actual)
        expected_object = cast(JsonObject, expected)
        if set(actual_object) != set(expected_object):
            raise PostMergeBindingError(f"{label}: unexpected keys")
        for key in expected_object:
            child = f"{label}.{key}" if label else key
            _compare_exact(actual_object[key], expected_object[key], child)
        return

    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise PostMergeBindingError(f"{label}: registered value mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            _compare_exact(left, right, f"{label}[{index}]")
        return

    if type(actual) is not type(expected) or actual != expected:
        if expected is False and actual is True:
            raise PostMergeBindingError(f"{label}: promotion forbidden")
        raise PostMergeBindingError(f"{label}: registered value mismatch")


@dataclass(frozen=True, slots=True)
class VerifiedPostMergeBinding:
    """Detached canonical readiness statement."""

    canonical_json: str
    sha256: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


def verify_statement_bytes(statement_bytes: bytes) -> VerifiedPostMergeBinding:
    """Verify exact readiness bytes without granting activation."""

    try:
        decoded = statement_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PostMergeBindingError("statement must be UTF-8") from exc

    try:
        payload = cast(
            object,
            json.loads(decoded, object_pairs_hook=_reject_duplicate_keys),
        )
    except json.JSONDecodeError as exc:
        raise PostMergeBindingError("statement is not valid JSON") from exc

    _assert_source_value_free(payload)
    expected = expected_statement()
    _compare_exact(payload, expected, "")

    canonical_json = (
        json.dumps(
            expected,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return VerifiedPostMergeBinding(canonical_json=canonical_json, sha256=digest)


def readiness_review(binding: VerifiedPostMergeBinding) -> JsonObject:
    """Return an aggregate-only review; activation remains blocked."""

    return {
        "schema_version": REPORT_SCHEMA,
        "graph": GRAPH,
        "readiness_status": READINESS_STATUS,
        "statement_sha256": binding.sha256,
        "fixed_bindings": {
            "scientific_parent_commit": SCIENTIFIC_PARENT_COMMIT,
            "scientific_parent_tree": SCIENTIFIC_PARENT_TREE,
            "backend_commit": BACKEND_COMMIT,
            "backend_tree": BACKEND_TREE,
            "workflow_path": WORKFLOW_PATH,
            "workflow_blob_sha": WORKFLOW_BLOB_SHA,
            "workflow_identity": WORKFLOW_IDENTITY,
            "request_fingerprint_sha256": REQUEST_FINGERPRINT_SHA256,
            "provider_roles": list(PROVIDER_ROLES),
        },
        "remaining_gates": {
            "provisioned_schema_identity": False,
            "credential_scope_authorized": False,
            "writer_authority_authorized": False,
            "prospective_start_registered": False,
            "human_activation_authorized": False,
        },
        "workflow_state": {
            "workflow_dispatch_present": True,
            "schedule_present": False,
        },
        "activation": {
            "schema_version": ACTIVATION_SCHEMA,
            "periodic_capture_activation_permitted": False,
        },
        "downstream_permissions": _downstream_permissions(),
    }
