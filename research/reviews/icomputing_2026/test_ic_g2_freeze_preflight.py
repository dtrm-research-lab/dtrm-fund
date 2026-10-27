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

    def test_supplied_letter_is_mapped_but_freeze_remains_blocked(self):
        reasons=self.validate()
        self.assertEqual(len(self.matrix["actual_reviewer_comments"]),22)
        self.assertNotIn("EDITOR_REVIEWER_ITEM_COUNT_MISMATCH",reasons)
        self.assertNotIn("EDITORIAL_SOURCE_MODE_MISSING",reasons)
        self.assertIn("PROTOCOL_FROZEN_COMMIT_NOT_SET",reasons)
        self.assertIn("ALL_G3_ANALYSES_NOT_PREDECLARED",reasons)
        self.assertNotIn("REVIEWER_MANUSCRIPT_SECTION_UNRESOLVED",reasons)

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
            doc["actual_reviewer_comments"]=[]
            doc["actual_reviewer_comment_count"]=0
            doc["all_g3_analyses_specified"]=True
            doc["revision_protocol_freeze_commit"]="some-commit"
        reasons=self.validate(fake)
        self.assertIn("EDITOR_REVIEWER_ITEMS_NOT_ENUMERATED",reasons)
        self.assertIn("EDITOR_REVIEWER_ITEM_COUNT_MISMATCH",reasons)
        self.assertIn("ORIGINAL_REVIEWER_ITEM_COVERAGE_INCOMPLETE",reasons)

    def test_invalid_reviewer_id_and_source_unverified(self):
        def fake(doc):
            doc["actual_reviewer_comments"][0].update({
                "id":"Reviewer A","source_status":"UNKNOWN",
                "source_document_sha256":"0"*64,
                "verified_against_source":False
            })
        reasons=self.validate(fake)
        self.assertIn("REVIEWER_ID_UNATTRIBUTED",reasons)
        self.assertIn("REVIEWER_USER_TRANSCRIPT_PROVENANCE_MISSING",reasons)
        self.assertIn("UNVERIFIED_SOURCE_MUST_NOT_HAVE_ASSERTED_HASH",reasons)
        self.assertIn("REVIEWER_ATTRIBUTION_NOT_VERIFIED",reasons)

    def test_missing_editor_requirement_detected(self):
        def fake(doc):
            doc["actual_reviewer_comments"]=[x for x in doc["actual_reviewer_comments"] if x["id"]!="E-04"]
            doc["actual_reviewer_comment_count"]=21
        reasons=self.validate(fake)
        self.assertIn("ORIGINAL_REVIEWER_ITEM_COVERAGE_INCOMPLETE",reasons)
        self.assertIn("EDITOR_REVIEWER_ITEM_PREFIX_COUNTS_MISMATCH",reasons)

    def test_missing_second_reviewers_literature_request_detected(self):
        def fake(doc):
            doc["actual_reviewer_comments"]=[x for x in doc["actual_reviewer_comments"] if x["id"]!="R2-08"]
        reasons=self.validate(fake)
        self.assertIn("ORIGINAL_REVIEWER_ITEM_COVERAGE_INCOMPLETE",reasons)

    def test_new_exploratory_analysis_requires_spec_or_nonexecute(self):
        reasons=self.validate()
        self.assertIn("G3_EXPLORATORY_SPEC_OR_NONEXECUTABLE_JUSTIFICATION_MISSING",reasons)

if __name__=="__main__":
    unittest.main()
