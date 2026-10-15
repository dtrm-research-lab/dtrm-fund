# Phase IV — First current-Mongo observed-window pilot v0

**15 October 2026 — outcome-blind, contract BEFORE implementation.**

## One deliverable, not another retrospective-clock gate

The user agreed to progress with independently captured future Temporal State evidence while preserving Phase III/MM1 in production. Before deploying or activating AWS, run a bounded **read-only observation** of current `trumpMinMax.trumpNews` on the operator's existing authenticated Mac Mongo configuration. This operator pilot quantifies the past-60-publication-day source coverage and confirms actual legacy `matched_tickers` element shapes **without exporting any news or ticker values**. It is the first scientific-source reconnaissance step for a future Mongo snapshot adapter, not the 14-day authenticated AWS/FMP campaign.

The original Phase-IV Stage-0 research contract remains DRAFT_FOR_REVIEW. No change to v3's preregistered 56 slots, existing AWS Lambda or FMP probe; no method-selection, training, outcome or production access.

## Registered graph and exact I/O

Inputs: operator-local `--env-file` (optional; existing `configured_uri` semantics; never pasted or copied), `--output` under an existing private, operator-owned, non-world-writable directory. The CLI runs **only when explicitly invoked**, never during CI, installation or GitHub Actions; it makes one read-only Mongo connection using existing `salvage_live_io.configured_uri` and `quiet_driver`. Fixed database/collection and projection `_id,date,text,matched_tickers`. No FMP, provider keys, prices, targets, ML models, AWS or bucket S3. The operator's current Mongo access may already be permitted for bounded private research from the evidence-first operational amendment; actual rights for retention/redistribution are not inferred.

Node 1: Freeze operator observation UTC start *before* the read, calculate a **publication-day** window from the UTC start date inclusive of the previous 59 days. A publication day is NOT original `first_seen`.

Node 2: `count_documents({})` (must be ≤250,000), then project/stream `find({}, projection=fixed, sort=_id ascending, limit=250001, batch_size=500)` with `ReadConcern('majority')`. Only BSON ObjectIds are structurally accepted. No prefilter by publication day (preserve stable count and detect future/unknown dates). Validate strict sorted IDs, `date` leading strict ISO day, `text` str and `matched_tickers` array. Normalize no identifiers. Count rows and daily publication-day histogram in the 60-day window. Record shape categories: empty, string-only, object-only, mixed/other; **do not call object elements malformed** without assessing actual semantics. Cap is fail-closed before a 250,001st row; huge or malformed document fails closed. A final count_documents must agree; count consistency is **not** snapshot isolation.

Node 3: Compute a deterministic SHA256 transcript over each ordered *raw projected BSON* preceded by an 8-byte unsigned length. This is an **engineering digest of the exact returned projection bytes**, not an independently signed clock or durable Mongo snapshot. The output JSON contains no text, IDs, ticker values, source URLs, provider or account identities. Operator UTC interval and counts only. Never upload raw data or even the aggregate without explicit review. A hash over read documents is not a content-vintage proof.

Node 4: After all reads, validate `initial_count = observed_count = final_count`, observation start ≤ end, bounded at 250k, then produce an **exclusively created**, `0600` canonical UTF-8 JSON file in an existing safe parent. Fail closed if the target exists, is a symlink, or source changes during count/stream. Serialize no stderr, connection strings, private paths or source documents. No output on failure.

## Nonpromotion invariants

Every successful report must carry:
- `status=PASS_CURRENT_MONGO_WINDOW_OBSERVATION`, `execution_mode=operator_live_mongo`;
- `scientific_status=BLOCKED_SOURCE_AUDIT`;
- `atomic_mongo_snapshot_authenticated=false`, `historical_source_first_seen_authenticated=false`, `historical_link_first_seen_authenticated=false`, `source_complete_60day_history_authenticated=false`;
- `temporal_state_training_permitted=false`, `outcomes_access_permitted=false`, `mm1_execution_permitted=false`, `aws_activated=false`.

One observation cannot prove it retained all notifications available at any earlier day nor all positive relations; zero count for a publication date means *zero rows currently present for that date in the bounded read*, not an authenticated historical absence. Probing Mongo today with dates up to today does **not** retrospectively admit those news items into yesterday's model. An actual future snapshot should use a consistent snapshot/transaction or immutable write protocol and an approved durable private storage strategy. A future evidence adapter must pin link-level identity and retention rights and must never silently use these diagnostics as training input.

## Acceptance

Contract commit precedes implementation. Unit tests pure synthetic + mock live transport; strict timestamp and malformed JSON cases; no private bytes in reports, no silent source mutation, no overwrite, CI refusal, hashed 250k cap. Ruff, mypy strict, inherited `pytest`, 157-file Phase III preservation and PR into `research/phase4-temporal-state`. No merge without separate review.

**Operational handoff after PR validation:** operator can run once with existing Mongo credentials in private environment; share only the redacted output summary and SHA digest. The next AWS step is a separately reviewed *real diagnostic* using the existing SHA-pinned ZIP and deployed diagnostic S3 bucket, not an unreviewed new scheduler or migration of Mongo. No AWS writes or extra recurring automation in this increment.
