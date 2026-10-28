#!/usr/bin/env python3
"""Static-only G2.13 source regression tests; do not open original market files."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

SRC=Path(__file__).with_name("ic_g2_a3_original_validation_date_coverage.py")
def parse():
    return ast.parse(SRC.read_text(encoding="utf-8"),filename=str(SRC))

class G213ValidationDateCoverageRegression(unittest.TestCase):
    def test_script_compiles(self):
        compile(SRC.read_text(encoding="utf-8"),str(SRC),"exec")
    def test_original_validation_19880_fixed(self):
        src=SRC.read_text(encoding="utf-8")
        self.assertIn("N_VALID=19880",src)
        self.assertIn('rows["split"].eq("valid")',src)
        self.assertIn("len(fold)==N_VALID",src)
        self.assertIn('SOURCE_NAME="legacy_model_rows_2026-05-01.pkl"',src)
    def test_original_sha_pins_are_declared(self):
        tree=parse();d={}
        for node in tree.body:
            if isinstance(node,ast.Assign):
                for t in node.targets:
                    if isinstance(t,ast.Name) and isinstance(node.value,ast.Constant):
                        d[t.id]=node.value.value
        for name in ("G29_SHA","G210_SHA"):
            self.assertIn(name,d)
            self.assertEqual(len(d[name]),64)
            self.assertTrue(all(c in "0123456789abcdef" for c in d[name]))
        self.assertEqual(len(d["PIN"]),40)
    def test_only_date_bar_cut_used_no_close_or_outcome(self):
        tree=parse()
        denied={"close","forward_excess_beta","target","baseline_prediction",
                "p10_pass","p10_calibrated","beta_pre","returns","ret"}
        for node in ast.walk(tree):
            if isinstance(node,ast.Subscript) and isinstance(node.slice,ast.Constant):
                self.assertNotIn(node.slice.value,denied)
        src=SRC.read_text(encoding="utf-8")
        self.assertIn("bisect_left(arr,when)",src)
        self.assertIn("n>=61",src)
        self.assertIn("n>=41",src)
    def test_no_g3_or_provider_vintage_certification(self):
        src=SRC.read_text(encoding="utf-8")
        self.assertIn('"g3_authorized":False',src)
        self.assertIn('"vendor_asof_acquisition_time_verified":False',src)
        self.assertIn('"corporate_action_adjustments_verified":False',src)
        self.assertIn('"volatility_computed":False',src)
    def test_trusted_original_pickles_explicit_and_hash_before_load(self):
        src=SRC.read_text(encoding="utf-8")
        self.assertIn("--trust-original-pickles",src)
        self.assertIn('sha(path)==item.get("sha256_new_local_commitment")',src)
        self.assertIn("model_sha=sha(orig)",src)
        self.assertIn("if out.exists():",src)
    def test_partial_validation_is_explicit_not_falsely_full(self):
        src=SRC.read_text(encoding="utf-8")
        self.assertIn("G2_13_A3_V0_VALID_PRICE_DATE_COVERAGE_PARTIAL_COMMON_CASE_REQUIRED",src)
        self.assertIn("return 0 if has_full else 2",src)
        self.assertIn("original_v0_model_rows_current_sha256",src)
if __name__=="__main__":
    unittest.main()
