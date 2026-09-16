from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "research/reports/DTRM_PHASE4_PROSPECTIVE_ACTIVATION_REBIND_VALIDATION_V1.json"
)


def test_activation_rebind_validation_record_is_frozen() -> None:
    report_bytes = REPORT.read_bytes()
    report = json.loads(report_bytes)

    assert hashlib.sha256(report_bytes).hexdigest() == (
        "6f1bd31e622f6e0213227e395784b619e7df957bee3c41639745aef0fe0004d3"
    )
    assert report["status"] == "PASS_EXACT_HEAD_VALIDATION"
    assert report["validated_implementation_head"] == (
        "7066af5f79a6e87147ec1ce16f25a75ff7164ffc"
    )
    assert report["workflow_runs"] == {
        "phase4_evidence_adequacy_v1_gates": {
            "conclusion": "success",
            "run_id": 35073445569,
        },
        "phase4_gates": {
            "conclusion": "success",
            "run_id": 35073445579,
        },
        "phase4_temporal_evidence_v1_gates": {
            "conclusion": "success",
            "run_id": 35073445692,
        },
        "tests": {
            "conclusion": "success",
            "run_id": 35073445680,
        },
    }
    assert report["operational_boundary"] == {
        "arm_variable_set_to_true": False,
        "campaign_started": False,
        "mm1_execution_permitted": False,
        "outcome_access_permitted": False,
        "provider_call_performed_by_rebind": False,
        "statement_provisioned": False,
    }
