# G5.7b — Correcting source-lineage false positive: producer versus consumer

Date 2026-10-29; ICOMPUTING-D-26-01069. **PRE-EXECUTION PROTOCOL, OLD OUTCOMES NOT AUTHORIZED.**

## Owner G5.7a primary evidence
G5.7a source-only scan success as operator-reported:
- SHA256 `4c1dc4bb7309e89020c58600fd58166958d74926173e4807bd1235b99c152c19`.
- 38 original .py source files scanned, 12 generic/static candidates, one exact filename reference each for V2, V3, and V4.
- No .pkl/.ipynb/outcome accessed. Source-to-target compatibility explicitly NOT established.

## Adversarial false-positive identified in original frozen Git source
`research/experiments/run_phase2_primary_bootstrap.py` contains ALL THREE exact filenames and calls `pd.read_pickle` to load existing V2/V3/V4 saved model targets. It also calls `np.savez_compressed` to persist derived bootstrap results. The original G5.7a scanner naively classified any file with both an exact input filename string and *any* writer-like call (including `savez_compressed`) as a producer candidate. The latter writes a different output, NOT the original *.pkl inputs.

This is a **known detector false-positive mechanism**. Merely finding a writer-like function anywhere in a file is not producer lineage. The original V2/V3/V4 exact filename references may all be explained by this preexisting consumer; the owner report must identify their exact relative candidate paths before saying that definitively.

## New strict source-only classification, independently source-hash bound
- Read exactly the operator G5.7a JSON bytes, SHA-matched to `4c1dc4bb7309e89020c58600fd58166958d74926173e4807bd1235b99c152c19` (no substitution).
- Verify original G5.7a schema, `PYTHON_FILES_CHECKED=38`, 12 candidates, V2/V3/V4 exact count each 1, zero old outcome reads and no compatibility proof.
- Resolve candidate relative Python source paths only under **exactly** the two operator-supplied roots, with path traversal, symlink and SHA mismatch rejected. Read only original `.py` source bytes, never `.ipynb`, `.pkl`, CSV, target, model, price or financial data.
- AST disambiguation, per exact target filename: evidence of actual archive producer only for a recognized **write call that contains that exact target filename as an argument** (e.g. `frame.to_pickle("EXACT.pkl")`, `pd.to_pickle(frame,"EXACT.pkl")`, `Path("EXACT.pkl").write_bytes(...)`). Under more complex variable-based paths, mark `DYNAMIC_OR_UNRESOLVED`—never pretend negative proof. Calls `pd.read_pickle`, `np.savez_compressed`, `np.save` without exact *.pkl target output do not count as producer proof.
- Report filename-relative and SHA-only evidence; source text, API secrets and raw financial values never serialized.
- Output must be **either** `G57B_DIRECT_EXACT_ARCHIVE_WRITE_CANDIDATE_PROVENANCE_OPEN` (static write candidate only) **or** `G57B_NO_DIRECT_EXACT_ARCHIVE_WRITER_PROVEN_IN_BOUNDED_PY_SCOPE`. Neither status proves same TRAIN clipping/centering or actual producer execution.
- Strict safety/privacy: no source snapshots committed, no target data, no new old cohort access authorization; keep original G5.7a report SHA and bug in public science ledger.
- Relevant original G5.6 TRAIN 75828 rows/171 tickers and owner G5.7 readback remain valid **source training results**; this source lineage issue is about later June target archive generation only.

**Decision criterion:** G5.7 attribution Δ(Y_model)=Δ(clipped Y)−Δ(TRAIN ticker mean) remains **NO-GO** without dated authentic evidence that the June archive labels were produced using exactly those original TRAIN clipping bounds and centers (or exact independent source-compatible reconstruction with original per-event beta); these files must not be decoded based on static source matching alone. Do not increase IC rebuttal score for finding a consumer.
