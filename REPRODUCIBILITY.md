# Reproducibility Guide — Beat the Machine / Intelligent Computing submission

This document describes how to reproduce the Phase 2 experiments supporting the manuscript **“Human-Defined Probabilistic Guardrails for Trustworthy AI Decision-Making in Financial Markets”** (SSRN preprint DOI: https://dx.doi.org/10.2139/ssrn.7328658).

The submission snapshot is derived from the frozen Phase 2 research state `dtrm-xgb-probabilistic-phase2-stats`. The raw financial-news and market datasets are **not redistributed** because they originate from commercial/vendor sources whose licensing terms prohibit public redistribution of the complete raw dataset. The repository instead provides the research code, frozen experimental contracts, statistical procedures, derived evidence summaries, and the exact specifications needed to reconstruct the licensed inputs and rerun the experiments.

## 1. What is publicly available

The repository contains:

- source code under `src/dtrm/`;
- experiment runners under `research/experiments/`;
- frozen Stage Contracts under `research/contracts/`;
- research configuration/reference files under `research/configs/` and `research/reference/`;
- derived evidence summaries under `research/reports/`;
- immutable historical research refs used by the manuscript, including:
  - `dtrm-baseline-exante-v0`;
  - `dtrm-xgb-probabilistic-v0`;
  - `dtrm-xgb-probabilistic-v1`;
  - `dtrm-xgb-probabilistic-v2`;
  - `dtrm-xgb-probabilistic-v3`;
  - `dtrm-xgb-probabilistic-v4`;
  - `dtrm-xgb-probabilistic-phase2-stats`.

The main Phase 2 statistical contract is:

`research/contracts/DTRM_XGB_PROBABILISTIC_PHASE2_STATS.yaml`

The principal evidence summary is:

`research/reports/DTRM_XGB_PROBABILISTIC_PHASE2_EVIDENCE.md`

## 2. What is intentionally not distributed

The following are not included in the public repository:

- raw Financial Modeling Prep (FMP) financial-news records;
- raw/licensed market-price downloads or vendor snapshots;
- API keys, credentials, tokens, or account information;
- vendor-proprietary source payloads whose licenses do not permit redistribution;
- private local caches containing those licensed records.

Researchers must obtain equivalent source access directly from the relevant provider(s) under their own license.

## 3. Software environment

The frozen research code targets Python 3.10 or later. The experiment runners use, at minimum:

- Python >= 3.10;
- NumPy;
- pandas;
- XGBoost 3.0.2 for the frozen Phase 2 probabilistic implementation.

Install the package in editable mode from the repository root, then install the runtime dependencies required by the experiment runners if they are not already present in the local environment.

Example:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pandas xgboost==3.0.2
```

If the licensed input pipeline is regenerated from raw news text rather than from a previously reconstructed embedding cache, use the same 384-dimensional Sentence-BERT representation documented in the manuscript/Paper I. The frozen Phase 2 runners consume the reconstructed embedding cache as an input artifact; they do not download vendor data or regenerate the original news corpus automatically.

## 4. Licensed-source reconstruction

### 4.1 Financial news

Reconstruct the event-driven news corpus from the same commercial/vendor source family used by the study (Financial Modeling Prep financial-news endpoints).

The Phase 2 baseline runners expect a reconstructed news table covering the historical model period used in the study. The frozen research artifact naming convention includes:

`news_2025-01-01_2026-05-01.pkl`

At minimum, each retained news record must preserve:

- a stable `news_id`;
- publication timestamp/date;
- full news text (`news_text` in the frozen runner);
- ticker/company association needed to create event–ticker pairs;
- source provenance sufficient to audit the record.

The original DTRM event pipeline applies the strategic-actor/equity relevance logic documented in Paper I. Researchers should reproduce the same retention and ticker-mapping logic before constructing the model rows.

### 4.2 Event–ticker rows

The frozen baseline consumes two reconstructed artifacts under `research/local_data/`:

- `legacy_pairs_enriched_2025-01-01_2026-05-01.pkl`
- `legacy_model_rows_2026-05-01.pkl`

The model-row table must preserve, at minimum, the fields consumed by the frozen runners:

- `news_id`;
- `ticker`;
- `date_dt`;
- `beta_pre`;
- `split` (`train`, `valid`, or `test`).

The full enriched pair table is used to recover the exact legacy ordering before model-selected rows are retained. Duplicate event–ticker pairs must not be introduced.

### 4.3 Text representation

The frozen feature vector contains **390 variables**:

- 384-dimensional Sentence-BERT embedding;
- 5 lightweight text statistics;
- pre-event beta (`beta_pre`).

The contemporaneous/future-dependent market-return feature `ret_spy_evt` is excluded from the ex-ante baseline.

The frozen runners expect the following embedding-cache artifacts:

- `news_emb_2025-01-01_2026-05-01.dat`
- `news_emb_shape_2025-01-01_2026-05-01.pkl`
- `news_emb_index_2025-01-01_2026-05-01.pkl`

The embedding index must map the reconstructed `news_id` values to the corresponding rows of the 384-dimensional embedding matrix.

### 4.4 Market prices

Reconstruct adjusted/closing price histories for every required equity plus `SPY`, using the same source convention as the study. The frozen runners consume a local price cache in which each ticker file contains at least:

- `date`;
- `close`.

The ex-ante baseline runner documents a fixed historical snapshot suffix `2026-07-05`; subsequent Phase 2 holdouts use their frozen price-snapshot specifications recorded in the Stage Contracts. For example, V2 records a `2026-08-10` snapshot and 174 assets including SPY.

Ticker normalization must follow each frozen contract. Example: `BRK.B` is normalized to `BRK-B` in the V2 holdout.

## 5. Target construction and leakage control

For each event–ticker observation, the predictive target is the **60-day forward excess-beta return**:

`stock forward return - beta_pre × benchmark forward return`

where the benchmark is SPY and the target horizon is 60 days with the frozen price-tolerance rule used by the runners.

To preserve the ex-ante design:

- no information unavailable at prediction time may enter model features;
- chronological splits/embargo logic from the frozen data construction must be retained;
- target clipping bounds and ticker de-meaning must be learned on TRAIN only;
- validation information may be used only where the Stage Contracts explicitly permit it;
- holdout outcomes must not be used to retune model, threshold, ranking rule, Top-K fraction, or cohort definition.

## 6. Path mapping for external reproduction

The experiment scripts are frozen research artifacts and retain the original author's local `OUTPUTS` path constant. External researchers should **change only filesystem locations**, not scientific parameters.

Two acceptable approaches are:

1. map/symlink the licensed reconstructed artifacts to the path expected by the frozen runner; or
2. edit only the local path constants so that they point to the researcher's licensed reconstruction directory.

A path-only modification must not change:

- data contents;
- ordering rules;
- model parameters;
- split labels;
- thresholds;
- Top-K fraction;
- holdout definitions;
- random seeds;
- statistical procedures.

Record any path-only modification in the reproduction log.

## 7. Frozen experimental sequence

The manuscript intentionally retains failed experiments as part of the evidence chain.

### Baseline — ex-ante deterministic ranking

Runner:

```bash
python research/experiments/run_exante_baseline_v0.py
```

Frozen contract:

`research/contracts/DTRM_BASELINE_EXANTE_V0.yaml`

Key expected properties include:

- feature count: 390;
- removed feature: `ret_spy_evt`;
- selected Top-K ranking iteration: 10;
- Top-K fraction: 10%.

### V0 — probabilistic replacement

Runner:

```bash
python research/experiments/run_probabilistic_xgb_v0.py
```

The P10/P50/P90 quantile models are calibrated. V0 is **not promoted** because replacing the deterministic ranking with probabilistic outputs does not improve the decision metric.

### V1 — absolute downside veto

Frozen rule:

`calibrated P10 > 0`

V1 is **not promoted** because the rule is infeasible out of sample: zero rows pass the veto in the frozen holdout. The experiment is closed without outcome-based threshold relaxation.

### V2 — relative downside veto

Frozen contract:

`research/contracts/DTRM_XGB_PROBABILISTIC_V2.yaml`

The candidate preserves the baseline ranking and accepts only rows satisfying:

`calibrated P10 >= -0.16665692627429962`

The threshold is the weighted 25th percentile of calibrated P10 estimated on the frozen V0 validation distribution. The ranking is then walked in original order until Top-K = 10% is filled.

Expected V2 result:

- rows: 4,449;
- Top-K: 444;
- baseline Top-K mean: -0.1949552297592163;
- candidate Top-K mean: -0.050660423934459686;
- delta: **+0.14429480582475662**.

### V3 — prospective replication

Apply the identical V2 rule and threshold to the next untouched temporal cohort. No threshold retuning or model retraining is allowed.

Expected delta Top-K mean:

**+0.14943748898804188**

### V4 — long-window robustness

Apply the identical frozen rule to the substantially longer V4 cohort.

Expected delta Top-K mean:

**+0.027561593800783157**

## 8. Dependency-aware statistical analysis

After V2–V4 are frozen, execute the pre-specified statistical runners.

### Primary news-event cluster bootstrap

```bash
python research/experiments/run_phase2_primary_bootstrap.py
```

Frozen parameters:

- cluster: `news_id`;
- replicates: 10,000 per cohort;
- seed: `20260821`;
- confidence level: 95%;
- percentile interval;
- recompute K and both selections inside every replicate;
- all candidate selections must fill the full Top-K.

Expected 95% intervals for delta Top-K mean:

- V2: `[0.12422081055119634, 0.1529691657051444]`
- V3: `[0.12443295484408737, 0.16876715365506242]`
- V4: `[0.020819739997386934, 0.032413393817842]`

### Ticker-cluster sensitivity

```bash
python research/experiments/run_phase2_ticker_bootstrap.py
```

Frozen parameters:

- cluster: `ticker`;
- replicates: 10,000 per cohort;
- seed: `20260822`.

Expected 95% intervals for delta Top-K mean:

- V2: `[-0.006220224499702454, 0.19615343257319176]`
- V3: `[0.007538507026038135, 0.193316538631916]`
- V4: `[-0.010468163806945084, 0.07181955866981293]`

These results intentionally show that ticker-level uncertainty is wider and that V2 and V4 include zero.

### V4 weekly temporal robustness

```bash
python research/experiments/run_phase2_v4_weekly_robustness.py
```

The frozen ISO-8601 weekly partition retains all six weeks intersecting V4, including partial boundary weeks. Four of six weeks have positive delta Top-K mean. This analysis is descriptive and must not be interpreted as six independent trading experiments because the 60-day forward-return windows overlap.

## 9. Expected claim boundary

A successful reproduction should support only the manuscript's bounded claim:

> The frozen probabilistic downside guardrail shows reproducible incremental decision value across three untouched temporal tests, with dependency-aware uncertainty analysis.

The evidence does **not** establish:

- absolute profitability;
- positive expected return;
- universal human superiority over AI;
- uniform ticker-level robustness;
- invariant week-by-week superiority;
- statistically independent trading opportunities.

## 10. Reproduction checklist

Before comparing results, confirm that the reproduction satisfies all of the following:

- licensed vendor data obtained independently;
- source timestamps and ticker mappings preserved;
- exact event–ticker keys reconstructed without duplicates;
- 390-feature ex-ante representation used;
- `ret_spy_evt` excluded;
- same TRAIN/VALID/TEST labels and embargo logic retained;
- train-only preprocessing preserved;
- baseline ranking iteration 10 preserved;
- calibrated P10 offset preserved;
- relative veto threshold `-0.16665692627429962` preserved;
- Top-K fraction fixed at 10%;
- V2 rule reused without retuning in V3 and V4;
- bootstrap seeds and cluster definitions unchanged;
- failed V0/V1 experiments retained rather than omitted.

## 11. Audit anchors

For manuscript review and independent audit, use the frozen Stage Contracts and derived evidence files as the authoritative numerical anchors. In particular:

- `research/contracts/DTRM_BASELINE_EXANTE_V0.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_V0.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_V1.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_V2.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_V3.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_V4.yaml`
- `research/contracts/DTRM_XGB_PROBABILISTIC_PHASE2_STATS.yaml`
- `research/reports/DTRM_XGB_PROBABILISTIC_PHASE2_EVIDENCE.md`

These files define the experiment, frozen parameters, expected outputs, limitations, and maximum supported claim.

## 12. Contact

For questions about licensed-source reconstruction that cannot be resolved from the public audit trail:

**Urtzi Arana Santamaria**  
DTRM Research Lab  
dtrmresearchlab@gmail.com  
ORCID: 0009-0008-9926-5768

The author cannot redistribute vendor-protected raw records or credentials, but can clarify the public reconstruction protocol and audit artifacts.