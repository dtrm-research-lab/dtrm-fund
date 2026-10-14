# Phase IV — Frozen C0 decision-clock static audit v0

**2026-10-14; registered before implementation.** Contract-only first commit in a new bounded feature branch, target `research/phase4-temporal-state`. This is an **outcome-blind, offline, source-code-only** audit of the frozen Phase III/MM1 control for Phase IV cross-arm clock compatibility. It does not change C0, the Phase-III estimator, the MM1 optimizer, or any prior experiment.

## Scientific question and fixed source anchors

The Phase IV counterfactual comparison **T vs C0** can only be interpreted as access-to-history improvement if the current-event and frozen-control feature set correspond to a compatible authenticated decision time. The base Stage-0 contract is `DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md`, inherited code snapshot `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`.

This audit pins three exact preexisting source files and Git blob identities (not a new release):

| Path | Required Git blob SHA-1 |
|---|---|
| `research/experiments/build_phase3_mm1_v5_exante_artifacts.py` | `75b2c07e86820923deaaebc1d8c4b4265db7d877` |
| `research/experiments/build_phase3_mm1_v6_exante_artifacts.py` | `0b4a2d61715ba6d3dc497118a98a5aa48e765f42` |
| `research/experiments/run_exante_baseline_v0.py` | `cecd1a71ffc1526d64f37d0a52b47db4b1e36675` |

Git blob verification is `sha1(b"blob " + ascii(len(content)) + b"\\0" + content)`. The validation reads only these fixed tracked sources, never imports their modules, loads pickle/prices, opens Mongo, or accesses environment secrets. It also checks exact inherited fragments, failing closed if the source changes.

## Static findings to reproduce

1. V5 normalizes `document["date"]` by `pd.to_datetime(str(raw_date)[:10], utc=True)` in the candidate builder (around original line 127). V6 uses the same expression (around original line 111). **Only a day-granularity event date is retained by these paths**, not authenticated intra-day source availability.
2. V5 `price_history_on_or_before` compares `_naive_utc(date) <= cutoff` when accumulating price histories (around original line 214). The downstream `beta_pre_for_pairs` calls it for both stock and SPY with event date (around 241–242). The code enforces nominal date ordering, **not an independently established publication/availability time of that daily close or vintage**.
3. V6 explicitly reuses `v5.load_exante_price_cache()` and `v5.beta_pre_for_pairs(pairs, prices)` (around 241–242); the inherited cache loader loads `*_2026-07-05.pkl` with `frame["date"]` and `frame["close"]`. The cache is a snapshot and cannot alone attest the exact first availability/revision of each price.
4. V6 projects only `text`, `date`, `matched_tickers` and `_id` from its news source, with no independently observed `first_seen_at`, `version_observed_at` or `linked_at`. The earlier Phase IV source audits already showed source clock/vintage gaps. Thus the current frozen code alone cannot authenticate the same decision cutoff as a prospective as-of history dataset.
5. **No leakage is proven merely by inspecting these operations.** Treat the same-day close potential as a **testable timing risk**, not a demonstrated historical violation. Report `CONTROL_CLOCK_ATTESTATION_REQUIRED` and `control_clock_authenticated=false`; never claim that frozen Phase III/MM1 was scientifically invalid, retune it, edit its code, or declare a T-vs-C0 result.

## Required future external evidence, not collected here

- Explicit actual decision instant `t` (UTC, tie semantics), current-event arrival and linked-asset visibility; reconcile source `date` daily projection to observed `version_observed_at` and `linked_at`.
- For every C0 price input, price-session market/date/timezone, timestamp of **first availability** of exactly that close, actual data cache vintage/corrections, calendar, time tolerance, and all pre-event beta lookback dependencies. Price date `<= event_date` does not establish availability `< t`.
- Exact frozen C0 predictor/calibration and candidate universe identity shared across S/B/T/O. If mismatched, stop with `BLOCKED_CONTROL_CLOCK_MISMATCH` **only after actual independently authenticated evidence contradicts the registered cutoff**, never based on static code alone.
- Prospective 14-day/56-slot transport proves collection adequacy only; neither temporal history/model sufficiency nor 60-calendar-day plus five-day target maturation follows from it.

## Pre-registered pure graph and acceptance

- `load_fixed_frozen_sources`: fixed paths from repository root, no arbitrary input path override, explicit regular-file/no symlink check; always read bytes with no imports or network.
- `assert_frozen_git_blobs`: validate exact Git object hashes for all three files. Any failure -> fixed `BLOCKED_FROZEN_CONTROL_SOURCE_DRIFT`, no positive report.
- `inspect_static_clock_contract`: check exact source fragments above; missing fragment -> fixed fail-closed source-drift error; no dynamic model or data access.
- `emit_sanitized_static_report`: deterministic source identities, bounded static findings, explicit permanent nonauthorization flags. No ticker, price, event value, outcome, token, environment path, timestamp from real input or local cache.
- CLI prints **only** a sanitized canonical JSON to stdout after all gates. No output files, AWS calls, subprocess, live data or credentials. Domain result is frozen/tuple backed.

Tests: exact-source real tracked readback; content mutation/empty path/symlink rejected; absent essential fragment rejected despite forged expected hash in synthetic unit tests; static result detached/immutable and deterministic; permanent `source_authenticated=false`, `decision_clock_bound=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`. All inherited regression, Ruff, strict mypy, synthetic-evidence, packaging and source preservation gates are required for review. No merge until human approval.

## Status

`engineering_status=PASS_FROZEN_CONTROL_STATIC_CLOCK_AUDIT` merely means byte-level source identity and fragment semantics are consistent. The scientific status is permanently `BLOCKED_CONTROL_CLOCK_ATTESTATION` on this path. It is **not** a successful source/temporal admissibility test; actual availability remains unproven. PR36's independently preregistered exact common cohort and history lookback-before-binning rule remains binding for any future live study. AWS quota request last operator-observed `CASE_OPENED`; not accessed here.
