# Intelligent Computing Major Revision — G0/G1 evidence audit (2026-10-27)

Manuscript: ICOMPUTING-D-26-01069. Revision due: 2026-11-25.
Stage status as of 2026-10-27: **G0 CLOSED (historic scope); G1 CLOSED WITH DOCUMENTED LIMITATION; G2 ACTIVE DRAFT/UNFROZEN; G3 NOT YET AUTHORIZED. NO NEW OUTCOME RESULTS.**

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

## 2026-10-27 G1.2h embedding-source inventory PREPARED; operator run outstanding

Created `ic_g1_embedding_inventory.py` and
`G1_2H_EMBEDDING_SOURCE_INVENTORY.md`. The program reads only
explicitly trusted historical manifest/cache shape-index/supplement
structures, compares news-ID coverage with preanchored V1
40,320-row signals, checks original documented 4,764+735+27
source counts and validates Nx384 float32 .dat file sizing;
cache files are SHA-hashed but vector values are not evaluated.
It exposes aggregate source counts and identifier types only.
**It has NOT been executed by the operator yet.**

Strict source labels must determine embedding sources before
any numeric reconstruction. No prospective holdout, return
labels or historic target values may be opened.

## 2026-10-27 G1.2h operator outcome: historical embedding SOURCE inventory PASS

The operator executed `ic_g1_embedding_inventory.py` against historical
V1 original trusted local inputs. Terminal status:
`G1_2H_MANIFEST_AND_CACHE_SCHEMA_PASS_EMBEDDING_VALUES_UNTESTED`.

- Frozen V1 signal unique news: **5,526**; manifest rows: **5,526**.
- Missing signal news from manifest: **0**; additional news in
  manifest: **0**.
- Exact historically declared embedding-source groups:
  `2026-06-06`: **4,764**; `2026-05-23`: **735**;
  `v1_supplement`: **27**.
- 2026-06-06 cache shape **26,519×384**, index **26,519** unique
  string news identifiers. All **4,764/4,764** manifest June
  news IDs exist in this cache; **2,467** June-selected IDs
  ALSO occur in May's cache. The manifest's June label MUST
  remain authoritative: do not choose vector source by
  numerical concordance.
- 2026-05-23 cache shape **25,816×384**, index **25,816** unique
  string identifiers. All **735/735** manifest May IDs exist
  in the May cache; none of the May-selected IDs exists in June's
  cache.
- `probabilistic_v1_missing_embeddings_2026-06-06.pkl`
  is a six-key dictionary with values of types:
  list (1), ndarray (1), str (2), bool (1), int (1).
  New local SHA256
  `1697fc009800b673edda43ede18373f96916934d05cc03f50d16363b19d118d3`.
  Neither an ID→vector mapping nor 27 supplement vector
  records has yet been verified. The G1.2h structural
  `supplement_structural_id_matches: 0` compares six metadata
  field names to news IDs, and **is not evidence of absent
  supplement news**.
- Both cache shapes/index offsets and .dat float32 byte sizes
  validated; no embedding numeric vectors, target outcomes, prices
  or prospective data were inspected.

**Scientific status**: historical source coverage structure PASS,
full 384-feature vector parity not yet run. G1.2i must first inspect
the six-field supplement schema without printing news IDs or vector
values. Do not infer metadata keys are the 27 missing event IDs.
The original V1 raw-pair filename/row-count discrepancy and full
filtering chain remain OPEN. Prospective scoring stays BLOCKED.

## 2026-10-27 G1.2i operator supplement-schema probe PREPARED; not yet run

Added `ic_g1_supplement_schema.py` and
`G1_2I_SUPPLEMENT_SCHEMA.md`. Requires G1.2h audit status
PASS and original historic manifest and supplement SHA256 anchors.
It inspects the six *supplement metadata dictionary fields*
only (types, array/list shape/count) and checks exact
27-news matching only for **explicitly named** ID list
fields. It does not read/export vector elements or invent
the supplement mapping. If schema names are not recognized,
result is `G1_2I_SUPPLEMENT_SCHEMA_NEEDS_EXPLICIT_MAPPING`,
not an efficacy failure.

This is not a new empirical validation; no model inference or
financial returns/targets inspected. G1.2j numerical V1
embedding replay and G1.3 independent temporal holdout remain OPEN.

## 2026-10-27 G1.2i supplement-ID/vector metadata — operator PASS

Operator ran `ic_g1_supplement_schema.py` on previously SHA256-hashed
original local V1 supplement and embedding-source manifest.
Exact status: `G1_2I_SUPPLEMENT_NAMED_SCHEMA_READY_FOR_PREDECLARED_MAPPING`.
The original supplement is a 6-field metadata dictionary:
- `news_ids`: list of **27 unique string news IDs**;
  **exactly identical set** to the 27 manifest source-labeled
  `v1_supplement` news identifiers.
- `embeddings`: ndarray **(27,384)**, dtype **float32**.
- `dtype`: str (length 7); `max_chars`: int;
  `model`: str (length 16);
  `normalize_embeddings`: bool.
- No vector values were compared, and no individual news IDs,
  predictions, targets, prices, or newer cohort inputs were exposed.

**Next check now prepared but not yet operator-run:**
`ic_g1_embedding_parity.py` and `G1_2J_EMBEDDING_PARITY.md`
carry out a strictly historical fixed-source 40,320×384
comparison using the original manifesto-specified cache or
supplement, both earlier audit hashes, and 1e-6 fixed
absolute tolerance. Mismatch stops progress, no cache reassignment.
A PASS, combined with G1.2f/g, would reproduce all 390
historical input features; **it would not prove the historical
raw→selected filtering rule or independent post-August holdout**.

## 2026-10-27 G1.2j — 40,320 × 384 original embedding parity EXACT (operator-reported)

The operator ran `ic_g1_embedding_parity.py` against the SHA-bound
original V1 `probabilistic_v1_holdout_features_2026-06-06.npy`,
original signal rows, original `embedding_source` manifest and
exactly the two declared historical caches plus source-labeled
supplement. Predecessor G1.2f (keyed beta), G1.2g (five original text
columns), G1.2h (cache/schema coverage), and G1.2i (27-ID/vector
supplement) all passed locally, as separately documented.

Exact CLI status:
`G1_2J_HISTORICAL_384_EMBEDDING_ROW_PARITY_PASS`.
- June 6 cache: **35,358 scored ticker–news rows**, max abs difference 0.0, 0 mismatches.
- May 23 cache: **4,753 scored rows**, max abs difference 0.0, 0 mismatches.
- 27-news original V1 supplement: **209 scored rows**, max abs difference 0.0, 0 mismatches.
- **TOTAL: 40,320 rows × 384 embedding dimensions = 15,482,880 coordinates**.
  Max absolute difference **0.0**, mean difference **0.0**,
  rows outside 1e-6 **0**, coordinates outside 1e-6 **0**,
  exactly equal coordinates **15,482,880 / 15,482,880**.
- Historical five original text features: 40,320 × 5, max abs
  difference **0.0**, no mismatches (G1.2g).
- Original keyed beta source vs feature column 390: 40,320 / 40,320
  matches, max abs difference **0.0** (G1.2f).
- Together these support **numerically exact reconstruction of
  all 390 input features** on the historically consumed V1 cohort:
  40,320 × 390 = **15,724,800** source-feature coordinates.
- G1.2b/c previously reproduced the original 40,320 row
  ex-ante ranker predictions exactly, raw P10 exactly,
  calibrated P10 at max abs difference 7.450580596923828e-09,
  and both historical V1/V4 veto masks exactly.
- The historical model weights were *retrained from frozen
  source/data*, not recovered as pre-existing serialized boosters.
  The observed original numerical predictions match but do not
  prove byte-identical original XGBoost tree weights.

**Scientific interpretation: HISTORICAL NUMERIC RECONSTRUCTION PASS.**
This is a *retrospective* historical reproducibility result, not
new out-of-sample efficacy, precommitted new cohort evidence,
or proof of profitability.

**Still open and separately tracked**:
1. Original 2026 V1 YAML attributes **40,320 rows** to the
   `pairs_raw_2025-01-01_2026-06-06.pkl` filename,
   while the local file of exactly that name has **265,145**.
2. The original exact raw→scored V1 cohort selection/filtering
   procedure remains uncaptured by the currently verified
   historical source contract (despite complete normalized
   pair membership and ordered-subsequence matches).
3. A completely independent and temporally nonoverlapping
   prospective 60-day test is NOT started nor authorized.
4. Source-cache/supplement local SHA commitments are newly
   observed during this audit, whereas the original V1
   features/signals have earlier independent V4 hashes.

Next: make a local hash-bound **evidence dossier** from the already
produced G0–G1.2j JSON reports and reconstructed candidate boosters
without any re-training or inspection of market outcomes.
Continue metadata-only investigation of original raw-pair source
provenance. No promotion to 'original saved model'.

## 2026-10-27 original V1 raw-source filtering: frozen repository scope verified

Inspected original pinned git tree at
`c7502a690162459cdfb3413573e3133c42efb126`
(105 tracked tree nodes) and its `research/experiments` scripts.
The original pinned repository includes historical train/validation
runners, quantile V0 and Phase II statistical reruns, but **no
dedicated V1 raw-pair snapshot selection/generation runner** that
materializes exactly the 40,320 selected V1 pairs from the 265,145
local raw pair candidates. Existing
`src/dtrm/legacy_model_rows.py` and `legacy_row_order.py`
specify a training-era prefilter/reordering mechanism; they do not
by themselves certify the later V1 cohort inclusion/filtering rule.

Thus historical V1 event-source selection evidence must be traced to
the old PCDoMoney notebook/backend acquisition and preprocessing
lineage or another original retained source artifact. Do NOT
reverse-engineer a 40,320 subset rule from signal outcomes and present
it as a preexisting frozen algorithm. The numerical input/prediction
reproduction is unaffected, but documentary completeness is OPEN.

G1.2k `ic_g1_seal_dossier.py` and
`G1_2K_EVIDENCE_DOSSIER.md` were created for the operator
to checksum-seal nine prior historical JSON audits and four
UNAPPROVED reconstructed model binaries; **not yet executed**.
It does not read raw scientific Pickles, new samples, or outcomes.

## 2026-10-27 G1.2k OPERATOR PASS — cryptographically sealed historical numeric dossier

The operator executed `ic_g1_seal_dossier.py` on nine previously
produced local G1.2 historical audit JSON reports and four
locally reconstructed, **UNAPPROVED** original-XGBoost candidates.
No scientific raw files, historical/future target outcomes, or
unseen news/price data were opened.

Exact terminal status:
`G1.2k: HISTORICAL_RECONSTRUCTION_390_FEATURES_AND_SIGNALS_PASS_PROVENANCE_OPEN`.

- Complete V1 original historical source input coordinates validated:
  **15,724,800 = 40,320 × 390**.
- Audit reports **9**; reconstructed candidate models **4**;
  verified their source histories and model SHA commitments
  against earlier local audit reports.
- Original source commit:
  `c7502a690162459cdfb3413573e3133c42efb126`.
- Local path (operator-only):
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G1_2_historical_dossier.json`.
- **Final dossier SHA256**:
  `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.

**Scientific disposition:** historical numerical reproducibility
fully **PASS** to original defined tolerances. Not original binary
model identity; not new-interval performance; no unconditional
ticker-cluster significance/realized trading profitability claim.

**Remaining blockers:** (A) original V1 raw-pair source file
265,145 rows versus 40,320 stated in pinned V1 contract,
and exact original raw→40,320 filtering/copy lineage; (B) new
non-overlapping time-window cohort, frozen pre-outcome registered
protocol and data/forward 60-calendar-day maturity.

Next: G1.2l metadata-only original notebook/backend lineage
discovery; G1.3 **draft** preregistration and feasibility audit.
Do not authorize prospective scoring or future target inspection
from this PASS.

## 2026-10-27 G1.2l source-discovery + G1.3 outcome-blind design PREPARED, not operator-run

Added:
- `ic_g1_raw_lineage_discovery.py` and
  `G1_2L_RAW_LINEAGE_DISCOVERY.md`: safe bounded, **source-file-only**
  search under original PCDoMoney Backend and dtrm-fund for the
  actual V1 265145→40320 provenance/selection pipeline.
  Original notebook **filenames only**, not notebook contents;
  no .pkl/.npy/memmap scientific data nor return labels read.
  **This script has NOT been executed**. Any candidate references
  require source chronology corroboration.
- `G1_3_INDEPENDENT_TEMPORAL_PREREG_DRAFT.md`: UNFROZEN
  preregistration design with fixed original relative P10
  threshold, ex-ante ranking, 60 **calendar** day target window
  and +5-day original future-price alignment tolerance.
  Distinguishes genuinely future-prospective vs new retrospective
  outcome-blind temporal holdout; the latter is not prospective.
  No new event dates, data provider, price maturity, cohort hash,
  preregistered cutoff or independence status has been certified.
- Research paper ICOMPUTING-D-26-01069 deadline **2026-11-25**;
  late October 2026 newly started 60-day genuinely prospective
  observations cannot all mature before this deadline. A
  retrospective new-date, genuinely outcome-uninspected check
  may be possible IF inputs/outcome-blindness are established;
  never mislabel it forward prospective.
- G1.2k sealed dossier unchanged at
  SHA256 `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.

**Study G1.3 status: DRAFT, NOT PREREGISTERED/FROZEN;
NEW TARGET SCORING BLOCKED.**

## 2026-10-27 G1.2l operator source-reference inventory completed; no original generator identified

The operator ran the code-source-only
`ic_g1_raw_lineage_discovery.py` with existing local
`dtrm-fund` and `PCDoMoney_Backend` source trees.
- Status printed: `SOURCE_LINEAGE_REFERENCE_INVENTORY_ONLY`.
- **301** source/documentation text files searched.
- **5** potentially relevant files, all high-level old contracts,
  Phase II bootstrap/evidence reports, or a Phase III document.
  None provides an identified historically dated complete V1
  raw→selected file generation algorithm.
- **33** notebook *filenames* inventoried; their contents,
  output cells and code cells were NOT inspected.
- No Pickles, target returns, future prices, embedding matrices,
  notebook contents, or model execution read at G1.2l.
- Metadata-only search alone does not certify source provenance;
  original 265,145-vs-40,320 file cardinality inconsistency is OPEN.

Next G1.2m controls a single *previously declared* historical
calendar-holdout window test, 2026-05-02 ≤ news UTC event_date
< 2026-06-07, using source June 6 news dates and the exact
original BRK.B→BRK-B alias. The hypothesis is independent of
outcomes and must not be tuned to reconstruct 40,320.

`ic_g1_declared_date_filter.py` and
`G1_2M_DECLARED_DATE_FILTER.md` have been committed
BEFORE the local operator test; **G1.2m not yet run**.
Even an exact source/date/key/order match would remain
structural corroboration, not authenticated original
generation code. The 33 notebook code cells can be separately
inspected ONLY if source provenance remains open,
without execution or access to notebook output cells.

G1.3 prospectively scored independent 60-calendar-day
event cohort still unregistered and BLOCKED. The
previously sealed historical evidence dossier
SHA256 remains `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.

## 2026-10-27 G1.2m ORIGINAL-DECLARED DATE FILTER: OPERATOR PASS, SOURCE CODE STILL OPEN

Operator executed the **precommitted, single historical-hypothesis**
`ic_g1_declared_date_filter.py` against original V1 source
Pickles (trusted local) and hash-verified G1.2e/G1.2g
predecessor reports. The only inclusion hypothesis tested
was V1's original declared event date window:
`2026-05-02 <= UTC news.date_dt < 2026-06-07`, with
historically recorded ticker alias `BRK.B -> BRK-B`.

Exact terminal status:
`V1_DECLARED_DATE_FILTER_EXACT_KEY_SET_AND_ORDER_PASS_SOURCE_CODE_OPEN`.

- Original raw candidate pairs: **265,145** (previously verified).
- Original full June-6 news snapshot ID joins missing: **0**.
- Date-window selected pairs: **40,320**, exactly the **40,320**
  precommitted original V1 signal pair observations.
- Pairs missing in derived window: **0**.
- Additional pair keys in derived window: **0**.
- Canonicalized `(news_id,ticker)` pair key sets identical: **True**.
- Raw-relative V1 row order identical: **True**.
- Source event timestamps agree with frozen signal dates: **True**.
- No alternative windows, target labels, forward 60-day
  returns, prospective news, model training or inference inspected.

**Disposition G1.2m: FROZEN-DATE-ONLY RAW→V1 SELECTION STRUCTURAL PARITY PASS.**

This resolves the **observational selection mechanism** to the
historically stated date restriction plus the already-frozen
ticker alias. It also supplies a plausible explanation for
the 265,145-vs-40,320 count difference: raw candidates across
the broader news snapshot versus scored event-date subcohort.
It does NOT independently authenticate the original notebook
that generated or copied the raw file, nor resolve why the
pinned V1 contract's `pairs_snapshot.file` with the same basename
was annotated `rows: 40320`. The historic source-file
filename/cardinality documentation discrepancy remains open,
and must be disclosed if relevant to a reviewer.

**Final current evidence split:**
- G1.2k historic 390-input/model reconstruction dossier PASS,
  SHA256 `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`
  **unchanged**; nine prior reports/4 rebuilt model binaries.
- G1.2m is **supplementary source-lineage evidence** and does
  not retroactively modify or relabel the sealed G1.2k JSON.
- Authentic V1 original generating-code and same-basename
  physical-file origin remains OPEN (documentary), no numerical
  discrepancy observed.
- G1.3 outcome-blind independent temporal validation remains
  NOT preregistered or authorized. Do not claim a new result.

## 2026-10-27 G1.3a feasibility discovery PREPARED; no new dataset opened

Created `ic_g1_3_news_source_inventory.py` and
`G1_3A_NEW_EVENT_INPUTS_INVENTORY.md`. They authorize a
strictly filenames-and-file-sizes-only scan of original
local research input roots for possible newer news/event
and embedding-cache artifacts. File contents (including
news, model weights, prices and returns) are not read,
and names containing price/target/outcome/return terms
are omitted from positive candidates. Any apparent
post-2026-06-14 filename date has NO demonstrated
event-date or acquisition-time validity.

Created `IC_G1_REVIEWER_REPRODUCIBILITY_EVIDENCE_DRAFT.md`
with a reviewer-safe summary of the now proven G1.2k
historical 390-feature/model numerical repeatability
and G1.2m exact declared UTC cohort-date filtering,
preserving unresolved physical original file source/copy
provenance and cross-ticker statistical limitations.

**G1.3a has NOT been executed by the operator.
G1.3 preregistration remains DRAFT; new inference and
all prospective target/return examination BLOCKED.**

## 2026-10-27 G1.3a operator metadata-only input-source search — NO NEW DATED NEWS FOUND

Operator executed `ic_g1_3_news_source_inventory.py` on
two original local roots:
`dtrm-fund/research/local_data` and
`PCDoMoney_Backend/Notebooks/Outputs`.

Status:
`G1_3A_FILENAMES_ONLY_AVAILABLE_NEWS_NOT_YET_VERIFIED`.

Filename-only categories:
- Embedding candidate, historic/consumed: **29**.
- Embedding candidate, undated filename: **1**,
  `sbert_embeddings_xgb_v1.npy`, 43,664,000 bytes,
  legacy-looking name — **not** proof of an untouched newer cohort.
- News/event candidate, historic/consumed: **10**.
- Pairs candidate, historic/consumed: **11**.
- **0** candidates with filename dates after 2026-06-14 in
  these two scanned roots.
- No file contents, market prices, returns, news text,
  outcome labels, model weights or inference inspected.
- G1.2m supplemental historic UTC declared-date filter report
  SHA256: `388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.
- G1.2k frozen historical reconstruction evidence dossier SHA256
  unchanged: `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.

**Scientific interpretation:** the two exact scanned local folders
contain NO **filename-dated** post-consumed-period news or
event-source candidates. The scan does not prove that new input
data are unavailable in other original repos, connected sources,
cloud storage, or undated filenames; nor that the undated
legacy SBERT matrix is a valid new cohort.

**Gate:** `G1_3_NEW_EVENT_INPUT_AVAILABILITY_NOT_DEMONSTRATED`;
do not preregister a made-up cohort or open forward labels.
Continue with only a bounded, metadata-only search in other
explicit local research locations and/or preserve a future
prospective ingestion plan. Meanwhile finish journal major
revision on independently verified historical reproducibility,
with original statistical limitations and transparent missing
new-cohort evidence.

## 2026-10-27 G1.3b broad local metadata scan — OPERATOR EXECUTED, NO ELIGIBLE NOVEL EVENT SOURCE

The operator reran the **same metadata-only** G1.3a inventory,
this time against broader roots:
`~/Desktop/DTRM_Lab` and `~/Desktop/Play4Fun`.
Tool status still `G1_3A_FILENAMES_ONLY_AVAILABLE_NEWS_NOT_YET_VERIFIED`;
G1.3b denotes broader search *scope*, not a distinct approved test.

Filename-category totals:
- 29 original dated/consumed embeddings; 10 dated/consumed news
  files; 11 dated/consumed pair files.
- **49 undated candidate paths**: 3 old/undated embeddings or
  SBERT classifier artifacts, 7 Phase IV **unit-test fixtures**,
  and 39 **PaymentGame** pair reports/receipts/validation,
  not HDPG event-ticker pairs.
- **Zero** files in filename-date `AFTER_CONSUMED_HOLDOUT_FAMILY`
  bucket. Detector handles YYYY-MM-DD and NOT compact
  YYYYMMDD, so some newer PaymentGame receipts
  are assigned `NO_DATE_IN_FILENAME`. Do **not**
  claim no newer *files* exist; rather, none is demonstrated
  to be a new HDPG **scientifically eligible event cohort**.
- No file contents, news IDs, prices, return labels, model
  weights, or evaluation outcomes accessed in the scan.

Decision: `G1_3_LOCAL_HISTORICAL_INPUT_DISCOVERY_STOP_NO_ELIGIBLE_NEW_COHORT`.
No original event-time news dataset with defensible point-in-time
availability and disjointness has been located under the
reviewed local roots. Stop additional speculative local
scanning; examine a specified external provider only if
a new acquisition/provenance project is separately authorized.

Created `G1_3B_BROAD_SOURCE_TRIAGE_STOP.md`.
G1.3 remains UNFROZEN and BLOCKED; prioritize scientific
revision of ICOMPUTING-D-26-01069 without invented external
validation results. Historical G1.2k dossier and G1.2m date-rule
evidence SHA256 values unchanged.

## 2026-10-27 Agentic Graph Engineering stage transition: G1 CLOSE → G2 OPEN

**The originally specified G1 exit condition was disjunctive**:
"independent holdout feasible OR limitation documented."
We therefore formally close G1 by its **documented-limitation**
path, not by asserting existence of a new independent holdout.

Evidence:
- G1.2k sealed exact historical 40,320×390 input/reconstructed
  numerical predictor parity, dossier SHA256
  `7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
- G1.2m outcome-blind originally declared date-only
  265,145→40,320 structural row-key/order/timestamp parity,
  supplement SHA256
  `388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.
- G1.3a/b local filename-only inventories: no newly
  **verified eligible** unused later HDPG event-time
  cohort in the audited research roots. The 49 undated
  broad-scan paths are unrelated PaymentGame material,
  Phase IV test fixtures or undated legacy SBERT artifacts.
- Original same-basename raw-file/copy provenance remains
  DOCUMENTARY_OPEN; not a numerical mismatch.
- The 60-calendar-day new forward study could not produce
  mature outcomes by the 2026-11-25 editorial deadline
  from an October-27 prospective start.

Transition artifact:
`G1_TO_G2_STAGE_HANDOFF.md`.
G2 active draft:
`G2_REVISION_PROTOCOL_DRAFT.md`.

**G2 gate is the entire revision protocol for the paper, NOT
equivalent to G1.3 new-holdout preregistration.**
It must cover the editor/reviewer exact objections, fixed
metrics/comparators/filters/thresholds, dispositions for
already-frozen versus secondary/exploratory versus
non-executable analysis, negative results and maximum
claim strength. Current map is preliminary, not copied
from reviewer letters. G2 is NOT yet frozen or complete,
so G3 new computations and all newer target/outcome
access remain NOT AUTHORIZED.

Agentic path remains:
G0 (historic audit) → G1 (feasibility result) →
G2 (freeze revision protocol) → G3 (execute authorized work;
non-executable experiments explicitly recorded) →
G4 (adversarial audit) → G5 (revise manuscript) →
G6 (reviewer rebuttal) → G7 (resubmission pack).
Original experiment tags/contracts remain intact.

## 2026-10-27 G2.1 executed document/control design; G2 reviewer source blocked

Under the existing G0→G7 Agentic Graph Engineering graph,
G2 **ACTIVE, NOT FROZEN**; G3 remains blocked.

G2 artifacts now created:
- `G2_REVIEWER_TRACEABILITY_PROVISIONAL.json` (10 internal
  Q-01..Q-10 technical areas; **explicitly NOT original or
  attributed peer-review quotations**). Every Q-topic
  records the existing audit basis, potential G3 disposition,
  proposed G5 manuscript section and claim limitation.
- `ic_g2_freeze_preflight.py` validates prior G1.2k/m
  SHA256 fingerprints, frozen V1 negative feasibility,
  V2/V3/V4 target/CI caveats, original P10 threshold
  and calibration constant, **verified full editorial
  review-letter coverage**, actual reviewer item mappings,
  and pinned permissible G3 specs. Returns
  `G2_FREEZE_GATE_BLOCKED` with nonzero exit unless all
  editor/reviewer inputs and risk controls exist.
  It does not itself authorize G3.
- `test_ic_g2_freeze_preflight.py` (nine metadata-only
  fail-closed test cases; committed, **not reported as
  operator-executed yet**).
- `G2_1_TRACEABILITY_AND_FREEZE_PREFLIGHT.md`
  documents reviewer source discovery and local preflight.

Editorial source discovery performed through available
connectors and project-file search:
- Gmail connector lookup failed `FORBIDDEN`; messages NOT read.
- Drive searched for case ID / Intelligent Computing /
  reviewer / major revision; no authenticated editorial
  review letter found in search results. Older unrelated
  work drafts do not establish reviewer objections.
- Project file search yielded no matching source document.
- No exact original reviewer comment count/content is
  independently available in current task.

**G2 blocker:** `G2_REQUIRED_AUTHENTIC_REVIEWER_SOURCE_UNAVAILABLE`.
We will not fabricate reviewer remarks or silently
reinterpret our ten internal Q-topics as real reviewer
requests. The original scientific model data / targets
remain closed, the review branch remains isolated, and
G1.2k/m evidence files/hashes remain unchanged.

## 2026-10-27 G2.2: actual journal decision supplied directly by author, 22-item traceability

The author pasted in-chat the complete decision
letter dated **2026-10-26**, for
`ICOMPUTING-D-26-01069`, major revision
due **2026-11-25**.
The editor requests a point-by-point reply,
a separately highlighted revised paper, editable/high
resolution figure files, signed all-author license
and COI forms, image rights documentation,
conditional authorship-change signatures, and
resubmission by Editorial Manager.

The editor and reviewers' requirements are
captured as **22** paraphrased and locally
traceable requirements:
**E-01..E-07 (7)**, **R1-01..R1-07 (7)**
(non-numbered original paragraphs deliberately
decomposed as internal audit theme IDs),
**R2-01..R2-08 (8)** (original numbered
reviewer #2 comments). No private letter
body or contact details copied into GitHub.
Source classification: `USER_SUPPLIED_COMPLETE_EDITORIAL_EMAIL_BODY_IN_CHAT`;
provider-origin MIME cryptographic authentication
NOT claimed. Previous Gmail connector search
blocked, now no longer a barrier to content mapping.

Created:
- `G2_2_AUTHENTIC_REVIEWER_REQUIREMENT_MAP.md`
- updated `G2_REVIEWER_TRACEABILITY_PROVISIONAL.json`
- `G2_3_ANALYSIS_PACKAGES_DRAFT.md`
- `G2_4_VERIFIED_LITERATURE_SHORTLIST.md`
- updated `ic_g2_freeze_preflight.py` with
  22-ID fixed coverage (7+7+8), source provenance,
  original scientific numerical controls and
  mandatory G3-specification freeze gates
- adjusted `test_ic_g2_freeze_preflight.py`
  (11 unit-test cases, written but NOT
  independently executed on operator Mac).

Main scientific reviewer risks:
- genuinely independent, nonoverlapping 60d
  test not available from G1.3a/b local input scans;
- P10 25th percentile cutoff sensitivity P15/P25/P35;
- conventional volatility/downside comparator;
- negative absolute excess-beta and actual trading
  returns, flat option and costs;
- 10% Top-K rationale, V4 attenuation/week
  instability, ticker dependence overlapping return
  targets, and human-specified (not human causal)
  claim ceiling; model independence needs second ranker.
These are explicitly combined into eight
nonduplicating G3 analysis/limitation packages.

**G2 = ACTIVE, RESEARCH DESIGN DRAFT.**
New G3 calculations **NOT YET AUTHORIZED**
because complete source-anchored plans / hashes
and scientific signoff are outstanding.
Historical G1.2k/m SHA commitments unchanged.

## 2026-10-27 G2.3–G2.5 analysis planning and guarded input readiness

Reviewer requirement mapping now counts **22/22** numbered
audit items, uniquely:
- seven editor submission requirements E-01..E-07;
- seven internal R1 themes decomposed from original
  unnumbered reviewer #1 paragraphs;
- eight original R2 reviewer numbered points.
All 22 have nonempty source locators,
faithful requirement paraphrases, G2 work IDs,
proposed G5 manuscript destinations, G6
response anchors; no false original provider
MIME/hash authentication claimed. In the branch,
`G2_REVIEWER_TRACEABILITY_PROVISIONAL.json` remains
a documented user-pasted transcript, not original email bytes.

A1..A7 + X1 deduplicated work-package design:
`G2_3_ANALYSIS_PACKAGES_DRAFT.md`.
The P10 P15/P25/P35 experiment refers only to
validation-distribution *weighted cutoff percentiles*
of the **same calibrated P10 forecaster**, not
retraining P15/25/35 predictive quantiles.
Old V2/V3/V4 outcomes already consumed:
future sensitivity/volatility/K/cost reanalyses
are inherently POST-OUTCOME exploratory,
never new confirmatory proof. New nonoverlapping
60-day event X1 still unexecutable under G1
new-source availability block.

Verified shortlist:
`G2_4_VERIFIED_LITERATURE_SHORTLIST.md`
(Gu/Kelly/Xiu 2020 finance, Rudin 2019
interpretable high-stakes ML, Geifman/El-Yaniv
2017 selective classification, Gonzalez et al.
2026 human-AI complementarity framework).
Do not claim these references were inserted into
the revised manuscript yet.

Created metadata-only/hash-only original old-input
discovery `ic_g2_historic_analysis_inputs.py`
with operator runbook
`G2_5_HISTORICAL_INPUT_HASH_PREFLIGHT.md`.
It does NOT deserialize sources or open
financial outcomes/model data; no scientific
G3 computations were launched. **Not yet run by
local operator**. Requires further source as-of
feasibility inspection and SHA-pinned full
preanalysis protocol or nonexecutability
decisions before G2 can freeze.

Revised `ic_g2_freeze_preflight.py`
now recognizes **explicit user-provided full
letter transcript** as adequate for reviewer
requirements mapping without asserting false
provider authentication; enforces E7+R1-7+R2-8
coverage and all historical veto/CI protections.
`test_ic_g2_freeze_preflight.py` now has
**11 metadata-only self-test functions**.
Code and files were read back via connected
GitHub; no operator/CI test run was executed.
A `G2_FREEZE_GATE_BLOCKED` remains expected
until full exploratory analysis source/protocol
hashes and human scientific signoff are done.

Current graph:
`G0 CLOSED; G1 CLOSED_WITH_DOCUMENTED_LIMITATION;
G2 ACTIVE_REVIEWER_MAPPED_NOT_FROZEN; G3 BLOCKED;
G4–G7 PENDING`. Historical G1.2k/m evidence
fingerprints are unchanged.

## 2026-10-27 G2.5 operator-run historical source SHA inventory PASS (metadata only)

Local operator ran `ic_g2_historic_analysis_inputs.py` on:
1. `dtrm-fund/research/local_data`;
2. `PCDoMoney_Backend/Notebooks/Outputs`;
3. `PCDoMoney_Backend/Outputs`.

Exact terminal status:
`G2_HISTORICAL_ANALYSIS_INPUTS_METADATA_ONLY_NOT_AUTHORIZED_FOR_G3`.
- **92** candidate existing original old-research files registered,
  **92**/92 file SHA256 streamed without deserialization,
  **0** skipped files larger than the 200 MiB hash limit.
- Filename search category matches: features **10**,
  historical cohorts **44**, price/beta history **50**,
  validation/quantile **5**. **Categories overlap**;
  these are not separate file counts.
- Visible historically named V2/V3/V4 tiny evaluation PKLs,
  V2 frozen P10 veto threshold `probabilistic_v2_frozen_p10_threshold.pkl`
  (248 bytes), V2/V3 holdout features/signals/targets,
  V1 features/source material and V4 signals.
  All are **already consumed**, not new event cohorts.
- The five validation/quantile filename matches DO NOT
  establish that the **19,880 individual historic validation
  calibrated-P10 predictions and legacy news weights** have
  been separately retained or independently precommitted.
- The 'price_beta_history' count is a filename-classification
  output, **NOT** proof of point-in-time daily stock prices
  for a volatility-based benchmark or realizable turnover/P&L.
- No original numerical values, returns, forward labels,
  trusted Pickles, model boosters or new cohorts were opened
  or inferred by this G2.5 script.
- The G2.5 operator report path is local only:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_historical_analysis_sources.json`.
  Report SHA256 has **not** been supplied by operator;
  do not claim an anchored report digest.

Additional frozen-source review:
- `research/contracts/DTRM_XGB_PROBABILISTIC_V2.yaml`
  at pin `c7502a` records original validation
  **19,880 rows** and weighted empirical q=0.25 cutoff
  `-0.16665692627429962` from calibrated P10.
- Original pinned `run_probabilistic_xgb_v0.py`
  has `weighted_quantile` implemented as
  `np.argsort(values)` + `np.cumsum(weights)` +
  `np.searchsorted(cumulative, q*total, side='left')`.
- The earlier G1 `ic_g1_reconstruct.py` recreates
  frozen train/valid/test rows, P10 valid scores
  at best_iteration **18**, calibration offset
  `-0.06494169682264328`, weights from
  `legacy_news_weights`, and checks q=0.25 against
  the **historical frozen threshold**.
  That previously reported 12/12 numerical historical
  reconstruction PASS; **alternate q=0.15/0.35
  sensitivities have NOT been calculated**.
- Therefore A2 validation threshold replication has
  an identified deterministic original source route,
  but G3 secondary cohort comparison and G2
  source-hash/implementation freeze remain open.
- A3 as-of price/volatility comparison; A4 tradable
  P&L/cost/flat, A6 Top-K sensitivity remain
  conditional on separate fixed, auditable protocols.

**G2.5 gate PASS metadata-only; G2 ACTIVE, NOT FROZEN;
G3 ALL ADDITIONAL FINANCIAL REANALYSES BLOCKED.**

## 2026-10-27 G2.6 operator PASS: original V0 validation-P10 source bound

The operator executed `ic_g2_validation_source_binding.py`.
Exact state:
`G2_6_A2_VALIDATION_P10_SOURCE_PATH_BOUND_THRESHOLDS_NOT_COMPUTED`.

- Frozen code commit `c7502a690162459cdfb3413573e3133c42efb126`.
- Original q25 weighted validation threshold numerical anchor
  **-0.16665692627429962**.
- **9/9** source routine checks passed: original
  weighted empirical quantile method, sorted cumulative
  `legacy_news_weights`, left-side searchsorted,
  valid-only P10 calibration and P10 predictions.
- **8** old V2/V3/V4/V1 artifact SHA refs tied through
  the original G2.5 metadata-only file inventory.
- Operator original G2.5 report SHA256:
  `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.
- Local G2.6 report:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_6_validation_source_binding.json`.
  Its own report SHA256 has NOT yet been separately shared.
- No q15/q35 values, old cohort return/target comparisons,
  Pickle/price scientific values, new event cohorts or
  model inferences were opened/run.

**G2.6 source readiness PASS for A2. G2 remains UNFROZEN,
G3 new analysis still BLOCKED.**

G2.7 prepared as a structured source-and-method
preanalysis *draft* (not a G3 launch):
`G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json`
and `ic_g2_a2_protocol_preflight.py`,
`G2_7_A2_PREREG_SOURCE_PREFLIGHT.md`.
It fixes validation-weighted P10 q=0.15/0.25/0.35,
the same original ranker and old V2/V3/V4 cohorts,
K values, full-K infeasibility, original news/ticker
bootstrap seeds and disclosure of **all 9 exploratory**
old-outcome comparison cells. Operator G2.7 is
NOT YET RUN. It never authorizes G3 by itself.

## 2026-10-27 G2.7 A2 preanalysis metadata gate: OPERATOR PASS, NO G3 WORK

Operator executed `ic_g2_a2_protocol_preflight.py` with
previously committed `G2_7_A2_THRESHOLD_SENSITIVITY_PREREG_DRAFT.json`,
local G2.5 SHA source inventory and G2.6 historical V0
validation-P10 source binding.

Exact CLI status:
`G2_7_A2_PLAN_SOURCE_AND_METHOD_METADATA_PASS_NOT_G2_FROZEN`.

- 8 earlier historical V1/V2/V3/V4 input SHA references checked.
- q-grid **[0.15, 0.25, 0.35]** fixed using original
  19,880-row validation calibrated **P10** scores, not
  alternate predictive quantile models.
- Original q25 **-0.16665692627429962** retained.
- **3 historical consumed cohorts × 3 cutoffs = 9
  explicitly exploratory cells**; old full-K requirements,
  source/cluster/ticker stop conditions and seeds fixed.
- Original G2.5 metadata report SHA256:
  `ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`.
- G2.6 operator source-binding report SHA256:
  `1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`.
- A2 preanalysis plan (local retrieved file) SHA256:
  `5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8`.
- G2.7 local report file:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_7_A2_spec_source_preflight.json`
  (its own SHA256 **not yet reported** by operator).
- No alternative q15/q35 cutoff values calculated, no
  scientific Pickles/labels/prices opened, no old-cohort
  inference, no results, no new event cohort.

**G2.7 scope source and plan metadata PASS**.
This is neither a signed frozen full-G2 protocol nor
permission to calculate A2 old-outcome sensitivity.
G3 remains BLOCKED while A3 volatility comparator,
A4 economic/flat/cost claims, A6 K-grid dispositions
and global G2 adversarial signoff remain open.

## 2026-10-27 G2.8 A3 metadata-only price source triage PREPARED

After G2.7 operator PASS, a new source-only A3 feasibility
preflight was prepared for **Reviewer #1's conventional
volatility/downside benchmark**.

The source is `ic_g2_a3_price_source_triage.py` and
the runbook is `G2_8_A3_PRICE_SOURCE_TRIAGE.md`.
They check G2.5 inventory SHA256
`ccf5ef4b7b9a63e6aada4cddb401fc7adb7d1ef7d564e4ea998718834ce2bec7`,
G2.6 source binding SHA256
`1ee9a491542ff5e5849cbaa13c8d022cc84639515a32fd51b0ff2e7805e291c2`,
and G2.7 A2 specification SHA256
`5992890e6cecb37182f006834b509de9b1c81efaeb86d52c6ada928819e756b8`,
plus the local G2.7 source-only PASS report.

G2.8 only triages filenames from the 92 prior SHA-recorded
historical source candidates, and reads original frozen
`src/dtrm/price_alignment.py` and
`src/dtrm/return_construction.py` source code.
It **never** reads historical market price observations,
future labels, Pickles, NPY, models or actual profits.
Target/evaluation/forward files are excluded from
being counted as credible pre-event-price candidates.

A3 design remains merely preliminary: a strict
event-time trailing-volatility filter, fixed cutpoint
on original validation only, matched frozen ranking
and full-K universe. As-of series, source adjustment,
prices, coverage and fair comparator cutoff remain
UNVERIFIED. The source-only G2.8 operator test has
NOT yet been run; no G3 experiment authorized.

## 2026-10-27 G2.8 OPERATOR-RUN, BOUNDED NEGATIVE WITH DETECTOR OMISSION; G2.9 CORRECTIVE AUDIT PREPARED

The operator executed `ic_g2_a3_price_source_triage.py`.
Exact status:
`G2_8_A3_NO_ASOF_PRICE_SERIES_IDENTIFIED_IN_G2_5_INVENTORY`.
Exact G2.5-catalog filename classifications:
- `BETA_OR_MARKET_CONTEXT_NOT_STOCK_PRICE_SOURCE`: **28**;
- `EXCLUDED_OUTCOME_OR_TEST_ARTIFACT`: **43**;
- `OTHER_FILE_NAME`: **21**;
- `POSSIBLE_PRICE_SOURCE`: **0**.

The 28 historical `SPY_...` files belonged to
`Notebooks/Outputs/price_cache_fmp_pickle` and
were hash-recorded by earlier G2.5 only because the
**basename matched `spy`**. Inspection of G2.5's
*source code* confirms it selected files using a
regex on `filename`, NOT on the full relative
path. Therefore original stock daily price-cache
files with generic ticker/date basenames were
excluded from the candidate inventory, even
though the directory itself has 'price_cache'.
This is a **candidate-discovery false-negative**,
not demonstrated absence of original stock prices.

Frozen source `research/experiments/run_exante_baseline_v0.py`
at original code pin `c7502a` explicitly loads
`Notebooks/Outputs/price_cache_fmp_pickle/*_2026-07-05.pkl`
using `frame["date"]`, `frame["close"]`.
Previous historical G1.2 preflight required and
operator previously PASSed metadata count **174**
files for the July-5 historic suffix. The 174 is
historic previously recorded metadata, **not**
a new G2.9 observation.

**Original G2.8 report preserved as a correct narrow
result about the 92 G2.5 files; must NOT be promoted to
the global claim 'A3 cannot be built'.**

Prepared a new, scope-correcting **G2.9**
`ic_g2_a3_price_cache_directory_inventory.py`
and `G2_9_A3_DIRECT_PRICE_CACHE_INVENTORY.md`.
G2.9 scans one original price-cache directory directly:
filenames/sizes and bounded streamed SHA256 of
the July-5/August-10 suffix file groups; excludes
scientific Pickle deserialization or any price/
return value examination. No original frozen source
contracts/old results are modified.

Pending actual G2.9 operator result, A3 historical
pre-event risk coverage, provider as-of timestamps,
unadjusted/adjusted price comparability, and
volatility comparator feasibility remain **OPEN**.
A date appearing in a snapshot filename alone does
NOT establish price availability before event or
corporate-action point-in-time adjustment.

**Scientific gate: G2 ACTIVE, NOT FROZEN; G3 BLOCKED.**

## 2026-10-27 G2.9 ORIGINAL FMP STOCK PRICE-CACHE DIRECTORY — OPERATOR PASS, HISTORICAL AS-OF STILL OPEN

The operator executed `ic_g2_a3_price_cache_directory_inventory.py`
on the original fixed folder
`PCDoMoney_Backend/Notebooks/Outputs/price_cache_fmp_pickle`.
Exact state:
`G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN`.

- **3,649** distinct named original price-cache PKL files inventoried
  (filename/size and bounded streamed SHA256 only).
- Exactly **174** files with the original
  `*_2026-07-05.pkl` suffix, representing **173
  distinct non-SPY tickers + SPY** (metadata only).
- Another **174** files with suffix `2026-08-10`;
  many other suffix/date groups, all retained in the
  operator report.
- **Zero** files skipped by 25-MiB hash cap among
  the watched original July-5/August-10 groups.
- Original historic pinned price-reader source
  at `c7502a690162459cdfb3413573e3133c42efb126`
  verified. Original V0 code expects `date` and
  `close` in historical price frames.
- Report path:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_9_A3_original_price_cache_inventory.json`;
  its own SHA256 **not yet provided** by operator.
- No Pickles deserialized, financial prices/targets,
  returns, outcome data, or model predictions opened.
  **No A3 experiment executed.**

**Interpretation:** G2.8's zero-price result was a
bounded file-discovery false negative caused by G2.5's
basename keyword filter (stock ticker/date names
omitted). This corrected scan identifies original
multiticker daily price-cache **candidate files**.
It does NOT prove dates/columns within each
dataframe, risk observation coverage, provider
historical as-of/acquisition timestamps, point-in-time
adjustment/corporate actions, or adequacy for a
fair volatility comparator. Snapshot suffix `2026-07-05`
is later than the May/June HDPG event decisions:
bar DATE < event date is necessary for no forward
market quotes, but insufficient to prove original
point-in-time availability of the version/adjustments.

**Gate G2.9 = METADATA_SOURCE_DISCOVERY_PASS; A3
HISTORICAL PRE-EVENT PRICE COVERAGE UNVERIFIED.
G2 ACTIVE/UNFROZEN; G3 BLOCKED.**

Next G2.10: separately authorized and operator-opt-in
trusted-original-pickle **SCHEMA AND DATE-ONLY**
inspection of original July-5 price frames. Do not
compute volatility or read/print any price values,
outcome labels, forward target or returns. Demand
frame `date`/`close` column names, unique
trading dates and adequate **strictly earlier**
daily bar dates before V2/V3/V4 first event dates.
Keep provider as-of lineage documentary-OPEN even
if column/date coverage passes.

## 2026-10-27 G2.10 ORIGINAL STOCK PRICE SCHEMA/DATE-ONLY CHECK PREPARED

Prepared `ic_g2_a3_original_price_schema_dates.py`
and `G2_10_A3_PRICE_DATE_SCHEMA_GATE.md`
to follow successful G2.9. This is the first G2
A3 source feasibility check to *explicitly* require
trusted Pickle deserialization; unlike G2.5–G2.9
it necessarily loads historical price frames into
memory to inspect only `date` and column names.
The implementation refuses to proceed unless the
operator supplies `--trust-original-price-pickles`,
which acknowledges Pickle's code-execution risk.
It verifies G2.9 recorded SHA for each of 174
original July-5 files before loading, never accesses
the `close` values, and computes only date coverage,
schema, uniqueness, row counts and min/max dates.
No volatility, market return, outcome labels,
execution-profit or ranking inference is computed.

Pre-event DATE-coverage windows fixed before
local operator run: earliest original V4 event
`2026-05-02`, V2 event `2026-06-07`, V3
event `2026-06-11`; 61 prior distinct trading
closes needed for 60 daily returns and 41 for
minimum 40. Date-only coverage is NOT full
ticker/news-event coverage or original V0
validation-population coverage. Snapshot named
`2026-07-05` remains after original May/June
decision dates; quote-vintage/acquisition and
split/dividend adjustment point-in-time integrity
cannot be certified from bars' dates alone.

**G2.9 was OPERATOR PASS; G2.10 source check is
PREPARED but has NOT been operator-run. G2 and
A3 full source-as-of gate UNFROZEN; G3 BLOCKED.**

## 2026-10-27 G2.10 first operator attempt — implementation NameError, no accepted scientific result

The operator ran original G2.10
`ic_g2_a3_original_price_schema_dates.py`
against the trusted original 174 July-5 price-cache
snapshots and metadata-only G2.5–G2.9 reports,
with explicit opt-in to trusted original-Pickle
loading. The CLI returned exactly:

`G2.10 HALTED: NameError: name 'G2_5' is not defined`.

This is a **new Python metadata-report assembly bug**
in G2.10, not evidence of missing historical prices,
inadequate trailing-date coverage or a changed
scientific assumption. The original code had
three undefined names in the final output JSON:
`G2_5`/`G2_6`/`G2_A2` instead of the previously
defined SHA pinned constants `G2_5_SHA`/
`G2_6_SHA`/`G2_A2_SHA`.
The fix replaces only those three final
metadata dictionary references, without changing
original source/price data or the temporal policy.
Commit `36cac4171284b5bf3eff5281d23be65af4ff5233`.

Since Python builds `result={...}` **after**
the 174-frame loop, the first run likely loaded
the 174 trusted original price frames (and date
column metadata) into memory before it failed.
It did **not** complete the report write or emit
PASS/PARTIAL; there is no accepted G2.10 result.
The code explicitly never reads the close series
for financial operations and never computes market
returns, volatility, P10 inference, portfolio P&L
or G3 analyses. Trusted Pickle deserialization has
intrinsic code-execution risk; no other untrusted
Pickle sources should be introduced.

Added metadata/code-only static regression
`test_ic_g2_10_schema_dates_regression.py`
with five assertions (syntax, output SHA symbols,
defined globals, no close-column observations,
trusted-Pickle and G3 safety controls). It is
COMMITTED BUT NOT OPERATOR-EXECUTED as of this log.
Operator correction/retry procedure and scientific
gate caveats recorded in
`G2_10_A3_PRICE_DATE_SCHEMA_GATE.md`.

**G2.10: OPERATOR RUN HALTED; RETEST PENDING.
G2 A3 AS-OF, RISK COMPARATOR AND FULL PROTOCOL
REMAIN UNVERIFIED. G3 STILL BLOCKED.**

## 2026-10-27 G2.10 CORRECTED OPERATOR PASS: 174/174 original quote DATE coverage, vintage unverified

After the metadata-report `NameError` defect was fixed
in the research branch, the operator reran the corrected
`ic_g2_a3_original_price_schema_dates.py` and **all five**
`test_ic_g2_10_schema_dates_regression.py` static-only
regression tests on Mac:
`Ran 5 tests in 0.007s: OK`.

**Exact operator CLI status:**
`G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`.

- **174/174** original `2026-07-05` cache Pickles,
  original reader schema `date` and `close`
  column *names* verified; 173 non-SPY symbols + SPY.
- Date structure `DATE_STRUCTURE_OK: 174`.
- At fixed earliest cohort event dates
  V4 `2026-05-02`, V2 `2026-06-07`,
  V3 `2026-06-11`, **174/174** files
  have calendar-date coverage for at least
  61 strictly earlier distinct closing dates (60
  trailing close-to-close returns), and hence at
  least 41 prior dates (40 returns).
- Source file metadata SHA was checked against G2.9
  prior to trusted original-Pickle deserialization.
  Original numerical `close` values were unpickled
  into memory but **not accessed or computed upon**;
  no prices, returns, risk, P&L, target outcomes,
  models or G3 comparator evaluations were
  examined or produced.
- Local report: `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_10_A3_price_schema_dates.json`.
  **Operator has not supplied SHA256 of this report**;
  do not claim a pinned generated report digest.
- Three shell diagnostic lines
  `zsh: command not found: #` came from pasted
  interactive comment lines; do not confuse these
  harmless shell messages with the Python test
  results or G2.10 PASS.

**Scientific interpretation:** 174/174 earlier
DATE coverage at **three earliest event dates only**.
This is NOT complete event-by-event/news-ticker
matching, original V0 validation-date coverage,
verified numeric valid `close` values, historical
point-in-time provider ingest vintage, adjusted
price status, or absence of corporate-action
revision. Original July-5 snapshot was saved
after May/June signal dates and may contain
retroactively adjusted data. A3 is source/date
STRUCTURALLY FEASIBLE, but still unapproved
as a true ex-ante point-in-time volatility
comparator. Only retrospective exploratory
reconstruction may be feasible with declared
data-vintage limitations.

**G2.10 PASS; G2 STILL UNFROZEN; G3 BLOCKED.**

## 2026-10-27 G2.11 A3/A4/A6 DRAFTS AND G2 FREEZE HANDOFF

Following operator G2.10 corrected PASS and five
static tests PASS, G2.11 documents the active
revision analysis plan without launching financial
experiments:
- `G2_11_A3_VOLATILITY_BENCHMARK_DRAFT.json`:
  60 trailing past-only daily simple returns,
  minimum 40 and volatility sample std ddof=1,
  validation-only admission-matched high-vol
  filter, common sample/ranking/Top-K, all V2/V3/V4
  reported, source vintage and adjustment qualifier.
- `G2_11_A4_A6_ECONOMIC_CAPACITY_DRAFT.json`:
  legitimate no-action comparison requires a
  **tradable absolute gross return** definition,
  not zero cash versus historical excess-beta.
  Event-level historical outcomes != self-financing
  repeated-ticker/overlapping event portfolio P&L.
  K sensitivity predeclared at 5/10/15% and
  remains post-outcome exploratory.
- `G2_11_A3_A4_A6_CONTROLLED_HANDOFF.md`:
  source proof gate, A1–A7/X1 dispositions,
  minimal operator SHA request for the original
  G2.9/G2.10 reports; no repeat source scans.

The G2.10 generated report's SHA256 is not
yet provided; source vendor as-of acquisition
and corporate-action vintage are unverified;
original V0 validation and all event/ticker
pre-event close quality coverage is not yet audited.
**G2 remains ACTIVE/NOT FROZEN; G3 still BLOCKED.**

## 2026-10-28 G2.11 — OPERATOR-SUPPLIED SHA256 of original G2.9/G2.10 reports

Operator ran `shasum -a 256` on the unchanged local
JSON output reports from source-only and trusted
date-schema-only steps. Exact SHA256, now recorded:

- G2.9 `IC_G2_9_A3_original_price_cache_inventory.json`:
  **`65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`**
- G2.10 `IC_G2_10_A3_price_schema_dates.json`:
  **`f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`**

Operator G2.9 result:
`G2_9_A3_HISTORICAL_PRICE_CACHE_SOURCE_FILENAMES_FOUND_ASOF_OPEN`;
3,649 named original FMP price-cache files,
174 original `2026-07-05` files (173 stocks plus SPY).

Operator corrected G2.10 result:
`G2_10_A3_ORIGINAL_STOCK_PRICE_BAR_DATE_COVERAGE_PASS_PROVIDER_VINTAGE_OPEN`;
5/5 regression tests PASS; 174/174 original July-5
frames have original `date` and `close` column
names and >=61 distinct earlier trading-bar dates
before the three original **first** V4/V2/V3 dates.

These are **operator-supplied fingerprints of local
reports**, not independently obtained file bytes
by GitHub. They bind next preanalysis checks
without uploading any private quoted prices.

**Scientific guardrails unchanged:** first-event
bar-date coverage does NOT establish every
(news_id,ticker) row, original V0 validation
date availability, actual close-value quality,
historical provider acquisition time or
corporate-action price adjustment vintage.
A3 volatility benchmark and G3 remain BLOCKED.

## 2026-10-28 G2.12 individual-event price-date source coverage PREPARED

User supplied SHA256 of two saved local original
price-source audit results and they were recorded
in the G2.11 SHA section above:

- `IC_G2_9_A3_original_price_cache_inventory.json`:
  `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`.
- `IC_G2_10_A3_price_schema_dates.json`:
  `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`.

Prepared original-source G2.12
`ic_g2_a3_per_event_bar_date_coverage.py`
with code-only regression
`test_ic_g2_12_per_event_date_regression.py`,
and operator guide
`G2_12_A3_PER_EVENT_DATE_COVERAGE.md`.

G2.12 SHA-checks original archived V1/V2/V3/V4
signal files and 174 original July-5 price
frames against prior G2.6/G2.9/G2.10 reports,
then inspects **only** old source `news_id`,
`ticker`, `date_dt` and price-bar `date`.
It verifies per-pair strictly earlier
historical bar-date counts for each cohort,
V1/V4 key/date set agreement, and
missing ticker/market-reference coverage.
User must authorize trusted original local
Pandas Pickle loading (the entire underlying
frame enters memory). Source is previous
holdout-consumed historical evidence.
Price numeric close values, returns, model
predictions, forward labels, targets, actual
risk/transaction costs or portfolio results
are NOT calculated in this G2 preflight.

**G2.12 NOT YET OPERATOR EXECUTED**; original
V0 validation cohort date/source coverage,
price adjustments/provider acquisition-time
and A3 comparator feasibility remain OPEN.
G2 NOT FROZEN, G3 BLOCKED.

## G2.12 OPERATOR PASS and G2.13 V0 VALID coverage prepared (2026-10-28)

Operator ran all seven local source-regression tests:
`Ran 7 tests in 0.005s: OK`, and original-source
`ic_g2_a3_per_event_bar_date_coverage.py`.
Exact source-only status:
`G2_12_A3_ALL_ORIGINAL_EVENT_PAIR_BAR_DATES_COVERED_VINTAGE_OPEN`.

Per original cohort pair DATE coverage with 61 strictly prior dated closes:
- V4 original V1 signals **40,320 / 40,320**, ticker miss **0**.
- V2 signals **4,449 / 4,449**, ticker miss **0**.
- V3 signals **2,827 / 2,827**, ticker miss **0**.
- V4 original signals **40,320 / 40,320** supplementary
  same cohort, not extra unique events.
- Distinct three-cohort original observations **47,596 / 47,596**.
- V1/V4 event ID/ticker/date key-set agreement **True**,
  and original source row order agreement **True**.
- Original file price cache **174** stock+SPY files.
- Provider ingestion vintage **False/unverified**.
- No numerical market close values, actual 60-day
  returns, volatility, historical target outcomes,
  predictive model inference or portfolio P&L calculated.
- Local report:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_12_A3_per_event_date_coverage.json`
  (SHA256 not yet received, next source preflight will
  hash and include it).

Original previously recorded G2.9/G2.10 local report hashes
remain `65cb3056fc2fafb8908c11a8329bae96b4e1c798f890defec508b2659043f7fb`
and `f4b873e10454d3b191b09ec7693111b3b5367bf3e92eb01643d8d785196ab6b3`
respectively.

**Scientific next missing input:** V0 original
`split="valid"` had 19,880 pairs, with a
frozen, weighted validation-only P10 veto. A
fair conventional volatility cutoff must use
that validation fold and strictly prior
daily closes, not historical V2/V3/V4 target
outcomes. G2.12 did NOT audit V0 valid dates.

G2.13 `ic_g2_a3_original_validation_date_coverage.py`,
`test_ic_g2_13_validation_dates_regression.py`,
and `G2_13_A3_ORIGINAL_V0_VALID_DATE_GATE.md`
have been committed. They check historical
original `legacy_model_rows_2026-05-01.pkl`
V0 valid 19,880 event/ticker/dates against
the SHA-bound original July-5 price-cache
dates, no numeric prices, volatility, target
values or rankings. Original local Pickles
must be trusted explicitly. **NOT YET OPERATOR-RUN**.

July-5 saved price vintage postdates
May/June decisions; historical provider
adjustments, numeric validity and price
acquisition timestamps remain **UNVERIFIED**.
G2 is ACTIVE and UNFROZEN; G3 BLOCKED.

## 2026-10-28 G2.13 — V0 validation 19,880/19,880 DATE source PASS

The original local operator ran seven
`test_ic_g2_13_validation_dates_regression.py`
static source tests, with **7/7 PASS**, and
`ic_g2_a3_original_validation_date_coverage.py`
against SHA-recorded trusted original historical
stock/SPY price caches and original
`legacy_model_rows_2026-05-01.pkl`.

Exact result:
`G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN`.

- Original frozen V0 `split="valid"`: **19,880/19,880**
  pairs have >=61 strictly earlier original
  daily bar DATES, sufficient *in principle*
  for up to 60 trailing close-to-close returns.
- **167** distinct validation tickers.
- Validation event dates **2025-12-24** to
  **2026-01-21**.
- Missing stock price symbol pairs: **0**.
- Original training-row file, new retrospective local
  SHA256 `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`.
  This is NOT an original historical/outcome-blind
  cryptographic commit.
- G2.12 operator report SHA256 independently
  supplied by G2.13 source-binding computation:
  `e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`.
- G2.13 output:
  `$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json`;
  its own SHA256 **not yet supplied or sealed**.
- No numeric close values, actual stock returns,
  financial outcomes, volatility, model scores,
  target labels, transaction costs or
  comparative performance were computed.

**Interpretation:** G2.12 test pairs (47,596/47,596)
and G2.13 original V0 validation pairs
(19,880/19,880) all have 60 pre-event
historical bar DATES (subject to the original
July-5 snapshot). This makes a *retrospective
date-restricted* conventional volatility
comparator structurally feasible.

**Scientific limits remain open:** original
2026-07-05 saved price-cache vintage postdates
both V0 validation and original V2/V3/V4
decision dates; original provider collection
timestamps, corporate-action revisions,
numerical `close` validity, real per-event
quote availability and actual tradable
portfolio returns were NOT authenticated
by G2.13. This must be described honestly
in any subsequent A3 secondary analysis
and response to Reviewer #1.

**G2.13 = SOURCE-DATE VALIDATION PASS.
G2 overall still UNFROZEN; G3 BLOCKED.**

## 2026-10-28 G2.14 ADVERSARIAL DESIGN PRE-FREEZE AND REVIEWER RESPONSE PREVIEW

The operator's **G2.13 7/7 code-only regression tests
and 19,880/19,880 original V0 validation row-date
source coverage PASS** have been recorded in the
preceding section, along with original local
model-row SHA `3b573c4e92dca404a5ab9d649dfa95ddfc58aa9b81ecd8563775cc56ac17b724`
and G2.12 source report SHA
`e67cf796975c60fdc674f15d985ce755ca1b862779253f4ef7f82a56d326785f`.

Created `G2_14_PRE_FREEZE_ADVERSARIAL_DISPOSITIONS.json`
and `G2_14_SCIENTIFIC_PRE_FREEZE_REVIEW.md`:
explicit scientific limitations (source acquisition
vintage, retroactively adjusted prices, incomplete
numeric quality, missing economic transaction
accounting, overlapping horizons and
ticker-cluster CIs covering zero), plus finite
go/no-go decisions per A1–A7 and X1.

Created `G6_REVIEWER_RESPONSE_WORKING_PREVIEW.md`:
English point-by-point reviewer response **working
draft**, not official G6 closure or submitted
manuscript. R1-01…R1-07 are internal audited
themes decomposed from unnumbered reviewer #1;
R2-01…R2-08 retain numbered reviewer #2 comments.
All future G3 calculations or new manuscript
changes carry explicit `[PENDING G3/G5]`
rather than fabricated experimental results.
Reviewer 1's requested independent,
nonoverlapping 60-calendar-day holdout is
honestly NOT EXECUTABLE under G1.3 data audits.

Updated G2.11 A3 conditional plan with
19,880 validation and 47,596 old test pair
historical bar-date structural availability,
and precise **numeric close quality,
adjustment/provider as-of vintage and final
common-sample rule still OPEN**.
A2 and A6 can be frozen as transparent
post-outcome exploratory analysis designs;
A3 remains conditional on numeric/vintage
limitation and fixed validator-cutoff/comparator
spec; A4 cannot claim realized self-financing
P&L or turnover; A5 lacks certified second
pre-outcome ranking model; A7 needs eventual
manuscript insertion.

**No G2 overall freeze commit, no manual scientific
signoff, no G3 financial tests, no official
G5/G6/G7 manuscript/editorial submissions yet.**

## 2026-10-28 G2.13 local report SHA256 operator commitment RECORDED

Operator computed `shasum -a 256` for saved
`$HOME/dtrm-ic-audit/g1-reconstruction/IC_G2_13_A3_V0_validation_bar_dates.json`
and provided exact digest
`e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`.

The preserved result remains:
`G2_13_A3_V0_VALID_19880_PAIR_BAR_DATES_FULL_COVERAGE_VINTAGE_OPEN`.
Seven local static regression tests PASS; original V0
validation 19,880/19,880 source pairs covering 167 tickers
(2025-12-24 to 2026-01-21) have >=61 prior bar dates;
G2.12 old V2/V3/V4 test pairs 47,596/47,596 similarly pass.

**Nature of evidence:** user-computed cryptographic
fingerprint of a saved local report. This assistant has
not independently downloaded local report bytes.
G2.13's local SHA confirms an exact report version but
does not certify provider price vintage or its
corporate-action adjustment availability as of
the old event dates. G3 remains blocked.

## 2026-10-28 G2.15 single freeze-decision register

Operator's new G2.13 original local report SHA256 is now
`e620944edc840500ff9cc1c7e8e823428a0127f66b90db27dd1b6d9e30cc49c7`
and is propagated to the G2.14 machine-readable
adversarial packet and conditional G2.11 A3 plan.

Created `G2_15_FREEZE_DECISION_REGISTER.md`
to consolidate reviewer-relevant conditions for
the final scientific G2 freeze **without
another data-source inventory**:
- A2 q15/q25/q35 and A6 K=5/10/15%
  are POST_OUTCOME_EXPLORATORY only, with 9
  old cohort cells apiece; original promoted
  q25/K10 policy remains untouched.
- A3 source **BAR-DATE** coverage is full
  for 19,880 original validation and
  47,596 original V2/V3/V4 test pairs;
  price numeric quality, original vendor
  vintage and corporate-action adjustment
  pre-event authenticity remain unverified.
- The older A3 JSON draft permitted >=40
  past daily returns, while a full-window
  primary risk benchmark demands 60; this
  must be settled and made internally
  consistent **before any quote-value or
  financial scoring analysis**.
- A4 actual capital turnover/cost/portfolio
  profit is NOT ESTIMABLE absent a
  self-financing dated transaction ledger.
- A5 independent second historic model and
  X1 new non-overlapping 60-day holdout
  are not verified from audited sources.
- Full G2 reviewer matrix currently has
  `all_g3_analyses_specified=false`,
  `revision_protocol_freeze_commit=null`.
  Its fail-closed preflight correctly
  remains blocking. A new real frozen code
  and signed scientific protocol is needed,
  not synthetic signoff.

**G2 SOURCE REPORT EVIDENCE SEALED AS USER-COMPUTED
HASHES; G2 OVERALL NOT FROZEN, G3 NOT AUTHORIZED.**
