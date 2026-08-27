from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "research" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import run_phase3_mm1_v5_primary_bootstrap_exact_ties as exact


def test_exact_tie_runner_preserves_preregistered_constants():
    assert exact.REPLICATES == 10_000
    assert exact.SEED == 20260827
    assert exact.TOPK_FRACTION == 0.10
    assert exact.CONFIDENCE_LEVEL == 0.95


def test_residual_overlap_uses_champion_copy_capacity_exactly():
    result = exact._solve_boundary(
        capacities=np.array([2, 1, 1]),
        champion_capacities=np.array([1, 1, 0]),
        adjusted=np.array([1.0, 1.0, 1.0]),
        baseline=np.array([0.5, 0.4, 0.9]),
        remaining_k=2,
        adjusted_required=2.0,
        objective="overlap",
    )
    assert result is not None
    assert result["overlap"] == 2
    assert int(np.sum(result["quantity"])) == 2


def test_residual_nominal_is_conditional_on_frozen_overlap_level():
    result = exact._solve_boundary(
        capacities=np.array([1, 1, 1]),
        champion_capacities=np.array([1, 0, 0]),
        adjusted=np.array([1.0, 1.0, 1.0]),
        baseline=np.array([0.1, 0.8, 0.7]),
        remaining_k=2,
        adjusted_required=2.0,
        overlap_required=1,
        objective="nominal",
    )
    assert result is not None
    assert result["overlap"] == 1
    assert result["quantity"].tolist() == [1, 1, 0]
    assert result["nominal_total"] == 0.9


def test_lex_solution_prefers_lowest_baseline_rank_quantity():
    witness = exact.ThetaWitness(
        theta=0.0,
        boundary_rows=np.array([0, 1, 2], dtype=np.int64),
        capacities=np.array([1, 1, 1], dtype=np.int64),
        champion_capacities=np.array([0, 0, 0], dtype=np.int64),
        adjusted=np.array([1.0, 1.0, 1.0]),
        baseline=np.array([0.5, 0.5, 0.5]),
        ranks=np.array([2, 0, 1], dtype=np.int64),
        remaining_k=1,
        adjusted_required=1.0,
        fixed_quantity=np.array([0, 0, 0], dtype=np.int64),
        fixed_overlap=0,
        fixed_nominal_total=0.0,
        max_overlap=0,
    )
    quantity = exact._lex_solution(
        witness,
        overlap_star=0,
        nominal_star_total=0.5,
    )
    assert quantity is not None
    assert quantity.tolist() == [0, 1, 0]


def test_exact_tie_source_has_no_retuning_or_outcome_based_policy_change():
    source = (
        EXPERIMENTS / "run_phase3_mm1_v5_primary_bootstrap_exact_ties.py"
    ).read_text()
    assert "RHO_MM0" in source
    assert "ROBUST_VALUE_TOLERANCE" in source
    assert '"rho_retuned": False' in source
    assert '"threshold_retuned": False' in source
    assert '"V5_policy_changed": False' in source
    assert "target_model" in source
    assert "20260827" in source
