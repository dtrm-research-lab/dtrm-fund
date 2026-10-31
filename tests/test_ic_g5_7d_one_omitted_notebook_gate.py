"""G5.7d: 1 omitted notebook synthetic-only, provenance caps and privacy."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"research"/"reviews"/"icomputing_2026"))
import ic_g5_7d_one_omitted_notebook_gate as d

def nb(code,large=False):
    outputs=[{"output_type":"stream","name":"stdout",
              "text":["NO_PUBLIC_FINANCIAL_VALUES"+"z"*500]}] if large else []
    return {"cells":[{"cell_type":"code","source":[code],
                      "execution_count":1,"metadata":{},"outputs":outputs}],
            "nbformat":4,"nbformat_minor":5,"metadata":{}}

class OneOmittedNotebookTests(unittest.TestCase):
    def fixtures(self,root,writer=False):
        records=[]
        for i in range(14):
            p=root/f"safe{i}.ipynb"
            p.write_text(json.dumps(nb("a=1\n")),encoding="utf-8")
            records.append({"relative_notebook_path":p.name,
                            "notebook_sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
        omitted=root/"excluded.ipynb"
        source=("result.to_pickle('probabilistic_v2_holdout_model_targets_2026-06-10.pkl')"
                 if writer else "print('source is not an original writer')\n")
        omitted.write_text(json.dumps(nb(source,True)),encoding="utf-8")
        report={"schema_version":"dtrm.ic.g5_7c.notebook_code_streaming_source.v0",
                "status":"G57C_NO_TARGET_PRODUCER_CODE_FOUND_IN_BOUNDED_NOTEBOOKS",
                "notebooks_enumerated":15,"notebooks_scanned":14,"oversize_skipped":1,
                "notebook_execution":False,
                "outputs_deserialized_or_saved":False,
                "financial_pickle_or_csv_opened":False,
                "train_transform_compatibility_proven":False,
                "old_v2_v3_v4_target_outcome_access_authorized":False,
                "notebooks":records}
        return report,omitted

    def test_metadata_one_skip_is_pinned_without_code_read(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp)
            source,omitted=self.fixtures(root)
            result=d.metadata_only(source,root)
            self.assertEqual(result["original_14_scanned_notebooks_sha_verified"],14)
            self.assertEqual(result["one_omitted_relative_path"],omitted.name)
            self.assertEqual(result["one_omitted_current_sha256"],
                             hashlib.sha256(omitted.read_bytes()).hexdigest())
            self.assertFalse(result["omitted_notebook_code_inspected"])
            self.assertFalse(result["original_target_producer_executed_proven"])

    def test_one_excluded_code_lead_is_unexecuted_even_when_exact(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp)
            source,_=self.fixtures(root,True)
            meta=d.metadata_only(source,root)
            result=d.code_only(meta,source,root)
            self.assertEqual(result["status"],"G57D_OMITTED_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY")
            self.assertTrue(result["omitted_notebook_code_inspected"])
            self.assertFalse(result["original_target_producer_executed_proven"])
            self.assertFalse(result["original_v0_train_transform_compatible_with_june_targets_proven"])
            self.assertFalse(result["notebook_outputs_decoded"])

    def test_one_excluded_no_writer_finite_stop(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,_=self.fixtures(root)
            meta=d.metadata_only(source,root)
            result=d.code_only(meta,source,root)
            self.assertEqual(result["status"],"G57D_NO_TARGET_WRITER_IDENTIFIED_IN_LAST_BOUNDED_NOTEBOOK")

    def test_sha_drift_in_first_14_refused(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,_=self.fixtures(root)
            (root/"safe8.ipynb").write_text("MODIFIED")
            with self.assertRaises(d.OmittedNotebookError):d.metadata_only(source,root)

    def test_skipped_file_source_changed_refused_after_metadata(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,omitted=self.fixtures(root)
            meta=d.metadata_only(source,root)
            omitted.write_text(omitted.read_text()+" ",encoding="utf-8")
            with self.assertRaises(d.OmittedNotebookError):d.code_only(meta,source,root)

    def test_missing_one_omitted_refused(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,omitted=self.fixtures(root)
            omitted.unlink()
            with self.assertRaises(d.OmittedNotebookError):d.metadata_only(source,root)

    def test_hard_ceiling_ends_source_search_with_no_parsing(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,omitted=self.fixtures(root)
            with mock.patch.object(d,"MAX_ONE_NOTEBOOK_BYTES",400):
                meta=d.metadata_only(source,root)
                self.assertEqual(meta["status"],"G57D_ONE_OMITTED_NOTEBOOK_TOO_LARGE_FINITE_SOURCE_STOP")
                with self.assertRaises(d.OmittedNotebookError):d.code_only(meta,source,root)

    def test_symlink_notebook_does_not_enter_original_scope(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(d,"MAX_BYTES_PER_NOTEBOOK",250):
            root=Path(temp);source,_=self.fixtures(root)
            (root/"link.ipynb").symlink_to(root/"safe0.ipynb")
            self.assertEqual(d.metadata_only(source,root)["original_notebook_scope_count"],15)

    def test_original_g57c_evidence_gate_prevents_bad_status(self):
        original={"status":"G57C_NOTEBOOK_EXACT_WRITER_CANDIDATE_ONLY"}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"dummy.json";path.write_text(json.dumps(original))
            with self.assertRaises(d.OmittedNotebookError):d.load_original(path)

if __name__=="__main__":
    unittest.main()
