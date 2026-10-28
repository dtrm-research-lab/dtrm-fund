"""Synthetic-only protected G3.1 A2/A6 original-mean-parity/18-grid tests.

Builds *artificial* arrays with original cohort lengths and published
delta/hit aggregates, without opening original confidential outcomes.
No market data, no Pickles, no G3.1 authorization.
"""
import unittest
from pathlib import Path
import numpy as np
from ic_g2_g3_exploratory_core import Q25_FROZEN,P10_OFFSET,ScientificGateError,HISTORICAL
from ic_g3_1_a2_a6_pure_grid import analyze_18_cells

def synthetic_all_cohorts():
    old={}
    for key,(n,delta,hit) in HISTORICAL.items():
        k=int(n*.10)
        hits=int(round(hit*k))
        assert abs(hits/k-hit)<1e-14
        pred=np.arange(n,0,-1,dtype=float)
        mask=np.zeros(n,dtype=bool)
        mask[k:2*k]=True
        p10=np.where(mask,Q25_FROZEN+.1,Q25_FROZEN-.1)
        target=np.full(n,-.001)
        target[k:k+hits]=(delta*k/hits)-.001
        news_id=np.arange(n)
        ticker=np.arange(n)%31
        old[key]={
            "prediction":pred,"p10_calibrated":p10,
            "original_q25_pass":mask,"target":target,
            "news_id":news_id,"ticker":ticker
        }
    v=np.full(19880,Q25_FROZEN-P10_OFFSET)
    ids=np.arange(19880)
    return v,ids,old

class PureGridTests(unittest.TestCase):
    def test_all_18_cells_and_original_parity_synthetic(self):
        valid,news,old=synthetic_all_cohorts()
        result=analyze_18_cells(original_valid_p10_raw=valid,
            original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
        self.assertEqual(result["cells_expected"],18)
        self.assertEqual(len(result["cells"]),18)
        self.assertEqual(sum(r["work_package"]=="A2" for r in result["cells"]),9)
        self.assertEqual(sum(r["work_package"]=="A6" for r in result["cells"]),9)
        self.assertEqual(result["frozen_q25"],Q25_FROZEN)
        self.assertFalse(result["g3_1_execution_authorized_by_this_module"])
        for cohort in ("V2","V3","V4"):
            self.assertAlmostEqual(
                result["old_historical_q25_k10_parity"][cohort]["delta_mean"],
                HISTORICAL[cohort][1],places=12)
    def test_original_q25_k10_must_match(self):
        valid,news,old=synthetic_all_cohorts()
        old["V2"]["target"][0]=42.
        with self.assertRaises(ScientificGateError):
            analyze_18_cells(original_valid_p10_raw=valid,
                original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
    def test_original_q25_boolean_source_must_match_calibration(self):
        valid,news,old=synthetic_all_cohorts()
        old["V3"]["original_q25_pass"][0]=True
        with self.assertRaises(ScientificGateError):
            analyze_18_cells(original_valid_p10_raw=valid,
                original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
    def test_validation_p10_original_cutoff_must_match(self):
        valid,news,old=synthetic_all_cohorts()
        valid[:]+=.02
        with self.assertRaises(ScientificGateError):
            analyze_18_cells(original_valid_p10_raw=valid,
                original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
    def test_requires_all_original_three_cohorts(self):
        valid,news,old=synthetic_all_cohorts()
        del old["V4"]
        with self.assertRaises(ScientificGateError):
            analyze_18_cells(original_valid_p10_raw=valid,
                original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
    def test_bootstrap_requires_exact_10k(self):
        valid,news,old=synthetic_all_cohorts()
        with self.assertRaises(ScientificGateError):
            analyze_18_cells(original_valid_p10_raw=valid,
                original_valid_news_ids=news,old_cohorts=old,bootstrap=True,replicates=10)
    def test_a6_15_percent_full_k_infeasible_is_disclosed(self):
        valid,news,old=synthetic_all_cohorts()
        r=analyze_18_cells(original_valid_p10_raw=valid,
            original_valid_news_ids=news,old_cohorts=old,bootstrap=False)
        a6=[x for x in r["cells"] if x["work_package"]=="A6" and x["setting"]==.15]
        self.assertEqual(len(a6),3)
        self.assertTrue(all(not x["full_k_feasible"] for x in a6))
        self.assertTrue(all(x["delta_mean_forward_excess_beta"] is None for x in a6))
    def test_original_phaseii_float32_mean_exact_semantics(self):
        from ic_g2_g3_exploratory_core import select_topk,cluster_bootstrap
        n=4449
        k=int(n*.10)
        pred=np.arange(n,0,-1,dtype=np.float32)
        target=np.random.default_rng(20261028).normal(
            .12,.6,size=n).astype(np.float32)
        mask=np.zeros(n,dtype=bool)
        mask[k:k+k]=True
        old_baseline=float(target[:k].mean())
        old_candidate=float(target[k:2*k].mean())
        original_delta=old_candidate-old_baseline
        upcast_delta=(float(target[k:2*k].astype(np.float64).mean())-
                      float(target[:k].astype(np.float64).mean()))
        self.assertGreater(abs(original_delta-upcast_delta),1e-12)
        observed=select_topk(pred,target,mask,.10)
        self.assertEqual(observed.delta_mean,original_delta)
        self.assertEqual(observed.baseline_mean,old_baseline)
        self.assertEqual(observed.candidate_mean,old_candidate)
        # All historical uncertainty paths must keep source precision.
        # No 10k bootstrap here; fixed deterministic tiny synthetic check.
        from unittest.mock import patch
        with patch("ic_g2_g3_exploratory_core.select_topk",
                   wraps=select_topk) as observed_selector:
            cluster_bootstrap(pred,target,mask,np.arange(n)%100,.10,
                              seed=20260821,replicates=2)
        self.assertTrue(observed_selector.called)
        self.assertEqual(observed_selector.call_args[0][1].dtype,
                         np.dtype("float32"))
    def test_pure_module_has_no_file_io_or_implicit_authorization(self):
        code=Path(__file__).with_name("ic_g3_1_a2_a6_pure_grid.py").read_text()
        for forbidden in ("pd.read_pickle","pickle.load","read_csv(","np.load(",
                          "to_pickle","open(","argparse.ArgumentParser","sys.argv"):
            self.assertNotIn(forbidden,code)
        self.assertIn('"g3_1_execution_authorized_by_this_module":False',code)

if __name__=="__main__":
    unittest.main()
