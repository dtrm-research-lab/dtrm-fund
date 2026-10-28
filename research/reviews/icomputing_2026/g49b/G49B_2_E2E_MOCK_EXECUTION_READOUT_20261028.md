# G4.9b — Fully simulated keyboard session: independent CI execution audit

**Date:** 2026-10-28. **Scientific protocol:** `7fbf67314f39f2bc7b9e34958dd3cbb38341ff3d`.
**Execution source:** `97b1820edfbff710baeb2c8d94ed18fafdfd53bb`.
**Status:** **E2E MOCK PASS / REAL HUMAN PILOT NOT STARTED**.

## Why this run exists

The author requested that the pilot be executed without access to their personal computer.
The repository could not be cloned into the assistant's isolated container due to DNS
restrictions, so an extra **full mock-input terminal regression** was committed to the
connected GitHub repo and executed on GitHub-hosted CI, with reproducible stdout logs.

**DO NOT count mock terminal events as real participants.** The test explicitly labels
the session as simulated, uses a transient temp directory, mocks the TTY and responses,
audits the resulting record, withdraws the fake session and deletes the entire temp
directory. No real data were collected, no external orders executed.

## Exact checked runs

- Isolated G4.9b workflow `40769897151` on commit `97b1820edfbff710baeb2c8d94ed18fafdfd53bb`: **SUCCESS; 38/38 tests OK**.
  https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40769897151
- Full repository suite `40769897177` on the same source commit: **SUCCESS**.
  https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40769897177
- Full repository suite `40769906987` on the same source commit: **SUCCESS**.
  https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40769906987
- New test: `tests/test_ic_g49b_e2e_mock.py` (five additional mock-only cases).

## End-to-end lifecycle verified in CI

1. Create operator-local private key in a temporary private directory.
2. Provide *mocked*, explicitly synthetic YES to both consent and 18+ eligibility.
3. Derive six B approval and six C direct-choice cases from the same frozen 12-case
   stimulus pool under one pseudonymous local session.
4. Provide simulated typed approval, policy change or refusal inputs for all 12 cases.
5. Check issuance/binding of 12 HMAC-based decision events, enforcement by existing
   deterministic selector, and the shared hard guard.
6. Confirm a private `0600` session JSON is created outside GitHub repo and
   contains the 12 task observations and no unexpected free-text identity fields.
7. Run the private auditor and verify it returns 12 rows, all assignment records,
   choice tokens and paired score proxy comparisons.
8. Withdraw/delete the mock record and verify the local auditor returns **0 sessions**.
9. Separately verify NO consent, NO adult eligibility and QUIT before completion
   produce **zero** complete participant session files.
10. Reject non-TTY automatic enrollment from the real CLI unless a mock/test double
    explicitly simulates a terminal. This blocks unattended CI from silently
    self-enrolling fake 'humans'.

Actual CI evidence (literal stdout flags):

```text
Ran 38 tests in 0.041s
OK
G49B_E2E_MOCK_ONLY_CONSENT_12_TASKS_AUDIT_WITHDRAW_PASS
G49B_E2E_MOCK_ONLY_NOT_ADULT_NO_RECORD_PASS
G49B_E2E_MOCK_ONLY_NO_CONSENT_NO_RECORD_PASS
G49B_E2E_MOCK_ONLY_WITHDRAW_MID_TASK_NO_RECORD_PASS
G49B_MOCK_CI_ONLY_NO_REAL_PARTICIPANTS
```

## Adversarial qualification

- A is still a deterministic policy stub, **not** a general-purpose autonomous model.
- B/C inputs in this smoke-test are fixtures, **not actual human responses**.
- HMAC verifies local record integrity against one operator key; the same operator
  could fabricate a session. No independently authenticated human actor, consent
  verifier, outside trusted issuer, external adversarial credential protection or
  deployed authorization service exists.
- Terminal response elapsed times in a mocked CI run do **not** represent real
  human cost or cognitive burden.
- Score proxies are simulated rankings. No prospective payoff/utility, realized
  trading return, user welfare or noninferiority is tested.
- The scripted fixture is predeclared for engineering assurance; passing it
  demonstrates conformity with the tested mechanism but **not novelty above
  existing decision-authorization designs**.
- Real voluntary human enrollment, privacy/ethics review and independent field
  assessment remain separate author-controlled future work.

## Gate verdict

**G4.9b software release E2E = MOCK PASS**.

**G4.9b real-person feasibility pilot = NOT STARTED / N=0 observed by this study**.

**G4 original Intelligent Computing novelty/reviewer gate = OPEN**.

Do not merge this readout into a manuscript sentence stating that humans have
been studied experimentally. For publication, human-intervention results require
real consenting and independently documented participant observations plus an
appropriate protocol. The work can support only a technical implementation
readiness claim at this stage.
