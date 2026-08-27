from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import run_phase3_mm1_v6_decision_freeze as v6


def _rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": [
                "2026-06-26T00:00:00Z",
                "2026-07-01T12:30:00Z",
                "2026-07-06T23:59:59Z",
            ],
        }
    )


def _features(rows: int = 3) -> np.ndarray:
    return np.zeros((rows, v6.EXPECTED_FEATURE_COUNT), dtype=np.float32)


def _provenance(rows_sha: str = "rows", features_sha: str = "features") -> dict:
    return {
        "artifacts": {
            "candidate_rows": {
                "path": str(v6.V6_ROWS_PATH.relative_to(v6.REPO_ROOT)),
                "sha256": rows_sha,
            },
            "feature_matrix": {
                "path": str(v6.V6_FEATURES_PATH.relative_to(v6.REPO_ROOT)),
                "shape": [v6.EXPECTED_ROWS, v6.EXPECTED_FEATURE_COUNT],
                "sha256": features_sha,
            },
        }
    }


def test_v6_frozen_constants_match_preregistered_replication():
    assert v6.V6_START == pd.Timestamp("2026-06-26T00:00:00Z")
    assert v6.V6_END == pd.Timestamp("2026-07-06T23:59:59Z")
    assert v6.EXPECTED_FEATURE_COUNT == 390
    assert v6.EXPECTED_ROWS == 11922
    assert v6.EXPECTED_RHO == 0.4378501384944031


def test_validate_v6_inputs_accepts_exact_exante_schema():
    rows, features = v6.validate_v6_inputs(_rows(), _features())
    assert list(rows.columns) == list(v6.REQUIRED_ROW_COLUMNS)
    assert features.shape == (3, 390)
    assert features.dtype == np.float32
    assert str(rows["date_dt"].dt.tz) == "UTC"


def test_validate_v6_inputs_rejects_extra_columns():
    rows = _rows()
    rows["target_model"] = 1.0
    with pytest.raises(ValueError, match="unexpected columns"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_duplicate_pair_keys():
    rows = _rows()
    rows.loc[1, ["news_id", "ticker"]] = rows.loc[0, ["news_id", "ticker"]]
    with pytest.raises(ValueError, match="duplicate"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_rows_outside_preregistered_window():
    rows = _rows()
    rows.loc[0, "date_dt"] = "2026-06-25T23:59:59Z"
    with pytest.raises(ValueError, match="outside"):
        v6.validate_v6_inputs(rows, _features())


def test_validate_v6_inputs_rejects_wrong_feature_width():
    with pytest.raises(ValueError, match="exactly 390"):
        v6.validate_v6_inputs(_rows(), np.zeros((3, 389), dtype=np.float32))


def test_validate_v6_inputs_rejects_nonfinite_features():
    features = _features()
    features[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        v6.validate_v6_inputs(_rows(), features)


def test_require_frozen_input_hashes_accepts_exact_provenance():
    v6.require_frozen_input_hashes(
        _provenance(), rows_sha256="rows", features_sha256="features"
    )


def test_require_frozen_input_hashes_rejects_candidate_row_mutation():
    with pytest.raises(RuntimeError, match="candidate-row SHA-256"):
        v6.require_frozen_input_hashes(
            _provenance(), rows_sha256="mutated", features_sha256="features"
        )


def test_require_frozen_input_hashes_rejects_feature_mutation():
    with pytest.raises(RuntimeError, match="feature-matrix SHA-256"):
        v6.require_frozen_input_hashes(
            _provenance(), rows_sha256="rows", features_sha256="mutated"
        )


def test_frozen_v5_policy_blob_map_contains_full_decision_chain():
    assert v6.FROZEN_V5_POLICY_BLOBS == {
        "src/dtrm/phase3_mm0_state.py": "43e1d654c970b2f6bbbc8d3c600105d918e5fd57",
        "src/dtrm/phase3_mm1_robust_value.py": "c8d05e002d0c1f5e646a593e13cfa570d4f17841",
        "src/dtrm/phase3_mm1_optimizer.py": "7d9f80db4d584d9106daa81015c9de1f781b5421",
        "research/experiments/run_phase3_mm0_rho_calibration.py": "5a9fc0c609b4cffd034a412d7101af8c7a450aea",
        "research/experiments/run_phase3_mm1_v5_decision_freeze.py": "8978a4ee78196a275d3f8299a63f4cc2bd652dde",
    }


def test_require_frozen_v5_policy_code_rejects_source_change(monkeypatch):
    monkeypatch.setattr(v6, "git_blob_sha", lambda _path: "changed")
    with pytest.raises(RuntimeError, match="Frozen V5 policy source changed"):
        v6.require_frozen_v5_policy_code()


def test_build_manifest_preserves_replication_firewall_and_policy_identity():
    signals = pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": pd.to_datetime(
                ["2026-06-26", "2026-06-27", "2026-06-28"], utc=True
            ),
            "baseline_point_score": [0.3, 0.2, 0.1],
            "baseline_rank": [0, 1, 2],
            "raw_p10": [-0.01, -0.02, -0.03],
            "calibrated_p10": [-0.07, -0.08, -0.09],
            "phase2_guardrail_pass": [True, True, True],
        }
    )
    optimization = SimpleNamespace(
        champion_indices=np.array([0, 1]),
        selected_indices=np.array([0, 2]),
        k=2,
        eligible_rows=3,
        robust_value_selected=0.12,
        robust_value_champion=0.10,
        robust_lift=0.02,
        nominal_mean_selected=0.20,
        nominal_mean_champion=0.25,
        overlap_with_champion=1,
        intervention=True,
        solver_status="optimal_exact_threshold_unique_primary_band",
        solver_mip_gap=0.0,
        scipy_version="test",
        numpy_version="test",
    )
    manifest = v6.build_manifest(
        signals=signals,
        optimization=optimization,
        rows_sha256="rows",
        features_sha256="features",
        signals_sha256="signals",
        provenance_sha256="provenance",
        source_head="abc123",
        source_branch="research/phase3-minmax-contract",
        offset_reproduced=v6.P10_CALIBRATION_OFFSET,
        threshold_reproduced=v6.P10_GUARDRAIL_THRESHOLD,
        baseline_best_iteration=6,
        p10_best_iteration=18,
        policy_blobs=v6.FROZEN_V5_POLICY_BLOBS,
    )
    assert manifest["cohort"]["id"] == "V6"
    assert manifest["cohort"]["role"] == "prospective_temporal_replication"
    assert manifest["source_code"]["policy_code_byte_identical_to_V5_freeze"] is True
    assert manifest["frozen_policy"]["rho"] == v6.EXPECTED_RHO
    assert manifest["frozen_policy"]["V5_results_used_to_change_policy"] is False
    assert manifest["information_firewall"]["V6_realized_outcomes_accessed"] is False
    assert manifest["information_firewall"]["V5_results_used_to_change_V6_policy"] is False
    assert manifest["information_firewall"]["realized_evaluation_before_2026_09_04"] == "forbidden"


def test_runner_source_contains_no_v6_realized_artifact_paths():
    source = (EXPERIMENTS / "run_phase3_mm1_v6_decision_freeze.py").read_text()
    forbidden = (
        "phase3_mm1_v6_target_model.pkl",
        "phase3_mm1_v6_price_snapshot.pkl",
        "run_phase3_mm1_v6_realized_evaluation",
    )
    for token in forbidden:
        assert token not in source
