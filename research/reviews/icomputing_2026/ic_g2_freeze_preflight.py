#!/usr/bin/env python3
"""G2 Agentic Graph Engineering fail-closed reviewer-to-experiment freeze preflight.

Reads only revision protocol Markdown and local G2 traceability JSON
metadata, never raw evidence/targets/news/models, never freezes by itself.
A BLOCKED report is a *correct* outcome until the authentic editor
letter, every comment and allowed new-analysis specs are documented.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PIN="c7502a690162459cdfb3413573e3133c42efb126"
CASE="ICOMPUTING-D-26-01069"
HIST="7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac"
DATE="388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f"
FIXED_CUTOFF=-0.16665692627429962
OFFSET=-0.06494169682264328
DISPOSITIONS={
    "ALREADY_FROZEN_HISTORICAL_STATISTICS",
    "DESCRIPTIVE_DOCUMENTATION",
    "DESCRIPTIVE_AND_CONDITIONAL",
    "DESCRIPTIVE_PLUS_CONDITIONAL",
    "EXPLORATORY_POST_OUTCOME_CONDITIONAL",
    "EXPLORATORY_IF_AUTHENTIC_BASELINE_EXISTS",
    "NOT_EXECUTABLE_VERIFIED_SOURCE_UNAVAILABLE",
    "NOT_EXECUTABLE",
}
ALLOWED_G3_PREFIXES=("REUSE_","NO_NEW_","ORIGINAL_","NOT_AUTHORIZED_","BLOCKED_")
REVIEW_ID=re.compile(r"^(?:E-\d{2,}|R\d+-\d{2,})$")
SHA=re.compile(r"^[0-9a-f]{64}$")

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def verify(matrix:dict,protocol:str):
    blocks=[]
    notes=[]
    def gate(ok:bool,code:str):
        if not ok: blocks.append(code)

    gate(matrix.get("schema_version")=="dtrm.ic.g2.reviewer_requirement_map.v1","SCHEMA_VERSION_UNEXPECTED")
    gate(matrix.get("case_id")==CASE,"EDITORIAL_CASE_MISMATCH")
    gate(matrix.get("original_source_commit")==PIN,"ORIGINAL_SOURCE_COMMIT_MISMATCH")
    gate(matrix.get("g1_historical_dossier_sha256")==HIST,"G1_2K_HISTORICAL_DOSSIER_HASH_MISMATCH")
    gate(matrix.get("g1_historical_date_filter_sha256")==DATE,"G1_2M_DATE_ONLY_EVIDENCE_HASH_MISMATCH")
    original=matrix.get("outcome_protection",{})
    gate(original.get("new_independent_holdout_permitted") is False,"NEW_INDEPENDENT_HOLDOUT_MUST_REMAIN_BLOCKED")
    gate(original.get("original_v1_absolute_guardrail_feasibility")=="FAILED_ZERO_PASS_PROTECTED","V1_NEGATIVE_FEASIBILITY_NOT_PROTECTED")
    gate(original.get("original_relative_p10_threshold")==FIXED_CUTOFF,"ORIGINAL_P10_VETO_CHANGED")
    gate(original.get("original_calibration_offset")==OFFSET,"ORIGINAL_P10_CALIBRATION_CHANGED")
    gate(original.get("frozen_topk_fraction")==0.10,"ORIGINAL_TOPK_CHANGED")
    gate(original.get("original_v2_v3_v4_topk_deltas")==[
        0.14429480582475662,0.14943748898804188,0.027561593800783157
    ],"OLD_V2_V3_V4_POINT_RESULTS_CHANGED")
    cis=original.get("original_ticker_cluster_ci95",{})
    gate(isinstance(cis,dict) and
         "V2" in cis and "V3" in cis and "V4" in cis and
         cis.get("V2",[1])[0]<0 and cis.get("V4",[1])[0]<0
         and cis.get("V3",[0])[0]>0,
         "TICKER_CLUSTER_CI_LIMITATION_MISSING")
    gate("forward_excess_beta" in str(original.get("target","")) and
         "NOT_REALIZED_TRADING_PNL" in str(original.get("target","")),
         "REALIZED_PROFIT_CLAIM_NOT_BLOCKED")

    mandatory_protocol_tokens=[
        "G2", "G3", "NOT_EXECUTABLE", "EXPLORATORY",
        "2026-11-25", "0.16665692627429962", "0.06494169682264328",
        "60", "390", "V2", "V3", "V4"
    ]
    for token in mandatory_protocol_tokens:
        gate(token in protocol,"PROTOCOL_MISSING_FIXED_TOKEN_"+token.replace(" ","_"))
    comments=matrix.get("actual_reviewer_comments",[])
    source_mode=matrix.get("source_mode")
    # Explicit user-supplied complete editorial transcript is primary
    # source for *content mapping*, but NOT a provider-verified MIME.
    # Do not block G2 solely on lack of the Gmail connector or an
    # impossible-to-claim source SHA. Hold a separate non-crypto caveat.
    user_transcript=(source_mode=="USER_SUPPLIED_COMPLETE_EDITORIAL_EMAIL_BODY_IN_CHAT")
    provider_verified=(matrix.get("editor_decision_authenticated") is True
          and matrix.get("reviewer_comments_authenticated") is True
          and bool(SHA.fullmatch(matrix.get("source_document_sha256") or "")))
    gate(user_transcript or provider_verified,"EDITORIAL_SOURCE_MODE_MISSING")
    if user_transcript:
        gate(matrix.get("editorial_decision_date")=="2026-10-26",
             "USER_TRANSCRIPT_EDITORIAL_DECISION_DATE_MISMATCH")
        gate(matrix.get("actual_editor_letter",{}).get("decision")=="MAJOR_REVISION",
             "USER_TRANSCRIPT_EDITORIAL_DECISION_MISSING")
        gate(matrix.get("actual_editor_letter",{}).get("deadline")=="2026-11-25",
             "USER_TRANSCRIPT_REVISION_DUE_DATE_MISMATCH")
        notes.append("User-provided editorial text was checked in-chat; original provider MIME/source hash not independently authenticated.")
    else:
        gate(bool(SHA.fullmatch(matrix.get("source_document_sha256") or "")),
             "EDITOR_SOURCE_DIGEST_MISSING")
    gate(isinstance(matrix.get("source_document_uri"),str)
         and bool(matrix.get("source_document_uri")),
         "EDITOR_SOURCE_REFERENCE_MISSING")
    gate(isinstance(comments,list) and bool(comments),"EDITOR_REVIEWER_ITEMS_NOT_ENUMERATED")
    if not isinstance(comments,list): comments=[]
    expected=matrix.get("actual_reviewer_comment_count")
    gate(isinstance(expected,int) and expected==22 and len(comments)==expected,
         "EDITOR_REVIEWER_ITEM_COUNT_MISMATCH")
    breakdown=matrix.get("requirement_count_breakdown",{})
    gate(breakdown=={"editorial":7,"reviewer1_themes":7,
                     "reviewer2_numbered":8,"total":22},
         "EDITOR_REVIEWER_SOURCE_BREAKDOWN_MISMATCH")
    counted={
        "editorial":sum(str(z.get("id","")).startswith("E-") for z in comments if isinstance(z,dict)),
        "reviewer1_themes":sum(str(z.get("id","")).startswith("R1-") for z in comments if isinstance(z,dict)),
        "reviewer2_numbered":sum(str(z.get("id","")).startswith("R2-") for z in comments if isinstance(z,dict)),
        "total":len(comments)
    }
    gate(counted==breakdown,"EDITOR_REVIEWER_ITEM_PREFIX_COUNTS_MISMATCH")
    required_ids={*(f"E-{j:02}" for j in range(1,8)),
                  *(f"R1-{j:02}" for j in range(1,8)),
                  *(f"R2-{j:02}" for j in range(1,9))}
    gate({str(z.get("id")) for z in comments if isinstance(z,dict)}==required_ids,
         "ORIGINAL_REVIEWER_ITEM_COVERAGE_INCOMPLETE")
    seen=set()
    for item in comments:
        if not isinstance(item,dict):
            blocks.append("REVIEWER_ITEM_INVALID");continue
        rid=item.get("id")
        gate(isinstance(rid,str) and bool(REVIEW_ID.fullmatch(rid or "")),"REVIEWER_ID_UNATTRIBUTED")
        if rid in seen: blocks.append("DUPLICATE_REVIEWER_ID")
        seen.add(rid)
        if provider_verified:
            gate(item.get("source_document_sha256")==matrix.get("source_document_sha256"),
                 "REVIEWER_SOURCE_DIGEST_LINEAGE_MISSING")
        else:
            gate(item.get("source_status")=="USER_PASTED_EDITORIAL_EMAIL_BODY",
                 "REVIEWER_USER_TRANSCRIPT_PROVENANCE_MISSING")
            gate(item.get("source_document_sha256") is None,
                 "UNVERIFIED_SOURCE_MUST_NOT_HAVE_ASSERTED_HASH")
        gate(item.get("requirement_style")=="FAITHFUL_PARAPHRASE_NOT_LITERAL_QUOTE",
             "REVIEWER_PARAPHRASE_STATUS_MISSING")
        gate(isinstance(item.get("source_locator"),str)
             and bool(item.get("source_locator")),
             "REVIEWER_SOURCE_LOCATION_MISSING")
        gate(isinstance(item.get("requirement_text"),str)
             and len(item.get("requirement_text","").strip())>=16,
             "REVIEWER_REQUIREMENT_TEXT_MISSING")
        gate(item.get("verified_against_source") is True,
             "REVIEWER_ATTRIBUTION_NOT_VERIFIED")
        gate(bool(item.get("g2_action_id")),"REVIEWER_ACTION_LINK_MISSING")
        gate(bool(item.get("g5_section")) and
             item.get("g5_section")!="G5 section to be assigned after analysis",
             "REVIEWER_MANUSCRIPT_SECTION_UNRESOLVED")
        gate(bool(item.get("g6_response_id")),"REVIEWER_REBUTTAL_ANCHOR_MISSING")
    gate(matrix.get("reviewer_comment_coverage_verified") is True,
         "ALL_REVIEWER_COMMENTS_NOT_COVERED")

    topics=matrix.get("provisional_concerns",[])
    gate(isinstance(topics,list) and len(topics)>=10,"PROVISIONAL_ANALYSIS_INVENTORY_INCOMPLETE")
    if not isinstance(topics,list):topics=[]
    tid=set()
    for item in topics:
        if not isinstance(item,dict):
            blocks.append("PROVISIONAL_ITEM_INVALID");continue
        id=item.get("id")
        if id in tid:blocks.append("DUPLICATE_INTERNAL_Q_ID")
        tid.add(id)
        gate(item.get("disposition") in DISPOSITIONS,"INVALID_G3_ANALYSIS_DISPOSITION")
        gate(bool(item.get("existing_evidence")),"G2_ITEM_WITHOUT_EVIDENCE_OR_RATIONALE")
        gate(bool(item.get("g5_target_section_draft")),"G5_SECTION_UNASSIGNED")
        gate(bool(item.get("g6_rebuttal_anchor")),"G6_RESPONSE_UNASSIGNED")
        if item.get("source_authority")!="SUPPLEMENTARY_INTERNAL_REPRODUCIBILITY_EVIDENCE":
            gate(bool(item.get("authentic_reviewer_ref")),
                 "REVIEWER_TOPIC_MAPPING_MISSING")
            gate(item.get("complete_in_actual_reviewer_letter") is True,
                 "G2_TOPIC_REQUIREMENT_NOT_COVERED")
        else:
            gate(item.get("id")=="Q-01",
                 "UNMAPPED_SUPPLEMENTARY_TOPIC_NEEDS_REVIEW")
        action=item.get("g3_execution_status","")
        gate(any(str(action).startswith(x) for x in ALLOWED_G3_PREFIXES),
             "UNKNOWN_G3_AUTHORIZATION_STATUS")
        if item.get("disposition") in (
            "EXPLORATORY_POST_OUTCOME_CONDITIONAL",
            "EXPLORATORY_IF_AUTHENTIC_BASELINE_EXISTS"):
            # Exploratory: either a fully pinned analysis spec
            # or a source-verified NOT_EXECUTABLE justification.
            spec=item.get("frozen_g3_experiment_spec_sha256")
            no_run=(
                str(action).startswith("NOT_AUTHORIZED") and
                bool(item.get("justified_not_executable"))
            )
            gate(bool(SHA.fullmatch(spec or "")) or no_run,
                 "G3_EXPLORATORY_SPEC_OR_NONEXECUTABLE_JUSTIFICATION_MISSING")
    gate(matrix.get("all_g3_analyses_specified") is True,
         "ALL_G3_ANALYSES_NOT_PREDECLARED")
    gate(bool(matrix.get("revision_protocol_freeze_commit")),
         "PROTOCOL_FROZEN_COMMIT_NOT_SET")
    if not matrix.get("actual_editor_letter"):
        notes.append("Original editor/review reports not included; no inferred review points allowed")
    notes.append("Source content is user-provided; if an original email file later becomes available, preserve and hash separately without overwriting the transcript source.")
    notes.append("This check cannot independently verify journal mail authenticity or scientific source access.")
    return sorted(set(blocks)),notes

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--matrix",required=True)
    ap.add_argument("--protocol",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    dest=Path(args.out).expanduser()
    if dest.exists():ap.error("Refusing to overwrite an earlier freeze-preflight report")
    matrix_p=Path(args.matrix).expanduser()
    protocol_p=Path(args.protocol).expanduser()
    matrix=json.loads(matrix_p.read_text(encoding="utf-8"))
    protocol=protocol_p.read_text(encoding="utf-8")
    problems,notes=verify(matrix,protocol)
    output={
        "schema_version":"dtrm.ic.g2.freeze_preflight.v0",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "case_id":CASE,
        "status":"G2_FREEZE_GATE_BLOCKED" if problems else "G2_FREEZE_SCHEMA_READY_REQUIRES_MANUAL_SCIENTIFIC_SIGNOFF",
        "matrix_sha256":sha(matrix_p),
        "protocol_sha256":sha(protocol_p),
        "blocking_codes":problems,
        "reviewer_items_listed":len(matrix.get("actual_reviewer_comments",[])),
        "internal_topics_listed":len(matrix.get("provisional_concerns",[])),
        "human_review_required":True,
        "this_script_never_authorizes_g3":True,
        "notes":notes,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G2:",output["status"])
    print("User-supplied editorial/reviewer requirements traced:",output["reviewer_items_listed"])
    print("Provisional internal topics:",output["internal_topics_listed"])
    print("Blocking gates:",len(problems))
    for b in problems:print(" BLOCK:",b)
    print("Report:",dest)
    print("No original science data, prices, targets, fitted models or G3 computations accessed")
    return 0 if not problems else 2

if __name__=="__main__":
    try:raise SystemExit(main())
    except Exception as exc:
        print("G2 freeze preflight HALTED:",type(exc).__name__,exc,file=sys.stderr)
        raise SystemExit(3)
