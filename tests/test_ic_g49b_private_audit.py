"""Mock-only verification of private aggregation. THESE ARE NOT REAL PARTICIPANTS."""
from __future__ import annotations
import hashlib
import hmac
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1] / "research" / "reviews" / "icomputing_2026" / "g49b"
sys.path.insert(0,str(ROOT))
import g49b_core as c  # noqa
import g49b_audit as a  # noqa

KEY=b"j"*32
SID="c"*32


def fake_ci_session(directory:Path) -> Path:
    cases=c.load_stimuli()
    order=c.assignment(SID,KEY,cases)
    by_id={x["id"]:x for x in cases}
    rows=[]
    for ix,x in enumerate(order):
        case=by_id[x["case_id"]]
        arm=x["arm"]
        # Fixed QA fixture. No person interacted; DO NOT use as empirical observations.
        decision="ACCEPT" if arm=="B_APPROVAL_REAL" else "CHOOSE"
        policy=case["proposed_policy"] if decision=="ACCEPT" else "balanced"
        if policy not in c.POLICIES:
            policy="balanced";decision="CHANGE"
        issued_at=12345+ix
        t=c.issue_event(SID,case["id"],arm,decision,policy,
                        "nonce-"+f"{ix:028d}",KEY,issued_at)
        outcome=c.execute_authorized(case,arm,SID,t,KEY,issued_at,set())
        baseline=c.shadow(case)
        rows.append({"case_id":case["id"],"arm":arm,"decision":decision,
                     "policy":policy,"status":outcome["status"],
                     "selected":outcome["selected"],"score_proxy":c.score_proxy(case,outcome["selected"]),
                     "shadow_status":baseline["status"],"shadow_selected":baseline["selected"],
                     "shadow_policy":baseline["policy"],
                     "shadow_score_proxy":baseline["score_proxy"],
                     "elapsed_human_input_ms":1000+ix, "event_token":t})
    record=c.build_session(SID,"2026-10-28T20:00:00+00:00",order,rows,True)
    env={"record":record,"hmac":hmac.new(KEY,c.canonical(record),hashlib.sha256).hexdigest()}
    path=directory/(SID+".json")
    path.write_text(json.dumps(env))
    return path


class PrivateAuditTests(unittest.TestCase):
    def test_no_human_file_yields_no_participants(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(a.aggregate_private(Path(tmp),KEY),
                             {"designation":"NO_PARTICIPANTS_COLLECTED","sessions":0,"rows":0})

    def test_mock_record_verifies_but_is_not_human_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            report=a.audit_session(p,KEY)
            self.assertEqual(report["rows"],12)
            aggregate=a.aggregate_private(Path(tmp),KEY)
            self.assertEqual((aggregate["sessions"],aggregate["rows"]),(1,12))
            self.assertEqual(aggregate["paired_executed_cases"]+aggregate["unpaired_or_abstained_cases"],12)
            self.assertIn("NO_OUTCOME_UTILITY_OR_NONINFERIORITY",aggregate["notice"])
            self.assertNotIn("participant_names",aggregate)

    def test_modified_outer_record_fails_hmac(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            env=json.loads(p.read_text())
            env["record"]["consent"]="NO"
            p.write_text(json.dumps(env))
            with self.assertRaises(a.SessionAuditError):
                a.audit_session(p,KEY)

    def test_signed_but_modified_token_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            env=json.loads(p.read_text())
            env["record"]["rows"][0]["event_token"]["payload"]["policy"]="open"
            env["hmac"]=hmac.new(KEY,c.canonical(env["record"]),hashlib.sha256).hexdigest()
            p.write_text(json.dumps(env))
            with self.assertRaises(a.SessionAuditError):
                a.audit_session(p,KEY)

    def test_signed_but_wrong_assignment_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            env=json.loads(p.read_text())
            env["record"]["order"].reverse()
            env["hmac"]=hmac.new(KEY,c.canonical(env["record"]),hashlib.sha256).hexdigest()
            p.write_text(json.dumps(env))
            with self.assertRaises(a.SessionAuditError):
                a.audit_session(p,KEY)

    def test_extra_pii_field_rejected_even_when_signed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            env=json.loads(p.read_text())
            env["record"]["participant_email"]="do-not-collect@example.invalid"
            env["hmac"]=hmac.new(KEY,c.canonical(env["record"]),hashlib.sha256).hexdigest()
            p.write_text(json.dumps(env))
            with self.assertRaises(a.SessionAuditError):
                a.audit_session(p,KEY)

    def test_session_filename_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=fake_ci_session(Path(tmp))
            p.rename(Path(tmp)/("d"*32+".json"))
            with self.assertRaises(a.SessionAuditError):
                a.aggregate_private(Path(tmp),KEY)


if __name__=="__main__":
    unittest.main()
