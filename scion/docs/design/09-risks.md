# 9. Risk register

Likelihood (L) and impact (I) are rated 1–5. The score is L × I. Owners are roles.

| ID | Risk | L | I | Score | Mitigation | Trigger / early warning | Owner |
|---|---|---|---|---|---|---|---|
| R-01 | Landing starvation under high contention | 3 | 5 | 15 | group commit per server; jittered backoff; deadline; swarm simulation in CI | land retries/s and time-to-land rising (superfan) | Landing owner |
| R-02 | Single-host storage (SQLite) becomes the bottleneck | 4 | 4 | 16 | narrow `MetaStore` interface; keep access patterns single-row; plan a Spanner adapter | write latency p99; SQLITE_BUSY errors | Architect |
| R-03 | Deferred blame backfill is slow on deep histories | 3 | 3 | 9 | eager-backfill command; per-path blame option later | first-blame latency | Core owner |
| R-04 | Merge semantics differ from git, confusing users | 3 | 3 | 9 | diff3 semantics; structured conflicts; documented first-parent rules (BR-06) | conflict reports from users | Core owner |
| R-05 | Comment-only classifier misses a logic change | 2 | 5 | 10 | conservative classifier (unknown means logic; strings tracked); tests per language; owners for sensitive directories | post-merge failures on "comment-only" CRs | Review owner |
| R-06 | Cache outage overloads the servers | 2 | 5 | 10 | strict tiering; single flight; failover; rate limits | server object RPC rate spikes | Operator |
| R-07 | Policy change leaves previously public objects cached | 3 | 4 | 12 | re-index plus cache restart procedure (UC-22); alert on policy change without re-index | policy hash differs from the hash at last re-index | Security |
| R-08 | Plaintext transport in the prototype | 5 | 4 | 20 | TLS/mTLS before any production use (NFR-20); prototype runs on localhost | any non-local deployment | Security |
| R-09 | Ingestion diverges from git | 2 | 5 | 10 | byte-for-byte verify; ordering invariant; incremental and idempotent runs | verify mismatches | Migration owner |
| R-10 | Very large files hurt every tier | 3 | 3 | 9 | per-file size limit; chunking later | object size histogram | Operator |
| R-11 | No kernel virtual filesystem means tools must use the client to materialize | 4 | 2 | 8 | `scn materialize` / `read()`; a FUSE adapter is future work | developer feedback | Client owner |
| R-12 | Admin force-land bypasses review | 2 | 4 | 8 | admin-only; audit log (FR-IAM-10) | force-land count > 0 | Security |
| R-13 | Post-merge testing lets main be red briefly | 4 | 3 | 12 | auto-revert; deploy gate; fast workers | main red duration | Release manager |
| R-14 | Requirements drift because code came first | 4 | 3 | 12 | this package as the baseline; traceability matrix; change control (12) | untraced code changes | Project lead |
| R-15 | Rate limits are per process, not global | 3 | 2 | 6 | per-principal limits sized per server; a shared limiter later | rejections imbalanced across servers | Operator |
| R-16 | The fsmonitor misses events | 2 | 3 | 6 | sync cookie; overflow means rescan; fallback to a full scan | status disagrees with a full scan in tests | Client owner |
