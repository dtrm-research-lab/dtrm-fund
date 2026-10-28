# G4.9b — Local operator handbook, privacy gates and bounded scientific language

**Case:** ICOMPUTING-D-26-01069 | **Pilot:** human decision-authority feasibility | **Date:** 2026-10-28
**Status:** IMPLEMENTATION UNDER CI; **NO RECRUITMENT OR HUMAN OBSERVATIONS REPORTED BY THIS REPOSITORY**.
**Protocol commit (before code):** `7fbf67314f39f2bc7b9e34958dd3cbb38341ff3d`.
**Technical parent:** G4.9a (scripted three-arm synthetic mechanism), **not a new release of frozen G2/G3 finance code**.

## What the user/research organizer must do first

1. Review protocol `G49B_0_HUMAN_PILOT_PROTOCOL_PREEXECUTION.md` and participant notice in `g49b_pilot.py`. Conduct appropriate independent ethics/privacy review and define recruitment, retention/deletion and consent processes BEFORE recruiting anybody. Never imply that an institutional ethics committee has approved the study unless documented.
2. Participant must be a **consenting adult (18+)**. The CLI actively asks for consent and adult eligibility; NO and QUIT create no completed participant record. Do not use someone else's answers or claim synthetic tests are participants.
3. Keep all files **local** and outside the repository. Never upload raw sessions, HMAC key or other individual-level data to a public GitHub PR, email, ChatGPT or the revised journal supplement. Protect physical access to the device; pseudonymous ID is not full anonymity.
4. Initial convenience pilot is NOT powered for human-vs-agent statistical inference and **not** a noninferiority trial. A is a deterministic fixed stub, B/C require direct keyboard human input; no real market return or user welfare measured.

## Safe operator commands (macOS/Linux; no other libraries needed)

```bash
cd ~/Desktop/DTRM_Lab/dtrm-fund
git fetch origin research/ic-g4-9b-human-consent-pilot-20261028
git switch --detach 8fec1820a0629f835ebbc352315acc62b35c1b7d
python3 --version

PILOT="research/reviews/icomputing_2026/g49b/g49b_pilot.py"
AUDIT="research/reviews/icomputing_2026/g49b/g49b_audit.py"
PRIVATE="$HOME/.local/share/dtrm-g49b-private"

# Operator provisions protected local record-integrity key, ONCE:
python3 "$PILOT" --private-dir "$PRIVATE" init-key

# Each eligible adult can voluntarily enter a single 12-task session:
python3 "$PILOT" --private-dir "$PRIVATE" enroll

# Read-only local verification and aggregate summary. NEVER send raw sessions:
python3 "$AUDIT" --private-dir "$PRIVATE"

# A participant may exercise local withdrawal using their printed random code:
# python3 "$PILOT" --private-dir "$PRIVATE" withdraw --session-id <EXACT_32_CHAR_HEX>
```

**Note:** pin an actual reviewed final G4.9b commit SHA at operator start, not a moving branch. The example detached commit above was the initially tested base and must be refreshed against the final audited, passing PR head before real enrollment. The immutable protocol SHA is a separate earlier commit. If your original `dtrm-fund` folder has local changes, use a separate clean clone/worktree instead of switching its branch and losing state.

No runnable service, web collection endpoint, email address, contact list or consent form is created externally; the computer operator manages participation voluntarily, offline.

## Scientific observation types and interpretation

- **A_DELEGATED_SHADOW**: simulated deterministic policy choice. The participant does **not** make decisions in A. It is computed on the identical task and same synthetic candidate inputs.
- **B_APPROVAL_REAL**: person types ACCEPT, CHANGE or REFUSE on a stub-proposed policy.
- **C_DIRECT_REAL**: person types policy choice or REFUSE without seeing the stub proposal.
- **Outcomes**: a symbolic synthetic candidate choice, or ABSTAIN/DENY; displayed score is a model score-proxy, not utility.
- **Timing**: milliseconds from prompt activation to response within the terminal; not total work/human cognitive effort/cost.
- **Auditable mechanism**: HMAC-signed local choice events bound to session/case/arm/policy, protected key outside repository, refusal/expiry/replay checks. But same local trusted process issues and verifies the MAC; **no independent real identity or external actor authorization is proved**.
- **Audit:** read-only auditor replays original assignment, verifies consent/record HMAC, all choice-event HMACs, unique event nonces and scenario outcomes, and produces only aggregated counts and proxy deltas. An organizer with key can fabricate records; independent witness/recruitment custody remains essential if this will become human behavioral evidence.
- **Privacy:** exact prompts do not ask for names, contact details or narrative. The private JSON includes timestamps, choices and case IDs; protect it and delete on withdrawal, including other copies if any.

## Inference and publication red lines

Cannot claim from this pilot:
- 'Humans were statistically as good as autonomous agents'; A is not an LLM.
- 'No utility cost of retaining human authority'; synthetic scores aren't ultimate outcomes, and a volunteer convenience pilot is unpowered.
- 'Actual human control has been independently certified'; participation is self-attested.
- 'HDPG achieves better stock returns'; original financial G2/G3 data are not used here.
- 'Security has been proven'; HMAC is only a local trust-boundary prototype.

If `N=0` actual voluntary sessions, G4.9b remains **READY FOR CONSENTED PILOT**, not completed. Real people must explicitly participate after ethical assessment. If `N>0`, report N, selection/refusal/overrides, paired displayed-score proxies, participation burden, cases excluded/missing, limitations and exact protocol/source SHA. A pilot may identify feasibility issues; do not calculate noninferiority from its hand-curated cases.

## Next real scientific gate

G4.9c should demand separate assessor/blinding, robust issuer/participant credential separation, a non-synthetic autonomous model competitor, task utility outcomes established without using participants' predictions as ground truth, prospective justified delta, adequate recruitment/power and an ethics/privacy basis. Such work is a new protocol, not an automatic G5 result.

This handbook is intentionally executable but **is not a claim that participants have been enrolled**.
