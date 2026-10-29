"""Synthetic-only G5.4 ticker-centering decomposition tests; no old returns."""
import sys
import unittest
from pathlib import Path
import numpy as np
SRC=Path(__file__).resolve().parents[1]/"research"/"reviews"/"icomputing_2026"
sys.path.insert(0,str(SRC))
from ic_g5_4_target_decomposition import decompose_same_target,DecompositionError

class TargetDecompositionTests(unittest.TestCase):
    def test_sign_reversal_due_to_train_center_selection_composition(self):
        # Raw clipped selected quality worse by 1 but transformed outcome
        # improvement +9 comes from selecting ticker whose train center is 10 lower.
        y=np.array([0,0,9,9],dtype=np.float32)
        mu=np.array([10,10,0,0],dtype=np.float64)
        z=decompose_same_target([2,3],[0,1],y,mu)
        self.assertEqual(z["transformed_model_target_delta"],9.)
        self.assertEqual(z["pre_centered_clipped_target_delta"],-1.)
        self.assertEqual(z["train_ticker_mean_composition_delta"],-10.)

    def test_same_selected_set_zero_effect(self):
        z=decompose_same_target([1,2],[2,1],[1.,2.,3.],[.1,.2,.3])
        self.assertAlmostEqual(z["transformed_model_target_delta"],0)

    def test_zero_center_yields_identical_clipped_and_model_effect(self):
        z=decompose_same_target([2],[0],[1.,2.,3.],[0,0,0])
        self.assertEqual(z["transformed_model_target_delta"],
                         z["pre_centered_clipped_target_delta"])

    def test_unmatched_original_row_sets_rejected(self):
        with self.assertRaises(DecompositionError):
            decompose_same_target([1],[0],[1.,2.],[.1])

    def test_invalid_nonfinite_target_rejected(self):
        with self.assertRaises(DecompositionError):
            decompose_same_target([1],[0],[1.,float("nan")],[.1,.2])

    def test_duplicate_selected_rows_rejected(self):
        with self.assertRaises(DecompositionError):
            decompose_same_target([1,1],[0,1],[1.,2.,3.],[.1,.2,.3])

    def test_cannot_claim_original_trade_return_from_clipped_label(self):
        z=decompose_same_target([2],[0],[1.,2.,3.],[1.,1.,1.])
        self.assertIn("CLIPPED_TARGET",z["status"])
        self.assertFalse(z["raw_unclipped_stock_return_recovered"])
        self.assertIsNone(z["realized_tradable_pnl"])
        self.assertFalse(z["old_outcome_access_authorized_by_this_module"])

if __name__=="__main__":
    unittest.main()
