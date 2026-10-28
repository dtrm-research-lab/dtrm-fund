# G4.9a — Mechanism pilot: pre-execution protocol and scientific boundaries

Date: 2026-10-28. Editorial case: ICOMPUTING-D-26-01069.
Status at creation: **PRE-EXECUTION SPECIFICATION, NO PILOT OUTCOMES YET**.
Branch: `research/ic-g4-9a-mechanism-pilot-20261028` (separate from frozen G2/G3 source).
No original historical market data, pretrained proprietary model, live order, live purchase, connected human participant, or outcome label may be read.

## Objective and falsifiability

Test a **software-level mechanism**, not the human-vs-autonomous performance hypothesis:
Under identical synthetic ranked choices and an identical hard-safety boundary,
does a policy-authority gate (i) prevent executing unapproved or revoked/expired
policies; (ii) allow *authorized* changes to apply consistently; (iii) yield the
same selected outcome when policy, input and ranking are held equal; and
(iv) quantify additional **logical** authorization checks versus delegated rule
selection?

**Null/no-surprise outcome expected and allowed:** if the policy is identical,
the choice is identical. That is an implementation property, not a human advantage.
Other possible findings include a gate bypass, unauthenticated revision acceptance,
a policy mismatch, or a false refusal. Any such counterexample blocks release.
Do not curate failures away.

## Arms (mechanical simulations, not behavioral study)

- `A_DELEGATED`: a **deterministic stub**, not an autonomous LLM, picks one
  policy from a shared frozen menu inside the initial human-authorized mission.
- `B_APPROVAL`: the same stub proposes the same policy but execution requires
  an externally supplied **scripted** authorization record for the actual rule.
  Authorization may change the rule, refuse it, expire or be revoked.
- `C_DIRECT`: a **scripted human-choice surrogate**, not a real person,
  chooses from the identical policy menu; requires the same authorization gate.
- `M_MATCHED`: deterministic invariant: identical signed policy + data yields
  identical selected candidate regardless of a displayed controller label.
  This is an internal assertion, not another independent outcome arm.

**All arms:** identical candidates, scores, risk flags, policy menu, hard safety
requirements and selection engine. All operations run in memory; no network or
payment/trading connector. The common hard guard rejects unverified candidates,
blocked instruments, and risk > 5. The menu offers `balanced` (risk <= 4),
`cautious` (risk <= 2) and `open` (risk <= 5).
A deterministic tie-break sorts by score descending then candidate ID ascending.
A valid action chooses **one** candidate; none is an explicit `ABSTAIN`.

## Synthetic challenge classes frozen before evaluation

The fixture must cover normal selection, common hard-safety exclusion,
authorized stricter-policy choice, empty feasible set, missing approval,
revocation, expiration, attempted rule swapping, cross-case authorization
mismatch and malformed/out-of-menu rule request. Scenario identifiers and
candidate values are synthetic and nontradeable.

When `B_APPROVAL` has missing/revoked/expired/mismatched approval, no action may
be executed. It is expected for `A_DELEGATED` to act in the *same scenario*
under valid prior delegation, so **the count of refusals is not a fair
cross-arm evidence of improved external safety**. Report it as enforcement behavior.
No 'unsafe actions prevented' headline or observed human cognition inferred.

## Primary technical acceptance gates (not hypothesis testing)

1. Every test fixture produces deterministic output with identical bytes on re-run
   when timestamp and protocol version fixed.
2. No arm executes a candidate violating the common hard-safety invariants.
3. No B/C action without exact policy/case/version authorization, nor after
   revocation/expiration, even if an untrusted injection requests execution.
4. With identical approved policy and eligible candidates, A/B/C execution
   returns the exact same candidate (matched-policy invariant).
5. All scenarios are retained including `DENY`/`ABSTAIN`, with evidence of
   policies actually applied, shared inputs, counts of checks, and canonical JSON
   output with SHA256 digest.
6. Inputs fail closed on unknown policy, duplicate candidate IDs, invalid score,
   invalid risk, missing provenance, or unknown scenario/arm fields.
7. Run unit tests before pilot report; no relaxation after an adverse failure
   without documented protocol/code revision.
8. Review local report and code in independent GitHub Actions CI before calling
   an implementation smoke-test PASS.

## Quantities and forbidden interpretations

Descriptive counts by scenario/arm: `EXECUTE`, `ABSTAIN`, `DENY`;
common invariant violations; unapproved/misbinding overrides executed;
same-policy parity; and number of logical checks. These are **synthetic
software-check counts**, not monetary returns, welfare, measured latency, real
human-review effort, LLM quality or statistically estimated differences.
Do **not** compute a p-value/CI for this hand-designed fixture or select a
noninferiority margin from its outputs.

All scenario/controller selections are scripted. This *does not* measure the
causal effect of human control or validate the thesis that governance has
negligible utility cost. A later separately registered study would need
genuine consenting participants, comparable agents, randomized authority
rights, a prospectively justified noninferiority margin, enough observations,
and independent measurement of end-user outcomes/contestation.

## Freeze and reporting

Commit THIS protocol as a separate GitHub commit **before** committing the
executable implementation and running the fixture. Use that protocol commit
SHA in all implementation readouts. Treat the fixture and tests as predeclared
*engineering verification*, not a prospectively blind behavioral RCT.
Retain all failures. Do not touch the original frozen finance study.
G4.9a success permits only **technical feasibility** wording in the current
Intelligent Computing revision, subject to reviewer coherence and G4 approval.

Falsification: any accepted unapproved case, risk/provenance invariant bypass,
silently accepted untrusted policy mutation, inability to reproduce outputs,
or unequal matched-policy choice invalidates the mechanism smoke-test claim.
