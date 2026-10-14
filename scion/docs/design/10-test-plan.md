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
| Integration | server + cache + daemon(s) in-process over real sockets | the hermetic `Cluster` helper | `tests/test_tiers.py`, `tests/test_iam.py`, `tests/test_client.py`, `tests/test_antique.py`, `tests/test_ops.py` |
| Simulation / stress | swarm of agents doing clone, commit, review and land concurrently on 2 servers | `SCION_SIM_AGENTS`, `SCION_SIM_ROUNDS` | `tests/test_simulation.py` |
| Migration | real git repositories with branches, merges, renames, modes, symlinks, file↔directory swaps | `git` CLI in a temp directory | `tests/test_ingest.py` |
| System / E2E | separate processes: server, cache, daemon (Unix socket), CLI | shell script | `examples/demo.sh` |
| Performance | commit scaling, ancestry, tiered checkout | `scion-admin bench` | `scion/tools/bench.py` |
| Documentation | every Mermaid diagram renders; every requirement ID is traced | `mmdc` render check; ID cross-check script | T-DOC-01, T-DOC-02 |

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
| T-PM-01 | FR-PM-01…05, FR-LD-06/07, FR-AUT-02 | post-merge worker, auto-revert, deploy gate | test_antique |
| T-SIM-01 | FR-LD-02/03, FR-REF-04, FR-CS-05/06, NFR-01 | swarm of agents on 2 servers; no lost updates; CAS-chained ref log | test_simulation |
| T-MG-01 | FR-MG-01/03/05/07 | ingest, verify, incremental | test_ingest |
| T-MG-02 | FR-MG-01, FR-DD-09 | blame parity with `git blame` | test_ingest |
| T-MG-03 | FR-MG-02 | ordering invariant | test_ingest |
| T-OPS-01 | FR-OP-06 | token bucket, concurrency, 429 plus client backoff | test_ops |
| T-OPS-02 | FR-OP-03/04 | superfan novel and threshold findings; unreachable | test_ops |
| T-SR-01 | FR-SR-01/02, FR-DD-12 | bloom pruning; grep | test_ops |
| T-AUT-01 | FR-AUT-01 | bisect without checkout | test_ops |
| T-AUT-02 | FR-AUT-02, FR-LD-06 | revert pipeline under contention | test_ops |
| T-CORE-10 | FR-CS-09, NFR-05 | one-file commit time is flat (±25%) across 10² and 10⁴ files (asserted) | test_core |
| T-DD-07 | FR-DD-06 | backfilling a deferred type computes it for a revision and all ancestors | test_core |
| T-DD-08 | BR-06 | history and blame follow the first parent only; merge-introduced lines belong to the merge | test_core |
| T-MR-01 | FR-IAM-02, ADR-13 | two repositories with different policies on one deployment; caches key by repository; a private repository's objects are never cached | test_multirepo |
| T-TLS-01 | NFR-20, ADR-14 | TLS on every TCP hop; mutual TLS identifies tiers; plaintext and wrong certificates are refused | test_tls |
| T-LIM-01 | FR-WR-07 | an oversized upload gets 413 and stores nothing | test_ops |
| T-CL-13 | FR-FP-03 | an interrupted clone resumes in place and reuses received objects | test_client |
| T-IAM-09 | FR-IAM-01 | repository-level read restriction, through the API and through the caches | test_iam |
| T-IAM-10 | FR-IAM-09 | re-indexing ACLs after a policy change restricts existing objects | test_iam |
| T-AUD-01 | FR-IAM-10, ADR-15 | policy loads, denials and admin actions are audited; the hash chain verifies and detects tampering | test_iam |
| T-REF-01 | FR-REF-05 | release branches: created by the release role only, moved by CAS, logged | test_iam |
| T-ADM-01 | FR-AD-05 | admin ref operations run as an explicit identity and respect protections | test_ops |
| T-BAK-01 | FR-AD-06, NFR-13 | backup then restore reproduces refs, changesets and objects | test_ops |
| T-RV-07 | FR-RV-09, ADR-17 | approve, comment (inline) and land from the web UI; CSRF enforced | test_antique |
| T-RV-08 | FR-RV-10 | CR events reach a notification webhook | test_antique |
| T-LD-03 | FR-LD-01, D-02 | a CR shows `landing` while queued | test_antique |
| T-PM-02 | FR-PM-01, D-01 | concurrent workers claim every job exactly once | test_antique |
| T-SR-02 | FR-SR-03, ADR-16 | indexed content search reads only candidate blobs and matches a full scan | test_ops |
| T-OPS-03 | FR-OP-05 | superfan findings are delivered to a webhook | test_ops |
| T-OPS-04 | FR-OP-08, ADR-18 | superfans read component logs and attach them to findings | test_ops |
| T-MG-04 | FR-MG-04 | ingestion memory stays flat as history grows | test_ingest |
| T-E2E-01 | system | multi-process demo including git ingestion | examples/demo.sh |
| T-PERF-01 | NFR-05/06, FR-OP-07 | benchmarks | scion-admin bench |
| T-DOC-01 | 06 | all diagrams render (`mmdc`) | doc check: run for this baseline; the script is committed with WP-03 after M0 |
| T-DOC-02 | 03–05, 10, 11 | every requirement ID is defined once and traced; coverage counts in 11.3 | doc check: run for this baseline; the script is committed with WP-03 after M0 |

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
SCION_FUZZ_SEEDS=40 python3 -m unittest tests/test_fuzz.py              # deeper fuzzing
SCION_SIM_AGENTS=32 SCION_SIM_ROUNDS=5 python3 -m unittest tests/test_simulation.py   # stress
./examples/demo.sh                                                      # end to end
python3 -m scion scion-admin bench                                      # performance
```
