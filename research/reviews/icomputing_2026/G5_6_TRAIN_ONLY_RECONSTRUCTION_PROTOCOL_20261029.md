# G5.6 — Original TRAIN-only ticker-centering reconstruction: protocol before any private-data execution

Date 2026-10-29. Scientific case ICOMPUTING-D-26-01069. Parent G5.5 original frozen source/code audit, PR #53.
**STATE NOW: TRAIN-ONLY NUMERIC RECONSTRUCTION NOT EXECUTED ON ORIGINAL PRIVATE DATA.**

## Exact method and source

Reuse the original frozen `c7502a690162459cdfb3413573e3133c42efb126` code, pinned by matching Git blob IDs, including original `order_selected_legacy_rows`, `forward_excess_beta_target`, `train_only_clip_bounds`, `_kahan_mean_float32`, and `preprocess_legacy_targets`.

1. Verify G5.5 local six-old-source+TRAIN-file SOURCE METADATA report first: it checks archive identity but **does not deserialize any Pickle**. Separately verify historical G2.9, G2.10, G2.12, G2.13, G2.6 source report SHA and the full **174** original July-5 price cache files SHA; no new current market prices or unbound replacement archive.
2. Pin original model rows `legacy_model_rows_2026-05-01.pkl` to original SHA `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`. The original `legacy_pairs_enriched_2025-01-01_2026-05-01.pkl` full-row archive must be declared unbound if its exact historical SHA cannot be recovered; never quietly treat existence as archival identity.
3. Require the operator to **explicitly approve trusted local pickle deserialization** in a clean, hash-verified environment, and separately acknowledge the 2026-07-05 price provider acquisition vintage and point-in-time adjustments remain unverified. This permission is **TRAIN-only input and price-source access, NOT old V2/V3/V4 outcomes**.
4. Reconstruct the **exact original ordered model rows** from the original full-row archive plus selected model rows using the frozen routine and pair keys. Verify no duplicates, exact selection and date, V0 VALID row count 19,880, and a nonempty TRAIN; keep TEST/VALID completely out of target generation.
5. For **TRAIN rows only**, reconstruct every raw `Y_raw = forward_return(stock, event+60d) - beta_pre * forward_return(SPY,event+60d)` with original 5-day tolerance. The stock and SPY original 2026-07-05 price snapshots are already historical and their acquisition vintage may be later than the events. This is retrospective source reconstruction, NOT proof of tradability.
6. Apply original TRAIN-only global q1/q99 clipping bounds, clip to float32, group in original row order by ticker, and apply the frozen **float32 Kahan-mean** routine to derive `mu_train[ticker]`. Do NOT recalculate using the original old 47,596 V2/V3/V4 target labels or VALID/TEST outcomes; do not retune thresholds after inspecting old cohort results.
7. Compare the TRAIN-derived means computed independently against `preprocess_legacy_targets(TRAIN, TRAIN_raw, empty VALID/TEST)` using the same original code, strict float32 dtype and original ticker row order, no force-cast to float64. Include sample N, ticker count, clip bounds, SHA of output **canonical ordered ticker/mean bit patterns** and source hashes; **do not serialize per-ticker means, raw returns, news IDs, event dates or price rows** to GitHub or user-facing report. Keep all numeric train arrays in memory and discard upon exit.
8. Fail closed if any hash, key order, source date/price, finite target, interpolation, model code version or numeric parity gate fails. No fallback to live price data, alternative quotes, different clipping or missing tickers.

## Fixed restrictions and inference limits

- G5.6 reconstructs **TRAIN-only ticker centers** but does not yet compute historical deltas. The later decomposition `ΔY_model = Δclipped_target − Δmu_train` for V2/V3/V4 needs explicit **new** old-outcome authorization plus original cohort row-order, model-target float32 parity, original source fingerprints and all observed null/adverse effects. Existing G3 consents do not implicitly approve this new experiment.
- G5.6 does not by itself provide a valid new 60-day heldout test, a second independent ranker, external vendor acquisition point-in-time provenance, raw absolute stock returns, cash/fees or realizable trading P&L.
- Small in-process engineering unit tests may use fabricated **fixture numbers only**. They NEVER count as real model efficacy evidence.
- Any historical comparison on already-consulted V2/V3/V4 outcomes stays **POST-OUTCOME EXPLORATORY**.
- The original G4.12 scientific rebuttal score remains unaltered by code/metadata readiness.

## G5.6 entry & exit status

Entry technical condition: frozen original code PASS (G5.5, 36/36 CI) and original six-file SHA-only gate program prepared. EXIT `G56_TRAIN_ONLY_ORIGINAL_TICKER_CENTERS_HASH_COMMITTED_NO_HELDOUT_ACCESS` requires the real private **source-only preflight** and separately signed operator approval to run the TRAIN-only numeric loader, genuine original source bytes and full method/float32 parity. This note/CI **cannot assert exit PASS before an actual Mac run**.

Owner-run command and required source file arguments will be described in G5.6 runbook. No manual copying of per-ticker returns or unredacted private model data to a public PR.
