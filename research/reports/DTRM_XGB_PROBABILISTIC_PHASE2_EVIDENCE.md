# DTRM XGBoost Probabilistic — Phase 2 Evidence

## Research question

Does calibrated probabilistic downside information add
decision value to a frozen deterministic ex-ante ranking?

## Frozen decision mechanism

Baseline ranking:
- frozen ex-ante XGBoost point prediction
- selected ranking iteration: 10

Probabilistic guardrail:
- calibrated P10
- P10 best iteration: 18
- calibration offset: -0.06494169682264328
- relative veto threshold: -0.16665692627429962

Decision rule:
- preserve baseline ranking
- reject candidates with calibrated P10 below the frozen threshold
- walk down the original ranking until Top-K = 10% is filled

No threshold retuning or model retraining was allowed on V2-V4.

## Experimental sequence

### V0 — probabilistic replacement

Status: NOT PROMOTED

Quantile models were successfully calibrated, but replacing the
deterministic ranking directly with probabilistic scores did not
improve Top-K decision quality.

Interpretation:
probabilistic information was useful as uncertainty information,
but not as a direct replacement ranking.

### V1 — absolute downside veto

Rule:
calibrated P10 > 0

Status: NOT PROMOTED — feasibility failure

Holdout rows: 40320
Required Top-K: 4032
Passing rows: 0

Outcomes were not inspected.

Interpretation:
an absolute downside requirement was too restrictive out of sample.

### V2 — relative downside veto

Status: PROMOTED

Holdout rows: 4449
Top-K rows: 444

Baseline Top-K mean:
-0.1949552297592163

Candidate Top-K mean:
-0.050660423934459686

Delta Top-K mean:
+0.14429480582475662

Baseline hit rate:
0.04504504504504504

Candidate hit rate:
0.6238738738738738

Delta hit rate:
+0.5788288288288288

### V3 — prospective replication

Status: PROMOTED

Holdout rows: 2827
Top-K rows: 282

Baseline Top-K mean:
-0.1790371835231781

Candidate Top-K mean:
-0.029599694535136223

Delta Top-K mean:
+0.14943748898804188

Baseline hit rate:
0.06028368794326241

Candidate hit rate:
0.6453900709219859

Delta hit rate:
+0.5851063829787234

### V4 — long-window robustness test

Status: PROMOTED

Holdout rows: 40320
Top-K rows: 4032

Baseline Top-K mean:
-0.05458883196115494

Candidate Top-K mean:
-0.02702723816037178

Delta Top-K mean:
+0.027561593800783157

Baseline hit rate:
0.3864087301587302

Candidate hit rate:
0.4880952380952381

Delta hit rate:
+0.10168650793650791

## Evidence summary

The same frozen relative calibrated-P10 veto improved
Top-K decision quality in V2, V3, and V4.

The effect replicated without:
- model retraining
- threshold retuning
- changes to ranking
- changes to Top-K fraction
- changes to fill policy

The magnitude varied across temporal regimes, but the sign of
incremental decision value remained positive in all three tests.

## Claim boundary

Supported claim:

Calibrated probabilistic downside information provides reproducible
incremental decision value when used as a guardrail around a frozen
deterministic ranking.

Not supported:

The experiments do not establish absolute profitability.
Candidate Top-K mean remained negative in V2, V3, and V4.

The scientific contribution is therefore decision improvement under
uncertainty, not a claim of profitable trading performance.

## Phase 2 status

EVIDENCE COMPLETE — READY FOR STATISTICAL ROBUSTNESS ANALYSIS
AND PAPER PREPARATION.
