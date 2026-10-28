"""Synthetic TEST DOUBLE for G4.9c interactive trial. NO PEOPLE IN CI."""
from __future__ import annotations
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE=Path(__file__).resolve().parents[1]/"research"/"reviews"/"icomputing_2026"/"g49c"
sys.path.insert(0,str(HERE))
import g49c_participant as p  # noqa
import g49c_readback as a  # noqa
import g49c_world as w  # noqa
import g49c_agent as m  # noqa


class MockTTY(io.StringIO):
    def isatty(self): return True


class HumanPilotMockOnlyTests(unittest.TestCase):
    def test_no_sessions_reports_zero(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            self.assertEqual(a.aggregate(Path(d),b"x"*32),
                             {"status":"NO_CONSENTED_SESSIONS","sessions":0,"observed_rows":0})

    def test_12_decisions_consent_private_record_audit_and_withdraw(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            folder=Path(d)/"study_private"
            p.initialize(folder)
            key=p._key(folder)
            sid="f"*32
            train, evals=w.make_worlds()
            model=m.fit(w.training_rows(train))
            assignment=p.order_for(sid,key,[x.public for x in evals])
            case_map={x.public["id"]:x.public for x in evals}
            inputs=["YES","YES"]
            for item in assignment:
                if item["arm"]=="B_APPROVAL_REAL":
                    inputs.append("A")
                else:
                    inputs.append("CAUTIOUS")
            mockout=MockTTY()
            with (mock.patch.object(sys,"stdin",MockTTY()),
                  mock.patch.object(sys,"stdout",mockout),
                  mock.patch("builtins.input",side_effect=inputs),
                  mock.patch.object(p.secrets,"token_hex",
                      side_effect=[sid]+[f"{i+1:032x}" for i in range(12)])):
                self.assertEqual(p.enroll(folder),sid)
            saved=folder/(sid+".json")
            self.assertTrue(saved.is_file())
            self.assertEqual(saved.stat().st_mode & 0o077,0)
            self.assertIn("12/12",mockout.getvalue())
            self.assertNotIn("realized_quality",mockout.getvalue())
            self.assertEqual(len(json.loads(saved.read_text())["record"]["rows"]),12)
            read=a.audit_one(saved,key)
            self.assertEqual(read["session_rows"],12)
            report=a.aggregate(folder,key)
            self.assertEqual(report["sessions"],1)
            self.assertEqual(report["observed_rows"],12)
            self.assertEqual(report["by_arm"]["B_APPROVAL_REAL"]["task_count"],6)
            self.assertEqual(report["by_arm"]["C_DIRECT_REAL"]["task_count"],6)
            self.assertEqual(report["statistical_noninferiority"],"NOT_TESTED")
            self.assertEqual(report["real_welfare_or_trading_outcomes"],"NOT_MEASURED")
            self.assertNotIn("session_id",str(report))
            saved.unlink()
            self.assertEqual(a.aggregate(folder,key)["sessions"],0)

    def test_declining_consent_records_no_session(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            folder=Path(d)
            with (mock.patch.object(sys,"stdin",MockTTY()),
                  mock.patch.object(sys,"stdout",MockTTY()),
                  mock.patch("builtins.input",return_value="NO")):
                self.assertIsNone(p.enroll(folder))
            self.assertEqual(list(folder.glob("*.json")),[])

    def test_declining_age_eligibility_records_no_session(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            folder=Path(d)
            with (mock.patch.object(sys,"stdin",MockTTY()),
                  mock.patch.object(sys,"stdout",MockTTY()),
                  mock.patch("builtins.input",side_effect=["YES","NO"])):
                self.assertIsNone(p.enroll(folder))
            self.assertEqual(list(folder.glob("*.json")),[])

    def test_non_tty_cannot_start_real_enrollment(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            with mock.patch.object(sys.stdin,"isatty",return_value=False):
                with self.assertRaises(RuntimeError):
                    p.enroll(Path(d))

    def test_authorization_mismatch_detected_even_with_outer_recomputed_key(self):
        with tempfile.TemporaryDirectory(prefix="G49C_MOCK_NOT_HUMAN_") as d:
            folder=Path(d)
            p.initialize(folder)
            key=p._key(folder)
            sid="f"*32
            train,evals=w.make_worlds()
            order=p.order_for(sid,key,[x.public for x in evals])
            model=m.fit(w.training_rows(train))
            case=next(x.public for x in evals if x.public["id"]==order[0]["id"])
            from g49b_core import issue_event
            arm=order[0]["arm"]
            proposed=model.choose(case)
            decision="ACCEPT" if arm=="B_APPROVAL_REAL" else "CHOOSE"
            token=issue_event(sid,case["id"],arm,decision,proposed,"q"*32,key,100)
            # MAC belongs to the original policy; changing just the payload must fail.
            token["payload"]["policy"]="open" if proposed!="open" else "cautious"
            from g49b_core import verify_event
            from g49b_core import IntegrityFailure
            with self.assertRaises(IntegrityFailure):
                verify_event(token,key,sid,case["id"],arm,100,set())

    def test_order_has_both_arms_and_only_heldout(self):
        _,evals=w.make_worlds()
        ordered=p.order_for("f"*32,b"x"*32,[x.public for x in evals])
        self.assertEqual(len(ordered),12)
        self.assertEqual(sum(x["arm"]=="B_APPROVAL_REAL" for x in ordered),6)
        self.assertEqual(sum(x["arm"]=="C_DIRECT_REAL" for x in ordered),6)
        self.assertTrue(all(x["id"].startswith("EVAL_") for x in ordered))
        self.assertEqual(len(set(x["id"] for x in ordered)),12)


if __name__=="__main__":
    unittest.main()
