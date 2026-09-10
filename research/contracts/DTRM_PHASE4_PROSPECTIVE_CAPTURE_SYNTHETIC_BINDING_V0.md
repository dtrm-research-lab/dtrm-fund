# Phase IV prospective capture synthetic binding v0

Date: 2026-09-10. Status: REGISTERED_BEFORE_IMPLEMENTATION.
Parent protocol registration: `85c02cca5a477b6c68b43dbac35d517e58f66518`.
Parent protocol SHA-256:
`a343f076a9713b5e1b037cf83ecc864d9bc4308a9592bef0dabeafa00617e629`.

## Purpose

This binding resolves the prior-state input of the pure synthetic conformance
graph without changing the registered prospective protocol. The protocol says
that revision chains are complete within supplied prior state plus the bundle;
the v0 bundle intentionally does not contain a prior-version-state field.

For this synthetic implementation, the supplied prior version state is fixed
to the empty tuple. Every logical event represented by a new-version record
must therefore include its complete chain from the root inside the same bundle.
A record cannot cite a `supersedes_version_id` that is absent from that bundle.

`previous_ledger_head_sha256` authenticates only ledger continuity. It is not a
substitute for prior version state and cannot authorize an external predecessor,
first-seen value, content digest or ticker-link history. A non-genesis bundle
may contain zero new records, in which case its output head equals its input
head. A non-genesis bundle with new records may exercise hash-chain continuity,
but every included logical revision chain still begins at its root in this
synthetic cut.

The future production deployment contract must bind the exact durable prior
version index, its digest, lookup semantics, atomicity and failure behavior
before incremental revisions may be accepted. That contract may extend the
input schema under a new version; it may not reinterpret this synthetic pass as
evidence that deployed prior state exists.

## Fixed implementation identities

- graph: `phase4_prospective_capture_protocol_v0`;
- report schema: `dtrm.phase4.prospective_capture_review.v0`;
- dataset role: `synthetic` only;
- prior version state: empty tuple;
- CLI: `research/experiments/run_phase4_prospective_capture_review.py` with
  required `--input` and `--output` paths;
- successful status:
  `PASS_SYNTHETIC_PROSPECTIVE_CAPTURE_PROTOCOL`;
- scientific status: `BLOCKED_PROSPECTIVE_DEPLOYMENT`.

The implementation embeds the parent protocol registration commit and both
contract SHA-256 identities. It produces aggregate/identity-only evidence and
keeps every scientific permission false. No production collector, database,
network, environment or outcome access is authorized.
