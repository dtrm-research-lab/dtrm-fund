# Phase IV — Partial identification of historical link availability from positive archived witnesses

**Research note, 2026-10-15; follows an explicitly exploratory archive census.** This is a source-identification protocol, not a preregistered model effect, actual history construction or G5 activation.

## Identification problem

Let `e=(providerArticleId, exactContentSha256, ticker)` denote a *representation-level* article–asset link, and `a_i` the independently verified archive-created UTC time for archived frozen ranking capture `i`. Let `S_i` be the positive selected link representations inside that archive (2d or 5d with known clipping/selection). The archive itself is SHA-verified. A source article's `publishedAt` or the ranking market `asOf` are **not** substitutions for `a_i`.

What the witness can establish:

- If `e in S_i`, the **frozen ranking representation** of e existed no later than `a_i` (subject to independent attestation of metadata, archive integrity, and evidence-chain permissions).
- It does **not** establish when the provider first published the article, when the link first became valid, what the classifier would have matched historically prior to `a_i`, or whether today's Mongo `matched_tickers` were present at that older time.
- If `e not in S_i`, classify `UNKNOWN_SELECTED_EXPORT`. This is true even in a 2d batch with fewer than 500 selected items due to URL, eligibility, deduplication and window selection; missingness cannot be mapped to absence.
- If `e` occurs in `S_i` and `S_j` with identical content at `a_i < a_j`, the representation is positively witnessed at **two distinct captures**. No assertion of uninterrupted persistence on `(a_i,a_j)` is permitted without an independent append-only write/revision/retention trail; absence and reappearance between captures cannot be ruled out.
- If the archive was retained and independently accessible after `a_i`, future research may preregister *a separate historical archive-replay information policy* with inputs limited to archived captures provably available by each cutoff. That would answer a different estimand than complete provider news-history access and cannot silently be compared to frozen C0 as if it had a common full universe.

## Admissibility decisions at arbitrary decision cutoff t

**No inference from `asOf` alone.** For a fixed `t`, `source_proven_positive_by_t` requires all of: explicit authenticated `a_i <= t`, immutable ZIP/source/manifest hash and link identity, the *same* exact source-vintage digest, and independently confirmed source storage access/rights at `t`. The current exploratory census establishes several archive content witnesses and GitHub created-at metadata, but does **not** establish universal capture rights, source completeness, source first-seen, historical rule parity or retrospective operational availability across all decision cutoffs. Therefore no G5 input history is yet admissible.

Separately maintain `linked_at_lower_bound` as UNKNOWN. The earliest observed positive archived time is an **upper bound on representation availability**, not the earliest real link creation time. Never set `linked_at = publishedAt` or default UNKNOWN to zero.

## Family and truncation gates

Source/model family digest changed twice across the 21 archives (segments 4, 8, 9). A cross-family link match may be noted only as an identity intersection, not equivalent C0/S/B/T/O selection policy. In 21/21 5d archives and 13/21 2d archives the fixed 500 cap censors possible missing links; the other 2d archives are still content-selected, not exhaustive.

The 36,440 unique represented positive triples from the exploratory census are a union **over selected/censored outputs**, not an unbiased 60-day history or independent model observations. 22,348 summed within-family 2d adjacent shared-link appearances are repeat counts, not a new independent population. The Sep-19 verified `--apply` backfill is a separate *possible link-mutation mechanism* with successfully reported update requests; aggregate reports do not identify exactly which documents were modified.

## Operational research priorities (non-authorizing)

1. Verify retention/archive access evidence, immutable output created-at UTC and source family manifests for each archived run.
2. Preserve a **positive-only and censoring-aware** observational ledger *privately*; no public release of link IDs/tickers/articles/URL, no negative labels synthesized from absence.
3. For genuine prospective Time State, capture version first-seen, ticker association observations, subsequent edit/mutation receipts, strict acquisition UTC, same point-in-time universe and all C0 price-vintage clocks. Use user-authorized AWS diagnostic infrastructure only after its separate write/activation gate.
4. Fix **cohort, chronological partition, history lookback L and cutoffs before measuring temporal richness**, preserving untouched confirmation and outcomes matured at 60 days + 5-day price tolerance.
5. Only then preregister B/S/T/O fitting and ask the scientific question whether robust policy results improve relative to C0. Never label an archive-recovery count as an economic uplift.

**Current gates:** `BLOCKED_SOURCE_AUDIT`; `historical_link_clock_authenticated=false`, `source_completeness_authenticated=false`, `model_fitting_permitted=false`, `outcome_access_permitted=false`, `mm1_execution_permitted=false`, `scientific_counting_permitted=false`. No production MM1 change.
