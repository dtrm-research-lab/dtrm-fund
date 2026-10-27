# G1.3a — Input availability decision after local metadata-only search

Date: 2026-10-27
Manuscript: Intelligent Computing ICOMPUTING-D-26-01069
Decision: `G1_3_NEW_EVENT_INPUT_AVAILABILITY_NOT_DEMONSTRATED`

## Operator observations (filenames only)

G1.3a printed
`G1_3A_FILENAMES_ONLY_AVAILABLE_NEWS_NOT_YET_VERIFIED`.

Scanned research input directories, and **only** these two:
- `dtrm-fund/research/local_data`.
- `PCDoMoney_Backend/Notebooks/Outputs`.

Filename buckets:
- historic/consumed embedding candidates: 29.
- historic/consumed news event candidates: 10.
- historic/consumed pair candidates: 11.
- newer filename-dated candidates (after 2026-06-14): 0.
- undated embedding candidate: exactly 1 —
  `sbert_embeddings_xgb_v1.npy`, 43,664,000 bytes.
  From its name alone we cannot assign a newer event cohort
  or point-in-time validity. No contents were opened.
No historical or new target outcomes, prices, raw news text,
model weights or model predictions were accessed.

Separate original V1 date-only selection corroboration, G1.2m:
`IC_G1_2_declared_date_filter.json` SHA256
`388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.
Exact 265,145 candidate pair → 40,320 V1 historical
signal pair set, order and event timestamps using only
precommitted V1 event-date UTC window and original BRK.B alias.

Historical numeric reproducibility remains sealed in original
G1.2k dossier SHA256
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.
Neither dossier has been rewritten.

## What this decision DOES NOT claim

- Does not establish that new data do not exist in other
  local project directories, connected services, cloud
  buckets, API providers, archives or undated files.
- Does not assert the undated SBERT array has new independent
  news events.
- Does not authorize G1.3 inference or target opening;
  G1.3 preregistration remains UNFROZEN.
- Does not dilute the previously established G1.2 numeric
  reproduction and declared-date historic V1 selection PASS.

## Next bounded discovery (not yet run)

Reuse the **same** previously reviewed G1.3a metadata-only
script with distinct larger *known local research folders*:
```bash
AUDIT="$HOME/dtrm-ic-audit"
python3 "$AUDIT/ic_g1_3_news_source_inventory.py" \
  --search-root "$HOME/Desktop/DTRM_Lab" \
  --search-root "$HOME/Desktop/Play4Fun" \
  --out "$AUDIT/g1-reconstruction/IC_G1_3_broader_event_inputs_metadata.json"
```
These roots overlap the original two; redundant older
entries do not count as a new independent cohort.
If no newer filename-dated sources are identified
in this broader scan, stop speculative historical
cohort searching. Proceed through one documented
provider-specific acquisition pathway if access and
time-at-observation lineage can be established,
or design genuine future prospective capture for
a post-review test.

## Manuscript revision decision (Nov 25, 2026 deadline)

The present paper should rest on the completed original
frozen V2/V3/V4 tests and strongly verified historical
reproducibility (G1.2k/m), while **explicitly declaring**
cross-ticker and temporal robustness limitations:
- V2, V3, V4 original incremental Top-K mean
  excess-beta estimates: +0.144295, +0.149437, +0.027562.
- Ticker-cluster 95% bootstrap CI for V2:
  [-0.006220, +0.196153].
- For V3: [+0.007539, +0.193317].
- For V4: [-0.010468, +0.071820].
  CI crosses zero for V2 and V4.
- Within original reused V4 calendar event cohort,
  only four of six ISO weeks yielded a positive
  incremental Top-K mean; time-regime effect is not
  uniformly stable.
- These target statistics are `forward_excess_beta`,
  **not** realized portfolio profitability.
- Do not describe a new independent G1.3 prospective
  study as finished, or backdate a new study protocol.

## Separation between retrospective and prospective pathways

A new event interval with already historical data,
never previously scored and outcome-blind until a fixed
protocol, can be a **new retrospective holdout** if
all point-in-time source and embargo gates pass.
A genuinely future-prospective event starts after
preregistration, predicts at observation time, and
must wait 60 calendar days plus event-price alignment.
It cannot mature by Nov 25 if it starts Oct 27.

**STOP condition:** no source-and-provenance-verified new news
means G1.3 is not promoted. Publication revision can
proceed with transparent historical evidence.
