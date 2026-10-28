# G4.9c2 — Adversarial transparent-baseline check (2026-10-28)

**Status: exploratory post-original-run external replay; NOT original G4.9c preregistration.**

A separate local Python implementation reconstructed the public G4.9c generator, ridge learner and heldout evaluation. Its baseline synthetic utility means **exactly matched all three GitHub CI values to 8 decimal places** at seed 20261029: learned 83.45532793, balanced 80.81257747, hindsight ceiling 84.19572118.

It introduced an **ex-ante transparent competitor** selecting the allowable policy whose public highest-ranked candidate maximizes `predicted score - w*risk` (abstention utility 0). The underlying synthetic data generate realized quality from the public score plus mean-zero Gaussian noise, so the transparent rule uses no hidden evaluation outcomes.

Original 60 heldout cases:
- Transparent 83.28853647 vs learned 83.45532793 (transparent-minus-learned -0.16679147); policy selections differ on 2/60 cases.
- For EVAL_0013, learned cautious synthetic utility 79.006876 vs transparent balanced 59.053019.
- For EVAL_0020, learned cautious 56.831625 vs transparent balanced 66.777994.
- Neither difference proves a general model benefit.

**Post-outcome additional robustness (NOT confirmatory):** 32 deterministic synthetic generator seeds 20261030..20261061, each freshly train 300 and evaluate 60 heldout synthetic cases. Transparent-minus-learned mean across seeds **+0.05694396**, standard deviation 0.25694727; 9 seeds favor transparent, 6 favor learned, 17 ties in mean utility; average policy choices differed **0.8125 / 60 per seed**. Across seeds mean synthetic utility: transparent 80.53310211, learned 80.47615815, fixed balanced 77.34472373, hindsight ceiling 81.24337264. Per-seed difference range -0.46751962..+1.16270032. These are descriptive seeded simulator comparisons and **not prospective policy generalization**.

**Scientific meaning:** learned-vs-fixed advantage in the original world is real within synthetic conditions, but almost entirely replicated by a simple transparent policy. No robust incremental learned-model advantage over this transparent baseline has been established. Since the generative oracle is deliberately `score + zero-mean noise - w*risk`, the rule's high performance is partly structurally built into the simulation. The test does NOT indicate humans are better, that authority has no cost, or that an LLM competitor was assessed.

**Human subjects N=0. Genuine LLM agent N=0. Governance noninferiority NOT TESTED. G4 novelty gate OPEN.**

Reproduction provenance: local independent source `/mnt/data/g49c_independent_review/g49c_adversarial_replay.py` and aggregate JSON `G49C_ADVERSARIAL_INDEPENDENT_REPLAY_20261028.json`. This reimplementation is source-level reconstructed, not bitwise source commit reproducibility, and original GitHub G4.9c code was not modified. Any journal inclusion should cite the original frozen G4.9c protocol and explicitly label this after-the-fact challenger as exploratory.
