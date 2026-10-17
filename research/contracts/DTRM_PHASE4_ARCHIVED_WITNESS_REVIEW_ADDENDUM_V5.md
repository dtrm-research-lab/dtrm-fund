# Phase IV ZIP LZMA resilience addendum v5

2026-10-15. Registered BEFORE code modification in PR #42 exact-head `110e9b42dd3788cad301b0609d9b073772be2e8c` to address Codex P2 on `ZipFile.read` of adversarial `ZIP_LZMA` members. Python's zipfile can raise `lzma.LZMAError`, which is not covered by existing `zlib.error`/ValueError handlers, yielding an unredacted provider decompression exception instead of fixed `ArchivedWitnessError`.

Add `lzma.LZMAError` to both inner `_sealed_read` and outer `_read_archive` exception normalization, without ever exposing raw archive/provider content, stack, link IDs/tickers, filenames or secrets. Tests: synthetic LZMA compressed sealed archive round-trip, corrupt LZMA member with matching outer ZIP SHA and fixed error, injected `lzma.LZMAError` and valid deflate regression. Neither scientific authority nor source-first-seen, model/training, outcomes, AWS activation or MM1 changes. Run 4/4 CI and fresh Codex review.
