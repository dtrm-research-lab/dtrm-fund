# Phase IV — Source-clock audit decision plan (outcome blind)

**15 October 2026.** This is a research execution checklist, **not** a claim that real source admissibility has been proved. Follow the immutable Stage-0 draft and Issue #34 G2–G5, the still-unmerged 21-source ZIP provenance PRs #41–#45, and the synthetic proof-obligation contract on this branch.

## What the preserved archive does and does not establish

| Evidence axis | Observed status | Consequence |
| --- | --- | --- |
| 21 original ZIP artifact payload identities | Operator-reported `PASS` for each original ZIP SHA256 and canonical manifest | Byte integrity of these **private saved** source records |
| 21 per-capture and four cutoff selected-positive censuses | Operator-reported `PASS` of exact v1 real ZIP replay, output SHA256 `3324efbb6cb8540b74c89af0c633b15656fd04260058b1ebed217b1c6484b1cb` | 36,440 globally distinct selected positive representations; full family-summed 38,968, NOT independent historical events |
| Selected-export truncation | 13/21 two-day captures capped 500; 21/21 five-day captures capped 500 | Unselected / absent values are **UNKNOWN**, not negative observations |
| Source-version original first-available UTC | Not authenticated | Publication dates cannot replace this missing clock |
| Exact article-content-ticker mapping first-available UTC | Not authenticated, including Sept 19 reported backfill chronology | Archive `created_at` is a latest positive witness time, not a source insertion/mutation timestamp |
| Derived-feature and price-vintage availability | Not authenticated | No legitimate common decision-time C0/S/B/T/O data construction |
| Full source 60-calendar-day history plus source rights | Not established | No scientific source admission, comparison or source reuse/publication claim |
| V3 real 14-day, four-slots/day prospective capture adequacy | Not completed and activation not authorized here | 56 slots / ≥48 accepted requirements **remain prospective**, with G2 AWS/GitHub/Dynamo chain independent |

The phrase **zero authenticated historical link first-seen records in the supplied proof package** means zero *authenticated by this current audit*, not evidence that no genuine early links exist. The amount of trainable temporal history is **unknown**, not `36,440`, `38,968` or zero.

## Evidence acquisition paths, in order

**A. Archived-event provenance pilot (read-only, bounded, separately authorized):** Identify whether original append-only ingestion audit, FMP immutable receipt, Mongo change stream archive, application job logs, GitHub Actions run payload or S3 object-version evidence can independently bind:
`SHA256(exact content vintage)` + `source original receipt UTC` + `article version` + `exact asset link assertion UTC` + `revision provenance`.
The existing ZIPs prove only archive presence at externally observed GitHub timestamps. Refuse to forge `first_seen` from `asOf`, `publishedDate`, current Mongo state, backfills, or reconstructive reruns. Any attempt must be source-only, minimize identifiers and obey Issue #18 private rights controls. No Mongo live access in this increment.

**B. Prospective original-version event ledger:** If original clocks cannot be recovered, use a future separately authorized append-only writer that records, at capture-time, immutable content-vintage digest, provider response/arrival event, UTC trusted writer clock, added/updated link/version (including tombstones or mapping removals if the provider genuinely reports them), source request identity, and monotonic capture/writer lineage. Version changes must be new events, never historical rewrites. Store private data only under separately reviewed entitlements, rather than in GitHub's public repository. The existing v3 14-day schedule is a **capture process adequacy** test; 14d by itself cannot certify 60d historic event coverage or 60+5d realized outcome maturity.

**C. Independent prospective transport proof:** Before a real v3 scientific counter can be accepted, validate EventBridge scheduler origin, Lambda invoke control/data evidence, HMAC campaign target/slot, DynamoDB first-write claim, original GitHub run/writer identity and lag/duration per fixed contract. AWS quota increase and an offline Lambda package are **not** a deployment permission or trust attestation. Cloud resource writes/real third-party API use require explicit human cost/security/activation authorization.

**D. Common decision data firewall:** Bind price availability (historical price version and observed ingestion), inherited beta/lookback fields, ticker/link compatibility across families, fixed decision cutoff and source-rights evidence. Reconcile a **common** C0/S/B/T/O universe with explicit empty, short, truncated and unknown histories; never impute absent associations as zero. Freeze data windows, exclusion handling, horizon and inference design **before** training, target inspection or model comparisons.

## Next safe engineering increments

1. The current PR supplies a **closed synthetic-only** proof obligation shape test; all successful example shapes remain `real_source_admission_permitted=false` and `BLOCKED_SOURCE_AUDIT`.
2. Next separate project increment may design a **metadata-only provider proof receipt schema/verifier**, with independent trust keys/clock sources and rights evaluated by a human reviewer **without** any live Mongo/FMP/AWS read. It must fail closed on forged receipt and link/version hash mismatch before touching private values.
3. Then plan a **bounded, separately approved audit** of only the original source provenance fields; do not backfill raw news into this public repo or infer the timestamp from an archived ranking alone.

**Not permitted by this document:** AWS activation, bucket/Lambda scheduling, CloudTrail chargeable diagnostics, FMP/Mongo live operations, model fitting, outcomes, source promotion, paper uplift claims, merges or changes to Phase III/MM1 and production `humanclause.com`. Every real execution requires its own decision record and human gate.
