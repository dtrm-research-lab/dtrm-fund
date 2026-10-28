# G4.0 — Adversarial scientific gate entry (OPEN; not a scientific PASS)

**Manuscript:** ICOMPUTING-D-26-01069  
**Date:** 2026-10-28  
**Editorial decision:** Major Revision, dated 2026-10-26; author-reported submission deadline 2026-11-25.  
**Review base branch:** research/ic-major-revision-2026, HEAD d57cfc5ec8cebfc810c6cb07ac4bb970249fa400.  
**This work branch:** research/ic-g4-adversarial-scientific-pivot-20261028.  
**Status:** G4_ENTRY_RECORDED_ADVERSARIAL_REVIEW_OPEN — NOT G4 PASS, NOT G5 OR G6 AUTHORIZATION.

## Mission and separation of objectives

1. **Editorial:** defend the actual, already-performed HDPG original and supplemental experiments; answer all 22 editor/reviewer requirements (E-01..E-07, R1-01..R1-07, R2-01..R2-08) with either evidence, an explicit limitation, or a correction of manuscript claims.
2. **Scientific evolution:** clarify the distinction between prediction/optimization and the legitimate authority to set objectives, constraints, refusal conditions and accountability. Describe Human Clause as a **governance proposition**, NOT as a human-versus-AI performance result.
3. Never convert already-consumed original historical outcomes into an unobserved confirmatory experiment. New noninferiority/equivalence, human-governed-versus-autonomous and second-ranker studies need separate prospective designs.

**Proposed scientifically bounded thesis:** Human-specified decision constraints provide a transparent, testable interface to a machine-generated ranking. Their predictive/economic value is conditional on policy and evidence and must not be inferred from human authorship. Current results evaluate *deterministic algorithmic constraints*, not causal effects of interacting humans or the superiority of human governance itself.

## Immutable historical / executed source anchors

- Original frozen source: c7502a690162459cdfb3413573e3133c42efb126.
- G2 immutable revision protocol: 3d53d2d5c7a4e3345b238b2b045fbd47f6e40de0; operator-attested G2 frozen/approved. See G2_18_G2_FROZEN_G3_0_ENTRY_RECORD.md.
- G3.1 A2/A6 scientific source: 0c5e433f10ce742bc129b666dfc4551f4b2fd21b.
- G3.1 full historic bootstrap report local SHA256: 53c4618f86f46a80a5a783c3449a8d120379f26c8d459c8e740dd4fb63697968. Read-only QA previously reported PASS, 18 exploratory settings, 36 news/ticker blocks, zero infeasible draws. See G3_1_A2_A6_36_CI_AUDITED_INTERPRETATION.md.
- G3.2 A3 paired-bootstrap frozen code: 2e4cce43f59d23ea5758bc7581cf7f42969cec9e. Local operator execution 2026-10-28: 138/138 tests passed; 3 cohorts x 2 cluster schemes x 10,000 resamples = 60,000, 36/36 nominal CIs available, zero infeasible resamples; aggregate QA PASS; report local SHA256 824f9466894ff7fe6ef7680fe4314cb6b59feb068e43d0db4034608fa60c2428.
- G3.2 evidence is **operator-provided terminal output and local QA claim**, not an independent cloud inspection of original private JSON bytes and historical Pickles. No raw target/price/identifier data should be committed to GitHub.
- Neither the new review notes nor a document-only PR may change any frozen experimental source, threshold, seed, code, or original numerical outcomes.

## Evidence snapshot: favorable and adverse

The original published comparison uses mean 60-calendar-day beta-adjusted forward target (forward_excess_beta), not portfolio P&L. Original P10-q25/K10 vs unfiltered frozen ranking: V2 +0.14429480582475662; V3 +0.14943748898804188; V4 +0.027561593800783157.

A2/A6 exploratory: 18 setting appearances correspond to 15 unique policy-cohort combinations; the q25/K10 policy is duplicated across A2 and A6, NOT independent replication. All 18 news-cluster nominal 95% mean-effect CIs exclude zero; ticker-cluster CIs exclude zero for only three appearances (two unique V3 settings). Original q25/K10 ticker mean-effect CIs include zero in V2 and V4. Do not claim general or multiplicity-adjusted superiority.

A3 conventional 60-prior-return trailing-volatility comparator, original frozen ranking, capacity K10, same three-arm eligible cohorts, validation-only calibrated admission cutoff. Its observed incremental forward_excess_beta means vs baseline are V2 +0.23292389139533043; V3 +0.24126996472477913; V4 +0.07162084616720676. **P10-minus-volatility** direct mean differences and nominal 95% cluster CIs from operator terminal:

| Cohort | N / K | P10 − volatility mean | News ID CI95 | Ticker CI95 |
| --- | ---: | ---: | --- | --- |
| V2 | 4449 / 444 | -0.0886290855705738 | [-0.10426419954746961, -0.07793700639158488] | [-0.27664247662760316, -0.006365072214975955] |
| V3 | 2827 / 282 | -0.09183247573673725 | [-0.10928647629916667, -0.07149558279197664] | [-0.26584376133978366, -0.004959207726642496] |
| V4 | 40320 / 4032 | -0.04405925236642361 | [-0.05038500349037349, -0.036389776365831496] | [-0.10585299655795097, -0.004092793386917044] |

All six **nominal** A3 direct-contrast intervals exclude zero. They are UNADJUSTED and POST-OUTCOME EXPLORATORY; clustering by ticker/news does not remove shared 60-day calendar overlap, dependent cohort periods, unspecified familywise multiple-comparison error or non-verified vendor price acquisition/adjustment vintage. Price cache was archived on 2026-07-05 after original decision dates; the benchmark is not an authenticated ex-ante risk deployment. The stronger conventional comparator is a central **adverse finding** that must appear prominently, not be hidden.

## Formal claims classification for G4

- **SUPPORTED DESCRIPTIVELY:** adding the originally fixed P10 constraint improved the historical forward_excess_beta *point* means vs unfiltered frozen ranking in V2/V3/V4; conditional nominal news-ID CIs are positive.
- **SUPPORTED WITH MAJOR LIMITS:** policy comparison and sensitivity are reproducible under operator-attested SHA-bound historical inputs; different constraints change observed policy outcomes. Some ticker CIs include zero; original price vintage is not point-in-time verified.
- **CONTRADICTED IN A3 HISTORICAL EXPLORATION:** P10 is empirically superior to a conventional volatility veto, on the tested metric/cohorts; reverse sign is observed.
- **NOT DEMONSTRATED:** causal lift from a human-in-the-loop intervention, autonomous vs governed equivalence or noninferiority, independently matured nonoverlapping 60d holdout, generalization across independent ranking models, positive absolute economic returns/net tradable P&L, transaction-cost/turnover improvements, causal benefit of user oversight or 'human accountability' measured experimentally.

## Adversarial work checks (G4.1–G4.5)

**G4.1 Statistical dependency:** identify observational unit; ticker/news clustering are alternative resampling schemes, not independent cohorts; test interpretation of overlapping outcome horizons, unadjusted percentile CIs, multiplicity. Absence of significance cannot establish equivalence. No ex-post noninferiority margin allowed.

**G4.2 Temporal integrity and source lineage:** interrogate original classifier/booster source authenticity vs reconstructed boosters; original news feature vintage; pre-event price date vs archived vendor vintage and adjustments; raw-file/cardinality documentary mismatch noted in G1.3b. Distinguish source preflight 'PASS' from valid production-time trading availability.

**G4.3 Comparator fairness:** same original ranker and original K; calibrated thresholds set on validation only; risk admission rates are not pair-count matched in old cohorts even though matched by news-weighted validation rate; no capacity/backfill tricks or retrospective retuning.

**G4.4 Economic and causality:** original target is excess-beta, not self-financing profit; cash/flat requires a common economic estimand; no realized costs or holdings ledger; every fixed guardrail was authored by people, including the nominal 'AI-only' baseline objective; design portability is not an independent second-ranker test.

**G4.5 Novelty and editorial:** compare HDPG to existing selective prediction/abstention, risk constraints, risk coverage, human-AI decision governance, and auditable ML systems; require precise **specific** contribution beyond 'a human chose a filter'. Verify relation to legitimate authority and the narrower experimental intervention without an unmeasured bridge claim. Ensure exactly four journal-prescribed main body sections in G5.

## Gate logic and no-go conditions

G4 is NOT complete until:
1. A reproducible claim-to-source-to-result ledger maps each material manuscript claim to exact evidence and permissible wording, with negative/null observations disclosed.
2. Every one of 15 reviewer observations and 7 editor items has a response route (EVIDENCE / LIMITATION / RETRACTION_OR_REWORDING / ADMINISTRATIVE), and 22/22 entries have an accountable action and downstream section/file.
3. Adversarial inference check distinguishes nominal uncertainty from multiple-comparison/calendar dependence, documented in English in manuscript-safe language.
4. Novelty assessment states the best skeptical explanation ('this is conventional deterministic filtering') and explains exactly which parts of an auditable governance interface are new versus common practice. If not supportable, narrow scope.
5. Verification status of private local reports and original manuscript is explicitly disclosed; original full JSON is not in GitHub. No claim of independently verifying their bytes.
6. Editor-specific requirements for G7 and remaining external-source authenticity work are recorded; no submission/acceptance reported.

**NEXT:** G4.1 claim/evidence matrix and G4.2 editorial/scientific pivot design, followed by independent challenge and only then G4 closure signoff. This document is a documented ENTRY, not acceptance.
