"""Pure Phase-IV entitlement evidence intake validator v0."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from typing import cast

GRAPH = "phase4_entitlement_evidence_intake_v0"
MANIFEST_SCHEMA = "dtrm.phase4.entitlement_evidence_intake.v0"
REPORT_SCHEMA = "dtrm.phase4.entitlement_evidence_intake_review.v0"
ENGINEERING_STATUS = "PASS_ENTITLEMENT_EVIDENCE_INTAKE"
SCIENTIFIC_STATUS = "BLOCKED_PROSPECTIVE_DEPLOYMENT"

CONTRACT_PATH = "research/contracts/DTRM_PHASE4_ENTITLEMENT_EVIDENCE_INTAKE_V0.md"
CONTRACT_BLOB_SHA = "67ffde2df83518094b2c97513630102990cde4f6"
REGISTRATION_COMMIT = "0f49321811c3a992d7486dd122e25ae4a9a2a5fd"
PARENT_INTEGRATION = "4e64bf27fed918fe0b022c21769e96d500a99d6e"
TRACKED_MANIFEST_SHA256 = "7ad80458b92353a8079297ddcc99e1e6c51f102229cc783f4d15f09702bafb5d"

ALLOWED_EVIDENCE_STATES = {"NO_EVIDENCE", "EVIDENCE_PRESENT_UNVERIFIED"}
ALLOWED_ANSWERS = {"YES", "NO", "UNKNOWN"}
EVIDENCE_CLASS_KEYS = {
    "account_plan_summary",
    "order_form_or_subscription_terms",
    "written_provider_clarification",
    "provider_licensing_statement",
}
ANSWER_KEYS = {
    "programmatic_registered_news_access",
    "exact_payload_storage",
    "retention_through_phase4_evaluation",
    "retention_period_constraints",
    "termination_deletion_or_cessation",
    "internal_research_and_derived_analysis",
    "publication_display_redistribution_restrictions",
    "additional_storage_security_controls",
}
FORBIDDEN_FRAGMENTS = (
    "mongodb://",
    "mongodb+srv://",
    "apikey=",
    "api_key=",
    "authorization:",
    "bearer ",
    "cookie:",
    "set-cookie:",
    "session=",
    "account_id=",
    "customer_id=",
    "invoice_number=",
    "order_number=",
    "billing_address=",
    "-----begin private key-----",
)
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
LOWER_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")

JsonObject = dict[str, object]


class EntitlementEvidenceError(ValueError):
    """The entitlement evidence statement violates its preregistered boundary."""


def _fixed_permissions() -> JsonObject:
    return {
        "production_provider_access_permitted": False,
        "production_storage_mutation_permitted": False,
        "runtime_adapter_execution_permitted": False,
        "workflow_activation_permitted": False,
        "provider_semantics_live_probe_permitted": False,
        "history_construction_permitted": False,
        "temporal_state_fitting_permitted": False,
        "training_permitted": False,
        "outcome_access_permitted": False,
        "model_fitting_performed": False,
        "mm1_execution_permitted": False,
        "scientific_status": SCIENTIFIC_STATUS,
    }


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


def assert_no_sensitive_material(value: object) -> None:
    """Reject secret/account-identifier shaped material without echoing it."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_FRAGMENTS):
            raise EntitlementEvidenceError("statement contains forbidden sensitive material")
        if EMAIL_RE.search(text):
            raise EntitlementEvidenceError("statement contains forbidden sensitive material")


def _require_exact_keys(value: object, expected: set[str], label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise EntitlementEvidenceError(f"{label}: expected object")
    mapping = cast(JsonObject, value)
    if set(mapping) != expected:
        raise EntitlementEvidenceError(f"{label}: unexpected keys")
    return mapping


def _require_bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise EntitlementEvidenceError(f"{label}: expected boolean")
    return value


def _validate_iso_date_or_none(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise EntitlementEvidenceError(f"{label}: expected date or null")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise EntitlementEvidenceError(f"{label}: invalid date") from exc
    return value


def _validate_sha256_or_none(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or LOWER_HEX_64_RE.fullmatch(value) is None:
        raise EntitlementEvidenceError(f"{label}: invalid SHA-256")
    return value


def _validate_permissions(value: object) -> JsonObject:
    expected = _fixed_permissions()
    permissions = _require_exact_keys(value, set(expected), "permissions")
    for key, expected_value in expected.items():
        actual = permissions[key]
        if type(actual) is not type(expected_value) or actual != expected_value:
            if expected_value is False and actual is True:
                raise EntitlementEvidenceError(f"permissions.{key}: promotion forbidden")
            raise EntitlementEvidenceError(f"permissions.{key}: registered value mismatch")
    return dict(permissions)


def _validate_registered_contract(value: object) -> JsonObject:
    expected: JsonObject = {
        "path": CONTRACT_PATH,
        "blob_sha": CONTRACT_BLOB_SHA,
        "registration_commit": REGISTRATION_COMMIT,
        "parent_integration": PARENT_INTEGRATION,
    }
    actual = _require_exact_keys(value, set(expected), "registered_contract")
    for key, expected_value in expected.items():
        if actual[key] != expected_value:
            raise EntitlementEvidenceError(
                f"registered_contract.{key}: registered value mismatch"
            )
    return dict(actual)


@dataclass(frozen=True, slots=True)
class NormalizedEntitlementEvidence:
    """Detached immutable canonical intake statement."""

    canonical_json: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


@dataclass(frozen=True, slots=True)
class EntitlementEvidenceReview:
    """Aggregate intake classification that cannot authorize rights."""

    statement_sha256: str
    evidence_state: str
    evidence_class_count: int
    yes_count: int
    no_count: int
    unknown_count: int
    has_redacted_evidence_digest: bool

    def to_dict(self) -> JsonObject:
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "engineering_status": ENGINEERING_STATUS,
            "evidence_state": self.evidence_state,
            "account_entitlement_status": "BLOCKED",
            "storage_retention_rights_status": "BLOCKED",
            "human_rights_review_required": True,
            "provider_semantics_probe_permitted": False,
            "activation_readiness_status": "BLOCKED",
            "bindings": {
                "parent_integration": PARENT_INTEGRATION,
                "registration_commit": REGISTRATION_COMMIT,
                "contract_blob_sha": CONTRACT_BLOB_SHA,
                "statement_sha256": self.statement_sha256,
            },
            "evidence_summary": {
                "evidence_class_count": self.evidence_class_count,
                "yes_count": self.yes_count,
                "no_count": self.no_count,
                "unknown_count": self.unknown_count,
                "has_redacted_evidence_digest": self.has_redacted_evidence_digest,
            },
            "permissions": _fixed_permissions(),
        }


def normalize_entitlement_evidence(payload: object) -> NormalizedEntitlementEvidence:
    """Validate a sanitized evidence statement without treating it as authorization."""

    assert_no_sensitive_material(payload)
    root = _require_exact_keys(
        payload,
        {
            "schema_version",
            "graph",
            "registered_contract",
            "provider_scope",
            "evidence_state",
            "evidence_classes",
            "evidence_date",
            "redacted_evidence_sha256",
            "answers",
            "reviewer_attestation",
            "permissions",
        },
        "statement",
    )
    if root["schema_version"] != MANIFEST_SCHEMA:
        raise EntitlementEvidenceError("schema_version: registered value mismatch")
    if root["graph"] != GRAPH:
        raise EntitlementEvidenceError("graph: registered value mismatch")
    if root["provider_scope"] != "FINANCIAL_MODELING_PREP":
        raise EntitlementEvidenceError("provider_scope: registered value mismatch")
    registered_contract = _validate_registered_contract(root["registered_contract"])

    evidence_state = root["evidence_state"]
    if not isinstance(evidence_state, str) or evidence_state not in ALLOWED_EVIDENCE_STATES:
        raise EntitlementEvidenceError("evidence_state: promotion or value forbidden")

    evidence_classes = _require_exact_keys(
        root["evidence_classes"], EVIDENCE_CLASS_KEYS, "evidence_classes"
    )
    normalized_classes = {
        key: _require_bool(evidence_classes[key], f"evidence_classes.{key}")
        for key in sorted(EVIDENCE_CLASS_KEYS)
    }
    evidence_date = _validate_iso_date_or_none(root["evidence_date"], "evidence_date")
    evidence_digest = _validate_sha256_or_none(
        root["redacted_evidence_sha256"], "redacted_evidence_sha256"
    )

    answers = _require_exact_keys(root["answers"], ANSWER_KEYS, "answers")
    normalized_answers: dict[str, str] = {}
    for key in sorted(ANSWER_KEYS):
        answer = answers[key]
        if not isinstance(answer, str) or answer not in ALLOWED_ANSWERS:
            raise EntitlementEvidenceError(f"answers.{key}: invalid answer")
        normalized_answers[key] = answer

    attestation = _require_exact_keys(
        root["reviewer_attestation"],
        {
            "human_review_completed",
            "reviewed_on",
            "review_artifact_registered",
            "contradiction_free",
        },
        "reviewer_attestation",
    )
    normalized_attestation = {
        "human_review_completed": _require_bool(
            attestation["human_review_completed"],
            "reviewer_attestation.human_review_completed",
        ),
        "reviewed_on": _validate_iso_date_or_none(
            attestation["reviewed_on"], "reviewer_attestation.reviewed_on"
        ),
        "review_artifact_registered": _require_bool(
            attestation["review_artifact_registered"],
            "reviewer_attestation.review_artifact_registered",
        ),
        "contradiction_free": _require_bool(
            attestation["contradiction_free"],
            "reviewer_attestation.contradiction_free",
        ),
    }
    if any(
        (
            normalized_attestation["human_review_completed"],
            normalized_attestation["review_artifact_registered"],
            normalized_attestation["contradiction_free"],
            normalized_attestation["reviewed_on"] is not None,
        )
    ):
        raise EntitlementEvidenceError("reviewer_attestation: promotion forbidden")

    evidence_count = sum(bool(value) for value in normalized_classes.values())
    if evidence_state == "NO_EVIDENCE":
        if evidence_count != 0 or evidence_date is not None or evidence_digest is not None:
            raise EntitlementEvidenceError("NO_EVIDENCE: evidence material forbidden")
        if any(answer != "UNKNOWN" for answer in normalized_answers.values()):
            raise EntitlementEvidenceError("NO_EVIDENCE: answers must remain UNKNOWN")
    else:
        if evidence_count == 0:
            raise EntitlementEvidenceError(
                "EVIDENCE_PRESENT_UNVERIFIED: evidence class required"
            )
        if evidence_date is None:
            raise EntitlementEvidenceError(
                "EVIDENCE_PRESENT_UNVERIFIED: evidence date required"
            )

    permissions = _validate_permissions(root["permissions"])
    normalized: JsonObject = {
        "schema_version": MANIFEST_SCHEMA,
        "graph": GRAPH,
        "registered_contract": registered_contract,
        "provider_scope": "FINANCIAL_MODELING_PREP",
        "evidence_state": evidence_state,
        "evidence_classes": normalized_classes,
        "evidence_date": evidence_date,
        "redacted_evidence_sha256": evidence_digest,
        "answers": normalized_answers,
        "reviewer_attestation": normalized_attestation,
        "permissions": permissions,
    }
    canonical = (
        json.dumps(
            normalized,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
    return NormalizedEntitlementEvidence(canonical)


def canonical_statement_bytes(statement: NormalizedEntitlementEvidence) -> bytes:
    """Return the exact canonical statement bytes."""

    return statement.canonical_json.encode("utf-8")


def review_entitlement_evidence(payload: object) -> EntitlementEvidenceReview:
    """Classify sanitized evidence while keeping rights and operations blocked."""

    normalized = normalize_entitlement_evidence(payload)
    statement = normalized.to_dict()
    evidence_classes = cast(dict[str, object], statement["evidence_classes"])
    answers = cast(dict[str, object], statement["answers"])
    evidence_state = cast(str, statement["evidence_state"])
    digest = cast(str | None, statement["redacted_evidence_sha256"])
    answer_values = tuple(cast(str, value) for value in answers.values())
    return EntitlementEvidenceReview(
        statement_sha256=hashlib.sha256(canonical_statement_bytes(normalized)).hexdigest(),
        evidence_state=evidence_state,
        evidence_class_count=sum(value is True for value in evidence_classes.values()),
        yes_count=answer_values.count("YES"),
        no_count=answer_values.count("NO"),
        unknown_count=answer_values.count("UNKNOWN"),
        has_redacted_evidence_digest=digest is not None,
    )


def serialize_review(review: EntitlementEvidenceReview) -> str:
    """Serialize aggregate-only intake evidence."""

    return (
        json.dumps(
            review.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
