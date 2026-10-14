# Phase IV matched-tickers shape audit — review addendum v1

**2026-10-14 | REGISTERED_BEFORE_FIX | no live-source execution or scientific promotion.**

Review of PR #40 head `5ad96f5cdc6ab685106c0884c35e8ad2b7fa8003` identified two P2 defects at the terminal report-publication boundary. This preregistration modifies only the dormant operator CLI, not its pinned Mongo query, type-only schema, counts, credentials, scientific status or any frozen Phase-III/MM1 file.

1. **Post-publication staging cleanup must be best-effort.** After the exclusive hard link has succeeded and the complete aggregate-only report is present at the final destination, a transient `os.unlink(temp)` failure must **not** downgrade the audit status to failure; publication is authoritative. Before publish, temp unlink errors remain failures. Do not delete or replace the final report. Expose no raw filesystem path or exception text. An orphan staging path after successful publication is a local cleanup concern, not an invalid published artifact.
2. **Status emission must be best-effort** on both accepted success and failure paths. After a report has been published, a stdout `BrokenPipeError`, `OSError`, or closed-stream `ValueError` must not cause the CLI to report that the audit failed, nor surface raw tracebacks. The exclusive complete report is the authoritative evidence. Console status success is advisory only.
3. **Fault-injection tests** must confirm that forced temp cleanup failure after publish returns success with unchanged final bytes and suppressed output failure; forced stdout error after publish yields success; failure before publish does not leave a final report, and existing no-clobber/symlink/never-connect-on-preflight tests still pass.
4. Do not change the original fixed aggregate-only BSON type query or its scientific flags. Live Mongo operator execution still requires separate approval after CI/human review; no AWS, protected source values, prices, market outcomes, history construction, training or MM1 execution permitted.

Acceptance: contract-before-code ancestry, exact-head 4/4 workflows, safety tests, Codex review threads answered and resolved, no merge without the separate integration authorization.
