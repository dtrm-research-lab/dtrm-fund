"""G4.9b tests: synthetic/mock inputs only. NEVER count CI as a human participant."""
from __future__ import annotations

import dataclasses
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BASE=Path(__file__).resolve().parents[1] / "research" / "reviews" / "icomputing_2026" / "g49b"
sys.path.insert(0,str(BASE))
import g49b_core as c  # noqa: E402
import g49b_pilot as cli  # noqa: E402

KEY=b"k"*32
SID="a"*32


def raw_token(case="routine",arm="B_APPROVAL_REAL",decision="ACCEPT",policy="balanced",now=100):
    return c.issue_event(SID,case,arm,decision,policy,"nonce-"+"z"*30,KEY,now)


class G49bPilotTests(unittest.TestCase):
    def test_protocol_precedes_executable(self):
        self.assertEqual(c.PROTOCOL_COMMIT,"7fbf67314f39f2bc7b9e34958dd3cbb38341ff3d")

    def test_fixture_pinned_and_no_real_market_inputs(self):
        stimuli=c.load_stimuli()
        self.assertEqual(len(stimuli),12)
        self.assertEqual(c.sha(stimuli),c.FIXTURE_CANONICAL_SHA256)
        self.assertTrue(all(x["id"]!="real_market" for x in stimuli))

    def test_balanced_within_session_assignments(self):
        a=c.assignment(SID,KEY,c.load_stimuli())
        self.assertEqual(len(a),12)
        self.assertEqual({x["case_id"] for x in a},{x["id"] for x in c.load_stimuli()})
        self.assertEqual([x["arm"] for x in a].count("B_APPROVAL_REAL"),6)
        self.assertEqual([x["arm"] for x in a].count("C_DIRECT_REAL"),6)
        self.assertEqual(a,c.assignment(SID,KEY,c.load_stimuli()))

    def test_different_id_changes_assignment_seed(self):
        a=c.assignment(SID,KEY,c.load_stimuli())
        b=c.assignment("b"*32,KEY,c.load_stimuli())
        self.assertNotEqual(a,b)

    def test_wrong_context_rejected(self):
        t=raw_token()
        for sid,cid,arm in [("b"*32,"routine","B_APPROVAL_REAL"),(SID,"other","B_APPROVAL_REAL"),(SID,"routine","C_DIRECT_REAL")]:
            with self.assertRaises(c.IntegrityFailure):
                c.verify_event(t,KEY,sid,cid,arm,100,set())

    def test_mac_tampering_rejected(self):
        t=raw_token()
        t["payload"]["policy"]="cautious"
        with self.assertRaises(c.IntegrityFailure):
            c.verify_event(t,KEY,SID,"routine","B_APPROVAL_REAL",100,set())

    def test_wrong_key_rejected(self):
        with self.assertRaises(c.IntegrityFailure):
            c.verify_event(raw_token(),b"q"*32,SID,"routine","B_APPROVAL_REAL",100,set())

    def test_expired_future_rejected(self):
        with self.assertRaises(c.IntegrityFailure):
            c.verify_event(raw_token(),KEY,SID,"routine","B_APPROVAL_REAL",3701,set())
        with self.assertRaises(c.IntegrityFailure):
            c.verify_event(raw_token(),KEY,SID,"routine","B_APPROVAL_REAL",99,set())

    def test_replay_nonce_rejected(self):
        t=raw_token()
        used=set()
        c.verify_event(t,KEY,SID,"routine","B_APPROVAL_REAL",100,used)
        with self.assertRaises(c.IntegrityFailure):
            c.verify_event(t,KEY,SID,"routine","B_APPROVAL_REAL",100,used)

    def test_approve_matches_proposed(self):
        r=c.execute_authorized(c.load_stimuli()[0],"B_APPROVAL_REAL",SID,raw_token(),KEY,100,set())
        self.assertEqual((r["status"],r["selected"]),("EXECUTE","SYN-01"))

    def test_approve_mismatched_proposal_denied(self):
        t=raw_token(policy="cautious")
        with self.assertRaises(c.IntegrityFailure):
            c.execute_authorized(c.load_stimuli()[0],"B_APPROVAL_REAL",SID,t,KEY,100,set())

    def test_valid_change_can_change_selection(self):
        case=next(x for x in c.load_stimuli() if x["id"]=="authorized_change")
        t=c.issue_event(SID,case["id"],"B_APPROVAL_REAL","CHANGE","cautious",
                        "nonce-"+"x"*30,KEY,100)
        r=c.execute_authorized(case,"B_APPROVAL_REAL",SID,t,KEY,100,set())
        self.assertEqual((r["status"],r["selected"]),("EXECUTE","SYN-07"))
        self.assertEqual(c.shadow(case)["selected"],"SYN-06")

    def test_change_must_actually_change_policy(self):
        t=raw_token(decision="CHANGE",policy="balanced")
        with self.assertRaises(c.IntegrityFailure):
            c.execute_authorized(c.load_stimuli()[0],"B_APPROVAL_REAL",SID,t,KEY,100,set())

    def test_human_refusal(self):
        t=raw_token(decision="REFUSE",policy=None)
        r=c.execute_authorized(c.load_stimuli()[0],"B_APPROVAL_REAL",SID,t,KEY,100,set())
        self.assertEqual((r["status"],r["selected"]),("DENY_HUMAN_REFUSAL",None))

    def test_direct_choice_restriction(self):
        t=c.issue_event(SID,"routine","C_DIRECT_REAL","CHOOSE","open","nonce-"+"z"*30,KEY,100)
        r=c.execute_authorized(c.load_stimuli()[0],"C_DIRECT_REAL",SID,t,KEY,100,set())
        self.assertEqual(r["status"],"EXECUTE")
        with self.assertRaises(c.IntegrityFailure):
            c.execute_authorized(c.load_stimuli()[0],"C_DIRECT_REAL",SID,raw_token(),KEY,100,set())

    def test_shared_hard_guard_cannot_be_overridden(self):
        case=next(x for x in c.load_stimuli() if x["id"]=="hard_stop")
        t=c.issue_event(SID,case["id"],"C_DIRECT_REAL","CHOOSE","open","nonce-"+"z"*30,KEY,100)
        out=c.execute_authorized(case,"C_DIRECT_REAL",SID,t,KEY,100,set())
        self.assertEqual(out["selected"],"SYN-04")

    def test_empty_feasible_set_abstains(self):
        case=next(x for x in c.load_stimuli() if x["id"]=="empty_feasible")
        t=c.issue_event(SID,case["id"],"C_DIRECT_REAL","CHOOSE","open","nonce-"+"z"*30,KEY,100)
        self.assertEqual(c.execute_authorized(case,"C_DIRECT_REAL",SID,t,KEY,100,set())["status"],"ABSTAIN")

    def test_invalid_policy_issuance_rejected(self):
        with self.assertRaises(ValueError):
            c.issue_event(SID,"routine","B_APPROVAL_REAL","ACCEPT","other",
                          "nonce-"+"z"*30,KEY,100)

    def test_session_does_not_forge_consented_data(self):
        order=c.assignment(SID,KEY,c.load_stimuli())
        with self.assertRaises(c.IntegrityFailure):
            c.build_session(SID,"2026-10-28T00:00:00Z",order,[],True)
        with self.assertRaises(c.IntegrityFailure):
            c.build_session(SID,"2026-10-28T00:00:00Z",order,[],False)

    def test_no_consent_records_nothing(self):
        class TTY:
            def isatty(self):return True
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(cli.sys,"stdin",TTY()), mock.patch.object(cli.sys,"stdout",TTY()):
                with mock.patch.object(cli,"_ask",return_value="NO"):
                    self.assertIsNone(cli.run_enrollment(Path(tmp)))
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_not_a_tty_never_enrolls(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(cli.sys.stdin,"isatty",return_value=False):
                with self.assertRaises(RuntimeError):
                    cli.run_enrollment(Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_key_private_storage_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"pilot"
            cli.initialize(root)
            p=root/".issuer_hmac_key"
            self.assertEqual(p.stat().st_mode & 0o077,0)
            self.assertEqual(root.stat().st_mode & 0o077,0)
            self.assertEqual(len(cli._key(root)),32)
            with self.assertRaises(FileExistsError):
                cli.initialize(root)

    def test_unsafe_repo_private_dir_rejected(self):
        with self.assertRaises(ValueError):
            cli._private_root(cli.ROOT_REPO/"research"/"local_data"/"participant_logs")

    def test_withdraw_works_by_random_session_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=root/(SID+".json")
            p.write_text("{}")
            cli.withdraw(root,SID)
            self.assertFalse(p.exists())

    def test_withdraw_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                cli.withdraw(Path(tmp),"../test")

    def test_no_stats_or_real_return_claims_in_core(self):
        s=Path(c.__file__).read_text()
        self.assertIn("not the identity of a human",s)
        self.assertNotIn("scipy",s)
        self.assertNotIn("realized_profit",s)


if __name__=="__main__":
    unittest.main()
