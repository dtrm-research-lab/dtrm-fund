# Phase IV — eliminate posterior synthetic raw-sighting denominator leakage v4

**2026-10-17. Before code.** Exact-head Codex P2 on `8e305b3a82be58bbf57e48347e2bedefb74e5139`: although supported post-cutoff siblings are excluded from positive age/count and uncertainty, `raw_synthetic_sightings` still increments *before* exclusion. Therefore merely appending a future revision changes a prior cutoff report, violating the registered as-of rule.

Fix synthetic as-of denominator only: validate all record type/identity/clock fields but **increment `raw_synthetic_sightings` only after excluding proved post-cutoff version or link**. No exposure of future-link values; legacy uncertain clocks remain counted as unknowns (not zeros). Test full report equivalence between `[v1]` and `[v1, post-cutoff-v2]` where version or link attested > cutoff, including raw count, roles, uncertainty and known ages. Do not train or make real source trust claim. No new Mongo, AWS, model or MM1 changes.
