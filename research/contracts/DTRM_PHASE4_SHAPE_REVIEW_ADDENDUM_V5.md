# Phase IV shape audit — review addendum v5

2026-10-15. Registered before code/doc correction on PR #40 head `fec656c37da0a03477d44013da729d9e0b4deada`.

Codex P2: the **operative** operator runbook still says the conditional backfill is “not evidence it ran”, in contradiction with independently checked backend Actions run `35439965103` (2026-09-19) and the later correction. Replace this sentence **in place** (not a contradictory appendix) with: the actual `--apply` workflow executed successfully, its script reported 3 insertions and 3 completed update calls; individual `modified_count`, affected article IDs, and first link availability are **not independently proved**. Preserve source blobs and the separate PR #41 provenance report. No live Mongo/AWS calls; no MM1 or scientific promotion.
