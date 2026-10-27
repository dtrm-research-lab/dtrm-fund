#!/usr/bin/env python3
"""G2 freeze gate self-tests; metadata JSON only, no scientific raw data.

From research/reviews/icomputing_2026:
  python3 -m unittest test_ic_g2_freeze_preflight.py -v
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from ic_g2_freeze_preflight import verify

ROOT=Path(__file__).resolve().parent

class G2FreezePreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix=json.loads((ROOT/"G2_REVIEWER_TRACEABILITY_PROVISIONAL.json").read_text(encoding="utf-8"))
        cls.protocol=(ROOT/"G2_REVISION_PROTOCOL_DRAFT.md").read_text(encoding="utf-8")

    def validate(self,mod=None,protocol=None):
        doc=copy.deepcopy(self.matrix)
        if mod:mod(doc)
        return verify(doc,self.protocol if protocol is None else protocol)[0]

    def test_provisional_matrix_is_blocked(self):
        reasons=self.validate()
        self.assertIn("AUTHENTIC_EDITOR_DECISION_MISSING",reasons)
        self.assertIn("AUTHENTIC_REVIEWER_COMMENTS_MISSING",reasons)
        self.assertIn("EDITOR_SOURCE_DIGEST_MISSING",reasons)
        self.assertIn("EDITOR_REVIEWER_ITEMS_NOT_ENUMERATED",reasons)
        self.assertIn("PROTOCOL_FROZEN_COMMIT_NOT_SET",reasons)
        self.assertGreater(len(reasons),10)

    def test_original_relative_p10_cutoff_cannot_change(self):
        reasons=self.validate(lambda doc:doc["outcome_protection"].update({
            "original_relative_p10_threshold":-0.15
        }))
        self.assertIn("ORIGINAL_P10_VETO_CHANGED",reasons)

    def test_v1_zero_acceptance_must_remain_negative(self):
        reasons=self.validate(lambda doc:doc["outcome_protection"].update({
            "original_v1_absolute_guardrail_feasibility":"PROMOTED"
        }))
        self.assertIn("V1_NEGATIVE_FEASIBILITY_NOT_PROTECTED",reasons)

    def test_g1_source_hashes_pinned(self):
        reasons=self.validate(lambda doc:doc.update({
            "g1_historical_dossier_sha256":"0"*64
        }))
        self.assertIn("G1_2K_HISTORICAL_DOSSIER_HASH_MISMATCH",reasons)

    def test_g2_cannot_approve_new_independent_inference(self):
        reasons=self.validate(lambda doc:doc["outcome_protection"].update({
            "new_independent_holdout_permitted":True
        }))
        self.assertIn("NEW_INDEPENDENT_HOLDOUT_MUST_REMAIN_BLOCKED",reasons)

    def test_protocol_must_state_limits_and_cutoff(self):
        reasons=self.validate(protocol="G2 G3 2026-11-25")
        self.assertTrue(any(x.startswith("PROTOCOL_MISSING_FIXED_TOKEN") for x in reasons))

    def test_forged_empty_letter_must_not_pass(self):
        def fake(doc):
            doc.update({
                "editor_decision_authenticated":True,
                "reviewer_comments_authenticated":True,
                "source_document_sha256":"f"*64,
                "source_document_uri":"https://example.invalid/letter",
                "reviewer_comment_coverage_verified":True,
                "all_g3_analyses_specified":True,
                "revision_protocol_freeze_commit":"some-commit",
            })
        reasons=self.validate(fake)
        self.assertIn("EDITOR_REVIEWER_ITEMS_NOT_ENUMERATED",reasons)
        self.assertIn("REVIEWER_COMMENT_COUNT_OR_COVERAGE_MISMATCH",reasons)

    def test_invalid_reviewer_id_and_source_unverified(self):
        def fake(doc):
            doc["actual_reviewer_comments"]=[{
                "id":"Reviewer A", "source_document_sha256":"bad",
                "source_locator":"page 1", "requirement_text":"f"*30,
                "verified_against_source":False,
                "g2_action_id":"Q-01","g5_section":"methods","g6_response_id":"R1"
            }]
            doc["actual_reviewer_comment_count"]=1
        reasons=self.validate(fake)
        self.assertIn("REVIEWER_ID_UNATTRIBUTED",reasons)
        self.assertIn("REVIEWER_SOURCE_DIGEST_LINEAGE_MISSING",reasons)
        self.assertIn("REVIEWER_ATTRIBUTION_NOT_VERIFIED",reasons)

    def test_new_exploratory_analysis_requires_spec_or_nonexecute(self):
        reasons=self.validate()
        self.assertIn("G3_EXPLORATORY_SPEC_OR_NONEXECUTABLE_JUSTIFICATION_MISSING",reasons)

if __name__=="__main__":
    unittest.main()
