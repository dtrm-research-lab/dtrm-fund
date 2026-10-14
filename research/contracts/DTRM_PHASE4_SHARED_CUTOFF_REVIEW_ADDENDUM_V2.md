# Phase IV shared-cutoff review addendum v2 — ambiguous UTC offsets and range failures

**2026-10-14. Registered before implementation.** Codex exact-head review of `64b005e6a365cd5b3dede1421fd3701189ed05fd` found two P2 parser boundary defects. This addendum applies to the **synthetic-only** PR #38, does not amend original Stage-0 or #36 scientific estimand, and does not permit any real-data/AWS/financial exposure.

1. A full ISO-like timestamp ending in `-00:00` is an RFC3339 marker for *unknown local timezone offset*, not proven UTC. It **must be rejected** with the existing sanitized `INVALID_SYNTHETIC_SHARED_CUTOFF_FIXTURE` error, not normalized to `Z`. Valid positive zero `+00:00` and `Z` remain supported as expressly UTC.
2. A syntactically valid timestamp at representational extremes may parse while `.astimezone(UTC)` raises `OverflowError` or `ValueError`; catch either during UTC conversion, rejecting via the same sanitized domain error. No raw exception values, conversion guesses or clamping.
3. Tests must cover unknown-offset clock on cutoff, news and price fields, valid `+00:00` and `Z`, underflow `0001-01-01T00:00:00+14:00`, overflow `9999-12-31T23:59:59-14:00`, and the permanent scientific-gate blocks.
4. Existing v1 causal ordering (version preceding link, price-first preceding price-vintage), strict full instants, immutable state and current-head CI gates remain intact.

No source provenance is authenticated by handling these synthetic timestamps.
