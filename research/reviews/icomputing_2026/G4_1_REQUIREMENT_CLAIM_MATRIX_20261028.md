# G4.1 — 22-requirement adversarial claim / evidence / response matrix

**Status:** initial critical review; open, not G4 signed off.  
**Editorial case:** ICOMPUTING-D-26-01069; source of requirement mapping is G2_2_AUTHENTIC_REVIEWER_REQUIREMENT_MAP.md.  
**Evidence provenance:** Git SHA-anchored code + operator-reported local aggregate reports; not an independent verification of raw private files.  
**Convention:** P = experimentally addressed with qualification; L = documented limitation/claim restriction rather than experimental fulfillment; D = drafting/documentation outstanding; E = editorial action outstanding. These are **work states**, not reviewer acceptance.

## Reviewer #1 (7 work themes; IDs are internally assigned)

| ID | Demand / skeptical test | Disposition, evidence, outstanding action | Proposed G5/G6 treatment |
| --- | --- | --- | --- |
| R1-01 | Unused independent and nonoverlapping matured 60-day holdout | **L** — G1.3a/b searched specified local scope, none authenticated; overlapping forward periods persist. A prospective design is future work, not a completed test. | Explicit 'not demonstrated'; remove independent temporal-validation rhetoric; forward protocol in future work. |
| R1-02 | Dependence, short V2/V3, uncertainty by ticker | **P+L** — G3.1 36 CI blocks, original q25/K10 ticker interval includes 0 in V2/V4; news and ticker bootstrap are alternative uncertainty views; 60-day calendar overlap remains. | Disclose full ticker/news side-by-side, dependence and no pooled independent cohort p-value. |
| R1-03 | q15/q25/q35 weighted threshold sensitivity | **P** — G3.1 A2 fixed 3x3 grid, 10k per cluster scheme; q25/K10 parity retained. No q35-vs-q25 paired significance test and no multiplicity correction. | Report **all nine** effect/coverage/feasibility cells; say q35 is NOT validated as a better threshold. |
| R1-04 | Conventional volatility/downside benchmark | **P+L** — G3.2 original A3 60k paired news/ticker resamples; risk veto observed better than P10 in all three historical means; six nominal direct CIs exclude 0. Source saved 2026-07-05; vendor vintages/adjustments unverified. | Report adverse benchmark in core Results; classify as retrospective exploration not confirmed point-in-time deployable superiority. |
| R1-05 | Negative absolute target, actual returns, risk, costs/turnover | **L+D** — A4 draft and original negative absolute excess-beta evidence; no capital-constrained self-financing portfolio ledger, realized P&L, turnover or credible cost study. | Separate forward_excess_beta from absolute returns/cash P&L; 'not estimable' where no data, not invented. |
| R1-06 | Human causal effect, model independence | **L** — human *specified* deterministic rule tested; no randomized human participation. Same frozen ranker; no independent cross-model effect. | Reformulate architecture as design, not empirical human superiority. |
| R1-07 | Second independent ranking model | **L** — no authenticated original pre-outcome independent second ranking model in G1 source scope. | Do not claim model-agnostic empirical validity; state required second-model protocol. |

## Reviewer #2 (eight numbered comments)

| ID | Demand / skeptical test | Disposition, evidence, outstanding action | Proposed G5/G6 treatment |
| --- | --- | --- | --- |
| R2-01 | Human judgment versus ordinary algorithmic filtering | **L+D** — mechanism is deterministic veto, not human participation; novelty must be formalized as explicit, auditable rule interface, if supported, not as human causal lift. | Make treatment and counterfactual precise; compare literature on selective prediction and risk filters. |
| R2-02 | Why P10 and weighted validation q25 | **P+D** — P10 is predicted 10th quantile; q15/q25/q35 are weighted *percentiles of the original P10 validation distribution*; G3.1 sensitivity observed, original q25 unchanged. | Correct terminology, describe rationale as ex ante design choice, not established optimum. |
| R2-03 | V2/V3 overlapping 60-day outcomes | **L** — overlap is real despite separate news dates. | Correct cohort-independence language; no combined independence significance. |
| R2-04 | Original V2/V4 ticker CIs contain zero | **P+L** — explicitly preserved; G3.1 fresh nominal bootstrap still q25/K10 V2/V4 includes zero. | Show rather than hide; no uniform ticker-level robust lift. |
| R2-05 | No-action/flat, expenses, nontradable target | **L+D** — flat cash cannot be compared directly to beta-adjusted target; data insufficient for realized trading account. | Discussion of absent economic comparison and prospective portfolio experiment. |
| R2-06 | K=floor(.1N) justification and sensitivity | **P** — G3.1 A6 K5/K10/K15 x cohorts completed with 10k news/ticker blocks; no capacity optimum. | Report nine feasibility/effect cells; K is a selection-coverage assumption, not observed capital. |
| R2-07 | V4 attenuation and weekly reversals | **P+L** — original V4 +0.02756 vs +0.1443/+0.1494 in V2/V3; only 4 of 6 V4 ISO weeks positive. | Explicit heterogeneous temporal descriptive evidence, no post hoc regime explanation. |
| R2-08 | Relevant work on ML finance, risk filters, human-AI | **D** — G2.4 shortlist verified but not yet inserted; possible additional Vaccaro et al. (2024) after source verification. | Literature subsection with precise novelty boundary; cross-check bibliography and source claims. |

## Editor (seven operational requirements)

| ID | Requirement | Disposition and exit evidence |
| --- | --- | --- |
| E-01 | Full point-by-point reviewer response | **E** — existing G6_REVIEWER_RESPONSE_WORKING_PREVIEW.md is pre-G3, stale. Update all 15 scientific themes and change pointers. |
| E-02 | Separate highlighted/tracked revised manuscript | **E** — no finalized G5 artifact verified; need source baseline/diff and clean revised version. |
| E-03 | Figures in separate high-resolution/editable accepted files | **E** — inventory figure source/format, confirm independent source and no PowerPoint figure export masquerading as approved design file. |
| E-04 | License to Publish and COI signed by all authors | **E** — author/signature inventory pending. Official journal normally requests completed forms before acceptance, but the **case-specific editor letter governs if it requires earlier delivery**. |
| E-05 | Permissions for third-party figures if reused/modified | **E** — audit rights/attribution; no assumption that third-party content is free. |
| E-06 | Authorship-change form if applicable | **E conditional** — preserve author list or gather all required signatures if altered. |
| E-07 | Editorial Manager revised submission by 2026-11-25 | **E** — no completed upload/submission; G7 evidence and user authorization needed. |

## Mandatory claim changes to apply in G5

| Candidate claim | G4 disposition | Why |
| --- | --- | --- |
| Human-defined rules beat AI alone | **REJECT** | No human-vs-AI counterfactual; all tested algorithms have human-authored objectives. |
| Human-governed AI is statistically equivalent/noninferior to autonomous AI | **REJECT** | No prospective margin, no autonomy experiment and noninferiority analysis. |
| P10 uniformly improves across ticker uncertainty | **REJECT** | Original q25/K10 V2 & V4 ticker CIs include zero. |
| P10 is best risk control | **CONTRADICTED** | Conventional volatility improves the tested metric by more in all 3 A3 historical comparisons. |
| The A3 volatility filter was available at the historical decision-time in the same form | **NOT AUTHENTICATED** | Historical bar dates exist, but original provider vintage/adjustments unauthenticated. |
| Original effects imply trading profitability | **REJECT** | Beta-adjusted target is not realized portfolio profit; absolute means remain negative. |
| Three historical cohorts are three independent 60-day confirmations | **REJECT** | Forward windows overlap. |
| HDPG provides an explicitly specified, reproducible **algorithmic** constraint-evaluation interface around one ranking model | **CONDITIONALLY DEFENDABLE** | Demonstrated same ranker + policy veto + K + source/CI evidence; require comparison to ordinary existing methods before claiming novelty. |
| Keeping humans responsible for purposes is a normative design principle | **DEFENDABLE AS PRINCIPLE ONLY** | It is not an experimentally established causal performance benefit. |

## Claim-evidence ledger minimum for the final manuscript

Each substantive Results/Abstract/Discussion assertion must map to:
(1) paragraph & figure/table ID; (2) exact original or supplemental source/target definition; (3) immutable code commit; (4) source manifest/report SHA; (5) confidence scheme and any infeasibility; (6) **POST_OUTCOME_EXPLORATORY** tag when applicable; (7) limitation and competing explanation; (8) response-to-reviewer ID.

For A3 cite the operator-reported local report SHA256 824f9466894ff7fe6ef7680fe4314cb6b59feb068e43d0db4034608fa60c2428, and disclose that the full report is not independently read in the public repo. Never fabricate raw outcome observations or a multiple-comparison-adjusted significance claim.

**G4.1 remains OPEN until original manuscript source/draft section positions are mapped to this ledger and an independent adversarial reader checks the manuscript's revised language.**
