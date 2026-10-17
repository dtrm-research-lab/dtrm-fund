# Phase IV — independent GitHub metadata readback, 2026-10-15

**Observed, read-only, not a confirmatory experiment.** The GitHub connector queried `tech-com-UA00001/theresistance-back` `list workflow run artifacts` separately for each of the 21 `run_id` entries from PR #41's metadata-only canonical manifest (Git blob SHA-1 `eb7c91b462ddb822835c20fc126492bfcae5eea0`). This occurred after previous offline exploration, so it is **not a blind preregistration**. The 21-source manifest is on an UNMERGED separate branch; not contained in this branch. Issue #34 records the same observation in comment 6189344543.

| Provider metadata comparison | New readback |
| --- | ---: |
| Expected run IDs independently queried | 21 / 21 |
| Expected artifact IDs in respective run listings | 21 / 21 |
| Exact `artifact.created_at` matched | 21 / 21 |
| Exact `daily-ranking-<run_id>` matched | 21 / 21 |
| Exact `workflow_run.id` matched | 21 / 21 |
| Provider `expired=false` at check time | 21 / 21 |

Earliest provider `expires_at`: **2026-10-16T00:41:51Z**, `run_id=35040651840`, `artifact_id=10424883893`. Second: 2026-10-17T00:49:19Z. Third: 2026-10-18T00:37:38Z. These are provider-declared and may change. The **original ZIP bytes must be privately preserved and SHA-verified before expiry** if not already retained. The original 21 ZIPs and their raw content have NOT been copied or committed in this increment.

**Caveats:** The current PR's new pure verifier is a *separate implementation*, verified on synthetic receipts once CI passes. It was **not run against the 21 raw API JSON responses** in this GitHub commit; hence no claim of actual CLI replay. The direct connector readback was examined in the chat, not saved as an independently signed or externally timestamped provider ledger. The reported `21/21` is therefore an independently repeated API comparison, not a cryptographic attestation of true creation instant, source first-seen or association mutation. Expiry observed in API is not archive preservation.

No article/ticker identifiers, provider text/URLs, model scores, prices, protected targets, or real ZIP bytes recorded. No AWS, Mongo/FMP, MM1 or Phase III changes, no merges, no new model fitting, no outcomes. No rewrite of frozen research contract. Scientific state: **BLOCKED_SOURCE_AUDIT**. PR #44's reproducibility and cutoff per-family observations remain separate review gates.
