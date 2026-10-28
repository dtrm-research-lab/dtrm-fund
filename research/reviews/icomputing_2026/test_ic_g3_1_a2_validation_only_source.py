"""Static-only protection for unexecuted original 19,880 V0 P10 feature replay."""
from pathlib import Path
import unittest,ast
SOURCE=Path(__file__).with_name("ic_g3_1_a2_validation_only_source.py")

class G31OriginalValidOnlySource(unittest.TestCase):
    def test_source_compiles(self):
        compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec")
    def test_no_standalone_cli_or_auto_run(self):
        s=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn('if __name__=="__main__"',s)
        self.assertNotIn("argparse.ArgumentParser",s)
        self.assertNotIn("read_pickle",s)
    def test_original_only_frozen_source_and_row_sha(self):
        s=SOURCE.read_text(encoding="utf-8")
        self.assertIn("c7502a690162459cdfb3413573e3133c42efb126",s)
        self.assertIn("3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724",s)
        self.assertIn('head!=PIN or dirty',s)
        self.assertIn('_sha(orig_rows)!=ROWS_SHA',s)
        self.assertIn("dossier.get(\"reconstructed_unapproved_model_sha256\",{}).get(\"p10.ubj\")",s)
    def test_valid_only_19880_and_390(self):
        s=SOURCE.read_text(encoding="utf-8")
        self.assertIn('rows["split"].eq("valid").to_numpy()',s)
        self.assertIn("int(mask.sum())!=19880",s)
        self.assertIn("features.shape==(len(rows),390)",s)
        self.assertIn("iteration_range=(0,19)",s)
        self.assertIn("original_validation_p10_thresholds(raw,news_ids)",s)
    def test_never_rebuild_original_forward_targets(self):
        s=SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "module.build_exante_raw_targets(",
            "module.load_exante_price_cache(",
            "module.prepare_training_data(",
            "module.train_quantile_models(",
            "module.train_legacy_model(",
            "signals.merge(",
            '["target_model"]',
            "to_pickle",
        ):self.assertNotIn(forbidden,s)
        self.assertIn('"heldout_financial_target_labels_loaded":False',s)

if __name__=="__main__":unittest.main()
