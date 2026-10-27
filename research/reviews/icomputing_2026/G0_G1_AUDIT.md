# Intelligent Computing Major Revision — G0/G1 evidence audit (2026-10-27)

Manuscript: ICOMPUTING-D-26-01069. Revision due: 2026-11-25.
Status: **AUDIT IN PROGRESS; NO NEW RESULTS**.

## Immutable source
- Historical tag: `dtrm-xgb-probabilistic-phase2-stats`
- Resolved commit: `c7502a690162459cdfb3413573e3133c42efb126`
- Existing V0–V4 contracts, source, and paper's reported statistics are not to be rewritten.
- This branch separates review work from historical releases.

## Read-only audit observations
- The published tag contains contracts, test code and statistical runners, but NOT the referenced `research/local_data/*.pkl` signals/target/model files.
- `run_phase2_primary_bootstrap.py` expects paired signal/target pickles for V2, V3, V4.
- Original windows: V4 2026-05-02..2026-06-06, V2 2026-06-07..2026-06-10, V3 2026-06-11..2026-06-14.
- Outcome is a forward 60-calendar-day excess-beta target, with a documented +/- 5 day price matching tolerance; check actual price alignment and per-row realized intervals before declaring non-overlap.
- Last historical signal date was June 14. A truly nonoverlapping later window requires new events and target start dates at least after the latest realized end from that cohort. With the documented 5-day price-alignment tolerance, a conservative calendar starting bound is *after approximately August 18*; actual realized dates must still be audited before approval.
- As of October 27, nominal 60-day maturity implies cohorts must end no later than ~August 28 before accounting for price tolerance and actual vendor availability. As of Oct 27, a conservative maturity bound (60 days plus up to 5 days tolerance) suggests roughly August 19–23 only as a *potential* nonoverlapping, fully matured date range, not an approved or necessarily sufficiently sized holdout.
- Ticker-cluster intervals in V2/V4 straddle zero; original results cannot establish uniform robustness.
- Google Drive keyword checks did not locate raw cohort pickles. Absence from search is not proof of absence in local/AWS storage.

## Mandatory G0 gates
1. Locate licensed private raw artifacts and trained model weights under authorized storage; do not upload vendor data to public GitHub.
2. Verify exact file paths, SHA256 hashes, schema, training cutoff, source provenance, snapshots, prediction timestamps and code dependencies.
3. Independently reproduce V2/V3/V4 observed selection and CIs from raw inputs, preserving all negative results.
4. Capture an audit manifest with machine-readable PASS/FAIL/UNKNOWN states. Do not claim reproduction prematurely.

## Mandatory G1 gates
1. Enumerate prospective untreated event cohorts *without reading outcomes*.
2. Build interval overlap check using actual event timestamps and matched market-price horizons; check full 60-day target, not just signal dates.
3. Verify model feature compatibility, coverage (news, embeddings, beta, prices), cohort size and fully matured outcomes.
4. Pre-register selection criteria and final cohort before consuming outcome values; record any unavoidable historical exposure as a limitation.
5. No fitting, inference, benchmark comparison or threshold sensitivity result until gates pass.

## Reviewer tasks after G1
- P10 lower-tail and weighted VALID P15/P25/P35 sensitivity; no best-after-test selection.
- Comparison against ex-ante volatility/downside filters, capacity matched.
- Realized tradable returns, abstention/flat option, turnover, transaction cost and concentration-aware portfolio mapping.
- Clarify that human-defined rule design is not evidence of human judgment treatment effect.
- K capacity sensitivity, regime variation and second frozen ranker (if feasible).

## Safeguards
- No mutation of old tags/contracts. No premature MM1/Phase IV/STAMP blending.
- Research-only, least-privilege data access, no secrets or raw licensed vendor records in repository.
- Red-team checks for leakage, horizon overlap, selective reporting, double dipping and repeated tickers.

## 2026-10-27 G0.1/G0.2 operator checkpoint
The operator reports running the local hash-only discovery:
- required files located 10/10, no duplicate names
- 0 historical hash discrepancies
- status `PRESENCE_AND_ANCHOR_HASHES_OK_NOT_REPRODUCED`.

The operator also reports successful trusted-local point replay using
`ic_g0_reproduce.py`:
- V2: rows=4449; K=444; P10 pass=2530; delta=+0.144294805825; PASS
- V3: rows=2827; K=282; P10 pass=1634; delta=+0.149437488988; PASS
- V4: rows=40320; K=4032; P10 pass=23348; delta=+0.027561593801; PASS
- Status: `POINT_REPLAY_PASS_NOT_RAW_REPRODUCED`.

This is **operator-supplied terminal evidence**, not independent receipt
of the underlying JSON, and does NOT establish raw-data/model reconstruction
or historic confidence interval replication.

## G0.3 bootstrap next
- A pinned-code bootstrap wrapper exists at `research/reviews/icomputing_2026/ic_g0_bootstrap.py`.
- It verifies the preceding G0.2 gate, rediscovered input SHA256, and the original runner Git blob hashes.
- Instructions: `G0_3_BOOTSTRAP_RUNBOOK.md`.
- Outputs aggregate-only verification JSON plus locally retained bootstrap distributions.
- State: NOT EXECUTED by the assistant; awaiting operator-run results.

## 2026-10-27 G0.3 news-cluster bootstrap: operator-reported PASS

The operator ran the pinned historical code through `ic_g0_bootstrap.py --cluster news` on their trusted local Mac using the recovered data. Complete visible terminal output establishes:

| Cohort | Rows | news_id clusters | Replicates | Infeasible | Point delta mean | Point delta hit | Verification |
|---|---:|---:|---:|---:|---:|---:|---|
| V2 | 4,449 | 575 | 10,000 | 0 | 0.14429480582475662 | 0.5788288288288288 | PASS |
| V3 | 2,827 | 398 | 10,000 | 0 | 0.14943748898804188 | 0.5851063829787234 | PASS |
| V4 | 40,320 | 5,526 | 10,000 | 0 | 0.027561593800783157 | 0.10168650793650791 | PASS |

The wrapper output states `G0 news: BOOTSTRAP_REPLAY_PASS`, meaning the historical 95% CI endpoints and feasibility gates matched its stored contract checks (within 1e-8); the terminal does not display each CI endpoint. Local-only aggregate paths:
`$HOME/dtrm-ic-audit/bootstrap/IC_G0_bootstrap_news_aggregate.json`
`$HOME/dtrm-ic-audit/bootstrap/IC_G0_bootstrap_news_verification.json`.
JSON source not independently transferred or inspected; claim classification is **operator-reported verified local execution**, not assistant-executed reproduction.

**Open gate**: ticker-cluster bootstrap G0.3 not yet executed/reported. G1 independent temporal holdout not authorized. Nothing in this replay establishes independently spaced 60-day targets or removes the V2/V4 ticker CI concern.

## 2026-10-27 G0.3 ticker-cluster bootstrap: operator-reported PASS

Operator terminal transcript shows exact frozen ticker-cluster bootstrap replay:
- V2: 4,449 rows, 108 ticker clusters, 10,000 replicates, 0 infeasible; point delta +0.14429480582475662; PASS.
- V3: 2,827 rows, 125 ticker clusters, 10,000 replicates, 0 infeasible; point delta +0.14943748898804188; PASS.
- V4: 40,320 rows, 171 ticker clusters, 10,000 replicates, 0 infeasible; point delta +0.027561593800783157; PASS.
- Terminal final: `G0 ticker: BOOTSTRAP_REPLAY_PASS`.
- Historical CI checks in the wrapper passed; precise CI endpoints are held in local operator JSON rather than reproduced in terminal.

**Checkpoint conclusion**: G0.1 file recovery PASS; G0.2 point-estimate replay PASS; G0.3 frozen news- and ticker-cluster CI bootstrap replay PASS (60,000 aggregate bootstrap draws in total). These are *operator-reported local executions*, not new out-of-sample evidence or a raw upstream-model reconstruction. Do not treat ticker-level significance or independence as established; V2/V4 95% ticker CIs include zero. The main reviewer objection remains OPEN.

**Next**: G1.0 outcome-blind availability-only inventory of post-June event data, immutable ranker artifacts, and market-price snapshot *metadata*. No prospective test may read outcomes until a predeclared disjoint window is locked and feasibility documented.

## 2026-10-27 G1.0 initial metadata-only inventory: operator-reported

Command scanned two local directories without reading scientific file contents:

| Root alias | Files visited | Categorized | Post-July dated filenames | Last named event/newspaper date |
|---|---:|---:|---:|---|
| dtrm-fund | 497 | 41 | 0 | 2026-06-14 |
| theresistance-back | 450 | 7 | 0 | none determinable in this scan |

Category counts in `dtrm-fund`: event_ticker_pairs=3; features_and_embeddings=9; frozen_models_or_model_metadata=2; news_snapshots=2; other_dated_research_artifacts=6; price_snapshots=6; signals_and_predictions=6; targets_metadata_only=7. None contained post-July date tokens in their **filenames**.

The `theresistance-back` root had 4 frozen_models_or_model_metadata, 2 news_snapshots and 1 price_snapshots but no date tokens in names.

Terminal status: `G1: METADATA_INVENTORY_ONLY_NO_NEW_RESULTS`, no outcome values opened. **Do not interpret this as proof that every record ends in June**. File naming may omit dates, and other source locations were not scanned.

### G1.1 decisions still open
- Locate August/September news-event source and market-price snapshot metadata in other authorized local DTRM directories, with no outcome access.
- Audit whether the historical XGBoost and quantile boosters exist as saved model files. Frozen bootstrap/selection replay uses saved predictions and is NOT evidence that frozen models can score a new cohort. Published source runners call `xgb.train`; no explicit `save_model` was found in `run_exante_baseline_v0.py` or `run_probabilistic_xgb_v0.py`.
- If weights are absent, any reconstructive deterministic training must first recreate **historic predictions** within a frozen predeclared tolerance on existing rows, using only historical TRAIN/VALID. It cannot be called frozen-model inference until equivalence is demonstrated. No holdout access until then.
- Prospective window remains UNSPECIFIED and UNAPPROVED; no prospective returns, alpha, filter effectiveness or feasibility outcomes examined.
