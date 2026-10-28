"""G2.17 freeze-builder static source tests; never performs a signoff."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("ic_g2_17_operator_freeze.py")

class G217FreezeBuilderProtection(unittest.TestCase):
    def test_source_compiles(self):
        compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec")
    def test_operator_approval_is_explicit_and_triple_guarded(self):
        s=SOURCE.read_text(encoding="utf-8")
        for token in (
           "--approve-g3-0-source-parity-only",
           "--acknowledge-retrospective-data-vintage-risk",
           "--acknowledge-no-independent-60day-holdout",
           "if not (a.approve_g3_0_source_parity_only"
        ):self.assertIn(token,s)
    def test_frozen_git_code_and_builder_are_bound_to_pass(self):
        s=SOURCE.read_text(encoding="utf-8")
        for token in (
            'git(repo,"show",commit+":"+ROOT+base)',
            'digest(contents["freezer"])==sha(Path(__file__).resolve())',
            "result.get(resultkey)",
            "result.get(\"tests_run\",0)>=36"
        ):self.assertIn(token,s)
    def test_legacy_full_reviewer_gate_and_22_items(self):
        s=SOURCE.read_text(encoding="utf-8")
        self.assertIn("ic_g2_freeze_preflight.verify(matrix,protocol)",s)
        self.assertIn("LOCKED_IDS",s)
        self.assertIn("len({str(out),str(mout),str(gout)})==3",s)
    def test_never_authorizes_g3_1_old_outcomes(self):
        s=SOURCE.read_text(encoding="utf-8")
        for token in (
            '"g3_1_old_outcome_access_authorized":False',
            'matrix["g3_1_historic_financial_target_access_authorized"]=False',
            '"no_model_training_or_scoring_performed":True',
            'with path.open("xb") as fp'
        ):self.assertIn(token,s)
if __name__=="__main__":
    unittest.main()
