# Phase IV v3 — Signed dispatch envelope compatibility preregistration v0

**Status:** PREREGISTERED BEFORE CODE, OFFLINE_SYNTHETIC_ONLY, NONCOUNTING, NO OUTCOME ACCESS.

Scientific parent = PR #31 merge commit `cecaa8667c5130d3e4b3c9828bd5980ee8515eb7` on `research/phase4-temporal-state`. Previous approved v3 operational contract = PR #30 merge `7f45b0a8c2a64b7620098544d79a492f63d474aa`. Next-step Issue #32 tracks the **separate** future evidence-adequacy adapter. No provider or real AWS call is authorized.

## Objective

Provide a **strict, outcome-blind, local contract check** for the signed *source-value-free* v3 dispatch envelope matching the dormant backend parser protocol (`dtrm.phase4.repository_dispatch_envelope.v1`, event type `phase4_fmp_news_temporal_capture_v3`). This is a synthetic compatibility primitive, **not** a real scheduler-origin verifier or a scientific accepted-slot auditor.

## Frozen implementation

Add `src/dtrm/phase4/v3_signed_dispatch_synthetic_boundary.py` and `tests/test_phase4_v3_signed_dispatch_synthetic_boundary.py`. Implement one stdlib-only import-side-effect-free pure validation function. Input:
- exact JSON **envelope object bytes** (not raw GitHub event), max 16 KiB; canonical UTF-8 JSON sorted keys, no whitespace, `ensure_ascii=True`;
- *externally supplied* expected SHA-256 of these exact bytes: check exact digest equality, but do not claim it was established by an independent party;
- expected frozen scientific activation ID/digest, expected scheduler identity, expected HMAC key ID and synthetic HMAC secret bytes (at least 32, <=4096; never print);
- campaign start UTC day, target index integer in [0,55] and one synthetic GitHub `run_attempt` integer equal to one; runner validated start UTC;
- require exact 11 envelope fields and exact signing fields from the registered dormant backend: schema, campaign_statement, campaign_statement_sha256, target_slot, target_at_utc, dispatch_id, dispatch_at_utc, scheduler_identity, signature_algorithm, signature_key_id, signature;
- validate canonical ISO UTC with terminal Z; frozen target clocks `00:15`, `06:15`, `12:15`, `18:15` across 14 UTC days; expected dispatch ID = lowercase SHA-256 of canonical sorted JSON of campaign_statement + campaign_statement_sha256 + target_at_utc + target_slot, exactly backend `expected_dispatch_id()`; HMAC-SHA256 over sorted canonical JSON of the other ten keys excluding `signature`;
- demand dispatch and runner clocks satisfy target <= dispatch <= runner <= target+120min. Accept exact bound, reject before target, after target or inverted order. Check HMAC and hashes with `hmac.compare_digest`;
- strict decoder rejects duplicated keys, NaN, nonfinite values, other keys, bad types and noncanonical byte encodings; no reflected raw user data in errors;
- fixed, sanitized **noncounting** report only (slot integer, status `SYNTHETIC_COMPATIBILITY_ONLY`, `cryptographic_test_passed=true`, `scheduler_origin_independently_verified=false`, `runtime_provenance_independently_verified=false`, `dynamodb_claim_independently_verified=false`, `scientific_counting_permitted=false`, `provider/outcome/mm1 permitted=false`); no secret, signature, account, provider values, and no authorizing state.

Do not import or change the frozen v1/v2 scientific adequacy auditor. Do not mark any v3 attempt ACCEPTED, allow history/fitting, or change the v3 future live trust hierarchy. **Supplying both a fabricated envelope and its digest does not prove provider origin** and is never sufficient for future counting.

## Frozen synthetic regression matrix

- valid canonical envelope and correct key/signature/ID, representative first and last slot, 120m exact bound;
- duplicate keys, extra keys, malformed/noncanonical JSON, oversized UTF-8 payload;
- wrong HMAC key/signature, wrong digest, too short HMAC key;
- wrong campaign name/digest, scheduler name/key ID, target slot and UTC target timestamp, dispatch ID;
- early, late, reversed clocks; rerun `run_attempt=2`; `True` disguised as int; outside [0,55];
- deterministic report and no credentials/raw signature emitted; absolutely no positive scientific/production permissions.

Quality: scoped pytest, Ruff lint/format, strict mypy if available, Phase III source preservation, no secrets or network in code, complete relevant CI and exact-head Codex. Parent merge ancestry must be preserved; future PR merge still needs separate human authorization. *No positive real-world v3 adequacy or scheduler provenance claim is supported by synthetic fixtures.*
