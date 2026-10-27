# G2.2 — Authentic reviewer/editor requirement mapping from user-provided decision letter

Date received in conversation: 2026-10-27
Editorial letter date: **2026-10-26**
Manuscript: **ICOMPUTING-D-26-01069**
Decision: **MAJOR REVISION**
Deadline: **2026-11-25**
Primary evidence: **complete editorial letter copied directly into this conversation by the manuscript author.**
The original SMTP/MIME email bytes are NOT available to this audit, so a
provider-origin SHA256 is NOT asserted. The full letter and review comments
are not copied into a public source repo; this document gives faithful
paraphrases and stable work-item IDs.

## 22 traceable requirements, without double counting experiments

The editor specified **seven** administrative conditions tracked E-01…E-07.
Reviewer #1 supplied **unnumbered** comments, which we decompose into
**seven audit themes** R1-01…R1-07. Those IDs are *ours*,
not editorial numbering. Reviewer #2 supplied precisely **eight
numbered** comments, retained in order R2-01…R2-08.

| ID | Required resolution | Work package / evidence | Editorial route |
| --- | --- | --- | --- |
| E-01 | Point-by-point reply or rebuttal | G6 response matrix | G6/G7 |
| E-02 | Separate revised paper with tracked/highlighted changes | G5 version + change evidence | G5/G7 |
| E-03 | Separate high-resolution, preferably vector/editable figure files | figure sources and conversion check | G5/G7 |
| E-04 | Signed License to Publish and Conflict of Interest documents from **all** authors | signatory checklist; forms | G7 |
| E-05 | Permissions for reused/modified third-party graphics | rights ledger and permissions | G7 |
| E-06 | Authorship-change forms signed by all authors **only if authorship changes** | conditional checklist | G7 |
| E-07 | Submit by November 25, 2026 through Editorial Manager revision record | submission checklist | G7 |
| R1-01 | Independent later test without 60d outcome overlap | X1: unavailable, document G1.3 data limitation, prospective study separate | G4/G5/G6 |
| R1-02 | Cross-ticker CIs, short adjacent V2/V3 intervals and overlapping horizons | A1: reuse original ticker/news bootstrap and V4 weekly evidence, honest uncertainty | G3/G4/G5 |
| R1-03 | Explain and sensitivity-test P10 weighted validation percentile veto 15/25/35 | A2: historic cohort exploratory frozen threshold sensitivity; no ex-post optimum | G2/G3 |
| R1-04 | Conventional risk-management comparator (volatility/downside constraint) | A3: point-in-time volatility filter, baseline capacity matched; conditional on verified data | G2/G3 |
| R1-05 | Negative absolute excess-beta, actual investment return, risk, turnover and costs | A4: clearly scoped economic outcomes and flat alternative; no realized-trading claim without portfolio simulation | G2/G3/G5 |
| R1-06 | Human-designed deterministic rules vs observed human judgment; model independence language | A1: tighten noncausal HDPG claims | G5 |
| R1-07 | Second ranker as model-agnostic stress test | A5: require existing authentically frozen alternate ranker; otherwise qualification | G2/G3 |
| R2-01 | HDPG vs ordinary algorithmic risk filter, human-defined vs human causal effect | A1 (shared with R1-06) | G5 |
| R2-02 | Why prediction P10 and why weighted percentile 25 within calibrated P10 | A2 (shared with R1-03), separate prediction quantile vs veto threshold | G2/G3/G5 |
| R2-03 | Overlap of 60d V2/V3 targets, independence misinterpretation | A1 + X1 | G4/G5 |
| R2-04 | V2/V4 ticker-cluster 95% CIs cross zero | A1 | G4/G5 |
| R2-05 | Flat/no-action, negative targets, nontradable excess-beta, costs | A4 (shared with R1-05) | G3/G5 |
| R2-06 | Reason for K=floor(0.10N) and capacity/selection assumptions | A6: analysis rationale + fixed 5/10/15% exploratory grid subject to feasibility | G2/G3/G5 |
| R2-07 | V4 improvement drop (+0.0276), unstable weekly effects | A1: six-week original frozen descriptive profile, dependence-aware caveat | G4/G5 |
| R2-08 | Additional literature on AI-assisted financial decisions | A7: verify citations and differentiate deterministic risk controls vs governance | G5 |

## Deduplicated work packages and prioritization

| Package | Work | Type and status | Requirement coverage |
| --- | --- | --- | --- |
| A1 | Reconcile uncertainty, overlap, 6-week V4 effect and human-defined claim framing | **existing historical evidence / descriptive**, ready for G5 claim constraints | R1-02, R1-06, R2-01, R2-03, R2-04, R2-07 |
| A2 | Validation-only weighted cutoff P15/P25/P35 of the **same calibrated P10 model**, with acceptance/capacity, K and downside outcomes | **post-outcome exploratory**, NOT YET PRE-FROZEN | R1-03, R2-02 |
| A3 | One genuine volatility/downside comparator with same baseline rank, price-as-of provenance, K and capacity | **post-outcome exploratory conditional on price source**, NOT YET PRE-FROZEN | R1-04 |
| A4 | Financial performance semantics, raw/tradable returns vs excess-beta, flat arm, downside, turnover and costs | **partly descriptive, empirical portion conditional** | R1-05, R2-05 |
| A5 | Second original fully independently frozen ranking model | **NOT EXECUTABLE unless original prior booster/checkpoint exists** | R1-07 |
| A6 | Top-K=10% capacity rationale and 5%/10%/15% descriptive sensitivity | **post-outcome exploratory conditional**, NOT YET PRE-FROZEN | R2-06 |
| A7 | Verified domain citations and literature crosswalk | **documentation**, no price/target access | R2-08 |
| X1 | Non-overlapping independent 60-day event holdout | **NOT EXECUTABLE FOR CURRENT REVISION**: no later point-in-time, outcome-blind cohort identified in G1.3a/b; future signed prospective experiment only | R1-01, R2-03 |

Do not describe A2/A3/A4/A6 as newly confirmatory even
if G2 freezes their specifications now: original May/June
V2/V3/V4 outcomes are already known. Show **all thresholds
and all risk/feasibility outcomes**, including worse alternatives.

## Special methodological constraints

**Distinct percentile meanings:** `P10` represents a
10th-quantile predictive **outcome distribution**;
`P15/P25/P35` in the revisor's suggested sensitivity
are defined in this revision plan as the **15th, 25th,
35th weighted percentiles of the validation distribution
of the *same* calibrated P10 predictions**. The original
guardrail uses weighted validation P25; this does not
authorize training P15/P25/P35 predictive quantile models
or moving the baseline frozen P25 rule. Do not select the
best alternative by the old holdout's outcome.

**Original negative results preserved:** V1 absolute P10>0
feasibility FAIL (0 accepted); V2/V3/V4 guardrail absolute
mean `forward_excess_beta` remains negative; ticker
cluster CIs cross zero in V2 and V4. Four of six V4 ISO
weeks have positive within-week delta. No pooled independent
test p-value across overlapping 60d forward intervals.

**Editorial claims:** A positive incremental mean is not
proof of positive alpha/profit or a cash-generating strategy;
deterministic human-specified rules are not randomized
human treatment; evidence on only one ranker is not
evidence of experimentally model-independent improvement.

## Status and controlled path forward

1. Requirement-by-requirement mapping: **CAPTURED from user-provided letter**.
2. Original provider MIME authentication: **not independently verified**;
   the user's supplied text suffices to scope drafting, not to
   assert cryptographic origin.
3. Complete dataset/hash/precision/probe-preflight for A2, A3,
   A4, A6: **PENDING**. No future target or inference execution.
4. G2 adversarial statistical methods signoff: **PENDING**.
5. G2 freeze commit + protocol digest: **PENDING**.
6. G3: **NOT AUTHORIZED** until conditional analyses are
   either fully specified/frozen or explicitly non-executable.

Proof references:
- `G1_TO_G2_STAGE_HANDOFF.md`
- `G1_3B_BROAD_SOURCE_TRIAGE_STOP.md`
- `G2_REVIEWER_TRACEABILITY_PROVISIONAL.json`
- `G2_REVISION_PROTOCOL_DRAFT.md`
- `G2_3_ANALYSIS_PACKAGES_DRAFT.md`
