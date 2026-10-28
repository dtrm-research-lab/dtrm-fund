"""Static-only explicit-authorization controls for G3.1 A2/A6 runner.

Never calls runner main, loads actual labels or reads confidential sources.
"""
from pathlib import Path
import ast
import unittest
SCRIPT=Path(__file__).with_name("ic_g3_1_a2_a6_protected_runner.py")
def s():return SCRIPT.read_text(encoding="utf-8")

class ProtectedG31ReleaseTests(unittest.TestCase):
    def test_python_compiles(self):
        compile(s(),str(SCRIPT),"exec")
    def test_separate_human_authorization_and_acknowledgements(self):
        code=s()
        for token in ("--authorize-retrospective-a2-a6-old-outcome-access",
                      "--acknowledge-no-independent-60d-holdout",
                      "--acknowledge-no-realized-tradable-pnl",
                      "--trust-original-audited-pickles",
                      "if not (a.authorize_retrospective_a2_a6_old_outcome_access"):
            self.assertIn(token,code)
    def test_frozen_commit_binds_all_scientific_source_and_test_files(self):
        code=s()
        self.assertIn('git(repo,"show",commit+":"+FROZEN_PATH+name)',code)
        self.assertIn('must(actual==expected',code)
        for name in ("ic_g3_1_a2_a6_protected_runner.py",
                     "ic_g3_1_a2_a6_join_contract.py",
                     "ic_g3_1_a2_validation_only_source.py",
                     "ic_g3_1_a2_a6_pure_grid.py",
                     "ic_g2_g3_exploratory_core.py"):
            self.assertIn(name,code)
    def test_operator_historic_source_sha_is_bound(self):
        code=s()
        self.assertIn("3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8",code)
        self.assertIn("a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a",code)
        self.assertIn("source.get(\"g2_freeze_commit\")==G2_FREEZE",code)
        self.assertIn("source.get(\"g2_owner_freeze_approval_sha256\")==",code)
    def test_all_original_six_sources_rehashed_before_deserialization(self):
        code=s()
        self.assertIn('for cohort in COHORTS:',code)
        self.assertIn('for role in ("signals","targets"):',code)
        self.assertIn('sha(p)==rec["sha256_original_g2_5"]',code)
        self.assertLess(code.index('exact,bound=make_release_checks(a)'),
                        code.index('import pandas as pd'))
        self.assertLess(code.index('exact,bound=make_release_checks(a)'),
                        code.index('pd.read_pickle(bound'))
    def test_original_v4_uses_v1_target_file(self):
        self.assertIn("probabilistic_v1_holdout_model_targets_2026-06-06.pkl",s())
    def test_original_q25_reproduced_before_18_alternatives(self):
        code=s()
        self.assertIn("valid_raw,valid_news,valid_check=reconstruct_valid_p10_only(",code)
        self.assertIn("response=analyze_18_cells(",code)
        self.assertIn('must(response["cells_expected"]==18',code)
        self.assertIn("Original source q25 / K10 parity PASS:",code)
    def test_no_a3_no_account_pnl_and_no_new_holdout_claim(self):
        code=s()
        self.assertIn('"a3_price_volatility_experiment_authorized":False',code)
        self.assertIn('"no_independent_matured_new_60_day_holdout":True',code)
        self.assertIn('"all_old_outcomes_were_previously_consulted":True',code)
        self.assertIn("60_day_forward_excess_beta_NOT_REALIZED_TRADING_PNL",code)
    def test_modes_restrict_bootstrap_claim(self):
        code=s()
        self.assertIn('choices=("point","full")',code)
        self.assertIn('bootstrap=(a.mode=="full")',code)
        self.assertIn("POINT_ESTIMATES_ONLY_BOOTSTRAP_NOT_YET_RUN",code)
        self.assertIn("G3_1_A2_A6_FULL_18_CELL_POST_OUTCOME_EXPLORATORY",code)
    def test_original_inputs_not_committed_and_results_no_overwrite(self):
        code=s()
        self.assertIn('must(not dest.exists()',code)
        self.assertIn('with dest.open("x",encoding="utf-8")',code)
        self.assertNotIn('to_pickle(',code)
        self.assertNotIn('to_csv(',code)
        self.assertNotIn('np.save(',code)

if __name__=="__main__":
    unittest.main()
