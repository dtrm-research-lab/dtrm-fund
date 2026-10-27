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
