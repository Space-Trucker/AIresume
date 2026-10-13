# Feature map: "Redesigning source control at Anthropic" → this implementation

Every claim in the article that describes *what the system does* is listed here with an ID,
and mapped to the code that implements it. Claims that are about Anthropic's organization,
scale numbers, or history (e.g. "30,000 merges per day") are context, not features, and are
listed at the end for completeness.

Legend: **Done** = implemented and covered by tests (`tests/`, 79 tests). **Partial** = implemented with a documented
simplification. **Out of scope** = cannot be reproduced in a repository (explained).

## 1. Principles

| ID | Article feature | Where | Status |
|----|-----------------|-------|--------|
| P1 | Clients are always online; client and protocol designed around an always-reachable server; clients fetch data only when they need it | `client.ObjectFetcher.fetch_stream`, `tiers.py` | Done |
| P2 | Client–server asymmetry: server answers history and blame, creates commits, performs merges and rebases | `repo.py` (`file_history`, `blame`, `create_changeset`, `merge`, `rebase`) | Done |
| P3 | Client keeps a *bounded* local object cache | `storage.BoundedFileObjectStore` (`WorkingCopy.local`); the daemon uses the same store node-wide | Done |
| P4 | Client lays out working copy files on disk | `client.WorkingCopy._write_file` | Done |
| P5 | Client monitors for filesystem changes | `fsmonitor.py` (inotify via ctypes, with a stat-scan fallback) | Done |
| P6 | Client gives an ergonomic way to work with the server | `cli.py` (`scn`) | Done |
| P7 | Every source-control query the client uses is also exposed via API, so jobs need no local repo | `server.py` RPC surface; `client.ServerApi` uses the same RPCs | Done |
| P8 | Novel applications on top of the API: automated bisect and revert pipelines | `tools/bisect.py` (API-only predicates), `tools/revert.py` (lands via `antique.land_changeset`) | Done |
| P9 | Horizontally scalable: data is distributed, every component scales independently | stateless `scion-server` processes over shared blob storage + metadata DB; caches can fan out to several servers | Partial (single-machine SQLite stands in for Spanner) |
| P10 | No fully materialized copy of the repo anywhere, even on the server | server stores changesets + content-addressed objects only; trees are derived on demand | Done |
| P11 | No packfiles, so no repository maintenance | `storage.FileObjectStore`: one compressed file per object; no gc/repack command exists | Done |
| P12 | Commits are cheap and incremental: cost scales with the size of the change, not the repo | `trees.apply_augmented` only rewrites trees on changed paths; all derived types are incremental | Done |
| P13 | Commits are lock-free; nothing to push, because commit, rebase and merge happen on the server | `repo.create_changeset` (idempotent insert keyed by content hash, no ref movement) | Done |
| P14 | Refs are discouraged except for main and release branches | refs are optional; changesets are addressable by id; `iam` protects refs | Done |
| P15 | The working copy is optional: a CI job can ask the server for the diff between a commit and its merge base | `repo.diff`, `ServerApi.diff(merge_base=True)` | Done |
| P16 | Writes can skip the checkout and work entirely through the API | `create_changeset` with `content_b64` (+ optional ref CAS); `scn api commit --file` | Done |
| P17 | Sparse checkouts that only contain requested directories | `client.SparseProfile` | Done |
| P18 | Virtualized checkouts that materialize files on demand; the client only pays for what it reads | `client.WorkingCopy` virtual mode (`scn cat`, `scn materialize`, `WorkingCopy.read`) | Partial (on-demand through the API/CLI; no kernel FUSE layer) |

## 2. Data structures

| ID | Article feature | Where | Status |
|----|-----------------|-------|--------|
| D1 | Unit of work is a "changeset", an entry in a write-ahead log | `meta.MetaStore.changesets` (append-only, sequence numbered) | Done |
| D2 | Changeset stores the list of files changed relative to its **first parent** (also for merges) | `changeset.Changeset.changes` | Done |
| D3 | Content-addressed pointers to compressed file contents in blob storage | `objects.py`, `storage.py` (zlib-compressed, sha256-addressed) | Done |
| D4 | Changesets are created server-side and are available everywhere, instantly | `repo.create_changeset` | Done |
| D5 | High-throughput acceptance: no packfiles, no locking or cross-server coordination, no refs moved | `create_changeset` | Done |
| D6 | Refs exist; moving one is a compare-and-swap on a single row, separate from creating changesets | `meta.MetaStore.cas_ref` | Done |
| D7 | Everything else is "derived data", computed through **one generic mechanism** | `derived.py` (`DerivedType`, `DerivedDataManager`) | Done |
| D8 | Each derived type is defined recursively from its values for the changeset's parents | `DerivedType.derive(repo, cs_id, cs, parent_values)` | Done |
| D9 | Derived structure: file blame | `derived_types.BlameType` | Done |
| D10 | Derived structure: path history | `derived_types.HistoryTreeType` (+ `repo.file_history`) | Done |
| D11 | Derived structure: skip lists for the commit graph | `derived_types.GraphType` (generation numbers + first-parent skip lists) | Done |
| D12 | Easy to add a new derived type | `DerivedDataManager.register`; see `docs/DERIVED_DATA.md` | Done |
| D13 | Per type: compute eagerly or defer | `DerivedType.eager`; `scion-admin derive` backfill | Done |
| D14 | Clients never see derived internals, so they can be optimized freely | only query APIs are exposed | Done |
| D15 | Derived index for copy detection | `derived_types.CopyInfoType` | Done |
| D16 | Derived index for path-based file search | `derived_types.SearchTreeType` (bloom-filtered trigram tree) | Done |
| D17 | Footnote: history and blame follow the main line (first parent) | `repo.file_history`, `BlameType` | Done |

## 3. Scaling and the checkout architecture

| ID | Article feature | Where | Status |
|----|-----------------|-------|--------|
| S1 | A small fleet of servers provides APIs: get changesets, compute diffs, find merge bases, fetch blobs | `server.py` | Done |
| S2 | All data is content-addressed and immutable, so any server can cache it without coordination | `repo.Repository` LRU caches; `tiers.CachingSource` | Done |
| S3 | Servers are essentially large caches that compute derived data on the fly and write it back to the metadata store | `DerivedDataManager.get` writes back with `INSERT OR IGNORE` | Done |
| S4 | "Metadata-only" mode: answering metadata queries for repos before having a client and protocol | `ingest.py` + server API usable without any `scn` client | Done |
| S5 | `scn` negotiation does **not** say what the client has; it asks only for the objects it wants | `client.WorkingCopy._collect_files` + `ObjectFetcher.fetch_stream` | Done |
| S6 | Start from the root tree, check the local store for missing trees, request them recursively, then do the same for blobs | `_collect_files` (breadth-first, one round trip per level) | Done |
| S7 | Every request is for a specific immutable object, so any cache can answer it | `get_objects` RPC | Done |
| S8 | Efficient and resumable: no single multi-gigabyte packfile response | batched requests; objects persisted as they arrive | Done |
| S9 | Sparse and virtual checkouts need no special protocol support | the client simply doesn't request unwanted trees | Done |
| S10 | `scion-daemon`: talks to clients over a socket and stores objects for the whole node | `tiers.DaemonService`, `scion-daemon` (Unix socket) | Done |
| S11 | The daemon starts from a periodically refreshed snapshot | `snapshot.py`; `DaemonService.refresh_snapshot` + refresh thread | Done |
| S12 | The daemon talks only to regional `scion-cache` servers | `scion-daemon --upstream`; tier enforcement | Done |
| S13 | Caches stream objects from memory in the daemon's on-disk format, with no missing-object computation or delta compression | compressed bytes are passed through verbatim | Done |
| S14 | Cache misses go to the authoritative `scion-server`, which reads from the metadata store and cloud storage | `CachingSource` → `RemoteSource` → `Repository.fetch_objects` | Done |
| S15 | daemon, cache and server answer **identical RPCs**, so the client doesn't know the topology | shared `get_objects` handler (`rpc.py`) | Done |
| S16 | Tiering is strictly enforced to isolate failure domains | `X-Scion-Tier` header + `allowed_callers` per tier | Done |
| S17 | Cache hit rate is observable (the article reports more than 99%) and tiers hold no long-lived state | `/stats` on every tier; caches are in-memory | Done |
| S18 | No repository maintenance for clients or caches | there is no gc/repack anywhere; the bounded cache evicts by LRU | Done |

## 4. "What we learned" items that describe system features

| ID | Article feature | Where | Status |
|----|-----------------|-------|--------|
| L1 | git-to-Scion ingestion pipeline that preserves ordering invariants with low memory | `ingest.py` (streaming, topological, incremental, `--verify`) | Done |
| L2 | Look up when a change merged to main through the code review tool, not by scanning the log | `antique.Antique.find_landing` (indexed table) | Done |
| L3 | Hermetic simulations of infrastructure and source-control interactions | `tests/test_simulation.py` (in-process server, cache, daemon, concurrent agents) | Done |
| L4 | Fuzzing | `tests/test_fuzz.py` (random histories checked against a naive model) | Done |
| L5 | Sophisticated rate limiting | `ratelimit.py` (per-principal token buckets by request class + concurrency caps) | Done |
| L6 | Algorithmic optimization of ancestry queries using an index | `GraphType` skip lists + generation pruning; `tools/bench.py` | Done |
| L7 | Rich access control on repositories | `iam.Policy` (repo-level read/write, groups, admins) | Done |
| L8 | Permissions on individual directories, enforced end to end (including the object protocol and caches) | `iam.Policy.paths`, `object_acl`, restricted objects never cached by tiers | Done |
| L9 | Code review that expresses semantic constraints on approvals (comment-only vs logic changes) | `antique.py` + `classify.py` | Done |
| L10 | Code review surface (Antique) | `antique.py` (RPC) + read-only HTML at `/antique` | Done |
| L11 | Code search | `search.py` (path search over the derived index, server-side grep) | Done |
| L12 | Novel ways of landing large amounts of reviewed code: no global merge-queue lock | `Antique.land`: server-side rebase + one ref CAS, per-server group commit, jittered retry | Done |
| L13 | Post-merge and pre-deploy automated testing instead of a merge queue | `postmerge.py` (worker, auto-revert, deploy gate) | Done |
| L14 | Concurrent changes can conflict and get fixed quickly | `land` returns structured 409 conflicts and marks the CR; `scn rebase` + `review update` | Done |
| L15 | "Superfans": per-component monitors that watch telemetry and flag subtle, novel issues | `superfan.py` (adaptive baselines per metric, per component) | Partial (statistical watcher; the LLM agent in Slack is out of scope) |
| L16 | Traditional alerts alongside superfans | `superfan.py` static thresholds | Done |

## 5. "Contributing to the ecosystem" ideas

| ID | Idea | Where | Status |
|----|------|-------|--------|
| E1 | A server need not work like the client | the server is a different program from `scn` | Done |
| E2 | Comprehensive server-side RPCs, possibly standardized | `docs/API.md` | Done |
| E3 | A different negotiation protocol | want-only object protocol (S5–S7) | Done |
| E4 | Sparse and shallow features that compose well | sparse + virtual + no-history clones are the default, and all compose | Done |

## 6. Context, not features

These describe Anthropic's situation and are not reproducible as code: merges per day (2,500 → 30,000),
100 GB of history and a 25 GB working copy, 25 million checkouts per day, roughly 600 PB per day of
naive git traffic, several hundred git mirrors, a 200x smaller footprint, checkouts two orders of
magnitude faster, a 25% CPU saving in CI, a seven-person team, five months, the Claude Mythos
Preview rewrite (20x less memory, 4x faster), and Claude Tag. Spanner is replaced by SQLite (WAL
mode) and cloud storage by a directory. Both sit behind narrow interfaces (`meta.py`, `storage.py`),
so they can be swapped.

## Bugs the fuzzer and the stress simulation found while building this

The article credits fuzzing and hermetic simulations for Scion's quality. They earned their keep here too:

1. `file_history` crossed a file↔directory change at the same path and reported the directory's history (fuzzer).
2. A three-way merge read a base *directory* as a blob when both sides had replaced it with files (fuzzer).
3. Identical bytes at a public path and a restricted path in the same changeset were wrongly hidden from readers of the public path (IAM tests).
4. 32 agents × 5 landings on 2 servers starved some optimistic landers. Fixed with per-server group commit plus jittered backoff, still with no repository lock (swarm simulation).
5. `scn add` outside a sparse profile produced an empty commit (end-to-end demo).
