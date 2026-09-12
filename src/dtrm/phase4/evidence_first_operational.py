"""Pure validator for the Phase-IV evidence-first operational amendment v0."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_evidence_first_operational_v0"
STATEMENT_SCHEMA = "dtrm.phase4.evidence_first_operational.v0"
REPORT_SCHEMA = "dtrm.phase4.evidence_first_operational_report.v0"
ENGINEERING_STATUS = "PASS_EVIDENCE_FIRST_OPERATIONAL_AMENDMENT"
SCIENTIFIC_EVIDENCE_STATUS = "AUTHORIZED_PROSPECTIVE_EVIDENCE_CAPTURE"
PROVIDER_RIGHTS_STATUS = "DEFERRED_UNRESOLVED_PENDING_VALUE_ASSESSMENT"

CONTRACT_PATH = (
    "research/contracts/DTRM_PHASE4_EVIDENCE_FIRST_OPERATIONAL_AMENDMENT_V0.md"
)
CONTRACT_BLOB_SHA = "f80dd1838eb491ed7d0695af1c423c870eef687c"
REGISTRATION_COMMIT = "0a0d2282d2786cb66f34d047dd864874c8df3ed4"
PARENT_INTEGRATION = "c5f5f16d103222e51914140f257f0922966188d1"
BACKEND_REPOSITORY = "tech-com-UA00001/theresistance-back"
BACKEND_COMMIT = "e6f60c6eaf74a9f4354ca7f9f6aff6dfdd80f8a5"
BACKEND_TREE = "2b5422f554119ecf48663d5506d9fdd38ab7738f"

EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
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
    "-----begin private key-----",
)

JsonObject = dict[str, object]


class EvidenceFirstOperationalError(ValueError):
    """The evidence-first statement violates the preregistered boundary."""


def _expected_registered_contract() -> JsonObject:
    return {
        "path": CONTRACT_PATH,
        "blob_sha": CONTRACT_BLOB_SHA,
        "registration_commit": REGISTRATION_COMMIT,
        "parent_integration": PARENT_INTEGRATION,
    }


def _expected_backend_binding() -> JsonObject:
    return {
        "repository": BACKEND_REPOSITORY,
        "commit": BACKEND_COMMIT,
        "tree": BACKEND_TREE,
    }


def _expected_provider_roles() -> JsonObject:
    return {
        "fmp_articles": "https://financialmodelingprep.com/stable/fmp-articles",
        "general_latest": "https://financialmodelingprep.com/stable/news/general-latest",
        "stock_latest": "https://financialmodelingprep.com/stable/news/stock-latest",
    }


def _expected_safety_bounds() -> JsonObject:
    return {
        "max_pages_per_role": 100,
        "max_candidates_per_run": 25000,
        "max_new_versions_per_run": 5000,
        "max_payload_bytes_per_candidate": 1048576,
    }


def _expected_permissions() -> JsonObject:
    return {
        "live_provider_probe_permitted": True,
        "private_raw_evidence_capture_permitted": True,
        "private_raw_evidence_processing_permitted": True,
        "public_raw_provider_data_redistribution_permitted": False,
        "confirmatory_history_construction_permitted": False,
        "temporal_state_outcome_fitting_permitted": False,
        "outcome_access_permitted": False,
        "mm1_execution_permitted": False,
        "phase3_policy_mutation_permitted": False,
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
    """Reject secret-shaped material without echoing the rejected value."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_FRAGMENTS):
            raise EvidenceFirstOperationalError("statement contains forbidden sensitive material")
        if EMAIL_RE.search(text):
            raise EvidenceFirstOperationalError("statement contains forbidden sensitive material")


def _require_exact_object(value: object, expected: JsonObject, label: str) -> JsonObject:
    if not isinstance(value, dict):
        raise EvidenceFirstOperationalError(f"{label}: expected object")
    mapping = cast(JsonObject, value)
    if set(mapping) != set(expected):
        raise EvidenceFirstOperationalError(f"{label}: unexpected keys")
    for key, expected_value in expected.items():
        actual = mapping[key]
        if type(actual) is not type(expected_value) or actual != expected_value:
            raise EvidenceFirstOperationalError(f"{label}.{key}: registered value mismatch")
    return dict(mapping)


@dataclass(frozen=True, slots=True)
class NormalizedEvidenceFirstOperational:
    """Detached immutable canonical evidence-first statement."""

    canonical_json: str

    def to_dict(self) -> JsonObject:
        return cast(JsonObject, json.loads(self.canonical_json))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json.encode("utf-8")).hexdigest()


def normalize_evidence_first_operational(payload: object) -> NormalizedEvidenceFirstOperational:
    """Validate and canonicalize the fixed evidence-first operational state."""

    assert_no_sensitive_material(payload)
    if not isinstance(payload, dict):
        raise EvidenceFirstOperationalError("statement: expected object")
    root = cast(JsonObject, payload)
    expected_keys = {
        "schema_version",
        "graph",
        "registered_contract",
        "backend_binding",
        "provider_scope",
        "scientific_evidence_status",
        "provider_rights_status",
        "provider_roles",
        "safety_bounds",
        "permissions",
    }
    if set(root) != expected_keys:
        raise EvidenceFirstOperationalError("statement: unexpected keys")

    fixed_scalars: dict[str, str] = {
        "schema_version": STATEMENT_SCHEMA,
        "graph": GRAPH,
        "provider_scope": "FINANCIAL_MODELING_PREP",
        "scientific_evidence_status": SCIENTIFIC_EVIDENCE_STATUS,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
    }
    for key, expected in fixed_scalars.items():
        if root[key] != expected:
            raise EvidenceFirstOperationalError(f"{key}: registered value mismatch")

    _require_exact_object(
        root["registered_contract"], _expected_registered_contract(), "registered_contract"
    )
    _require_exact_object(root["backend_binding"], _expected_backend_binding(), "backend_binding")
    _require_exact_object(root["provider_roles"], _expected_provider_roles(), "provider_roles")
    _require_exact_object(root["safety_bounds"], _expected_safety_bounds(), "safety_bounds")
    _require_exact_object(root["permissions"], _expected_permissions(), "permissions")

    canonical = json.dumps(root, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return NormalizedEvidenceFirstOperational(canonical_json=canonical)


def build_evidence_first_report(
    state: NormalizedEvidenceFirstOperational,
) -> JsonObject:
    """Build the aggregate report without raw provider data or secret material."""

    return {
        "schema_version": REPORT_SCHEMA,
        "graph": GRAPH,
        "engineering_status": ENGINEERING_STATUS,
        "scientific_evidence_status": SCIENTIFIC_EVIDENCE_STATUS,
        "provider_rights_status": PROVIDER_RIGHTS_STATUS,
        "statement_sha256": state.sha256,
        "bindings": {
            "parent_integration": PARENT_INTEGRATION,
            "registration_commit": REGISTRATION_COMMIT,
            "contract_blob_sha": CONTRACT_BLOB_SHA,
            "backend_repository": BACKEND_REPOSITORY,
            "backend_commit": BACKEND_COMMIT,
            "backend_tree": BACKEND_TREE,
        },
        "provider_roles": _expected_provider_roles(),
        "safety_bounds": _expected_safety_bounds(),
        "permissions": _expected_permissions(),
    }


def canonical_report_json(payload: object) -> str:
    """Validate a statement and return canonical aggregate report JSON."""

    state = normalize_evidence_first_operational(payload)
    return json.dumps(
        build_evidence_first_report(state),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"
