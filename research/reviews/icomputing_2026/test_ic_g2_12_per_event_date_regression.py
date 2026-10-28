#!/usr/bin/env python3
"""G2.12 static-only regression: no original private data loaded by tests."""
import ast
from pathlib import Path
import unittest

SCRIPT=Path(__file__).with_name("ic_g2_a3_per_event_bar_date_coverage.py")

def parse():
    return ast.parse(SCRIPT.read_text(encoding="utf-8"))

class G212SourceRegressions(unittest.TestCase):
    def test_source_compiles(self):
        compile(SCRIPT.read_text(encoding="utf-8"),str(SCRIPT),"exec")

    def test_sha_pin_names_are_literal_64_hex(self):
        literals={}
        for node in parse().body:
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if (isinstance(target,ast.Name) and
                        isinstance(node.value,ast.Constant) and
                        isinstance(node.value.value,str)):
                        literals[target.id]=node.value.value
        for name in ("PIN","BIND_SHA","G29_SHA","G210_SHA"):
            self.assertIn(name,literals)
        self.assertEqual(len(literals["PIN"]),40)
        for name in ("BIND_SHA","G29_SHA","G210_SHA"):
            with self.subTest(name=name):
                self.assertEqual(len(literals[name]),64)
                self.assertTrue(all(ch in "0123456789abcdef" for ch in literals[name]))

    def test_never_index_numeric_prediction_or_price_columns(self):
        forbidden={"close","baseline_prediction","p10_prediction",
                   "p10_calibrated","p10_pass","forward_excess_beta",
                   "raw_target","target","return","spy_return"}
        for node in ast.walk(parse()):
            if isinstance(node,ast.Subscript) and isinstance(node.slice,ast.Constant):
                self.assertNotIn(node.slice.value,forbidden)

    def test_g3_authorization_is_explicitly_false(self):
        src=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"g3_scoring_authorized":False',src)
        self.assertIn('"provider_acquisition_vintage_verified":False',src)
        self.assertIn('"corporate_action_adjustments_point_in_time_verified":False',src)
        self.assertIn('"original_validation_pair_date_coverage_checked":False',src)

    def test_trusted_pickles_and_no_overwrite(self):
        src=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("--trust-original-pickles",src)
        self.assertIn("if out.exists():",src)
        self.assertIn('sha(path) == expected',src)
        self.assertIn('sha(path) == exp_hash',src)

    def test_60_return_bar_dates_are_strictly_before_event_day(self):
        src=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("bisect_left(d,event_date)",src)
        self.assertIn("count>=61",src)
        self.assertIn("count>=41",src)
        self.assertIn("strictly before event UTC calendar date",src.lower())

    def test_original_v1_v4_pair_agreement_is_required(self):
        src=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('row_keys["V4_original_V1_signals"]',src)
        self.assertIn('row_keys["V4_original_V4_signals"]',src)
        self.assertIn("all_good=False",src)

if __name__=="__main__":
    unittest.main()
