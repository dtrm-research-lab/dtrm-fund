"""G5.7b synthetic source-fixture tests plus frozen PUBLIC Phase-II reader.

Never accesses actual original market data or old labels.
"""
import ast
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"/"reviews"/"icomputing_2026"))
import ic_g5_7b_direct_writer_disambiguation as a
from ic_g5_7a_target_producer_source_scan import TARGET_FILES

class G57BSourceReaderWriter(unittest.TestCase):
    def test_known_original_phase2_consumer_not_producer(self):
        path=ROOT/"research"/"experiments"/"run_phase2_primary_bootstrap.py"
        source=path.read_text(encoding="utf-8")
        tree=ast.parse(source)
        self.assertTrue(all(name in source for name in TARGET_FILES.values()))
        calls=a._callname
        seen={calls(x) for x in ast.walk(tree) if isinstance(x,ast.Call)}
        self.assertIn("read_pickle",seen)
        self.assertIn("savez_compressed",seen)
        for filename in TARGET_FILES.values():
            self.assertEqual(a._direct_target_writer(tree,filename),[])

    def test_exact_to_pickle_producer_candidate_only(self):
        code="data.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')"
        tree=ast.parse(code)
        self.assertEqual(a._direct_target_writer(tree,TARGET_FILES["V2"]),
                         ["TO_PICKLE_EXACT_ARGUMENT"])
        self.assertFalse(a._direct_target_writer(tree,TARGET_FILES["V3"]))

    def test_pd_to_pickle_producer_candidate_only(self):
        tree=ast.parse("pd.to_pickle(frame,'probabilistic_v3_holdout_model_targets_2026-06-14.pkl')")
        self.assertEqual(a._direct_target_writer(tree,TARGET_FILES["V3"]),
                         ["TO_PICKLE_EXACT_ARGUMENT"])

    def test_unrelated_savez_does_not_count_as_pkl_writer(self):
        tree=ast.parse("np.savez_compressed('bootstrap-results.npz', x=1)\n"
                       "n='probabilistic_v1_holdout_model_targets_2026-06-06.pkl'")
        self.assertEqual(a._direct_target_writer(tree,TARGET_FILES["V4"]),[])

    def test_dynamic_writer_not_overclaimed(self):
        tree=ast.parse("filename = 'probabilistic_v2_holdout_model_targets_2026-06-10.pkl'\n"
                       "df.to_pickle(filename)")
        self.assertEqual(a._direct_target_writer(tree,TARGET_FILES["V2"]),[])

    def test_exact_open_write_or_path_write_counts_as_candidate(self):
        t=ast.parse("open('probabilistic_v2_holdout_model_targets_2026-06-10.pkl','wb')")
        self.assertIn("OPEN_EXACT_TARGET_WRITE_MODE",
                      a._direct_target_writer(t,TARGET_FILES["V2"]))
        t=ast.parse("Path('probabilistic_v2_holdout_model_targets_2026-06-10.pkl').write_bytes(x)")
        self.assertIn("PATH_WRITE_BYTES_EXACT_RECEIVER",
                      a._direct_target_writer(t,TARGET_FILES["V2"]))

    def _fake_archive(self,roots,mutate=False):
        refs={"V2":1,"V3":1,"V4":1}
        files=[]
        src=(ROOT/"research"/"experiments"/"run_phase2_primary_bootstrap.py").read_text()
        for i in range(12):
            if i==0:
                name="real_consumer.py";text=src;scope=2;ref=list(refs)
            else:
                name=f"generic_{i}.py";text="target_model.to_pickle(path)\n";scope=1;ref=[]
            fp=roots[scope-1]/name
            fp.write_text(text)
            files.append({
                "scope_id":scope,
                "relative_python_path":name,
                "python_source_sha256":hashlib.sha256(text.encode()).hexdigest(),
                "exact_target_filename_references":ref,
            })
        return {
          "schema_version":"dtrm.ic.g5_7a.source_only_target_producer_search.v0",
          "python_files_checked":38,
          "static_source_candidates":files,
          "exact_target_reference_counts":refs,
          "notebook_code_cells_scanned":False,
          "pickle_files_opened":False,
          "original_old_cohort_targets_read":False,
          "target_generation_execution_proven":False,
          "v2_v3_v4_label_transform_compatibility_proven":False,
          "old_outcome_access_permitted":False,
        }

    def test_all_12_rehashed_and_original_consumer_not_writer(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            roots=[p/"one",p/"two"]
            for r in roots:r.mkdir()
            manifest=self._fake_archive(roots)
            report=a.analyze_source_report(manifest,roots)
            self.assertEqual(report["original_source_files_rehashed"],12)
            self.assertEqual(report["status"],"G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE")
            rows=[z for z in report["verified_source_candidates"] if z["exact_target_filename_references"]]
            self.assertEqual(len(rows),1)
            self.assertTrue(rows[0]["same_module_nontarget_savez_present"])
            self.assertTrue(rows[0]["same_module_read_pickle_present"])
            self.assertFalse(rows[0]["is_direct_target_writer_candidate"])
            self.assertFalse(report["v2_v3_v4_label_transform_compatibility_proven"])

    def test_source_sha_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);roots=[p/"one",p/"two"]
            for x in roots:x.mkdir()
            manifest=self._fake_archive(roots)
            (roots[1]/"real_consumer.py").write_text("sneaky_source_change")
            with self.assertRaises(a.SourceLineageFailure):
                a.analyze_source_report(manifest,roots)

    def test_source_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);roots=[p/"one",p/"two"]
            for x in roots:x.mkdir()
            manifest=self._fake_archive(roots)
            manifest["static_source_candidates"][0]["relative_python_path"]="../secret.py"
            with self.assertRaises(a.SourceLineageFailure):
                a.analyze_source_report(manifest,roots)

    def test_manifest_misrepresents_no_outcome_gate_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);roots=[p/"one",p/"two"]
            for x in roots:x.mkdir()
            manifest=self._fake_archive(roots)
            manifest["original_old_cohort_targets_read"]=True
            with self.assertRaises(a.SourceLineageFailure):
                a.analyze_source_report(manifest,roots)

    def test_no_source_text_or_secrets_serialized(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);roots=[p/"one",p/"two"]
            for x in roots:x.mkdir()
            manifest=self._fake_archive(roots)
            (roots[0]/"generic_1.py").write_text("SECRET_API_KEY_DO_NOT_EXPORT\ntarget_model.to_pickle(path)")
            manifest["static_source_candidates"][1]["python_source_sha256"]=hashlib.sha256(
                (roots[0]/"generic_1.py").read_bytes()).hexdigest()
            import json
            res=a.analyze_source_report(manifest,roots)
            self.assertNotIn("SECRET_API_KEY",json.dumps(res))

if __name__=="__main__":
    unittest.main()
