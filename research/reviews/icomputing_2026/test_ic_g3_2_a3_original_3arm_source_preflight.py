"""G3.2 A3 three-arm SOURCE-ONLY preview tests: artificial frames only.

NO local user data, saved original Pickles, targets or external files.
"""
import unittest
from pathlib import Path
from datetime import date,timedelta
import numpy as np
import pandas as pd

from ic_g3_2_a3_original_3arm_source_preflight import (
    counts,EXPECTED,CUTOFF,ORIGINAL_Q25,OFFSET,SCRIPTS
)

FILE=Path(__file__).with_name("ic_g3_2_a3_original_3arm_source_preflight.py")

def synthetic(prevent_risk=False):
    n=EXPECTED["V2"]
    raw=np.linspace(-.18,-.13,n,dtype=np.float64)
    p10=raw+OFFSET
    # Threshold comparison only: the data are artificial and have not
    # been calibrated against original real V0 source.
    scores=np.arange(n,0,-1,dtype=np.float64)
    signals=pd.DataFrame({
        "news_id":[f"fake-news-{i//2}" for i in range(n)],
        "ticker":["AAA" if i%2==0 else "BBB" for i in range(n)],
        "date_dt":pd.to_datetime(["2026-05-20T10:00:00Z"]*n),
        "baseline_prediction":scores,
        "p10_raw":raw,
        "p10_calibrated":p10,
        "p10_pass":(p10>=ORIGINAL_Q25),
    })
    # Synthetic prices with zero vol unless prevent_risk=True.
    dates=[date(2026,1,1)+timedelta(days=i) for i in range(100)]
    smooth=[101.0]*100
    volatile=[101.0 if i%2==0 else 150.0 for i in range(100)]
    prices={"AAA":(dates,volatile if prevent_risk else smooth),
            "BBB":(dates,volatile if prevent_risk else smooth)}
    return signals,prices

class A3SourceOnlyTest(unittest.TestCase):
    def test_compile_without_running_user_data(self):
        compile(FILE.read_text(),str(FILE),"exec")
    def test_does_not_load_or_compute_old_financial_targets(self):
        s=FILE.read_text()
        for forbidden in ('target_model','forward_excess_beta',
                          'reconstruct_valid_p10_only(',
                          'pd.read_pickle(local/"probabilistic_v1_holdout_model_targets_',
                          'cluster_bootstrap(', 'to_pickle(', 'np.save('):
            self.assertNotIn(forbidden,s)
        self.assertIn('"any_forward_target_or_old_outcome_opened":False',s)
        self.assertIn('"a3_old_outcome_comparison_authorized":False',s)
    def test_source_first_174_original_price_hashes_before_loading(self):
        s=FILE.read_text()
        part=s[s.index("def main():"):]
        verify=part.index("files=recheck_all_historical_price_hashes(")
        self.assertLess(verify,part.index("import pandas as pd"))
        self.assertLess(verify,part.index("pd.read_pickle("))
        self.assertIn("g26[\"g2_5_historic_old_cohort_input_sha256\"][key]",s)
        self.assertIn('"g3-2-valid-cutoff-report"',s)
    def test_fixed_original_cutoffs_in_sha_locked_calibration(self):
        s=FILE.read_text()
        self.assertIn("0.020823002555902668",s)
        self.assertIn("f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21",s)
        self.assertIn("91979425af5b3785c15fd7a74e821429f094b23c5ea1ede0c8b89efb457ee83a",s)
        self.assertIn("19880",s)
        self.assertIn("47596",s)
    def test_operator_consent_and_historic_vintage_caveat(self):
        s=FILE.read_text()
        for phrase in ("--authorize-original-a3-three-arm-source-only-preflight",
                       "--trust-original-audited-pickles",
                       "--acknowledge-vintage-unverified",
                       '"vendor_asof_acquisition_verified":False',
                       '"point_in_time_corporate_action_adjustment_verified":False'):
            self.assertIn(phrase,s)
    def test_original_signal_schema_and_p10_exact_check(self):
        signals,prices=synthetic()
        result=counts(signals,prices,"V2")
        self.assertEqual(result["old_original_pairs"],4449)
        self.assertEqual(result["k_floor_10_percent"],444)
        self.assertEqual(result["volatility_v0_cutoff_admitted_pairs"],4449)
        self.assertTrue(result["volatility_original_full_k_feasible"])
        self.assertEqual(result["p10_original_q25_admitted_pairs"],
                         int(signals["p10_pass"].sum()))
    def test_float_scores_untrusted_flag_and_offset_are_rejected(self):
        original,prices=synthetic()
        wrong=original.copy()
        wrong.loc[5,"p10_raw"]+=.01
        with self.assertRaisesRegex(RuntimeError,"offset drift"):
            counts(wrong,prices,"V2")
        invalid=original.copy()
        invalid.loc[3,"p10_pass"]=None
        with self.assertRaisesRegex(RuntimeError,"not strictly boolean"):
            counts(invalid,prices,"V2")
    def test_unfilled_risk_k_is_reported_not_spuriously_marked_full(self):
        signals,prices=synthetic(prevent_risk=True)
        result=counts(signals,prices,"V2")
        self.assertEqual(result["volatility_v0_cutoff_admitted_pairs"],0)
        self.assertFalse(result["volatility_original_full_k_feasible"])
        self.assertFalse(result["three_arms_all_full_k_feasible"])
    def test_repeated_news_id_across_tickers_permitted_but_duplicate_pair_rejected(self):
        signals,prices=synthetic()
        self.assertTrue(signals["news_id"].duplicated().any())
        self.assertEqual(counts(signals,prices,"V2")["old_original_pairs"],4449)
        signals.loc[2,["news_id","ticker"]]=signals.loc[0,["news_id","ticker"]]
        with self.assertRaisesRegex(RuntimeError,"duplicated original sample identity"):
            counts(signals,prices,"V2")
    def test_invalid_event_date_or_original_bar_blocks(self):
        signals,prices=synthetic()
        signals.loc[0,"date_dt"]=pd.NaT
        with self.assertRaisesRegex(RuntimeError,"Null or duplicated original sample"):
            counts(signals,prices,"V2")
        signals,prices=synthetic()
        prices["BBB"]=([date(2026,5,20)], [100])
        with self.assertRaisesRegex(RuntimeError,"numeric quality drift"):
            counts(signals,prices,"V2")
    def test_no_raw_pairs_or_risk_are_reported(self):
        signals,prices=synthetic()
        result=counts(signals,prices,"V2")
        self.assertNotIn("news_id",result)
        self.assertNotIn("ticker",result)
        self.assertNotIn("risk_scores",result)
        self.assertNotIn("prediction",result)
        self.assertNotIn("target",result)
        self.assertFalse(result["old_target_labels_opened"])
    def test_expected_three_original_cohorts_only(self):
        self.assertEqual(EXPECTED,{"V2":4449,"V3":2827,"V4":40320})
        self.assertIn("test_ic_g3_2_a3_original_3arm_source_preflight.py",SCRIPTS)

if __name__=="__main__":
    unittest.main()
