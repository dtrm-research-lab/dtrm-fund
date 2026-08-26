from __future__ import annotations

import hashlib
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

import run_phase3_mm1_v5_decision_freeze as v5


def _rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": [
                "2026-06-15T10:00:00Z",
                "2026-06-20T12:30:00Z",
                "2026-06-25T23:00:00Z",
            ],
        }
    )


def _features(rows: int = 3) -> np.ndarray:
    return np.zeros((rows, v5.EXPECTED_FEATURE_COUNT), dtype=np.float32)


def _provenance(rows_sha: str = "rows", features_sha: str = "features") -> dict:
    return {
        "artifacts": {
            "candidate_rows": {
                "path": str(v5.V5_ROWS_PATH.relative_to(v5.REPO_ROOT)),
                "sha256": rows_sha,
            },
            "feature_matrix": {
                "path": str(v5.V5_FEATURES_PATH.relative_to(v5.REPO_ROOT)),
                "shape": [10745, v5.EXPECTED_FEATURE_COUNT],
                "sha256": features_sha,
            },
        }
    }


def test_validate_v5_inputs_accepts_exact_exante_schema():
    rows, features = v5.validate_v5_inputs(_rows(), _features())

    assert list(rows.columns) == list(v5.REQUIRED_ROW_COLUMNS)
    assert len(rows) == 3
    assert features.shape == (3, 390)
    assert features.dtype == np.float32
    assert isinstance(rows["date_dt"].dtype, pd.DatetimeTZDtype)
    assert str(rows["date_dt"].dt.tz) == "UTC"


def test_validate_v5_inputs_rejects_extra_columns():
    rows = _rows()
    rows["unexpected"] = 1.0

    with pytest.raises(ValueError, match="unexpected columns"):
        v5.validate_v5_inputs(rows, _features())


def test_validate_v5_inputs_rejects_duplicate_pair_keys():
    rows = _rows()
    rows.loc[1, "news_id"] = rows.loc[0, "news_id"]
    rows.loc[1, "ticker"] = rows.loc[0, "ticker"]

    with pytest.raises(ValueError, match="duplicate"):
        v5.validate_v5_inputs(rows, _features())


def test_validate_v5_inputs_rejects_rows_outside_preregistered_window():
    rows = _rows()
    rows.loc[0, "date_dt"] = "2026-06-14T23:59:59Z"

    with pytest.raises(ValueError, match="outside"):
        v5.validate_v5_inputs(rows, _features())


def test_validate_v5_inputs_rejects_wrong_feature_width():
    with pytest.raises(ValueError, match="exactly 390"):
        v5.validate_v5_inputs(_rows(), np.zeros((3, 389), dtype=np.float32))


def test_validate_v5_inputs_rejects_feature_row_mismatch():
    with pytest.raises(ValueError, match="row count"):
        v5.validate_v5_inputs(_rows(), _features(rows=2))


def test_validate_v5_inputs_rejects_nonfinite_features():
    features = _features()
    features[0, 0] = np.nan

    with pytest.raises(ValueError, match="finite"):
        v5.validate_v5_inputs(_rows(), features)


def test_sha256_file_matches_known_digest(tmp_path):
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"abc")

    assert v5.sha256_file(path) == hashlib.sha256(b"abc").hexdigest()


def test_require_frozen_input_hashes_accepts_exact_provenance():
    v5.require_frozen_input_hashes(
        _provenance(),
        rows_sha256="rows",
        features_sha256="features",
    )


def test_require_frozen_input_hashes_rejects_candidate_row_mutation():
    with pytest.raises(RuntimeError, match="candidate-row SHA-256"):
        v5.require_frozen_input_hashes(
            _provenance(),
            rows_sha256="mutated",
            features_sha256="features",
        )


def test_require_frozen_input_hashes_rejects_feature_mutation():
    with pytest.raises(RuntimeError, match="feature-matrix SHA-256"):
        v5.require_frozen_input_hashes(
            _provenance(),
            rows_sha256="rows",
            features_sha256="mutated",
        )


def test_selection_identities_are_sorted_by_frozen_baseline_rank():
    signals = pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": pd.to_datetime(
                ["2026-06-15", "2026-06-16", "2026-06-17"],
                utc=True,
            ),
            "baseline_rank": [2, 0, 1],
        }
    )

    identities = v5.selection_identities(signals, np.array([0, 2, 1]))

    assert [item["baseline_rank"] for item in identities] == [0, 1, 2]
    assert [item["ticker"] for item in identities] == ["BBB", "CCC", "AAA"]


def test_build_manifest_marks_information_firewall_and_full_identities():
    signals = pd.DataFrame(
        {
            "news_id": ["n1", "n2", "n3"],
            "ticker": ["AAA", "BBB", "CCC"],
            "date_dt": pd.to_datetime(
                ["2026-06-15", "2026-06-16", "2026-06-17"],
                utc=True,
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
        solver_status="optimal",
        solver_mip_gap=0.0,
        scipy_version="test",
        numpy_version="test",
    )

    manifest = v5.build_manifest(
        signals=signals,
        optimization=optimization,
        rows_sha256="rows",
        features_sha256="features",
        signals_sha256="signals",
        provenance_sha256="provenance",
        source_head="abc123",
        source_branch="research/phase3-minmax-contract",
        offset_reproduced=v5.P10_CALIBRATION_OFFSET,
        threshold_reproduced=v5.P10_GUARDRAIL_THRESHOLD,
        baseline_best_iteration=6,
        p10_best_iteration=18,
    )

    assert manifest["status"] == "decision_frozen_pending_git_commit"
    assert manifest["frozen_exante_provenance"]["sha256"] == "provenance"
    assert manifest["frozen_exante_provenance"]["input_hashes_enforced_before_scoring"] is True
    assert manifest["information_firewall"]["V5_realized_outcomes_accessed"] is False
    assert manifest["information_firewall"]["manifest_commit_required_before_realized_evaluation"] is True
    assert len(manifest["decision"]["phase2_champion_row_identities"]) == 2
    assert len(manifest["decision"]["MM1_selected_row_identities"]) == 2
    assert manifest["decision"]["intervention"] is True


def test_runner_source_contains_no_v5_realized_artifact_path():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_decision_freeze.py"
    ).read_text()

    forbidden = (
        "phase3_mm1_v5_target",
        "phase3_mm1_v5_model_target",
        "phase3_mm1_v5_prices",
        "target_model.pkl",
    )

    for token in forbidden:
        assert token not in source
