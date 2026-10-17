# Phase IV — Temporal admissibility proof obligations v0

**15 October 2026. Contract-before-code; isolated, synthetic-only incremental graph.**

## Motivation and authority

The operator has separately reported PASS for the immutable 21-ZIP Phase-IV archive census and full per-capture coverage replay in unmerged PR #41/#44. Its 36,440 globally distinct *selected positive representation triples* remain **archived witnesses**, not 36,440 independently authenticated first-seen events or trainable rows. 13/21 selected 2d and 21/21 selected 5d exports hit the 500-item cap. The source clock, original association mutation time, complete 60-day history and rights are unresolved. Stage-0 `DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md` is `DRAFT_FOR_REVIEW`; Issue #34 G5 is still blocked.

**Question for this increment:** What explicit independent evidence would be needed, in principle, to admit a content-vintage-to-ticker representation to a particular *decision cutoff*, instead of equating a past publication date or archived presence with original link availability?

This is a *proof-obligation classifier*, not an actual provider-receipt authenticator or a complete scientific firewall. It is not a new hypothesis test and does not register a Phase-IV training dataset.

## Sources and evidence classes

Inputs are **synthetic, opaque, bounded** tokens and timezone-aware UTC ISO-8601 second-resolution strings; any real raw article IDs, tickers, URLs, text and source receipts remain outside code, test fixtures, CI and reports. Source fields are **declarations**, not proof that a provider clock is authentic:

1. `published_at_utc`: publisher/event time, context only. Never sufficient for eligibility.
2. `archived_positive_at_utc`: time an *exact link-and-version positive* first appears in an independently supplied selection archive. Before-cutoff archive presence is evidence **only of an earlier archival positive witness**; missing or post-cutoff archive is UNKNOWN as to original existence (not a negative).
3. `source_vintage_first_available_at_utc`: separately claimed availability of the exact original text version.
4. `link_mapping_first_available_at_utc`: separately claimed earliest availability of this *version's exact asset relation*.
5. `derived_state_first_available_at_utc`: separately claimed earliest availability of the derived features used at decision time.
6. `price_vintage_first_available_at_utc`: separately claimed exact eligible price-vintage availability for the common C0/S/B/T/O cutoff.
7. Four **independently authenticated receipt** booleans for source, link, derived state and price. In this increment booleans are **synthetic fixture values only**; they are not real trust anchors and are never promoted into scientific authority.

A local classifier may distinguish synthetic **proof-shape complete**, **incomplete**, and **future-claimed** inputs, while separately recording archival-witness-before-cutoff. No combination of booleans in this synthetic graph permits real decision admission. Outputs must have `scientific_status=BLOCKED_SOURCE_AUDIT`, `real_source_admission_permitted=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcomes_access_permitted=false`, `mm1_execution_permitted=false`. Missing/unobserved source and links are `UNKNOWN`, never `FALSE` or `ZERO`. `first_seen_authenticated=false` remains fixed for all cases.

## Temporal and provenance invariants

- Admissibility is conditional on **all four** source, link, derived and price availability claims being present, independently evidenced and **strictly earlier than the UTC decision cutoff**. Equality at the cutoff is not admitted. A publication timestamp, whether earlier or later, does not replace any claim.
- The archived positive time is an **independent descriptive axis**, also strict `< cutoff` when used as a prior witness. A post-cutoff positive must never be backdated using the record's `asOf` or publication time.
- If an explicit claimed receipt is post-cutoff, classify as **future/deferred** before incomplete, regardless of archived witness. Missing receipts cause proof-shape incompleteness. A later claim never overwrites an earlier archival witness or certifies that no earlier link existed.
- Reject naive times, timezone offsets, malformed dates, duplicate source roles, raw identifying values, obviously invalid combinations and future archive witnesses mislabeled as prior.
- Per-link synthetic classification must not be multiplied into training population counts. No universal claims about 60-day history, 14-day prospective completeness, provider rights, inferred negatives, cohort sufficiency, or economic uplift.
- The graph is pure and deterministic, input immutable; fixed redacted failures, serialization limited to category/counters and synthetic case tags. No GitHub/AWS/FMP/Mongo, network, secrets or financial outcomes at runtime.

## Expected synthetic acceptance cases

1. Publication early, archive late relative to decision, all other claims absent ⇒ `NO_PRE_CUTOFF_ARCHIVE` and `INCOMPLETE_PROOF`, never admit.
2. Archive before decision but original source/link first-seen missing ⇒ `PRIOR_ARCHIVED_POSITIVE` and `INCOMPLETE_PROOF`.
3. Archive before decision and all four synthetic claims and booleans pre-cutoff ⇒ `PRIOR_ARCHIVED_POSITIVE` and `SYNTHETIC_PROOF_SHAPE_COMPLETE` with **real admission false**.
4. Any source/link/price/derived availability equal to or after decision ⇒ `FUTURE_CLAIM`; refuses admission even if archive was earlier.
5. Publication alone never substitutes for the exact vintage, link, derived and price proofs.
6. Family/source regime identity must not be silently crossed; any real archive family compatibility remains a separate contract/gate.
7. Invalid/naive/offset/non-strict timestamps or unsafe identifiers cause fixed rejection.
8. Deterministic synthetic report, no private values and all scientific gates remain false.

## Follow-on evidence required (not acquired here)

Independent provider (or append-only ingestion) receipt validation must bind immutable **content digest + exact link mapping + actual ingestion and mutation time + trusted external clock**, including revisions and historical backfill. Independently prove derived-feature and price-vintage clocks, source rights, shared universe and availability for C0/S/B/T/O. The prospective v3 campaign also requires trusted AWS origin/GitHub/Dynamo claim provenance, a separately approved real activation, 56 planned slots/adequacy checks and source completeness. Only a future separately registered data-admission adapter may consider authenticated examples, with explicit scientific authorization.

**No changes to the Stage-0 contract, Phase III/MM1's 157 inherited files, `humanclause.com`, backend, schedules or AWS. No PR merge or activation without explicit human approval.**
