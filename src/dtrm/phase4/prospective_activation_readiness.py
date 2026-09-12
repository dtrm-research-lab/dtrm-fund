"""Pure validator for Phase-IV prospective activation readiness v0."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_prospective_activation_readiness_v0"
MANIFEST_SCHEMA = "dtrm.phase4.prospective_activation_readiness_manifest.v0"
REPORT_SCHEMA = "dtrm.phase4.prospective_activation_readiness_review.v0"
ENGINEERING_STATUS = "PASS_PROSPECTIVE_ACTIVATION_READINESS_REVIEW"
READINESS_STATUS = "BLOCKED"
SCIENTIFIC_STATUS = "BLOCKED_PROSPECTIVE_DEPLOYMENT"

CONTRACT_PATH = "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_READINESS_V0.md"
CONTRACT_SHA256 = "81b653ffec1044e27dbaa009349cfa55ee60a2a1e895815b4eb430129fff0ccd"
REGISTRATION_COMMIT = "dde70ab0e58a9c48ba1be0dc2894ac0d2b435e18"
PARENT_INTEGRATION = "cdd78c38f8b543bc8a06f6fbca5f852926682621"

WRITER_MERGE_COMMIT = "e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5"
WRITER_MERGE_TREE = "2b5422f554119ecf48663d5506d9fdd38ab7738f"
WRITER_FILES = (
    (
        "adr_causality",
        "docs/architecture/ADR-017B-phase4-prior-state-causality-v0.md",
        "ee2d18c88ef7895b93afa4497007352f5b83036e",
    ),
    (
        "adr_clock",
        "docs/architecture/ADR-017A-phase4-prospective-news-clock-binding-v0.md",
        "8886f1faec2082d86699ac171fb4ff1490ab518c",
    ),
    (
        "adr_shadow",
        "docs/architecture/ADR-017-phase4-prospective-news-shadow-v0.md",
        "c273bf34555f4bc3f188a0b8b379b0d02264cb79",
    ),
    (
        "application_orchestrator",
        "src/theresistance_backend/application/plan_prospective_news_capture.py",
        "032490dca027a2b718f47f9ac57d3b843c00f9bf",
    ),
    (
        "domain_graph",
        "src/theresistance_backend/domains/markets/prospective_news.py",
        "aed46c420059642ff1fa4558c07b3532f4adf911",
    ),
    (
        "ports",
        "src/theresistance_backend/ports/prospective_news.py",
        "2f25d135a2c9af983f86627e8482a4d59e282eba",
    ),
)
PROVIDER_ROLES = (
    ("fmp_articles", "https://financialmodelingprep.com/stable/fmp-articles"),
    ("general_latest", "https://financialmodelingprep.com/stable/news/general-latest"),
    ("stock_latest", "https://financialmodelingprep.com/stable/news/stock-latest"),
)

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


class ActivationReadinessError(ValueError):
    """The readiness manifest violates its preregistered boundary."""


def _fixed_permissions() -> JsonObject:
    return {
        "readiness_status": READINESS_STATUS,
        "activation_permitted": False,
        "production_source_access_permitted": False,
        "production_storage_mutation_permitted": False,
        "source_authenticated": False,
        "clock_authenticated": False,
        "coverage_authenticated": False,
        "history_construction_permitted": False,
        "training_permitted": False,
        "outcome_access_permitted": False,
        "model_fitting_performed": False,
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
        "dormant_writer": {
            "repository": "tech-com-UA00001/theresistance-back",
            "repository_id": 1128196792,
            "branch": "main",
            "merge_commit": WRITER_MERGE_COMMIT,
            "merge_tree": WRITER_MERGE_TREE,
            "validated_feature_head": "9eab8ee4b6ac9f7a0f67550a0e75e2489a5bc7d7",
            "pinned_parent": "7a8107e4451891535366acaf766348785ccc157b",
            "files": [
                {"role": role, "path": path, "blob_sha": blob}
                for role, path, blob in WRITER_FILES
            ],
        },
        "provider": {
            "observed_on": "2026-09-12",
            "documentation_url": "https://site.financialmodelingprep.com/developer/docs/stable",
            "endpoint_identity_status": "DOCUMENTED",
            "roles": [
                {"role": role, "endpoint": endpoint}
                for role, endpoint in PROVIDER_ROLES
            ],
            "page_limit_example_documented": True,
            "request_semantics_authenticated": False,
            "bounded_exhaustion_authenticated": False,
        },
        "licence": {
            "observed_on": "2026-09-12",
            "terms_url": "https://site.financialmodelingprep.com/terms-of-service",
            "account_specific_evidence_present": False,
            "public_terms_account_or_order_scope": True,
            "public_terms_copy_download_restriction_without_prior_approval": True,
            "licence_retention_authorized": False,
            "exact_payload_storage_authorized": False,
            "retain_through_phase4_evaluation": True,
            "proposed_minimum_years_after_final_artifact": 5,
        },
        "storage": {
            "database": "trumpMinMax",
            "event_collection": "phase4ProspectiveNewsV0",
            "run_collection": "phase4ProspectiveRunsV0",
            "legacy_collection": "trumpNews",
            "storage_schema_provisioned": False,
            "runtime_schema_mutation_permitted": False,
        },
        "authority": {
            "least_privilege_credential_provisioned": False,
            "writer_authority_enumerated": False,
            "secret_material_permitted": False,
        },
        "runtime": {
            "runtime_adapter_validated": False,
            "workflow_activation_ready": False,
            "workflow_enabled": False,
            "prospective_start_registered": False,
        },
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
    """Reject direct secret-shaped material without echoing it."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_SECRET_FRAGMENTS):
            raise ActivationReadinessError("manifest contains forbidden secret material")


def _normalize_unordered_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ActivationReadinessError(f"{label}: expected list")
    copied: list[JsonObject] = []
    for item in value:
        if not isinstance(item, dict):
            raise ActivationReadinessError(f"{label}: invalid item")
        entry = cast(JsonObject, item)
        role = entry.get("role")
        if not isinstance(role, str):
            raise ActivationReadinessError(f"{label}: invalid item")
        copied.append(dict(entry))
    copied.sort(key=lambda item: cast(str, item["role"]))
    return cast(list[object], copied)


def _normalize_payload(payload: object) -> JsonObject:
    if not isinstance(payload, dict):
        raise ActivationReadinessError("manifest: expected object")
    root = cast(JsonObject, payload)
    expected = _expected_manifest()
    if set(root) != set(expected):
        raise ActivationReadinessError("manifest: unexpected keys")
    normalized = dict(root)

    writer = root["dormant_writer"]
    provider = root["provider"]
    if not isinstance(writer, dict) or not isinstance(provider, dict):
        raise ActivationReadinessError("manifest: invalid nested object")
    writer_copy = dict(cast(JsonObject, writer))
    provider_copy = dict(cast(JsonObject, provider))
    writer_copy["files"] = _normalize_unordered_list(
        writer_copy.get("files"), "dormant_writer.files"
    )
    provider_copy["roles"] = _normalize_unordered_list(
        provider_copy.get("roles"), "provider.roles"
    )
    normalized["dormant_writer"] = writer_copy
    normalized["provider"] = provider_copy
    return normalized


def _compare_exact(actual: object, expected: object, label: str) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise ActivationReadinessError(f"{label}: expected object")
        actual_object = cast(JsonObject, actual)
        expected_object = cast(JsonObject, expected)
        if set(actual_object) != set(expected_object):
            raise ActivationReadinessError(f"{label}: unexpected keys")
        for key in expected_object:
            _compare_exact(
                actual_object[key],
                expected_object[key],
                f"{label}.{key}" if label else key,
            )
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ActivationReadinessError(f"{label}: registered value mismatch")
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            _compare_exact(left, right, f"{label}[{index}]")
        return
    if type(actual) is not type(expected) or actual != expected:
        if expected is False and actual is True:
            raise ActivationReadinessError(f"{label}: promotion forbidden")
        raise ActivationReadinessError(f"{label}: registered value mismatch")


@dataclass(frozen=True, slots=True)
class NormalizedReadinessManifest:
    """Detached immutable canonical manifest."""

    canonical_json: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))


@dataclass(frozen=True, slots=True)
class ActivationReadinessReview:
    """Aggregate-only readiness result; v0 can only remain blocked."""

    manifest_sha256: str

    def to_dict(self) -> JsonObject:
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "engineering_status": ENGINEERING_STATUS,
            "readiness_status": READINESS_STATUS,
            "bindings": {
                "scientific_parent_integration": PARENT_INTEGRATION,
                "registration_commit": REGISTRATION_COMMIT,
                "contract_sha256": CONTRACT_SHA256,
                "manifest_sha256": self.manifest_sha256,
                "writer_merge_commit": WRITER_MERGE_COMMIT,
                "writer_merge_tree": WRITER_MERGE_TREE,
            },
            "provider": {
                "endpoint_identity_status": "DOCUMENTED",
                "registered_roles": len(PROVIDER_ROLES),
                "page_limit_example_documented": True,
                "request_semantics_authenticated": False,
                "bounded_exhaustion_authenticated": False,
            },
            "readiness_gates": {
                "licence_retention_authorized": False,
                "storage_schema_provisioned": False,
                "least_privilege_credential_provisioned": False,
                "writer_authority_enumerated": False,
                "runtime_adapter_validated": False,
                "workflow_activation_ready": False,
                "prospective_start_registered": False,
            },
            "permissions": _fixed_permissions(),
        }


def normalize_readiness_manifest(payload: object) -> NormalizedReadinessManifest:
    """Validate exact v0 readiness evidence and return detached canonical state."""

    assert_no_secret_material(payload)
    normalized = _normalize_payload(payload)
    _compare_exact(normalized, _expected_manifest(), "")
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
    return NormalizedReadinessManifest(canonical)


def canonical_manifest_bytes(manifest: NormalizedReadinessManifest) -> bytes:
    """Return the exact canonical manifest representation."""

    return manifest.canonical_json.encode("utf-8")


def review_manifest(payload: object) -> ActivationReadinessReview:
    """Run the fixed pure readiness graph."""

    manifest = normalize_readiness_manifest(payload)
    digest = hashlib.sha256(canonical_manifest_bytes(manifest)).hexdigest()
    return ActivationReadinessReview(digest)


def serialize_review(review: ActivationReadinessReview) -> str:
    """Serialize aggregate-only readiness evidence."""

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
