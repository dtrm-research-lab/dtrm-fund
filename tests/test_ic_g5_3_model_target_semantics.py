"""Audits original target preprocessing on synthetic numbers; no original financial data."""
from __future__ import annotations
import unittest
import numpy as np
from dtrm.legacy_target_preprocessing import preprocess_legacy_targets

class OriginalModelTargetSemantics(unittest.TestCase):
    def setUp(self):
        self.z=preprocess_legacy_targets(
            train_tickers=["A","A","B","B"],
            train_targets=[0.0,2.0,4.0,100.0],
            valid_tickers=["A","C"],
            valid_targets=[1.0,3.0],
            test_tickers=["B","C"],
            test_targets=[5.0,6.0],
        )

    def test_train_only_quantile_clipping_bounds(self):
        self.assertGreater(self.z["clip_lower"],0.0)
        self.assertLess(self.z["clip_upper"],100.0)

    def test_training_ticker_means_recenter_clipped_label(self):
        self.assertAlmostEqual(float(np.mean(self.z["train"][:2])),0.0,places=5)
        self.assertAlmostEqual(float(np.mean(self.z["train"][2:])),0.0,places=5)

    def test_validation_ticker_uses_train_center_not_validation_mean(self):
        a=self.z["valid"][0]
        self.assertTrue(np.isfinite(a))
        self.assertNotEqual(float(a),1.0)
        self.assertEqual(self.z["valid"].dtype,np.float32)

    def test_unknown_ticker_has_zero_train_center(self):
        self.assertNotIn("C",self.z["ticker_means"])
        self.assertAlmostEqual(float(self.z["valid"][1]),3.0,places=5)

    def test_clipped_raw_information_cannot_be_recovered_from_model_label(self):
        # Two different raw targets beyond train upper bound collapse to the
        # SAME transformed model label for an unseen ticker.
        a=preprocess_legacy_targets(
            train_tickers=["A","A","B","B"],train_targets=[0.0,2.0,4.0,100.0],
            valid_tickers=["C","C"],valid_targets=[101.0,999.0],
            test_tickers=["C","C"],test_targets=[101.0,999.0],
        )
        self.assertEqual(float(a["valid"][0]),float(a["valid"][1]))

    def test_model_target_not_raw_cash_return(self):
        # Formal counterexample: raw training 100 and model target ~= midpoint
        # minus ticker mean; hence an observed negative transformed label does
        # NOT mathematically imply a negative raw stock return.
        self.assertGreater(100.0,0)
        self.assertLess(float(self.z["train"][2]),0.0)

if __name__=="__main__":
    unittest.main()
