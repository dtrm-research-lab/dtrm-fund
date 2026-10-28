"""Synthetic-only regression tests; no financial inputs, no G3 execution."""
import unittest
from datetime import date
import numpy as np
from ic_g2_g3_exploratory_core import (
    ScientificGateError,original_weighted_quantile,legacy_news_weights,
    select_topk,cluster_bootstrap,trailing_volatility_60,
    validation_only_volatility_cutoff,original_validation_p10_thresholds,
    assert_original_q25_k10_replication,
)

class FrozenExploratoryCoreTests(unittest.TestCase):
    def test_original_weighted_quantile_left_search(self):
        self.assertEqual(original_weighted_quantile([1,2,3,4],[1,1,1,1],.25),1.)
        self.assertEqual(original_weighted_quantile([1,2,3,4],[1,1,1,1],.50),2.)
        self.assertEqual(original_weighted_quantile([1,2,3,4],[1,1,1,1],.75),3.)
    def test_legacy_per_news_weights(self):
        np.testing.assert_allclose(legacy_news_weights(["a","b","a","c","a","b"]),
                                   [1/3,1/2,1/3,1,1/3,1/2])
    def test_bad_weight_rejected(self):
        for weights in ([1,0,1],[-1,1,1],[1,float("nan"),1]):
            with self.assertRaises(ScientificGateError):
                original_weighted_quantile([1,2,3],weights,.25)
    def test_original_10_percent_k_floor_and_argsort(self):
        a=select_topk([1,4,3,2,0,5,6,7,8,9],
                      [1,2,3,4,5,6,7,8,9,10],
                      [True,True,True,True,True,True,True,True,True,True],.10)
        self.assertEqual(a.k,1)
        self.assertEqual(a.baseline_mean,10)
        self.assertEqual(a.delta_mean,0)
    def test_veto_walks_original_order_no_reranking(self):
        x=[9,8,7,6,5,4,3,2,1,0]
        y=[0,1,2,3,4,5,6,7,8,9]
        mask=[False,False,True,True]+[False]*6
        r=select_topk(x,y,mask,.2)
        self.assertTrue(r.feasible)
        self.assertEqual(r.k,2)
        self.assertEqual(r.admitted,2)
        self.assertEqual(r.baseline_mean,.5)
        self.assertEqual(r.candidate_mean,2.5)
    def test_infeasible_k_no_partial_fill(self):
        r=select_topk(range(10),range(10),[True]+[False]*9,.3)
        self.assertFalse(r.feasible)
        self.assertIsNone(r.delta_mean)
        self.assertIsNone(r.candidate_hit_rate)
    def test_original_parity_fail_closed(self):
        with self.assertRaises(ScientificGateError):
            assert_original_q25_k10_replication("V2",[0]*4449,[0]*4449,[True]*4449)
    def test_input_nonfinite_rejected(self):
        with self.assertRaises(ScientificGateError):
            select_topk([1,float("nan")],[0,1],[True,True],.5)
    def test_bootstrap_duplicate_cluster_and_determinism(self):
        p=[5,4,3,2,1,0,1,2,3,4]
        y=[5,4,3,2,1,0,1,2,3,4]
        c=["a","a","b","b","c","c","d","d","e","e"]
        mask=[True]*10
        a=cluster_bootstrap(p,y,mask,c,.3,seed=42,replicates=40)
        b=cluster_bootstrap(p,y,mask,c,.3,seed=42,replicates=40)
        self.assertEqual(a,b)
        self.assertEqual(a["infeasible_replicates"],0)
        self.assertIsNotNone(a["ci95_delta_topk_mean"])
    def test_bootstrap_infeasible_withholds_ci(self):
        p=[10,9,8,7,6,5,4,3,2,1]
        y=list(range(10))
        c=list("abcdefghij")
        mask=[True]+[False]*9
        r=cluster_bootstrap(p,y,mask,c,.5,seed=6,replicates=50)
        self.assertEqual(r["infeasible_replicates"],50)
        self.assertIsNone(r["ci95_delta_topk_mean"])
    def test_event_day_bar_not_usable(self):
        days=[date.fromordinal(date(2025,1,1).toordinal()+i) for i in range(61)]
        closes=[100+i for i in range(61)]
        v,status=trailing_volatility_60(days,closes,date(2025,3,2))
        # 2025-03-02 is 60 days after Jan 1. Last dated bar (Mar 2)
        # must not enter the previous 61 closes, so only 60 remain.
        self.assertIsNone(v)
        self.assertEqual(status,"INSUFFICIENT_61_PRIOR_BARS")
    def test_volatility_requires_full_60_returns(self):
        days=[date.fromordinal(date(2025,1,1).toordinal()+i) for i in range(70)]
        values=[100+i for i in range(70)]
        v,status=trailing_volatility_60(days,values,date(2025,3,30))
        self.assertIsNotNone(v)
        self.assertEqual(status,"OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED")
        self.assertGreaterEqual(v,0.)
    def test_missing_close_has_no_40_return_fallback(self):
        start=date(2025,1,1).toordinal()
        days=[date.fromordinal(start+i) for i in range(65)]
        price=[100+i for i in range(65)]
        price[-1]=float("nan")
        value,status=trailing_volatility_60(days,price,date(2025,4,1))
        self.assertIsNone(value)
        self.assertEqual(status,"INVALID_SELECTED_HISTORIC_CLOSE")
    def test_duplicate_dates_fail_closed(self):
        with self.assertRaises(ScientificGateError):
            trailing_volatility_60([date(2025,1,1)]*61,[100]*61,date(2025,4,1))
    def test_validation_only_volatility_cutoff(self):
        r=validation_only_volatility_cutoff([.10,.20,.30,.40],
                                           [True,True,False,False],
                                           ["a","b","c","d"])
        self.assertEqual(r["cutoff"],.20)
        self.assertEqual(r["original_p10_weighted_admission"],.5)
        self.assertFalse("target" in r)
    def test_validation_pred_requires_original_19880(self):
        with self.assertRaises(ScientificGateError):
            original_validation_p10_thresholds([0,1],["a","b"])
    def test_g3_source_module_does_not_open_any_original_inputs(self):
        from pathlib import Path
        src=Path(__file__).with_name("ic_g2_g3_exploratory_core.py").read_text()
        for forbidden in ("read_pickle","open(","xgb.train(","pd.read_csv(","loadtxt(","pickle.load"):
            self.assertNotIn(forbidden,src)

if __name__=="__main__":
    unittest.main()
