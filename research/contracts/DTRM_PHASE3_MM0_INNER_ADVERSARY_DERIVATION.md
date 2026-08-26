# DTRM Phase 3 — MM0 Exact Inner Adversary Derivation

**Status:** frozen mathematical derivation / structural non-triviality failure

**Scope:** derive the exact inner adversary for the already-frozen MM0 action set and budgeted downside uncertainty family. This document does **not** change Binding A, B, C, D, the frozen Phase-2 champion, the MM0 uncertainty family, or the frozen value of `rho_MM0`.

## 1. Frozen objects

For one frozen cohort `H`, let:

- `K = K_H` be the frozen Top-K cardinality;
- `C = a_H^(2)` be the frozen Phase-2 champion selection;
- `S = S_H(a)` be any admissible MM0 challenger selection;
- `b_i = baseline_point_score_i`;
- `l_i = min(b_i, calibrated_p10_i)`;
- `d_i = b_i - l_i >= 0`;
- `rho = rho_MM0 = 0.4378501384944031`;
- `B = rho K` be the total adversarial stress budget.

The MM0 scenario value is

\[
y_i(z)=b_i-z_i d_i,
\]

with

\[
0\le z_i\le1,
\qquad
\sum_i z_i\le B.
\]

Champion and challenger are evaluated in the same scenario vector `z`.

## 2. Incremental value under one scenario

Because `|S|=|C|=K`, the incremental value is

\[
\Delta V_H(S,z)
=
\frac1K\sum_{i\in S}(b_i-z_i d_i)
-
\frac1K\sum_{i\in C}(b_i-z_i d_i).
\]

Define the nominal difference

\[
\Delta_0(S)
=
\frac1K\left(\sum_{i\in S}b_i-\sum_{i\in C}b_i\right).
\]

Then

\[
\Delta V_H(S,z)
=
\Delta_0(S)
-
\frac1K
\sum_i z_i d_i
\left(\mathbf 1_{i\in S}-\mathbf 1_{i\in C}\right).
\]

Rows in `S cap C` cancel exactly. Rows outside `S union C` also have zero coefficient.

Let

\[
P=S\setminus C,
\qquad
N=C\setminus S.
\]

Then

\[
\Delta V_H(S,z)
=
\Delta_0(S)
-
\frac1K\sum_{i\in P} z_i d_i
+
\frac1K\sum_{i\in N} z_i d_i.
\]

## 3. Exact inner adversary

The adversary minimizes `Delta V`. Therefore:

- stressing a row in `P = S minus C` decreases challenger-relative value;
- stressing a row in `N = C minus S` increases challenger-relative value;
- stressing a common row has no relative effect.

Because the budget is an inequality (`sum z_i <= B`) rather than an equality, an optimal adversary never spends budget on `N`, common rows, or zero-coefficient rows.

The exact inner problem reduces to

\[
\max_{z}
\sum_{i\in P} z_i d_i
\]

subject to

\[
0\le z_i\le1,
\qquad
\sum_{i\in P}z_i\le B.
\]

This is a continuous fractional-knapsack problem.

Sort the downside widths of challenger-only rows in non-increasing order:

\[
d_{(1)}\ge d_{(2)}\ge\cdots\ge d_{(q)},
\qquad q=|P|.
\]

Let

\[
g=\lfloor B\rfloor,
\qquad
r=B-g.
\]

The optimal adversarial penalty is

\[
\Psi_B(P)
=
\sum_{j=1}^{\min(g,q)}d_{(j)}
+
\begin{cases}
 r\,d_{(g+1)}, & g<q,\\
 0, & g\ge q.
\end{cases}
\]

where the second term is omitted when `r = 0`.

Equivalently, the adversary fully stresses the largest downside wedges among `S minus C`, fractionally stresses at most one additional challenger-only row, and leaves all other rows unstressed. Ties in `d_i` can produce multiple optimal stress vectors, but the worst-case value is unique.

Therefore the exact robust margin is

\[
\boxed{
\Gamma_H(S)
=
\Delta_0(S)
-
\frac{1}{K}\Psi_B(S\setminus C)
}
\]

for the frozen MM0 family.

No scenario enumeration, Monte Carlo procedure, or numerical optimizer is required for the inner problem.

## 4. Structural dominance theorem for frozen MM0

### Theorem

Under frozen Binding B and the frozen MM0 uncertainty family,

\[
\Gamma_H(S)\le0
\]

for every admissible challenger `S`.

The frozen Phase-2 champion satisfies

\[
\Gamma_H(C)=0.
\]

Hence

\[
\boxed{
\max_{S\in\mathcal A_2(Z_H)}\Gamma_H(S)=0
}
\]

and a strictly positive MM0 robust-improvement intervention is impossible.

### Proof

Binding B defines `C` as the first `K` Phase-2-eligible rows in descending frozen baseline score. Every non-neutral MM0 action can only veto some eligible rows and continue farther down that same frozen baseline ranking until `K` rows are again filled.

Therefore any challenger `S` replaces one or more rows of `C` with rows that occur no earlier in the same descending baseline order. Consequently,

\[
\sum_{i\in S}b_i\le\sum_{i\in C}b_i,
\]

so

\[
\Delta_0(S)\le0.
\]

Independently, the MM0 uncertainty set explicitly contains the nominal scenario `z=0`. Therefore

\[
\Gamma_H(S)
=
\min_z\Delta V_H(S,z)
\le
\Delta V_H(S,0)
=
\Delta_0(S)
\le0.
\]

The exact inner derivation strengthens this result because

\[
\Psi_B(S\setminus C)\ge0,
\]

hence

\[
\Gamma_H(S)
=
\Delta_0(S)-\Psi_B(S\setminus C)/K
\le\Delta_0(S)\le0.
\]

For the champion itself, `S=C`, the challenger-only set is empty, the nominal difference is zero, and champion and challenger values are identical under every common scenario. Thus

\[
\Gamma_H(C)=0.
\]

QED.

## 5. Interpretation

The MM0 action space is combinatorially non-empty when more than `K` rows pass the Phase-2 guardrail, but it is **decision-theoretically dominated** under the frozen value and uncertainty definitions.

The source of the degeneracy is the conjunction of three previously frozen choices:

1. Phase 2 already selects the highest `b_i` rows among the eligible pool;
2. MM0 is allowed only to add vetoes and may not reorder/select differently within that pool;
3. the uncertainty set contains the nominal world `z=0`, where scenario values equal `b_i`.

Therefore an additional-veto challenger starts weakly below the champion in the nominal world, and the adversary can only make challenger-only replacements worse relative to the champion.

This is a structural result. It must not be repaired by reducing `rho`, removing unfavorable scenarios after inspection, or tuning on a Phase-3 holdout.

## 6. Scientific consequence

The frozen MM0 specification is retained as a valid negative theoretical result: **an additional adversarial veto layered on a ranking that is already optimal for the nominal score cannot establish positive baseline-relative MaxMin improvement when the nominal score vector itself belongs to the uncertainty set.**

No Phase-3 holdout outcome needs to be inspected to establish this result.

The next experiment, if pursued, requires a separately preregistered change to at least one structural degree of freedom. The cleanest candidate is to retain the Phase-2 eligible pool, frozen signals, fixed `K`, and champion fallback, while allowing the robust decision layer to choose a different full-`K` subset within that already-approved pool. Such a specification would be a new MM1 action contract, not a retrospective modification of MM0.

## Gate 3.8 — exact inner adversary

**Status: PASS for derivation / FAIL for MM0 non-trivial robust intervention.**

Permitted next work:

- preserve MM0 as a negative theoretical result;
- preregister a distinct MM1 action-space hypothesis if Phase 3 continues;
- derive MM1 before any Phase-3 holdout inspection.

Not permitted:

- implement an MM0 outer optimizer and present its inevitable fallback as an empirical discovery;
- lower `rho` to force intervention;
- remove `z=0` after observing this theorem;
- alter Phase-2 ranking or eligibility silently;
- inspect Phase-3 holdout outcomes to choose the redesign.
