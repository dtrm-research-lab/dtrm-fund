"""G3.1 original-only failure triage synthetic and static protection tests.

No real original files, Pickles, prices, targets, or G3.1 18-cell results.
"""
import ast
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
import pandas as pd

from ic_g3_1_a2_a6_join_contract import source_exact_join,extract_source_arrays,Q25,OFFSET
from ic_g2_g3_exploratory_core import select_topk
from ic_g3_1_original_q25_parity_diagnostic import one_diagnostic

SRC=Path(__file__).with_name("ic_g3_1_original_q25_parity_diagnostic.py")

def synthetic_inputs(n=4449):
    k=int(n*.1)
    pred=np.arange(n,0,-1,dtype=float)
    mask=np.zeros(n,dtype=bool)
    mask[k:k+k]=True
    raw=np.where(mask,Q25+.1-OFFSET,Q25-.1-OFFSET)
    calibrated=raw+OFFSET
    times=pd.date_range("2026-06-10",periods=n,freq="min",tz="UTC")
    keys=[f"synthetic_{i}" for i in range(n)]
    sig=pd.DataFrame({
        "news_id":keys,"ticker":["AAA"]*n,"date_dt":times,
        "baseline_prediction":pred,
        "p10_raw":raw,
        "p10_calibrated":calibrated,
        "p10_pass":mask,
    })
    tar=pd.DataFrame({
        "news_id":keys,"ticker":["AAA"]*n,
        "date_dt":times,"target_model":np.r_[np.zeros(k),np.ones(k),np.zeros(n-2*k)]
    })
    return sig,tar

def original_eval(p,mask,y):
    n=len(y);k=int(.10*n);order=np.argsort(-p)
    baseline=y[order[:k]]
    passing=order[mask[order]]
    if len(passing)<k:return None
    cand=y[passing[:k]]
    return {
     "topk_rows":k,
     "baseline_topk_mean":float(np.mean(baseline)),
     "candidate_topk_mean":float(np.mean(cand)),
     "delta_topk_mean":float(np.mean(cand)-np.mean(baseline)),
     "baseline_topk_hit_rate":float(np.mean(baseline>0)),
     "candidate_topk_hit_rate":float(np.mean(cand>0)),
     "delta_topk_hit_rate":float(np.mean(cand>0)-np.mean(baseline>0))
    }

def original_stub(sig,tar,expected_mean=1.0,expected_hit=1.0):
    j=sig.merge(tar[["news_id","ticker","date_dt","target_model"]],
                on=["news_id","ticker"],how="inner",sort=False,
                validate="one_to_one",suffixes=("_signal","_target"))
    return SimpleNamespace(
      COHORTS={"V2":{"expected_delta_mean":expected_mean,
                    "expected_delta_hit":expected_hit}},
      load_cohort=lambda a,b:j,
      evaluate_selection=original_eval
    )

class OriginalOnlyDiagnosticSyntheticTests(unittest.TestCase):
    def test_compiles_without_implicit_cli_execution(self):
        compile(SRC.read_text(),str(SRC),"exec")
    def test_preserves_original_historical_phase2_function(self):
        s=SRC.read_text()
        self.assertIn('original.load_cohort(files[(cohort,"signals")],files[(cohort,"targets")])',s)
        self.assertIn('original.evaluate_selection(',s)
        self.assertIn('c7502a690162459cdfb3413573e3133c42efb126',s)
        self.assertIn('APPROVED_G31="5cf62c854643576ee6059ac44f55a805b8ff3137"',s)
    def test_rehashes_sources_and_frozen_code_before_deserialize(self):
        s=SRC.read_text()
        self.assertIn("frozen_source(Path(__file__).resolve(),REL,review,diagnostic_commit)",s)
        self.assertIn("frozen_source(original_path,OLD,original_root,FROZEN_ORIGINAL)",s)
        self.assertIn("exact,bound=make_release_checks(a)",s)
        self.assertLess(s.index("exact,bound=make_release_checks(a)"),
                        s.index("original=original_module(original_path)"))
    def test_human_authorization_is_diagnostic_only(self):
        s=SRC.read_text()
        self.assertIn("--authorize-original-q25-parity-diagnostic-only",s)
        self.assertIn("--trust-previously-sha-audited-original-pickles",s)
        for token in ('"any_q15_q35_or_k5_k15_sensitivity_executed":False',
                      '"any_bootstrap_executed":False',
                      '"any_new_a2_a6_18_cell_result_executed":False',
                      '"g3_1_18_cell_results_authorized_by_diagnostic":False'):
            self.assertIn(token,s)
    def test_synthetic_exact_original_and_guarded_parity(self):
        sig,tar=synthetic_inputs()
        stub=original_stub(sig,tar)
        with patch("pandas.read_pickle",side_effect=[sig,tar]):
            r=one_diagnostic(stub,"V2",
                {("V2","signals"):Path("s.pkl"),("V2","targets"):Path("t.pkl")},
                source_exact_join,extract_source_arrays,select_topk)
        self.assertEqual(r["classification"],"ORIGINAL_AND_PROTECTED_Q25_K10_PARITY_PASS")
        self.assertTrue(r["original_point_parity_pass"])
        self.assertTrue(r["protected_point_parity_pass"])
    def test_synthetic_original_source_vs_historical_expected_drift_classified(self):
        sig,tar=synthetic_inputs()
        stub=original_stub(sig,tar,expected_mean=1.01)
        with patch("pandas.read_pickle",side_effect=[sig,tar]):
            r=one_diagnostic(stub,"V2",
                {("V2","signals"):Path("s.pkl"),("V2","targets"):Path("t.pkl")},
                source_exact_join,extract_source_arrays,select_topk)
        self.assertEqual(r["classification"],
            "ORIGINAL_SOURCE_VS_FROZEN_EXPECTED_MISMATCH_METHODS_AGREE")
        self.assertFalse(r["original_point_parity_pass"])
        self.assertTrue(r["two_implementations_agree"])
    def test_original_source_and_protected_selection_disagreement_classified(self):
        sig,tar=synthetic_inputs()
        stub=original_stub(sig,tar)
        def wrong_selection(p,y,mask,fraction):
            from dataclasses import replace
            z=select_topk(p,y,mask,fraction)
            return replace(z,delta_mean=z.delta_mean+0.1)
        with patch("pandas.read_pickle",side_effect=[sig,tar]):
            r=one_diagnostic(stub,"V2",
                {("V2","signals"):Path("s.pkl"),("V2","targets"):Path("t.pkl")},
                source_exact_join,extract_source_arrays,wrong_selection)
        self.assertEqual(r["classification"],"NEW_JOIN_OR_SELECTION_REGRESSION_ORIGINAL_IS_PASS")
        self.assertTrue(r["original_point_parity_pass"])
        self.assertFalse(r["two_implementations_agree"])
    def test_no_nonlegacy_experiments_or_raw_result_files(self):
        s=SRC.read_text()
        for token in ("cluster_bootstrap(","analyze_18_cells(",
                      "reconstruct_valid_p10_only(","to_pickle(","to_csv(",
                      "np.save("):
            self.assertNotIn(token,s)
        self.assertIn('"target_not_realized_portfolio_pnl":True',s)

if __name__=="__main__":
    unittest.main()
