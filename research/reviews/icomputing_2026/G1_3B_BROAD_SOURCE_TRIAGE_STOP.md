# G1.3b — Broad local source filename triage, decision: STOP historical cohort discovery

Date: 2026-10-27
Manuscript: Intelligent Computing ICOMPUTING-D-26-01069

**Operator execution:** unchanged `ic_g1_3_news_source_inventory.py`
with original local roots `~/Desktop/DTRM_Lab` and
`~/Desktop/Play4Fun`. Program terminal status remains
`G1_3A_FILENAMES_ONLY_AVAILABLE_NEWS_NOT_YET_VERIFIED`,
since G1.3b is the *second scope of the same metadata-only
inventory*, not a newly validated test.

## Exact operator-reported filename counts

- `embedding_candidate/HISTORIC_OR_CONSUMED`: **29**.
- `embedding_candidate/NO_DATE_IN_FILENAME`: **3**.
- `news_event_candidate/HISTORIC_OR_CONSUMED`: **10**.
- `news_event_candidate/NO_DATE_IN_FILENAME`: **7**.
- `pairs_candidate/HISTORIC_OR_CONSUMED`: **11**.
- `pairs_candidate/NO_DATE_IN_FILENAME`: **39**.
- **No entries** in any `AFTER_CONSUMED_HOLDOUT_FAMILY`
  filename-date bucket.
- **49** newer-or-undated entries printed and not opened.
  Their structure and scientific contents were NOT examined.

### Named metadata-only triage

| Counts | Source paths or basename | Conservative interpretation |
| ---: | --- | --- |
| 1 | `PCDoMoney_Backend/Notebooks/Outputs/sbert_embeddings_xgb_v1.npy` (43,664,000 bytes) | Original v1-era undated embedding; NOT evidence of later news/unused events |
| 1 | `PCDoMoney_Backend/Outputs/sbert_embeddings_binary.npy` (122,473,088 bytes) | Undated historical embedding; exact original event keys/date coverage UNVERIFIED |
| 1 | `PCDoMoney_Backend/Outputs/trump_score_lr_sbert_binary.pkl` (3,935 bytes) | Undated old SBERT classifier/scoring-related Pickle; NOT an event-time news cohort |
| 7 | `dtrm-fund/tests/fixtures/phase4_event_batch_v0.json` (1); `theresistance-back*` Phase IV prospective-news mapping/shadow-summary *test fixtures* (6) | Unit-test fixture files, NOT an independent HDPG observed event cohort |
| 39 | `dtrm-paymentgame` and `paymentgame-*` pair-audit/receipt descriptions (38) plus an `ebay_repair_validation` JSON (1) | Different experiment (smartphone PaymentGame), NOT `(news_id,ticker)` investment source pairs |

Classification is based on **filename/path semantics**, not
opening scientific contents or demonstrating event-date lineage.
The absence of dated new files in these roots does not imply
absence in a connected news service, an unexamined archive or
an explicitly future-collected source.

**Filename detector limitation:** the
`DATE_TOKEN = re.compile(r"20(?:25|26)-\\d{2}-\\d{2}")`
in G1.3a matches ISO-style `YYYY-MM-DD`, not `YYYYMMDD`.
Consequently, many **20261017–20261023 PaymentGame receipts**
appear in the `NO_DATE_IN_FILENAME` bucket. This is a
discovery-tool classification limitation and does not make
these files valid HDPG sources. Do not claim that *no files
of any kind* were created after June 2026.

## Study gate decision

`G1_3_LOCAL_HISTORICAL_INPUT_DISCOVERY_STOP_NO_ELIGIBLE_NEW_COHORT`

- **No time-stamped, unused later investment-news sample
  with original event IDs, acquisition-time provenance and
  point-in-time feature coverage has been identified in either
  scanned local set.**
- No new HDPG retrospective-outcome-blind holdout has been
  **authorized, scored, preregistered, or evaluated**.
- **STOP additional speculative local filename scanning.**
  New evidence would require a *separately justified*
  news provider/archive with auditable acquisition timestamps
  and disjoint news identifiers, or forward capture after
  a signed prediction-time registration.
- The revised article should use already consumed V2/V3/V4
  with explicit ticker-cluster CI limitations, and G1.2k/m
  historic reproducibility. Do not claim new independent G1.3
  validation, unconditional robustness or realized trading P&L.

## Historical evidence commitments unaffected

G1.2k sealed historical exact 40,320×390 replay dossier:
SHA256
`7d91095d42edf044d7f5030e23519291c156d95f4eddc766048b493744ae52ac`.

G1.2m separately sealed original date-only 265,145→40,320
V1 source selection parity:
SHA256
`388345ba7bcca9c9a5103584d999aef4f033a3656d746b26efae337cf569b81f`.

The original same-basename physical raw file vs V1 contract
cardinality documentary discrepancy remains OPEN.
No historic model-input numerical discrepancy remains known.
No original scientific file contents, forecasts, market
returns or model inference were accessed by G1.3b.

**Disposition: historical reproducibility PASS;
G1.3 new-cohort scientific gate BLOCKED; proceed with
Intelligent Computing major revision with declared limits.**
