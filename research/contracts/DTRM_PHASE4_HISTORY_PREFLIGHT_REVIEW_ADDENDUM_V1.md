# Phase IV synthetic history preflight — fail-closed review addendum v1

**2026-10-14. Registered before hardening implementation.** This is a narrowly scoped correction to `DTRM_PHASE4_HISTORY_SUFFICIENCY_PREFLIGHT_V0.md` on the same unmerged feature branch. The original contract and frozen Phase-III/MM1 files remain unchanged.

## Review trigger

Codex PR #35 reported (i) mutable assessment state, (ii) duplicate JSON keys silently collapsed before validation, and (iii) cohort identifiers that could directly carry lower-case asset tickers. An additional ancestry concern was independently checked against GitHub's actual commit parents: `7404756` parent `2ed1f2d`, `7b1554e` parent `7404756`, `fc4c2f2` parent `7b1554e`, and `5763aa3` parent `fc4c2f2`; the preregistration does precede implementation. These corrections are preregistered here before code changes.

## Narrow binding changes, superseding v0 only where specified

1. **Immutable state.** Every validated cohort and top-level assessment is a typed frozen value with immutable tuple counters and cohort tuples. Serializing JSON materializes entirely new dicts/lists; modifying that serialization cannot mutate the assessed scientific state. Domain functions do not return mutable dictionaries.
2. **No ambiguous JSON.** The CLI must use a duplicate-key-rejecting JSON parse hook at every object nesting level. An otherwise valid fixture with repeated `dataset_role`, repeated counts, repeated `cohorts`, or repeated nested keys fails before domain assessment and before any output is created; no original fixture content appears in errors.
3. **Closed synthetic vocabulary.** `cohort_tag` is now exactly one of `case_01` … `case_64`, with a fixed zero-padded numeric suffix (not a caller-defined free-text tag). This replaces the v0 permissive tag regex and the illustrative v0 `case_a` example; test fixtures are updated. Each synthetic tag occurs once. This is a *synthetic test identifier*, never an authenticated temporal cohort, ticker, asset, source or confirmation window.
4. Keep exact keys and all count, fail-closed role, source/outcome-blocking, and CLI no-overwrite rules from v0. No new live adapter, training or date selection. The registered source-availability boundary and existing negative live source findings are unaffected.

## Acceptance before PR review

Verify frozen dataclass mutation attempts fail, recursively mutable JSON copies cannot change frozen state or a later serialization, duplicate JSON keys are rejected at root and nested levels, real-asset-looking tags (including `tsla`) fail, tags `case_00`, `case_65` and `case_1` fail, valid `case_01` … `case_64` work, permutation hashes match, sample/counter mismatches still fail, and no output is created on invalid input. Preserve prereg ancestry and the inherited scientific gates.

This addendum does **not** preregister G5 training/evaluation design and does **not** claim as-of event history or AWS quotas approved.
