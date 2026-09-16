from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from dtrm.phase4.prospective_activation_rebind import (
    PREVIOUS_STATEMENT_SHA256,
    REBIND_STATEMENT_ID,
    REBIND_WORKFLOW_BLOB_SHA,
    ProspectiveActivationRebindError,
    verify_rebind,
)

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT / "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2.json"
REBOUND = (
    ROOT
    / "research/contracts/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_STATEMENT_V2_REBOUND.json"
)
EVIDENCE = ROOT / "research/evidence/phase4_prospective_activation_rebind_v1.json"


def _bytes(path: Path) -> bytes:
    return path.read_bytes()


def test_rebound_statement_and_evidence_verify_exactly() -> None:
    statement_sha, evidence_sha = verify_rebind(
        previous_statement_bytes=_bytes(PREVIOUS),
        rebound_statement_bytes=_bytes(REBOUND),
        evidence_bytes=_bytes(EVIDENCE),
    )
    assert statement_sha == "5625b8930f5c6aefd9aa6193c5211c74ec61d96a4d88ea72307c42bbe654dbd5"
    assert evidence_sha == "9b090069961f262f21da66ba2a646837f7f4af9fbc6f31dd1d7b74abdadb9d73"


def test_previous_statement_is_preserved_and_only_executor_binding_changes() -> None:
    previous_bytes = _bytes(PREVIOUS)
    previous = json.loads(previous_bytes)
    rebound = json.loads(_bytes(REBOUND))

    assert hashlib.sha256(previous_bytes).hexdigest() == PREVIOUS_STATEMENT_SHA256

    changed = {key for key in previous if previous[key] != rebound[key]}
    assert changed == {"activation_statement", "workflow_blob_sha"}
    assert rebound["activation_statement"] == REBIND_STATEMENT_ID
    assert rebound["workflow_blob_sha"] == REBIND_WORKFLOW_BLOB_SHA


def test_rebind_keeps_campaign_inert() -> None:
    evidence = json.loads(_bytes(EVIDENCE))
    operational = evidence["operational_state"]
    assert operational == {
        "arm_variable_set_to_true": False,
        "campaign_started": False,
        "human_activation_authorized_for_rebound": False,
        "previous_statement_provisioned": False,
        "rebound_statement_prepared": True,
        "rebound_statement_provisioned": False,
    }
    assert all(value is False for value in evidence["downstream_permissions"].values())


def test_workflow_blob_tampering_fails_closed() -> None:
    rebound = json.loads(_bytes(REBOUND))
    rebound["workflow_blob_sha"] = "0" * 40
    tampered = (json.dumps(rebound, indent=2, sort_keys=True) + "\n").encode()

    with pytest.raises(
        ProspectiveActivationRebindError,
        match="rebound activation statement mismatch",
    ):
        verify_rebind(
            previous_statement_bytes=_bytes(PREVIOUS),
            rebound_statement_bytes=tampered,
            evidence_bytes=_bytes(EVIDENCE),
        )


def test_campaign_window_tampering_fails_closed() -> None:
    rebound = json.loads(_bytes(REBOUND))
    rebound["prospective_start_utc"] = "2026-09-19T00:00:00Z"
    tampered = (json.dumps(rebound, indent=2, sort_keys=True) + "\n").encode()

    with pytest.raises(
        ProspectiveActivationRebindError,
        match="rebound activation statement mismatch",
    ):
        verify_rebind(
            previous_statement_bytes=_bytes(PREVIOUS),
            rebound_statement_bytes=tampered,
            evidence_bytes=_bytes(EVIDENCE),
        )
