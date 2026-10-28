"""No-real-data checks for protected A3 10k news/ticker bootstrap runner."""
from pathlib import Path
import unittest
from ic_g3_2_a3_paired_bootstrap_runner import (
    verify_prior_point_rows,CODE_FILES,A3_PRIOR_POINT_SHA,
    SOURCE_PREFLIGHT_SHA,VALID_CUTOFF_SHA,
)
SRC=Path(__file__).with_name("ic_g3_2_a3_paired_bootstrap_runner.py")

class A3PairedRunnerSourceGuards(unittest.TestCase):
    def test_python_compiles_without_any_original_outcome_access(self):
        compile(SRC.read_text(),str(SRC),"exec")
    def test_old_exact_point_values_must_be_preserved(self):
        original={"status":"G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY",
                  "news_id_cluster_bootstrap_completed":False,
                  "ticker_cluster_bootstrap_completed":False,
                  "original_price_vendor_asof_vintage_verified":False,
                  "original_parity_q25_k10_rechecked":True,
                  "cohorts":[
                    {"cohort":"V2","p10_minus_risk_paired_delta_mean":-.0886290855705738},
                    {"cohort":"V3","p10_minus_risk_paired_delta_mean":-.09183247573673725},
                    {"cohort":"V4","p10_minus_risk_paired_delta_mean":-.04405925236642361}
                  ]}
        verify_prior_point_rows(original,{
            "cohort":"V3","p10_minus_risk_paired_delta_mean":-.09183247573673725})
        with self.assertRaisesRegex(RuntimeError,"point effect"):
            verify_prior_point_rows(original,{
                "cohort":"V3","p10_minus_risk_paired_delta_mean":+.09183247573673725})
    def test_prior_point_with_bootstrap_fails(self):
        original={"status":"G3_2_A3_ORIGINAL_3_ARM_PAIRED_POINT_ONLY_POST_OUTCOME_EXPLORATORY",
                  "news_id_cluster_bootstrap_completed":True,
                  "ticker_cluster_bootstrap_completed":False,
                  "original_price_vendor_asof_vintage_verified":False,
                  "original_parity_q25_k10_rechecked":True,
                  "cohorts":[{}, {}, {}]}
        with self.assertRaisesRegex(RuntimeError,"Prior exact original A3"):
            verify_prior_point_rows(original,{"cohort":"V2"})
    def test_new_scoped_consent_is_not_reused_point_consent(self):
        s=SRC.read_text()
        self.assertIn("--authorize-a3-old-outcomes-paired-news-ticker-bootstrap",s)
        self.assertNotIn("--authorize-a3-retrospective-old-outcome-point-only",s)
        for flag in ("--acknowledge-no-independent-60d-holdout",
                     "--acknowledge-retrospective-price-vintage-unverified",
                     "--acknowledge-no-realized-tradable-pnl",
                     "--trust-original-audited-pickles"):
            self.assertIn(flag,s)
    def test_prior_original_sha_and_all_scientific_source_gates(self):
        s=SRC.read_text()
        self.assertEqual(len(CODE_FILES),4)
        # The prior A3 POINT digest is defined locally, while both
        # the source-only preflight and V0 calibration digests are
        # deliberately imported from the earlier SHA-bound A3 runner.
        # Test the resolved values AND their actual evidence() binding,
        # not the incidental presence of duplicate digest literals.
        self.assertEqual(
            A3_PRIOR_POINT_SHA,
            "b5b94f09d57d8bb3336ea01eb469f5ef703743a1217422be7e0f4b98484b4087")
        self.assertEqual(
            SOURCE_PREFLIGHT_SHA,
            "9c03f925be0429b9b70407018d59f1df801682a9e7a821a6bb9c6d3ef80fe317")
        self.assertEqual(
            VALID_CUTOFF_SHA,
            "f27ffa219efc763f3db170bfaa45ca45148dd64a3fab82b6a55e6dfc73b50b21")
        self.assertIn("SOURCE_PREFLIGHT_SHA,G31_ORIGINAL_POINT_SHA,ORIGINAL_P10",s)
        self.assertIn(
            "original_a3=evidence(a.g3_2_original_3arm_point_report,A3_PRIOR_POINT_SHA)",s)
        self.assertIn(
            "calibration=evidence(a.g3_2_valid_cutoff_report,VALID_CUTOFF_SHA)",s)
        self.assertIn(
            "preflight=evidence(a.g3_2_three_arm_source_preflight_report,",s)
        self.assertIn(
            "                       SOURCE_PREFLIGHT_SHA)",s)
        for text in ("verify_new_source(a.review_repo,commit)",
                     "verify_local_runner_code(a.review_repo,commit)",
                     "check_code(a.review_repo,commit)",
                     "make_release_checks(a)",
                     "recheck_all_historical_price_hashes(",
                     "validate_aggregate_checkpoints(",
                     "check_point_against_original(",
                     "verify_prior_point_rows("):
            self.assertIn(text,s)
    def test_original_price_and_target_hashes_before_deserialization(self):
        s=SRC.read_text()
        main=s[s.index("def main():"):]
        self.assertLess(main.index("_,original_inputs=make_release_checks(a)"),
                        main.index("import pandas as pd"))
        self.assertLess(main.index("price_files=recheck_all_historical_price_hashes("),
                        main.index("import pandas as pd"))
        self.assertLess(main.index("price_files=recheck_all_historical_price_hashes("),
                        main.index("pd.read_pickle("))
    def test_both_paired_cluster_schemes_are_required_and_same_original_rows(self):
        s=SRC.read_text()
        self.assertIn('scheme="news_id"',s)
        self.assertIn('scheme="ticker"',s)
        self.assertIn('arrays["news_id"]',s)
        self.assertIn('arrays["ticker"]',s)
        self.assertIn('risk=source_risk_admission_mask(',s)
        self.assertIn('"total_news_and_ticker_resamples":60000',s)
        self.assertIn('"all_CIs_withheld_per_cluster_scheme_if_any_K_infeasible":True',s)
    def test_no_recalibration_training_nor_prospective_claims(self):
        s=SRC.read_text()
        for forbidden in ("xgb.train(","booster.fit(","--retune-risk",
                          "--select-optimal-q","to_pickle(","np.save("):
            self.assertNotIn(forbidden,s)
        for expected in (
            '"familywise_multiple_comparisons_controlled":False',
            '"price_provider_vintage_verified":False',
            '"point_in_time_corporate_actions_verified":False',
            '"realized_tradable_account_pnl":False',
            '"no_new_independent_matured_60day_holdout":True',
            '"old_60day_outcomes_previously_consulted":True'
        ):
            self.assertIn(expected,s)

if __name__=="__main__":
    unittest.main()
