# DTRM Phase IV — Post-merge prospective activation binding readiness v1

Date: 2026-09-14. Status: **PREREGISTERED_CANDIDATE_BEFORE_PERIODIC_ACTIVATION**.

This increment freezes the immutable facts that became knowable only after backend PR #90 was merged. It does not activate periodic capture, provision credentials, mutate storage, access outcomes, execute MM1, construct confirmatory history, fit Temporal State to outcomes, or mutate Phase III.

## Purpose

The next live Phase-IV action must eventually be authorized by an exact `dtrm.phase4.prospective_activation_statement.v2` statement. Before that statement can exist, the scientific repository needs a source-value-free, reviewable binding between the merged backend implementation and the still-unresolved operational authority evidence.

This readiness record is intentionally **blocked**. A later activation statement may only be constructed after every unresolved gate is evidenced and after a separate explicit human activation authorization.

## Immutable post-merge bindings

The following values are frozen by this increment:

- scientific parent commit before this increment: `6e5b73b971a26db28c10802852bc82d38b0b8b61`;
- scientific parent tree before this increment: `caafe2951dfd004245cba0f0a140bfd1c2748e07`;
- backend repository: `tech-com-UA00001/theresistance-back`;
- backend merge commit: `974a7a744642cc8268ca5972df4ef208f629ed2b`;
- backend merge tree: `0edcbca9d38b3a35b9b6a7b5fbb32b04d67119c9`;
- workflow path: `.github/workflows/phase4_fmp_news_temporal_capture_v1.yml`;
- workflow Git blob: `5ab8f5b2c7ca9d89f4bf613355d97ad5f12ffc2b`;
- workflow identity: `phase4_fmp_news_temporal_capture_v1`;
- ordered provider roles: `fmp_articles`, `general_latest`, `stock_latest`;
- registered request fingerprint: `932aef0ac257a9622562d2255a9c3c453ce43ab3f897bb3f0a6166192fcee9fd`;
- target activation schema: `dtrm.phase4.prospective_activation_statement.v2`.

`workflow_identity` is frozen here as the stable extension-free basename of the pinned workflow path. It is a scientific provenance identifier, not the human-readable GitHub Actions display name.

The backend commit/tree and workflow blob above are **dormant-lineage anchors only**. They identify the exact reviewed implementation from which the schedule-bearing revision must descend. Because adding `schedule:` necessarily changes the backend revision and workflow blob, these dormant identifiers MUST NOT be reused as the final scheduled-run provenance after that edit.

## Verified dormant workflow state

At the pinned backend merge, the workflow is `workflow_dispatch` only. The exact pinned workflow blob contains no periodic `schedule:` trigger. Therefore this increment cannot start the evidence campaign.

Adding or enabling a periodic schedule requires a separate backend increment. That increment must preserve the preregistered four daily cron opportunities, workflow path/identity, provider-role order, request fingerprint, source-value-free slot-record semantics and all downstream prohibitions.

## Required scheduled-revision addendum

Before any periodic activation, a separate scientific addendum MUST register the exact schedule-bearing backend revision produced by that backend increment. The addendum must bind, at minimum:

- the descendant backend commit and tree;
- the schedule-bearing workflow path, blob SHA and stable workflow identity;
- the exact four preregistered cron expressions;
- the ordered provider roles;
- the registered request fingerprint;
- the ancestry relation back to the dormant backend merge commit above;
- confirmation that no scientific geometry, downstream permission, provider role or request semantics changed while adding the schedule trigger.

The final `dtrm.phase4.prospective_activation_statement.v2` must bind to the exact **schedule-bearing revision registered by that addendum**, not to the dormant commit/tree/blob frozen in this readiness record. Scheduled slot evidence must then match that final activation provenance exactly.

If no such addendum exists, periodic activation is forbidden.

## Deliberately unresolved activation fields

The source-value-free readiness statement records the following as unresolved rather than inventing or inferring them:

- `provisioned_schema_identity = null`;
- `credential_scope_status = UNVERIFIED`;
- `credential_scope_evidence_sha256 = null`;
- `writer_authority_status = UNVERIFIED`;
- `writer_authority_evidence_sha256 = null`;
- `prospective_start_utc = null`;
- `human_activation_authorized = false`;
- `periodic_capture_activation_permitted = false`.

No repository search result, merged code path, or workflow definition is sufficient evidence by itself to promote any of those fields. In particular, the GitHub connector used to inspect code does not expose secret values and this contract must not contain secret material.

## Promotion rule

A later activation candidate may be constructed only if all of the following are independently established without provider values or secrets:

1. a provisioned schema identity exists for the registered private evidence collections;
2. least-privilege credential scope is explicitly `AUTHORIZED` and represented only by a sanitized SHA-256 evidence digest;
3. writer authority is explicitly `AUTHORIZED` and represented only by a sanitized SHA-256 evidence digest;
4. a schedule-bearing backend revision has been created as a descendant of the dormant backend merge and preserves the frozen workflow path/identity, provider-role order, request fingerprint and campaign geometry;
5. a separate scientific scheduled-revision addendum has registered that exact descendant backend commit/tree and schedule-bearing workflow blob before activation;
6. a canonical `prospective_start_utc` is chosen on its UTC day in the interval `[00:00:00Z, 00:15:00Z)`;
7. provider-role order and registered request fingerprint still match;
8. the exact activation-statement bytes bind the registered schedule-bearing revision and pass the backend v2 fail-closed verifier;
9. the human gives a separate explicit authorization to activate periodic capture.

Any mismatch means no activation. The campaign is never shortened, shifted, backfilled, or partially counted to accommodate a late or incompatible activation.

## Frozen campaign geometry

This increment does not alter the preregistered evidence campaign:

- 14 consecutive UTC days;
- targets at `00:15`, `06:15`, `12:15`, `18:15` UTC;
- exactly 56 opportunities;
- at least 48 accepted slots;
- at least one accepted first-day slot and one accepted last-day slot;
- no backfill and no early stopping;
- only scheduled attempt 1 can be counting-eligible;
- reruns remain diagnostic and non-counting;
- finalization only after the last slot plus the preregistered 240-minute boundary.

## Frozen downstream prohibitions

Until the prospective evidence campaign is complete and the separately preregistered adequacy audit returns PASS, all of these remain false:

- confirmatory history construction;
- Temporal State outcome fitting;
- outcome access;
- MM1 execution;
- Phase III policy mutation;
- public raw provider-data redistribution.

## Machine-checkable statement

The exact readiness statement is:

`research/contracts/DTRM_PHASE4_POSTMERGE_ACTIVATION_BINDING_STATEMENT_V1.json`

Its canonical SHA-256 is:

`7f3c668bce9866a2eb8483c270e8ae23a26a1ca0cb3bd8d40c11a5f7e924c442`

The pure validator in `src/dtrm/phase4/postmerge_activation_binding.py` rejects duplicate JSON keys, secret-shaped material, unexpected keys, immutable dormant-binding drift, and any attempt to promote an unresolved activation field inside this preregistration increment.

The machine-checkable backend/workflow values in that statement describe only the current dormant lineage. They do not authorize a future scheduled revision. The required scheduled-revision addendum is the sole bridge from these dormant anchors to the exact provenance that the final activation statement may use.

## Scientific interpretation

After this increment is reviewed and integrated, the remaining pre-campaign work is operational evidence, the schedule-bearing backend increment, its exact scientific addendum, and the explicit human activation gate—not redesign of the scientific comparison. The later 14-day collection is itself part of the preregistered experiment. Outcomes and MM1 remain protected until the campaign and adequacy gate are complete.
