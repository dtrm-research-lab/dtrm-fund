"""Fake bytes only; no original private market Pickles are accessed in CI."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research"/"reviews"/"icomputing_2026"))
import ic_g5_5_private_source_metadata_gate as gate


def fake_sources(root:Path):
    files={}
    for cohort,n in gate.EXPECTED.items():
        files[cohort]={"expected_rows":n,"files":{}}
        for role in ("signals","targets"):
            name=f"FAKE_{cohort}_{role}.pkl"
            blob=("NOT_A_PICKLE:"+name).encode()
            (root/name).write_bytes(blob)
            files[cohort]["files"][role]={
                "basename":name,
                "sha256_original_g2_5":hashlib.sha256(blob).hexdigest(),
                "size_bytes":len(blob),
                "source_metadata_status":"ORIGINAL_G2_5_MANIFEST_SHA_PASS"
            }
    return {"status":"G3_1_A2_A6_ORIGINAL_SOURCE_HASHES_READY_OUTCOMES_STILL_BLOCKED",
            "original_expected_total_pairs":47596,
            "g3_1_outcome_access_authorized":False,
            "old_financial_targets_deserialized":False,
            "cohorts":files}


class OriginalPrivateSourceMetadataFakeTests(unittest.TestCase):
    def test_six_original_sources_sha_and_metadata_only(self):
        with tempfile.TemporaryDirectory(prefix="G55_FAKE_BYTES_NOT_MARKET_") as d:
            src=Path(d)
            result=gate.audit_source_manifest(fake_sources(src),src)
            self.assertEqual(set(result),set(gate.EXPECTED))
            self.assertEqual(sum(len(x) for x in result.values()),6)
            self.assertTrue(all(v["lineage"]=="EXACT_G2_5_SHA_PASS"
                for cohort in result.values() for v in cohort.values()))

    def test_replaced_source_bytes_fail(self):
        with tempfile.TemporaryDirectory(prefix="G55_FAKE_BYTES_NOT_MARKET_") as d:
            src=Path(d)
            m=fake_sources(src)
            (src/"FAKE_V3_targets.pkl").write_bytes(b"CHANGED")
            with self.assertRaises(gate.SourceGateError):
                gate.audit_source_manifest(m,src)

    def test_unapproved_old_outcome_manifest_refused(self):
        with tempfile.TemporaryDirectory(prefix="G55_FAKE_BYTES_NOT_MARKET_") as d:
            src=Path(d)
            m=fake_sources(src)
            m["g3_1_outcome_access_authorized"]=True
            with self.assertRaises(gate.SourceGateError):
                gate.audit_source_manifest(m,src)

    def test_manifest_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="G55_FAKE_BYTES_NOT_MARKET_") as d:
            src=Path(d)
            m=fake_sources(src)
            m["cohorts"]["V2"]["files"]["signals"]["basename"]="../outsider.pkl"
            with self.assertRaises(gate.SourceGateError):
                gate.audit_source_manifest(m,src)

    def test_missing_training_sources_rejected_without_opening_data(self):
        with tempfile.TemporaryDirectory(prefix="G55_FAKE_BYTES_NOT_MARKET_") as d:
            root=Path(d)
            outs=root/"out";outs.mkdir()
            pc=root/"prices";pc.mkdir()
            with self.assertRaises(gate.SourceGateError):
                gate.inspect_training_metadata(root,outs,pc)

    def test_original_frozen_source_identifiers_are_fixed(self):
        self.assertEqual(gate.ORIGINAL_ROWS_SHA,"3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724")
        self.assertEqual(gate.ORIGINAL_G31_SOURCE_REPORT_SHA,
            "3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8")
        self.assertEqual(sum(gate.EXPECTED.values()),47596)


if __name__=="__main__":
    unittest.main()
