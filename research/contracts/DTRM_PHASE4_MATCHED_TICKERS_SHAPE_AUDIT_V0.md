# Phase IV — Matched-tickers BSON shape census v0

**2026-10-14 | REGISTERED BEFORE CODE | source-characterization only, not G5.**
Feature branch `feature/phase4-matched-tickers-shape-audit-v0` from `research/phase4-temporal-state` head `3c9c7a2443213c991bba4cb621b97d9a56b3dd6c`.

## Why this is necessary

The previously accepted 2026-09-10 bounded retrospective census showed 63,873 current news rows, all with nonempty `matched_tickers` arrays, but **405,565 nested elements did not match a string-only ontology**. This is an element count, not a row count. The audit explicitly did **not** establish that those associations are invalid: objects and structured nested records may be normal. This missing schema boundary prevents relying on the historical asset-link field even for exploratory shape feasibility, much less a real point-in-time mapping.

This new audit answers only: *Which BSON element/container structural types and common allowlisted object-field type combinations occur?* It **does not** read or publish ticker values, texts, URLs, event IDs, document timestamps, scores, outcomes, or per-row identifiers. It does not prove that the mapping is correct, historically available or immutable.

## Frozen scope

- Namespace strictly `trumpMinMax.trumpNews`. No other collection.
- Read-only, operator-local **future** transport, never run by agent or GitHub Actions against production.
- Cap 250,000 original documents; on 250,001 or count mismatch, abort. The inherited 63,873 count is a historical observation, not a hardcoded expected live result.
- Two read-only operations maximum: `count_documents({})` and one registered aggregate bounded by `$limit: 250001`, no `$out`, `$merge`, `$function`, `$where`, `$lookup`, `$unionWith`, updates or deletes; `allowDiskUse=false`, bounded `maxTimeMS`. Majority read concern requested, no automatic downgrade. Result is not an atomic snapshot; abort if count/aggregate disagreement.
- Server aggregation reads only `matched_tickers`; **source values are never projected into the returned results**. The response is exactly one document with two aggregate facets:
  - `containers`: counts grouped solely by BSON `$type` of the top-level `matched_tickers` field. An array may be empty; a missing/null/non-array field is reported explicitly.
  - `elements`: for arrays only, counts grouped by element BSON `$type`, plus BSON types (not values) of allowlisted object subfields: `ticker`, `symbol`, `name`, `score`, `confidence`; non-objects use a `not_object` marker. Unknown extra subfields are never enumerated or copied. These names are **candidate inspection keys**, not assumed mapping semantics.
- No unredacted Mongo cursor, literal element, identifier, sample document or source value may cross the programmatic driver boundary. Only grouped counts.
- No indexing or automatic collection mutation. No CDN/cloud/FMP/price/baseline/target access, no history construction.

## Deterministic pure domain

Define exact pipeline generator `build_shape_pipeline()` without variable input. Implement strict `normalize_shape_counts(...)` parsing an injected aggregate response:

1. Exact object keys and exact BSON vocabulary. `containers` is a bounded list of unique `{kind,n}`; `elements` is a bounded list of unique `{kind,ticker,symbol,name,score,confidence,n}`. The types are whitelist literals only, including `missing` and `null`; no arbitrary group identifiers.
2. `n` is an integer, non-boolean, positive, limited to 5,000,000 per bin, with total 0–5,000,000. Across facets, `sum(containers.n) == counted_documents`; each element group kind is a valid BSON type and field types are `not_object` if `kind != object`. For objects, all field types must be valid BSON type strings; mixing placeholder and real types is invalid.
3. Output fixed canonical order, frozen typed state, source/count metadata identities and a SHA-256 of the sanitized aggregate-only payload, **not a digest of any source value**. Classify any count/profile disagreements as fixed errors; no report on failure. Report `scientific_status=BLOCKED_SOURCE_AUDIT`, `asset_mapping_authenticated=false`, `vintage_authenticated=false`, `decision_clock_authenticated=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`.
4. Prescriptive acceptance of resulting shapes **is not** part of v0. The audit must not silently derive ticker IDs from any object path, infer mapping accuracy, drop malformed values, or change time splits after seeing counts.
5. Synthetic tests provide fixed fake aggregation result, malformed/duplicate/overflow/counter disagreement, unexpected keys, type confusion, zero array and object shape mix, permutation digest invariance, and immutability. The production operator read boundary must enforce the same shape and redacted errors, with no credentials logged.

## Future operator/authorization boundary

This PR can include a *dormant*, local-only, authenticated Mongo read adapter reusing the existing `salvage_live_io.configured_uri` security policy. **Do not execute against the live database as part of engineering validation.** A later separate user-authorized run may produce one sanitized aggregate report, with exclusive atomic write and a SHA-256; operator checks it locally before sharing. Avoid exposing env files, Mongo URI or credentials. CI may use fake driver or explicit disposable localhost Mongo test only.

If the actual groups reveal object fields, a separately preregistered **semantic mapping proof** is needed to interpret them; values are not recorded in this audit. Even a perfect structural mapping does not authenticate when an asset association was created or available, so confirmatory Phase-IV history, B fitting, T, outcomes and MM1 remain blocked. Frozen Phase III source and user-facing production must be byte-identical.

## Review gates

Contract → code → tests → Ruff/strict mypy → current-head CI and 157 inherited SHA preservation → Codex/human review. No feature merge until separate authorization. This instrument is outcome-blind and cannot repair the previously frozen retrospective `RETROSPECTIVE_PROXY_PARTIAL` result.
