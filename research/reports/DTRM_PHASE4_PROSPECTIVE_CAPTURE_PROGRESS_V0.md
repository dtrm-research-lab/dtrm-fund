# Phase IV prospective capture protocol v0 — progress

Date: 2026-09-10.

## Outcome

The retrospective evidence established that the existing collection cannot
authenticate when the machine observed each content version or ticker link.
This increment starts the confirmatory alternative by specifying and testing a
prospective capture protocol. It does not deploy that protocol.

The protocol records a conservative run-level observation clock, content and
payload digests, deterministic logical/version identity, complete immutable
revision chains, mapping-versioned ticker links, reconciled run counters and a
canonical append-only hash chain. Its audit output is aggregate/identity-only.

## Registered ancestry

- integration parent: `6314de2e53f01409918e01e519f5acfa98b7c09f`;
- protocol registration: `85c02cca5a477b6c68b43dbac35d517e58f66518`;
- protocol SHA-256:
  `a343f076a9713b5e1b037cf83ecc864d9bc4308a9592bef0dabeafa00617e629`;
- synthetic prior-state binding:
  `d058b02fcf2e28c4987954876433b6efa695ab06`;
- binding SHA-256:
  `0ec92acb50d3011063db595e6bc026b99bd9847f8d6e4dcc080ab5266ea65e31`;
- implementation and locally validated remote candidate:
  `3dda1a39946fd2d073a99d846f610f9d671774f9`;
- validated tree: `54dc4b275897c69e098bb0f4518014fb7fba3abf`.

The separate synthetic binding fixes prior version state to an empty tuple.
Complete revision chains must therefore begin at their roots inside the
synthetic bundle. A previous ledger hash proves only ledger continuity; it does
not invent prior version state. Production prior-state storage remains a later
contract.

## Implemented graph

The pure graph normalizes the exact envelope, reconciles counters, validates
version identities and complete chains, validates ticker-link provenance,
checks canonical ledger hashes and emits one deterministic review. Typed state
is frozen and detached from input. The CLI has only explicit synthetic input
and new-output paths and emits fixed redacted errors.

The tracked fixture contains three synthetic versions, two logical events and
four links. It exercises a revision, provider-ID identity, exact-URL-digest
fallback, one repeat sighting, one rejected candidate and genesis ledger
construction. The tracked report reproduces byte for byte.

## Validation

- 44 targeted acceptance/failure tests passed;
- full suite: 624 passed, 6 dedicated-Mongo tests skipped normally;
- scoped Ruff passed;
- strict mypy passed for 21 Phase-IV source/entrypoint files;
- ontology, metadata, feasibility, retrospective-salvage and new prospective
  synthetic reports reproduced byte for byte;
- the 12-finding collector-lineage evidence validator passed;
- a disposable source archive built the wheel successfully;
- preservation passed before and after all gates for the 157 inherited files
  and the original Stage-0 contract.

The six skipped tests require the explicit disposable Mongo CI service and do
not concern the new pure protocol. Current-head GitHub checks remain the remote
acceptance evidence.

## Scientific boundary and next operation

Status is `BLOCKED_PROSPECTIVE_DEPLOYMENT`. No production source was accessed,
no collector or workflow was modified, and no history, representation,
outcome, training or MM1 operation occurred. A synthetic hash chain does not
authenticate coverage, runtime clock, deployed code, exclusive write authority
or durable retention.

After CI and human review, the next bounded contract may bind the exact
production collector repository and parent, storage namespace, UTC clock,
overlap schedule, request fingerprint, append-only write, durable prior-version
index, retention and workflow/run evidence. Only future accepted observations
can enter that prospective interval; this work cannot backdate the existing
collection.
