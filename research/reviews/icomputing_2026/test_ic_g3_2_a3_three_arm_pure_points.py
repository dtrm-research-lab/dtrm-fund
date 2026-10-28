"""Synthetic only: A3 three-arm paired point estimands, no old targets read."""
from datetime import date,timedelta
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

from ic_g3_2_a3_three_arm_pure_points import (
    EXPECTED,K_FRACTION,RISK_CUTOFF,
    source_risk_admission_mask,three_arm_point_effects
)
from ic_g2_g3_exploratory_core import select_topk,ScientificGateError

N=EXPECTED["V2"]

def fixtures():
    prediction=np.linspace(2.,-2.,N,dtype=np.float64)
    target=np.linspace(-.3,.7,N,dtype=np.float32)
    p10=np.arange(N)%3!=0
    risk=np.arange(N)%4!=0
    return prediction,target,p10,risk

def surrogate_original_parity(cohort,pred,y,mask):
    return select_topk(pred,y,mask,.10)

class A3ThreeArmPureTests(unittest.TestCase):
    def test_three_arm_point_consistent_frozen_original_selection(self):
        p,y,a,b=fixtures()
        with patch("ic_g3_2_a3_three_arm_pure_points.assert_original_q25_k10_replication",
                   side_effect=surrogate_original_parity) as parity:
            result=three_arm_point_effects("V2",p,y,a,b)
        self.assertEqual(parity.call_count,1)
        self.assertEqual(result["K_floor_10_percent"],444)
        self.assertTrue(result["all_three_original_arms_full_K"])
        self.assertAlmostEqual(result["p10_minus_risk_paired_delta_mean"],
             result["p10_minus_baseline_delta_mean"]-
             result["risk_minus_baseline_delta_mean"],places=12)
        self.assertIsNone(result["paired_news_cluster_ci"])
        self.assertFalse(result["financial_target_is_realized_trading_pnl"])
    def test_original_precision_float32_not_promoted(self):
        p,y,a,b=fixtures()
        with patch("ic_g3_2_a3_three_arm_pure_points.assert_original_q25_k10_replication",
                   side_effect=surrogate_original_parity):
            result=three_arm_point_effects("V2",p,y,a,b)
        expected=select_topk(p,y,a,.10)
        self.assertEqual(result["original_p10_q25_topk_mean_forward_excess_beta"],
                         expected.candidate_mean)
    def test_original_q25_parity_failure_never_ignored(self):
        p,y,a,b=fixtures()
        with patch("ic_g3_2_a3_three_arm_pure_points.assert_original_q25_k10_replication",
                   side_effect=ScientificGateError("1e-12 parity failure")):
            with self.assertRaisesRegex(ScientificGateError,"1e-12"):
                three_arm_point_effects("V2",p,y,a,b)
    def test_no_partial_fill_risk_policy(self):
        p,y,a,b=fixtures();b[:]=False
        with patch("ic_g3_2_a3_three_arm_pure_points.assert_original_q25_k10_replication",
                   side_effect=surrogate_original_parity):
            with self.assertRaisesRegex(ScientificGateError,"cannot fill"):
                three_arm_point_effects("V2",p,y,a,b)
    def test_input_sample_drift_fail_closed(self):
        p,y,a,b=fixtures()
        with self.assertRaisesRegex(ScientificGateError,"cardinality drift"):
            three_arm_point_effects("V2",p,y[:-1],a,b)
    def test_wrong_cohort_fail_closed(self):
        p,y,a,b=fixtures()
        with self.assertRaisesRegex(ScientificGateError,"Only original"):
            three_arm_point_effects("V0",p,y,a,b)
    def test_synthetic_old_stock_vol_only_uses_earlier_bars(self):
        dates=[date(2026,1,1)+timedelta(days=i) for i in range(80)]
        signal=pd.DataFrame({
            "news_id":np.arange(N),
            "ticker":["AAA"]*N,
            "date_dt":pd.to_datetime(["2026-04-01"]*N,utc=True)})
        prices={"AAA":(dates,[100.]*80)}
        mask=source_risk_admission_mask(signal,prices,"V2")
        self.assertEqual(int(mask.sum()),N)
        self.assertEqual(mask.dtype,np.dtype(bool))
    def test_synthetic_insufficient_bars_blocks_risk(self):
        signal=pd.DataFrame({"ticker":["AAA"]*N,
            "news_id":np.arange(N),
            "date_dt":pd.to_datetime(["2026-02-01"]*N,utc=True)})
        prices={"AAA":([date(2026,1,1)],[100.])}
        with self.assertRaisesRegex(ScientificGateError,"common-eligible risk"):
            source_risk_admission_mask(signal,prices,"V2")
    def test_never_serialize_old_targets_or_call_price_loaders(self):
        from pathlib import Path
        src=Path(__file__).with_name("ic_g3_2_a3_three_arm_pure_points.py").read_text()
        for forbidden in ("pd.read_pickle","pickle.load(","json.dump(","xgboost","target_model","np.save("):
            self.assertNotIn(forbidden,src)
        self.assertIn("DATE_RESTRICTED_POST_OUTCOME_EXPLORATORY",src)

if __name__=="__main__":
    unittest.main()
