"""Synthetic-only tests for the information-matched decision rule; no old outcomes."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
import numpy as np
SRC=Path(__file__).resolve().parents[1]/"research"/"reviews"/"icomputing_2026"
sys.path.insert(0,str(SRC))
from ic_g5_3_matched_information import (calibrate_on_validation,chosen_indices,
    evaluate_old_outcome_only_after_authorized_reader,GateFailure)

class MatchedInformationTests(unittest.TestCase):
    def setUp(self):
        self.plan=calibrate_on_validation(name="p10_calibrated",
            point_validation=list(range(1,11)),
            risk_validation=list(range(-3,7)),
            frozen_cutoff=0,direction=1)

    def test_only_validation_scores_determine_scale(self):
        self.assertEqual(self.plan.coefficient,1.0)

    def test_same_score_same_candidate_universe_different_enforcement(self):
        p=[100,90,80,70,60,50,40,30,20,10]
        r=[-3,2,3,4,5,6,7,8,9,10]
        z=chosen_indices(p,r,self.plan)
        self.assertEqual((z["n"],z["k"]),(10,1))
        self.assertEqual(z["raw"].tolist(),[0])
        self.assertEqual(z["hard"].tolist(),[1])
        self.assertEqual(z["soft"].tolist(),[0])

    def test_no_target_ever_passed_to_selection(self):
        a=chosen_indices(list(range(10)),list(range(10)),self.plan)
        b=chosen_indices(list(range(10)),list(range(10)),self.plan)
        for arm in ("raw","hard","soft"):
            self.assertEqual(a[arm].tolist(),b[arm].tolist())

    def test_shared_policy_coverage_hard_capacity(self):
        z=chosen_indices(list(range(10)),list(range(10)),self.plan)
        self.assertEqual(z["admitted"],10)
        self.assertEqual(len(z["hard"]),1)

    def test_infeasible_hard_veto_rejected(self):
        with self.assertRaises(GateFailure):
            chosen_indices(list(range(10)),[-20]*10,self.plan)

    def test_bad_multiplier_disallowed(self):
        with self.assertRaises(GateFailure):
            calibrate_on_validation(name="p10_calibrated",point_validation=list(range(10)),
                risk_validation=list(range(10)),frozen_cutoff=0,direction=1,multiplier=2)

    def test_degenerate_train_scale_rejected(self):
        with self.assertRaises(GateFailure):
            calibrate_on_validation(name="p10_calibrated",point_validation=[1]*10,
                risk_validation=list(range(10)),frozen_cutoff=0,direction=1)

    def test_risk_direction_reversal_for_volatility(self):
        p=calibrate_on_validation(name="trailing_volatility",
            point_validation=list(range(10)),risk_validation=list(range(10)),
            frozen_cutoff=2,direction=-1)
        z=chosen_indices(list(range(10)),list(range(10)),p)
        self.assertEqual(z["hard"].tolist(),[2])

    def test_mislabelled_signal_direction_refused(self):
        with self.assertRaises(GateFailure):
            calibrate_on_validation(name="trailing_volatility",
                point_validation=list(range(10)),risk_validation=list(range(10)),
                frozen_cutoff=2,direction=1)

    def test_old_label_evaluator_preserves_float32_and_scope(self):
        z=chosen_indices(list(range(10)),list(range(10)),self.plan)
        r=evaluate_old_outcome_only_after_authorized_reader(z,np.arange(10,dtype=np.float32))
        self.assertIn("TRANSFORMED_TARGET",r["status"])
        self.assertIsNone(r["realized_tradable_pnl"])
        self.assertFalse(r["independent_unused_60d_holdout"])

    def test_integer_or_misaligned_target_refused(self):
        z=chosen_indices(list(range(10)),list(range(10)),self.plan)
        with self.assertRaises(GateFailure):
            evaluate_old_outcome_only_after_authorized_reader(z,np.arange(10,dtype=np.int64))
        with self.assertRaises(GateFailure):
            evaluate_old_outcome_only_after_authorized_reader(z,np.arange(9,dtype=np.float32))

    def test_small_sample_cannot_autofill_k(self):
        with self.assertRaises(GateFailure):
            chosen_indices([1,2],[1,2],self.plan,fraction=.1)

if __name__=="__main__":
    unittest.main()
