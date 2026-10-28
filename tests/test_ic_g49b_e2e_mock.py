"""G4.9b end-to-end terminal smoke test with MOCKED keyboard input.

IMPORTANT: absolutely NO real participant. All mock session files are created in
a temporary directory and automatically deleted. These tests must NOT be counted
as observed humans or used for behavioral inference or publication outcomes.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "reviews" / "icomputing_2026" / "g49b"
sys.path.insert(0, str(BASE))
import g49b_core as core  # noqa: E402
import g49b_pilot as cli  # noqa: E402
import g49b_audit as audit  # noqa: E402


class FakeTerminal(io.StringIO):
    """Implements a TTY-looking test double; NOT a person."""
    def isatty(self):
        return True


class G49bFullInteractiveMockTests(unittest.TestCase):
    def test_complete_12_task_cli_run_audit_withdraw_all_local(self):
        """Consent YES/YES + actual CLI prompts + authorized choices + private audit."""
        sid = "e" * 32
        with tempfile.TemporaryDirectory(prefix="g49b_MOCK_NOT_HUMAN_") as tmp:
            private = Path(tmp) / "operator-private"
            self.assertFalse(private.exists())
            cli.initialize(private)
            secret = cli._key(private)
            cases = core.load_stimuli()
            order = core.assignment(sid, secret, cases)
            by_id = {x["id"]: x for x in cases}
            scripted_answers = ["YES", "YES"]  # mock opt-in, NOT a human
            for row in order:
                case = by_id[row["case_id"]]
                arm = row["arm"]
                if arm == "B_APPROVAL_REAL":
                    if case["id"] == "routine":
                        scripted_answers.append("R")
                    elif case["proposed_policy"] not in core.POLICIES:
                        scripted_answers.extend(["M", "BALANCED"])
                    elif case["id"] == "authorized_change":
                        scripted_answers.extend(["M", "CAUTIOUS"])
                    else:
                        scripted_answers.append("A")
                else:
                    scripted_answers.append("R" if case["id"] == "routine" else "BALANCED")

            fake_in, fake_out = FakeTerminal(), FakeTerminal()
            nonces = [f"{i + 1:032x}" for i in range(12)]
            with (mock.patch.object(sys, "stdin", fake_in),
                  mock.patch.object(sys, "stdout", fake_out),
                  mock.patch("builtins.input", side_effect=scripted_answers) as reader,
                  mock.patch.object(cli.secrets, "token_hex", side_effect=[sid] + nonces)):
                self.assertEqual(cli.run_enrollment(private), sid)
                self.assertEqual(reader.call_count, len(scripted_answers))

            stored_path = private / f"{sid}.json"
            self.assertTrue(stored_path.is_file())
            self.assertEqual(stored_path.stat().st_mode & 0o077, 0)
            self.assertEqual(private.stat().st_mode & 0o077, 0)
            saved = json.loads(stored_path.read_text())
            self.assertEqual(saved["record"]["consent"], "ACTIVE_YES_AND_ADULT_YES")
            self.assertEqual(len(saved["record"]["rows"]), 12)
            self.assertEqual([r["arm"] for r in saved["record"]["rows"]].count("B_APPROVAL_REAL"), 6)
            self.assertEqual([r["arm"] for r in saved["record"]["rows"]].count("C_DIRECT_REAL"), 6)
            self.assertTrue(all("event_token" in r for r in saved["record"]["rows"]))

            verified = audit.audit_session(stored_path, secret)
            summary = audit.aggregate_private(private, secret)
            self.assertEqual(verified["rows"], 12)
            self.assertEqual(summary["rows"], 12)
            self.assertEqual(summary["sessions"], 1)
            self.assertEqual(
                summary["paired_executed_cases"] + summary["unpaired_or_abstained_cases"], 12
            )
            self.assertIn("NO_OUTCOME_UTILITY_OR_NONINFERIORITY", summary["notice"])
            self.assertNotIn("participant_email", json.dumps(saved))
            self.assertNotIn("participant_name", json.dumps(saved))

            # Explicitly delete *mock* participant-like record. Never publish.
            cli.withdraw(private, sid)
            self.assertFalse(stored_path.exists())
            self.assertEqual(audit.aggregate_private(private, secret)["sessions"], 0)
        print("G49B_E2E_MOCK_ONLY_CONSENT_12_TASKS_AUDIT_WITHDRAW_PASS")

    def test_mock_participant_declines_consent_no_file_written(self):
        with tempfile.TemporaryDirectory(prefix="g49b_MOCK_NOT_HUMAN_") as tmp:
            private = Path(tmp) / "operator-private"
            cli.initialize(private)
            fake_in, fake_out = FakeTerminal(), FakeTerminal()
            with (mock.patch.object(sys, "stdin", fake_in),
                  mock.patch.object(sys, "stdout", fake_out),
                  mock.patch("builtins.input", return_value="NO")):
                self.assertIsNone(cli.run_enrollment(private))
            self.assertEqual(list(private.glob("*.json")), [])
        print("G49B_E2E_MOCK_ONLY_NO_CONSENT_NO_RECORD_PASS")

    def test_mock_participant_declines_adult_eligibility_no_file_written(self):
        with tempfile.TemporaryDirectory(prefix="g49b_MOCK_NOT_HUMAN_") as tmp:
            private = Path(tmp) / "operator-private"
            cli.initialize(private)
            fake_in, fake_out = FakeTerminal(), FakeTerminal()
            with (mock.patch.object(sys, "stdin", fake_in),
                  mock.patch.object(sys, "stdout", fake_out),
                  mock.patch("builtins.input", side_effect=["YES", "NO"])):
                self.assertIsNone(cli.run_enrollment(private))
            self.assertEqual(list(private.glob("*.json")), [])
        print("G49B_E2E_MOCK_ONLY_NOT_ADULT_NO_RECORD_PASS")

    def test_mock_participant_quit_mid_task_no_completed_record(self):
        with tempfile.TemporaryDirectory(prefix="g49b_MOCK_NOT_HUMAN_") as tmp:
            private = Path(tmp) / "operator-private"
            cli.initialize(private)
            fake_in, fake_out = FakeTerminal(), FakeTerminal()
            with (mock.patch.object(sys, "stdin", fake_in),
                  mock.patch.object(sys, "stdout", fake_out),
                  mock.patch("builtins.input", side_effect=["YES", "YES", "QUIT"])):
                self.assertIsNone(cli.run_enrollment(private))
            self.assertEqual(list(private.glob("*.json")), [])
        print("G49B_E2E_MOCK_ONLY_WITHDRAW_MID_TASK_NO_RECORD_PASS")

    def test_real_interactive_enrollment_rejected_on_non_tty(self):
        with tempfile.TemporaryDirectory(prefix="g49b_MOCK_NOT_HUMAN_") as tmp:
            with (mock.patch.object(sys.stdin, "isatty", return_value=False)):
                with self.assertRaises(RuntimeError):
                    cli.run_enrollment(Path(tmp))
            self.assertEqual(list(Path(tmp).rglob("*.json")), [])


if __name__ == "__main__":
    unittest.main()
