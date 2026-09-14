"""Fail-closed preregistration for the merged Phase-IV scheduled revision."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_scheduled_revision_addendum_v1"
STATEMENT_SCHEMA = "dtrm.phase4.scheduled_revision_addendum.v1"
STATUS = "PREREGISTERED_SCHEDULED_REVISION_BOUND_UNARMED"
SCIENTIFIC_PARENT_COMMIT = "a7e03fdd72e4b2132d877d7e30785803398650a9"
SCIENTIFIC_PARENT_TREE = "02e4517b021a0337fef49416e0d5fba76b8182f4"
BACKEND_REPOSITORY = "tech-com-UA00001/theresistance-back"
BACKEND_MERGE_COMMIT = "bf844932f8bb3e6773c329a45135fd754c6d8342"
BACKEND_MERGE_TREE = "c090c3cb41165ee513de812dec562f497407df62"
BACKEND_DORMANT_ANCESTOR = "974a7a744642cc8268ca5972df4ef208f629ed2b"
VALIDATED_PR_HEAD = "ce04527c9a36c9055c9180a534dda0d91ba69952"
WORKFLOW_PATH = ".github/workflows/phase4_fmp_news_temporal_capture_v1.yml"
WORKFLOW_BLOB = "0ea9b53b300ea8bbd8f14d3d309cf1d73ecc6c22"
WORKFLOW_IDENTITY = "phase4_fmp_news_temporal_capture_v1"
CRON = ("15 0 * * *", "15 6 * * *", "15 12 * * *", "15 18 * * *")
PROVIDER_ROLES = ("fmp_articles", "general_latest", "stock_latest")
REQUEST_FINGERPRINT = "932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd"
ARM_VARIABLE = "PHASE4_PROSPECTIVE_CAPTURE_ARMED"
ARM_VALUE = "true"
ACTIVATION_B64_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_B64"
ACTIVATION_ID_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_ID"
ACTIVATION_SHA256_VARIABLE = "PHASE4_ACTIVATION_STATEMENT_SHA256"
TARGET_SLOT_MIN = 0
TARGET_SLOT_MAX = 55
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


class ScheduledRevisionAddendumError(ValueError):
    """The scheduled-revision addendum violates the preregistered boundary."""


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
        "backend_revision": {
            "repository": BACKEND_REPOSITORY,
            "merge_commit": BACKEND_MERGE_COMMIT,
            "merge_tree": BACKEND_MERGE_TREE,
            "dormant_ancestor_commit": BACKEND_DORMANT_ANCESTOR,
            "validated_pr_head": VALIDATED_PR_HEAD,
        },
        "workflow": {
            "path": WORKFLOW_PATH,
            "blob_sha": WORKFLOW_BLOB,
            "identity": WORKFLOW_IDENTITY,
            "cron": list(CRON),
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
        "runtime_semantics": {
            "schedule_default_armed": False,
            "periodic_capture_activation_permitted": False,
            "prospective_start_bound": False,
            "credential_or_writer_authority_claimed": False,
            "activation_statement_provisioned": False,
            "provider_credential_available_during_checkout_setup_install_or_preflight": False,
            "provider_credential_scoped_only_to_post_verification_capture_step": True,
            "scheduled_side_effects_require_arm_and_exact_statement_verification": True,
            "scheduled_target_slot_min": TARGET_SLOT_MIN,
            "scheduled_target_slot_max": TARGET_SLOT_MAX,
            "scheduled_first_attempt_target_derived_from_runner_clock": True,
            "scheduled_rerun_target_derivation_from_rerun_clock_permitted": False,
            "scheduled_rerun_without_same_run_immutable_attempt1_provenance_fails_closed": True,
            "scheduled_rerun_counting_eligible": False,
            "manual_workflow_dispatch_counting_eligible": False,
            "scheduled_side_effects_permitted_after_final_slot": False,
        },
        "downstream_permissions": _downstream_permissions(),
        "status": STATUS,
    }


def _unique_object(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise ScheduledRevisionAddendumError("statement contains duplicate JSON keys")
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
            raise ScheduledRevisionAddendumError("statement contains forbidden secret material")


def _compare_exact(actual: object, expected: object, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise ScheduledRevisionAddendumError(f"{label}: expected object")
        actual_obj = cast(JsonObject, actual)
        expected_obj = cast(JsonObject, expected)
        if set(actual_obj) != set(expected_obj):
            raise ScheduledRevisionAddendumError(f"{label}: unexpected keys")
        for key in expected_obj:
            child = f"{label}.{key}" if label else key
            _compare_exact(actual_obj[key], expected_obj[key], child)
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ScheduledRevisionAddendumError(f"{label}: registered value mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            _compare_exact(left, right, f"{label}[{index}]")
        return
    if type(actual) is not type(expected) or actual != expected:
        raise ScheduledRevisionAddendumError(f"{label}: registered value mismatch")


@dataclass(frozen=True, slots=True)
class VerifiedScheduledRevisionAddendum:
    canonical_json: str
    sha256: str


def verify_statement_bytes(statement_bytes: bytes) -> VerifiedScheduledRevisionAddendum:
    try:
        decoded = statement_bytes.decode("utf-8")
        payload = cast(object, json.loads(decoded, object_pairs_hook=_unique_object))
    except ScheduledRevisionAddendumError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise ScheduledRevisionAddendumError("invalid statement JSON") from None

    _assert_source_value_free(payload)
    expected = expected_statement()
    _compare_exact(payload, expected, "")
    canonical = (
        json.dumps(expected, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return VerifiedScheduledRevisionAddendum(canonical_json=canonical, sha256=digest)
