"""G5.7c: synthetic original-notebook JSON fixtures, never actual market outputs."""
import json
import hashlib
import tempfile
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"/"reviews"/"icomputing_2026"))
import ic_g5_7c_notebook_code_source_scan as mod

def notebook(cells):
    return {"cells":cells,"metadata":{"kernelspec":{"name":"python3"}},
            "nbformat":4,"nbformat_minor":5}
def code(src,outputs=None):
    return {"cell_type":"code","metadata":{},"source":src,
            "outputs":outputs or [],"execution_count":None}
def markdown(src):
    return {"cell_type":"markdown","metadata":{},"source":[src]}

class NotebookStreamSourceOnly(unittest.TestCase):
    def make(self,root,cells):
        p=root/"original.ipynb"
        p.write_text(json.dumps(notebook(cells)),encoding="utf-8")
        return p

    def test_direct_exact_producer_is_lead_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.make(root,[code(["f.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')"])])
            result=mod.scan(root)
            self.assertEqual(result["status"],"G57C_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY")
            self.assertFalse(result["june_target_producer_execution_proven"])
            self.assertFalse(result["train_transform_compatibility_proven"])
            self.assertEqual(result["notebooks_scanned"],1)

    def test_dynamic_variable_writer_remains_unproven(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.make(root,[code(["outpath = 'cohort_' + str(2) + '.pkl'\n",
                                   "target_model.to_pickle(outpath)\n"])])
            report=mod.scan(root)
            self.assertEqual(report["status"],"G57C_NOTEBOOK_DYNAMIC_WRITER_LEADS_ONLY")
            self.assertEqual(report["notebooks"][0]["possible_dynamic_target_writer_cells"],1)

    def test_embedded_output_values_are_not_parsed_as_code(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            payload={"output_type":"execute_result",
                     "data":{"text/plain":["f.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')",
                                         "top-secret-financial-result"]},
                     "metadata":{"source":["target_model.to_pickle('other.pkl')"]},
                     "execution_count":123}
            self.make(root,[code("print('safe')\n",[payload])])
            result=mod.scan(root)
            self.assertEqual(result["status"],"G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS")
            self.assertEqual(result["notebooks"][0]["code_cells_scanned"],1)
            self.assertFalse(result["outputs_deserialized_or_saved"])
            self.assertNotIn("top-secret",json.dumps(result))

    def test_markdown_mentions_do_not_count(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.make(root,[markdown("target_model.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')")])
            result=mod.scan(root)
            self.assertEqual(result["status"],"G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS")

    def test_exact_reader_is_not_producer(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.make(root,[code("df = pd.read_pickle('probabilistic_v3_holdout_model_targets_2026-06-14.pkl')")])
            result=mod.scan(root)
            self.assertEqual(result["status"],"G57C_NOTEBOOK_TARGET_REFERENCES_ONLY")
            self.assertEqual(result["notebooks"][0]["direct_exact_target_write_code_cell_counts"]["V3"],0)

    def test_source_string_and_list_forms(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.make(root,[code("a=1\n"),code(["b=2\n","c=3\n"])])
            result=mod.scan(root)
            self.assertEqual(result["notebooks"][0]["code_cells_scanned"],2)

    def test_malformed_notebook_and_no_cells_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"invalid.ipynb"
            p.write_text('{"cells":[{"cell_type":"code","source":["incomplete"}}',encoding="utf-8")
            with self.assertRaises(mod.NotebookGateError):mod.scan(root)
            p.write_text('{"notcells":[]}',encoding="utf-8")
            with self.assertRaises(mod.NotebookGateError):mod.scan(root)

    def test_symlink_root_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"source";p.mkdir()
            q=root/"link";q.symlink_to(p,target_is_directory=True)
            with self.assertRaises(mod.NotebookGateError):mod.scan(q)

    def test_symlink_file_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/"real.txt"
            src.write_text(json.dumps(notebook([code("target_model.to_pickle(filename)")]))
                           ,encoding="utf-8")
            (root/"symlink.ipynb").symlink_to(src)
            report=mod.scan(root)
            self.assertEqual(report["notebooks_scanned"],0)

    def test_oversize_is_skipped_and_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=self.make(root,[code("a=1")])
            original=mod.MAX_BYTES_PER_NOTEBOOK
            try:
                mod.MAX_BYTES_PER_NOTEBOOK=10
                report=mod.scan(root)
                self.assertEqual(report["oversize_skipped"],1)
                self.assertEqual(report["notebooks_scanned"],0)
            finally:mod.MAX_BYTES_PER_NOTEBOOK=original

if __name__=="__main__":
    unittest.main()
