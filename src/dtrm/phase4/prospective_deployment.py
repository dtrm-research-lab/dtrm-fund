"""Pure validator for the registered prospective deployment contract."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import cast

GRAPH = "phase4_prospective_deployment_contract_v0"
MANIFEST_SCHEMA = "dtrm.phase4.prospective_deployment_manifest.v0"
REPORT_SCHEMA = "dtrm.phase4.prospective_deployment_review.v0"
ENGINEERING_STATUS = "PASS_PROSPECTIVE_DEPLOYMENT_CONTRACT"
SCIENTIFIC_STATUS = "BLOCKED_PROSPECTIVE_DEPLOYMENT"

CONTRACT_PATH = (
    "research/contracts/DTRM_PHASE4_PROSPECTIVE_DEPLOYMENT_CONTRACT_V0.md"
)
CONTRACT_SHA256 = "157aec8cf2cc2ad7f0143d644f2b703744a78ddbee3093baa0110d69b1f6acec"
REGISTRATION_COMMIT = "541d3cacc77a2551aad088ed054f97f4fca6531e"

TARGET_REPOSITORY = "tech-com-UA00001/theresistance-back"
TARGET_REPOSITORY_ID = 1128196792
TARGET_BRANCH = "main"
TARGET_PARENT_COMMIT = "7a8107e4451891535366acaf766348785ccc157b"
TARGET_PARENT_TREE = "f295888372d9ef3c089cc24dd1e72e6b1f2c92cf"
TARGET_FILES = (
    (
        "agent/trump_model/news_collector.py",
        "700e831db5c1d196a8e7c2c1dc6d10148237e710",
        "collector_parent",
    ),
)

PROTOCOLS = (
    (
        "prospective_capture_protocol",
        "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAPTURE_PROTOCOL_V0.md",
        "a343f076a9713b5e1b037cf83ecc864d9bc4308a9592bef0dabeafa00617e629",
        "85c02cca5a477b6c68b43dbac35d517e58f66518",
    ),
    (
        "prospective_capture_synthetic_binding",
        "research/contracts/DTRM_PHASE4_PROSPECTIVE_CAPTURE_SYNTHETIC_BINDING_V0.md",
        "0ec92acb50d3011063db595e6bc026b99bd9847f8d6e4dcc080ab5266ea65e31",
        "d058b02fcf2e28c4987954876433b6efa695ab06",
    ),
)

ALLOWED_OPERATIONS = ("find", "insert")
FORBIDDEN_OPERATIONS = (
    "$merge",
    "$out",
    "bulk_rewrite",
    "delete",
    "drop",
    "index_create",
    "rename",
    "replace",
    "server_javascript",
    "update",
    "upsert",
)
NODES = (
    "normalize_manifest",
    "validate_target_binding",
    "validate_storage_isolation",
    "validate_transaction_policy",
    "validate_clock_coverage_retention",
    "enforce_permission_floor",
    "serialize_review",
)
FORBIDDEN_SECRET_FRAGMENTS = (
    "mongodb://",
    "mongodb+srv://",
    "authorization: bearer",
    "-----begin private key-----",
)


class ProspectiveDeploymentError(ValueError):
    """The deployment manifest violates its preregistered boundary."""


def _object(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ProspectiveDeploymentError(f"{label}: unexpected keys")
    return cast(dict[str, object], value)


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ProspectiveDeploymentError(f"{label}: expected list")
    return value


def _text(value: object, label: str, maximum: int = 240) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
    ):
        raise ProspectiveDeploymentError(f"{label}: invalid text")
    return value


def _sha(value: object, label: str, length: int) -> str:
    text = _text(value, label, maximum=length)
    if not re.fullmatch(rf"[0-9a-f]{{{length}}}", text):
        raise ProspectiveDeploymentError(f"{label}: invalid digest")
    return text


def _integer(value: object, label: str, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ProspectiveDeploymentError(f"{label}: invalid integer")
    return value


def _false(value: object, label: str) -> bool:
    if value is not False:
        raise ProspectiveDeploymentError(f"{label}: promotion forbidden")
    return False


def _true(value: object, label: str) -> bool:
    if value is not True:
        raise ProspectiveDeploymentError(f"{label}: required invariant missing")
    return True


def _exact(value: object, expected: str, label: str) -> str:
    if _text(value, label) != expected:
        raise ProspectiveDeploymentError(f"{label}: registered value mismatch")
    return expected


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
    """Reject connection strings and direct authorization material."""

    for value_text in _walk_strings(value):
        lowered = value_text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_SECRET_FRAGMENTS):
            raise ProspectiveDeploymentError("manifest contains forbidden secret material")


@dataclass(frozen=True, slots=True)
class RegisteredContract:
    path: str
    sha256: str
    registration_commit: str

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "registration_commit": self.registration_commit,
        }


@dataclass(frozen=True, slots=True)
class TargetFile:
    path: str
    blob_sha: str
    role: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "blob_sha": self.blob_sha, "role": self.role}


@dataclass(frozen=True, slots=True)
class TargetWriter:
    repository: str
    repository_id: int
    branch: str
    parent_commit: str
    parent_tree: str
    files: tuple[TargetFile, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "repository_id": self.repository_id,
            "branch": self.branch,
            "parent_commit": self.parent_commit,
            "parent_tree": self.parent_tree,
            "files": [item.to_dict() for item in self.files],
        }


@dataclass(frozen=True, slots=True)
class ProtocolBinding:
    role: str
    path: str
    sha256: str
    registration_commit: str

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role,
            "path": self.path,
            "sha256": self.sha256,
            "registration_commit": self.registration_commit,
        }


@dataclass(frozen=True, slots=True)
class StoragePolicy:
    database: str
    event_collection: str
    run_collection: str
    legacy_collection: str
    runtime_allowed_operations: tuple[str, ...]
    runtime_forbidden_operations: tuple[str, ...]
    runtime_schema_mutation_permitted: bool
    legacy_writer_permissions: str

    def to_dict(self) -> dict[str, object]:
        return {
            "database": self.database,
            "event_collection": self.event_collection,
            "run_collection": self.run_collection,
            "legacy_collection": self.legacy_collection,
            "runtime_allowed_operations": list(self.runtime_allowed_operations),
            "runtime_forbidden_operations": list(self.runtime_forbidden_operations),
            "runtime_schema_mutation_permitted": self.runtime_schema_mutation_permitted,
            "legacy_writer_permissions": self.legacy_writer_permissions,
        }


@dataclass(frozen=True, slots=True)
class TransactionPolicy:
    read_concern: str
    write_concern: str
    journaled: bool
    manifest_inserted_last: bool
    all_or_nothing: bool
    zero_version_manifest_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "read_concern": self.read_concern,
            "write_concern": self.write_concern,
            "journaled": self.journaled,
            "manifest_inserted_last": self.manifest_inserted_last,
            "all_or_nothing": self.all_or_nothing,
            "zero_version_manifest_required": self.zero_version_manifest_required,
        }


@dataclass(frozen=True, slots=True)
class ClockPolicy:
    policy: str
    completed_at_semantics: str
    workflow_completion_is_later_bound: bool
    authenticated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "policy": self.policy,
            "completed_at_semantics": self.completed_at_semantics,
            "workflow_completion_is_later_bound": self.workflow_completion_is_later_bound,
            "authenticated": self.authenticated,
        }


@dataclass(frozen=True, slots=True)
class CoveragePolicy:
    overlap_complete_utc_days: int
    include_current_partial_day: bool
    max_pages_per_role: int
    max_candidates_per_run: int
    max_new_versions_per_run: int
    max_payload_bytes_per_candidate: int
    bound_exhaustion_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "overlap_complete_utc_days": self.overlap_complete_utc_days,
            "include_current_partial_day": self.include_current_partial_day,
            "max_pages_per_role": self.max_pages_per_role,
            "max_candidates_per_run": self.max_candidates_per_run,
            "max_new_versions_per_run": self.max_new_versions_per_run,
            "max_payload_bytes_per_candidate": self.max_payload_bytes_per_candidate,
            "bound_exhaustion_action": self.bound_exhaustion_action,
        }


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    retain_through_phase4_evaluation: bool
    minimum_years_after_final_artifact: int
    licence_review_required_before_activation: bool
    conflict_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "retain_through_phase4_evaluation": self.retain_through_phase4_evaluation,
            "minimum_years_after_final_artifact": self.minimum_years_after_final_artifact,
            "licence_review_required_before_activation": (
                self.licence_review_required_before_activation
            ),
            "conflict_action": self.conflict_action,
        }


@dataclass(frozen=True, slots=True)
class RuntimePolicy:
    implementation_mode: str
    credential_scope: str
    environment_inspection_permitted: bool
    provider_access_permitted: bool
    storage_access_permitted: bool
    workflow_enabled: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "implementation_mode": self.implementation_mode,
            "credential_scope": self.credential_scope,
            "environment_inspection_permitted": self.environment_inspection_permitted,
            "provider_access_permitted": self.provider_access_permitted,
            "storage_access_permitted": self.storage_access_permitted,
            "workflow_enabled": self.workflow_enabled,
        }


@dataclass(frozen=True, slots=True)
class PermissionPolicy:
    implementation_permitted: bool
    activation_permitted: bool
    production_source_access_permitted: bool
    production_storage_mutation_permitted: bool
    source_authenticated: bool
    clock_authenticated: bool
    coverage_authenticated: bool
    history_construction_permitted: bool
    training_permitted: bool
    outcome_access_permitted: bool
    model_fitting_performed: bool
    scientific_status: str

    def to_dict(self) -> dict[str, object]:
        return {
            "implementation_permitted": self.implementation_permitted,
            "activation_permitted": self.activation_permitted,
            "production_source_access_permitted": self.production_source_access_permitted,
            "production_storage_mutation_permitted": (
                self.production_storage_mutation_permitted
            ),
            "source_authenticated": self.source_authenticated,
            "clock_authenticated": self.clock_authenticated,
            "coverage_authenticated": self.coverage_authenticated,
            "history_construction_permitted": self.history_construction_permitted,
            "training_permitted": self.training_permitted,
            "outcome_access_permitted": self.outcome_access_permitted,
            "model_fitting_performed": self.model_fitting_performed,
            "scientific_status": self.scientific_status,
        }


@dataclass(frozen=True, slots=True)
class DeploymentManifest:
    registered_contract: RegisteredContract
    target_writer: TargetWriter
    protocols: tuple[ProtocolBinding, ...]
    storage: StoragePolicy
    transaction: TransactionPolicy
    clock: ClockPolicy
    coverage: CoveragePolicy
    retention: RetentionPolicy
    runtime: RuntimePolicy
    permissions: PermissionPolicy

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": MANIFEST_SCHEMA,
            "graph": GRAPH,
            "registered_contract": self.registered_contract.to_dict(),
            "target_writer": self.target_writer.to_dict(),
            "protocols": [item.to_dict() for item in self.protocols],
            "storage": self.storage.to_dict(),
            "transaction": self.transaction.to_dict(),
            "clock": self.clock.to_dict(),
            "coverage": self.coverage.to_dict(),
            "retention": self.retention.to_dict(),
            "runtime": self.runtime.to_dict(),
            "permissions": self.permissions.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class DeploymentAssessment:
    manifest_sha256: str
    target_writer: TargetWriter
    storage: StoragePolicy
    coverage: CoveragePolicy
    permissions: PermissionPolicy

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": REPORT_SCHEMA,
            "graph": GRAPH,
            "registered_contract": {
                "path": CONTRACT_PATH,
                "sha256": CONTRACT_SHA256,
                "registration_commit": REGISTRATION_COMMIT,
            },
            "completed_nodes": list(NODES),
            "manifest_sha256": self.manifest_sha256,
            "target": {
                "repository": self.target_writer.repository,
                "repository_id": self.target_writer.repository_id,
                "parent_commit": self.target_writer.parent_commit,
                "parent_tree": self.target_writer.parent_tree,
                "selected_file_count": len(self.target_writer.files),
            },
            "isolation": {
                "database": self.storage.database,
                "event_collection": self.storage.event_collection,
                "run_collection": self.storage.run_collection,
                "legacy_collection": self.storage.legacy_collection,
                "legacy_writer_permissions": self.storage.legacy_writer_permissions,
            },
            "operational_limits": self.coverage.to_dict(),
            "engineering_status": ENGINEERING_STATUS,
            **self.permissions.to_dict(),
        }


def _registered_contract(value: object) -> RegisteredContract:
    item = _object(value, {"path", "sha256", "registration_commit"}, "contract")
    return RegisteredContract(
        _exact(item["path"], CONTRACT_PATH, "contract.path"),
        _exact(item["sha256"], CONTRACT_SHA256, "contract.sha256"),
        _exact(
            item["registration_commit"],
            REGISTRATION_COMMIT,
            "contract.registration_commit",
        ),
    )


def _target_writer(value: object) -> TargetWriter:
    item = _object(
        value,
        {"repository", "repository_id", "branch", "parent_commit", "parent_tree", "files"},
        "target_writer",
    )
    files: list[TargetFile] = []
    for raw in _list(item["files"], "target_writer.files"):
        file_item = _object(raw, {"path", "blob_sha", "role"}, "target_writer.file")
        files.append(
            TargetFile(
                _text(file_item["path"], "target_writer.file.path"),
                _sha(file_item["blob_sha"], "target_writer.file.blob_sha", 40),
                _text(file_item["role"], "target_writer.file.role"),
            )
        )
    files.sort(key=lambda entry: entry.path)
    actual = tuple((entry.path, entry.blob_sha, entry.role) for entry in files)
    if actual != TARGET_FILES:
        raise ProspectiveDeploymentError("target_writer.files: registered value mismatch")
    repository_id = _integer(item["repository_id"], "target_writer.repository_id")
    if repository_id != TARGET_REPOSITORY_ID:
        raise ProspectiveDeploymentError("target_writer.repository_id: registered value mismatch")
    return TargetWriter(
        _exact(item["repository"], TARGET_REPOSITORY, "target_writer.repository"),
        repository_id,
        _exact(item["branch"], TARGET_BRANCH, "target_writer.branch"),
        _exact(item["parent_commit"], TARGET_PARENT_COMMIT, "target_writer.parent_commit"),
        _exact(item["parent_tree"], TARGET_PARENT_TREE, "target_writer.parent_tree"),
        tuple(files),
    )


def _protocols(value: object) -> tuple[ProtocolBinding, ...]:
    entries: list[ProtocolBinding] = []
    for raw in _list(value, "protocols"):
        item = _object(raw, {"role", "path", "sha256", "registration_commit"}, "protocol")
        entries.append(
            ProtocolBinding(
                _text(item["role"], "protocol.role"),
                _text(item["path"], "protocol.path"),
                _sha(item["sha256"], "protocol.sha256", 64),
                _sha(item["registration_commit"], "protocol.registration_commit", 40),
            )
        )
    entries.sort(key=lambda entry: entry.role)
    actual = tuple(
        (entry.role, entry.path, entry.sha256, entry.registration_commit)
        for entry in entries
    )
    if actual != PROTOCOLS:
        raise ProspectiveDeploymentError("protocols: registered value mismatch")
    return tuple(entries)


def _exact_string_list(value: object, expected: tuple[str, ...], label: str) -> tuple[str, ...]:
    values = tuple(sorted(_text(item, label) for item in _list(value, label)))
    if values != expected:
        raise ProspectiveDeploymentError(f"{label}: registered value mismatch")
    return values


def _storage(value: object) -> StoragePolicy:
    item = _object(
        value,
        {
            "database",
            "event_collection",
            "run_collection",
            "legacy_collection",
            "runtime_allowed_operations",
            "runtime_forbidden_operations",
            "runtime_schema_mutation_permitted",
            "legacy_writer_permissions",
        },
        "storage",
    )
    event_collection = _exact(
        item["event_collection"], "phase4ProspectiveNewsV0", "storage.event_collection"
    )
    run_collection = _exact(
        item["run_collection"], "phase4ProspectiveRunsV0", "storage.run_collection"
    )
    legacy_collection = _exact(
        item["legacy_collection"], "trumpNews", "storage.legacy_collection"
    )
    if len({event_collection, run_collection, legacy_collection}) != 3:
        raise ProspectiveDeploymentError("storage: collections must be isolated")
    return StoragePolicy(
        _exact(item["database"], "trumpMinMax", "storage.database"),
        event_collection,
        run_collection,
        legacy_collection,
        _exact_string_list(
            item["runtime_allowed_operations"], ALLOWED_OPERATIONS, "storage.allowed"
        ),
        _exact_string_list(
            item["runtime_forbidden_operations"], FORBIDDEN_OPERATIONS, "storage.forbidden"
        ),
        _false(
            item["runtime_schema_mutation_permitted"],
            "storage.runtime_schema_mutation_permitted",
        ),
        _exact(item["legacy_writer_permissions"], "none", "storage.legacy_writer_permissions"),
    )


def _transaction(value: object) -> TransactionPolicy:
    item = _object(
        value,
        {
            "read_concern",
            "write_concern",
            "journaled",
            "manifest_inserted_last",
            "all_or_nothing",
            "zero_version_manifest_required",
        },
        "transaction",
    )
    return TransactionPolicy(
        _exact(item["read_concern"], "majority", "transaction.read_concern"),
        _exact(item["write_concern"], "majority", "transaction.write_concern"),
        _true(item["journaled"], "transaction.journaled"),
        _true(item["manifest_inserted_last"], "transaction.manifest_inserted_last"),
        _true(item["all_or_nothing"], "transaction.all_or_nothing"),
        _true(
            item["zero_version_manifest_required"],
            "transaction.zero_version_manifest_required",
        ),
    )


def _clock(value: object) -> ClockPolicy:
    item = _object(
        value,
        {"policy", "completed_at_semantics", "workflow_completion_is_later_bound", "authenticated"},
        "clock",
    )
    return ClockPolicy(
        _exact(item["policy"], "utc_runner_bracket_v0", "clock.policy"),
        _exact(
            item["completed_at_semantics"],
            "after_canonical_staging_before_transaction",
            "clock.completed_at_semantics",
        ),
        _true(
            item["workflow_completion_is_later_bound"],
            "clock.workflow_completion_is_later_bound",
        ),
        _false(item["authenticated"], "clock.authenticated"),
    )


def _coverage(value: object) -> CoveragePolicy:
    item = _object(
        value,
        {
            "overlap_complete_utc_days",
            "include_current_partial_day",
            "max_pages_per_role",
            "max_candidates_per_run",
            "max_new_versions_per_run",
            "max_payload_bytes_per_candidate",
            "bound_exhaustion_action",
        },
        "coverage",
    )
    expected = (7, 100, 25000, 5000, 1048576)
    actual = (
        _integer(item["overlap_complete_utc_days"], "coverage.overlap_complete_utc_days"),
        _integer(item["max_pages_per_role"], "coverage.max_pages_per_role"),
        _integer(item["max_candidates_per_run"], "coverage.max_candidates_per_run"),
        _integer(item["max_new_versions_per_run"], "coverage.max_new_versions_per_run"),
        _integer(
            item["max_payload_bytes_per_candidate"],
            "coverage.max_payload_bytes_per_candidate",
        ),
    )
    if actual != expected:
        raise ProspectiveDeploymentError("coverage: registered bound mismatch")
    return CoveragePolicy(
        overlap_complete_utc_days=actual[0],
        include_current_partial_day=_true(
            item["include_current_partial_day"], "coverage.include_current_partial_day"
        ),
        max_pages_per_role=actual[1],
        max_candidates_per_run=actual[2],
        max_new_versions_per_run=actual[3],
        max_payload_bytes_per_candidate=actual[4],
        bound_exhaustion_action=_exact(
            item["bound_exhaustion_action"],
            "reject_entire_run_BOUND_EXHAUSTED",
            "coverage.bound_exhaustion_action",
        ),
    )


def _retention(value: object) -> RetentionPolicy:
    item = _object(
        value,
        {
            "retain_through_phase4_evaluation",
            "minimum_years_after_final_artifact",
            "licence_review_required_before_activation",
            "conflict_action",
        },
        "retention",
    )
    years = _integer(
        item["minimum_years_after_final_artifact"],
        "retention.minimum_years_after_final_artifact",
    )
    if years != 5:
        raise ProspectiveDeploymentError("retention: registered duration mismatch")
    return RetentionPolicy(
        _true(
            item["retain_through_phase4_evaluation"],
            "retention.retain_through_phase4_evaluation",
        ),
        years,
        _true(
            item["licence_review_required_before_activation"],
            "retention.licence_review_required_before_activation",
        ),
        _exact(item["conflict_action"], "block_activation", "retention.conflict_action"),
    )


def _runtime(value: object) -> RuntimePolicy:
    item = _object(
        value,
        {
            "implementation_mode",
            "credential_scope",
            "environment_inspection_permitted",
            "provider_access_permitted",
            "storage_access_permitted",
            "workflow_enabled",
        },
        "runtime",
    )
    return RuntimePolicy(
        _exact(item["implementation_mode"], "dormant_shadow", "runtime.implementation_mode"),
        _exact(
            item["credential_scope"],
            "dedicated_two_namespace_read_insert_only",
            "runtime.credential_scope",
        ),
        _false(
            item["environment_inspection_permitted"],
            "runtime.environment_inspection_permitted",
        ),
        _false(item["provider_access_permitted"], "runtime.provider_access_permitted"),
        _false(item["storage_access_permitted"], "runtime.storage_access_permitted"),
        _false(item["workflow_enabled"], "runtime.workflow_enabled"),
    )


def _permissions(value: object) -> PermissionPolicy:
    fields = {
        "implementation_permitted",
        "activation_permitted",
        "production_source_access_permitted",
        "production_storage_mutation_permitted",
        "source_authenticated",
        "clock_authenticated",
        "coverage_authenticated",
        "history_construction_permitted",
        "training_permitted",
        "outcome_access_permitted",
        "model_fitting_performed",
        "scientific_status",
    }
    item = _object(value, fields, "permissions")
    return PermissionPolicy(
        implementation_permitted=_true(
            item["implementation_permitted"], "permissions.implementation_permitted"
        ),
        activation_permitted=_false(
            item["activation_permitted"], "permissions.activation_permitted"
        ),
        production_source_access_permitted=_false(
            item["production_source_access_permitted"],
            "permissions.production_source_access_permitted",
        ),
        production_storage_mutation_permitted=_false(
            item["production_storage_mutation_permitted"],
            "permissions.production_storage_mutation_permitted",
        ),
        source_authenticated=_false(
            item["source_authenticated"], "permissions.source_authenticated"
        ),
        clock_authenticated=_false(
            item["clock_authenticated"], "permissions.clock_authenticated"
        ),
        coverage_authenticated=_false(
            item["coverage_authenticated"], "permissions.coverage_authenticated"
        ),
        history_construction_permitted=_false(
            item["history_construction_permitted"],
            "permissions.history_construction_permitted",
        ),
        training_permitted=_false(
            item["training_permitted"], "permissions.training_permitted"
        ),
        outcome_access_permitted=_false(
            item["outcome_access_permitted"],
            "permissions.outcome_access_permitted",
        ),
        model_fitting_performed=_false(
            item["model_fitting_performed"], "permissions.model_fitting_performed"
        ),
        scientific_status=_exact(
            item["scientific_status"],
            SCIENTIFIC_STATUS,
            "permissions.scientific_status",
        ),
    )


def normalize_deployment_manifest(value: object) -> DeploymentManifest:
    assert_no_secret_material(value)
    item = _object(
        value,
        {
            "schema_version",
            "graph",
            "registered_contract",
            "target_writer",
            "protocols",
            "storage",
            "transaction",
            "clock",
            "coverage",
            "retention",
            "runtime",
            "permissions",
        },
        "manifest",
    )
    _exact(item["schema_version"], MANIFEST_SCHEMA, "manifest.schema_version")
    _exact(item["graph"], GRAPH, "manifest.graph")
    return DeploymentManifest(
        _registered_contract(item["registered_contract"]),
        _target_writer(item["target_writer"]),
        _protocols(item["protocols"]),
        _storage(item["storage"]),
        _transaction(item["transaction"]),
        _clock(item["clock"]),
        _coverage(item["coverage"]),
        _retention(item["retention"]),
        _runtime(item["runtime"]),
        _permissions(item["permissions"]),
    )


def canonical_manifest_bytes(manifest: DeploymentManifest) -> bytes:
    return (
        json.dumps(
            manifest.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def assess_deployment_manifest(manifest: DeploymentManifest) -> DeploymentAssessment:
    digest = hashlib.sha256(canonical_manifest_bytes(manifest)).hexdigest()
    return DeploymentAssessment(
        digest,
        manifest.target_writer,
        manifest.storage,
        manifest.coverage,
        manifest.permissions,
    )


def run_deployment_review(value: object) -> DeploymentAssessment:
    return assess_deployment_manifest(normalize_deployment_manifest(value))


def serialize_deployment_review(review: DeploymentAssessment) -> str:
    return json.dumps(
        review.to_dict(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
