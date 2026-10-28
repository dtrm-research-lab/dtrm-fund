# G4.9b — Consented human-authority pilot (protocol recorded BEFORE any participant observation)

**Case:** ICOMPUTING-D-26-01069 | **Date:** 2026-10-28
**Research stage:** G4.9b PROTOCOL / ENTRY ONLY, no recruited participants, no observed human responses, no inference.
**Parent G4.9a:** `research/ic-g4-9a-mechanism-pilot-20261028`, synthetic 25/25 tests / 12 cases.
**Branch:** `research/ic-g4-9b-human-consent-pilot-20261028`.
**User's scientific question:** Does *actually preserving policy decision authority* have an observable operational cost and opportunity to correct agent policy proposals?
**Important:** This pilot cannot establish economic noninferiority, human superiority or broad field validity. No positive results are presupposed.

## Design and eligible participants

Voluntary **adult (18+)** participants only. Consent must be actively acknowledged at runtime, not simulated. No medical, financial account or identity data are solicited. The participant uses an offline interactive terminal to choose among three identical public policies with synthetic candidates and scores. No trades, payments, network queries, financial forward targets, or third-party customer data. Researchers must conduct an appropriate ethics/consent review *before real enrollment*. No claim of IRB approval.

Real arm attribution is based on **self-attested direct interactive keyboard responses**, not an identity-verification system; an operator can impersonate a person and all sessions remain self-reported. Neither tests nor samples produced by code are real people.

The initial convenience pilot is **feasibility/descriptive**; a planned larger trial with justified recruitment, randomization, sample size, independent source of task outcomes and power would be needed to make causal/noninferiority claims. No numbers of people are declared before consenting individuals actually participate.

## Stimuli and arms

A shared pool of 12 synthetic tasks based only on the existing G4.9a candidate/risk/provenance information, with **no pre-scripted human choices or failure modes shown as participant prompts**. No outcome truth or future alpha is available. The primary visible performance proxy is the *model's displayed score*, not true decision utility.

Policy menu identical in each arm: `cautious` risk<=2; `balanced` risk<=4; `open` risk<=5. Mandatory hard veto: verified AND not blocked AND risk<=5. The hard veto may not be lifted by participants.

- **A_DELEGATED_SHADOW:** a documented deterministic **agent-stub** always proposes the predeclared `balanced` policy, except where an invalid proposal was frozen in the original G4.9a fixture. A is computed in background on the identical case, not an LLM or an independently optimized autonomous rival.
- **B_APPROVAL_REAL:** a consenting participant sees the agent stub's proposed policy and explicitly **approves, changes to another menu policy, or refuses**. A real keyboard decision must be recorded; then the deterministic policy engine acts, with a local HMAC-authenticated approval record.
- **C_DIRECT_REAL:** a consenting participant **chooses** a policy or refuses without being shown the stub proposal; then the same deterministic policy engine acts under a local HMAC-authenticated approval record.

Each session receives 12 cases, **6 B and 6 C**, shuffled reproducibly using HMAC-derived participant-specific seed and balanced by a fixed within-session crossover; the same candidate list is not shown twice in one session. The A shadow comparison is always the *same case* and information but no independent agent cognition. This design is susceptible to carryover and case-difficulty effects: descriptive feasibility pilot only, no causal attribution.

For abstentions, the terminal must visibly offer a no-action option rather than silently filling capacity. The choice is `approve`, `policy change`, or `decline` in B; `policy choice` or `decline` in C. An invalid policy must fail closed.

## Predeclared technical metrics (not confirmatory statistics)

- Total sessions actually saved with consent, per-arm task counts, script-proposal approvals, human modifications, refusals, policy-validation failures, final EXECUTE/ABSTAIN/DENY, shared hard-risk/provenance breaches.
- Difference in mean selected **displayed rank score** between actual policy and A stub for *paired same cases*, including explicit missing/abstained counts and no posthoc exclusion. These are not verified user outcomes.
- Additional elapsed **human interaction time** from monotonic clock per decision; do not describe as whole-process or monetary cost. Session records don't capture external thought and time usage.
- Matched-policy invariant: when actual approved policy equals A shadow's policy and both execute, selected candidate must be identical (same deterministic source).
- Contestability measure: share of genuine B human *changes/refusals* and whether enforced; it is an interaction **affordance**, not proof that those edits were beneficial.

No p-values, confidence intervals, equivalence margins, inferiority/superiority claims, participants' predictive skill, causal treatment comparison or published effectiveness claim based on this tiny convenience study. Report selection and nonresponse transparently.

## Consent, privacy, integrity and operational boundaries

1. Display full disclosure at enrollment; require *explicit* `YES` opt-in and an adult eligibility confirmation. A blank/default answer is NO. Exit with **zero** saved participant data if either fails.
2. Do not request participant name, email, contact, investment preferences, or free-form narrative. Generate random pseudonymous session ID locally.
3. Save per-session JSON under an explicitly operator-owned private location **outside the repository**, with `0600` mode and no cloud upload; never publish individual-level data. Provide a withdrawal command to delete own local session. Privacy obligations and lawful basis must be reviewed by the study organizer before recruiting.
4. Authentication integrity: operator provisions a random HMAC key **outside the repository**; after a participant types a choice the local trusted issuer signs a context-bound event (session/case/arm/policy/time/decision) and downstream verification rejects altered signatures and mismatched case/arm, unauthorized policy, expiration and missing token. This is NOT identity proof or a hardened deployed multi-party authentication service; an operator with key/process control can forge events, and revocation/expiration are limited to the local context.
5. Agent and participant see only task information and the shared menu; the secret HMAC key is never displayed. HMAC records alone cannot certify an actual independent participant. No programmatic scripted human decisions may be mislabeled as actual human evidence.
6. No real external action; engine selects **synthetic candidate IDs** only.
7. Store report counts and source lineage, not participant raw logs in GitHub; never upload HMAC secrets.
8. Explicit human safety concern: a recruited participant must be free to exit without penalty; if interrupted, do not persist incomplete session as completed. Withdrawing requires local removal AND any previously copied data according to consent notice.

## Go / No-go and manuscript boundary

**G4.9b READY FOR RECRUITMENT** only if: (a) code/tests and deterministic mock input replay pass independent CI; (b) offline live terminal path is manually reviewed, including consent opt-out, withdrawal, malformed/prompt injection and HMAC context binding; (c) researcher reviews ethics, recruitment, data minimization and disclosure; (d) external participant recruitment/consent actually takes place.

**G4.9b PILOT COMPLETED** only when consenting adult sessions have actually been collected and independently checked without using synthetic CI responses as participants; report *N*, missing/withdrawal data and all adverse or inconclusive findings.

**Scientific article claim:** may say only 'a bounded consented usability/feasibility pilot was undertaken' if completed, with proper sample/setting and without equivalence or behavior generalization. Otherwise call it unexecuted future work, not current original research.

**Not a new preregistered market-outcome study.** Historical G2/G3 frozen science remains unchanged.
