"""Synthetic contract tests ONLY: A3 retrospective point runner, no original files."""
from pathlib import Path
import unittest

from ic_g3_2_a3_three_arm_point_runner import (
    validate_aggregate_checkpoints,check_point_against_original,
    SOURCE_PREFLIGHT_SHA,QUALITY_SHA,VALID_CUTOFF_SHA,
    G31_ORIGINAL_POINT_SHA,EXPECTED,MY_SCRIPTS
)
from ic_g3_2_a3_original_3arm_source_preflight import CUTOFF

ME=Path(__file__).with_name("ic_g3_2_a3_three_arm_point_runner.py")

def fixtures():
    pre={"status":"G3_2_A3_3_ARM_ORIGINAL_SOURCE_ONLY_K10_FEASIBILITY_PASS_OUTCOMES_BLOCKED",
         "original_historical_pairs":47596,
         "any_forward_target_or_old_outcome_opened":False,
         "a3_comparison_or_bootstrap_executed":False,
         "a3_old_outcome_comparison_authorized":False,
         "original_historical_quality_common_sample_full":True,
         "original_validation_only_cutoff_report_sha256":VALID_CUTOFF_SHA,
         "original_g3_2_numeric_source_quality_sha256":QUALITY_SHA,
         "vendor_asof_acquisition_verified":False,"cohorts":{}}
    point={"status":"G3_1_A2_A6_POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN",
        "mode":"point",
        "no_independent_matured_new_60_day_holdout":True,
        "financial_target_definition":"60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",
        "results":{"cells":[]}}
    cal={"status":"G3_2_A3_V0_VALIDATION_ONLY_WEIGHTED_VOLATILITY_CUTOFF_PASS_OUTCOMES_BLOCKED",
         "retrospective_stock_volatility_cutoff_daily_std_ddof1":CUTOFF,
         "original_validation_source_check":{"source_p10_q25_frozen":-.16665692627429962},
         "risk_threshold_uses_validation_only":True,
         "old_forward_targets_opened":False,
         "a3_old_outcome_access_authorized":False,
         "original_price_vendor_acquisition_vintage_verified":False}
    quality={"status":"G3_2_A3_NUMERIC_CLOSE_SOURCE_QUALITY_ALL_ELIGIBLE_VINTAGE_UNVERIFIED",
         "validation_common_quality_eligible_pairs":19880,
         "old_common_quality_eligible_pairs":47596,
         "forward_outcome_labels_targets_or_returns_accessed":False}
    for c,n in EXPECTED.items():
        pre["cohorts"][c]={
          "old_original_pairs":n,"common_source_quality_eligible_pairs":n,
          "k_floor_10_percent":int(.10*n),"three_arms_all_full_k_feasible":True,
          "saved_risk_cutoff":CUTOFF,
          "original_q25_cutoff":-.16665692627429962,
          "p10_original_q25_admitted_pairs":int(.6*n),
          "volatility_v0_cutoff_admitted_pairs":int(.4*n),
          "top_k_overlap_p10_volatility":int(.06*n)}
        point["results"]["cells"].append({
          "work_package":"A2","cohort":c,"setting":.25,
          "full_k_feasible":True,
          "baseline_mean_forward_excess_beta":.03,
          "veto_mean_forward_excess_beta":.1,
          "delta_mean_forward_excess_beta":.07,
          "baseline_hit_rate":.5,
          "veto_hit_rate":.6,
          "delta_hit_rate":.1})
    return pre,point,cal,quality

class ThreeArmPointRunnerChecks(unittest.TestCase):
    def test_source_compiles(self):
        compile(ME.read_text(),str(ME),"exec")
    def test_fixture_good_aggregates_pass(self):
        validate_aggregate_checkpoints(*fixtures())
    def test_missing_original_cohort_is_refused(self):
        pre,p,c,q=fixtures(); del pre["cohorts"]["V4"]
        with self.assertRaisesRegex(RuntimeError,"omitted an original cohort"):
            validate_aggregate_checkpoints(pre,p,c,q)
    def test_bad_original_cutoff_is_refused(self):
        pre,p,c,q=fixtures()
        c["retrospective_stock_volatility_cutoff_daily_std_ddof1"]+=.01
        with self.assertRaisesRegex(RuntimeError,"cutoff changed"):
            validate_aggregate_checkpoints(pre,p,c,q)
    def test_without_full_K_is_refused(self):
        pre,p,c,q=fixtures()
        pre["cohorts"]["V3"]["three_arms_all_full_k_feasible"]=False
        with self.assertRaisesRegex(RuntimeError,"preflight evidence drift"):
            validate_aggregate_checkpoints(pre,p,c,q)
    def test_original_q25_effect_must_be_unchanged(self):
        pre,p,c,q=fixtures()
        old=p["results"]["cells"][0]
        prev=pre["cohorts"]["V2"]
        new={"cohort":"V2",
             "common_original_pairs":prev["old_original_pairs"],
             "K_floor_10_percent":prev["k_floor_10_percent"],
             "p10_admitted_pairs":prev["p10_original_q25_admitted_pairs"],
             "risk_admitted_pairs":prev["volatility_v0_cutoff_admitted_pairs"],
             "topk_overlap_p10_risk":prev["top_k_overlap_p10_volatility"],
             "original_baseline_topk_mean_forward_excess_beta":
                  old["baseline_mean_forward_excess_beta"],
             "original_p10_q25_topk_mean_forward_excess_beta":
                  old["veto_mean_forward_excess_beta"],
             "p10_minus_baseline_delta_mean":old["delta_mean_forward_excess_beta"],
             "original_baseline_topk_hit_rate":old["baseline_hit_rate"],
             "original_p10_topk_hit_rate":old["veto_hit_rate"],
             "p10_minus_baseline_delta_hit":old["delta_hit_rate"]}
        check_point_against_original(new,prev,p)
        new["p10_minus_baseline_delta_mean"]+=.0001
        with self.assertRaisesRegex(RuntimeError,"G3.1 published q25"):
            check_point_against_original(new,prev,p)
    def test_requires_explicit_new_consent_and_not_old_g31_consent(self):
        s=ME.read_text()
        for f in ("--authorize-a3-retrospective-old-outcome-point-only",
                  "--acknowledge-no-independent-60d-holdout",
                  "--acknowledge-retrospective-price-vintage-unverified",
                  "--acknowledge-no-realized-tradable-pnl",
                  "--trust-original-audited-pickles"):
            self.assertIn(f,s)
        self.assertNotIn("--authorize-retrospective-a2-a6-old-outcome-access",s)
    def test_original_old_sources_and_every_price_rehashed_before_unpickle(self):
        s=ME.read_text();main=s[s.index("def main():"):]
        self.assertIn("make_release_checks(args)",main)
        self.assertIn("check_code(args.review_repo,commit)",main)
        self.assertIn("verify_local_runner_code(args.review_repo,commit)",main)
        self.assertLess(main.index("prices_bound=recheck_all_historical_price_hashes("),
                        main.index("import pandas as pd"))
        self.assertLess(main.index("prices_bound=recheck_all_historical_price_hashes("),
                        main.index("pd.read_pickle("))
    def test_original_source_and_preflight_sha_bound(self):
        s=ME.read_text()
        for c in (SOURCE_PREFLIGHT_SHA,QUALITY_SHA,VALID_CUTOFF_SHA,G31_ORIGINAL_POINT_SHA):
            self.assertIn(c,s)
        self.assertEqual(len(MY_SCRIPTS),4)
    def test_stays_point_only_and_postoutcome(self):
        s=ME.read_text()
        self.assertIn('"news_id_cluster_bootstrap_completed":False',s)
        self.assertIn('"ticker_cluster_bootstrap_completed":False',s)
        self.assertIn("DATE_RESTRICTED_POST_OUTCOME_EXPLORATORY_POINT_ONLY",s)
        for forbidden in ("--mode full","cluster_bootstrap(","booster.fit(","xgb.train(","to_pickle("):
            self.assertNotIn(forbidden,s)

if __name__=="__main__":
    unittest.main()
