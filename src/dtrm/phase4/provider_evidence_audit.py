"""Pure validator for Phase-IV provider evidence audit v0."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_provider_evidence_audit_v0"
MANIFEST_SCHEMA = "dtrm.phase4.provider_evidence_manifest.v0"
REPORT_SCHEMA = "dtrm.phase4.provider_evidence_review.v0"
ENGINEERING_STATUS = "PASS_PROVIDER_EVIDENCE_AUDIT"
SCIENTIFIC_STATUS = "BLOCKED_PROSPECTIVE_DEPLOYMENT"

CONTRACT_PATH = "research/contracts/DTRM_PHASE4_PROVIDER_EVIDENCE_AUDIT_V0.md"
CONTRACT_SHA256 = "708dcc4e43da77aaa6b5686d1343c1924a557b9e7a19e9734708abf265ad1b84"
REGISTRATION_COMMIT = "8fbe5301d2cd5a7af219dbf185d69b8d63c991f1"
PARENT_INTEGRATION = "02bdc19e501697395526bac7a5a661637dd945f8"

FORBIDDEN_SECRET_FRAGMENTS = (
    "mongodb://",
    "mongodb+srv://",
    "apikey=",
    "api_key=",
    "authorization:",
    "bearer ",
    "-----begin private key-----",
    "cookie:",
    "set-cookie:",
)

JsonObject = dict[str, object]


class ProviderEvidenceError(ValueError):
    """The provider-evidence manifest violates its preregistered boundary."""


def _fixed_permissions() -> JsonObject:
    return {
        "production_provider_access_permitted": False,
        "production_storage_mutation_permitted": False,
        "runtime_adapter_execution_permitted": False,
        "workflow_activation_permitted": False,
        "history_construction_permitted": False,
        "temporal_state_fitting_permitted": False,
        "training_permitted": False,
        "outcome_access_permitted": False,
        "model_fitting_performed": False,
        "mm1_execution_permitted": False,
        "scientific_status": SCIENTIFIC_STATUS,
    }


def _expected_manifest() -> JsonObject:
    return {
        "schema_version": MANIFEST_SCHEMA,
        "graph": GRAPH,
        "registered_contract": {
            "path": CONTRACT_PATH,
            "sha256": CONTRACT_SHA256,
            "registration_commit": REGISTRATION_COMMIT,
            "parent_integration": PARENT_INTEGRATION,
        },
        "sources": [
            {
                "role": "api_documentation",
                "url": "https://site.financialmodelingprep.com/developer/docs",
                "observed_on": "2026-09-12",
                "authority": "OFFICIAL_PUBLIC",
                "snapshot_immutable": False,
                "provider_last_updated": None,
            },
            {
                "role": "commercial_pricing",
                "url": "https://site.financialmodelingprep.com/developer/docs/pricing?planType=commercial",
                "observed_on": "2026-09-12",
                "authority": "OFFICIAL_PUBLIC",
                "snapshot_immutable": False,
                "provider_last_updated": None,
            },
            {
                "role": "terms_of_service",
                "url": "https://site.financialmodelingprep.com/terms-of-service",
                "observed_on": "2026-09-12",
                "authority": "OFFICIAL_PUBLIC",
                "snapshot_immutable": False,
                "provider_last_updated": "2023-08-01",
            },
        ],
        "endpoints": [
            {
                "role": "fmp_articles",
                "endpoint": "https://financialmodelingprep.com/stable/fmp-articles",
                "example_query": "?page=0&limit=20",
                "latest_feed_documented": True,
                "page_parameter_documented": True,
                "limit_parameter_documented": True,
            },
            {
                "role": "general_latest",
                "endpoint": "https://financialmodelingprep.com/stable/news/general-latest",
                "example_query": "?page=0&limit=20",
                "latest_feed_documented": True,
                "page_parameter_documented": True,
                "limit_parameter_documented": True,
            },
            {
                "role": "stock_latest",
                "endpoint": "https://financialmodelingprep.com/stable/news/stock-latest",
                "example_query": "?page=0&limit=20",
                "latest_feed_documented": True,
                "page_parameter_documented": True,
                "limit_parameter_documented": True,
            },
        ],
        "semantics": {
            "date_window_equivalent_documented": False,
            "ordering_stability_documented": False,
            "terminal_page_rule_documented": False,
            "short_page_exhaustion_documented": False,
            "empty_page_exhaustion_documented": False,
            "repeated_page_exhaustion_documented": False,
            "revision_semantics_documented": False,
            "late_arrival_semantics_documented": False,
            "decision_interval_completeness_documented": False,
            "provider_observation_clock_authenticated": False,
            "live_probe_permitted": False,
        },
        "rights": {
            "account_entitlement_evidence_present": False,
            "account_or_order_scope_required_by_public_terms": True,
            "personal_copy_download_requires_prior_approval": True,
            "display_redistribution_specific_agreement_required": True,
            "stored_data_security_controls_required": True,
            "termination_deletion_obligation_documented": True,
            "exact_payload_storage_authorized": False,
            "research_retention_authorized": False,
            "redistribution_authorized": False,
            "termination_retention_authorized": False,
        },
        "unresolved_gates": [
            {
                "gate": "ACCOUNT_ENTITLEMENT",
                "evidence_class": "ACCOUNT_OR_WRITTEN_PROVIDER_EVIDENCE",
            },
            {
                "gate": "DATE_WINDOW_SEMANTICS",
                "evidence_class": "LIVE_PROVIDER_SEMANTICS_PROBE",
            },
            {
                "gate": "EXHAUSTION_SEMANTICS",
                "evidence_class": "LIVE_PROVIDER_SEMANTICS_PROBE",
            },
            {
                "gate": "ORDERING_STABILITY",
                "evidence_class": "LIVE_PROVIDER_SEMANTICS_PROBE",
            },
            {
                "gate": "REVISION_LATE_ARRIVAL_SEMANTICS",
                "evidence_class": "LIVE_PROVIDER_SEMANTICS_PROBE",
            },
            {
                "gate": "STORAGE_RETENTION_RIGHTS",
                "evidence_class": "ACCOUNT_OR_WRITTEN_PROVIDER_EVIDENCE",
            },
        ],
        "permissions": _fixed_permissions(),
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


def assert_no_secret_material(value: object) -> None:
    """Reject secret-shaped material without echoing it."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_SECRET_FRAGMENTS):
            raise ProviderEvidenceError("manifest contains forbidden secret material")


def _normalize_role_list(value: object, label: str, key: str) -> list[object]:
    if not isinstance(value, list):
        raise ProviderEvidenceError(f"{label}: expected list")
    copied: list[JsonObject] = []
    for item in value:
        if not isinstance(item, dict):
            raise ProviderEvidenceError(f"{label}: invalid item")
        entry = cast(JsonObject, item)
        marker = entry.get(key)
        if not isinstance(marker, str):
            raise ProviderEvidenceError(f"{label}: invalid item")
        copied.append(dict(entry))
    copied.sort(key=lambda item: cast(str, item[key]))
    return cast(list[object], copied)


def _normalize_payload(payload: object) -> JsonObject:
    if not isinstance(payload, dict):
        raise ProviderEvidenceError("manifest: expected object")
    root = cast(JsonObject, payload)
    expected = _expected_manifest()
    if set(root) != set(expected):
        raise ProviderEvidenceError("manifest: unexpected keys")
    normalized = dict(root)
    normalized["sources"] = _normalize_role_list(root["sources"], "sources", "role")
    normalized["endpoints"] = _normalize_role_list(
        root["endpoints"], "endpoints", "role"
    )
    normalized["unresolved_gates"] = _normalize_role_list(
        root["unresolved_gates"], "unresolved_gates", "gate"
    )
    return normalized


def _compare_exact(actual: object, expected: object, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise ProviderEvidenceError(f"{label}: expected object")
        actual_object = cast(JsonObject, actual)
        expected_object = cast(JsonObject, expected)
        if set(actual_object) != set(expected_object):
            raise ProviderEvidenceError(f"{label}: unexpected keys")
        for key in expected_object:
            _compare_exact(
                actual_object[key],
                expected_object[key],
                f"{label}.{key}" if label else key,
            )
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ProviderEvidenceError(f"{label}: registered value mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            _compare_exact(left, right, f"{label}[{index}]")
        return
    if type(actual) is not type(expected) or actual != expected:
        if expected is False and actual is True:
            raise ProviderEvidenceError(f"{label}: promotion forbidden")
        raise ProviderEvidenceError(f"{label}: registered value mismatch")


@dataclass(frozen=True, slots=True)
class NormalizedProviderEvidenceManifest:
    """Detached immutable canonical evidence manifest."""

    canonical_json: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


@dataclass(frozen=True, slots=True)
class ProviderEvidenceReview:
    """Aggregate documentary review; operational/scientific gates remain blocked."""

    manifest_sha256: str

    def to_dict(self) -> JsonObject:
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "engineering_status": ENGINEERING_STATUS,
            "documentary_endpoint_identity_status": "PASS",
            "documentary_pagination_parameter_status": "PASS",
            "provider_request_semantics_status": "BLOCKED",
            "account_entitlement_status": "BLOCKED",
            "activation_readiness_status": "BLOCKED",
            "bindings": {
                "parent_integration": PARENT_INTEGRATION,
                "registration_commit": REGISTRATION_COMMIT,
                "contract_sha256": CONTRACT_SHA256,
                "manifest_sha256": self.manifest_sha256,
            },
            "documentary_evidence": {
                "official_public_sources": 3,
                "registered_endpoints": 3,
                "latest_feed_roles_documented": 3,
                "page_parameter_roles_documented": 3,
                "limit_parameter_roles_documented": 3,
            },
            "blocked_semantics": {
                "date_window_equivalent": True,
                "ordering_stability": True,
                "terminal_page_rule": True,
                "revision_late_arrival": True,
                "decision_interval_completeness": True,
                "provider_observation_clock": True,
            },
            "blocked_rights": {
                "account_entitlement": True,
                "exact_payload_storage": True,
                "research_retention": True,
                "redistribution": True,
                "termination_retention": True,
            },
            "unresolved_gate_count": 6,
            "permissions": _fixed_permissions(),
        }


def normalize_provider_evidence_manifest(
    payload: object,
) -> NormalizedProviderEvidenceManifest:
    """Validate exact v0 documentary evidence and return canonical state."""

    assert_no_secret_material(payload)
    normalized = _normalize_payload(payload)
    expected = _normalize_payload(_expected_manifest())
    _compare_exact(normalized, expected, "")
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
    return NormalizedProviderEvidenceManifest(canonical)


def canonical_manifest_bytes(manifest: NormalizedProviderEvidenceManifest) -> bytes:
    """Return the exact canonical manifest representation."""

    return manifest.canonical_json.encode("utf-8")


def review_manifest(payload: object) -> ProviderEvidenceReview:
    """Run the fixed pure provider-evidence graph."""

    normalized = normalize_provider_evidence_manifest(payload)
    digest = hashlib.sha256(canonical_manifest_bytes(normalized)).hexdigest()
    return ProviderEvidenceReview(digest)


def serialize_review(review: ProviderEvidenceReview) -> str:
    """Serialize aggregate-only evidence."""

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
