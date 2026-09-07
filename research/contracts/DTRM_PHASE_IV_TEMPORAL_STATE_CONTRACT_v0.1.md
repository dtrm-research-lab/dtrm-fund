# DTRM Phase IV — Temporal State

**Stage 0 · Research contract and preregistration draft · v0.1 · 7 September 2026**

Scientific lead: Urtzi Arana Santamaria · DTRM Research Lab

**Status: DRAFT_FOR_REVIEW.** This document establishes the Phase-IV question, inherited policy boundary, proposed comparisons, and requirements for the subsequent preregistration. It is not a claim that the complete experiment has been registered or frozen. The unresolved specifications in Section 10 must be bound before their corresponding work begins. No Phase-IV data construction, model fitting, or outcome evaluation has been performed in preparing this contract.

## 1. Purpose and governing theses

> The machine searches. The human defines the game.

> The next frontier in AI decision-making may not be better prediction, but better use of what the machine already knows.

The research progression is:

**Point Prediction → Uncertainty → Robust Decision → Temporal State**

Paper III reports positive incremental decision value from frozen MM1 relative to the promoted Phase-II guardrail in V5 and V6, with important dependence limitations. Phase IV takes those results as prior evidence and asks a new question about representation. It does not reopen Phase III or extend its claims retroactively.

The second thesis is a motivating hypothesis. Phase IV can supply bounded evidence for or against it; it cannot establish a universal frontier for AI. Historical observations need not have been retained or encoded in the current model. Here, “already knows” means information demonstrably available to the system by the decision cutoff, whose sequential structure the frozen snapshot may fail to retain.

PRAGMA is architectural inspiration only. Its results are not evidence for DTRM's hypothesis, and its architecture, weights, objectives, or performance are not adopted by this contract.

## 2. Research question and estimand

**Does historical event representation improve a frozen robust decision policy beyond point-in-time information?**

Let X_i,t denote the information used by the frozen snapshot pipeline for candidate i at cutoff t. Let H_i,t be the admissible history available before that cutoff, with the current event handled consistently across arms. Let π_MM1 be the frozen robust decision mapping.

The control supplies the frozen Phase-II state to π_MM1. The treatment supplies a probabilistic state derived from X_i,t and a sequential representation of H_i,t to the same mapping. Including the same current information in both arms avoids confusing the addition of history with the removal of useful snapshot features.

For a common evaluation cohort H and K_H selected rows:

    S_H^C0 = π_MM1(Z_H^C0)
    S_H^T  = π_MM1(Z_H^T)
    Δ_H(T,C0) = mean(Y_model,i for i in S_H^T)
                − mean(Y_model,i for i in S_H^C0)

The primary endpoint is **incremental realized Top-K mean in frozen Phase-II target-model units**, with favorable direction Δ_H(T,C0) > 0. Neither predictive loss nor an increase in a model's own robust objective substitutes for this endpoint.

The statistical unit of the selection benchmark remains the evaluation cohort. Candidate rows are event–ticker observations, not independent investments or simultaneous portfolio positions. The comparison is an offline policy benchmark; it does not identify a causal market effect.

The null includes zero or negative incremental value. Identical selected actions imply exactly zero incremental decision value on a common complete target vector.

## 3. Immutable control and policy inheritance

The inherited implementation is anchored to repository snapshot **a853d5d3f2d6c93a3483a0126ab3475b02960bfc** in `dtrm-research-lab/dtrm-fund`, inspected from `research/phase3-minmax-contract`. This is the inspected source snapshot, not a newly created release tag or a claim that the entire commit was the original scientific freeze.

The following values agree with the retrieved Phase-III contracts and final Paper III:

| Component | Inherited specification |
| --- | --- |
| Control state | `news_id`, `ticker`, `date_dt`, baseline point score, baseline rank, calibrated P10, guardrail-pass flag |
| Control point-model iteration | 10 |
| Control P10-model best iteration | 18 |
| Control P10 calibration offset | −0.06494169682264328 |
| Guardrail threshold τ | −0.16665692627429962 |
| Capacity | K_H = floor(0.10 × n_H), using the full common cohort size |
| Eligible set | Rows whose calibrated P10 ≥ τ |
| Downside width | d_i = max(0, b_i − calibrated_P10_i) |
| Uncertainty budget | ρ = 0.4378501384944031; total stress ≤ ρK_H; each stress coefficient lies in [0,1] |
| Objective | Maximize each exact-K eligible subset's own worst-case arithmetic mean |
| Fallback | Use the arm's guardrail champion unless the maximum robust value exceeds that champion's robust value by more than 1e−12 |
| Tie hierarchy | Maximum champion overlap; maximum nominal mean; lexicographically smallest sorted baseline-rank tuple |
| Solver semantics | Exact frozen objective and hierarchy, including the recorded V6 residual-tie amendment; no approximate-incumbent substitution |
| Realized horizon | 60 calendar days, with the inherited five-day price tolerance |
| Target units | Stock forward return − frozen pre-event beta × SPY forward return, followed by frozen TRAIN clipping and ticker de-meaning |

The control's model weights, preprocessing, feature semantics, calibration, and all of MM1's numerical policy constants remain fixed. The frozen TRAIN clipping bounds and ticker means are reused across every arm; they are not re-estimated on Phase-IV evaluation data. Unseen-ticker target de-meaning uses the inherited zero-mean fallback.

Phase IV introduces a separately versioned upstream state adapter. It does not edit Phase-III contracts, source files, artifacts, results, or negative results. Historical-state prohibitions in the Phase-III experiment remain valid for that experiment.

**Policy identity is a mapping, not a fixed list of selected rows.** Each arm supplies b and calibrated P10 in the same units. Rank and the guardrail flag are derived by the same frozen rules. Each arm therefore has its own eligible set and guardrail champion. A changed eligible set caused by changed input estimates is recorded as a treatment effect. Threshold relaxation, candidate-universe changes, or a different fallback definition are forbidden. Forcing the control's literal eligible mask onto all arms would be a different, narrower experiment and is not silently substituted here.

Only the control reuses the old P10 offset as its calibration constant. New state heads require their own preregistered fitting and calibration procedure on permitted development data, producing the same target units and nominal lower-tail meaning. The old offset must not be blindly added to a different predictor. MM1's τ, ρ, objective, fallback, and tie rules stay fixed.

No embeddings, new quantiles, historical realized outcomes, or learned actions are passed directly into MM1. The temporal representation is compressed into its existing input interface.

## 4. Proposed experimental arms and claim attribution

All arms use the same candidate identities, cutoff rules, current-event access, target construction, K, and frozen MM1 mapping. The snapshot control already includes inherited historical summaries such as pre-event beta; “snapshot” does not mean that it contains no historical information whatsoever.

| Arm | State construction | Role |
| --- | --- | --- |
| C0 — Frozen control | Original Phase-II snapshot predictions and calibration | Authoritative reference for incremental decision value |
| S — Matched snapshot | A newly fitted state model with comparable architecture, heads, training data, and training budget to T, with history access removed | Distinguishes history access from refitting and model capacity |
| B — Simple history baseline | Current information plus a prespecified non-Transformer history summary | Tests whether a simpler representation is sufficient; built before T |
| T — Sequential treatment | Current information plus a Transformer representation of admissible event history, followed by compatible probabilistic heads | Sole primary challenger against C0 |
| O — Order ablation | A matched history model with explicit order and timing information removed under a preregistered transformation | Tests the additional contribution of temporal structure |

The exact recipes and matching tolerances are bound before fitting. B may summarize counts or recency, but its concrete fields and windows belong to the next preregistration stages. O must retain the same permitted event content and history coverage while removing the explicit temporal structure being tested. Merely shuffling rows while retaining recoverable timestamps or positional features is not an adequate order ablation. Remaining time clues in event content must be documented.

The comparisons have distinct meanings:

- **T versus C0:** does the full temporal-state pipeline improve the frozen reference system?
- **T versus S:** is there evidence attributable to access to history, beyond the matched refitted snapshot?
- **B versus C0 and T versus B:** does simple historical representation suffice, and does the Transformer add value over it?
- **T versus O:** is the result sensitive to the explicit temporal structure, rather than just the event collection?

A positive T-versus-C0 result alone supports a pipeline-level claim. A claim about history requires the matched snapshot comparison. A claim about order requires the order ablation. T-versus-B alone does not isolate order. No arm becomes the primary challenger because it happens to win on the holdout.

## 5. Information and leakage boundary

The following are requirements for the ontology and firewall stages, not a declaration that a dataset already meets them.

1. **Availability governs admission.** An event must have been available to the system by the decision cutoff. Event time, publisher time, first availability or ingestion time, revisions, and derived-feature availability must be distinguishable. A publication date alone is not proof that the historical text version was available then.
2. **Preserve vintages.** Later edits, ticker mappings, corporate-action corrections, and backfilled records must not rewrite historical information silently. If availability cannot be established, the affected confirmatory claim is blocked or explicitly limited before fitting.
3. **Define the prediction clock.** Resolve same-day prices, pre-event beta, event timestamps, and execution/target timing together. No feature may rely on information arriving after its declared cutoff. An incompatibility in the inherited control is reported as a Phase-IV feasibility issue; Phase III is not rewritten.
4. **Labels are not event-history features.** Do not feed forward targets, future prices, future-derived labels, or evaluation diagnostics into the representation. Observed historical market measurements can enter only after separate ontology approval and an availability check. No new source family is introduced only for T without matched controls or a separately declared scope.
5. **Fitting respects time.** Tokenizers, vocabulary, normalizers, imputers, encoders, self-supervised pretraining, heads, calibration, and checkpoint selection use only the registered development partitions. Unlabelled holdout histories are not a hidden pretraining set. Replayed historical model scores and genuinely logged historical predictions have different provenance and must be identified.
6. **Split by time and dependence.** Purging and embargo rules must use actual label-availability intervals, the 60-day horizon and tolerance, duplicate events, and shared histories. A random row split is not accepted. Two sequences sharing an already-available past event are not automatically leakage, but that overlap must be represented in the dependence analysis.
7. **Protect common rows.** Define short-history and empty-history behavior, truncation, ticker entry/exit, and missing-data rules before model outputs are inspected. All arms retain the common prespecified cohort. Post-outcome row dropping, changing K, or selecting a favorable coverage subset is forbidden.
8. **Freeze actions before targets.** Model artifacts, allowed histories, predictions, calibration, selected identities, fallback status, source hashes, and the full cohort manifest must be committed to a timestamped record before exact confirmatory targets and comparisons are released to the evaluator.

V2–V6 are already consumed evidence. They cannot become fresh Phase-IV confirmation by changing their names, recomputing a metric, or hiding targets in another file. Any retrospective development use must be declared. A clean Phase-IV confirmatory cohort requires an exposure ledger and a separately registered window; prospective collection is preferred. No exact test dates are asserted in this draft.

## 6. Learning and search discipline

Each representation stage requires a preregistered recipe before its first fit: inputs, context limits, loss, model family, parameter budget, seeds, fitting partition, calibration partition, stopping rule, and any bounded hyperparameter search. S and T must have comparable access to development information.

Ordinary parameter learning on TRAIN and a fixed selection procedure on VALID are allowed only as preregistered. This permission does not authorize discretionary outcome-driven retuning. Downstream MM1 realized gains are not used to revise representations, windows, model families, or policies. Confirmatory targets and diagnostics are never model-selection criteria.

Complete the simple representation baseline before implementing the Transformer. Progression is based on the declared stage requirements, not on a favorable confirmatory return. Both successful and failed attempts remain in the run ledger; no best-seed reporting. No learning through the optimizer or joint policy training is included in this experiment.

After outcome release, a negative or null result closes the registered comparison under its original rules. Any scientifically different hypothesis requires a new registration and new eligible confirmation data. A rerun can verify deterministic reproduction; it cannot replace a result with a revised model.

## 7. Evaluation and evidence rules

**Primary contrast:** T versus C0 on the common complete cohort and frozen target vector. Report the full-K feasibility of every arm before interpreting a gain. A missing target or infeasible selection is not repaired by deleting unfavorable or incomplete rows after outcome access. Use an explicit infeasible status if the registered completeness rule fails.

**Secondary diagnostics:** hit-rate difference, lower-tail calibration and predictive loss, selection overlap, guardrail eligibility, fallback frequency, and representation coverage. These explain behavior; they cannot rescue a failed primary endpoint. Own robust values under different predicted states are not comparable realized rewards and are not used as the promotion statistic.

The statistical addendum must be frozen before any Phase-IV fitting or access to confirmatory outcomes. It must specify the dependence-aware paired procedure, cluster/block construction, interval method and level, seeds, replicate count, infeasible-replicate rule, cohort aggregation, and treatment of multiple confirmatory comparisons. Pair arms within each resample. If policies are recomputed for inference, predictions and fitted models remain frozen and recomputation follows a prespecified outcome-blind rule; the original point-evaluation actions are never replaced.

News clusters alone do not address all repeated-ticker, market-time, overlapping-forward-window, and shared-history dependence. The inference design must address these explicitly. If there is insufficient temporal information for the registered inference, report that limitation rather than switch methods after seeing the result.

| Observed pattern | Permitted interpretation |
| --- | --- |
| T selects the same action as C0 | No incremental action; Δ = 0 |
| Δ(T,C0) ≤ 0 | No positive incremental decision value for the registered primary comparison |
| Δ(T,C0) > 0, with inconclusive registered inference | Positive point result; uncertainty remains |
| Primary contrast and matched-history attribution criteria pass | Evidence for incremental value from historical information under this design |
| Order ablation also passes its registered criterion | Additional evidence for explicit temporal structure |
| B improves C0 but T does not improve B | Simple history may suffice; Transformer superiority is unsupported |
| Predictive metrics improve but decision value does not | Better predictive representation without demonstrated incremental MM1 decision value |

Exact inferential thresholds and any temporal replication gate remain unresolved until the statistical addendum is fixed. This draft does not authorize a confirmatory PASS or a significance claim. Replication dates and the no-retuning rule must be registered before the first confirmatory outcome; one cohort cannot be substituted for another after inspection.

## 8. Incremental work sequence

| Stage | Deliverable and exit condition |
| --- | --- |
| 0 — Contract | Reviewable question, policy inheritance, comparisons, endpoint, and claim boundaries; this draft |
| 1 — Data / event ontology | Field definitions, entities, source/vintage provenance, cutoff clock, history coverage, universe, and exposure ledger, using no confirmatory outcomes |
| 2 — Leakage firewall | Enforced availability and partition rules; synthetic boundary checks; data and statistical addenda frozen before fitting |
| 3 — Representation baseline | Registered B recipe, development-only fitting, comparison setup against C0, compatible state interface, reproducible artifacts; test outcomes remain sealed |
| 4 — Transformer | Registered S/T/O recipes and bounded fitting procedure, frozen checkpoints and calibration; S is fitted here so it matches T; all confirmatory actions recorded before target release |
| 5 — Evaluation | One prespecified report including primary result, attribution comparisons, dependence analyses, all failures, and registered replication |

Each stage freezes its decisions before the next relevant operation. Later addenda may resolve declared fields using permitted provenance and development information; they cannot rewrite the primary question or respond to protected outcomes. Neither ontology implementation nor model development is part of the work completed with this draft.

## 9. Provenance and preservation record

Sources inspected for this contract:

- Final manuscript: `Beat_the_Machine_III_MaxMin_DTRM_SSRN_FINAL.pdf`, September 2026, Sections 3–5, 8–10 and Appendices A–C. Used to recover the completed Phase-III claim boundary and proposed temporal-state direction.
- [MM1 evaluation contract](https://github.com/dtrm-research-lab/dtrm-fund/blob/a853d5d3f2d6c93a3483a0126ab3475b02960bfc/research/contracts/DTRM_PHASE3_MM1_EVALUATION_CONTRACT.yaml). Git blob: `d050cb0657eda1606b51be2156ae4a7a4df3b802`.
- [MM1 action-set binding](https://github.com/dtrm-research-lab/dtrm-fund/blob/a853d5d3f2d6c93a3483a0126ab3475b02960bfc/research/contracts/DTRM_PHASE3_MM1_BINDING_B_ACTION_SET.yaml). Git blob: `6868f2343a0673701e06ff16565797145f043300`.
- [MM1 robust-objective binding](https://github.com/dtrm-research-lab/dtrm-fund/blob/a853d5d3f2d6c93a3483a0126ab3475b02960bfc/research/contracts/DTRM_PHASE3_MM1_BINDING_C_ROBUST_OBJECTIVE.yaml). Git blob: `bbe984fdcb6d78e40f524595c629f4379cc61cd5`.
- [V6 residual-tie amendment](https://github.com/dtrm-research-lab/dtrm-fund/blob/a853d5d3f2d6c93a3483a0126ab3475b02960bfc/research/contracts/DTRM_PHASE3_MM1_V6_RESIDUAL_TIE_SOLVER_AMENDMENT.yaml). Git blob: `f4cd1b77324529c85b6ba3029ed4b1a26db4a1da`.
- [V6 ex-ante provenance](https://github.com/dtrm-research-lab/dtrm-fund/blob/a853d5d3f2d6c93a3483a0126ab3475b02960bfc/research/contracts/DTRM_PHASE3_MM1_V6_EXANTE_PROVENANCE.json). Git blob: `4e5457789c553e32445ed893c826e7e7a8ad0170`.

The source records preserve their historical stage statuses; an early “evaluation pending” or “blocked” field is not used to override the subsequent recorded Phase-III completion. This review checked documentation and source identity. It did not rerun Phase III or verify the bytes of every large local model/data artifact.

## 10. Declared unresolved specifications

These fields are intentionally unresolved, not implementation defaults:

| Item | Must be fixed by |
| --- | --- |
| Exact control model/preprocessing artifact hashes and executable MM1 dependency set | Source-binding addendum before any model or decision run |
| Universe membership rule and timestamp, event sources and keys, vintage evidence, decision clock | Ontology exit |
| TRAIN / VALID / calibration / untouched confirmation dates; previously inspected data ledger; replication windows and stopping date | Firewall/statistical freeze before fitting |
| History lookback, truncation, empty-history handling, common-row eligibility | Firewall freeze before fitting |
| Actual label-availability intervals, purging, embargo, and dependence-aware inference specification | Firewall/statistical freeze before fitting |
| Numerical evidence gates, multiplicity treatment, and claim levels | Statistical freeze before fitting |
| B representation and head/calibration recipe, search limits, seeds, and stopping rules | Before the first B fit |
| S/T/O architecture, order-ablation transformation, matching tolerances, head/calibration recipes, seeds, and stopping rules | Before the first S/T/O fit, with confirmatory outcomes still sealed |
| Timestamped registration location and immutable complete-protocol identifier | Before treating the experiment as fully preregistered |

**Immediate next step:** specify the data/event ontology against the inherited control's information clock and verified available history. No Transformer implementation is needed for that step.

## Revision log

| Version | Date | Change | Phase-IV outcome access |
| --- | --- | --- | --- |
| 0.1 | 2026-09-07 | Initial Stage-0 contract, grounded in final Paper III and pinned Phase-III source contracts | None in this task |
