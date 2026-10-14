# 10. Verification and test plan

## 10.1 Objectives

1. Show that every **Must** requirement meets its acceptance criterion (03).
2. Find defects in concurrency, history semantics and access control. The article credits fuzzing
   and hermetic simulation for exactly these.
3. Measure the scaling properties that can be reproduced on one host (NFR-05, NFR-06, NFR-02).

## 10.2 Test levels

| Level | What | How | Where |
|---|---|---|---|
| Unit | objects, storage, changesets, trees, merge3, classifier, rate limiter | `unittest`, deterministic inputs | `tests/test_core.py`, `tests/test_ops.py`, `tests/test_antique.py` |
| Property / fuzz | trees, diffs, history, blame, ancestry, merge bases, search vs. a naive model and algorithm-independent invariants | seeded random histories with edits, renames, file↔directory swaps and merges; `SCION_FUZZ_SEEDS`, `SCION_FUZZ_STEPS` | `tests/test_fuzz.py` |
| Integration | server + cache + daemon(s) in-process over real sockets | the hermetic `Cluster` helper | `tests/test_tiers.py`, `tests/test_iam.py`, `tests/test_client.py`, `tests/test_antique.py`, `tests/test_ops.py`, `tests/test_automation.py`, `tests/test_search.py`, `tests/test_superfan.py`, `tests/test_admin.py` |
| Simulation / stress | swarm of agents doing clone, commit, review and land concurrently on 2 servers | `SCION_SIM_AGENTS`, `SCION_SIM_ROUNDS` | `tests/test_simulation.py` |
| Migration | real git repositories with branches, merges, renames, modes, symlinks, file↔directory swaps | `git` CLI in a temp directory | `tests/test_ingest.py` |
| System / E2E | separate processes: server, cache, daemon (Unix socket), CLI | shell script | `examples/demo.sh` |
| Performance | commit scaling, ancestry, tiered checkout; Scion against git on the same repository | `scion-admin bench` (invariants asserted by T-PERF-01), `scion-admin bench --vs-git` | `scion/tools/bench.py`, `tests/test_admin.py` |
| Metadata backends | the metadata conformance suite, and the integration suites that write metadata, on SQLite and on Google's Spanner emulator | `SCION_TEST_SPANNER=<emulator REST endpoint>` selects Spanner; without it the Spanner tests skip | `tests/test_metastore.py` and the suites below |
| Migration pilot | ingest CPython with verification; serve its history to CI with no client; measure growth | manual run, results recorded in 11 | `examples/pilot.sh` |
| Documentation | every Mermaid diagram renders; every requirement and test ID is defined, traced and tested | `scripts/check_docs.py` (`--mmdc` adds the render check) | T-DOC-01, T-DOC-02 |

## 10.3 Environments

* **Developer / CI:** Linux, Python ≥ 3.10, `git`; no network access needed (everything binds to localhost and Unix sockets).
* **Stress:** the same as above, with larger environment-variable settings; run before each release.
* **Production-like (future):** multiple hosts with TLS. Not available to the prototype.

## 10.4 Test cases by area

| Test ID | Covers | Description | Automated in |
|---|---|---|---|
| T-CORE-01 | FR-OBJ-01/04 | stored-object round trip and integrity failure | test_core.TestObjects |
| T-CORE-02 | FR-OBJ-03, FR-TIER-02, FR-CL-02 | bounded stores evict and rebuild from disk | test_core.TestObjects |
| T-CORE-03 | FR-CS-02/03/05 | changes relative to the first parent; no-op detection | test_core.TestChangesets |
| T-CORE-04 | FR-CS-04 | idempotent creation | test_core.TestChangesets |
| T-CORE-05 | FR-REF-01/02 | no refs needed; CAS semantics | test_core.TestChangesets |
| T-CORE-06 | FR-CS-07 | revision syntax | test_core.TestChangesets |
| T-CORE-07 | FR-CS-08 | validation, including file↔directory replacement | test_core.TestChangesets |
| T-CORE-08 | FR-CS-09, FR-OBJ-05 | only changed subtrees are rewritten | test_core.TestChangesets |
| T-CORE-09 | FR-QRY-03 | scoped diffs and text diffs | test_core.TestChangesets |
| T-CORE-11 | FR-QRY-08 | read a file and list a directory at a revision | test_core |
| T-CORE-12 | FR-DD-12, FR-SR-01 | path search skips subtrees whose bloom filter cannot match | test_core |
| T-DD-01 | FR-DD-01/02/03 | eager vs deferred; ancestors derived first | test_core.TestDerived |
| T-DD-02 | FR-DD-04 | registering a new type | test_core.TestDerived |
| T-DD-03 | FR-DD-11, FR-QRY-06 | copy and rename detection; history across renames | test_core.TestDerived |
| T-DD-04 | FR-DD-08 | file and directory history | test_core.TestDerived |
| T-DD-05 | FR-DD-09, BR-06 | blame: linear, through copies, through merges | test_core.TestDerived |
| T-DD-06 | FR-DD-10, FR-QRY-05/09, NFR-06 | skip lists, generations, O(log n) steps, merge bases | test_core.TestAncestry |
| T-WR-01 | FR-WR-02/03/04 | merge3, rebase stacks, drop applied, revert, conflicts | test_core.TestMergeRebaseRevert |
| T-FUZZ-01 | FR-DD-*, FR-QRY-03/05/06/07, FR-SR-01 | random histories vs. a naive model and invariants | test_fuzz |
| T-TIER-01 | FR-TIER-01/05/06, NFR-02 | clone through the tiers; a second job on the node causes zero cache traffic | test_tiers |
| T-TIER-02 | FR-FP-05 | identical RPC on every tier | test_tiers |
| T-TIER-03 | FR-TIER-07, NFR-08 | strict tiering refusals | test_tiers |
| T-TIER-04 | FR-DD-04 (privacy of internals) | derived objects aren't served | test_tiers |
| T-TIER-05 | FR-TIER-03/11 | snapshot warm start and refresh | test_tiers |
| T-TIER-06 | FR-TIER-09 | failover between servers | test_tiers |
| T-TIER-07 | FR-TIER-10 | single flight | test_tiers |
| T-TIER-08 | FR-OBJ-04 | forged object rejected | test_tiers |
| T-IAM-01 | FR-IAM-03/04, FR-CL-01 | clone skips unreadable directories; nested public directory | test_iam |
| T-IAM-02 | FR-IAM-11 | public bytes stay public, both orders | test_iam |
| T-IAM-03 | FR-IAM-04, FR-SR-04 | filtered APIs: read, blame, list, grep, search, changeset | test_iam |
| T-IAM-04 | FR-IAM-05/08 | restricted objects through every tier; delegation | test_iam |
| T-IAM-05 | FR-IAM-03 | write permissions | test_iam |
| T-IAM-06 | FR-REF-03 | protected refs | test_iam |
| T-IAM-07 | FR-CS-01 | the author can't be spoofed | test_iam |
| T-IAM-08 | FR-IAM-07 | token authentication | test_iam |
| T-CL-01 | FR-CL-05/06 | edit, status, add, commit; nothing to push | test_client |
| T-CL-02 | FR-CL-03 | modes and symlinks round-trip | test_client |
| T-CL-03 | FR-CL-07 | update fetches only the diff; protects local changes | test_client |
| T-CL-04 | FR-CL-08 | server-side rebase from the client | test_client |
| T-CL-05 | FR-CL-05 | local diff | test_client |
| T-CL-06 | FR-CL-01/09, FR-FP-02/04 | sparse checkout, sparse add/remove, profile-scoped update | test_client |
| T-CL-07 | FR-CL-01/10 | virtual checkout, materialize on read, writes without reading | test_client |
| T-CL-08 | FR-CL-02 | tiny bounded cache | test_client |
| T-CL-09 | FR-CL-04 | fsmonitor journal and sync cookie | test_client |
| T-CL-10 | FR-WR-01/05, FR-QRY-04 | checkout-less write and merge-base diff | test_client |
| T-CL-11 | FR-CL-11 | CLI end to end | test_client |
| T-CL-12 | FR-CL-09 | adding a file outside the sparse profile | test_client |
| T-RV-01 | FR-RV-05 | classifier: Python, C-like, docs, binary, mode | test_antique.TestClassify |
| T-RV-02 | FR-RV-06/07, BR-03 | comment and docs changes need no approval | test_antique |
| T-RV-03 | FR-RV-04, BR-01 | self-approval doesn't count | test_antique |
| T-RV-04 | FR-RV-06 | owner approvals | test_antique |
| T-RV-05 | FR-RV-02, BR-02 | new revision resets approvals | test_antique |
| T-LD-01 | FR-LD-01/05, FR-REF-01 | lock-free landing, rebase, landing index | test_antique |
| T-LD-02 | FR-LD-04 | structured conflicts and resolution | test_antique |
| T-RV-06 | FR-RV-08 | HTML view with escaping and diff | test_antique |
| T-PM-01 | FR-PM-01…05, FR-LD-06/07, FR-AUT-02 | post-merge worker with a reused checkout, auto-revert only on a passing base, deploy gate | test_automation |
| T-SIM-01 | FR-LD-02/03, FR-REF-04, FR-CS-05/06, NFR-01 | swarm of agents on 2 servers; no lost updates; CAS-chained ref log; no starvation (every landing within 60 s); at stress size more than 3.5 landings a second | test_simulation |
| T-MG-01 | FR-MG-01/03/05/07 | ingest, verify, incremental, the git map both ways | test_ingest |
| T-MG-02 | FR-MG-01, FR-DD-09 | blame parity with `git blame --first-parent` | test_ingest |
| T-MG-03 | FR-MG-02 | ordering invariant | test_ingest |
| T-OPS-01 | FR-OP-06 | token bucket, concurrency, 429 plus client backoff; a kept connection the server closed while idle is replaced at once, with no backoff (found by the CPython pilot) | test_ops |
| T-OPS-02 | FR-OP-03/04 | superfan novel (hit-rate drop), threshold, restart and unreachable findings; each raised once and resolved; cache and landing-queue profiles | test_superfan |
| T-SR-01 | FR-SR-01/02/04, FR-DD-12 | bloom pruning; grep (regex, fixed, case-insensitive, limits) filtered by permissions | test_search |
| T-AUT-01 | FR-AUT-01 | bisect without a checkout in ⌈log₂ n⌉ probes; the range is paged by changeset, and an offset past the server's cap is refused | test_automation |
| T-AUT-02 | FR-AUT-02, FR-LD-06 | revert pipeline under contention | test_automation |
| T-CORE-10 | FR-CS-09, NFR-05 | a one-file commit writes the same 3 trees and 10 objects at 10² and 10⁴ files, and with objects in memory takes the same time within ±25% (interleaved, asserted) | test_core |
| T-DD-07 | FR-DD-06 | backfilling a deferred type computes it for a revision and all ancestors | test_core |
| T-DD-08 | BR-06 | history and blame follow the first parent only; merge-introduced lines belong to the merge | test_core |
| T-MR-01 | FR-IAM-02, ADR-13 | two repositories with different policies on one deployment; caches key by repository; a private repository's objects are never cached | test_multirepo |
| T-TLS-01 | NFR-20, ADR-14 | TLS on every TCP hop; mutual TLS identifies tiers; plaintext and wrong certificates are refused | test_tls |
| T-LIM-01 | FR-WR-07 | an oversized upload gets 413 and stores nothing | test_ops |
| T-OPS-05 | FR-OP-01/02, NFR-16 | health, stats, latency percentiles, error counts and hit rates on server, cache and daemon | test_ops |
| T-STD-01 | NFR-19 | the package imports only the standard library | test_ops |
| T-IAM-11 | FR-IAM-04/11 | a restricted object can't be republished by its id; an uploader who has the bytes can commit them | test_iam |
| T-IAM-12 | FR-IAM-04 | snapshots leave out restricted objects | test_iam |
| T-IAM-13 | FR-IAM-06 | group membership changes apply to the next request | test_iam |
| T-IAM-14 | FR-IAM-05/09, ADR-20 | after a repository turns private or a re-index restricts objects, caches and daemons (also restarted ones) purge them within the epoch interval; stale snapshots are not imported | test_iam |
| T-RV-09 | FR-RV-03 | comments are stored with revision, path and line | test_antique |
| T-LD-04 | FR-LD-03 | concurrent landings on one server are group-committed | test_antique |
| T-LD-05 | FR-LD-06 | landing without a CR is for services and administrators | test_antique |
| T-PM-03 | FR-LD-07 | post-merge jobs are claimed and reported only by services and administrators | test_antique |
| T-ERR-01 | NFR-18 | errors are structured, with stable codes | test_ops |
| T-CL-14 | FR-CL-11, FR-RV-07 | review from the CLI | test_client |
| T-CL-13 | FR-FP-03 | an interrupted clone resumes in place and reuses received objects | test_client |
| T-IAM-09 | FR-IAM-01 | repository-level read restriction, through the API and through the caches | test_iam |
| T-IAM-10 | FR-IAM-09 | re-indexing ACLs after a policy change restricts existing objects | test_iam |
| T-AUD-01 | FR-IAM-10, ADR-15 | policy loads, denials and admin actions are audited; the hash chain verifies and detects tampering | test_iam |
| T-REF-01 | FR-REF-05 | release branches: created by the release role only, moved by CAS, logged | test_iam |
| T-ADM-01 | FR-AD-05 | admin ref operations run as an explicit identity and respect protections | test_ops |
| T-BAK-01 | FR-AD-06, NFR-13 | backup while landings continue, then restore: refs, changesets, CRs, permissions and the audit chain as at the snapshot; damaged backups and non-empty targets refused; verify finds missing and corrupt objects | test_admin |
| T-RV-07 | FR-RV-09, ADR-17 | approve, comment (inline) and land from the web UI; CSRF enforced | test_antique |
| T-RV-08 | FR-RV-10 | CR events reach a notification webhook; an endpoint that breaks off its reply doesn't stop the notifier | test_antique |
| T-LD-03 | FR-LD-01, D-02 | a CR shows `landing` while queued | test_antique |
| T-PM-02 | FR-PM-01, D-01 | concurrent workers claim every job exactly once | test_automation |
| T-SR-02 | FR-SR-03, ADR-16 | indexed content search reads only candidate blobs and matches a full scan, non-ASCII case folding and git's line numbers included | test_search |
| T-OPS-03 | FR-OP-05 | superfan findings are delivered to a webhook as a Slack-compatible payload | test_superfan |
| T-OPS-04 | FR-OP-08, ADR-18 | superfans read component logs and attach the lines around a finding; logs need an administrator or a service principal | test_superfan |
| T-MG-04 | FR-MG-04 | ingestion memory stays flat as history grows | test_ingest |
| T-MG-05 | FR-MG-06 | metadata queries (resolve, ancestry, blame, git lookups) over ingested history, with no client | test_ingest |
| T-PM-04 | FR-PM-01, D-01 | a lost worker's job returns to the queue after its lease; its late report is refused | test_automation |
| T-ADM-02 | FR-AD-01…04/06, FR-MG-05 | the scion-admin commands end to end: init, create-repo, ingest --verify, derive, snapshot, reindex-acl, audit --verify, backup, restore, verify | test_admin |
| T-E2E-01 | system, NFR-09/17 | every component in its own process: git ingestion with verification, clones through the tiers, sparse checkout, permissions, grep, review and landing, six concurrent landers, post-merge testing and the deploy gate, a superfan, server failover, online backup and verified restore, the audit chain, each process's footprint | examples/demo.sh |
| T-SYS-01 | NFR-02, NFR-17 | steady-state hit rates: one node with 100 jobs ≥ 99%; one cache behind 100 nodes ≥ 99% over its life, cold start included; every store within its configured MB bound, evicting when tiny | test_system |
| T-SYS-02 | NFR-13 | losing the daemon with its disk store, the cache and a server loses no data: replacements serve identical checkouts, and a new server process on the same storage serves everything | test_system |
| T-ST-01 | FR-ST-01 | metadata conformance: changesets, refs and the ref log, derived values, indexes, object ACLs and grants, settings, the content index, the audit chain, change requests, landings, the post-merge queue and the git map behave the same on SQLite and on the Spanner emulator; conditional CR transitions; a landing commits with its ref's move; reads of many large values stay under Spanner's result limit | test_metastore |
| T-ST-02 | FR-ST-02, UC-32 | a deployment configured for Spanner serves the whole API: clone, commit, review, land, search, audit; switching backends is configuration only; errors read in both of Spanner's formats | test_metastore |
| T-ST-03 | FR-ST-03 | under contention on Spanner: concurrent compare-and-swaps have exactly one winner; concurrent post-merge claims take every job once; the landing swarm loses nothing; an aborted transaction is retried in its session | test_metastore, test_simulation |
| T-ST-04 | FR-ST-04 | a backup of a Spanner deployment taken under load restores to SQLite and to Spanner, with identical refs, changesets and audit chain; every repository's metadata is read before any object is copied | test_metastore, test_admin |
| T-OPS-06 | FR-OP-09, UC-31 | against a fake Claude API, a finding leads to tool calls over stats and logs, and the analysis reaches the webhook beside the finding | test_superfan_agent |
| T-OPS-07 | FR-OP-10 | the agent's limits and failure paths: API errors with retries, a refusal, the turn and token limits, a repeated finding, a failing tool; no credential in any request log, prompt or post | test_superfan_agent |
| T-PERF-02 | FR-OP-11, NFR-17 | Scion against git serving the same repository: server CPU, peak memory and wall time per checkout, with working copies identical to the committed bytes (git's own checkout may be converted by .gitattributes) (a small repository in the suite; CPython in the pilot) | test_admin; `scion-admin bench --vs-git` |
| T-PILOT-01 | FR-MG-01…07, FR-SR-03, NFR-03, M4 | CPython ingested in order with every file verified against git; blame and the grep index computed with each import (12.9 decisions 8–9), so grep reads only candidate files; history, blame and ancestry served with no client; memory and per-operation cost tracked as history grows | examples/pilot.sh |
| T-IAM-15 | FR-IAM-03/04, ADR-20 | a read rule on the repository's root restricts every object it covers: the object index records it, and caches, daemons and snapshots never hold those objects | test_iam |
| T-IAM-16 | FR-IAM-09 | an object committed while a re-index runs keeps the entries its commit wrote | test_iam |
| T-AUD-02 | FR-IAM-10 | a denial is audited in the repository the request used, whether the method names it in the query or in the body | test_iam |
| T-RV-10 | FR-RV-05, ADR-09 | comments that tools read are code (a comment ending in a backslash, shebangs, coding lines, Go directives and cgo, Dockerfile parser directives); indentation in YAML, INI, Makefiles and Dockerfiles and whitespace in strings count; a file is docs by its format, never by its directory | test_antique |
| T-RV-11 | FR-RV-06, FR-IAM-04 | the approval rules see the files their readers can't (restricted directories, private repositories); an approval counts for a scope only from someone who can read all of it; conflicts under unreadable paths stay hidden | test_antique |
| T-RV-12 | FR-RV-02, BR-02 | approving or landing names the revision its actor saw: a replaced revision is refused, by RPC and on the pages; a revision arriving mid-landing stops the landing | test_antique |
| T-RV-13 | FR-RV-08 | a landed CR's page shows the diff of everything it landed | test_antique |
| T-RV-14 | FR-RV-09, FR-IAM-01 | removing or rotating a user's token ends their review-page sessions at the next request | test_antique |
| T-LD-06 | FR-LD-01/05, BR-06 | a CR that merged its target in is replayed, not fast-forwarded: the target's first-parent chain keeps every landing and the index holds only the CR's changesets; a merge whose first parent is the tip fast-forwards; landing onto a new ref indexes only its head | test_antique |
| T-LD-07 | FR-LD-03 | a request that fails with something other than a conflict fails alone: the rest of its batch lands, no thread is left waiting, and the CR can land again | test_antique |
| T-LD-08 | FR-LD-01/05/07 | the ref's compare-and-swap, the landing index, the post-merge job and the CR's new state commit as one transaction, or not at all | test_antique |
| T-LD-09 | FR-LD-01, FR-REF-03 | a target Antique may not move is refused before the CR changes state; a CR left `landing` by a stopped server can be landed or abandoned again | test_antique |
| T-LD-10 | FR-LD-01/03 | landing is idempotent: a land resent while the CR is landing (a client that timed out) waits for that landing and answers with it, so the change lands once and the resend succeeds (found by the 16 × 3 swarm on the Spanner emulator) | test_antique |
| T-PM-05 | FR-PM-04 | a revert that can't land (later work conflicts) leaves the job failed and the worker running | test_automation |
| T-PM-06 | FR-PM-04 | a failure on top of a base still being tested waits for the base's result, then is reverted | test_automation |
| T-MG-06 | FR-MG-01/04/05, FR-DD-09 | names holding a carriage return or a form feed survive storage and read back in another process; a commit's encoding header decodes its message; each run reports its own counts; blame counts lines as git does | test_ingest |
| T-MG-07 | FR-MG-01/04, FR-DD-06, FR-SR-03 | an import computes blame for every changeset it brings in and indexes its final revision, within its memory bounds, so the first queries derive nothing; `derive=False` leaves both to the first query | test_ingest |
| T-SR-03 | FR-SR-03, ADR-16 | the content index covers the revisions searched: a revision is indexed from the last one indexed in full (one changed file adds one blob), and a revision never searched adds nothing | test_search |
| T-SYS-03 | NFR-03 | no component materializes the repository: path queries read the same 27 objects at 500 and 10,000 files; a sparse checkout of 1 of 40 projects fetches 103 of 4,081 objects | test_system |
| T-PERF-01 | NFR-02/04/05/06, FR-OP-07 | benchmark invariants: constant tree writes per commit, O(log n) ancestry steps, a second clone with zero cache requests, a sparse checkout in under 10 s | test_admin; `scion-admin bench` |
| T-DOC-01 | 06 | all diagrams render (`mmdc`) | `scripts/check_docs.py --mmdc PATH` |
| T-DOC-02 | 03–05, 10, 11 | every requirement ID is defined once and traced; every test cited in 11 is planned in 10, every planned test exists in tests/ (a test whose requirements are all still planned for a milestone may wait for it), and every named test is planned; `--release` requires every requirement I or P and every test written | `scripts/check_docs.py` |

## 10.5 Entry and exit criteria

* **Entry (per work item):** the requirement is approved; the acceptance criterion is written; the test case is designed.
* **Exit (per work item):** the new test passes; the full suite passes; the stress simulation passes at 32×5; the docs check passes.
* **Release exit:** every Must requirement in scope has a passing automated test; no open defect of severity 1 or 2; benchmarks recorded.

## 10.6 Defect management

* **Severity:** 1 data loss or confidentiality breach; 2 wrong results in history, blame or merge, or landing failure; 3 degraded performance; 4 cosmetic.
* Every defect found by the fuzzer or the simulation gets a deterministic regression test (as
  the five found during the prototype did; see [../FEATURES.md](../FEATURES.md)).

## 10.7 Commands

```bash
python3 -m unittest discover -s tests                                   # full suite
SCION_FUZZ_SEEDS=40 python3 -m unittest discover -s tests -p test_fuzz.py   # deeper fuzzing
SCION_SIM_AGENTS=32 SCION_SIM_ROUNDS=5 python3 -m unittest discover -s tests -p test_simulation.py   # stress
./examples/demo.sh                                                      # end to end
python3 -m scion scion-admin bench                                      # performance
python3 scripts/check_docs.py --release [--mmdc PATH]                   # documentation checks
SCION_TEST_SPANNER=http://127.0.0.1:9020 python3 -m unittest discover -s tests   # the suite on the Spanner emulator
python3 -m scion scion-admin bench --vs-git PATH                         # Scion against git on one repository
PILOT_GIT=cpython.git examples/pilot.sh WORKDIR                          # the CPython pilot (T-PILOT-01)
```
