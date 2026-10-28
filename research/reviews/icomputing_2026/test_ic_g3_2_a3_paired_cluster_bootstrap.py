"""G3.2 A3 paired cluster bootstrap, synthetic-only protection tests."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
from ic_g3_2_a3_paired_cluster_bootstrap import (
    original_paired_a3_cluster_bootstrap
)
from ic_g2_g3_exploratory_core import (
    ScientificGateError,SEEDS,select_topk
)

FILE=Path(__file__).with_name("ic_g3_2_a3_paired_cluster_bootstrap.py")

def three_arm():
    n=4449
    score=np.linspace(-2,2,n,dtype=np.float64)
    y=np.linspace(-.8,.8,n,dtype=np.float32)
    a=np.arange(n)%3!=0
    b=np.arange(n)%4!=0
    news=np.asarray([f"syn-{i//15}" for i in range(n)],dtype=object)
    ticker=np.asarray([f"syn-{i%30}" for i in range(n)],dtype=object)
    return score,y,a,b,news,ticker

class FakeRandom:
    def __init__(self,c,selected=0):
        self.c=c
        self.selected=selected
    def integers(self,low,high,size):
        # deterministic resample all observed clusters once.
        return np.arange(size)

class A3PairedClusterTests(unittest.TestCase):
    def test_synthetic_fixed_10k_no_io_both_ci_available(self):
        p,y,a,b,news,ticker=three_arm()
        with patch("ic_g3_2_a3_paired_cluster_bootstrap.np.random.default_rng",
                   return_value=FakeRandom(30)):
            r=original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,news,scheme="news_id")
        self.assertEqual(r["replicates"],10000)
        self.assertEqual(r["infeasible_replicates"],0)
        self.assertEqual(r["seed"],SEEDS["news_id"])
        self.assertEqual(r["source_float_dtype_preserved"],"float32")
        expected_p=select_topk(p,y,a,.10)
        expected_v=select_topk(p,y,b,.10)
        for name,value in (
            ("p10_minus_risk",expected_p.candidate_mean-expected_v.candidate_mean),
            ("p10_minus_baseline",expected_p.delta_mean),
            ("risk_minus_baseline",expected_v.delta_mean)):
            self.assertEqual(r["comparison_intervals"][name]["ci95_delta_mean"],
                             [value,value])
    def test_bootstrap_both_policies_must_fill_K_else_all_ci_withheld(self):
        p,y,a,b,news,ticker=three_arm()
        # Withhold only on resampled infeasibility, despite both
        # original arms being feasible.
        a[:]=True
        b[:]=False
        b[:500]=True
        self.assertTrue(select_topk(p,y,b,.1).feasible)
        # two sampled clusters hold the only eligible volatility
        # positions; when the full sample loses one, fewer than K admit.
        ticker=np.asarray(["hi" if i<500 else "lo" for i in range(len(p))])
        class Unbalanced:
            def integers(self,low,high,size):
                return np.asarray([1,1],dtype=int)
        with patch("ic_g3_2_a3_paired_cluster_bootstrap.np.random.default_rng",
                   return_value=Unbalanced()):
            r=original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,ticker,scheme="ticker")
        self.assertEqual(r["infeasible_replicates"],10000)
        self.assertEqual(r["feasible_replicates"],0)
        for v in r["comparison_intervals"].values():
            self.assertIsNone(v["ci95_delta_mean"])
            self.assertIsNone(v["ci95_delta_hit_rate"])
    def test_not_10000_replications_refused(self):
        p,y,a,b,news,ticker=three_arm()
        with self.assertRaisesRegex(ScientificGateError,"Fixed 10k"):
            original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,news,scheme="news_id",replicates=9999)
    def test_unknown_schemes_refused(self):
        p,y,a,b,news,ticker=three_arm()
        with self.assertRaisesRegex(ScientificGateError,"frozen news_id/ticker"):
            original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,news,scheme="price_date")
    def test_original_truncation_refused(self):
        p,y,a,b,news,ticker=three_arm()
        with self.assertRaisesRegex(ScientificGateError,"alignment drift"):
            original_paired_a3_cluster_bootstrap(
                "V2",p[:-1],y,a,b,news,scheme="news_id")
    def test_float32_target_retained_and_double_not_required(self):
        p,y,a,b,news,ticker=three_arm()
        self.assertEqual(y.dtype,np.float32)
        with patch("ic_g3_2_a3_paired_cluster_bootstrap.np.random.default_rng",
                   return_value=FakeRandom(30)):
            r=original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,news,scheme="news_id")
        self.assertEqual(r["source_float_dtype_preserved"],"float32")
    def test_original_no_full_K_refused_before_bootstrapping(self):
        p,y,a,b,news,ticker=three_arm()
        b[:]=False
        with self.assertRaisesRegex(ScientificGateError,"cannot fill K"):
            original_paired_a3_cluster_bootstrap(
                "V2",p,y,a,b,news,scheme="news_id")
    def test_no_original_source_readers_or_training_in_pure_module(self):
        s=FILE.read_text()
        compile(s,str(FILE),"exec")
        for x in ("pd.read_pickle(","pickle.load(","json.dump(","np.load(",
                  "xgb.train(","from dtrm.","target_model","requests.get("):
            self.assertNotIn(x,s)
        self.assertIn("RETROSPECTIVE_UNADJUSTED_NOT_INDEPENDENT_CONFIRMATION",s)
        self.assertIn('"provider_price_vintage_verified":False',s)

if __name__=="__main__":
    unittest.main()
