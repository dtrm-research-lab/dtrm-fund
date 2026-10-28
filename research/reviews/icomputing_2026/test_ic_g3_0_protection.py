"""Static-only protection tests for the PREPARED, never-yet-run G3.0 parity gate."""
import ast
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("ic_g3_0_original_model_row_parity.py")
def read():return SOURCE.read_text(encoding="utf-8")

class G30SourceProtection(unittest.TestCase):
    def test_compiles(self):
        compile(read(),str(SOURCE),"exec")
    def test_requires_human_science_and_freeze_manifest(self):
        s=read()
        self.assertIn("--g2-freeze-approval",s)
        self.assertIn('freeze.get("human_scientific_signoff") is True',s)
        self.assertIn('freeze.get("source_gate_report_sha256")==sha(gate_path)',s)
        self.assertIn('freeze.get("g3_1_old_outcome_access_authorized") is False',s)
    def test_does_not_reference_old_target_artifact_filenames(self):
        s=read()
        self.assertNotIn("_model_targets_",s)
        self.assertNotIn("price_cache_fmp_pickle",s)
        self.assertNotIn("target_model",s)
    def test_original_model_hashes_protected(self):
        s=read()
        self.assertIn("reconstructed_unapproved_model_sha256",s)
        self.assertIn("sha(file)==model_hashes.get(name)",s)
    def test_original_features_hash_bound_and_safe_numpy(self):
        s=read()
        self.assertIn('sha(f)==expected',s)
        self.assertIn("allow_pickle=False",s)
        self.assertIn("X.shape==(n,390)",s)
    def test_original_row_mask_and_ranker_numerics(self):
        s=read()
        self.assertIn('signals["p10_pass"]',s)
        self.assertIn('signals["baseline_prediction"]',s)
        self.assertIn('iteration_range=(0,11)',s)
        self.assertIn('iteration_range=(0,19)',s)
        self.assertIn("veto_bad=int(np.sum",s)
    def test_no_false_numeric_p10_parity_without_source_reference(self):
        s=read()
        self.assertIn("original_p10_numeric_reference_available",s)
        self.assertIn("BASELINE_NUMERIC_AND_P10_MASK_PARITY_PASS_P10_NUMERIC_REFERENCE_ABSENT",s)
        self.assertIn('status!="ROW_PARITY_PASS"',s)
    def test_original_boolean_mask_cannot_be_cast_from_string(self):
        s=read()
        self.assertIn('signals["p10_pass"].isin([True,False])',s)
        self.assertIn("original_mask_type_valid",s)
    def test_never_approves_g3_1(self):
        s=read()
        self.assertIn('"g3_1_financial_comparison_authorized":False',s)
        self.assertIn("No old forward-target/outcome values opened",s)

if __name__=="__main__":
    unittest.main()
