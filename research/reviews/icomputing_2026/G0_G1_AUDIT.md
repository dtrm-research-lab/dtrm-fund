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

## 2026-10-27 G1.1 booster JSON structural audit: operator PASS for detection, **HDPG weights NOT FOUND**

- The operator executed `ic_g1_booster_audit.py` on the recovered original
  PCDoMoney/Outputs files.
- All seven candidate JSONs were structurally valid XGBoost models, but none
  is 390-feature point ranker or 390-feature quantile P10:
  389 binary classification; 391 reg:squarederror (two variants);
  384 binary classification (two variants); 414 binary classification (two variants).
- Outcome-blind finding: **do not reuse** these models as HDPG.
- Frozen source comparison establishes HDPG expected architecture: 390 features,
  `reg:squarederror` ranker iteration 10 and `reg:quantileerror` P10
  best iteration 18, fitted using 2025-01-01..2026-05-01 historical inputs.

### G1.2 new stage prepared; NO reconstruction yet
- Script `ic_g1_reconstruct.py`: pinned commit and pristine-tree input preflight;
  reconstruction mode for original historical training data; aggregate metric checks;
  outputs labeled `reconstructed_UNAPPROVED`, never promoted on aggregate agreement alone.
- Guide `G1_2_RECONSTRUCTION.md`.
- Operator asked to run **preflight only** before training; prior Python package
  versions and training inputs still need verification.
- No prospective labels, August+ cohort outcomes, or thresholds have been inspected.

## 2026-10-27 G1.2 pinned historical source preflight — OPERATOR PASS

Operator executed `ic_g1_reconstruct.py --mode preflight` from
`~/Desktop/DTRM_Lab`:
- Independent clone checked out pinned commit `c7502a690162459cdfb3413573e3133c42efb126` (detached HEAD).
- Exact CLI status: `G1.2: PRECHECK_ONLY`.
- Exact report path: `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G1_2_preflight.json`.
- Original training-input presence: `True`.
- Historical `*_2026-07-05.pkl` price cache: 174 files.
- Zero scientific Pickles opened and zero models trained by this step.
- Apparent `zsh: command not found: #` messages resulted from pasted interactive-shell comments, not the verification tool, and did not prevent preflight.
- Python package versions are present in the locally saved preflight JSON but not in the terminal excerpt; environment-version parity has NOT yet been assessed.
- This checkpoint confirms path/source prerequisites only. Reconstruction weights and row-wise prediction parity are still **OPEN**.

## 2026-10-27 G1.2 historical reconstruction — operator-reported 12/12 aggregate PASS

Operator's local versions: numpy=1.26.4; pandas=2.2.2;
xgboost=3.0.2; sentence-transformers=2.6.1.
After the successfully pinned-source G1.2 preflight, the operator invoked
`ic_g1_reconstruct.py --mode rebuild --trust-historical-pickles`.
The trainer used only historical TRAIN/VALID source inputs in
`~/Desktop/Play4Fun/PCDoMoney_Backend/Notebooks/Outputs`
and `dtrm-fund/research/local_data`; the original frozen commit was
`c7502a690162459cdfb3413573e3133c42efb126`.

Terminal shows `G1.2: HISTORICAL_AGGREGATE_PARITY_ONLY`;
all twelve checks were PASS:
390 features; original ranker best iteration/RMSE, selected Top-K
iteration/validation mean/hit, original P10/P50/P90 best iterations,
P10 best pinball, P10 VALID calibration offset and relative veto
threshold. Reconstructed boosters were saved locally in
`g1-reconstruction/reconstructed_UNAPPROVED/`, SHA references in
`IC_G1_2_rebuild.json`.

This is **NOT proof of rowwise prediction parity** or prospective
holdout independence. The next program `ic_g1_row_parity.py`
read-only compares historical V1/V4 40,320 rows with their independently
anchored original feature/signals, including explicit distinction between
the V1 absolute-zero veto and V4 relative-P25 veto. See
`G1_2B_ROW_PARITY_RUNBOOK.md`. This checker has NOT been executed
by operator yet. G1 remains open.

## 2026-10-27 G1.2b historic V1/V4 40,320-row parity — operator-reported PASS, provenance OPEN

Operator ran `ic_g1_row_parity.py` with original V1 feature matrix and signals,
source SHA256 anchors and rebuilt locally hashed boosters. Terminal:
- `G1.2b: HISTORICAL_NUMERIC_PARITY_PASS_PROVENANCE_PENDING`.
- Baseline ranking numeric row parity: 40,320/40,320 within 1e-6;
  maximum absolute difference **0.0**, mean absolute difference **0.0**.
- V4 P25 relative calibrated-P10 veto: 23,348 original and reconstructed
  eligible; **0 disagreeing flags** in 40,320 rows.
- V1 original strict-P10>0 veto: original 0 and reconstructed 0 eligible;
  **0 disagreeing flags** in 40,320 rows.
- Numeric reference columns `p10_raw` and `p10_calibrated` both exist
  in original signal artifact; **the previous G1.2b wrapper uses
  ANY matching numeric P10 column**, so this terminal output does not
  independently prove both P10 numeric series were within tolerance.
  The next check `ic_g1_dual_p10_check.py` requires both explicitly.
- Source feature matrix lacks pair-key labels; original source raw pair
  lineage is the next independent audit; `ic_g1_pair_keys.py`.
- No future outcomes, prices, post-June news or new holdout inspected.

**Interpretation:** exceptionally strong frozen-model numerical
reconstruction evidence, **not yet** provenance-certified new-inference
approval and not a new empirical gain claim.

## 2026-10-27 G1.2c strict P10 numeric parity — operator-reported PASS

The operator executed `ic_g1_dual_p10_check.py` on its pre-existing G1.2b
local JSON; it read neither new data nor Pickles:
- `baseline_40320 PASS`; max absolute numeric difference 0.0.
- `p10_raw_40320 PASS`; max absolute difference 0.0.
- `p10_calibrated_40320 PASS`; max absolute difference 7.450580596923828e-09.
- Both V1 zero-veto and V4 relative-P25-veto masks PASS.
- Terminal: `G1.2c: DUAL_P10_NUMERIC_PARITY_PASS_PROVENANCE_OPEN`.

All original historical **model numeric prediction** checks have
now passed to 1e-6 tolerance; original underlying event-to-feature
row mapping remains unproven.

## 2026-10-27 G1.2d original pair key/order comparison — NOT A SCIENTIFIC FAIL

The operator executed `ic_g1_pair_keys.py`; output:
- `G1.2d: V1_SOURCE_PAIRS_MISMATCH_OR_UNKNOWN`.
- `pairs_raw_2025-01-01_2026-06-06.pkl`: **265,145 rows**, columns
  `news_id`, `ticker`, **no `date_dt`**.
- `probabilistic_v1_holdout_signals_2026-06-06.pkl`: **40,320 rows**.
- The script required **identical row sets and order** across those files.
  That comparison is inappropriate if the 265,145 rows are a
  pre-filtered raw candidate universe. It cannot distinguish input-stage
  count from an actual lineage inconsistency. No new outcomes opened.
- **Separate, material provenance discrepancy:** the pinned historical
  `research/contracts/DTRM_XGB_PROBABILISTIC_V1.yaml` attributes
  `rows: 40320` to the file *with exactly that raw basename*.
  Local file has 265,145. This must be resolved, NOT silently rationalized
  as filtering; it might represent an upstream snapshot or changed file.

**Next diagnostic:** `ic_g1_source_subset.py` checks exact and narrowly
predeclared BRK.B->BRK-B normalized signal pair **membership** within
the larger raw universe, duplicate key counts, and ordered-subsequence
only where unambiguous. It preserves the raw file's current SHA256
as a new local anchor, clearly not an independent original commitment.
Even a full subset match does not prove historical inclusion/exclusion
rules or 390-feature embedding/beta row mapping.

**State:** Historical numerical model recreation = PASS. Source
provenance = OPEN. Prospective evaluation = NOT AUTHORIZED.

## 2026-10-27 G1.2e original raw→selected key membership: operator-reported canonicalized PASS; full provenance OPEN

The operator ran `ic_g1_source_subset.py` on trusted 2026 original local
raw-candidate pairs and the cryptographically anchored V1 40,320-row
signal cohort. No target outcomes, prospective news/prices, or model
inference were inspected. Terminal output:
- Status: `CANONICALIZED_SOURCE_SUBSET_MEMBERSHIP_ONLY_DERIVATION_PENDING`.
- Original raw candidate rows: **265,145**; V1 selected signal rows: **40,320**.
- Exact-key membership: **40,287/40,320**, **33 missing**.
- After the *pre-existing, historically documented* normalization
  `BRK.B → BRK-B`: **40,320/40,320**, **0 missing**.
- Raw pair duplicates: 0; V1 signal pair duplicates: 0.
- Raw subsequence ordering: **not tested** in this run (the exact-key
  test had missing keys); DO NOT report as an order match.
- V1 event dates: 2026-05-02T03:06:00Z through
  2026-06-06T22:22:29Z; both inside the historically declared V1 window.
- **Open contract discrepancy:** the frozen V1 YAML labels
  `pairs_raw_2025-01-01_2026-06-06.pkl` as containing 40,320 rows,
  but the found local file with that basename contains 265,145.
  Provenance/filtering/copy identity still unresolved. No historic
  anchor hash for raw pairs claimed.

Interpretation: all scored signal keys occur in the historical raw
candidate universe under the **declared** BRK.B alias; no novel key
transformation introduced. This is strong historical *membership*
corroboration; it does **not** independently recover the filtering
algorithm, event-to-embedding/5-text/beta feature row alignment, or
verify a new temporally independent test.

Next strictly outcome-blind G1.2f: evaluate canonicalized source
subsequence order, aliases and original beta/embedding manifest
structures; explicitly separate metadata-only and trusted-historical
file inspection. Prospective scoring remains UNAPPROVED.

## 2026-10-27 G1.2f next controlled local audit PREPARED (not executed)

Added `ic_g1_feature_provenance.py` and `G1_2F_FEATURE_PROVENANCE.md`.
The program requires G1.2e successful subset report, historical V4
pre-committed V1 SHA256 anchors for features/signals/beta, and the
new G1.2e local SHA for the original raw pairs. It checks normalized
raw input key uniqueness/order and historical feature dimension
390. If the V1 beta artifact has a recognized numeric/keyed schema
it compares the source beta_pre values to the final feature column at
historical float32 precision; otherwise it leaves a schema gate open.
The embedding manifest is only structurally inventoried. No old or
prospective outcome/return targets will be opened, and models are not
loaded or executed.

**No G1.2f result exists yet.** The original contract/raw file
265145-vs-40320 cardinality discrepancy, exact raw→selected filtering,
full embedding/text row mapping, and independent new holdout remain OPEN.

## 2026-10-27 G1.2f operator-run: canonical source row order and keyed beta column PASS

Operator ran `ic_g1_feature_provenance.py` on SHA256-anchored
original V1 inputs. Report:
`G1.2f: HISTORICAL_CANONICAL_PAIR_AND_BETA_LINKAGE_PASS_FULL_PROVENANCE_OPEN`.

- Raw source pairs **265,145**, selected V1 signal pairs **40,320**.
- Normalized raw pair duplicates: **0**; full normalized signal
  membership = **True**; all selected pair keys are an **ordered
  subsequence** of original raw source keys after historically declared
  `BRK.B → BRK-B` normalization.
- Precommitted V1 feature matrix **(40,320 × 390)**.
- Original `probabilistic_v1_holdout_beta_pre_2026-06-06.pkl`
  SHA256 `e39896db92f1bb7c8334f61a6eee7bc71f8acbd6b6e87504c388ae0b8b1463d8`
  verified and recognized as a 40,320×4 DataFrame with columns
  `news_id`, `ticker`, `date_dt`, `beta_pre`.
- Keyed by `(news_id, normalized ticker)`, **all 40,320 beta_pre
  values match the final feature column exactly**; max absolute
  difference **0.0**. This is keyed source correspondence, not merely
  same-position numeric comparison.
- Historical embedding provenance manifest exists:
  `probabilistic_v1_embedding_manifest_2026-06-06.pkl`,
  **5,526 × 3** DataFrame with columns
  `date_dt`, `embedding_source`, `news_id`, local SHA256
  `3c74994a08384ea009af36b4cf3bcef592c95a06daf2d9889b3eaef79b24e52e`.
  Hash is a **new local commitment**, not independently preanchored.
- No target values, realized returns, newer cohorts or model inference
  accessed by this step.

**Interpretation:** original 40,320 frozen V1 news/ticker keys are an
ordered subset of raw candidates, and the 390th feature is verified
against its historically preanchored original keyed beta table.
Unverified: 384 embedding values, five frozen text features,
original raw→selected filtering specification, historical V1 contract
raw basename claiming 40,320 when local raw source has 265,145.
These open issues must remain separate from completed numeric model
reconstruction. No forward holdout authorized.

Next: G1.2g outcome-blind, historical text feature recreation and
source-cache availability check. It MUST not infer fresh returns or
assume a particular embedding cache representation.

## 2026-10-27 G1.2g new gated historical text provenance checker PREPARED

- `ic_g1_text_provenance.py`: SHA-bound old V1 feature matrix/signals
  and trusted V1 2026-06-06 news snapshot only; direct import
  from pinned `c7502a6` original five-text-feature source;
  row-wise compare feature columns 385–389 at tolerance 1e-6.
- Metadata-only listing of original embedding-cache file basenames and
  sizes to inform next 384-dim source verification; it does not read
  embedding cache bytes or execute any model.
- `G1_2G_TEXT_PROVENANCE.md` runbook for operator.
- **Not yet executed.** No newly dated events, returns or targets
  opened. Separate V1 contract/raw basename cardinality discrepancy
  and full embedding/selection provenance remain OPEN.

## 2026-10-27 G1.2g operator PASS: original five-text-feature provenance

Operator ran the SHA-bound `ic_g1_text_provenance.py` against
historical V1 source and pinned original text-feature code.
- Status: `TEXT_FEATURE_5_OF_5_ROW_PARITY_PASS_EMBEDDINGS_OPEN`.
- Frozen V1 40,320 pairs; historical news snapshot
  `news_2025-01-01_2026-06-06.pkl`: 43,183 rows.
- All five historical text features in columns 385–389 (0-based
  384:389) reproduced for **40,320 / 40,320** observations;
  max absolute difference **0.0**; mismatches per feature:
  `[0, 0, 0, 0, 0]`.
- G1.2f previously verified keyed `beta_pre` against column 390,
  max absolute difference 0.0. Therefore all **six non-embedding
  columns** have historical source-level parity.
- Available historical embedding cache families, each with
  `.dat` + index/shape PKL, include `2026-06-06`
  (40,733,184-byte `.dat`) and `2026-05-23`
  (39,653,376-byte `.dat`).
- `probabilistic_v1_embedding_manifest_2026-06-06.pkl` was
  previously found: 5,526 news rows, columns
  `news_id`, `date_dt`, `embedding_source`.
- `probabilistic_v1_missing_embeddings_2026-06-06.pkl`
  exists (42,446 bytes); content/schema not yet verified.
- Original V1 contract documents three *intended* provenance
  counts: cache_2026-06-06 = 4,764;
  cache_2026-05-23 = 735;
  v1_reproduced_supplement = 27. These sum to 5,526, but are
  **not yet reconstructed or cryptographically tied** to the
  384×40,320 embedding feature block.
- No targets, outcomes, price series, post-June events, or fresh
  evaluation were inspected.

**Next G1.2h:** inspect, without matching vectors to targets,
the original index/shape/supplement schemas and count the exact
manifest-based source groups; then only if source mapping is
unambiguous attempt strict float32 embedding row parity. Frozen
raw filename contract cardinality still unresolved; prospective
evaluation remains NOT AUTHORIZED.
