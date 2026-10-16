# Phase IV matched-tickers shape audit — source-informed review addendum v2

**2026-10-14 | REGISTERED BEFORE IMPLEMENTATION | outcome-blind static backend-source inspection.**

## New independent static code evidence, not actual Mongo proof

At backend repository `tech-com-UA00001/theresistance-back`, pinned commit `05cbae1a074c4b23e445d6c313299b6b622054a3`:

- `agent/trump_model/news_collector.py`, Git blob `868e3f0fcb118eef18ecb110c4dbc36922c6d055`: `match_news_to_tickers` produces a list of objects with explicit `ticker` and `match_type`; recognized source-code enum values `ticker`, `keyword`, `sector_keyword`. This means a large non-string `matched_tickers` element count is **plausibly expected structure**, not proof of malformed data.
- `agent/trump_model/score.py`, blob `207efb569975dbffba4568d7b3b317700168e636`: `get_tickers_from_news` explicitly keeps `match.get("ticker")` from dictionary elements.
- `agent/trump_model/precohort_news_identity_backfill.py`, blob `073648fedd6ad6c20331beb7268d5a897c111256`: registered script docs and code show default **dry run**, optional explicit `--apply`. When applied it may `insert_one` new news and `update_one({"_id":...},{"$set":{"matched_tickers":merged}})` existing news associations (for the narrow MCO/ICE/AON/FI case). This identifies a **possible post-insert link mutation path** not covered by a simplistic insert-only collector audit; there is **no proof that it was deployed, authorized, or run with --apply** in any interval. It cannot be used to assert actual mutation, nor to upgrade historical as-of authenticity.

The previously accepted 63,873 current rows / 405,565 non-string nested elements remain an outcome-blind structural observation. No retrospective numeric claim is rewritten. The existing v0 source-bound scope and sanitized aggregator are retained.

## Preregistered modification of the dormant aggregate query

Expand the fixed **allowlisted object field type** set from five keys `ticker, symbol, name, score, confidence` to six by adding `match_type`, the confirmed static writer field. Return only its BSON type (e.g. `string` or `missing`) and aggregate element count, never the value `ticker`, `match_type` itself, a raw document, URL or text. The pipeline must remain a read-only `$type`/$facet group, and the reducer strictly rejects extra keys/value-bearing output. Existing tests update their fixed synthetic aggregate fixture with `match_type` type, test missing/invalid type classification, and assert no actual match-type value is reported. Update the outcome-blind runbook to distinguish code-expected shape versus source-proven schema.

No live Mongo read, pricing, protected targets, FMP, AWS or deployment is authorized. Source shape success would **not** prove historical link availability or B/T training sufficiency. The existence of a potential mutable writer is referred to a separate source/write-authority audit; do not erase original unknown runtime/write-authority fields.

Acceptance: contract-before-code ancestry, 4/4 exact-head CI, Codex review, no inherited Phase-III/MM1 change and human approval before merge; operator-only actual read still requires separate explicit approval.


## Later correction, 2026-10-15 — execution attested

The earlier “no proof it ran with --apply” statement is **superseded**: authenticated GitHub Actions run [35439965103](https://github.com/tech-com-UA00001/theresistance-back/actions/runs/35439965103) on **2026-09-19** at exact head `87f21b985ec03d2ba24819bce787b0cb7f2d58e4` completed the `--apply` workflow; its checked script report claimed **3 inserted rows and 3 completed update requests** (`addedMatchCounts={"AON":2,"MCO":4}`). A separate repair run 35439978926 failed **before** its apply step. This is **positive procedure-level evidence**; exact Mongo modifiedCount, affected IDs, actual changed history, writer exhaustiveness and `linked_at` remain unproven. See [PR #41](https://github.com/dtrm-research-lab/dtrm-fund/pull/41) for the full pinned evidence report. Scientific status unchanged.
