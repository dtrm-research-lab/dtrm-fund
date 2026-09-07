# DTRM research engineering

Read the user's current scientific stage, `docs/phase4/agentic-graph-engineering.md`,
and `research/reports/DTRM_PHASE4_PROGRESS.md` before changing Phase IV.

## Scientific boundary

- Phase III/MM1 is scientifically frozen. Preserve every inherited tracked file
  at `a853d5d3f2d6c93a3483a0126ab3475b02960bfc`; Phase-IV work is additive.
- Keep the original Phase-IV v0.1 contract intact. Register explicit addenda
  for new bindings rather than silently rewriting an earlier contract.
- Follow contract → ontology → leakage firewall → representation baseline →
  Transformer → evaluation, with the relevant gates closed before advancing.
- Engineering checks do not authorize model fitting, outcomes, retuning,
  scientific promotion, or an assertion of real-data readiness.
- Never use consumed V2–V6 evidence as new confirmation. Never revise a policy
  or research question in response to protected outcomes.

## Graph and delivery discipline

- Define typed, immutable state and each node's inputs, outputs, invariants,
  failure behavior, and permitted side effects before implementation.
- Keep domain nodes deterministic and I/O at explicit boundaries.
- Use one bounded `feature/phase4-*` branch and a PR into
  `research/phase4-temporal-state`. Preserve Phase III's branch and `main`.
- Record contracts, code, tests, source identities, and validation evidence in
  the repository. Use the PR's current-head checks as remote CI evidence.
- Required gates: scoped lint and strict typing, deterministic tests, inherited
  regression tests, source preservation, reproducible synthetic evidence,
  package build, and human review before integration.
- User acceptance of a bounded stage does not imply acceptance of later
  experiments or release. Ask for the human review only after a concrete PR
  and its validation are available.

## Current checks

Install research dependencies and `research/configs/phase4_quality_requirements.txt`
in an isolated environment. Set `PYTHONPATH=src`, `MYPYPATH=src`, and
`PYTHONDONTWRITEBYTECODE=1`. See `.github/workflows/phase4.yml` for exact commands.
Run `research/experiments/validate_phase4_source_preservation.py` before and after
validation. Build from a disposable source archive so packaging does not rewrite
the inherited tracked distribution metadata. Do not broaden legacy lint or
rewrite Phase-III code to satisfy a new Phase-IV style gate.
