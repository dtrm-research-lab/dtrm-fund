"""Pure Phase-IV human rights review policy validator v0."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from typing import cast

GRAPH = "phase4_human_rights_review_v0"
STATEMENT_SCHEMA = "dtrm.phase4.human_rights_review.v0"
REPORT_SCHEMA = "dtrm.phase4.human_rights_review_report.v0"
ENGINEERING_STATUS = "PASS_HUMAN_RIGHTS_REVIEW_PROTOCOL"
SCIENTIFIC_STATUS = "BLOCKED_PROSPECTIVE_DEPLOYMENT"

CONTRACT_PATH = "research/contracts/DTRM_PHASE4_HUMAN_RIGHTS_REVIEW_V0.md"
CONTRACT_BLOB_SHA = "e707e7a8d8e5c148d39fe62020cc08e0ba948fbf"
REGISTRATION_COMMIT = "173b7d09dd4bd3746e8dbd2223c398f5299d517b"
PARENT_INTEGRATION = "62c2a2735d663413390aa966a2be3cd934c77ce6"
TRACKED_STATEMENT_SHA256 = "af430a75ba2618e38c6fd6b93e560da2ee078eefad5560f26d265ccac7d17b07"

ALLOWED_REVIEW_STATES = {
    "PENDING_HUMAN_EVIDENCE",
    "HUMAN_REVIEW_COMPLETED_BLOCKED",
    "HUMAN_REVIEW_COMPLETED_SUPPORTED",
}
ALLOWED_ASSESSMENTS = {"SUPPORTED", "NOT_SUPPORTED", "UNKNOWN"}
EVIDENCE_CLASS_KEYS = {
    "ACCOUNT_PLAN_SUMMARY",
    "ORDER_FORM_OR_SUBSCRIPTION_TERMS",
    "PROVIDER_WRITTEN_CLARIFICATION",
    "PROVIDER_LICENSING_STATEMENT",
}
RIGHTS_KEYS = {
    "programmatic_endpoint_access",
    "exact_payload_storage",
    "retain_through_phase4_evaluation",
    "internal_research_use",
    "termination_or_entitlement_loss_obligation_known",
    "publication_display_redistribution_restrictions_known",
    "storage_security_obligations_known",
    "retention_duration_compatible_with_phase4",
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
    "password=",
    "account_id=",
    "customer_id=",
    "invoice_number=",
    "order_number=",
    "billing_address=",
    "raw_contract",
    "order_form_text",
    "screenshot_content",
    "provider_payload",
    "account_email",
    "reviewer_name",
    "reviewer_email",
    "-----begin private key-----",
)
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
LOWER_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")

JsonObject = dict[str, object]


class HumanRightsReviewError(ValueError):
    """The human-rights review statement violates its preregistered boundary."""


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
    """Reject secret/identifier/private-material shaped content without echoing it."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_FRAGMENTS):
            raise HumanRightsReviewError("statement contains forbidden sensitive material")
        if EMAIL_RE.search(text):
            raise HumanRightsReviewError("statement contains forbidden sensitive material")


def _require_exact_keys(value: object, expected: set[str], label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise HumanRightsReviewError(f"{label}: expected object")
    mapping = cast(JsonObject, value)
    if set(mapping) != expected:
        raise HumanRightsReviewError(f"{label}: unexpected keys")
    return mapping


def _require_bool(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise HumanRightsReviewError(f"{label}: expected boolean")
    return value


def _validate_iso_date_or_none(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise HumanRightsReviewError(f"{label}: expected date or null")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise HumanRightsReviewError(f"{label}: invalid date") from exc
    return value


def _validate_sha256_or_none(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or LOWER_HEX_64_RE.fullmatch(value) is None:
        raise HumanRightsReviewError(f"{label}: invalid SHA-256")
    return value


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
            raise HumanRightsReviewError(
                f"registered_contract.{key}: registered value mismatch"
            )
    return dict(actual)


def _validate_permissions(value: object) -> JsonObject:
    expected = _fixed_permissions()
    actual = _require_exact_keys(value, set(expected), "permissions")
    for key, expected_value in expected.items():
        observed = actual[key]
        if type(observed) is not type(expected_value) or observed != expected_value:
            if expected_value is False and observed is True:
                raise HumanRightsReviewError(f"permissions.{key}: promotion forbidden")
            raise HumanRightsReviewError(f"permissions.{key}: registered value mismatch")
    return dict(actual)


@dataclass(frozen=True, slots=True)
class NormalizedHumanRightsReview:
    """Detached immutable canonical review statement."""

    canonical_json: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


@dataclass(frozen=True, slots=True)
class HumanRightsReviewReport:
    """Aggregate rights classification with all operational permissions closed."""

    statement_sha256: str
    review_state: str
    evidence_class_count: int
    supported_count: int
    not_supported_count: int
    unknown_count: int
    has_redacted_evidence_digest: bool
    human_review_completed: bool
    rights_supported: bool

    def to_dict(self) -> JsonObject:
        rights_status = "SUPPORTED_BY_REVIEW" if self.rights_supported else "BLOCKED"
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "engineering_status": ENGINEERING_STATUS,
            "review_state": self.review_state,
            "account_entitlement_status": rights_status,
            "storage_retention_rights_status": rights_status,
            "provider_semantics_probe_eligible": self.rights_supported,
            "activation_readiness_status": "BLOCKED",
            "bindings": {
                "parent_integration": PARENT_INTEGRATION,
                "registration_commit": REGISTRATION_COMMIT,
                "contract_blob_sha": CONTRACT_BLOB_SHA,
                "statement_sha256": self.statement_sha256,
            },
            "review_summary": {
                "evidence_class_count": self.evidence_class_count,
                "supported_count": self.supported_count,
                "not_supported_count": self.not_supported_count,
                "unknown_count": self.unknown_count,
                "has_redacted_evidence_digest": self.has_redacted_evidence_digest,
                "human_review_completed": self.human_review_completed,
            },
            "permissions": _fixed_permissions(),
        }


def normalize_human_rights_review(payload: object) -> NormalizedHumanRightsReview:
    """Validate a sanitized human-review statement without performing external I/O."""

    assert_no_sensitive_material(payload)
    root = _require_exact_keys(
        payload,
        {
            "schema_version",
            "graph",
            "registered_contract",
            "provider_scope",
            "review_state",
            "evidence_classes_reviewed",
            "review_date",
            "redacted_evidence_sha256",
            "rights_assessment",
            "reviewer_attestation",
            "permissions",
        },
        "statement",
    )
    if root["schema_version"] != STATEMENT_SCHEMA:
        raise HumanRightsReviewError("schema_version: registered value mismatch")
    if root["graph"] != GRAPH:
        raise HumanRightsReviewError("graph: registered value mismatch")
    if root["provider_scope"] != "FINANCIAL_MODELING_PREP":
        raise HumanRightsReviewError("provider_scope: registered value mismatch")

    registered_contract = _validate_registered_contract(root["registered_contract"])
    review_state = root["review_state"]
    if not isinstance(review_state, str) or review_state not in ALLOWED_REVIEW_STATES:
        raise HumanRightsReviewError("review_state: invalid value")

    evidence_classes = _require_exact_keys(
        root["evidence_classes_reviewed"],
        EVIDENCE_CLASS_KEYS,
        "evidence_classes_reviewed",
    )
    normalized_classes = {
        key: _require_bool(
            evidence_classes[key], f"evidence_classes_reviewed.{key}"
        )
        for key in sorted(EVIDENCE_CLASS_KEYS)
    }
    evidence_count = sum(value is True for value in normalized_classes.values())
    review_date = _validate_iso_date_or_none(root["review_date"], "review_date")
    evidence_digest = _validate_sha256_or_none(
        root["redacted_evidence_sha256"], "redacted_evidence_sha256"
    )

    assessments = _require_exact_keys(
        root["rights_assessment"], RIGHTS_KEYS, "rights_assessment"
    )
    normalized_assessments: dict[str, str] = {}
    for key in sorted(RIGHTS_KEYS):
        assessment = assessments[key]
        if not isinstance(assessment, str) or assessment not in ALLOWED_ASSESSMENTS:
            raise HumanRightsReviewError(f"rights_assessment.{key}: invalid value")
        normalized_assessments[key] = assessment

    attestation = _require_exact_keys(
        root["reviewer_attestation"],
        {
            "human_review_completed",
            "direct_support_confirmed",
            "contradiction_free",
            "raw_private_material_stored_in_repo",
            "secrets_or_identifiers_stored_in_repo",
        },
        "reviewer_attestation",
    )
    normalized_attestation = {
        key: _require_bool(attestation[key], f"reviewer_attestation.{key}")
        for key in (
            "human_review_completed",
            "direct_support_confirmed",
            "contradiction_free",
            "raw_private_material_stored_in_repo",
            "secrets_or_identifiers_stored_in_repo",
        )
    }

    if normalized_attestation["raw_private_material_stored_in_repo"]:
        raise HumanRightsReviewError(
            "reviewer_attestation.raw_private_material_stored_in_repo: forbidden"
        )
    if normalized_attestation["secrets_or_identifiers_stored_in_repo"]:
        raise HumanRightsReviewError(
            "reviewer_attestation.secrets_or_identifiers_stored_in_repo: forbidden"
        )

    all_supported = all(
        value == "SUPPORTED" for value in normalized_assessments.values()
    )
    support_conditions = (
        evidence_count > 0
        and review_date is not None
        and normalized_attestation["human_review_completed"]
        and normalized_attestation["direct_support_confirmed"]
        and normalized_attestation["contradiction_free"]
        and all_supported
    )

    if review_state == "PENDING_HUMAN_EVIDENCE":
        if evidence_count != 0 or review_date is not None or evidence_digest is not None:
            raise HumanRightsReviewError(
                "PENDING_HUMAN_EVIDENCE: reviewed evidence forbidden"
            )
        if any(value != "UNKNOWN" for value in normalized_assessments.values()):
            raise HumanRightsReviewError(
                "PENDING_HUMAN_EVIDENCE: assessments must remain UNKNOWN"
            )
        if any(normalized_attestation.values()):
            raise HumanRightsReviewError(
                "PENDING_HUMAN_EVIDENCE: attestation must remain false"
            )
    else:
        if evidence_count == 0:
            raise HumanRightsReviewError("completed review: evidence class required")
        if review_date is None:
            raise HumanRightsReviewError("completed review: review date required")
        if not normalized_attestation["human_review_completed"]:
            raise HumanRightsReviewError(
                "completed review: human_review_completed required"
            )
        if review_state == "HUMAN_REVIEW_COMPLETED_SUPPORTED":
            if not support_conditions:
                raise HumanRightsReviewError(
                    "supported review: mandatory positive support missing"
                )
        elif support_conditions:
            raise HumanRightsReviewError(
                "blocked review: fully supported evidence must use supported state"
            )

    permissions = _validate_permissions(root["permissions"])
    normalized: JsonObject = {
        "schema_version": STATEMENT_SCHEMA,
        "graph": GRAPH,
        "registered_contract": registered_contract,
        "provider_scope": "FINANCIAL_MODELING_PREP",
        "review_state": review_state,
        "evidence_classes_reviewed": normalized_classes,
        "review_date": review_date,
        "redacted_evidence_sha256": evidence_digest,
        "rights_assessment": normalized_assessments,
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
    return NormalizedHumanRightsReview(canonical)


def canonical_statement_bytes(statement: NormalizedHumanRightsReview) -> bytes:
    """Return the exact canonical statement bytes."""

    return statement.canonical_json.encode("utf-8")


def review_human_rights(payload: object) -> HumanRightsReviewReport:
    """Apply the preregistered review-state policy to a sanitized statement."""

    normalized = normalize_human_rights_review(payload)
    statement = normalized.to_dict()
    classes = cast(dict[str, object], statement["evidence_classes_reviewed"])
    assessments = cast(dict[str, object], statement["rights_assessment"])
    attestation = cast(dict[str, object], statement["reviewer_attestation"])
    review_state = cast(str, statement["review_state"])
    digest = cast(str | None, statement["redacted_evidence_sha256"])
    assessment_values = tuple(cast(str, value) for value in assessments.values())
    rights_supported = review_state == "HUMAN_REVIEW_COMPLETED_SUPPORTED"
    return HumanRightsReviewReport(
        statement_sha256=hashlib.sha256(canonical_statement_bytes(normalized)).hexdigest(),
        review_state=review_state,
        evidence_class_count=sum(value is True for value in classes.values()),
        supported_count=assessment_values.count("SUPPORTED"),
        not_supported_count=assessment_values.count("NOT_SUPPORTED"),
        unknown_count=assessment_values.count("UNKNOWN"),
        has_redacted_evidence_digest=digest is not None,
        human_review_completed=attestation["human_review_completed"] is True,
        rights_supported=rights_supported,
    )


def serialize_review(review: HumanRightsReviewReport) -> str:
    """Serialize aggregate-only human-rights review evidence."""

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
