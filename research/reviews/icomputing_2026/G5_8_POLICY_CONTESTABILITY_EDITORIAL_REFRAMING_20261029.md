# G5.8 — Scientific narrative alignment: contestable AI action policies (editorial-only)

**2026-10-29**, case ICOMPUTING-D-26-01069, **WORKING REVISION — NOT EMPIRICAL EXPERIMENT**.
**Original title maintained:** *Human-Defined Probabilistic Guardrails for Trustworthy AI Decision-Making in Financial Markets*.

## Human Clause public motivation, explicitly NOT the peer-reviewed result

> Beat The Machine does not necessarily mean making better decisions than the machine; it means refusing to give up the right to question them, even when they appear mathematically optimal.

This belongs in Human Clause public/book discourse, not as a tested quantitative outcome. In the manuscript the academic claim is narrower: optimizing a prediction score does not itself demonstrate that its downstream action policy is optimal for a real decision criterion; **human authorship does not establish policy optimality either**. Already known in decision-focused optimization, selective prediction, decision sciences and risk governance. **No first-invention or universal human-superiority claim**.

## Exact supported contribution and competing controls

- Original frozen XGBoost ranker and fixed K; V0 quantile re-ranking unsuccessful; V1 absolute positive-P10 veto infeasible (zero admissions).
- Original V2/V3/V4 P10 differences in saved transformed Y_model compared with unfiltered original ranker: **+0.1442948**, **+0.1494375**, **+0.0275616**.
- Post-outcome **conventional trailing-volatility veto** on the same ranker/capacity yielded **+0.2329239**, **+0.2412700**, **+0.0716208**: an adverse alternative-policy comparator. It is NOT an information-matched negative control: it introduces different risk information and uses historical vendor prices of unverified acquisition/adjustment vintage.
- Original ticker-cluster nominal 95% CIs cross zero in V2 and V4; 60d windows overlap and exploratory threshold/capacity comparisons have no multiplicity correction.
- Saved June V2/V3/V4 `target_model` archives have **unproven producer and preprocessing-vintage compatibility** with the source-reconstructed 75,828-row TRAIN / 171 ticker mapping. Within-cohort fixed-target contrasts remain descriptive; not raw returns, tradable P&L or decomposed ticker-centering effects.
- No prospective unconsulted 60d holdout; no second genuinely frozen ranker; no causal human-authority arm; no originally executed same-risk-information hard-vs-soft benchmark.

**Novelty claim:** source-traceable **case-specific, capacity-matched adversarial evaluation of action-policy packages**, with negative results preserved; *not* invention of selective prediction, human oversight, dynamic governance, decision-focused optimization or uniquely superior P10.

## Placement in the research paper (G5.5 author-held)

1. Abstract: start with prediction-objective vs action-policy distinction; retain exact V2–V4 and adverse comparator, uncertainty and source-vintage caveats.
2. Introduction: scientific question and symmetric machine/human optimum caveat.
3. Contribution: describe a bounded case study and what cannot be isolated (risk information vs hard enforcement).
4. Results: move adverse volatility comparison from 'awkward limitation' to core **falsifiable alternative-policy challenge**. Correctly call it *retrospective benchmark*, NOT formal randomized negative control or new holdout.
5. Discussion/Conclusion: optimization of predictive score doesn't validate action utility; an investigator’s original preferred human-designed gate also needs scrutiny. Distinguish governance motivation from observed authority interventions.
6. Figures/Table S1/Table 4 unchanged numerically; no invented new statistics.

## Reviewer traceability (G6.5 author-held)

- **R1-04:** substantive conventional volatility benchmark preserved despite exceeding P10; uncertainty, source-vintage and posterior exploration explicitly stated.
- **R1-06:** human-specified rules ≠ measured human judgment, no human-v-machine causal comparison; baseline also human designed.
- **R2-01:** policy choice is contestable; refute unique P10 advantage; narrow novelty against known selective prediction and ordinary risk filtering.
- **R2-08:** prior art acknowledged, source-compatible/equal-information experiment absent, do not infer a new governance theorem.
- All other reviewer requests remain mapped, including R1-01/R1-07/R1-05/R2-05 genuinely unfulfilled.

## Concrete private author-held working artifacts (not committed to public GitHub)

- `IC_G5_5_POLICY_CONTESTABILITY_REFRAMED_WORKING_20261029.docx`, SHA256 `4fed7d122d8fc894825d909b6d4e9f40fef7a2d2e56db749ab1121a17ca529bc`, 21 rendered pages, 4 retained images, 8 tables, 210-word Abstract. Original main body 4 sections, with revision paragraphs highlighted as **working editorial markup**, not XML tracked changes.
- `IC_G6_5_POLICY_CONTESTABILITY_RESPONSES_WORKING_20261029.docx`, SHA256 `5f10b06cc69ed8325195e401d24f5bd049354035245b7b5098c29020c788b077`, 5 rendered pages. Keeps all 22 project review headings; highlights updated response paragraphs. Source provenance details retained under reviewer replies, no duplicate appendix page.
- `IC_EDITOR_REVISION_FRAMING_NOTE_WORKING_20261029.docx`, SHA256 `8a046ea16c3425b669c9004a57a620be72da4c8cebf2a78b9284126f94fcd6aa`, single rendered page. Revision cover note NOT a new submission, needs author final signoff.

**Editorial requirements** from official Intelligent Computing author instructions checked 29 Oct 2026: Research Article must offer major advance and <=250 word abstract; four specified main body sections, single-column numbered lines, review response with exact editorial numbering, independent editable figure files, signed forms as relevant. AI-assisted research/writing must be disclosed in cover and acknowledgments; research methods should include detailed prompt/tool/version disclosures as required. **The current Word working files are NOT yet reconciled to the certified actual Editorial Manager submitted baseline or verbatim referee comments.** Final release needs exact line references, old portal manuscript identity check, data/figures/rights and portal submission by the stated 2026-11-25 deadline.

## Scientific scoring discipline

Prior G4.12 scientific readiness ~63.53/100; before G5.8 provisional improved working reply ~67/100. **G5.8 is an editorial framing improvement only**, no new evidence and **NO new score uplift**, no promise of journal acceptance. Keep the original adverse results instead of reversing hypotheses after outcome consultation. Future new G5.8 experiments require separately frozen source/protocol and owner permission for original financial data; none authorized by this document.
