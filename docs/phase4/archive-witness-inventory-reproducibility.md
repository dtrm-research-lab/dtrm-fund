# Reproduce the 21 archived Phase-IV positive Time State witnesses offline

**Research status:** exploratory, source availability partially identified, **BLOCKED_SOURCE_AUDIT**; not a trade/model/outcome or a proof of link first-seen time. No AWS, Mongo, FMP, network, source text or ticker values are read by this procedure beyond the files the operator supplies locally.

## Canonical source identities

The repository includes `research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json` with exactly 21 **public metadata-only** GitHub Actions run IDs, artifact IDs, GitHub artifact-created UTC timestamps, original ZIP SHA256s, and frozen `sourceNewsSha256`/`familyManifestSha256`. These are the 21 archive inputs for the aggregate-only census. They can be checked against `tech-com-UA00001/theresistance-back` using an independently authorized GitHub account **without** exposing contained article IDs/tickers/URLs/text.

Source credentials and downloaded private ZIPs must remain outside this repository and should not be pasted into chat. GitHub may expire the original artifacts; a reproducibility package should retain these ZIP bytes privately within the organization under separately agreed rights and security controls, not in public research history.

## Local-only reproduction

From the repository root with Python 3.11, place the 21 original downloaded ZIPs (without unpacking) into a **private** directory so the exact filename for each is `<artifact_id>.zip`, e.g. `10424883893.zip`. Do **not** rename or mutate the ZIP's internal entries. The manifest pins the expected SHA and rejects edited archives.

```bash
PYTHONPATH=src python research/experiments/derive_phase4_archived_time_state_inventory_v0.py \
  --manifest research/evidence/DTRM_PHASE4_21_ARCHIVED_RANKING_SOURCE_MANIFEST_V0.json \
  --archive-dir /private/local/path/to/the/21/zips \
  > /private/local/path/phase4-aggregate-only-reproduction.json
```

Check the output **locally**, including flags `source_completeness_authenticated=false` and `model_fitting_permitted=false`, before sharing. It emits only family/run-independent aggregate counts, asOf dates and selected positive overlap quantities, never original IDs, ticker strings, URLs or text. No backend/environment variables or provider credentials are required.

Expected current v0 aggregate invariants from the initial audited selection:
- 21 snapshots, 3 families with 4, 8 and 9 snapshots;
- asOf 2026-09-15 through 2026-10-13;
- 21 of 21 five-day candidate exports and 13 of 21 two-day candidate exports hit the fixed 500-item cap;
- 36,440 unique (article ID, exact text digest, ticker) **selected representation triples** across both exports;
- 18 adjacent transitions share the same family; sums of *repeated* positive shared triples across those transitions: 22,348 for 2d, 26,396 for 5d.

Any mismatch means `REPRODUCTION_NOT_CONFIRMED` until independently investigated, **not** permission to change historical sample/windows or claim a different scientific result.

## Interpretation

The selected and often-capped snapshots are not an exhaustive Mongo/market-news universe. Presence within a SHA-pinned archived representation is positive evidence at that archive's externally observed GitHub creation time. Absence in output is **UNKNOWN**, not proof the link did not exist. `asOf` market date cannot be backdated to news/link first-seen. Even two equal-text observations with the same link at different captures do not certify persistence between them. A separate source-rights and event-version clock/price-vintage proof is necessary before any comparative Temporal State model fitting.

The derived JSON schema differs from the earlier descriptive local report whose SHA was pinned as `14c10f19012010073a157b2d9aefc2007c8f768a4077f13ce0bdf000924daa37`; **do not expect the serialized output SHA to match that older report**. Compare the preregistered *aggregate quantities and source identities*, not arbitrary serialization hashes.
