#!/usr/bin/env python3
"""G3.1 A2/A6 static-only original target SHA gate regression.

These tests must never execute the gate main function, inspect saved
financial targets or deserialize Pickles.
"""
import ast
from pathlib import Path
import unittest
SCRIPT=Path(__file__).with_name("ic_g3_1_a2_a6_source_gate.py")

class G31SourceOnlyProtections(unittest.TestCase):
    def test_source_compiles(self):
        compile(SCRIPT.read_text(encoding="utf-8"),str(SCRIPT),"exec")
    def test_no_pickle_or_numpy_target_loading(self):
        src=SCRIPT.read_text(encoding="utf-8")
        for token in ("pd.read_pickle","pickle.load","np.load(","read_csv(",
                      '["target_model"]',"xgb.Booster","xgb.train"):
            self.assertNotIn(token,src)
        self.assertIn('"old_financial_targets_deserialized":False',src)
        self.assertIn('"g3_1_outcome_access_authorized":False',src)
    def test_exact_original_phaseii_target_names(self):
        tree=ast.parse(SCRIPT.read_text(encoding="utf-8"))
        literals=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant)
                  and isinstance(n.value,str)]
        for name in (
          "probabilistic_v2_holdout_model_targets_2026-06-10.pkl",
          "probabilistic_v3_holdout_model_targets_2026-06-14.pkl",
          "probabilistic_v1_holdout_model_targets_2026-06-06.pkl",
          "probabilistic_v4_holdout_signals_2026-06-06.pkl"):
            self.assertIn(name,literals)
    def test_frozen_g3_parity_sha_and_freeze_approval(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("a5bb3f6a3a4e2862a9898eea812a87a01b4b6e12191f4ffad9c03c50af61684a",s)
        self.assertIn('freeze.get("g3_1_old_outcome_access_authorized") is False',s)
        self.assertIn('parity.get("g2_freeze_approval_sha256")==sha(report_paths["g2_freeze_approval"])',s)
        self.assertIn("G3_0_V2_V3_ORIGINAL_ROW_PARITY_PASS_G3_1_STILL_BLOCKED",s)
    def test_all_original_inputs_sha_and_size_guarded(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('v.get("root_ordinal")==1',s)
        self.assertIn('sha(path)!=supplied',s)
        self.assertIn('entry.get("size_bytes")!=actual_size',s)
        self.assertIn('g26.get(config["signals_g26_key"])!=supplied',s)
    def test_explicit_original_key_date_join_policy(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("exact news_id+ticker one-to-one and exact date_dt",s)
        self.assertIn("G3_1_A2_A6_SOURCE_SHA_OR_LINEAGE_GAPS_OUTCOMES_STILL_BLOCKED",s)
    def test_non_overwrite_and_no_auto_authorization(self):
        s=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('if dest.exists()',s)
        self.assertIn('"g3_1_execution_authorized":False',s)
        self.assertIn('"models_or_embeddings_executed":False',s)

if __name__=="__main__":
    unittest.main()
