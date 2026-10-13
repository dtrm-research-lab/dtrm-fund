# Phase IV v3 — numeric-overflow fail-closed addendum v1

**Preregistered before implementation**, triggered by Codex P2 on scientific PR #33 exact head `cf9fdc8bc2081302c407444e6c7ab4c9e542e498`.

## Defect

CPython `json.loads(..., parse_constant=...)` does not invoke `parse_constant` for a large JSON numeric exponent such as `1e999`. The parsed float is infinity. Subsequently `json.dumps(allow_nan=False)` raises an unclassified `ValueError`, violating the boundary's fixed-code `SyntheticV3EnvelopeError` contract.

## Frozen correction

- In the synthetic-only verifier, supply `parse_float` that converts the numeric literal to `float`, checks `math.isfinite`, and issues `SyntheticV3EnvelopeError("INVALID_JSON")` for infinity, negative infinity or NaN. No raw token may appear in the error. All other number handling remains unchanged; parse_constant remains fail-closed.
- Add synthetic regression tests using canonical `1e999` and `-1e999` JSON tokens, within 16 KiB and with the expected digest of those exact bytes, verifying `INVALID_JSON` rather than an escaping `ValueError`. Preserve duplicate key and NaN tests.
- No modification of HMAC semantics, campaign/slot clocks, external AWS/GitHub interfaces, scientific evidence criteria, acceptance authority, MM1 or Phase III. All positive reports remain `SYNTHETIC_COMPATIBILITY_ONLY`; no real origin or counted observation.
- Run scoped Ruff/format/mypy/pytest and all four CI workflows on exact new head, request fresh Codex exact-head review, resolve the P2 only after proof; do not merge without distinct human permission.

This is a narrow correctness fix for the synthetic wire boundary, **not** a security claim for real provider data.
