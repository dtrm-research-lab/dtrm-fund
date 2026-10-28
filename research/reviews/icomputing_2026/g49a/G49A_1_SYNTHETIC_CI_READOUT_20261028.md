# G4.9a — First execution: synthetic authority-mechanism CI readout

**Case:** ICOMPUTING-D-26-01069 | **Run date:** 2026-10-28  
**Protocol was committed BEFORE source / data / test execution:** `6e77f2a2b7d5667c21d275cc25d7b1143c95c335`.  
**Evaluated implementation commit:** `02f076e7babc7d08f6505a44ba15a649060bd899`.  
**CI (separate source-only workflow):** `https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40763313090`.  
**Repository full test workflow:** `https://github.com/dtrm-research-lab/dtrm-fund/actions/runs/40763312962` — SUCCESS.
**Status: ENGINEERING SOFTWARE PILOT PASS / HUMAN-AUTHORITY SCIENCE NOT TESTED.**

## Immutable run facts (GitHub Actions stdout, not manual observations)

- Exact standalone unit tests: **25/25 OK**.
- Synthetic decision cases: **12**, all predetermined in `g49a_synthetic_cases.json`.
- Arm×case rows: **36** (12 per A/B/C).
- Matched-policy selection assertions: **36**.
- Shared hard guard breaches: **0**.
- Internal SHA256 of scenario cases: `5c783b478fcab7c0dc8b5fb1a33f8d67588c9917a6e613302f0e3ed54f850a9c`.
- Report canonical JSON digest: `c12337322b9f5c2b0b645d1f9b9300211b8d2f03a0ecdc4b7f3a577691983b1c`.
- Actual report file SHA256: `80ae0a3293138af0067334c76894d92b4475f27f4a9652ab4e701c352a36baae`.
- Protocol file SHA256: `38e016fb57146ed0bdbda0feae7f26c5794f954694ea30f199c16f71d9fcfe8e`.
- Engine file SHA256: `dbd38134a29d22ada4a4b75704cf018c5f7183ac25cae46d25503c20aeaeb768`.
- Fixture file SHA256: `38a46555e360d4ef405fee0aa05160b12e0fe6ea16db86e2b866ba87dfa18f11`.
- Action artifact: `G49A-SYNTHETIC-MECHANISM-NOT-HUMAN-EXPERIMENT`, retention 30 days.

## Full reported statuses, no cherry-picking

| Arm | EXECUTE | ABSTAIN | DENY (all reasons) | Logical checks |
| --- | ---: | ---: | ---: | ---: |
| A_DELEGATED: deterministic agent-policy stub | 10 | 1 | 1 (out-of-menu policy) | 12 |
| B_APPROVAL: scripted approval, NOT a real person | 5 | 1 | 6 (bad policy, expiration, no approval, record mutation, revocation, wrong context) | 23 |
| C_DIRECT: scripted direct choice, NOT a real person | 6 | 1 | 5 (expiration, no approval, record mutation, revocation, wrong context) | 24 |

**Do NOT present 10 versus 5 actions as a difference in utility or human safety benefit.** The arms intentionally differ in authorization preconditions and the refusal counts are an expected mechanical outcome, not independent evidence of better judgment. The `checks` column is literally branches/checks counted in a synthetic program, **not elapsed latency, money, human effort or compute resources measured**.

## Transparent remediation audit

First workflow attempt `40763243588` failed **1 of 25** tests on an expected count of authorization checks (`24` expected for B vs `23` observed). The engine rejected a deliberately malformed agent proposal **before** performing the approval check. The only change was to correct that test expectation to **23**, reflecting the real early-deny path; **no** policy, hard guard, selection or authorization logic was modified to force a PASS. Successful rerun `40763313090` had 25/25 PASS. Both failing and passing runs are retained in Actions history.

## Measured engineering contract only

- Same candidate scores/flags and policy menu for all scripted arms.
- A common *hard guard* forbids unverified, blocked, and risk > 5 cases.
- A `balanced`, `cautious`, or `open` policy further restricts admissibility.
- Scripts can approve a different menu rule than the agent proposed.
- Missing, revoked, expired, case-mismatched and content-digest-mutated **scripted trusted approval** records prevent action in B and C.
- Lower-trust injected text is ignored by all arms, but **no live LLM or active real attacker** was tested.
- Exact same policy + candidate list produces same deterministic choice (matched-policy code invariant).
- No financial input or real human participant was present.

## Essential scientific/security limitations and red-team objections

1. **This is NOT a randomized human-vs-AI experiment.** Both 'human' policy authorizations and 'agent' proposals are deterministic scripts, not observations of human and autonomous agent behavior.
2. **Hash is NOT authentication.** The content SHA detects an un-recomputed mutation; anyone with the ability to forge a whole trusted authorization record can recompute the hash. There is no separately secured identity provider, authorized signer, real human consent, nonce/replay-resistant proof, or deployed permission infrastructure. The prototype validates only the internal trust assumptions, not security against an adversary holding that trusted control.
3. **No prospective utility / economic comparison.** Synthetic scores are not 60-day stock returns, financial benefit, outcomes from purchases, or reported user satisfaction.
4. **No observed contestability or fairness.** Ability to set/revoke a scripted policy is a mechanical affordance; no individual actually contested a decision.
5. **Hard safety is equal across arms.** Denial frequency is not a common externally adjudicated outcome demonstrating superiority of one arm; no p-values or confidence intervals are justified for 12 hand-designed fixtures.
6. **No trade/purchase or LLM.** Prompts, latency, operational cost and cyber attack resilience are not measured.
7. **Pre-execution specification is engineering preregistration**, not an external prospective causal trial or proof of generalizability; scenarios and tests were authored together before execution.

## Current decision

**PASS for:**
- offline deterministic synthetic mechanism, 25 tests, 12 scenarios/36 rows, shared hard-rule enforcement, source/report hashes and fail-closed scripted approval cases.

**NOT PASS / NOT CLAIMED:**
- actual human authority, behavioral control advantage, human/AI utility parity or noninferiority, security against credential forgery, market profits, journal-level methodological novelty, G4 full scientific gate, or inclusion in final G5 Article as a validated human effect.

**Next stage recommended:** independent code-security adversarial audit of provenance boundary; mock auth issuer separated from downstream planner; instrument real approvals and measurable outcomes in a new consented prospective study. Before any inclusion in current *Intelligent Computing* revision, decide if this software contract adds sufficient genuine novelty compared with standard authorization gates. It may be useful solely as implementation/supplementary proof and not justify a new paper claim.

To reproduce without network and without any original financial data:
```bash
python3 -m unittest discover -s tests -p 'test_ic_g49a_mechanism.py' -v
python3 research/reviews/icomputing_2026/g49a/g49a_run.py \
  --out /tmp/G49A_SYNTHETIC_MECHANISM_REPORT.json
```

This report is an honest synthetic technical pilot, **NOT** evidence that humans control autonomous systems without a performance cost.
