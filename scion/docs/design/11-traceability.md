# 11. Traceability and gap analysis

This matrix traces every requirement to use cases (05), features (04), design elements (06/07)
and tests (10). It also gives the **honest status of the code already written**, checked
against the code itself:

* **I**: implemented, and the acceptance criterion is verified by an automated test.
* **I\***: implemented, but the acceptance test is missing (a test gap).
* **P**: partially implemented (the note says what is missing).
* **G**: not implemented (a gap).

## 11.1 Functional requirements

| Req | Use cases | Feature | Design | Tests | Status | Note |
|---|---|---|---|---|---|---|
| FR-CS-01 | UC-04, UC-07 | F-01 | repo.create_changeset; client.commit | T-CL-01, T-IAM-07 | I | |
| FR-CS-02 | UC-04 | F-01 | changeset.Changeset | T-CORE-03, T-FUZZ-01 | I | |
| FR-CS-03 | UC-04 | F-02 | objects, storage | T-CORE-03 | I | |
| FR-CS-04 | UC-04 | F-01 | Changeset.id; meta.insert_changeset | T-CORE-04 | I | |
| FR-CS-05 | UC-04 | F-01 | meta.insert_changeset | T-CORE-05, T-SIM-01 | I | |
| FR-CS-06 | UC-04 | F-01 | shared MetaStore | T-SIM-01, T-TIER-06 | I | |
| FR-CS-07 | all queries | F-05 | repo.resolve | T-CORE-06 | I | |
| FR-CS-08 | UC-04, UC-07 | F-01 | repo.create_changeset; trees.apply_augmented | T-CORE-07 | I | |
| FR-CS-09 | UC-04 | F-03 | trees.apply_augmented; incremental derived types | T-CORE-08, T-PERF-01 | I\* | timing is benchmarked but not asserted |
| FR-REF-01 | UC-13, UC-15 | F-04 | meta.refs; antique.create | T-CORE-05, T-LD-01 | I | |
| FR-REF-02 | UC-15, UC-28 | F-04 | meta.cas_ref | T-CORE-05, T-SIM-01 | I | |
| FR-REF-03 | UC-28 | F-25 | iam.can_update_ref | T-IAM-06 | I | |
| FR-REF-04 | UC-28 | F-04 | meta.ref_log | T-SIM-01 | I | |
| FR-REF-05 | UC-28 | F-25 | protected_refs patterns; update_ref | — | P | no release-branch command or test |
| FR-OBJ-01 | all (5.3) | F-02 | objects | T-CORE-01 | I | |
| FR-OBJ-02 | all (5.3) | F-02 | storage.FileObjectStore | T-CORE-01 | I | |
| FR-OBJ-03 | all (5.3) | F-02 | bounded stores; no gc | T-CORE-02 | I | |
| FR-OBJ-04 | UC-01 | F-02 | decode_stored(expected_id) in daemon and client | T-TIER-08 | I | |
| FR-OBJ-05 | all (5.3) | F-02 | derived trees only | T-CORE-08 | I | |
| FR-DD-01 | UC-27 | F-06 | derived.DerivedDataManager | T-DD-01 | I | |
| FR-DD-02 | UC-09, UC-27 | F-06 | DerivedDataManager._derive_missing | T-DD-01 | I | |
| FR-DD-03 | UC-09, UC-27 | F-06 | DerivedType.eager | T-DD-01 | I | |
| FR-DD-04 | UC-27 | F-06 | register | T-DD-02 | I | |
| FR-DD-05 | UC-09 | F-06 | derived_put (insert or ignore) | T-SIM-01 | I | covered indirectly (two servers) |
| FR-DD-06 | UC-27 | F-06 | backfill; `scion-admin derive` | — | I\* | no test |
| FR-DD-07 | UC-01 | F-06 | RootTreeType | T-FUZZ-01 | I | |
| FR-DD-08 | UC-08 | F-08 | HistoryTreeType; repo.file_history | T-DD-04, T-FUZZ-01 | I | |
| FR-DD-09 | UC-09 | F-08 | BlameType | T-DD-05, T-FUZZ-01, T-MG-02 | I | |
| FR-DD-10 | UC-11 | F-07 | GraphType; is_ancestor; merge_bases | T-DD-06, T-FUZZ-01 | I | |
| FR-DD-11 | UC-08 | F-08 | CopyInfoType | T-DD-03 | I | |
| FR-DD-12 | UC-12 | F-39 | SearchTreeType | T-SR-01, T-FUZZ-01 | I | |
| FR-QRY-01 | all | F-09 | server.get_changeset(s) | T-IAM-03 | I | |
| FR-QRY-02 | UC-20 | F-09 | repo.log | T-AUT-01, T-DD-04 | I | |
| FR-QRY-03 | UC-05, UC-10 | F-09 | repo.diff; trees.diff | T-CORE-09, T-FUZZ-01 | I | |
| FR-QRY-04 | UC-10 | F-09 | server._diff(merge_base) | T-CL-10 | I | |
| FR-QRY-05 | UC-11 | F-07 | merge_bases; is_ancestor | T-DD-06, T-FUZZ-01 | I | |
| FR-QRY-06 | UC-08 | F-08 | file_history | T-DD-03/04 | I | |
| FR-QRY-07 | UC-09 | F-08 | blame | T-DD-05 | I | |
| FR-QRY-08 | UC-02 | F-09 | read_file; list_dir | T-IAM-03 | I | |
| FR-QRY-09 | UC-11, UC-20 | F-07 | fp_ancestor | T-DD-06 | I | |
| FR-QRY-10 | all | F-09 | client uses only public RPCs | T-CL-11 | I | |
| FR-WR-01 | UC-07 | F-11 | create_changeset (content_b64) | T-CL-10 | I | |
| FR-WR-02 | UC-06, UC-29 | F-10 | repo.merge; merge3 | T-WR-01 | I | |
| FR-WR-03 | UC-06 | F-10 | repo.rebase | T-WR-01, T-CL-04 | I | |
| FR-WR-04 | UC-21 | F-10 | repo.revert | T-WR-01, T-PM-01 | I | |
| FR-WR-05 | UC-07 | F-11 | create_changeset update_ref | T-CL-10 | I | |
| FR-WR-06 | UC-04 | F-11 | has_objects | T-CL-01 | I | |
| FR-WR-07 | UC-04, UC-07 | F-11 | — | — | G | only a 512 MB request-body cap exists |
| FR-FP-01 | UC-01 | F-12 | get_objects (ids only) | T-TIER-01 | I | |
| FR-FP-02 | UC-01 | F-12 | WorkingCopy._collect_files | T-CL-06 | I | |
| FR-FP-03 | UC-01 | F-12 | per-object framing; local cache | — | P | objects are reused from the daemon, but an interrupted `clone` cannot resume in place |
| FR-FP-04 | UC-01, UC-02 | F-12 | same RPC for every mode | T-CL-06/07 | I | |
| FR-FP-05 | UC-01 | F-12 | shared get_objects handler | T-TIER-02 | I | |
| FR-FP-06 | UC-01 | F-12 | stored bytes passed through | T-TIER-02 | I | |
| FR-FP-07 | UC-01 | F-12 | FETCH_BATCH; FETCH_PARALLEL | T-TIER-01 | I | |
| FR-TIER-01 | UC-01 | F-13 | DaemonService (Unix socket) | T-TIER-01 | I | |
| FR-TIER-02 | UC-01 | F-13 | BoundedFileObjectStore | T-CORE-02 | I | |
| FR-TIER-03 | UC-24 | F-14 | snapshot; refresh_snapshot | T-TIER-05 | I | |
| FR-TIER-04 | UC-25 | F-13 | tier principals; allowed callers | T-TIER-03 | I | |
| FR-TIER-05 | UC-01 | F-15 | MemoryObjectStore cache | T-TIER-01 | I | |
| FR-TIER-06 | UC-01 | F-15 | RemoteSource → server | T-TIER-01 | I | |
| FR-TIER-07 | UC-25 | F-16 | Service.dispatch(tiers) | T-TIER-03 | I | |
| FR-TIER-08 | UC-25 | F-15 | in-memory caches | T-TIER-06 | I | |
| FR-TIER-09 | UC-25 | F-15 | RemoteSource failover | T-TIER-06 | I | |
| FR-TIER-10 | UC-01 | F-15 | CachingSource single flight | T-TIER-07 | I | |
| FR-TIER-11 | UC-24 | F-14 | create_snapshot; LATEST | T-TIER-05 | I | |
| FR-CL-01 | UC-01 | F-17 | WorkingCopy.clone | T-CL-06/07, T-TIER-01 | I | |
| FR-CL-02 | UC-01 | F-18 | BoundedFileObjectStore | T-CL-08 | I | |
| FR-CL-03 | UC-01 | F-19 | _write_file | T-CL-02 | I | |
| FR-CL-04 | UC-03 | F-20 | fsmonitor | T-CL-09 | I | |
| FR-CL-05 | UC-03 | F-19 | status/add/rm/restore/diff_local | T-CL-01/05 | I | `restore` lacks a direct test |
| FR-CL-06 | UC-04 | F-19 | commit | T-CL-01 | I | |
| FR-CL-07 | UC-05 | F-19 | update | T-CL-03 | I | |
| FR-CL-08 | UC-06 | F-19 | rebase | T-CL-04 | I | |
| FR-CL-09 | UC-01 | F-17 | sparse_add/remove | T-CL-06, T-CL-12 | I | |
| FR-CL-10 | UC-02 | F-17 | materialize; read | T-CL-07 | I | |
| FR-CL-11 | all | F-21 | cli.scn_main | T-CL-11 | I | |
| FR-CL-12 | UC-01 | F-13 | config "objects" | T-TIER-01 | I | |
| FR-IAM-01 | UC-22 | F-22 | Policy.repo_read/repo_write | — | I\* | no repository-level restriction test |
| FR-IAM-02 | UC-22 | F-44 | — | — | G | one repository per server process |
| FR-IAM-03 | UC-22 | F-22 | PathRule | T-IAM-01, T-IAM-05 | I | |
| FR-IAM-04 | UC-01, UC-08…12 | F-23 | per-path checks; fetch_objects; snapshots | T-IAM-01/03/04 | I | parent trees reveal restricted names (threat I4, accepted) |
| FR-IAM-05 | UC-01 | F-23 | F_RESTRICTED; CachingSource.restricted | T-IAM-04 | I | |
| FR-IAM-06 | UC-22 | F-22 | groups, admins, service principals | T-IAM-01 | I | |
| FR-IAM-07 | UC-22 | F-24 | Policy.authenticate | T-IAM-08 | I | |
| FR-IAM-08 | UC-01 | F-24 | X-Scion-On-Behalf-Of | T-IAM-04 | I | |
| FR-IAM-09 | UC-22 | F-26 | reindex_acl | — | I\* | no test |
| FR-IAM-10 | UC-22 | F-26 | — | — | G | only the ref log exists |
| FR-IAM-11 | UC-22 | F-23 | _record_acl | T-IAM-02 | I | |
| FR-RV-01 | UC-13 | F-27 | antique.create | T-LD-01 | I | |
| FR-RV-02 | UC-14 | F-27 | antique.update | T-RV-05 | I | |
| FR-RV-03 | UC-14 | F-27 | antique.comment | T-RV-06 | I | line comments are stored but not shown inline in the diff |
| FR-RV-04 | UC-14 | F-27 | requirements (author excluded) | T-RV-03 | I | |
| FR-RV-05 | UC-14 | F-28 | classify | T-RV-01 | I | |
| FR-RV-06 | UC-14 | F-28 | review rules; owners | T-RV-04 | I | |
| FR-RV-07 | UC-14 | F-28 | requirements() | T-RV-02 | I | |
| FR-RV-08 | UC-14 | F-29 | server.handle_get /antique | T-RV-06 | I | |
| FR-RV-09 | UC-14 | F-29 | — | — | G | the web UI is read-only |
| FR-RV-10 | UC-13 | F-32 | — | — | G | |
| FR-LD-01 | UC-15 | F-30 | Antique._land_batch | T-LD-01 | I | |
| FR-LD-02 | UC-15 | F-30 | CAS only across servers | T-SIM-01 | I | |
| FR-LD-03 | UC-15 | F-30 | group commit; backoff; deadline | T-SIM-01 (32×5 stress) | I | |
| FR-LD-04 | UC-16 | F-30 | MergeConflict → 409; CR conflict state | T-LD-02 | I | |
| FR-LD-05 | UC-17 | F-31 | landings table; find_landing | T-LD-01, T-SIM-01 | I | |
| FR-LD-06 | UC-21 | F-38 | land_changeset | T-AUT-02, T-PM-01 | I | |
| FR-LD-07 | UC-15 | F-35 | postmerge row on landing | T-PM-01 | I | |
| FR-PM-01 | UC-18 | F-35 | postmerge_claim (conditional UPDATE) | — | I\* | no concurrent-claim test; see finding D-01 |
| FR-PM-02 | UC-18 | F-35 | run_worker reuses checkout | T-PM-01 | I | |
| FR-PM-03 | UC-18 | F-35 | postmerge_report | T-PM-01 | I | |
| FR-PM-04 | UC-18 | F-35 | revert_landing | T-PM-01 | I | |
| FR-PM-05 | UC-19 | F-36 | deploy_gate | T-PM-01 | I | |
| FR-AUT-01 | UC-20 | F-37 | tools.bisect | T-AUT-01 | I | |
| FR-AUT-02 | UC-21 | F-38 | tools.revert | T-AUT-02 | I | |
| FR-SR-01 | UC-12 | F-39 | search_paths | T-SR-01 | I | |
| FR-SR-02 | UC-12 | F-39 | grep | T-SR-01 | I | |
| FR-SR-03 | UC-12 | F-45 | — | — | G | grep scans files; no content index |
| FR-SR-04 | UC-12 | F-39 | per-path filtering | T-IAM-03 | I | |
| FR-MG-01 | UC-23 | F-33 | GitIngester.ingest | T-MG-01 | I | |
| FR-MG-02 | UC-23 | F-33 | missing-parent check | T-MG-03 | I | |
| FR-MG-03 | UC-23 | F-33 | git_map skip | T-MG-01 | I | |
| FR-MG-04 | UC-23 | F-33 | streaming rev-list and cat-file; bounded blob map | — | I\* | memory not measured |
| FR-MG-05 | UC-23 | F-33 | GitIngester.verify | T-MG-01 | I | |
| FR-MG-06 | UC-23 | F-34 | server API over ingested history | T-E2E-01 | I | |
| FR-MG-07 | UC-23 | F-33 | git_map; changeset extra["git"] | T-MG-01 | I | |
| FR-OP-01 | UC-26 | F-40 | /healthz, /stats on every tier | T-OPS-02 | I | |
| FR-OP-02 | UC-26 | F-40 | Metrics; CachingSource.stats | T-TIER-01 | I | |
| FR-OP-03 | UC-26 | F-41 | Superfan baselines | T-OPS-02 | I | |
| FR-OP-04 | UC-26 | F-41 | Superfan rules | T-OPS-02 | I | |
| FR-OP-05 | UC-26 | F-41 | Superfan.notify webhook | — | I\* | no test |
| FR-OP-06 | UC-25 | F-42 | ratelimit; 429 handling | T-OPS-01 | I | |
| FR-OP-07 | UC-25 | F-43 | tools.bench | T-PERF-01 | I | |
| FR-AD-01 | UC-23 | F-43 | scion-admin init | T-E2E-01 | I | |
| FR-AD-02 | UC-24 | F-43 | scion-admin snapshot | T-E2E-01 | I | |
| FR-AD-03 | UC-27 | F-43 | scion-admin derive | — | I\* | see FR-DD-06 |
| FR-AD-04 | UC-22 | F-43 | scion-admin reindex-acl | — | I\* | see FR-IAM-09 |
| FR-AD-05 | UC-28 | F-43 | scion-admin set-ref | — | P | the local admin tool bypasses protected-ref checks (direct storage access) |
| FR-AD-06 | UC-30 | F-43 | — | — | G | no backup or restore |

## 11.2 Non-functional requirements

| Req | Status | Evidence / note |
|---|---|---|
| NFR-01 | P | prototype target met (T-SIM-01 at 32×5 on 2 servers). The production rate can't be shown on one host. |
| NFR-02 | P | a second checkout on a node makes 0 cache requests (T-TIER-01); 99% steady-state rate not measured at fleet scale |
| NFR-03 | P | true by construction (no full copies); not exercised at 100 GB |
| NFR-04 | P | 2,000-file checkout in about 1 s from a warm daemon (T-PERF-01); no automated latency budget |
| NFR-05 | I\* | flat 8–10 ms commits from 10² to 10⁴ files (T-PERF-01); not asserted |
| NFR-06 | I | step counters asserted (T-DD-06) |
| NFR-07 | P | servers, caches and daemons scale out; the SQLite stand-in is single-host (R-02) |
| NFR-08 | I | T-TIER-03, T-TIER-07 |
| NFR-09 | P | failover implemented (T-TIER-06); no health-based load balancing |
| NFR-10 | I | T-IAM-*; residual I4 and R-07 |
| NFR-11 | I | T-TIER-08 |
| NFR-12 | I | T-SIM-01 (ref log chain), T-CORE-05 |
| NFR-13 | P | durable SQLite in WAL mode; no backup (FR-AD-06) |
| NFR-14 | I | no maintenance commands; T-DD-02 |
| NFR-15 | I | T-FUZZ-01, T-SIM-01 |
| NFR-16 | I | FR-OP-01/02 |
| NFR-17 | P | small in-memory caches; no comparison with git mirrors |
| NFR-18 | I | structured errors; 409 data used by tests |
| NFR-19 | I | standard library only |
| NFR-20 | G | plaintext HTTP |

## 11.3 Coverage summary

Computed by the T-DOC-02 cross-check, not by hand.

| | Total | I | I\* | P | G |
|---|---|---|---|---|---|
| Functional | 137 | 118 | 9 | 3 | 7 |
| Must (functional) | 104 | 98 | 4 | 2 | 0 |

No **Must** requirement is missing.

* **Partial Musts:** FR-FP-03 (resumable checkout) and FR-AD-05 (the admin tool bypasses ref protections).
* **Musts without an automated acceptance test:** FR-CS-09, FR-IAM-01, FR-MG-04 and FR-PM-01.
* **The 7 gaps (G)** are all Should or Could requirements.

## 11.4 Gap list (the proposed work queue, pending your approval)

| Gap | Requirement | Pri | Proposed work |
|---|---|---|---|
| GAP-01 | FR-FP-03 | M | resumable `clone` (detect a partial working copy and continue) |
| GAP-02 | FR-AD-05 | M | `scion-admin set-ref` runs as an explicit admin identity, with protections enforced (finding D-03) |
| GAP-03 | FR-CS-09, FR-IAM-01, FR-MG-04, FR-PM-01 | M | missing acceptance tests: commit-scaling assertion, repository-level read restriction, ingestion memory bound, concurrent post-merge claim (fixes finding D-01) |
| GAP-04 | NFR-20 | S (required before production) | TLS/mTLS between all tiers |
| GAP-05 | FR-IAM-10 | S | audit log for policy changes, denials and admin actions |
| GAP-06 | FR-IAM-02 | S | multi-repository hosting with a policy per repository |
| GAP-07 | FR-AD-06 | S | backup and restore of the metadata and blob stores (UC-30) |
| GAP-08 | FR-WR-07 | S | per-file upload size limit |
| GAP-09 | FR-SR-03 | S | trigram content index as a derived type |
| GAP-10 | FR-RV-09 | S | interactive review UI (approve, comment, inline line comments: finding D-04) |
| GAP-11 | FR-REF-05 | S | release-branch command and test |
| GAP-12 | FR-DD-06, FR-IAM-09, FR-OP-05 | S | missing tests for implemented features |
| GAP-13 | FR-RV-10 | C | reviewer notifications |

## 11.5 Findings from the review against the design

| ID | Finding | Severity | Action |
|---|---|---|---|
| D-01 | `postmerge_claim` gives up after 10 contended attempts and returns "no job" while jobs exist; a `--once` worker could then stop early. | 3 | Retry until the queue is empty, and add a concurrent-claim test (GAP-03). |
| D-02 | The design's CR state machine has a `Landing` state (6.7); the code keeps the CR `open` while a landing is queued. | 4 | Either add the state or amend the design. Decision needed. |
| D-03 | `scion-admin set-ref` writes refs without the protected-ref policy (FR-AD-05). | 3 | Run it as an explicit admin identity (GAP-02). |
| D-04 | Line comments are stored but not shown inline in the diff view. | 4 | Part of GAP-10. |
