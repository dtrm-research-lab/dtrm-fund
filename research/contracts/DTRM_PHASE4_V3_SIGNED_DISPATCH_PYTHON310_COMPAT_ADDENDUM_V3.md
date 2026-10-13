# Phase IV v3 — Python 3.10 signed transport compatibility addendum v3

**Preregistered before implementation** on PR #33, responding to Codex P2 at exact commit `ecbea70fd70f5f40ad7a8dbdf6fb596505595842`.

The scientific repository `pyproject.toml` declares `requires-python = ">=3.10"`. The synthetic signed-dispatch verifier imported `datetime.UTC` and `typing.Never`, both added in Python 3.11, so importing under supported Python 3.10 failed. This is a real supported-version defect despite the 3.11 scoped CI passing.

## Narrow correction

1. Replace `datetime.UTC` with `datetime.timezone.utc` using a module alias `UTC = timezone.utc`; replace `typing.Never` with `typing.NoReturn` and keep the fail-closed helper's `_bad` semantics unchanged.
2. In the synthetic test fixture replace `datetime.UTC` with an alias defined from `timezone.utc`. No change to canonical timestamps, signer, campaign geometry, scientific 56/48/first-and-last rule, HMAC or any evidence authorizations.
3. Extend the **existing scoped workflow** with a second Python 3.10 job that installs only `pytest`, imports the new verifier, and executes its synthetic tests using `PYTHONPATH=src`. Keep existing full 3.11 Ruff/strict mypy/synthetic suite/Phase III source preservation workflow unchanged; both versions must be independently green.
4. All downstream permissions stay false; no AWS, provider, GitHub dispatch or MM1 invocation. No PR merge without separately granted human approval. Fresh exact-head Codex review required before declaring review-ready.

## Regression

Require positive canonical synthetic envelope for first/last slot, and fail-closed tests for `1e999` JSON floats, signed identity/time mismatches, invalid date.max 14-day window on **both Python 3.10 and 3.11**. The two Python versions must produce the same fixed `SYNTHETIC_COMPATIBILITY_ONLY` status and error codes. The actual backend frozen reader/auditor remains unchanged.

This addendum documents Python compatibility only and **does not** attest scheduler origin, real cloud identity, qualified Lambda version, independent DynamoDB claim, scientific adequacy PASS or PRAGMA improvement.