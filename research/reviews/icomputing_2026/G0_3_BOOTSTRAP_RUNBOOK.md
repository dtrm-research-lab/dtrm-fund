# G0.3 — Reproduce historical bootstrap confidence intervals

Date: 2026-10-27. Manuscript: ICOMPUTING-D-26-01069.
Prerequisite: G0.2 operator-reported point replay PASS for V2/V3/V4.

## Scope
- Use **byte-identical original code**, protected by Git blob SHA, from August 2026 tag commit `c7502a690162459cdfb3413573e3133c42efb126`.
- Exact legacy 10,000 replicates, original seeds (news=20260821, ticker=20260822), original Top-K=0.10 and original resampling logic.
- Bootstrap **not** evidence of temporal independence; this confirms historical CI repeatability.
- No raw data moves to GitHub, no retraining, no new threshold fitting.
- Original confidential Pickle artifacts are loaded locally; `--trust-local-pickles` must be explicitly provided.
- Old scientific tags and original local datasets are read-only. Audit outputs are separate.

## One-time setup
```bash
mkdir -p "$HOME/dtrm-ic-audit/frozen_runners" "$HOME/dtrm-ic-audit/bootstrap"
COMMIT="c7502a690162459cdfb3413573e3133c42efb126"
URL="https://raw.githubusercontent.com/dtrm-research-lab/dtrm-fund"

curl -fsSL "$URL/research/ic-major-revision-2026/research/reviews/icomputing_2026/ic_g0_bootstrap.py" \
  -o "$HOME/dtrm-ic-audit/ic_g0_bootstrap.py"
for name in run_phase2_primary_bootstrap.py run_phase2_ticker_bootstrap.py; do
  curl -fsSL "$URL/$COMMIT/research/experiments/$name" \
    -o "$HOME/dtrm-ic-audit/frozen_runners/$name"
done
python3 -m py_compile "$HOME/dtrm-ic-audit/ic_g0_bootstrap.py" \
  "$HOME/dtrm-ic-audit/frozen_runners/run_phase2_primary_bootstrap.py" \
  "$HOME/dtrm-ic-audit/frozen_runners/run_phase2_ticker_bootstrap.py"
```

## Repeat original news-cluster CI
```bash
python3 "$HOME/dtrm-ic-audit/ic_g0_bootstrap.py" \
  --search-root "$HOME" \
  --discovery-manifest "$HOME/dtrm-ic-audit/IC_G0_discovery_manifest.json" \
  --point-replay "$HOME/dtrm-ic-audit/IC_G0_point_replay.json" \
  --frozen-runner-dir "$HOME/dtrm-ic-audit/frozen_runners" \
  --out-dir "$HOME/dtrm-ic-audit/bootstrap" \
  --cluster news \
  --trust-local-pickles
```

## Repeat original ticker-cluster CI
```bash
python3 "$HOME/dtrm-ic-audit/ic_g0_bootstrap.py" \
  --search-root "$HOME" \
  --discovery-manifest "$HOME/dtrm-ic-audit/IC_G0_discovery_manifest.json" \
  --point-replay "$HOME/dtrm-ic-audit/IC_G0_point_replay.json" \
  --frozen-runner-dir "$HOME/dtrm-ic-audit/frozen_runners" \
  --out-dir "$HOME/dtrm-ic-audit/bootstrap" \
  --cluster ticker \
  --trust-local-pickles
```

## Outputs and next gate
Share only `IC_G0_bootstrap_news_verification.json` and
`IC_G0_bootstrap_ticker_verification.json` (aggregate-only reports).
Keep distributions .npz and vendor data locally. Never upload .pkl/.npy.
Results **PASS** only if all six historical CI endpoints per cohort
(two CI metrics × two bounds, checked per arm) and feasibility match.
If mismatched, preserve the output and investigate. No retuning.

Once both pass: G0.3 can close as *historic bootstrap replay complete*;
G1 independent temporal validation remains a separate unexecuted stage.
