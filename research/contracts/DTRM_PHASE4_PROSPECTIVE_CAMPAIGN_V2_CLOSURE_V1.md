# DTRM Phase IV — Prospective Campaign v2 Closure v1

**Status:** outcome-blind decisive failure; no downstream scientific unlock.

## Purpose

Close the activated campaign `phase4-prospective-capture-2026-09-18-v2` under the adequacy rules frozen before capture. This closure uses only source-value-free operational metadata. It does not inspect article content, market outcomes, model performance, MM1 decisions, portfolio values, or any treatment effect.

## Frozen rule

The registered adequacy contract requires:

- 56 target slots over 14 UTC days;
- at least 48 `ACCEPTED` slots;
- scheduled attempt 1 only;
- start lag no greater than 120 minutes;
- no backfill and no threshold relaxation.

A slot whose eligible run begins more than 120 minutes after its target is `LATE` and cannot be accepted.

## Decisive evidence

The recovered source-value-free excerpt contains 42 complete slot records spanning slots 10–52, with slot 50 absent from the excerpt. Every recovered record:

- binds the approved activation statement and SHA-256;
- uses the frozen workflow path/blob/identity;
- uses backend commit `bf844932f8bb3e6773c329a45135fd754c6d8342` and tree `c090c3cb41165ee513de812dec562f497407df62`;
- uses request fingerprint `932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`;
- is a scheduled attempt 1;
- reports capture status `SUCCEEDED`;
- has raw-evidence and temporal-index SHA-256 digests;
- begins more than 120 minutes after its target.

Observed start-lag range: 155.401167 to 463.111860 minutes, median 290.845191 minutes.

Therefore at least 42 of 56 registered slots are irrevocably `LATE`. Even if every unobserved slot were accepted, the maximum possible accepted count is:

`56 - 42 = 14 < 48`

The adequacy gate is therefore mathematically impossible to pass. Full reconstruction of the remaining slots is not required to determine the final campaign result.

## Final status

`FAIL_PROSPECTIVE_EVIDENCE_ADEQUACY_V1`

Failure class: `OPERATIONAL_SCHEDULER_LATENCY`.

This is not classified as a provider-capture or temporal-index failure. The recovered records report successful bounded capture and derived-index production; the failing invariant is the preregistered schedule-lag bound.

## Scientific consequence

This campaign does **not** unlock confirmatory Temporal State history construction, outcome access, Temporal State outcome fitting, MM1 execution/evaluation, Phase III mutation, or public raw-provider redistribution.

The following are explicitly forbidden:

- retroactive backfill;
- reassigning target timestamps;
- relaxing the 120-minute bound for v2;
- counting late v2 slots as accepted;
- using v2 evidence as the confirmatory evidence set.

The v2 artifacts remain immutable operational evidence and may be used only for outcome-blind engineering diagnosis and exploratory source-quality work consistent with provider rights.

## Superseding campaign

A new campaign requires a new preregistration. Its scientific hypothesis, Phase II control, frozen Phase III/MM1 policy, request fingerprint, provider roles, source schema, target count, minimum accepted count, and 120-minute capture-lag bound remain unchanged unless separately justified and preregistered.

The operational replacement must remove GitHub `schedule` event generation from the counting clock. The replacement design is specified separately in `DTRM_PHASE4_PROSPECTIVE_CAMPAIGN_V3_OPERATIONAL_REPLACEMENT_V0.md`.

## Evidence

Canonical source-value-free decisive-failure evidence:

`research/evidence/phase4_prospective_campaign_v2_decisive_failure_v1.json`

SHA-256:

`21d3e984ded3adcf20247ad08a99264965ae21218e50b07fd87a5cf6aa6aa722`
