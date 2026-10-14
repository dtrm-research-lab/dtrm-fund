# Phase IV — Executed pre-cohort link backfill: outcome-blind source provenance observation v0

**Observed 2026-10-14, from GitHub Actions run/commit metadata.** This is an observational source-authority report, NOT prospective preregistration or a historical state reconstruction. Base: frozen Phase IV research integration `3c9c7a2443213c991bba4cb621b97d9a56b3dd6c`. Phase III/MM1 code and public production are unchanged.

## Previously missing fact

The existing retrospective scientific source audit, executed 2026-09-10, classified 63,873 current Mongo documents and their `matched_tickers` under `RETROSPECTIVE_PROXY_PARTIAL/BLOCKED_SOURCE_AUDIT`. The original audited writer manifest's `insert_only` describes its **pinned collector code path**, not all possible mutations in the collection. We must not infer universal immutability from that narrow manifest.

**Independent GitHub Actions evidence:** on **2026-09-19**, a real backend push workflow executed an explicit `--apply` script, which supports modifying the `matched_tickers` field of existing news observations without changing their original identifiers or nominal provider dates.

## Exact source and execution lineage

**Repository:** `tech-com-UA00001/theresistance-back`.

| Item | Immutable identifier / observed result |
| --- | --- |
| Successful apply workflow | [GitHub Actions run 35439965103](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35439965103) |
| Workflow name | `Apply pre-cohort identity news backfill once` |
| Run created | 2026-09-19 11:23:08 UTC |
| Run head commit | `87f21b985ec03d2ba24819bce787b0cb7f2d58e4` |
| Workflow source path | `.github/workflows/apply_precohort_news_identity_backfill_once.yml` |
| Workflow Git blob at exact run head | `0940c4bc3e24619fdee0388a180d0034df8778b0` |
| Script path | `agent/trump_model/precohort_news_identity_backfill.py` |
| Script Git blob at exact run head | `073648fedd6ad6c20331beb7268d5a897c111256` |
| Workflow job status | `apply: success` |
| `Reconfirm exact dry-run boundary` step | success |
| `Apply reviewed identity-only repair` step | success |
| `Upload repair evidence` step | success |
| Evidence artifact name | `precohort-news-identity-backfill-applied-35439965103` |
| Artifact ID | `10583402771` (observed 2026-10-14; not expired) |
| Artifact metadata | 1,202 bytes ZIP, created 2026-09-19 11:23:36Z, expires 2026-12-18 11:23:09Z |

At exactly that run head, the workflow contains an `--apply` invocation for 2026-07-20 through 2026-09-18. It checks `mode=apply`, `inserted == 3`, `updated == 3`, `addedMatchCounts == {"AON":2,"MCO":4}`; otherwise the step fails. Therefore the step's success **attests that the script itself reported 3 inserted rows and 3 completed update calls**. The script increments its `updated` counter after a `collection.update_one({"_id": ...}, {"$set": {"matched_tickers": merged}})` call returns. It does **not** test `matched_count`, `modified_count` or independently verify which persisted documents were actually mutated. The values AON/MCO and counts are pinned by the workflow's declared acceptance contract, not inferred from market results.

**Separate failed attempt:** [run 35439978926](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35439978926), created 2026-09-19 11:23:29 UTC, `Apply pre-cohort identity news repair once`, head `06805d689c6938dbb3d249359e004729bc3abc33`. Its **dry-run reconfirmation step failed** and the `Apply reviewed identity-only repair` and idempotency-verification steps were **skipped**. It does not show an additional successful mutation. A prior dry-run audit [run 35439832574](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35439832574) completed without an apply step.

## Inherited structural meaning

The pinned collector `news_collector.py` blob `868e3f0fcb118eef18ecb110c4dbc36922c6d055` explicitly writes `matched_tickers` elements as `{ticker, match_type}` objects (match types: ticker, keyword or sector_keyword), and pinned `score.py` blob `207efb569975dbffba4568d7b3b317700168e636` expects dictionary elements. **This means non-string elements are not automatically malformed**. The earlier census's 405,565 count is of elements failing a string-only ontology, not proof of malformed rows, affected cohorts or specific link values. PR #40 separately prepares a read-only type-only Mongo census to determine current structural distribution, without accessing actual ticker values.

## Scientific implications

1. **As-of associations must be versioned independently of the news record and text.** A fixed ObjectId and original `date` do not prove current `matched_tickers` existed at their dates. Candidate identity `(news_id,ticker)`, historical mapping and link availability must be reconstructed from **authenticated mutations / immutable provenance**, not from current enriched data.
2. **The distinction is outcome-blind.** This finding is from code and workflow execution metadata; no realized returns, model scores, winning portfolios, MM1 runs or market outcomes were observed in this audit.
3. **The positive evidence is bounded.** The workflow assertion establishes that its generated report claimed 3 inserts/3 completed update calls, while exact Mongo persistence, recipient document IDs, content-vintage link, other writer executions, and actual historical `linked_at` remain unverified. We cannot infer an exact per-document `linked_at` or the true observable news set for any retrospective cutoff.
4. **Timing:** the independent backfill workflow ran on 2026-09-19; the prior retrospective census dated 2026-09-10 predates it. The workflow is evidence of a later write opportunity and cannot be silently projected into September 10 data. If a later current collection contains those additional AON/MCO associations, do not backdate them to a July/August provider event simply because its record predates the repair.
5. **Control C0 clock:** frozen V5/V6 data/price clocks also require independent event, version and daily-close availability. This backfill does not itself prove Phase III suffered data leakage or change previously reported Phase-III results.

**Classification:** `EXECUTED_BACKFILL_WORKFLOW_ATTESTED`, `SCRIPT_APPLY_REPORT_COUNTS_ATTESTED`; **not** `PER_DOCUMENT_AS_OF_LINK_AUTHENTICATED`. The global research state remains `BLOCKED_SOURCE_AUDIT`; `historical_link_clock_authenticated=false`, `writer_exclusivity_authenticated=false`, `history_construction_permitted=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `scientific_counting_permitted=false`, `mm1_execution_permitted=false`.

## Next outcome-blind evidence gates

- Independently verify artifact identity, its exact redacted aggregate report and digest (if read access/retention remains available); **never publish raw source values or credentials**. The run reports are not a replacement for authoritative Mongo mutation acknowledgments/change-stream/audit logs.
- Bind the finite actual writer list, deployment intervals, permissions and whether any other direct edit/migration/update scripts ran. Read-only GitHub run/step metadata can help but cannot rule out manual writers, retries, deletes or DB-level changes.
- Establish immutable versioned asset-link mutation receipts or a prospective append-only link-observation ledger (UTC observation + exact news-vintage/link payload digest + historical universe/mapping). Without this, retrospective history counts are UNKNOWN at the affected cutoff, not zero.
- Freeze prospective common C0/S/B/T/O candidate manifest, history lookback **L**, time cutoffs, partitions/embargo/exposure ledger and baseline price availability **before** history-richness analysis. Only later with independent source and 60-calendar-day + five-day outcome maturity may model fitting and confirmation be proposed.
- The PR #39 synthetic B comparator and PR #40 type-only real-read instrument are separate, not merged or run against production. Neither their CI success nor this source provenance report permits actual research model fitting, AWS activation or MM1 changes.

No AWS operations, Mongo source reads, changes to Phase III files or production pipelines were performed while producing this report.
