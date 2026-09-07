"""Validate the preregistered static collector-lineage evidence boundary."""

import json
from dataclasses import dataclass
from typing import Literal, cast

SCHEMA_VERSION = "dtrm.phase4.collector_lineage_evidence.v0"
AUDIT_ID = "phase4_collector_lineage_audit_v0"
CONTRACT_PATH = "research/contracts/DTRM_PHASE4_COLLECTOR_LINEAGE_AUDIT_V0.md"
CONTRACT_SHA256 = "2242d3d83af01d2854315856757e4c7be02278e125fe605a17ba543c4d0727d5"
PREREGISTRATION_COMMIT = "6d7b41424dc65d6234a98a916e494f42bc0ee62d"
PARENT_EVIDENCE_PATH = (
    "research/reports/DTRM_PHASE4_SOURCE_METADATA_LIVE_20260907T183459Z.json"
)
PARENT_EVIDENCE_SHA256 = "30aa53d5bfad2a32b1b4ed0c9aa8eb2024fd60bf54dc5314b6b6af5b847b880b"

FindingStatus = Literal[
    "SUPPORTED_STATICALLY", "CONTRADICTED_STATICALLY", "UNRESOLVED"
]


class LineageEvidenceError(ValueError):
    """The static evidence manifest violates its registered boundary."""


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    commit: str
    tree_sha: str
    tree_entry_count: int
    role: str
    files: tuple[tuple[str, str], ...]


SOURCE_POLICY = {
    "tech-com-UA00001/DTRM_Fund_Agent_API": SourcePolicy(
        commit="badb20158890e9982c7806382cc3e151782af372",
        tree_sha="b5107d0ee17f2909e0b0c060a7d00d00bb91a567",
        tree_entry_count=4384,
        role="workflow_dispatch_and_artifact_retrieval",
        files=(
            ("src/github.js", "7a07384ac9c7efa70cef9c1d9682f727c2e10ac0"),
            ("src/mcp/mcpServer.js", "8cc006d5a8ef12ff68b2f18b104f3e977bc043ca"),
            ("src/routes.trumpScore.js", "16e549cf43ebeb8c6f1fc1a8248eaf8b96bd4bfc"),
            ("src/server.js", "a1cdcd663486be2bf7dfb3a90bab13927892bd4d"),
        ),
    ),
    "tech-com-UA00001/theresistance-back": SourcePolicy(
        commit="7a8107e4451891535366acaf766348785ccc157b",
        tree_sha="f295888372d9ef3c089cc24dd1e72e6b1f2c92cf",
        tree_entry_count=235,
        role="news_collection_and_ranking_evidence",
        files=(
            (
                ".github/workflows/daily_model_inference.yml",
                "2bed9fad2e42ed2e04ee5603aafbbd2d7a569924",
            ),
            (
                ".github/workflows/morning.yml",
                "4666c64c216f82a01e1000adce50e9101180bb7b",
            ),
            (
                ".github/workflows/trump_score.yml",
                "09b1267793ad20fd01474f60d3ae1b19b4150dfc",
            ),
            (
                "agent/trump_model/export_daily_news_candidates.py",
                "331f261bfd4be636d3cd675ed287de6acd2dab8a",
            ),
            (
                "agent/trump_model/freeze_daily_news_evidence.py",
                "18fd2ad6af63de54ba46b3d03444d12f1adb247f",
            ),
            (
                "agent/trump_model/freeze_loaded_news_evidence.py",
                "f5d2ca87937672e9b096cc6f3fc29d5390bdc09d",
            ),
            (
                "agent/trump_model/news_collector.py",
                "700e831db5c1d196a8e7c2c1dc6d10148237e710",
            ),
            (
                "agent/trump_model/run_pipeline.py",
                "b39643a418a531060dd4e09a39424350f527d1fe",
            ),
            (
                "agent/trump_model/run_score_with_frozen_news.py",
                "792a8dbb4848ebe578c4658cd9c2f5c38f984586",
            ),
            (
                "docs/architecture/daily_intelligence_append_only_recovery_v1.md",
                "11c769408054e62e2f819d6b59af87158827a04d",
            ),
            (
                "src/theresistance_backend/intelligence/canonical_evidence.py",
                "459e708055818a6fccea42e380ea6ef67cb4ecad",
            ),
            (
                "tests/foundation/test_canonical_evidence.py",
                "896b9a578284764f22d4a665e1c4251041638c45",
            ),
        ),
    ),
}

EXPECTED_FINDINGS: dict[str, FindingStatus] = {
    "F01_COLLECTOR_WRITE_SHAPE": "SUPPORTED_STATICALLY",
    "F02_OBSERVATION_CLOCK": "CONTRADICTED_STATICALLY",
    "F03_VERSION_LINEAGE": "CONTRADICTED_STATICALLY",
    "F04_LINK_PROVENANCE": "CONTRADICTED_STATICALLY",
    "F05_INCREMENTAL_COVERAGE": "CONTRADICTED_STATICALLY",
    "F06_SCHEDULED_ENTRYPOINTS": "SUPPORTED_STATICALLY",
    "F07_RANKING_TIME_FREEZE": "SUPPORTED_STATICALLY",
    "F08_HISTORICAL_ARCHIVE": "UNRESOLVED",
    "F09_API_BOUNDARY": "SUPPORTED_STATICALLY",
    "F10_RUNTIME_DEPLOYMENT": "UNRESOLVED",
    "F11_FREEZE_TESTS": "SUPPORTED_STATICALLY",
    "F12_COLLECTOR_PROVENANCE_TESTS": "UNRESOLVED",
}

FORBIDDEN_FRAGMENTS = (
    "mongodb+srv://",
    "?apikey=",
    "authorization: bearer",
    "-----begin private key-----",
)


@dataclass(frozen=True, slots=True)
class CitedFile:
    path: str
    blob_sha: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "blob_sha": self.blob_sha}


@dataclass(frozen=True, slots=True)
class InspectedSource:
    repository: str
    commit: str
    tree_sha: str
    recursive_tree_complete: bool
    tree_entry_count: int
    role: str
    files: tuple[CitedFile, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "commit": self.commit,
            "tree_sha": self.tree_sha,
            "recursive_tree_complete": self.recursive_tree_complete,
            "tree_entry_count": self.tree_entry_count,
            "role": self.role,
            "files": [item.to_dict() for item in self.files],
        }


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    repository: str
    path: str
    blob_sha: str
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "path": self.path,
            "blob_sha": self.blob_sha,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@dataclass(frozen=True, slots=True)
class LineageFinding:
    finding_id: str
    status: FindingStatus
    property: str
    statement: str
    evidence: tuple[EvidenceReference, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "status": self.status,
            "property": self.property,
            "statement": self.statement,
            "evidence": [item.to_dict() for item in self.evidence],
        }


@dataclass(frozen=True, slots=True)
class CollectorLineageAudit:
    sources: tuple[InspectedSource, ...]
    findings: tuple[LineageFinding, ...]
    conclusion: str
    next_permitted_operation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "audit_id": AUDIT_ID,
            "registered_contract": {
                "path": CONTRACT_PATH,
                "sha256": CONTRACT_SHA256,
                "preregistration_commit": PREREGISTRATION_COMMIT,
            },
            "parent_evidence": {
                "path": PARENT_EVIDENCE_PATH,
                "sha256": PARENT_EVIDENCE_SHA256,
            },
            "inspection": {
                "mode": "pinned_static_repository",
                "live_system_accessed": False,
                "outcome_files_accessed": False,
                "sources": [source.to_dict() for source in self.sources],
            },
            "findings": [finding.to_dict() for finding in self.findings],
            "decision": {
                "scientific_status": "BLOCKED_SOURCE_AUDIT",
                "training_permitted": False,
                "outcome_access_permitted": False,
                "history_construction_permitted": False,
                "model_fitting_performed": False,
                "true_observed_vintage_history_authenticated": False,
                "conclusion": self.conclusion,
                "next_permitted_operation": self.next_permitted_operation,
            },
        }


def _object(value: object, expected: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != expected:
        raise LineageEvidenceError(f"{label}: unexpected keys")
    return cast(dict[str, object], value)


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise LineageEvidenceError(f"{label}: expected list")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise LineageEvidenceError(f"{label}: expected nonempty trimmed string")
    return value


def _sha(value: object, label: str) -> str:
    text = _text(value, label)
    if len(text) not in (40, 64) or any(char not in "0123456789abcdef" for char in text):
        raise LineageEvidenceError(f"{label}: expected lowercase Git or SHA-256 digest")
    return text


def _positive_int(value: object, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise LineageEvidenceError(f"{label}: expected positive integer")
    return value


def _walk_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, dict):
        item = cast(dict[object, object], value)
        return tuple(
            text
            for key, nested in item.items()
            for text in (*_walk_strings(key), *_walk_strings(nested))
        )
    if isinstance(value, list):
        return tuple(text for item in value for text in _walk_strings(item))
    return ()


def assert_no_sensitive_material(value: object) -> None:
    """Reject connection strings and credential-shaped material at the evidence boundary."""

    for text in _walk_strings(value):
        lowered = text.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_FRAGMENTS):
            raise LineageEvidenceError("manifest contains forbidden credential material")


def _parse_sources(value: object) -> tuple[InspectedSource, ...]:
    sources: list[InspectedSource] = []
    for raw_source in _list(value, "inspection.sources"):
        item = _object(
            raw_source,
            {
                "repository",
                "commit",
                "tree_sha",
                "recursive_tree_complete",
                "tree_entry_count",
                "role",
                "files",
            },
            "source",
        )
        repository = _text(item["repository"], "source.repository")
        policy = SOURCE_POLICY.get(repository)
        if policy is None:
            raise LineageEvidenceError("source.repository: outside registered scope")
        if _sha(item["commit"], "source.commit") != policy.commit:
            raise LineageEvidenceError("source.commit: does not match registered binding")
        if _sha(item["tree_sha"], "source.tree_sha") != policy.tree_sha:
            raise LineageEvidenceError("source.tree_sha: does not match registered binding")
        if item["recursive_tree_complete"] is not True:
            raise LineageEvidenceError("source recursive tree was not complete")
        if _positive_int(item["tree_entry_count"], "source.tree_entry_count") != (
            policy.tree_entry_count
        ):
            raise LineageEvidenceError("source.tree_entry_count: unexpected value")
        if _text(item["role"], "source.role") != policy.role:
            raise LineageEvidenceError("source.role: unexpected value")
        allowed_files = dict(policy.files)
        files: list[CitedFile] = []
        for raw_file in _list(item["files"], "source.files"):
            file_item = _object(raw_file, {"path", "blob_sha"}, "source.file")
            path = _text(file_item["path"], "source.file.path")
            blob_sha = _sha(file_item["blob_sha"], "source.file.blob_sha")
            if allowed_files.get(path) != blob_sha:
                raise LineageEvidenceError("source.file: path/blob is outside registered evidence")
            files.append(CitedFile(path, blob_sha))
        if len({file.path for file in files}) != len(files):
            raise LineageEvidenceError("source.files: duplicate path")
        if {file.path for file in files} != set(allowed_files):
            raise LineageEvidenceError("source.files: incomplete selected evidence set")
        sources.append(
            InspectedSource(
                repository,
                policy.commit,
                policy.tree_sha,
                True,
                policy.tree_entry_count,
                policy.role,
                tuple(sorted(files, key=lambda file: file.path)),
            )
        )
    if len({source.repository for source in sources}) != len(sources):
        raise LineageEvidenceError("inspection.sources: duplicate repository")
    if {source.repository for source in sources} != set(SOURCE_POLICY):
        raise LineageEvidenceError("inspection.sources: incomplete registered source set")
    return tuple(sorted(sources, key=lambda source: source.repository))


def _parse_findings(
    value: object, sources: tuple[InspectedSource, ...]
) -> tuple[LineageFinding, ...]:
    selected = {
        (source.repository, file.path): file.blob_sha
        for source in sources
        for file in source.files
    }
    findings: list[LineageFinding] = []
    for raw_finding in _list(value, "findings"):
        item = _object(
            raw_finding,
            {"finding_id", "status", "property", "statement", "evidence"},
            "finding",
        )
        finding_id = _text(item["finding_id"], "finding.finding_id")
        expected_status = EXPECTED_FINDINGS.get(finding_id)
        if expected_status is None or item["status"] != expected_status:
            raise LineageEvidenceError("finding id/status is outside registered decision set")
        references: list[EvidenceReference] = []
        for raw_reference in _list(item["evidence"], "finding.evidence"):
            reference = _object(
                raw_reference,
                {"repository", "path", "blob_sha", "line_start", "line_end"},
                "evidence reference",
            )
            repository = _text(reference["repository"], "evidence.repository")
            path = _text(reference["path"], "evidence.path")
            blob_sha = _sha(reference["blob_sha"], "evidence.blob_sha")
            if selected.get((repository, path)) != blob_sha:
                raise LineageEvidenceError("evidence reference is not bound to a selected blob")
            line_start = _positive_int(reference["line_start"], "evidence.line_start")
            line_end = _positive_int(reference["line_end"], "evidence.line_end")
            if line_end < line_start or line_end > 100_000:
                raise LineageEvidenceError("evidence reference has invalid line range")
            references.append(
                EvidenceReference(repository, path, blob_sha, line_start, line_end)
            )
        if not references:
            raise LineageEvidenceError("finding.evidence: expected at least one reference")
        findings.append(
            LineageFinding(
                finding_id,
                expected_status,
                _text(item["property"], "finding.property"),
                _text(item["statement"], "finding.statement"),
                tuple(
                    sorted(
                        references,
                        key=lambda ref: (ref.repository, ref.path, ref.line_start, ref.line_end),
                    )
                ),
            )
        )
    if len({finding.finding_id for finding in findings}) != len(findings):
        raise LineageEvidenceError("findings: duplicate finding_id")
    if {finding.finding_id for finding in findings} != set(EXPECTED_FINDINGS):
        raise LineageEvidenceError("findings: incomplete registered decision set")
    return tuple(sorted(findings, key=lambda finding: finding.finding_id))


def parse_collector_lineage_evidence(value: object) -> CollectorLineageAudit:
    """Parse, bind, and freeze one collector-lineage manifest."""

    assert_no_sensitive_material(value)
    item = _object(
        value,
        {
            "schema_version",
            "audit_id",
            "registered_contract",
            "parent_evidence",
            "inspection",
            "findings",
            "decision",
        },
        "manifest",
    )
    if item["schema_version"] != SCHEMA_VERSION or item["audit_id"] != AUDIT_ID:
        raise LineageEvidenceError("manifest identity mismatch")
    contract = _object(
        item["registered_contract"],
        {"path", "sha256", "preregistration_commit"},
        "registered_contract",
    )
    if contract != {
        "path": CONTRACT_PATH,
        "sha256": CONTRACT_SHA256,
        "preregistration_commit": PREREGISTRATION_COMMIT,
    }:
        raise LineageEvidenceError("registered contract binding mismatch")
    parent = _object(item["parent_evidence"], {"path", "sha256"}, "parent_evidence")
    if parent != {"path": PARENT_EVIDENCE_PATH, "sha256": PARENT_EVIDENCE_SHA256}:
        raise LineageEvidenceError("parent evidence binding mismatch")
    inspection = _object(
        item["inspection"],
        {"mode", "live_system_accessed", "outcome_files_accessed", "sources"},
        "inspection",
    )
    if inspection["mode"] != "pinned_static_repository":
        raise LineageEvidenceError("inspection mode mismatch")
    if inspection["live_system_accessed"] is not False:
        raise LineageEvidenceError("live-system access is forbidden")
    if inspection["outcome_files_accessed"] is not False:
        raise LineageEvidenceError("outcome-file access is forbidden")
    sources = _parse_sources(inspection["sources"])
    findings = _parse_findings(item["findings"], sources)
    decision = _object(
        item["decision"],
        {
            "scientific_status",
            "training_permitted",
            "outcome_access_permitted",
            "history_construction_permitted",
            "model_fitting_performed",
            "true_observed_vintage_history_authenticated",
            "conclusion",
            "next_permitted_operation",
        },
        "decision",
    )
    required_decision = {
        "scientific_status": "BLOCKED_SOURCE_AUDIT",
        "training_permitted": False,
        "outcome_access_permitted": False,
        "history_construction_permitted": False,
        "model_fitting_performed": False,
        "true_observed_vintage_history_authenticated": False,
    }
    if any(decision[key] != expected for key, expected in required_decision.items()):
        raise LineageEvidenceError("decision attempts scientific promotion")
    return CollectorLineageAudit(
        sources,
        findings,
        _text(decision["conclusion"], "decision.conclusion"),
        _text(decision["next_permitted_operation"], "decision.next_permitted_operation"),
    )


def canonical_manifest_bytes(audit: CollectorLineageAudit) -> bytes:
    """Return the sole accepted deterministic serialization."""

    return (
        json.dumps(audit.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def validate_report_binding(audit: CollectorLineageAudit, report: str) -> None:
    """Require every immutable source and finding identity to appear in the report."""

    assert_no_sensitive_material(report)
    required = {
        AUDIT_ID,
        "BLOCKED_SOURCE_AUDIT",
        *(finding.finding_id for finding in audit.findings),
        *(source.repository for source in audit.sources),
        *(source.commit for source in audit.sources),
        *(source.tree_sha for source in audit.sources),
        *(file.path for source in audit.sources for file in source.files),
        *(file.blob_sha for source in audit.sources for file in source.files),
    }
    missing = sorted(token for token in required if token not in report)
    if missing:
        raise LineageEvidenceError(f"report is missing {len(missing)} bound identities")
