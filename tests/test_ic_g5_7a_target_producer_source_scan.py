"""G5.7a no-data source scanner fixture tests: never open market files."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/
    "research"/"reviews"/"icomputing_2026"))
import ic_g5_7a_target_producer_source_scan as scan


class TargetProducerStaticReadTests(unittest.TestCase):
    def test_exact_archive_name_with_writer_is_candidate_not_proof(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"original_producer.py").write_text(
                "frame.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')\n"
                "x = preprocess_legacy_targets(x,x,x,x,x,x)\n")
            x=scan.scan([p])
            self.assertEqual(x["status"],"G57A_SOURCE_WRITER_CANDIDATE_ONLY_PROVENANCE_OPEN")
            self.assertTrue(x["static_source_candidates"][0]["same_module_train_preprocess_reference"])
            self.assertFalse(x["target_generation_execution_proven"])
            self.assertFalse(x["v2_v3_v4_label_transform_compatibility_proven"])

    def test_reference_only_not_producer(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"study.py").write_text(
                "input='probabilistic_v3_holdout_model_targets_2026-06-14.pkl'\n"
                "target_model = None\n")
            x=scan.scan([p])
            self.assertEqual(x["status"],"G57A_TARGET_REFERENCES_ONLY_NO_PRODUCER_PROOF")
            self.assertEqual(x["exact_target_reference_counts"]["V3"],1)

    def test_no_exact_name_generic_writer_is_not_proven(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"generic.py").write_text("target_model.to_pickle(output_path)\n")
            x=scan.scan([p])
            self.assertEqual(x["status"],"G57A_NO_EXACT_TARGET_SOURCE_IN_BOUNDED_PY_SCOPE")
            self.assertEqual(x["exact_target_reference_counts"]["V4"],0)
            self.assertTrue(x["static_source_candidates"][0]["generic_target_writer_candidate_only"])

    def test_faked_private_pickles_not_opened(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"probabilistic_v1_holdout_model_targets_2026-06-06.pkl").write_bytes(
                b"SECRET_DO_NOT_READ")
            (p/"news.csv").write_text("SECRET_DO_NOT_READ")
            (p/"study.ipynb").write_text("not valid json and contains SECRET_DO_NOT_READ")
            x=scan.scan([p])
            self.assertEqual(x["python_files_checked"],0)
            self.assertEqual(x["static_source_candidates"],[])
            self.assertFalse(x["pickle_files_opened"])
            self.assertFalse(x["notebook_code_cells_scanned"])

    def test_symlink_subtree_not_traversed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"real").mkdir()
            (p/"real"/"a.py").write_text("target_model.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')")
            (p/"link").symlink_to(p/"real",target_is_directory=True)
            x=scan.scan([p])
            self.assertEqual(x["python_files_checked"],1)

    def test_source_secrets_are_never_persisted_as_content(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"foo.py").write_text(
                "secret='SECRET_TOKEN_THAT_MUST_NOT_APPEAR'\n"
                "foo='probabilistic_v1_holdout_model_targets_2026-06-06.pkl'\n")
            x=scan.scan([p])
            self.assertNotIn("SECRET_TOKEN",json.dumps(x))
            self.assertNotIn(str(p.resolve()),json.dumps(x))
            self.assertFalse(x["target_generation_execution_proven"])

    def test_unsafe_root_and_unbounded_number_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"link").symlink_to(p,target_is_directory=True)
            with self.assertRaises(scan.SourceScanError):
                scan.scan([p/"link"])
            with self.assertRaises(scan.SourceScanError):
                scan.scan([p]*5)

    def test_report_prohibits_historic_outcome_claim(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"v2.py").write_text(
                "frame.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')")
            x=scan.scan([p])
            self.assertFalse(x["original_old_cohort_targets_read"])
            self.assertFalse(x["identical_v0_training_clip_and_ticker_means_proven"])
            self.assertFalse(x["old_outcome_access_permitted"])

if __name__=="__main__":
    unittest.main()
