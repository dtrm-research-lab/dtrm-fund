from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from dtrm.phase4.prospective_evidence_adequacy import (
    ACTIVATION_SCHEMA,
    PROVIDER_ROLES,
    REQUEST_FINGERPRINT,
    REVIEW_AMENDMENT_V4,
    ActivationBinding,
    audit_evidence,
)


def test_canonical_audit_serializes_review_amendment_v4_lineage() -> None:
    statement = json.dumps(
        {
            "schema_version": ACTIVATION_SCHEMA,
            "activation_statement": "synthetic-activation-v4-lineage",
            "backend_commit": "a" * 40,
            "backend_tree": "b" * 40,
            "workflow_path": ".github/workflows/phase4-prospective-temporal-evidence-v1.yml",
            "workflow_blob_sha": "e" * 40,
            "workflow_identity": "phase4-prospective-temporal-evidence-v1",
            "provider_roles": list(PROVIDER_ROLES),
            "request_fingerprint_sha256": REQUEST_FINGERPRINT,
            "provisioned_schema_identity": "synthetic-prospective-schema-v1",
            "credential_scope_status": "AUTHORIZED",
            "credential_scope_evidence_sha256": "f" * 64,
            "writer_authority_status": "AUTHORIZED",
            "writer_authority_evidence_sha256": "1" * 64,
            "prospective_start_utc": "2026-09-15T00:00:00Z",
            "periodic_capture_activation_permitted": True,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    binding = ActivationBinding(
        statement_bytes=statement,
        trusted_activation_statement="synthetic-activation-v4-lineage",
        trusted_activation_statement_sha256=hashlib.sha256(statement).hexdigest(),
    )

    report = audit_evidence(
        binding,
        (),
        datetime(2026, 9, 15, 0, 0, tzinfo=UTC),
    )

    assert report["review_amendment_v4_commit"] == REVIEW_AMENDMENT_V4
