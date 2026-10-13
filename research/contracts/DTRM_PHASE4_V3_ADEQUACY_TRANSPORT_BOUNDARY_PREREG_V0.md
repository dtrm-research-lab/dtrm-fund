# Phase IV v3 — Scientific adequacy transport boundary v0 (preregistration)

**Status: PREREGISTERED_BEFORE_IMPLEMENTATION; RESEARCH-ONLY; NO CAMPAIGN ACTIVATION.**

Scientific parent: `research/phase4-temporal-state` at merge commit `7f45b0a8c2a64b7620098544d79a492f63d474aa` (scientific PR #30).
Linked exact scientific antecedents:
- PR #21, audited 56-slot source-evidence v1, `6e5b73b971a26db28c10802852bc82d38b0b8b61`
- PR #28, prospective campaign v2 failure + v3 operational replacement, `4e1b0eed4cb8228703fa731dfb8621bd1bfd008e`
- PR #29, successful source-value-free **non-counting** `repository_dispatch` diagnostic, `b244d313eeacbb54c702049ecc5b7812016bdee1`
- PR #30, dormant EventBridge Scheduler → Lambda → DynamoDB conditional claim → signed GitHub `repository_dispatch` v3 design, `7f45b0a8c2a64b7620098544d79a492f63d474aa`.

## A concrete scientific boundary gap, not a new adequacy rule

The **authoritative merged v1 adequacy auditor** `src/dtrm/phase4/prospective_evidence_adequacy.py` is outcome blind and correctly requires **56 opportunities, ≥48 accepted, ≥1 accepted on first and last UTC day, no backfill, no early closure, fixed UTC timestamps and lag/duration limits**. In `audit_evidence`, events other than `schedule` are deliberately ignored and classified as noncounting; its `SlotAttempt` constructor *rejects* target/cron/workflow fields on non-`schedule` records. In contrast v3's preregistered counting event is an authenticated `repository_dispatch`, and `schedule` must be noncounting in v3.

**Thus the V1 audit cannot be used unmodified to certify a v3 campaign.** The historical v1 audit is correct for v1/v2; it must not be silently broadened or have `repository_dispatch` relabeled as `schedule`.

## This increment's allowed scope

1. Register the transport-compatibility gap before any new implementation or v3 campaign evidence.
2. Add a **synthetic regression** that a v3 `repository_dispatch` attempt *with no source values and no target fields* remains noncounting under the unmodified v1 auditor. A different synthetic event `schedule` stays bound to the v1 meaning. This demonstrates why a separately preregistered v3 evidence/authority adapter is necessary.
3. Extend only the scoped offline quality workflow to execute the new test. No configuration of schedule triggers, secrets, provider access, AWS calls, outcomes, MM1 evaluation, history construction or activation statement.
4. Do NOT implement a v3 **positive acceptance** predicate in this increment. A Boolean field such as `authenticated=true` self-asserted in a JSON record is not independently verified authority and must not confer acceptance.

## Follow-on positive v3 auditor specification — design only, NOT implementation/permission

Before v3 can count any actual observation, separate preregistration, code and review must bind:
- exact future v3 activation-statement bytes and **separately trusted** expected ID/digest;
- authenticated HMAC `repository_dispatch` envelope and runtime GitHub event/run/workflow identity, provenance to the exact frozen backend commit/tree and v3 repository workflow blob;
- provider-neutral *actual* scheduler identity and conditional DynamoDB claim with **independently captured source-value-free evidence**, not a synthetic claim;
- target slot [0,55] and target timestamp consistent with 14×4 UTC clock geometry, start lag measured from target to actual validated capture start ≤120m;
- duration ≤60m; completion ≤180m; immutable record publication ≤60m; exact request fingerprint/provider roles/schema/writer/credential authority; raw+index digest presence and identity;
- only `run_attempt == 1`; unique target/run identity; duplicate/retried claims **fail closed**, never backfill;
- v3 `schedule`, manual triggers, diagnostic runs and legacy campaign events are **noncounting**;
- ≥48 accepted including first+last day; closure only after the fixed end-of-window finalization clock; no provider-content access or outcome/MM1 dependence.

A dispatch receipt or successfully demonstrated 16.8-second diagnostic **does not** prove the full v3 scheduler or scientific data sufficiency. The positive v3 bridge must be explicit, outcome-blind and independently reviewed. All scientific counting, outcome access, Temporal State fitting, MM1 execution, AWS provisioning and activation permissions remain **false**.

## Frozen tests and gates

Synthetic test: exact v3 event is ignored by unchanged v1 audit; no accepted slots; before finalization PENDING, after finalization FAIL; `ignored_nonscheduled` increases; zero provider/outcome/MM1 access. Reject malformed v3 attempts with target fields instead of quietly relabeling them. Scoped pytest and Ruff/format, scientific inherited Phase III source-preservation and exact-head Codex before any merge. No merge without separate authorization; no activation or cloud writes by this PR.
