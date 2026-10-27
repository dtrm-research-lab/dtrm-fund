# G2 checkpoint — technical matrix assembled, reviewer source still needed

**Date**: 2026-10-27
**Manuscript**: `ICOMPUTING-D-26-01069`
**Branch**: `research/ic-major-revision-2026`
**Stage**: `G2_ACTIVE_DRAFT_REVIEWER_SOURCE_REQUIRED`
**G3**: `BLOCKED`.

## Work performed in G2

1. Audited original stage handoff:
   `G1_TO_G2_STAGE_HANDOFF.md`, where G1 is closed **by documented
   limitation**, not by a newly successful independent holdout.
2. Read original historical `DTRM_XGB_PROBABILISTIC_PHASE2_STATS.yaml`
   plus V2/V3/V4 contracts from pinned source and reused G1.2k/m
   historical SHA values. The previously frozen relative P10
   cutoff is `-0.16665692627429962`, the calibration offset
   is `-0.06494169682264328`, original Top-K fraction 0.10,
   60-calendar-day excess-beta forward target. Old V1 absolute
   P10>0 feasibility remains **FAIL**, and ticker-bootstrap
   V2/V4 95% intervals cross zero.
3. Created `G2_REVIEWER_TRACEABILITY_PROVISIONAL.json`:
   ten provisional research topics Q-01 through Q-10 with
   explicit G3 action class, existing evidence, section
   destination, limit and placeholders for reviewer IDs.
   **No Q-topic is presented as a verbatim or authenticated
   reviewer objection.**
4. Created `ic_g2_freeze_preflight.py` to check original
   source/historical hash commitments, review-letter digest,
   stable reviewer identifiers, coverage count, G3 analysis
   specification hashes, G5/G6 destination pointers and
   protection of all negative/CI findings. A blocked preflight
   does not authorize G3.
5. Added `test_ic_g2_freeze_preflight.py`, nine metadata-only
   self-test cases covering absence of real source, mutation
   of P10 threshold, V1 failed feasibility, historical
   commitment hash mismatch, invalid reviewer attributions
   and unapproved exploratory analyses.

## Authentic reviewer source discovery (2026-10-27)

- Connected Gmail searches for case ID and Intelligent Computing
  major-review terms returned **FORBIDDEN** (provider access not
  authorized in this run). No mailbox data was read.
- Google Drive searches for `ICOMPUTING`, `Intelligent Computing`,
  `reviewer` and `major revision` identified older working
  papers and unrelated documents, **not a clearly identified
  2026 reviewer/decision letter**. Lack of results is not
  proof no such file exists.
- Project file-content searches (case ID and reviewer letter)
  returned no matches, with index incompleteness possible.
- Prior context mentions a major-revision decision, but
  **does not provide verbatim editor/reviewer reports**.
  The number and wording of original comments are therefore
  unverified; do not invent R1/R2 identifiers or responses.

## Closure blocker and next node

`G2_REQUIRED_AUTHENTIC_REVIEWER_SOURCE_UNAVAILABLE`.

Before freezing G2, acquire from authorized storage
the full manuscript review decision letter including
editor notes and **every** reviewer comment, with date,
source reference and SHA256. Do not publish personal
identifiers of peer reviewers or copyrighted reviewer
attachments in a public GitHub repository; use a
confidential local evidence bundle with a public
metadata-only hash and exact section/paragraph locators
(or a private repository branch, subject to consent).
Import actual reviewer IDs, numbered requirements,
and map each to a Q-topic or add a new requirement.

For any new G3 analysis of old already-inspected outcomes
freeze a fixed data-input digest, eligibility/exclusions,
comparator, estimand, preselected K grid/cost assumptions,
uncertainty/cluster strategy, random seeds, noncompletion
behavior, full reporting obligation and evidence label
`POST_OUTCOME_EXPLORATORY`. If no authentic comparators
or input snapshots are available, mark `NOT_EXECUTABLE`
with a source-grounded reason rather than 'pretend PASS'.

## Safe local preflight execution (no raw scientific inputs)

Run from the review checkout, after fetching new branch files:

```bash
cd "$HOME/Desktop/DTRM_Lab/dtrm-fund"
git fetch origin research/ic-major-revision-2026
git switch research/ic-major-revision-2026
git pull --ff-only origin research/ic-major-revision-2026

cd research/reviews/icomputing_2026
python3 -m unittest test_ic_g2_freeze_preflight.py -v

python3 ic_g2_freeze_preflight.py \
  --matrix G2_REVIEWER_TRACEABILITY_PROVISIONAL.json \
  --protocol G2_REVISION_PROTOCOL_DRAFT.md \
  --out "$HOME/dtrm-ic-audit/IC_G2_freeze_preflight_initial.json"
```

**Expected**: tests pass; preflight prints `G2_FREEZE_GATE_BLOCKED`
and exits 2. This is the **correct, intentional scientific
safety result**, not a script failure. It should list
`AUTHENTIC_EDITOR_DECISION_MISSING`,
`AUTHENTIC_REVIEWER_COMMENTS_MISSING`,
`EDITOR_SOURCE_DIGEST_MISSING`, reviewer coverage
and new-analysis specification blockers.
Do not rerun into same output path (script refuses overwrite).

If network/auth/local repo is unavailable, no need to run
this preflight to know G2 remains UNFROZEN. The public
status is already declared in the branch.

## G2 claim ceiling and deadline

Paper revision due **2026-11-25**. May/June historic
V2/V3/V4 effects are old outcome-consumed evidence.
Reproducing the old 390-input models, exact original
V1 date-selection mechanism and fixed P10 veto supplies
strong historical reproducibility, not new independent
efficacy. A late-October-2026 genuinely forward
60-calendar-day test cannot mature by the deadline;
do not fabricate new G1.3 cohorts from unit-test fixtures
or smartphone-shopping project outputs.

This stage can progress to freeze *without* a new temporal
holdout if the editor/reviewer objection map and a
scientifically honest analysis/limitation protocol are
complete. It cannot freeze with unauthenticated reviewer
requirements or unregistered new G3 analyses.

## 2026-10-27 SUPERSEDING STATUS — reviewer letter received in conversation

This runbook's earlier source-search FORBIDDEN/NOT FOUND
note is an **as-of-time record**, not a current G2
blocker. The manuscript author subsequently supplied
the **complete** editorial decision of 2026-10-26
including both reviewer reports in this chat.

The 22-item requirements matrix now contains 7 editor
actions, 7 internally reconstructed non-numbered
reviewer #1 themes and all 8 numbered reviewer #2
points. `ic_g2_freeze_preflight.py` has been
updated to recognize the explicitly identified
user-provided transcript without falsely claiming
an independently authenticated provider SHA.
It checks all 22 item IDs and their G5/G6 anchors.

**Remaining blockers are now primarily preanalysis
G3 plans and G2 manual signoff**, not source
access. If original journal email bytes become
available later, preserve and SHA-hash them as
a separate higher-assurance evidence record;
do not overwrite the current user-pasted
source attribution. The earlier literal 'nine'
test count is now superseded by **eleven**
unit-test cases in `test_ic_g2_freeze_preflight.py`.
`G2_FREEZE_GATE_BLOCKED` is still expected until
all conditional G3 analysis specs are signed.
