# Intelligent Computing — G1.2 historical model reconstruction gate

Date 2026-10-27; manuscript ICOMPUTING-D-26-01069.
No new temporal holdout has been authorized.

## Structural finding from the operator's local model audit
Seven structurally valid XGBoost JSONs are unrelated or unproven:
- `trump_score_xgb_excess_beta.json`: 389 features, `binary:logistic`, 81 trees
- `trump_score_xgb_reg_excess_beta.json`: 391 features, `reg:squarederror`, 217 trees
- `trump_score_xgb_reg_excess_beta_30d.json`: 391 features, `reg:squarederror`, 52 trees
- `trump_score_xgb_v1.json`: 384 features, `binary:logistic`, 107 trees
- `trump_score_xgb_v1_excess.json`: 384 features, `binary:logistic`, 189 trees
- `trump_score_xgb_v1p1_excess.json`: 414 features, `binary:logistic`, 68 trees
- `trump_score_xgb_v1p2_excess.json`: 414 features, `binary:logistic`, 55 trees

None is a 390-feature `reg:quantileerror` P10 model or a
390-feature `reg:squarederror` frozen HDPG point ranker.
These are **not interchangeable** with published HDPG models.

## G1.2 control
- Source = immutable original git commit `c7502a690162459cdfb3413573e3133c42efb126`.
- Do not modify original repository, historical tags, local data or MM1/Phase IV.
- Preflight checks pinned source, clean working tree, original historical inputs,
  174 files matching price snapshot suffix `_2026-07-05.pkl`, package versions;
  does not load data.
- Rebuild option (later, only after preflight review): original ex-ante point ranker,
  original full P10/P50/P90 XGBoost quantiles using only original historical
  dataset/masks and train/valid. Reproduce historical best iteration, validation
  Top-K, calibrated P10 validation offset and weighted P25 threshold.
- Reconstructed models must be saved only under a private
  `reconstructed_UNAPPROVED` directory and checksummed. Exact row-by-row
  correspondence to historical signals is a **separate mandatory gate**.
- Historical point replay plus bootstrap CI replay do not establish weights.
- A model re-trained retrospectively is a reconstruction and must be
  represented as such in the revised paper, even if numerical parity passes.
- New holdout data/returns are not inspected at this stage.

## Operator step — preflight only
From `~/Desktop/DTRM_Lab`:

```bash
AUDIT="$HOME/dtrm-ic-audit"
FROZEN="$AUDIT/frozen_source_c7502a"
if [ ! -d "$FROZEN/.git" ]; then
  git clone "https://github.com/dtrm-research-lab/dtrm-fund.git" "$FROZEN"
  git -C "$FROZEN" checkout --detach c7502a690162459cdfb3413573e3133c42efb126
fi

curl -fsSL \
  "https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g1_reconstruct.py" \
  -o "$AUDIT/ic_g1_reconstruct.py"
python3 -m py_compile "$AUDIT/ic_g1_reconstruct.py"

python3 "$AUDIT/ic_g1_reconstruct.py" \
  --mode preflight \
  --frozen-repo "$FROZEN" \
  --legacy-local-data "$PWD/dtrm-fund/research/local_data" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out-dir "$AUDIT/g1-reconstruction"
```

Required checkpoint: `IC_G1_2_preflight.json`.
No training is authorized until checking source state and Python package versions.

## Later operator step — only after preflight accepted
```bash
python3 "$AUDIT/ic_g1_reconstruct.py" \
  --mode rebuild \
  --frozen-repo "$FROZEN" \
  --legacy-local-data "$PWD/dtrm-fund/research/local_data" \
  --legacy-outputs "$HOME/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs" \
  --out-dir "$AUDIT/g1-reconstruction" \
  --trust-historical-pickles
```
This step loads **trusted historical** Pickles and trains (potentially
resource-intensive) models. It deliberately does not touch newer outcomes.
Never treat `HISTORICAL_AGGREGATE_PARITY_ONLY` as final approval for
forward inference. The next gate requires individual row-level agreement
and historic feature ordering/mapping.
