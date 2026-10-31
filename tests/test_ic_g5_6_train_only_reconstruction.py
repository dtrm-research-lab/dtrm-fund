"""G5.6 source and TRAIN-only numeric regression: synthetic fixtures ONLY.

No original training values, private news/price source, model fitting or heldout
outcome access in these tests. Source-code inspection for safety guarantees.
"""
from __future__ import annotations
import argparse
import ast
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from dtrm.legacy_target_preprocessing import preprocess_legacy_targets

SRC=Path(__file__).resolve().parents[1]/"research"/"reviews"/"icomputing_2026"
sys.path.insert(0,str(SRC))
import ic_g5_6_train_only_core as core
import ic_g5_6_train_only_protected_runner as runner
from ic_g5_5_private_source_metadata_gate import SourceGateError


class G56TrainOnlyTests(unittest.TestCase):
    def test_train_only_centers_replay_original_float32_kahan(self):
        targets=[-100., -2., 2., 10., 9., 20., -10., 1., 15., 3.]
        tickers=["A","A","B","B","A","B","C","C","A","B"]
        result=core.centers_from_train(ticker=tickers,raw_targets=targets)
        frozen=preprocess_legacy_targets(tickers,targets,[],[],[],[])
        self.assertEqual(result["train_rows"],10)
        self.assertEqual(result["train_tickers"],3)
        self.assertTrue(result["train_centered_float32_parity"])
        self.assertEqual(result["validation_or_test_labels_consumed"],False)
        self.assertEqual(result["v2_v3_v4_targets_consumed"],False)
        self.assertEqual(result["economic_returns_or_trading_pnl_inferred"],False)
        self.assertEqual(frozen["train"].dtype,np.float32)
        self.assertAlmostEqual(result["clip_lower"],frozen["clip_lower"],places=10)
        self.assertAlmostEqual(result["clip_upper"],frozen["clip_upper"],places=10)

    def test_float32_deterministic_digest(self):
        t=["X","Y","X","Y","X","Y","Z"]
        y=[0.,1.,2.,3.,4.,5.,6.]
        a=core.centers_from_train(ticker=t,raw_targets=y)
        b=core.centers_from_train(ticker=t,raw_targets=y)
        self.assertEqual(a,b)
        self.assertEqual(len(a["train_ticker_mean_float32_mapping_sha256"]),64)
        self.assertNotIn("ticker_means",a)

    def test_outcomes_are_not_exposed_in_aggregate(self):
        x=core.centers_from_train(ticker=["A","A","B","B"],raw_targets=[0.,1.,2.,3.])
        for k in ("raw_targets","ticker_means","selected_news_ids","date_dt","prices"):
            self.assertNotIn(k,x)

    def test_empty_train_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=[],raw_targets=[])

    def test_mismatch_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=["A","B"],raw_targets=[1.])

    def test_nonfinite_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=["A","B"],raw_targets=[1.,float("nan")])

    def test_inf_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=["A","B"],raw_targets=[1.,float("inf")])

    def test_blank_ticker_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=["","B"],raw_targets=[1.,2.])

    def test_degenerate_train_bounds_refused(self):
        with self.assertRaises(core.TrainOnlyError):
            core.centers_from_train(ticker=["A","B"],raw_targets=[1.,1.])

    def test_order_sensitivity_is_original_not_silently_sorted(self):
        vals=[2e8,1.0,-2e8,6.0,7.0,2.0]
        t=["X"]*6
        a=core.centers_from_train(ticker=t,raw_targets=vals)
        b=core.centers_from_train(ticker=list(reversed(t)),
                                  raw_targets=list(reversed(vals)))
        self.assertTrue(a["train_centered_float32_parity"])
        self.assertTrue(b["train_centered_float32_parity"])
        # Not asserting means differ: clipping may collapse extremes;
        # only confirms exact frozen Kahan in both original input orders.

    def test_source_metadata_gate_refuses_false_status(self):
        fake=argparse.Namespace()
        with tempfile.TemporaryDirectory(prefix="G56_FAKE_ONLY_") as tmp:
            root=Path(tmp)
            fake={"status":"FAKE_STAGE1_PASS",
                  "private_market_values_loaded":False,
                  "read_or_compute_train_ticker_means":False,
                  "original_v2_v3_v4_outcome_access_authorized":False}
            with self.assertRaises(runner.TrainReconstructionGate):
                runner.validate_stage1_metadata_report(fake,root,root,root)

    def test_old_outcome_reader_never_called_by_train_runner(self):
        source=(SRC/"ic_g5_6_train_only_protected_runner.py").read_text(encoding="utf-8")
        syntax=ast.parse(source)
        calls={n.func.attr for n in ast.walk(syntax) if isinstance(n,ast.Call)
               and isinstance(n.func,ast.Attribute)}
        self.assertNotIn("load_old_target",calls)
        self.assertNotIn("source_exact_join",calls)
        self.assertNotIn("evaluate_old_outcome_only_after_authorized_reader",calls)
        self.assertIn("read_pickle",calls)
        self.assertIn("audit_source_manifest",{
            n.func.id for n in ast.walk(syntax) if isinstance(n,ast.Call)
            and isinstance(n.func,ast.Name)})

    def test_refuses_missing_owner_approval_before_io(self):
        q=argparse.Namespace(authorize_train_only_numeric_reconstruction=False)
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.reconstruct_original_train_only(q)

    def test_refuses_untrusted_pickle_before_io(self):
        q=argparse.Namespace(authorize_train_only_numeric_reconstruction=True,
              trust_original_audited_pickles=False)
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.reconstruct_original_train_only(q)

    def test_requires_honest_price_vintage_acknowledgement(self):
        q=argparse.Namespace(authorize_train_only_numeric_reconstruction=True,
              trust_original_audited_pickles=True,
              acknowledge_price_vendor_vintage_unverified=False)
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.reconstruct_original_train_only(q)

    def test_requires_acknowledgement_original_row_source_unbound(self):
        q=argparse.Namespace(authorize_train_only_numeric_reconstruction=True,
              trust_original_audited_pickles=True,
              acknowledge_price_vendor_vintage_unverified=True,
              acknowledge_no_old_holdout_outcomes=True,
              acknowledge_original_full_row_provenance_unbound=False)
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.reconstruct_original_train_only(q)

    def test_unauthorized_old_outcome_access_rejected(self):
        q=argparse.Namespace(authorize_train_only_numeric_reconstruction=True,
              trust_original_audited_pickles=True,
              acknowledge_price_vendor_vintage_unverified=True,
              acknowledge_original_full_row_provenance_unbound=True,
              acknowledge_no_old_holdout_outcomes=False)
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.reconstruct_original_train_only(q)

    def test_tracked_code_commit_is_required(self):
        with self.assertRaises(runner.TrainReconstructionGate):
            runner.code_approval(SRC.parents[2],"not-a-valid-sha")

if __name__=="__main__":
    unittest.main()
