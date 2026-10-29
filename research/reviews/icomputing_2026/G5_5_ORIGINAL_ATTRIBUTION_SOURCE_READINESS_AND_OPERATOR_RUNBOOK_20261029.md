# G5.5 — Original-source attribution audit: factual progress, next hard gate and operator runbook

**Date:** 2026-10-29 | **Journal case:** ICOMPUTING-D-26-01069.
**Working decision:** proceed with original-data source audit, NOT new synthetic superiority experiments.
**Current state:** **PUBLIC ORIGINAL CODE + READ-ONLY HASH/METADATA PROGRAM PASS; PRIVATE LOCAL INPUTS STILL UNREAD**. No new empirical efficacy/economic results and no movement to 85/100 claimed.

## Actually executed on original GitHub source

- Original frozen scientific commit: `c7502a690162459cdfb3413573e3133c42efb126`. The five underlying original frozen source **Git blob hashes** were fetched directly for that commit, then compared to the current review branch and embedded immutably in the G5.5 source audit; **all five match**. CI uses `git hash-object` so it does not incorrectly depend on the historical commit object being available in a shallow checkout. Frozen commit itself is **not reloaded in each CI run**; the original blob identities were verified against the exact historic GitHub ref once in this review.
- Five original sources cover the point and P10 ranker experiments, original Phase II observed target, raw 60d stock-minus-beta×SPY target construction, and TRAIN-derived 1/99% clipping plus TRAIN ticker demeaning.
- Five prior research reader modules include original V2/V3/V4 continuous P10 saved signals, original matching/paired identity, date-restricted continuous volatility reconstruction, and V0 P10 validation source reader. Source-lineage audit passes nine structural AST checks, without opening any original data.
- GitHub Actions **40853396127** on commit `56034cf2333523650c99b8d264a28d9fbe073e0a` **36/36 tests PASS**, project-wide Tests also PASS. Negative fixtures deliberately alter SHA-bound source files, remove P10, break the target transformation, mutate a six-file manifest and attempt invalid/path-escaping entries, all fail closed.
- The stage 1 private-local source report checker `ic_g5_5_private_source_metadata_gate.py` is written and tested on **fake bytes only**. This checks original G3.1 SOURCE report exact SHA, original V2/V3/V4 signal+target files' SHA/size, the original TRAIN model-row SHA, existence of the original TRAIN full row/news/embedding files and the July-5 price-cache directory. It does **not** deserialize any Pickle or access numeric outcomes. **It has not been executed on the owner's actual Mac/private source files.**

## Actual original-source topology

- Original cohort signal/target files: `~/Desktop/DTRM_Lab/dtrm-fund/research/local_data/`.
- Original 6-file lineage report: `~/dtrm-ic-audit/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json`, SHA `3130207406a81417c79f4ae69a0d02c1d0933044381280ec9dd9b99862a4e5a8`.
- Original model row source: `legacy_model_rows_2026-05-01.pkl`, SHA `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
- Original TRAIN news+embeddings and historical stock close cache: `~/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs/`.
- The original `preprocess_legacy_targets()` in frozen `src/dtrm/legacy_target_preprocessing.py` returns TRAIN `ticker_means` and `clip_lower/upper`. These exact per-ticker centers need to be reconstructed from authentic TRAIN rows and authentic original archived close series. **Do not calculate on V2/V3/V4 evaluated targets.**
- The original G3.1 join exposes continuous `p10_calibrated` and original raw `baseline_prediction` in memory; the G3.2 source-only module computes trailing volatility from pre-event closes. P10 source software is verified, original continuous *numerical* arrays are still owner-local and not accessible in this cloud CI.
- The G3.1 V0 source-only reader reconstructs **P10 validation**, not the matching **point-model V0 distribution** required to fix soft-risk score scaling. Thus the information-parity feasibility gate remains open until the original point model is reconstructed and original V0 information is validated against a bound source; do not substitute cohort score IQR after seeing outcomes.

## One read-only Mac command for stage 1 (WHEN OWNER CHOOSES TO EXECUTE)

This command performs SOURCE HASHING / FILE METADATA ONLY. It does NOT unpickle the private sources, return any market data, or authorize a historical scientific comparison. It never overwrites an earlier report.

```bash
cd "$HOME/Desktop/DTRM_Lab/dtrm-fund"
git fetch origin research/ic-g5-3-information-parity-20261029
# Use a separate clean worktree if local changes exist:
git worktree add --detach "$HOME/dtrm-ic-g55-worktree" origin/research/ic-g5-3-information-parity-20261029
cd "$HOME/dtrm-ic-g55-worktree"

AUDIT="$HOME/dtrm-ic-audit"
TRAIN="$HOME/Desktop/DTRM_Lab/dtrm-fund/research/local_data"
OUTS="$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs"
REPORT="$AUDIT/g1-reconstruction/IC_G55_original_private_source_metadata_only.json"

python3 research/reviews/icomputing_2026/ic_g5_5_private_source_metadata_gate.py \
  --source-only-report "$AUDIT/g1-reconstruction/IC_G3_1_A2_A6_original_source_only_gate.json" \
  --original-local-data "$TRAIN" \
  --legacy-outputs "$OUTS" \
  --original-price-cache "$OUTS/price_cache_fmp_pickle" \
  --out "$REPORT"

shasum -a 256 "$REPORT"
```

**Privacy:** report contains original source basenames and SHA256 commitments, not individual observations or absolute local paths; however source hashes and project metadata should be handled as private audit metadata, not automatically uploaded to a public PR. Running it is purely optional until the owner has access to local files.

## Exact next original-data scientific gates (not yet run)

**G5.6 — TRAIN-only centering reconstruction:** source-hash original model train rows and TRAIN raw-target construction from original historical price cache, then obtain TRAIN-only 1%/99% clip boundaries and per-ticker TRAIN means. Verify original V0/V2/V3/V4 frozen preprocessing/source parity without tuning on old outcomes. New separate authorization and protected trusted Pickle handling required before execution.

**G5.7 — Independently protected old-cohort attribution:** after distinct explicit old outcome authorization, source fingerprint every original signal/target + price and open only originally approved V2/V3/V4 sources; recompute original q25/K10 parity on original float32; report all 3 cohorts and no exclusions:
`Δ transformed Y_model = Δ clipped forward beta-adjusted target − Δ TRAIN ticker means`.
Keep both hard-veto vs soft-risk information-matched comparison only if original V0 point/risk calibration verified. Include negative/infeasible results and dependence-aware uncertainty; classify **POST-OUTCOME EXPLORATORY**.

**Economic gate:** separate from G5.7. Raw stock return, corporate action basis, event-time entry/exit prices, acquisition-time archive vintage, actual cash/fees/capital turnover have not been independently authenticated. Do not claim raw return/portfolio P&L from clipping inverse or re-labeled Y_model.

## Required editorial treatment

Original *Intelligent Computing* science score remains anchored to G4.12 independent 64/100 baseline; author-held G5.1/G6.1 documentary work might provisionally lift to ~67/100, **not 85 achieved**. Real additional numerical G5.7 source evidence may improve the weighted rebuttal only after independent audit and crossed G5/G6 line references. This is a bounded original empirical financial-news question, not new original mathematics of clipping nor demonstrated Human Clause human-vs-AI causal benefit.

The review must remain submit-ready before author-reported **2026-11-25 deadline**. No arbitrary new code/data source substitute will be used solely to inflate the 85 target.
