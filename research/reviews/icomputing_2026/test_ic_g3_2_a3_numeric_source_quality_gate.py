"""G3.2 A3 source ONLY: synthetic close-quality and security gates.

DO NOT open any original prices, targets or models in these tests.
"""
from __future__ import annotations
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
import unittest

from ic_g3_2_a3_numeric_source_quality_gate import (
    inspect_series,canon,validation_source_checks,N_VALID,N_OLD
)
from ic_g2_g3_exploratory_core import (
    trailing_volatility_60,ScientificGateError
)

SCRIPT=Path(__file__).with_name("ic_g3_2_a3_numeric_source_quality_gate.py")
def days(n):
    start=date(2026,1,1)
    return [start+timedelta(days=i) for i in range(n)]

class A3OriginalSourceNumericalGateTests(unittest.TestCase):
    def test_source_compiles(self):
        compile(SCRIPT.read_text(encoding="utf-8"),str(SCRIPT),"exec")
    def test_no_prices_or_original_results_in_tester(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("target_model",s)
        self.assertNotIn("forward_excess_beta(",s)
        self.assertNotIn("analyze_18_cells(",s)
        self.assertNotIn("cluster_bootstrap(",s)
        self.assertNotIn("to_pickle(",s)
        self.assertNotIn("np.save(",s)
        self.assertIn('"numeric_volatility_scores_ever_serialized":False',s)
        self.assertIn('"A3_baseline_p10_risk_outcome_comparison_executed":False',s)
    def test_human_optin_and_vintage_must_remain_unverified(self):
        s=SCRIPT.read_text(encoding="utf-8")
        for a in ("--authorize-a3-price-numeric-source-quality-only",
                  "--trust-original-audited-pickles",
                  "--acknowledge-price-provider-vintage-unverified",
                  '"original_provider_vintage_verified":False',
                  '"price_adjustments_point_in_time_verified":False'):
            self.assertIn(a,s)
    def test_sha_protect_all_174_original_prices_before_unpickling(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("guarded_prices[name]=pth",s)
        self.assertIn("sha(pth)==record.get(\"sha256_new_local_commitment\")",s)
        self.assertLess(s.index("guarded_prices[name]=pth"),
                        s.index("import pandas as pd"))
        self.assertIn("for name in (\"ic_g3_2_a3_numeric_source_quality_gate.py\",CORE_NAME,",s)
        self.assertIn("core",s.lower())
    def test_original_four_g2_report_fingerprints_bound(self):
        s=SCRIPT.read_text(encoding="utf-8")
        for digest in (
           "65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb",
           "f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3",
           "e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f",
           "e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7",
        ):
            self.assertIn(digest,s)
    def test_only_original_validation_and_three_cohorts(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("N_VALID=19880",s)
        self.assertIn("N_OLD=47596",s)
        self.assertIn('"V2":("v2_signals"',s)
        self.assertIn('"V3":("v3_signals"',s)
        self.assertIn('"V4":("v4_signals"',s)
    def test_reject_unfrozen_bad_original_g2_lineage(self):
        correct={
          "status":"G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN",
          "watched_historical_filenames":{"2026-07-05":[{}]*174}
        }
        newer={
          "status":"G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN"
        }
        old={
          "status":"G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN",
          "v1_v4_event_pair_key_date_set_agreement":True,
          "source_cache_files_checked":174,
          "original_g2_9_report_sha256":"65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb",
          "original_g2_10_report_sha256":"f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3"
        }
        valid={
          "status":"G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN",
          "original_v0_model_rows_current_sha256":"3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724",
          "original_valid_split_rows":19880,
          "original_price_cache_files_sha_checked":174,
          "original_g2_12_sha256":"e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f"
        }
        binding={"status":"G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED"}
        manifest=validation_source_checks(correct,newer,old,valid,binding)
        self.assertEqual(len(manifest),174)
        valid["original_valid_split_rows"]=19879
        with self.assertRaisesRegex(RuntimeError,"ancestry drift"):
            validation_source_checks(correct,newer,old,valid,binding)
    def test_full_61_pre_event_closes_produce_source_eligible_count(self):
        x=days(70)
        event=x[-1]+timedelta(days=1)
        prices={"AAA":(x,[100+i*.1 for i in range(len(x))])}
        r=inspect_series([event,event,event],["AAA"]*3,
                         prices,trailing_volatility_60)
        self.assertEqual(r,{"OK_RETROSPECTIVE_DATE_ONLY_VINTAGE_UNVERIFIED":3})
    def test_no_40_return_fallback_and_no_event_day(self):
        d=days(62)
        price={"AAA":(d,list(range(100,162)))}
        r=inspect_series([d[60],d[60]],[ "AAA","AAA"],price,trailing_volatility_60)
        self.assertEqual(r,{"INSUFFICIENT_61_PRIOR_BARS":2})
    def test_selected_invalid_close_excludes_identical_event_pairs(self):
        d=days(65)
        close=[100+i for i in range(65)]
        close[-1]=float("nan")
        p={"AAA":(d,close)}
        event=d[-1]+timedelta(days=1)
        r=inspect_series([event,event],["AAA","AAA"],
                         p,trailing_volatility_60)
        self.assertEqual(r,{"INVALID_SELECTED_HISTORIC_CLOSE":2})
    def test_missed_symbol_counted_not_silently_dropped(self):
        d=days(70)
        p={"AAA":(d,[100+i for i in range(70)])}
        r=inspect_series([d[-1]+timedelta(days=1)]*3,
                         ["AAA","MISSING","AAA"],p,trailing_volatility_60)
        self.assertEqual(sum(r.values()),3)
        self.assertEqual(r["MISSING_ORIGINAL_PRICE_SYMBOL"],1)
    def test_brk_alias_only(self):
        self.assertEqual(canon("BRK.B"),"BRK-B")
        self.assertEqual(canon("BRK-B"),"BRK-B")
        self.assertEqual(canon("SPY"),"SPY")

if __name__=="__main__":
    unittest.main()
