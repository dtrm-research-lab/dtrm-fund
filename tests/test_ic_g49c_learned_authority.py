"""G4.9c synthetic learned policy and independent utility oracle: no humans."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"research"/"reviews"/"icomputing_2026"/"g49c"
sys.path.insert(0,str(SRC))
import g49c_agent as agent  # noqa
import g49c_world as world  # noqa
import g49c_run as run  # noqa


class G49cLearnedHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train,cls.eval=world.make_worlds()
        cls.model=agent.fit(world.training_rows(cls.train))

    def test_preexecution_protocol_pinned(self):
        self.assertEqual(agent.PROTOCOL_COMMIT,"333de0347f830dd7d581e992fcaa8fc905b04043")

    def test_fixed_train_300_and_holdout_60(self):
        self.assertEqual((len(self.train),len(self.eval)),(300,60))

    def test_train_holdout_ids_and_candidate_ids_do_not_overlap(self):
        trainids={w.public["id"] for w in self.train}
        testids={w.public["id"] for w in self.eval}
        self.assertFalse(trainids & testids)
        cid_train={c["id"] for w in self.train for c in w.public["candidates"]}
        cid_test={c["id"] for w in self.eval for c in w.public["candidates"]}
        self.assertFalse(cid_train & cid_test)

    def test_deterministic_generator(self):
        t,e=world.make_worlds()
        self.assertEqual(world.public_case_commitments(t),world.public_case_commitments(self.train))
        self.assertEqual(world.public_case_commitments(e),world.public_case_commitments(self.eval))

    def test_public_features_exclude_hidden_outcomes(self):
        for w in self.eval:
            self.assertEqual(set(w.public),{"id","risk_weight","candidates"})
            self.assertNotIn("realized_quality_by_id",json.dumps(w.public))

    def test_only_train_cases_accepted_for_fit_labels(self):
        with self.assertRaises(ValueError):
            world.training_rows(self.eval)
        rows=world.training_rows(self.train)
        self.assertEqual(len(rows),300)

    def test_train_rows_include_all_three_policies(self):
        for case,utility in world.training_rows(self.train):
            self.assertEqual(set(utility),set(agent.POLICY_ORDER))

    def test_model_is_fitted_not_fixed_hardcoded_choice(self):
        self.assertEqual((self.model.train_count,self.model.train_policy_rows),(300,900))
        self.assertEqual(len(self.model.coeffs),7)
        self.assertGreater(len({self.model.choose(w.public) for w in self.eval}),1)

    def test_agent_does_not_read_independent_hidden_labels(self):
        w=self.eval[0]
        p=self.model.choose(w.public)
        q=copy.deepcopy(w.public)
        self.assertEqual(self.model.choose(q),p)
        # Oracle labels don't appear in public case and cannot alter its choice.
        adjusted=world.World(q,{k:100000.0 for k in w.realized_quality_by_id})
        self.assertEqual(self.model.choose(adjusted.public),p)
        self.assertNotEqual(world.oracle_utility(w,p),
                            world.oracle_utility(adjusted,p))

    def test_all_policies_use_same_hard_safety_guard(self):
        for w in self.eval:
            for p in agent.POLICY_ORDER:
                pick=agent.select_candidate(w.public,p)
                if pick is not None:
                    self.assertTrue(pick["verified"])
                    self.assertFalse(pick["blocked"])
                    self.assertLessEqual(pick["risk"],5)
                    self.assertLessEqual(pick["risk"],agent.POLICY_LIMITS[p])

    def test_same_policy_deterministic_under_identical_public_inputs(self):
        for w in self.eval:
            for p in agent.POLICY_ORDER:
                a=agent.select_candidate(w.public,p)
                b=agent.select_candidate(copy.deepcopy(w.public),p)
                self.assertEqual(a,b)

    def test_unknown_policy_rejected(self):
        with self.assertRaises(ValueError):
            agent.select_candidate(self.eval[0].public,"no-rule")

    def test_utilities_are_finite_independent_synthetic_labels(self):
        vals=[world.oracle_utility(w,p) for w in self.eval for p in agent.POLICY_ORDER]
        self.assertEqual(len(vals),180)
        self.assertTrue(all(float("-inf")<x<float("inf") for x in vals))

    def test_heldout_full_evaluation_no_cherry_pick(self):
        r=run.benchmark()
        self.assertEqual((r["training_cases"],r["heldout_cases"]),(300,60))
        self.assertEqual(sum(r["agent"]["choose_counts"].values()),60)
        self.assertEqual(sum(r["learned_minus_balanced_"+s+"_cases"] for s in ("positive","negative","equal")),60)
        self.assertEqual(r["shared_hard_guard_breaches"],0)
        self.assertEqual(r["oracle_upper_bound_breaches"],0)

    def test_human_observations_and_noninferiority_explicitly_absent(self):
        r=run.benchmark()
        self.assertEqual(r["participant_count"],0)
        self.assertEqual(r["actual_llm_agent_count"],0)
        self.assertEqual(r["actual_human_authority_observations"],0)
        self.assertEqual(r["noninferiority"],"NOT_TESTED")
        self.assertNotIn("p_value",r)
        self.assertNotIn("human_mean",r)

    def test_report_reproducibility_and_hash(self):
        a=run.benchmark()
        b=run.benchmark()
        self.assertEqual(a,b)
        h=a.pop("report_sha256")
        self.assertEqual(h,world.canonical_sha(a))


if __name__=="__main__":
    unittest.main()
