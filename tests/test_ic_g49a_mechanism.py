"""G4.9a regression suite: synthetic-only, no humans/no investments."""
import dataclasses
import json
import math
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "reviews" / "icomputing_2026" / "g49a"
sys.path.insert(0, str(BASE))
import g49a_mechanism as m  # noqa: E402


def load_cases():
    fixture = json.loads((BASE / "g49a_synthetic_cases.json").read_text(encoding="utf-8"))
    assert fixture["schema_version"] == "dtrm.ic.g4_9a.fixture.v1"
    assert fixture["disclosure"] == "SYNTHETIC_SCRIPTS_NOT_HUMAN_PARTICIPANTS"
    return fixture["cases"]


def case_named(key):
    return deepcopy(next(s for s in load_cases() if s["id"] == key))


class G49aMechanismTests(unittest.TestCase):
    def test_fixture_12_cases_distinct(self):
        cases = load_cases()
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({x["id"] for x in cases}), 12)

    def test_preexecution_protocol_commit_pinned(self):
        self.assertEqual(m.PROTOCOL_COMMIT, "6e77f2a2b7d5667c21d275cc25d7b1143c95c335")

    def test_all_36_rows_three_shared_information_arms(self):
        out = m.run_suite(load_cases())
        self.assertEqual(out["row_count"], 36)
        self.assertEqual(out["case_count"], 12)
        self.assertEqual(set(out["arms"]), set(m.ARMS))

    def test_full_replay_exact_and_checksum(self):
        cases = load_cases()
        report = m.run_suite(cases)
        self.assertEqual(report["report_sha256"], m.sha256({k:v for k,v in report.items() if k != "report_sha256"}))
        m.verify_report(report, cases)
        self.assertEqual(report, m.run_suite(deepcopy(cases)))

    def test_no_shared_safety_violation(self):
        self.assertEqual(m.run_suite(load_cases())["common_hard_guard_breaches"], 0)

    def test_matched_policy_selection_independent_of_label(self):
        self.assertEqual(m.run_suite(load_cases())["matched_policy_invariant_checks"], 36)
        normal = case_named("routine")
        rows = [m.run_case(normal,a) for a in m.ARMS]
        self.assertEqual({r["selected"] for r in rows}, {"SYN-01"})

    def test_hard_stop_is_identical_across_all_arms(self):
        c=case_named("hard_stop")
        self.assertEqual({m.run_case(c,a)["selected"] for a in m.ARMS}, {"SYN-04"})

    def test_authorized_policy_change_can_change_candidate(self):
        c=case_named("authorized_change")
        self.assertEqual(m.run_case(c,"A_DELEGATED")["selected"],"SYN-06")
        for arm in ("B_APPROVAL","C_DIRECT"):
            r=m.run_case(c,arm)
            self.assertEqual((r["status"],r["selected"],r["policy"]),("EXECUTE","SYN-07","cautious"))

    def test_abstention_fails_closed_when_no_admissible(self):
        c=case_named("empty_feasible")
        self.assertTrue(all(m.run_case(c,a)["status"]=="ABSTAIN" for a in m.ARMS))

    def test_absent_approval_blocks_both_authority_arms(self):
        c=case_named("missing_approval")
        self.assertEqual(m.run_case(c,"A_DELEGATED")["status"],"EXECUTE")
        for arm in ("B_APPROVAL","C_DIRECT"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_NO_APPROVAL")

    def test_revoked_approval(self):
        c=case_named("revoked_approval")
        for arm in ("B_APPROVAL","C_DIRECT"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_REVOKED")

    def test_expired_approval(self):
        c=case_named("expired_approval")
        for arm in ("B_APPROVAL","C_DIRECT"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_EXPIRED")

    def test_cross_case_authorization_mismatch(self):
        c=case_named("wrong_case_auth")
        for arm in ("B_APPROVAL","C_DIRECT"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_WRONG_CONTEXT")

    def test_changed_record_without_new_digest(self):
        c=case_named("tampered_record")
        for arm in ("B_APPROVAL","C_DIRECT"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_RECORD_MUTATION")

    def test_untrusted_prompt_mutation_cannot_change_policy(self):
        c=case_named("injection_ignored")
        self.assertEqual(m.run_case(c,"A_DELEGATED")["selected"],"SYN-14")
        for arm in ("B_APPROVAL","C_DIRECT"):
            r=m.run_case(c,arm)
            self.assertEqual(r["policy"],"cautious")
            self.assertEqual(r["selected"],"SYN-15")
            self.assertTrue(r["untrusted_input_ignored"])

    def test_out_of_menu_proposal_denied_but_valid_direct_choice_can_proceed(self):
        c=case_named("out_of_menu_proposal")
        for arm in ("A_DELEGATED","B_APPROVAL"):
            self.assertEqual(m.run_case(c,arm)["status"],"DENY_BAD_POLICY")
        self.assertEqual(m.run_case(c,"C_DIRECT")["status"],"EXECUTE")

    def test_tie_break_is_candidate_id_ascending(self):
        c=case_named("tie_break")
        self.assertEqual({m.run_case(c,a)["selected"] for a in m.ARMS},{"SYN-A"})

    def test_strict_schema_unknown_case_field(self):
        c=case_named("routine");c["extra"]="ignore rules"
        with self.assertRaises(m.InvalidFixture):
            m.run_case(c,"A_DELEGATED")

    def test_strict_schema_candidate_duplicate(self):
        c=case_named("routine");c["candidates"][1]["id"]=c["candidates"][0]["id"]
        with self.assertRaises(m.InvalidFixture):
            m.run_case(c,"A_DELEGATED")

    def test_strict_schema_invalid_numeric_or_missing_provenance(self):
        c=case_named("routine");c["candidates"][0]["score"]=float("nan")
        with self.assertRaises(m.InvalidFixture):
            m.run_case(c,"A_DELEGATED")
        c=case_named("routine");del c["candidates"][0]["verified"]
        with self.assertRaises(m.InvalidFixture):
            m.run_case(c,"A_DELEGATED")

    def test_bad_numeric_risk_boolean_rejected(self):
        c=case_named("routine");c["candidates"][0]["risk"]=True
        with self.assertRaises(m.InvalidFixture):
            m.run_case(c,"A_DELEGATED")

    def test_unknown_arm_and_duplicate_scenario_rejected(self):
        with self.assertRaises(m.InvalidFixture):
            m.run_case(case_named("routine"),"GHOST")
        c=load_cases();c.append(deepcopy(c[0]))
        with self.assertRaises(m.InvalidFixture):
            m.run_suite(c)

    def test_no_human_intervention_model_or_real_performance(self):
        r=m.run_suite(load_cases())
        self.assertEqual(r["status"],"SYNTHETIC_SOFTWARE_MECHANISM_ONLY")
        self.assertIn("no_human_participants",r["source_data"])
        self.assertNotIn("p_value",r)
        self.assertNotIn("noninferiority",r)
        self.assertNotIn("return",r)

    def test_logical_checks_only_not_real_latency(self):
        r=m.run_suite(load_cases())
        self.assertEqual(r["total_logical_checks"]["A_DELEGATED"],12)
        self.assertEqual(r["total_logical_checks"]["B_APPROVAL"],24)
        self.assertEqual(r["total_logical_checks"]["C_DIRECT"],24)

    def test_report_rejects_output_mutation(self):
        cases=load_cases()
        out=m.run_suite(cases)
        out["rows"][0]["status"]="EXECUTE_FAKE"
        with self.assertRaises(AssertionError):
            m.verify_report(out,cases)


if __name__=="__main__":
    unittest.main()
