# 11. Traceability and gap analysis

This matrix traces every requirement to use cases (05), features (04), design elements (06/07)
and tests (10). At M0 the prototype was deleted (decision 2) and every requirement was rebuilt in
milestones **B1–B5** (12 §12.3). The Status column shows the planned milestone until the requirement is
built and its acceptance tests pass, then **I**. Every requirement of B1–B5 reads **I**; the requirements added after
B5 (12 §12.9) read **B6** until milestone B6 builds them.

## 11.1 Functional requirements

| Req | Use cases | Feature | Design | Tests | Status | Note |
|---|---|---|---|---|---|---|
| FR-CS-01 | UC-04, UC-07 | F-01 | repo.create_changeset; client.commit | T-CL-01, T-IAM-07 | I |  |
| FR-CS-02 | UC-04 | F-01 | changeset.Changeset | T-CORE-03, T-FUZZ-01 | I |  |
| FR-CS-03 | UC-04 | F-02 | objects, storage | T-CORE-03 | I |  |
| FR-CS-04 | UC-04 | F-01 | Changeset.id; meta.insert_changeset | T-CORE-04 | I |  |
| FR-CS-05 | UC-04 | F-01 | meta.insert_changeset | T-CORE-05, T-SIM-01 | I |  |
| FR-CS-06 | UC-04 | F-01 | shared MetaStore | T-DD-01 (two repositories on one store) | I |  |
| FR-CS-07 | all queries | F-05 | repo.resolve | T-CORE-06 | I |  |
| FR-CS-08 | UC-04, UC-07 | F-01 | repo.create_changeset; trees.apply_augmented | T-CORE-07 | I |  |
| FR-CS-09 | UC-04 | F-03 | trees.apply_augmented; incremental derived types | T-CORE-08, T-CORE-10 | I |  |
| FR-REF-01 | UC-13, UC-15 | F-04 | meta.refs; antique.create | T-CORE-05, T-LD-01 | I |  |
| FR-REF-02 | UC-15, UC-28 | F-04 | meta.cas_ref | T-CORE-05, T-SIM-01 | I |  |
| FR-REF-03 | UC-28 | F-25 | Policy.protected_refs; can_update_ref | T-IAM-06, T-LD-01 | I |  |
| FR-REF-04 | UC-28 | F-04 | meta.ref_log | T-CORE-05 | I |  |
| FR-REF-05 | UC-28 | F-25 | create_release RPC; release/* protection | T-REF-01 | I |  |
| FR-OBJ-01 | all (5.3) | F-02 | objects | T-CORE-01 | I |  |
| FR-OBJ-02 | all (5.3) | F-02 | storage.FileObjectStore | T-CORE-01 | I |  |
| FR-OBJ-03 | all (5.3) | F-02 | bounded stores; no gc | T-CORE-02 | I |  |
| FR-OBJ-04 | UC-01 | F-02 | decode_stored(expected_id) in daemon and client | T-CORE-01, T-TIER-08 | I |  |
| FR-OBJ-05 | all (5.3) | F-02 | derived trees only | T-CORE-08 | I |  |
| FR-ST-01 | UC-32 | F-46 | MetaStore interface; SqliteMetaStore; SpannerMetaStore (keys by repository, 06 §6.10) | T-ST-01 | B6 |  |
| FR-ST-02 | UC-32 | F-46 | `metadata` section of deployment.json; open_metastore | T-ST-02 | B6 |  |
| FR-ST-03 | UC-15, UC-18, UC-32 | F-46 | SpannerClient.run_in_transaction: retry on ABORTED with backoff | T-ST-03 | B6 |  |
| FR-ST-04 | UC-30, UC-32 | F-46 | backup: Spanner read-only transaction at one timestamp, written as a SQLite meta.db | T-ST-04 | B6 |  |
| FR-DD-01 | UC-27 | F-06 | derived.DerivedDataManager | T-DD-01 | I |  |
| FR-DD-02 | UC-09, UC-27 | F-06 | DerivedDataManager._derive_missing | T-DD-01 | I |  |
| FR-DD-03 | UC-09, UC-27 | F-06 | DerivedType.eager | T-DD-01, T-DD-07 | I |  |
| FR-DD-04 | UC-27 | F-06 | register | T-DD-02 | I |  |
| FR-DD-05 | UC-09 | F-06 | derived_put (insert or ignore) | T-DD-01 | I |  |
| FR-DD-06 | UC-27 | F-06 | backfill; `scion-admin derive` | T-DD-07 | I |  |
| FR-DD-07 | UC-01 | F-06 | RootTreeType | T-CORE-07, T-FUZZ-01 | I |  |
| FR-DD-08 | UC-08 | F-08 | HistoryTreeType; repo.file_history | T-DD-04, T-DD-08, T-FUZZ-01 | I |  |
| FR-DD-09 | UC-09 | F-08 | BlameType | T-DD-05, T-DD-08, T-FUZZ-01, T-MG-02 | I |  |
| FR-DD-10 | UC-11 | F-07 | GraphType; is_ancestor; merge_bases | T-DD-06, T-FUZZ-01 | I |  |
| FR-DD-11 | UC-08 | F-08 | CopyInfoType | T-DD-03 | I |  |
| FR-DD-12 | UC-12 | F-39 | SearchTreeType | T-CORE-12, T-FUZZ-01 | I |  |
| FR-QRY-01 | all | F-09 | server.get_changeset(s) | T-CORE-03 | I |  |
| FR-QRY-02 | UC-20 | F-09 | repo.log | T-DD-04 | I |  |
| FR-QRY-03 | UC-05, UC-10 | F-09 | repo.diff; trees.diff | T-CORE-09, T-FUZZ-01 | I |  |
| FR-QRY-04 | UC-10 | F-09 | server._diff(merge_base) | T-CL-10 | I |  |
| FR-QRY-05 | UC-11 | F-07 | merge_bases; is_ancestor | T-DD-06, T-FUZZ-01 | I |  |
| FR-QRY-06 | UC-08 | F-08 | file_history | T-DD-03, T-DD-04, T-FUZZ-01 | I |  |
| FR-QRY-07 | UC-09 | F-08 | blame | T-DD-05, T-DD-08, T-FUZZ-01 | I |  |
| FR-QRY-08 | UC-02 | F-09 | read_file; list_dir | T-CORE-11 | I |  |
| FR-QRY-09 | UC-11, UC-20 | F-07 | fp_ancestor | T-DD-06, T-FUZZ-01 | I |  |
| FR-QRY-10 | all | F-09 | ScionService registry; the client calls only registered RPCs | T-CL-11 | I |  |
| FR-WR-01 | UC-07 | F-11 | create_changeset with content_b64 or uploaded blobs | T-CL-10, T-CL-11 | I |  |
| FR-WR-02 | UC-06, UC-29 | F-10 | repo.merge; merge3 | T-WR-01 | I |  |
| FR-WR-03 | UC-06 | F-10 | repo.rebase | T-WR-01, T-CL-04 | I |  |
| FR-WR-04 | UC-21 | F-10 | repo.revert | T-WR-01, T-PM-01 | I |  |
| FR-WR-05 | UC-07 | F-11 | create_changeset update_ref (compare-and-swap) | T-CL-10 | I |  |
| FR-WR-06 | UC-04 | F-11 | has_objects; WorkingCopy.upload | T-CL-01 | I |  |
| FR-WR-07 | UC-04, UC-07 | F-11 | Policy.max_file_bytes; decode_limited; 413 | T-LIM-01 | I |  |
| FR-FP-01 | UC-01 | F-12 | get_objects {repo, ids}: no "have" field | T-TIER-02 | I |  |
| FR-FP-02 | UC-01 | F-12 | ObjectFetcher.trees by level; WorkingCopy._collect_files | T-CL-06 | I |  |
| FR-FP-03 | UC-01 | F-12 | per-object frames; pending target in state.db; clone resumes in place | T-CL-13 | I |  |
| FR-FP-04 | UC-01, UC-02 | F-12 | sparse and virtual modes use only get_objects | T-CL-06, T-CL-07 | I |  |
| FR-FP-05 | UC-01 | F-12 | one get_objects contract on ObjectTierService and ScionService | T-TIER-02 | I |  |
| FR-FP-06 | UC-01 | F-12 | CachingSource stores and serves stored bytes unchanged | T-TIER-02 | I |  |
| FR-FP-07 | UC-01 | F-12 | MAX_IDS_PER_REQUEST; ObjectFetcher.fetch_batches in parallel | T-TIER-01, T-CL-13 | I |  |
| FR-TIER-01 | UC-01 | F-13 | DaemonService on a Unix socket; BoundedFileObjectStore | T-TIER-01 | I |  |
| FR-TIER-02 | UC-01 | F-13 | BoundedFileObjectStore (LRU) | T-CORE-02, T-CL-08 | I |  |
| FR-TIER-03 | UC-24 | F-14 | DaemonService.refresh_snapshots; load_snapshot | T-TIER-05 | I |  |
| FR-TIER-04 | UC-25 | F-13 | RemoteSource checks each upstream's tier_info; servers refuse daemons | T-TIER-03 | I |  |
| FR-TIER-05 | UC-01 | F-15 | make_cache_service: MemoryObjectStore | T-TIER-01 | I |  |
| FR-TIER-06 | UC-01 | F-15 | RemoteSource to the servers: one request per batch | T-TIER-01 | I |  |
| FR-TIER-07 | UC-25 | F-16 | Method.tiers; TIER_PRINCIPALS; mutual TLS | T-TIER-03, T-TLS-01 | I |  |
| FR-TIER-08 | UC-25 | F-15 | tiers hold only caches over a shared deployment root | T-TIER-06 | I |  |
| FR-TIER-09 | UC-25 | F-15 | RemoteSource and FailoverClient | T-TIER-06 | I |  |
| FR-TIER-10 | UC-01 | F-15 | CachingSource single flight | T-TIER-07 | I |  |
| FR-TIER-11 | UC-24 | F-14 | create_snapshot; atomic LATEST; scion-admin snapshot | T-TIER-05 | I |  |
| FR-CL-01 | UC-01 | F-17 | WorkingCopy.clone: full, sparse, virtual | T-CL-06, T-CL-07, T-TIER-01 | I |  |
| FR-CL-02 | UC-01 | F-18 | BoundedFileObjectStore in .scn/objects | T-CL-08 | I |  |
| FR-CL-03 | UC-01 | F-19 | read_disk; WorkingCopy._write_file | T-CL-02 | I |  |
| FR-CL-04 | UC-03 | F-20 | fsmonitor: inotify journal, sync cookie, fallback scan | T-CL-09 | I |  |
| FR-CL-05 | UC-03 | F-19 | status, add, remove, restore, diff_local | T-CL-01, T-CL-05 | I |  |
| FR-CL-06 | UC-04 | F-19 | commit: create_changeset, nothing to push | T-CL-01 | I |  |
| FR-CL-07 | UC-05 | F-19 | update: server diff, local changes protected | T-CL-03 | I |  |
| FR-CL-08 | UC-06 | F-19 | rebase on the server, then update | T-CL-04 | I |  |
| FR-CL-09 | UC-01 | F-17 | sparse_add, sparse_remove; add widens the profile | T-CL-06, T-CL-12 | I |  |
| FR-CL-10 | UC-02 | F-17 | materialize; read | T-CL-07 | I |  |
| FR-CL-11 | all | F-21 | cli.scn_main | T-CL-11 | I |  |
| FR-CL-12 | UC-01 | F-13 | one object endpoint in the config (the node daemon) | T-TIER-01, T-CL-11 | I |  |
| FR-IAM-01 | UC-22 | F-22 | Policy.can_read_repo / can_write_repo; per-repository policy.json | T-IAM-09, T-MR-01 | I |  |
| FR-IAM-02 | UC-22 | F-44 | Deployment; repo-scoped RPCs; caches keyed by (repo, id) (ADR-13) | T-MR-01 | I |  |
| FR-IAM-03 | UC-22 | F-22 | Policy path rules (most specific wins; read and write inherit separately) | T-IAM-01, T-IAM-05 | I |  |
| FR-IAM-04 | UC-01, UC-08…12 | F-23 | Policy.can_read on every read RPC; object index (object_acl); filtered CR views; snapshots | T-IAM-03, T-IAM-01, T-IAM-11, T-IAM-12 | I |  |
| FR-IAM-05 | UC-01 | F-23 | restricted flag from the object index; CachingSource never stores it; ACL epochs purge what became restricted (ADR-20) | T-IAM-04, T-IAM-14 | I |  |
| FR-IAM-06 | UC-22 | F-22 | Identity groups, admins, services; Deployment.maybe_reload per request | T-IAM-13, T-IAM-07 | I |  |
| FR-IAM-07 | UC-22 | F-24 | Identity.check_token; Service.authenticate (401); client certificates for tiers | T-IAM-08, T-TLS-01 | I |  |
| FR-IAM-08 | UC-01 | F-24 | X-Scion-On-Behalf-Of; Caller.user | T-MR-01, T-IAM-04 | I |  |
| FR-IAM-09 | UC-22 | F-26 | Repository.reindex_acl; reindex_acl RPC; scion-admin reindex-acl; a new ACL epoch | T-IAM-10, T-IAM-14 | I |  |
| FR-IAM-10 | UC-22 | F-26 | audit.AuditLog (hash chain): policy loads, denials, ref moves, admin actions | T-AUD-01, T-ADM-01 | I |  |
| FR-IAM-11 | UC-22 | F-23 | "" entries in the object index; possession grants for uploaders | T-IAM-02, T-IAM-11 | I |  |
| FR-RV-01 | UC-13 | F-27 | antique.create from a changeset id | T-LD-01 | I |  |
| FR-RV-02 | UC-14 | F-27 | cr_revisions; approvals per revision | T-RV-05 | I |  |
| FR-RV-03 | UC-14 | F-27 | cr_comments (revision, path, line) | T-RV-09, T-RV-07 | I |  |
| FR-RV-04 | UC-14 | F-27 | requirements() drops the author's approval | T-RV-03 | I |  |
| FR-RV-05 | UC-14 | F-28 | classify.classify_file | T-RV-01 | I |  |
| FR-RV-06 | UC-14 | F-28 | review rules per directory and category; owners | T-RV-04, T-RV-02 | I |  |
| FR-RV-07 | UC-14 | F-28 | Antique.requirements in the API, CLI and pages | T-RV-02, T-RV-06, T-CL-14 | I |  |
| FR-RV-08 | UC-14 | F-29 | ui.ReviewUI pages with requirements, comments and the diff | T-RV-06 | I |  |
| FR-RV-09 | UC-14 | F-29 | ui.ReviewUI forms (session cookie, CSRF) | T-RV-07 | I |  |
| FR-RV-10 | UC-13 | F-32 | notify.Notifier webhooks on CR events | T-RV-08 | I |  |
| FR-LD-01 | UC-15 | F-30 | Antique.land: server-side rebase, one CAS | T-LD-01, T-LD-03 | I |  |
| FR-LD-02 | UC-15 | F-30 | no lock: per-server group commit, CAS only | T-SIM-01 | I |  |
| FR-LD-03 | UC-15 | F-30 | group commit; jittered backoff; deadline (503 retry) | T-SIM-01, T-LD-04 | I |  |
| FR-LD-04 | UC-16 | F-30 | MergeConflict -> 409 and CR state conflict | T-LD-02 | I |  |
| FR-LD-05 | UC-17 | F-31 | landings index (landed and source ids) | T-LD-01, T-SIM-01 | I |  |
| FR-LD-06 | UC-21 | F-38 | antique.land_changeset (services and admins) | T-LD-05 | I |  |
| FR-LD-07 | UC-15 | F-35 | postmerge queue row per landing | T-LD-01, T-PM-03 | I |  |
| FR-PM-01 | UC-18 | F-35 | Antique.postmerge_claim: conditional UPDATE, retried until the queue is empty (D-01); a lease re-queues the jobs of lost workers, and a claim token refuses their late reports | T-PM-02, T-PM-04 | I |  |
| FR-PM-02 | UC-18 | F-35 | PostMergeWorker._checkout: one working copy moved by `update` | T-PM-01 | I |  |
| FR-PM-03 | UC-18 | F-35 | Antique.postmerge_report (status, log, claim) | T-PM-01 | I |  |
| FR-PM-04 | UC-18 | F-35 | PostMergeWorker: tools.revert.revert_landing when the base passed; postmerge_reverted | T-PM-01 | I |  |
| FR-PM-05 | UC-19 | F-36 | Antique.deploy_gate (first-parent walk; only `passed`) | T-PM-01 | I |  |
| FR-AUT-01 | UC-20 | F-37 | tools.bisect over first-parent ranges, server-side predicates; `scn bisect` | T-AUT-01 | I |  |
| FR-AUT-02 | UC-21 | F-38 | tools.revert (revert, then land_changeset); `scn revert` | T-AUT-02 | I |  |
| FR-SR-01 | UC-12 | F-39 | search.search_paths over the bloom-filtered search tree | T-SR-01 | I |  |
| FR-SR-02 | UC-12 | F-39 | search.grep on the server; `grep` RPC; `scn grep` | T-SR-01 | I |  |
| FR-SR-03 | UC-12 | F-45 | ContentIndexType (deferred trigram postings) + blob_index (ADR-16) | T-SR-02 | I |  |
| FR-SR-04 | UC-12 | F-39 | per-path filtering of every search result | T-SR-01, T-IAM-03 | I |  |
| FR-MG-01 | UC-23 | F-33 | GitIngester.ingest (graph and first parents preserved) | T-MG-01, T-MG-02 | I |  |
| FR-MG-02 | UC-23 | F-33 | GitIngester.check_boundary (refuses before writing) | T-MG-03 | I |  |
| FR-MG-03 | UC-23 | F-33 | git_map skip of ingested commits | T-MG-01 | I |  |
| FR-MG-04 | UC-23 | F-33 | one `cat-file --batch` stream; tree diffs skip identical subtrees; byte-bounded caches | T-MG-04 | I |  |
| FR-MG-05 | UC-23 | F-33 | GitIngester.verify; `scion-admin ingest --verify` | T-MG-01, T-ADM-02 | I |  |
| FR-MG-06 | UC-23 | F-34 | server API over ingested history; `git_lookup` RPC | T-MG-05, T-E2E-01 | I |  |
| FR-MG-07 | UC-23 | F-33 | git_map in both directions; changeset extra["git"] | T-MG-01 | I |  |
| FR-OP-01 | UC-26 | F-40 | /healthz and /stats on every tier | T-OPS-05 | I |  |
| FR-OP-02 | UC-26 | F-40 | Metrics (p50/p90/p99, errors by status); CachingSource.stats (hit rate) | T-OPS-05, T-TIER-01 | I |  |
| FR-OP-03 | UC-26 | F-41 | superfan.Superfan: EWMA baselines and novel findings; daemon, cache and landing-queue profiles; `scion-superfan` | T-OPS-02 | I |  |
| FR-OP-04 | UC-26 | F-41 | superfan.Rule threshold rules (`for N`, severity) | T-OPS-02 | I |  |
| FR-OP-05 | UC-26 | F-41 | Superfan webhook through notify.Notifier.send (`text` payload) | T-OPS-03 | I |  |
| FR-OP-08 | UC-26 | F-41 | rpc.LogRing per component, GET /logs (ADR-18); findings attach the lines of the last two intervals | T-OPS-04 | I |  |
| FR-OP-09 | UC-31 | F-47 | superfan_agent.Investigator: Messages API over HTTPS, read-only tools (stats, logs, baselines, findings) | T-OPS-06 | B6 |  |
| FR-OP-10 | UC-31 | F-47 | Investigator limits (turns, tokens, concurrency), dedup by finding key, redaction, fallback post | T-OPS-07 | B6 |  |
| FR-OP-11 | UC-33 | F-48 | tools.bench --vs-git: git upload-pack and the Scion tiers measured on one host (ADR-26) | T-PERF-02 | B6 |  |
| FR-OP-06 | UC-25 | F-42 | RateLimiter; 429 with Retry-After; RpcClient backs off | T-OPS-01 | I |  |
| FR-OP-07 | UC-25 | F-43 | tools.bench; `scion-admin bench` | T-PERF-01 | I |  |
| FR-AD-01 | UC-23 | F-43 | `scion-admin init`, `create-repo` | T-ADM-02, T-E2E-01 | I |  |
| FR-AD-02 | UC-24 | F-43 | `scion-admin snapshot` | T-TIER-05, T-ADM-02 | I |  |
| FR-AD-03 | UC-27 | F-43 | `scion-admin derive` | T-DD-07, T-ADM-02 | I |  |
| FR-AD-04 | UC-22 | F-43 | `scion-admin reindex-acl` | T-IAM-10, T-ADM-02 | I |  |
| FR-AD-05 | UC-28 | F-43 | scion-admin set-ref --as (protections apply; audited) | T-ADM-01 | I |  |
| FR-AD-06 | UC-30 | F-43 | backup.backup (SQLite online backup, then objects), restore, verify; `scion-admin backup/restore/verify` | T-BAK-01, T-E2E-01 | I |  |

## 11.2 Non-functional requirements

| Req | Status | Evidence / note |
|---|---|---|
| NFR-01 | I | T-SIM-01: 32 agents × 5 rounds on 2 servers landed 160 changes at 21.7 landings/s, 6 times the design rate of 3.5/s, with 32 ref moves; the B5 stress run of 64 × 10 sustained 20.9 landings/s over 640 landings (61 ref moves, largest batch 27). No starvation: median time to land 0.33 s at 32 × 5 and 0.89 s at 64 × 10, longest 23 s with 64 landers in one process, inside the asserted 60 s (the landing deadline is 300 s). The rate includes each agent's clone, commit, review and update, so it understates landing capacity |
| NFR-02 | I | T-SYS-01: a node serving 100 jobs, 200 checkouts in all, hits 99.5%; a cache behind 100 nodes hits 99.0% over its whole life, cold start included. T-TIER-01, T-PERF-01 and T-E2E-01: a second clone on a node sends the cache nothing but requests for restricted objects, which are never cached (ADR-06) |
| NFR-03 | I | T-SYS-03: read, list, history, blame and diff of one path read the same 27 objects at 500 and at 10,000 files; a sparse checkout of 1 of 40 projects fetches 103 of 4,081 objects. T-CORE-08: commits rewrite only the changed path; T-MG-04: ingestion memory stays flat; T-CL-07: virtual checkouts fetch on read. The 100 GB and 25 GB sizes were not run on one host; no measured cost grows with the repository's total size |
| NFR-04 | I | T-PERF-01 asserts a sparse checkout from a warm daemon in under 10 s; the full benchmark checks out a 250-file project of a 5,000-file repository in 0.14–0.22 s |
| NFR-05 | I | T-CORE-10: a one-file commit writes the same 3 trees and 10 objects at 10² and 10⁴ files and, with objects in memory, takes the same time within ±25% (asserted); T-PERF-01: the final benchmark measured ×1.12 in memory and ×1.24 on disk from 10² to 10⁴ files (×1.52 before ADR-21; on this shared machine's disk, runs vary from ×1.1 to ×1.6) |
| NFR-06 | I | T-DD-06: ancestry over 100 changesets in < 20 steps; T-PERF-01: on a 10,000-commit line, is_ancestor takes 9 steps, fp_ancestor 8 hops and merge_base 19 steps, against 10,000 for a naive walk; history is one lookup per result |
| NFR-07 | I | T-TIER-06: two servers serve one deployment root; caches and daemons hold only caches, so adding or restarting one needs no data migration |
| NFR-08 | I | T-TIER-03 strict tiering; T-TIER-07 single flight; T-OPS-01 rate limits |
| NFR-09 | I | T-TIER-06: with one of two servers and one of two caches down, a clone succeeds with no client change |
| NFR-10 | I | T-IAM-01…04, T-IAM-11/12/14: no response, object fetch, snapshot or shared store gives restricted bytes to an unauthorized user (the leak sweep in T-IAM-03 checks every read RPC) |
| NFR-11 | I | T-TIER-08: the daemon and the client reject a forged object; every object they receive is checked against its id |
| NFR-12 | I | T-CORE-05: concurrent CAS, exactly one winner, unbroken ref log; T-DD-01: deterministic derived values across two servers |
| NFR-13 | I | T-SYS-02: losing the node daemon with its disk store, the regional cache and a server loses nothing: replacements serve identical checkouts, and a new server process on the same storage serves everything. T-BAK-01 and T-E2E-01: an online backup under load restores with the refs and changesets of the snapshot and verifies |
| NFR-14 | I | no maintenance commands exist; T-DD-02: a new derived type in one class |
| NFR-15 | I | T-FUZZ-01 checks random histories against a naive model (8 seeds in the suite, 40 in the B5 run); T-SIM-01 runs the agent swarm (32 × 5; 64 × 10 in the B5 run); every integration suite runs servers, caches and daemons over real sockets in the hermetic Cluster; T-E2E-01 runs every component in its own process |
| NFR-16 | I | T-OPS-05: health, stats, latency percentiles, error counts and hit rates on every tier |
| NFR-17 | I | T-SYS-01: every store stays within its configured size (a cache at 8 MB, daemons at 4 MB; a 20 KB daemon evicts); T-E2E-01: server, cache and daemon each 26–28 MB resident after the whole demo; servers hold no copies of their own (T-SYS-02) |
| NFR-18 | I | T-ERR-01: errors carry a stable code, an HTTP status and structured data (409 conflicts list path and reason); the CLI prints them |
| NFR-19 | I | T-STD-01: no third-party imports (the openssl tool is used only to make development certificates) |
| NFR-20 | I | T-TLS-01: TLS on every TCP hop; mutual TLS between tiers; plaintext and wrong certificates refused |

## 11.3 Coverage summary

Updated at the end of every milestone (computed by the T-DOC-02 cross-check).

| Milestone | Scope | Status |
|---|---|---|
| B1 | version control core | **done**: 45 requirements built and tested (21 core tests; fuzzing 8 seeds × 70 steps in the suite, 200 × 120 in a stress run) |
| B2 | service, tiers, client, multi-repository, TLS | **done**: 48 requirements built and tested (41 FR, 7 NFR; 39 new tests across tiers, client, CLI, multi-repository, TLS, IAM and operations) |
| B3 | IAM, audit, review and landing | **done**: 30 requirements built and tested (28 FR, 2 NFR); the 32 × 5 swarm landed all 160 changes on 2 servers with 31 ref moves |
| B4 | migration, automation, search, operations, backup | **done**: 28 requirements built and tested (31 new tests: 30 in five new suites for ingestion, automation, search, superfans and the admin toolkit, 1 in IAM; the IAM leak sweep now covers grep); the 32 × 5 swarm landed all 160 changes on 2 servers with 31 ref moves; the end-to-end demo (T-E2E-01) passes with every component in its own process |
| B5 | system verification of the non-functional requirements | **done**: the 7 remaining NFRs verified with measurements (T-SYS-01…03 added; the swarm now asserts the landing rate and time to land); every requirement is **I**; the doc checks are committed as `scripts/check_docs.py` and pass with `--release` |
| B6 | as Anthropic runs it: Spanner metadata, superfan agents, comparison with git, the CPython pilot (M4), adversarial review | **planned**: 7 requirements (FR-ST-01…04, FR-OP-09…11) |

## 11.4 Findings carried into the rebuild

| ID | Finding (from the review of the deleted prototype) | Resolution in the rebuild design |
|---|---|---|
| D-01 | `postmerge_claim` gave up after 10 contended attempts | claim retries until the queue is empty (T-PM-02) |
| D-02 | the CR stayed `open` while its landing was queued | CRs show `landing` while queued (T-LD-03) |
| D-03 | the admin tool moved refs without the protected-ref policy | admin ref operations run as an explicit identity (FR-AD-05, T-ADM-01) |
| D-04 | line comments were not shown inline | inline comments in the interactive review UI (FR-RV-09, T-RV-07) |
