# Phase IV archived positive-witness verifier — review addendum v1

2026-10-15, registered before implementation in PR #42 after exact-head Codex P2 comments.

1. Catch decompression/integrity failures thrown as `zlib.error` and `ValueError` both within ZIP entry reads and from outer archive traversal, normalize to the fixed `INVALID_PHASE4_ARCHIVED_WITNESS` without provider data/stack leakage. Keep previously accepted ZIP size bounds and no extraction.
2. Reject `tickers` entries consisting only of whitespace, or with leading/trailing whitespace. Do not normalize/silently trim archived identifiers or accept them as positive link witnesses. A closed grammar can be introduced in a separately preregistered cohort contract, not inferred now.
3. Tests inject a deliberately corrupt *compressed archive member* while re-hashing the entire ZIP (so only the reader detects corruption), whitespace-only and padded tickers, and assert fixed fail-closed type. Reconfirm all negative scientific authorizations, CI, no full source disclosure and no real private ZIP check-in.
4. Does not authenticate any first-seen timestamp, source completeness or history absence; no MM1, fit, outcomes, live Mongo/AWS operations.
