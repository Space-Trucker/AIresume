# 11. Traceability and gap analysis

This matrix traces every requirement to use cases (05), features (04), design elements (06/07)
and tests (10). At M0 the prototype was deleted (decision 2) and every requirement is being rebuilt
in milestones **B1–B5** (12 §12.3). The Status column shows the planned milestone, and becomes **I** once the
requirement is built and its acceptance tests pass.

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
| FR-REF-03 | UC-28 | F-25 | iam.can_update_ref | T-IAM-06 | B3 | |
| FR-REF-04 | UC-28 | F-04 | meta.ref_log | T-CORE-05 | I |  |
| FR-REF-05 | UC-28 | F-25 | create_release RPC; release/* protection | T-REF-01 | B3 | |
| FR-OBJ-01 | all (5.3) | F-02 | objects | T-CORE-01 | I |  |
| FR-OBJ-02 | all (5.3) | F-02 | storage.FileObjectStore | T-CORE-01 | I |  |
| FR-OBJ-03 | all (5.3) | F-02 | bounded stores; no gc | T-CORE-02 | I |  |
| FR-OBJ-04 | UC-01 | F-02 | decode_stored(expected_id) in daemon and client | T-CORE-01, T-TIER-08 | I |  |
| FR-OBJ-05 | all (5.3) | F-02 | derived trees only | T-CORE-08 | I |  |
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
| FR-QRY-10 | all | F-09 | client uses only public RPCs | T-CL-11 | B2 | |
| FR-WR-01 | UC-07 | F-11 | create_changeset (content_b64) | T-CL-10 | B2 | |
| FR-WR-02 | UC-06, UC-29 | F-10 | repo.merge; merge3 | T-WR-01 | I |  |
| FR-WR-03 | UC-06 | F-10 | repo.rebase | T-WR-01, T-CL-04 | I |  |
| FR-WR-04 | UC-21 | F-10 | repo.revert | T-WR-01, T-PM-01 | I |  |
| FR-WR-05 | UC-07 | F-11 | create_changeset update_ref | T-CL-10 | B2 | |
| FR-WR-06 | UC-04 | F-11 | has_objects | T-CL-01 | B2 | |
| FR-WR-07 | UC-04, UC-07 | F-11 | policy limits.max_file_bytes; 413 | T-LIM-01 | B2 | |
| FR-FP-01 | UC-01 | F-12 | get_objects (ids only) | T-TIER-01 | B2 | |
| FR-FP-02 | UC-01 | F-12 | WorkingCopy._collect_files | T-CL-06 | B2 | |
| FR-FP-03 | UC-01 | F-12 | clone progress marker; resume in place | T-CL-13 | B2 | |
| FR-FP-04 | UC-01, UC-02 | F-12 | same RPC for every mode | T-CL-06/07 | B2 | |
| FR-FP-05 | UC-01 | F-12 | shared get_objects handler | T-TIER-02 | B2 | |
| FR-FP-06 | UC-01 | F-12 | stored bytes passed through | T-TIER-02 | B2 | |
| FR-FP-07 | UC-01 | F-12 | FETCH_BATCH; FETCH_PARALLEL | T-TIER-01 | B2 | |
| FR-TIER-01 | UC-01 | F-13 | DaemonService (Unix socket) | T-TIER-01 | B2 | |
| FR-TIER-02 | UC-01 | F-13 | BoundedFileObjectStore | T-CORE-02 | B2 | |
| FR-TIER-03 | UC-24 | F-14 | snapshot; refresh_snapshot | T-TIER-05 | B2 | |
| FR-TIER-04 | UC-25 | F-13 | tier principals; allowed callers | T-TIER-03 | B2 | |
| FR-TIER-05 | UC-01 | F-15 | MemoryObjectStore cache | T-TIER-01 | B2 | |
| FR-TIER-06 | UC-01 | F-15 | RemoteSource → server | T-TIER-01 | B2 | |
| FR-TIER-07 | UC-25 | F-16 | Service.dispatch(tiers) | T-TIER-03 | B2 | |
| FR-TIER-08 | UC-25 | F-15 | in-memory caches | T-TIER-06 | B2 | |
| FR-TIER-09 | UC-25 | F-15 | RemoteSource failover | T-TIER-06 | B2 | |
| FR-TIER-10 | UC-01 | F-15 | CachingSource single flight | T-TIER-07 | B2 | |
| FR-TIER-11 | UC-24 | F-14 | create_snapshot; LATEST | T-TIER-05 | B2 | |
| FR-CL-01 | UC-01 | F-17 | WorkingCopy.clone | T-CL-06/07, T-TIER-01 | B2 | |
| FR-CL-02 | UC-01 | F-18 | BoundedFileObjectStore | T-CL-08 | B2 | |
| FR-CL-03 | UC-01 | F-19 | _write_file | T-CL-02 | B2 | |
| FR-CL-04 | UC-03 | F-20 | fsmonitor | T-CL-09 | B2 | |
| FR-CL-05 | UC-03 | F-19 | status/add/rm/restore/diff_local | T-CL-01/05 | B2 | |
| FR-CL-06 | UC-04 | F-19 | commit | T-CL-01 | B2 | |
| FR-CL-07 | UC-05 | F-19 | update | T-CL-03 | B2 | |
| FR-CL-08 | UC-06 | F-19 | rebase | T-CL-04 | B2 | |
| FR-CL-09 | UC-01 | F-17 | sparse_add/remove | T-CL-06, T-CL-12 | B2 | |
| FR-CL-10 | UC-02 | F-17 | materialize; read | T-CL-07 | B2 | |
| FR-CL-11 | all | F-21 | cli.scn_main | T-CL-11 | B2 | |
| FR-CL-12 | UC-01 | F-13 | config "objects" | T-TIER-01 | B2 | |
| FR-IAM-01 | UC-22 | F-22 | Policy.repo_read/repo_write | T-IAM-09 | B3 | |
| FR-IAM-02 | UC-22 | F-44 | Deployment registry; repo-scoped RPCs and caches (ADR-13) | T-MR-01 | B2 | |
| FR-IAM-03 | UC-22 | F-22 | PathRule | T-IAM-01, T-IAM-05 | B3 | |
| FR-IAM-04 | UC-01, UC-08…12 | F-23 | per-path checks; fetch_objects; snapshots | T-IAM-01/03/04 | B3 | |
| FR-IAM-05 | UC-01 | F-23 | F_RESTRICTED; CachingSource.restricted | T-IAM-04 | B3 | |
| FR-IAM-06 | UC-22 | F-22 | groups, admins, service principals | T-IAM-01 | B3 | |
| FR-IAM-07 | UC-22 | F-24 | Policy.authenticate | T-IAM-08 | B2 | |
| FR-IAM-08 | UC-01 | F-24 | X-Scion-On-Behalf-Of | T-IAM-04 | B2 | |
| FR-IAM-09 | UC-22 | F-26 | reindex_acl | T-IAM-10 | B3 | |
| FR-IAM-10 | UC-22 | F-26 | audit table, hash chain (ADR-15) | T-AUD-01 | B3 | |
| FR-IAM-11 | UC-22 | F-23 | _record_acl | T-IAM-02 | B3 | |
| FR-RV-01 | UC-13 | F-27 | antique.create | T-LD-01 | B3 | |
| FR-RV-02 | UC-14 | F-27 | antique.update | T-RV-05 | B3 | |
| FR-RV-03 | UC-14 | F-27 | antique.comment | T-RV-06 | B3 | |
| FR-RV-04 | UC-14 | F-27 | requirements (author excluded) | T-RV-03 | B3 | |
| FR-RV-05 | UC-14 | F-28 | classify | T-RV-01 | B3 | |
| FR-RV-06 | UC-14 | F-28 | review rules; owners | T-RV-04 | B3 | |
| FR-RV-07 | UC-14 | F-28 | requirements() | T-RV-02 | B3 | |
| FR-RV-08 | UC-14 | F-29 | server.handle_get /antique | T-RV-06 | B3 | |
| FR-RV-09 | UC-14 | F-29 | HTML forms + session/CSRF (ADR-17) | T-RV-07 | B3 | |
| FR-RV-10 | UC-13 | F-32 | notifier webhooks (ADR-18) | T-RV-08 | B3 | |
| FR-LD-01 | UC-15 | F-30 | Antique._land_batch | T-LD-01, T-LD-03 | B3 | |
| FR-LD-02 | UC-15 | F-30 | CAS only across servers | T-SIM-01 | B3 | |
| FR-LD-03 | UC-15 | F-30 | group commit; backoff; deadline | T-SIM-01 (32×5 stress) | B3 | |
| FR-LD-04 | UC-16 | F-30 | MergeConflict → 409; CR conflict state | T-LD-02 | B3 | |
| FR-LD-05 | UC-17 | F-31 | landings table; find_landing | T-LD-01, T-SIM-01 | B3 | |
| FR-LD-06 | UC-21 | F-38 | land_changeset | T-AUT-02, T-PM-01 | B3 | |
| FR-LD-07 | UC-15 | F-35 | postmerge row on landing | T-PM-01 | B3 | |
| FR-PM-01 | UC-18 | F-35 | postmerge_claim (conditional UPDATE) | T-PM-02 | B4 | |
| FR-PM-02 | UC-18 | F-35 | run_worker reuses checkout | T-PM-01 | B4 | |
| FR-PM-03 | UC-18 | F-35 | postmerge_report | T-PM-01 | B4 | |
| FR-PM-04 | UC-18 | F-35 | revert_landing | T-PM-01 | B4 | |
| FR-PM-05 | UC-19 | F-36 | deploy_gate | T-PM-01 | B4 | |
| FR-AUT-01 | UC-20 | F-37 | tools.bisect | T-AUT-01 | B4 | |
| FR-AUT-02 | UC-21 | F-38 | tools.revert | T-AUT-02 | B4 | |
| FR-SR-01 | UC-12 | F-39 | search_paths | T-SR-01 | B4 | |
| FR-SR-02 | UC-12 | F-39 | grep | T-SR-01 | B4 | |
| FR-SR-03 | UC-12 | F-45 | content index derived type (ADR-16) | T-SR-02 | B4 | |
| FR-SR-04 | UC-12 | F-39 | per-path filtering | T-IAM-03 | B4 | |
| FR-MG-01 | UC-23 | F-33 | GitIngester.ingest | T-MG-01 | B4 | |
| FR-MG-02 | UC-23 | F-33 | missing-parent check | T-MG-03 | B4 | |
| FR-MG-03 | UC-23 | F-33 | git_map skip | T-MG-01 | B4 | |
| FR-MG-04 | UC-23 | F-33 | streaming rev-list and cat-file; bounded blob map | T-MG-04 | B4 | |
| FR-MG-05 | UC-23 | F-33 | GitIngester.verify | T-MG-01 | B4 | |
| FR-MG-06 | UC-23 | F-34 | server API over ingested history | T-E2E-01 | B4 | |
| FR-MG-07 | UC-23 | F-33 | git_map; changeset extra["git"] | T-MG-01 | B4 | |
| FR-OP-01 | UC-26 | F-40 | /healthz, /stats on every tier | T-OPS-02 | B2 | |
| FR-OP-02 | UC-26 | F-40 | Metrics; CachingSource.stats | T-TIER-01 | B2 | |
| FR-OP-03 | UC-26 | F-41 | Superfan baselines | T-OPS-02 | B4 | |
| FR-OP-04 | UC-26 | F-41 | Superfan rules | T-OPS-02 | B4 | |
| FR-OP-05 | UC-26 | F-41 | Superfan.notify webhook | T-OPS-03 | B4 | |
| FR-OP-08 | UC-26 | F-41 | per-component log ring buffer, GET /logs (ADR-18) | T-OPS-04 | B4 | |
| FR-OP-06 | UC-25 | F-42 | ratelimit; 429 handling | T-OPS-01 | B2 | |
| FR-OP-07 | UC-25 | F-43 | tools.bench | T-PERF-01 | B4 | |
| FR-AD-01 | UC-23 | F-43 | scion-admin init | T-E2E-01 | B4 | |
| FR-AD-02 | UC-24 | F-43 | scion-admin snapshot | T-E2E-01 | B4 | |
| FR-AD-03 | UC-27 | F-43 | scion-admin derive | T-DD-07 | B4 | |
| FR-AD-04 | UC-22 | F-43 | scion-admin reindex-acl | T-IAM-10 | B4 | |
| FR-AD-05 | UC-28 | F-43 | scion-admin set-ref | T-ADM-01 | B3 | |
| FR-AD-06 | UC-30 | F-43 | SQLite online backup + object copy | T-BAK-01 | B4 | |

## 11.2 Non-functional requirements

| Req | Status | Evidence / note |
|---|---|---|
| NFR-01 | B5 | planned verification: T-SIM-01, T-PERF-01 |
| NFR-02 | B5 | planned verification: T-SIM-01, T-PERF-01 |
| NFR-03 | B5 | planned verification: 10 §10.4 |
| NFR-04 | B5 | planned verification: T-SIM-01, T-PERF-01 |
| NFR-05 | I | T-CORE-10: one-file commit time flat within ±25% from 10² to 10⁴ files, and a constant 3 tree writes |
| NFR-06 | I | T-DD-06: ancestry over 100 changesets in < 20 steps; history is one lookup per result |
| NFR-07 | B2 | planned verification: 10 §10.4 |
| NFR-08 | B2 | planned verification: 10 §10.4 |
| NFR-09 | B2 | planned verification: 10 §10.4 |
| NFR-10 | B3 | planned verification: 10 §10.4 |
| NFR-11 | B2 | planned verification: 10 §10.4 |
| NFR-12 | I | T-CORE-05: concurrent CAS, exactly one winner, unbroken ref log; T-DD-01: deterministic derived values across two servers |
| NFR-13 | B5 | planned verification: 10 §10.4 |
| NFR-14 | I | no maintenance commands exist; T-DD-02: a new derived type in one class |
| NFR-15 | B5 | planned verification: 10 §10.4 |
| NFR-16 | B2 | planned verification: 10 §10.4 |
| NFR-17 | B5 | planned verification: T-SIM-01, T-PERF-01 |
| NFR-18 | B3 | planned verification: 10 §10.4 |
| NFR-19 | B2 | planned verification: 10 §10.4 |
| NFR-20 | B2 | planned verification: 10 §10.4 |

## 11.3 Coverage summary

Updated at the end of every milestone (computed by the T-DOC-02 cross-check).

| Milestone | Scope | Status |
|---|---|---|
| B1 | version control core | **done**: 45 requirements built and tested (21 core tests; fuzzing 8 seeds × 70 steps in the suite, 200 × 120 in a stress run) |
| B2 | service, tiers, client, multi-repository, TLS | planned |
| B3 | IAM, audit, review and landing | planned |
| B4 | migration, automation, search, operations, backup | planned |
| B5 | system verification of the non-functional requirements | planned |

## 11.4 Findings carried into the rebuild

| ID | Finding (from the review of the deleted prototype) | Resolution in the rebuild design |
|---|---|---|
| D-01 | `postmerge_claim` gave up after 10 contended attempts | claim retries until the queue is empty (T-PM-02) |
| D-02 | the CR stayed `open` while its landing was queued | CRs show `landing` while queued (T-LD-03) |
| D-03 | the admin tool moved refs without the protected-ref policy | admin ref operations run as an explicit identity (FR-AD-05, T-ADM-01) |
| D-04 | line comments were not shown inline | inline comments in the interactive review UI (FR-RV-09, T-RV-07) |
