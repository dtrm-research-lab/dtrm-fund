"""Synthetic-only verification of the read-only 36-block report QA.

NO original private files opened or financial model inference.
"""
import copy
from pathlib import Path
import unittest

from ic_g3_1_a2_a6_full_report_qa import (
    qa,POINT_SHA,FULL_SHA,CODE_SHA,G2_FREEZE,G3_0_SHA,SOURCES_SHA,
    VALIDATION_THRESHOLDS,EXPECTED,ROWS,
)

def fake_pair():
    common={
       "immutable_a2_a6_runner_commit":CODE_SHA,
       "original_g2_freeze_commit":G2_FREEZE,
       "original_g3_0_source_report_sha256":G3_0_SHA,
       "six_original_source_report_sha256":SOURCES_SHA,
       "a3_price_volatility_experiment_authorized":False,
       "no_independent_matured_new_60_day_holdout":True,
       "all_old_outcomes_were_previously_consulted":True,
       "financial_target_definition":"60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",
    }
    def res():
        return {
         "cells_expected":18,
         "cutoffs_validation_only":VALIDATION_THRESHOLDS.copy(),
         "frozen_q25":VALIDATION_THRESHOLDS["0.25"],
         "target_is_tradable_portfolio_profit":False,
         "independent_new_60_day_holdout":False,
         "g3_1_execution_authorized_by_this_module":False,
         "cells":[]
        }
    pt={**common,"status":"G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN",
        "mode":"point","results":res()}
    fu={**common,"status":"G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY",
        "mode":"full","results":res()}
    pt["results"]["replicates_per_news_or_ticker_cell"]=0
    fu["results"]["replicates_per_news_or_ticker_cell"]=10000
    for arm in ("A2","A6"):
        for cohort in ("V2","V3","V4"):
            for setting in ((.15,.25,.35) if arm=="A2" else (.05,.10,.15)):
                record={
                 "work_package":arm,"cohort":cohort,"setting":setting,
                 "n_original_pairs":ROWS[cohort],
                 "k_required":int(ROWS[cohort]*.10),"admitted_pairs":int(ROWS[cohort]*.5),
                 "admitted_rate":.5,"full_k_feasible":True,
                 "baseline_mean_forward_excess_beta":0.02,
                 "veto_mean_forward_excess_beta":0.07,
                 "delta_mean_forward_excess_beta":0.05,
                 "baseline_hit_rate":0.43,"veto_hit_rate":0.51,
                 "delta_hit_rate":0.08,
                 "inferential_scope":"POST_OUTCOME_EXPLORATORY_NOT_PROSPECTIVE",
                 "news_cluster_bootstrap":None,
                 "ticker_cluster_bootstrap":None
                }
                pt["results"]["cells"].append(copy.deepcopy(record))
                for field,seed in (("news_cluster_bootstrap",20260821),
                                    ("ticker_cluster_bootstrap",20260822)):
                    record[field]={
                     "method":"cluster_bootstrap",
                     "replicates":10000,"seed":seed,"infeasible_replicates":0,
                     "ci95_delta_topk_mean":[0.01,0.08],
                     "ci95_delta_topk_hit_rate":[0.01,0.12],
                     "interpretation":"POST_OUTCOME_EXPLORATORY_NOT_INDEPENDENT_CONFIRMATION"
                    }
                fu["results"]["cells"].append(copy.deepcopy(record))
    return pt,fu

def cell(doc,arm,cohort,setting):
    return next(x for x in doc["results"]["cells"]
                if (x["work_package"],x["cohort"],x["setting"])==
                   (arm,cohort,setting))

class OnlyAggregateReportQATests(unittest.TestCase):
    def test_compiles_without_original_imports_or_side_effects(self):
        s=Path(__file__).with_name("ic_g3_1_a2_a6_full_report_qa.py").read_text()
        compile(s,"report_qa.py","exec")
        for forbidden in ("pd.read_pickle","pickle.load(","np.load(","xgb.","from dtrm","read_csv("):
            self.assertNotIn(forbidden,s)
    def test_36_valid_blocks_and_18_unchanged_points_pass(self):
        p,f=fake_pair()
        s=qa(p,f)
        self.assertEqual(s["valid_cluster_blocks"],36)
        self.assertEqual(s["withheld_cluster_blocks"],0)
        self.assertEqual(s["cells_with_both_news_and_ticker_intervals_valid"],18)
        self.assertEqual(s["cells_both_unadjusted_mean_cis_exclude_zero"],18)
    def test_one_infeasible_draw_requires_interval_suppression(self):
        p,f=fake_pair()
        c=cell(f,"A6","V4",.15)["news_cluster_bootstrap"]
        c["infeasible_replicates"]=1
        c["ci95_delta_topk_mean"]=None
        c["ci95_delta_topk_hit_rate"]=None
        s=qa(p,f)
        self.assertEqual(s["valid_cluster_blocks"],35)
        self.assertEqual(s["withheld_cluster_blocks"],1)
        self.assertEqual(s["cells_with_both_news_and_ticker_intervals_valid"],17)
    def test_infeasible_draw_with_published_ci_refused(self):
        p,f=fake_pair()
        c=cell(f,"A6","V4",.15)["news_cluster_bootstrap"]
        c["infeasible_replicates"]=1
        with self.assertRaisesRegex(ValueError,"Invalid interval"):
            qa(p,f)
    def test_changed_point_mean_refused(self):
        p,f=fake_pair()
        cell(f,"A2","V2",.35)["delta_mean_forward_excess_beta"]=.08
        with self.assertRaisesRegex(ValueError,"point estimate changed"):
            qa(p,f)
    def test_corrupt_or_nonfinite_ci_refused(self):
        p,f=fake_pair()
        c=cell(f,"A2","V3",.35)["ticker_cluster_bootstrap"]
        c["ci95_delta_topk_mean"]=[float("nan"),.1]
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            qa(p,f)
    def test_different_seed_refused(self):
        p,f=fake_pair()
        cell(f,"A2","V2",.15)["news_cluster_bootstrap"]["seed"]=7
        with self.assertRaisesRegex(ValueError,"changed fixed"):
            qa(p,f)
    def test_original_q25_k10_duplicate_ci_inequality_refused(self):
        p,f=fake_pair()
        cell(f,"A2","V3",.25)["news_cluster_bootstrap"]["ci95_delta_topk_mean"]=[.02,.09]
        with self.assertRaisesRegex(ValueError,"no longer deterministic"):
            qa(p,f)
    def test_missing_cell_refused(self):
        p,f=fake_pair()
        f["results"]["cells"].pop()
        with self.assertRaisesRegex(ValueError,"Not exactly 18"):
            qa(p,f)
    def test_original_source_and_commit_lineage_drift_refused(self):
        p,f=fake_pair()
        f["immutable_a2_a6_runner_commit"]="0"*40
        with self.assertRaisesRegex(ValueError,"commit differs"):
            qa(p,f)
    def test_withheld_ci_not_reported_as_statistical_significance(self):
        p,f=fake_pair()
        c=cell(f,"A6","V4",.15)["ticker_cluster_bootstrap"]
        c["infeasible_replicates"]=30
        c["ci95_delta_topk_mean"]=None
        c["ci95_delta_topk_hit_rate"]=None
        out=qa(p,f)
        self.assertIsNone(out["cluster_results"][("A6","V4",.15)]["ticker"][
                          "mean_ci95_excludes_zero_unadjusted"])
        self.assertFalse(out["familywise_multiple_testing_adjusted"])
        self.assertFalse(out["independent_holdout"])
        self.assertFalse(out["target_is_realized_portfolio_pnl"])

if __name__=="__main__":
    unittest.main()
