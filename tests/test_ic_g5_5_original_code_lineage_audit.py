"""Actual frozen Git SOURCE code test, no private financial records opened."""
from __future__ import annotations
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/"research"/"reviews"/"icomputing_2026"))
import ic_g5_5_original_code_lineage_audit as g55


class OriginalFrozenSourceLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=g55.audit(REPO)

    def test_real_original_git_blob_hashes_all_lineage_matched(self):
        r=self.result
        self.assertEqual(r["frozen_original_commit"],g55.FROZEN)
        self.assertEqual(len(r["frozen_original_public_source_sha256"]),5)
        self.assertEqual(len(r["existing_review_source_sha256"]),5)
        for path, recorded in r["frozen_original_public_source_sha256"].items():
            blob=subprocess.run(["git","-C",str(REPO),"show",g55.FROZEN+":"+path],
                capture_output=True,check=True).stdout
            self.assertEqual(hashlib.sha256(blob).hexdigest(),recorded)

    def test_source_semantics_pass_without_any_original_market_data(self):
        self.assertTrue(all(self.result["semantic_checks"].values()))
        self.assertEqual(self.result["status"],g55.STATUS)
        self.assertEqual(len(self.result["semantic_checks"]),9)
        self.assertTrue(all(v is False for v in self.result["still_unverified"].values()))
        self.assertIn("NO_PRIVATE_MARKET_DATA",self.result["conclusion"])

    def test_unknown_original_commit_is_rejected(self):
        with self.assertRaises(g55.CodeLineageError):
            g55.audit(REPO,"0"*40)

    def test_missing_critical_transformation_is_rejected(self):
        paths={**self.result["frozen_original_public_source_sha256"],
               **self.result["existing_review_source_sha256"]}
        blobs={p:(REPO/p).read_bytes() for p in paths}
        original="src/dtrm/legacy_target_preprocessing.py"
        blobs[original]=blobs[original].replace(
            b'"ticker_means": ticker_means,',b'"removed_train_ticker_centers": ticker_means,')
        with self.assertRaises(g55.CodeLineageError):
            g55.source_semantics(blobs)

    def test_missing_continuous_p10_source_is_rejected(self):
        paths={**self.result["frozen_original_public_source_sha256"],
               **self.result["existing_review_source_sha256"]}
        blobs={p:(REPO/p).read_bytes() for p in paths}
        key="research/reviews/icomputing_2026/ic_g3_1_a2_a6_join_contract.py"
        blobs[key]=blobs[key].replace(b'"p10_calibrated"',b'"removed_p10_calibrated"')
        with self.assertRaises(g55.CodeLineageError):
            g55.source_semantics(blobs)


if __name__=="__main__":
    unittest.main()
