# Phase IV collector and archive lineage audit v0

Date: 2026-09-07

Audit id: `phase4_collector_lineage_audit_v0`

Engineering status: `PASS_STATIC_EVIDENCE_BOUNDARY`

Scientific status: `BLOCKED_SOURCE_AUDIT`

## Decisive result

The inspected collector does **not** establish the observation and revision history required for a true observed-vintage Phase-IV event sequence. It records a provider publication date—or an unmarked collection-time fallback—together with current text and ticker matches, but no collection/first-seen clock, content-version identity, predecessor, mapping version, or link-availability time.

A separate and narrower mechanism does cryptographically bind the news rows used by recent governed ranking executions and can recover an unchanged append-only prefix. That is valuable ranking-time evidence. It is not a retrospective source-vintage archive: the published candidate batches cover two and five days, their workflow retention is configured for 30 days, and static code cannot establish which historical artifacts still exist.

Consequently:

- true observed-vintage history is not authenticated;
- coarse day-level history is not yet authorized;
- history construction, model fitting, outcomes, and MM1 execution remain prohibited;
- no claim about the Phase-IV treatment can yet be tested.

## Registered boundary and method

This audit implements the contract registered at commit `6d7b41424dc65d6234a98a916e494f42bc0ee62d`, before repository-content inspection. Contract SHA-256: `2242d3d83af01d2854315856757e4c7be02278e125fe605a17ba543c4d0727d5`.

Its parent is the user-supplied bounded Mongo metadata report `research/reports/DTRM_PHASE4_SOURCE_METADATA_LIVE_20260907T183459Z.json`, SHA-256 `30aa53d5bfad2a32b1b4ed0c9aa8eb2024fd60bf54dc5314b6b6af5b847b880b`.

Only recursive Git trees, default-branch code search, and cited text files at two pinned commits were inspected. Both recursive trees reported complete. No workflow run, artifact, endpoint, live database, outcome, target, score, return, or Phase-III evidence file was opened. No inspected external repository was modified.

| Repository | Commit | Tree | Entries | Interpreted role |
| --- | --- | --- | ---: | --- |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `badb20158890e9982c7806382cc3e151782af372` | `b5107d0ee17f2909e0b0c060a7d00d00bb91a567` | 4,384 | Workflow dispatch and artifact retrieval |
| `tech-com-UA00001/theresistance-back` | `7a8107e4451891535366acaf766348785ccc157b` | `f295888372d9ef3c089cc24dd1e72e6b1f2c92cf` | 235 | News collection and ranking evidence |

The first tree includes tracked dependency content; source-wide negative conclusions are restricted to its seven non-vendor files and the registered search terms. The historical `DTRM_Fund_Agent` redirect remains routing evidence only, as stated in the contract.

## Collector facts

`F01_COLLECTOR_WRITE_SHAPE` — `SUPPORTED_STATICALLY`

- The collector selects three Financial Modeling Prep news feeds, filters for Trump mentions, maps text to tickers, and writes to `trumpMinMax.trumpNews`.
- The visible stored fields are `date`, `text`, `source`, `matched_tickers`, `raw`, and normally `dedupe_key`.
- It attempts a unique sparse `dedupe_key` index and a `date` index, but index creation is best-effort and all creation errors are suppressed. The code therefore does not statically guarantee that the unique index exists at runtime.
- The ordinary write path is `insert_one`; no collector update, replace, delete, bulk-write, or upsert path was found at the pinned tree.

Evidence: [`news_collector.py` lines 54–63](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L54-L63), [`news_collector.py` lines 2017–2083](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L2017-L2083).

`F02_OBSERVATION_CLOCK` — `CONTRADICTED_STATICALLY`

- `date` prefers the upstream `publishedDate` or `date` value.
- If parsing fails or neither value is present, it silently substitutes the collector's current UTC time.
- The document does not mark which branch produced `date`, and it stores no `collected_at`, `first_seen_at`, `version_observed_at`, or equivalent field.

Thus the same field conflates two different clocks. Neither its value nor Mongo `_id` authenticates when a particular content version first became available to the decision system. Evidence: [`news_collector.py` lines 2055–2067](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L2055-L2067).

`F03_VERSION_LINEAGE` — `CONTRADICTED_STATICALLY`

- The deduplication key prefers a normalized URL; otherwise it hashes normalized day, source, and text.
- A record contains neither a content SHA-256 nor version/predecessor identity.
- Any exception from the first insert is treated as a likely duplicate. If no row with identical text is found, the fallback attempts a second insert after removing `dedupe_key`; a nested failure is silently suppressed.

This is insert-only intent, not an immutable revision chain. A changed article at the same URL can enter an ambiguous unkeyed fallback path, and any retained variants are not linked. Evidence: [`news_collector.py` lines 1993–2011](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L1993-L2011), [`news_collector.py` lines 2067–2083](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L2067-L2083).

`F04_LINK_PROVENANCE` — `CONTRADICTED_STATICALLY`

The collector computes ticker matches from its in-code mapping and stores only the resulting `matched_tickers`. It records neither a mapping version nor the time at which a link became available. A later reader cannot distinguish an original link from a mapping produced by another collector version. Evidence: [`news_collector.py` lines 2051–2066](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L2051-L2066).

## Incremental behavior and schedules

`F05_INCREMENTAL_COVERAGE` — `CONTRADICTED_STATICALLY`

Once any row exists, the next collection interval starts on the calendar day after the maximum stored `date`; no overlap or revision lookback is applied. The pinned workflows expose a weekday morning collection path and a 22:30 UTC daily-ranking collection path. If an earlier run has already written the current day, a later same-day invocation can receive an empty plan. This is a code-level possibility, not a claim that every scheduled run executed.

The implementation therefore cannot guarantee capture of late-arriving articles, same-day articles published after an earlier collection, backfills, or revisions attached to an already represented day. Evidence: [`news_collector.py` lines 2118–2172](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/news_collector.py#L2118-L2172), [`morning.yml` lines 3–40](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/.github/workflows/morning.yml#L3-L40), [`daily_model_inference.yml` lines 10–102](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/.github/workflows/daily_model_inference.yml#L10-L102).

`F06_SCHEDULED_ENTRYPOINTS` — `SUPPORTED_STATICALLY`

The morning workflow runs the full pipeline, the daily-ranking workflow invokes collector-only mode, and the manually dispatched score workflow also calls the full pipeline. In `run_pipeline.py`, collection is controlled by `--skip-collector`; the score `--no-mongo-update` flag does not suppress the collector. Evidence: [`run_pipeline.py` lines 148–216](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/run_pipeline.py#L148-L216), [`trump_score.yml` lines 55–74](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/.github/workflows/trump_score.yml#L55-L74).

## Ranking-time evidence is real but narrower

`F07_RANKING_TIME_FREEZE` — `SUPPORTED_STATICALLY`

The governed ranking wrapper reads `_id`-ordered rows and binds normalized day, text SHA-256, and tickers into `sameNewsSha256`. After scoring, it freezes two-day and five-day candidate batches and a digest-bearing manifest from the captured in-memory rows. The recovery helper accepts later appends only when the original evidence is still an exact canonical prefix; edits, deletions, and interior insertions fail closed.

This establishes integrity of a particular ranking-time subset when the corresponding files exist. It does not create the missing collector observation clock, and candidate `published_at` is still derived from the collector's ambiguous `date`. Evidence: [`run_score_with_frozen_news.py` lines 45–144](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/run_score_with_frozen_news.py#L45-L144), [`freeze_loaded_news_evidence.py` lines 107–209](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/freeze_loaded_news_evidence.py#L107-L209), [`canonical_evidence.py` lines 29–51](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/src/theresistance_backend/intelligence/canonical_evidence.py#L29-L51).

`F08_HISTORICAL_ARCHIVE` — `UNRESOLVED`

The daily workflow uploads its collection summary, ranking files, two-day and five-day news batches, and freeze manifest with `retention-days: 30`. No corresponding output files are tracked in the complete pinned repository tree. Static code cannot establish past artifact execution, survival, external copies, or coverage over a Phase-IV research horizon. Evidence: [`daily_model_inference.yml` lines 471–492](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/.github/workflows/daily_model_inference.yml#L471-L492), [`freeze_daily_news_evidence.py` lines 105–230](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/freeze_daily_news_evidence.py#L105-L230), [`export_daily_news_candidates.py` lines 156–218](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/agent/trump_model/export_daily_news_candidates.py#L156-L218).

## API and test boundaries

`F09_API_BOUNDARY` — `SUPPORTED_STATICALLY`

The inspected API dispatches a configurable GitHub workflow, polls run state, downloads `trump_score_outputs`, parses pipeline/collector/trainer/score summaries, and exposes them over HTTP/MCP. Its complete non-vendor source set contains no independent news collector, Mongo news write, observation clock, version archive, or ticker-link provenance transformation. It therefore adds no provenance layer to the news records it orchestrates. Evidence: [`github.js` lines 44–73](https://github.com/tech-com-UA00001/DTRM_Fund_Agent_API/blob/badb20158890e9982c7806382cc3e151782af372/src/github.js#L44-L73), [`routes.trumpScore.js` lines 18–125](https://github.com/tech-com-UA00001/DTRM_Fund_Agent_API/blob/badb20158890e9982c7806382cc3e151782af372/src/routes.trumpScore.js#L18-L125), [`mcpServer.js` lines 203–233](https://github.com/tech-com-UA00001/DTRM_Fund_Agent_API/blob/badb20158890e9982c7806382cc3e151782af372/src/mcp/mcpServer.js#L203-L233), [`server.js` lines 1–20](https://github.com/tech-com-UA00001/DTRM_Fund_Agent_API/blob/badb20158890e9982c7806382cc3e151782af372/src/server.js#L1-L20).

`F10_RUNTIME_DEPLOYMENT` — `UNRESOLVED`

Static snapshots do not prove which source revision was deployed on any historical day, whether a workflow completed, which database state it saw, or whether an artifact survived. Commit time, workflow schedule, output publication time, provider date, and Mongo `_id` are not substituted for those unknowns.

`F11_FREEZE_TESTS` — `SUPPORTED_STATICALLY`

The pinned backend tests exact snapshot recovery, appended-row recovery, and fail-closed mutation within a sealed prefix. Evidence: [`test_canonical_evidence.py` lines 7–37](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/tests/foundation/test_canonical_evidence.py#L7-L37), [`daily_intelligence_append_only_recovery_v1.md` lines 1–12](https://github.com/tech-com-UA00001/theresistance-back/blob/7a8107e4451891535366acaf766348785ccc157b/docs/architecture/daily_intelligence_append_only_recovery_v1.md#L1-L12).

`F12_COLLECTOR_PROVENANCE_TESTS` — `UNRESOLVED`

Complete pinned-tree searches found no collector tests enforcing timestamp origin, index-creation success, dedupe fallback behavior, immutable revisions, mapping/link provenance, or overlapping late-arrival collection. The ranking-evidence tests begin downstream and cannot supply those missing guarantees.

## Decision matrix

| Required property | Finding | Decision | Consequence for Phase IV |
| --- | --- | --- | --- |
| Known upstream and write shape | `F01_COLLECTOR_WRITE_SHAPE` | `SUPPORTED_STATICALLY` | Enables a bounded follow-up audit, not history construction |
| Observation/first-seen clock | `F02_OBSERVATION_CLOCK` | `CONTRADICTED_STATICALLY` | True point-in-time event availability is unauthenticated |
| Immutable revision lineage | `F03_VERSION_LINEAGE` | `CONTRADICTED_STATICALLY` | Historical content vintages cannot be reconstructed faithfully |
| Mapping/link availability | `F04_LINK_PROVENANCE` | `CONTRADICTED_STATICALLY` | Ticker links cannot be placed on an authenticated knowledge clock |
| Late-arrival/revision coverage | `F05_INCREMENTAL_COVERAGE` | `CONTRADICTED_STATICALLY` | Completeness by event day is not guaranteed |
| Operational ranking snapshot | `F07_RANKING_TIME_FREEZE` | `SUPPORTED_STATICALLY` | Bounded execution evidence may be usable if artifacts exist |
| Long-horizon archive | `F08_HISTORICAL_ARCHIVE` | `UNRESOLVED` | No historical archive claim is allowed |
| Deployment/runtime identity | `F10_RUNTIME_DEPLOYMENT` | `UNRESOLVED` | Static source cannot authenticate past execution state |

The statuses describe only the pinned code. `SUPPORTED_STATICALLY` is not equivalent to runtime proof or scientific authentication.

## Selected immutable source identities

| Repository | Path | Git blob SHA |
| --- | --- | --- |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `src/github.js` | `7a07384ac9c7efa70cef9c1d9682f727c2e10ac0` |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `src/mcp/mcpServer.js` | `8cc006d5a8ef12ff68b2f18b104f3e977bc043ca` |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `src/routes.trumpScore.js` | `16e549cf43ebeb8c6f1fc1a8248eaf8b96bd4bfc` |
| `tech-com-UA00001/DTRM_Fund_Agent_API` | `src/server.js` | `a1cdcd663486be2bf7dfb3a90bab13927892bd4d` |
| `tech-com-UA00001/theresistance-back` | `.github/workflows/daily_model_inference.yml` | `2bed9fad2e42ed2e04ee5603aafbbd2d7a569924` |
| `tech-com-UA00001/theresistance-back` | `.github/workflows/morning.yml` | `4666c64c216f82a01e1000adce50e9101180bb7b` |
| `tech-com-UA00001/theresistance-back` | `.github/workflows/trump_score.yml` | `09b1267793ad20fd01474f60d3ae1b19b4150dfc` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/export_daily_news_candidates.py` | `331f261bfd4be636d3cd675ed287de6acd2dab8a` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/freeze_daily_news_evidence.py` | `18fd2ad6af63de54ba46b3d03444d12f1adb247f` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/freeze_loaded_news_evidence.py` | `f5d2ca87937672e9b096cc6f3fc29d5390bdc09d` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/news_collector.py` | `700e831db5c1d196a8e7c2c1dc6d10148237e710` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/run_pipeline.py` | `b39643a418a531060dd4e09a39424350f527d1fe` |
| `tech-com-UA00001/theresistance-back` | `agent/trump_model/run_score_with_frozen_news.py` | `792a8dbb4848ebe578c4658cd9c2f5c38f984586` |
| `tech-com-UA00001/theresistance-back` | `docs/architecture/daily_intelligence_append_only_recovery_v1.md` | `11c769408054e62e2f819d6b59af87158827a04d` |
| `tech-com-UA00001/theresistance-back` | `src/theresistance_backend/intelligence/canonical_evidence.py` | `459e708055818a6fccea42e380ea6ef67cb4ecad` |
| `tech-com-UA00001/theresistance-back` | `tests/foundation/test_canonical_evidence.py` | `896b9a578284764f22d4a665e1c4251041638c45` |

The machine-readable binding and decisions are in `DTRM_PHASE4_COLLECTOR_LINEAGE_EVIDENCE_V0.json`.

## Next permitted operation

After this increment passes repository gates and human review, the next contract may authorize a bounded, read-only audit of nested `raw` metadata, actual collection indexes, date parsing/precision, provider identifiers, and non-outcome coverage. That contract must separately decide whether a conservative day-level decision clock is scientifically defensible or whether Phase IV requires prospective versioned collection. It may not manufacture first-seen times from existing fields.

Until that addendum is registered and validated, the sequence remains at the source-audit node. Representation baselines, Transformers, outcome access, policy comparison, and retuning remain outside scope.
