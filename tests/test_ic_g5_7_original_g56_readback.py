"""Synthetic metadata-only fixtures; no original private G5.6 JSON or results."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/"research"/"reviews"/"icomputing_2026"))
import ic_g5_6_original_report_readback as m

def fake():
    return {
        "schema_version":"dtrm.ic.g5_6.original_train_only_centers.v0",
        "status":"TRAIN_CENTERS_NUMERIC_PARITY_ONLY",
        "original_source_commit":m.ORIGINAL_FROZEN_SCIENCE,
        "approved_protected_runner_commit":m.ORIGINAL_OPERATOR_COMMIT,
        "g55_original_local_source_metadata_sha256":m.ORIGINAL_STAGE1_SHA,
        "original_historical_model_rows_sha256":"3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724",
        "original_full_rows_current_sha256":"b"*64,
        "original_full_rows_historical_sha_bound":False,
        "original_174_price_files_sha_checked":174,
        "original_cohort_files_hashed_not_opened":6,
        "train_rows":75828,"train_tickers":171,
        "clip_lower":-1.0,"clip_upper":1.0,
        "train_ticker_mean_float32_mapping_sha256":"a"*64,
        "original_train_centered_bytes_sha256":"c"*64,
        "train_centered_float32_parity":True,
        "original_heldout_v2_v3_v4_target_labels_accessed":False,
        "validation_or_test_targets_reconstructed":False,
        "validation_or_test_labels_consumed":False,
        "v2_v3_v4_targets_consumed":False,
        "original_price_provider_vintage_verified":False,
        "original_adjustment_point_in_time_verified":False,
        "economic_returns_or_trading_pnl_inferred":False,
        "historical_three_arm_or_policy_attribution_run":False,
        "no_real_trading_pnl":True,
        "scientific_use":"TRAIN_SOURCE_PARITY_ONLY_NOT_YET_INDEPENDENT_HOLDOUT_PROOF",
    }


class G56EvidenceReadbackTests(unittest.TestCase):
    def test_original_owner_report_status_collision_is_explicit(self):
        z=m.interpret(fake(),"f"*64)
        self.assertEqual(z["status"],m.PUBLIC_READBACK_STATUS)
        self.assertEqual(z["original_owner_g56_observed_status"],m.V0_LEGACY_CORE_STATUS)
        self.assertTrue(z["legacy_status_field_collision_present"])
        self.assertFalse(z["original_holdout_target_transform_compatibility_proven"])
        self.assertFalse(z["original_full_row_archival_identity_proven"])
        self.assertFalse(z["old_outcome_access_authorized_by_readback"])

    def test_fixed_source_science_and_original_owner_commit(self):
        z=m.interpret(fake(),"f"*64)
        self.assertEqual(z["original_owner_code_commit"],m.ORIGINAL_OPERATOR_COMMIT)
        self.assertEqual(z["original_science_commit"],m.ORIGINAL_FROZEN_SCIENCE)

    def test_protected_status_fix_preserves_internal_value(self):
        x=fake()
        x["status"]=m.PROTECTED_G56_STATUS
        x["numeric_core_status"]=m.V0_LEGACY_CORE_STATUS
        z=m.interpret(x,"f"*64)
        self.assertFalse(z["legacy_status_field_collision_present"])

    def test_false_authorization_rejected(self):
        x=fake();x["original_heldout_v2_v3_v4_target_labels_accessed"]=True
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_false_historical_provenance_rejected(self):
        x=fake();x["original_full_rows_historical_sha_bound"]=True
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_false_market_vintage_rejected(self):
        x=fake();x["original_price_provider_vintage_verified"]=True
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_wrong_train_n_rejected(self):
        x=fake();x["train_rows"]=75827
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_wrong_legacy_core_status_rejected(self):
        x=fake();x["numeric_core_status"]=m.V0_LEGACY_CORE_STATUS
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_missing_center_hash_rejected(self):
        x=fake();x.pop("train_ticker_mean_float32_mapping_sha256")
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_bad_clip_order_rejected(self):
        x=fake();x["clip_lower"]=3.0
        with self.assertRaises(m.ReportReadbackError):m.interpret(x)

    def test_sha_bound_fake_fixture_readback(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"fake_g56.json"
            p.write_text(json.dumps(fake()),encoding="utf-8")
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(m.file_readback(p,digest)["train_rows"],75828)
            with self.assertRaises(m.ReportReadbackError):m.file_readback(p,"e"*64)

    def test_previous_protected_status_merge_bug_corrected_in_source(self):
        import ast
        f=(P/"research"/"reviews"/"icomputing_2026"/
            "ic_g5_6_train_only_protected_runner.py").read_text(encoding="utf-8")
        tree=ast.parse(f)
        node=next(x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef)
                  and x.name=="reconstruct_original_train_only")
        result=next(x.value for x in ast.walk(node) if isinstance(x,ast.Return)
                    and isinstance(x.value,ast.Dict))
        key_positions=[i for i,k in enumerate(result.keys)
                       if isinstance(k,ast.Constant) and k.value=="status"]
        starred=[i for i,k in enumerate(result.keys) if k is None]
        self.assertTrue(starred)
        self.assertTrue(key_positions)
        self.assertGreater(key_positions[-1],starred[-1])

if __name__=="__main__":
    unittest.main()
