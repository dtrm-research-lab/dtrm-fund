"""Fail-closed validator for the Phase-IV activation statement rebind."""

from __future__ import annotations

import hashlib
import json
from typing import cast

from dtrm.phase4.prospective_activation_package import (
    ACTIVATION_SCHEMA,
    BACKEND_COMMIT,
    BACKEND_TREE,
    CREDENTIAL_SCOPE_EVIDENCE_SHA256,
    PROSPECTIVE_START_UTC,
    PROVIDER_ROLES,
    REQUEST_FINGERPRINT_SHA256,
    SLOT_SCHEMA,
    WORKFLOW_IDENTITY,
    WORKFLOW_PATH,
    WRITER_AUTHORITY_EVIDENCE_SHA256,
    expected_activation_statement,
)

GRAPH = "phase4_prospective_activation_rebind_v1"
REBIND_SCHEMA = "dtrm.phase4.prospective_activation_rebind.v1"
STATUS = "REBIND_PREPARED_NOT_PROVISIONED_NOT_ARMED"

SCIENTIFIC_PARENT_COMMIT = "d919ce57852652ee2e61ddbdb9e4188480e23f55"
SCIENTIFIC_PARENT_TREE = "1d8e6aeaa2eff2ff58d89d932e6380fccb11497e"

SCHEDULER_MERGE_COMMIT = "e73d5af5196ca765bd741722bba7fd85c6ae6b7c"
SCHEDULER_MERGE_TREE = "60165123fe82e05d120e4350780b65102828ec99"
SCHEDULER_VALIDATED_HEAD = "83f015bc642ac63483f6dee1d41668cff385dbe2"
PINNED_RUNTIME_COMMIT = BACKEND_COMMIT
PINNED_RUNTIME_TREE = BACKEND_TREE
REBIND_WORKFLOW_BLOB_SHA = "a79ec00ec5761f5fb8cc8a6c017be8bbe7eb75c3"

PREVIOUS_STATEMENT_ID = "phase4-prospective-capture-2026-09-18-v1"
PREVIOUS_STATEMENT_SHA256 = (
    "540a46f4b80e73cb776596936fd2d30fdf7d74d8a64d2c6ed2bd565deb8ed2b1"
)
REBIND_STATEMENT_ID = "phase4-prospective-capture-2026-09-18-v2"
REBIND_STATEMENT_PATH = (
    "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2_REBOUND.json"
)

JsonObject = dict[str, object]


class ProspectiveActivationRebindError(ValueError):
    """The superseding activation rebind violates the frozen boundary."""


def _unique_object(pairs: list[tuple[str, object]]) -> JsonObject:
    result: JsonObject = {}
    for key, value in pairs:
        if key in result:
            raise ProspectiveActivationRebindError("duplicate JSON key")
        result[key] = value
    return result


def _reject_non_finite(_value: str) -> object:
    raise ProspectiveActivationRebindError("non-finite JSON value")


def _load_exact(data: bytes) -> JsonObject:
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_non_finite,
        )
    except ProspectiveActivationRebindError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise ProspectiveActivationRebindError("invalid JSON") from None
    if not isinstance(value, dict):
        raise ProspectiveActivationRebindError("expected JSON object")
    return cast(JsonObject, value)


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


def expected_rebound_statement() -> JsonObject:
    statement = expected_activation_statement().copy()
    statement["activation_statement"] = REBIND_STATEMENT_ID
    statement["workflow_blob_sha"] = REBIND_WORKFLOW_BLOB_SHA
    return statement


def expected_rebind_evidence(statement_sha256: str) -> JsonObject:
    return {
        "schema_version": REBIND_SCHEMA,
        "graph": GRAPH,
        "scientific_parent": {
            "commit": SCIENTIFIC_PARENT_COMMIT,
            "tree": SCIENTIFIC_PARENT_TREE,
        },
        "scheduler_binding": {
            "merge_commit": SCHEDULER_MERGE_COMMIT,
            "merge_tree": SCHEDULER_MERGE_TREE,
            "validated_head": SCHEDULER_VALIDATED_HEAD,
            "workflow_path": WORKFLOW_PATH,
            "workflow_blob_sha": REBIND_WORKFLOW_BLOB_SHA,
            "workflow_identity": WORKFLOW_IDENTITY,
            "pinned_runtime_commit": PINNED_RUNTIME_COMMIT,
            "pinned_runtime_tree": PINNED_RUNTIME_TREE,
        },
        "supersedes": {
            "activation_statement": PREVIOUS_STATEMENT_ID,
            "activation_statement_sha256": PREVIOUS_STATEMENT_SHA256,
            "reason": "scheduler_workflow_hardened_before_statement_provisioning",
        },
        "rebound_statement": {
            "path": REBIND_STATEMENT_PATH,
            "id": REBIND_STATEMENT_ID,
            "sha256": statement_sha256,
            "schema_version": ACTIVATION_SCHEMA,
        },
        "campaign_window": {
            "prospective_start_utc": PROSPECTIVE_START_UTC,
            "first_slot_utc": "2026-09-18T00:15:00Z",
            "last_slot_utc": "2026-10-01T18:15:00Z",
            "target_days": 14,
            "target_slots": 56,
            "minimum_accepted_slots": 48,
        },
        "operational_state": {
            "previous_statement_provisioned": False,
            "rebound_statement_prepared": True,
            "rebound_statement_provisioned": False,
            "arm_variable_set_to_true": False,
            "human_activation_authorized_for_rebound": False,
            "campaign_started": False,
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


def verify_rebind(
    *,
    previous_statement_bytes: bytes,
    rebound_statement_bytes: bytes,
    evidence_bytes: bytes,
) -> tuple[str, str]:
    previous = _load_exact(previous_statement_bytes)
    rebound = _load_exact(rebound_statement_bytes)
    evidence = _load_exact(evidence_bytes)

    expected_previous = expected_activation_statement()
    if previous != expected_previous:
        raise ProspectiveActivationRebindError("previous activation statement mismatch")
    if hashlib.sha256(previous_statement_bytes).hexdigest() != PREVIOUS_STATEMENT_SHA256:
        raise ProspectiveActivationRebindError("previous activation statement digest mismatch")

    expected_rebound = expected_rebound_statement()
    if rebound != expected_rebound or rebound_statement_bytes != _canonical_bytes(expected_rebound):
        raise ProspectiveActivationRebindError("rebound activation statement mismatch")

    changed = {
        key
        for key in expected_previous
        if expected_previous.get(key) != expected_rebound.get(key)
    }
    if changed != {"activation_statement", "workflow_blob_sha"}:
        raise ProspectiveActivationRebindError("rebind changed scientific fields")

    statement_sha256 = hashlib.sha256(rebound_statement_bytes).hexdigest()
    expected_evidence = expected_rebind_evidence(statement_sha256)
    if evidence != expected_evidence or evidence_bytes != _canonical_bytes(expected_evidence):
        raise ProspectiveActivationRebindError("rebind evidence mismatch")

    if (
        rebound["backend_commit"] != BACKEND_COMMIT
        or rebound["backend_tree"] != BACKEND_TREE
        or rebound["provider_roles"] != list(PROVIDER_ROLES)
        or rebound["request_fingerprint_sha256"] != REQUEST_FINGERPRINT_SHA256
        or rebound["provisioned_schema_identity"] != SLOT_SCHEMA
        or rebound["credential_scope_evidence_sha256"]
        != CREDENTIAL_SCOPE_EVIDENCE_SHA256
        or rebound["writer_authority_evidence_sha256"]
        != WRITER_AUTHORITY_EVIDENCE_SHA256
        or rebound["prospective_start_utc"] != PROSPECTIVE_START_UTC
    ):
        raise ProspectiveActivationRebindError("frozen scientific boundary changed")

    return statement_sha256, hashlib.sha256(evidence_bytes).hexdigest()
