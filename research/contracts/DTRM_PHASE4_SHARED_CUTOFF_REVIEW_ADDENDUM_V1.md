# Phase IV shared cutoff — review hardening addendum v1

**2026-10-14 — recorded before subsequent implementation.** PR #38's original preregistration remains an ancestor. This addendum narrows acceptance in the existing synthetic-only shared-clock probe; no use of live sources, prices, outcomes, MM1 or AWS is authorized.

## Review findings and testable invariants

1. **Version-to-link causal order**: a link asserting association to the exact observed news vintage must not predate that vintage's `news_version_observed_at`. When both instants are non-null, require `news_version_observed_at <= news_linked_at`. An earlier link is contradictory evidence and invalidates the entire fixture; missing either value is `UNKNOWN` and cannot create a positive synthetic admission.
2. **Price first-to-vintage causal order**: when both `price_first_available_at` and `price_vintage_available_at` are known, require `price_first_available_at <= price_vintage_available_at`. An earlier exact vintage is inconsistent with the claimed initial availability. Missing one remains UNKNOWN and can never pass.
3. **Exact timestamp syntax**: require a full explicit ISO-style datetime `YYYY-MM-DDTHH:MM:SS[.fraction](Z|+HH:MM|-HH:MM)`. Normalize all valid offsets to UTC for strict-before/equal/after comparison. Do not accept a space instead of T, date-only input, omitted seconds, naive time, trailing whitespace, or non-ISO zone formats. `price_session_date` remains an economic date string only and is never used as availability clock.
4. Unknown timestamps are not backfilled, nor are contradictory instants repaired or reclassified from provider publication/calendar dates.
5. All relevant tests must cover contradictory linkage, contradictory price vintage, equal valid causal instants, unknown one-side (blocked), and malformed timestamps. The previously passing synthetic fixtures and all false authority/activation flags must remain unchanged.

The rule does **not** claim that independently authenticated live writer clocks or C0 price dependencies exist. `BLOCKED_CONTROL_CLOCK_ATTESTATION` is unchanged. No human promotion, AWS request or MM1 execution is implied.
