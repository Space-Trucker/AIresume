# Scion: agent-scale source control

> **Status: built and verified (B1–B5); B6 in progress.** The design baseline in [`docs/design/`](docs/design/00-process.md)
> was approved at M0 (2026-10-13). The earlier prototype was deleted by decision, and the system was rebuilt
> from the baseline in milestones: B1, the version control core; B2, the server API, the daemon → cache →
> server tiers with snapshots, the `scn` client (full, sparse and virtual checkouts), multiple repositories
> per deployment, and TLS with mutual TLS between tiers; B3, directory permissions enforced on every read
> path and tier, protected refs and release branches, a hash-chained audit log, and Antique: semantic review
> rules, review pages, webhooks and lock-free group-commit landing; B4, git ingestion, post-merge testing
> with a deploy gate, bisect and revert pipelines, indexed grep, superfans reading telemetry and logs,
> benchmarks, and backup and restore; and B5, system verification of the non-functional requirements.
> B6 (decided 2026-10-14) runs it as Anthropic does: metadata in Cloud Spanner, superfans that are Claude
> agents, a comparison with git on the same repository, and a migration pilot on CPython's full history.
> Status per requirement: [`docs/design/11-traceability.md`](docs/design/11-traceability.md).

A working implementation of the system described in Anthropic's engineering post
[*Redesigning source control at Anthropic*](https://www.anthropic.com/engineering/redesigning-source-control).
It includes the version control system (Scion), the code review and landing tool (Antique), code
search, directory-level IAM, the daemon → cache → server checkout architecture, and the
supporting tools the post mentions: git ingestion, automated bisect and revert, post-merge testing,
and "superfan" monitors.

It is pure Python 3.10+ with **no dependencies**. The metadata (changesets, refs, derived data, reviews,
queues, audit) lives in **Cloud Spanner**, reached through its REST API, or in SQLite on one host: the
deployment's configuration chooses, and the Spanner backend is tested against Google's Spanner emulator.
File contents live in a directory, standing in for cloud blob storage.

Every feature in the article is mapped to code in [`docs/FEATURES.md`](docs/FEATURES.md).

**Design baseline:** [`docs/design/`](docs/design/00-process.md) holds the full pre-code package:
vision, stakeholders, requirements, feature list, use cases, UML, architecture and ADRs, threat
model, risks, test plan, traceability with gap analysis, project plan, and glossary. Code changes
follow its gap list.

## How it works

```
                       ┌──────────────────────────── scion-server (×N, stateless) ─────────────┐
 scn / CI jobs / tools │ changesets (write-ahead log) · derived data · merge/rebase/revert     │
 ──── metadata RPCs ──▶│ history · blame · diff · merge-base · search · IAM · Antique          │
                       └───────────────┬────────────────────────────────────┬──────────────────┘
                                       │ get_objects (identical RPC)        │
                                 ┌─────┴──────┐                     objects (a directory) + metadata
                                 │scion-cache │  regional, in memory    (Cloud Spanner, or SQLite)
                                 └─────┬──────┘
                                       │ get_objects
                                 ┌─────┴───────┐   one per node, bounded disk store,
 scn ── unix socket ──────────▶  │scion-daemon │   starts from a periodically refreshed snapshot
                                 └─────────────┘
```

* **Changesets, not commits.** A changeset lists the files that changed relative to its
  *first parent*, with content-addressed pointers to compressed blobs. Creating one is an
  idempotent append to the log: no locks, no packfiles, and no refs to move. Refs are optional,
  and each one is moved by a compare-and-swap on a single row.
* **Derived data.** Root trees, history trees, commit-graph skip lists, copy detection, search
  indexes and blame are all built through one recursive mechanism (`derived.py`). Each type is
  computed eagerly or deferred, and is always incremental: a commit costs the same in a
  100-file repo as in a 10,000-file one.
* **The server does the thinking.** History, blame, diffs, merge bases, merges, rebases and
  reverts all happen on the server and are exposed as RPCs, so CI jobs and tools need no checkout.
* **Want-only fetching.** The client never tells the server what it already has. Starting from
  the root tree, it asks for the missing trees level by level, then for the missing blobs. Every
  request names immutable objects, so any tier can answer it. That is why sparse and virtual
  checkouts need no special protocol.
* **Strict tiering.** daemon, cache and server answer the same `get_objects` RPC, but each tier
  serves only the tier directly below it. Objects under read-restricted directories are never
  cached and are re-authorized at the server for every user.
* **Landing without a merge queue.** Antique rebases a reviewed change onto the tip on the server
  and publishes it with a compare-and-swap. Each server group-commits concurrent landings into a
  single CAS, and testing happens post-merge, with automatic revert, plus a pre-deploy gate.

## Quick start

```bash
cd scion
python3 -m unittest discover -s tests   # the full suite: core, fuzzing, tiers, client, TLS, IAM, review,
                                        # landing, ingestion, automation, search, superfans, admin
SCION_SIM_AGENTS=32 SCION_SIM_ROUNDS=5 python3 -m unittest discover -s tests -p test_simulation.py   # stress
python3 -m scion scion-admin bench      # benchmarks (--quick for small sizes, --json for numbers)
python3 -m scion scion-admin bench --vs-git ~/src/project   # checkouts against git serving the same repository
examples/pilot.sh /data/pilot           # the migration pilot: CPython's history, verified and measured
```

The same suite runs with the metadata on Spanner, through Google's emulator (`gcloud emulators spanner
start`, or its `gateway_main`; the REST port is 9020 by default). Every cluster and repository the tests
make gets a database of its own:

```bash
SCION_TEST_SPANNER=http://127.0.0.1:9020 python3 -m unittest discover -s tests
```

Running the pieces by hand:

```bash
export PYTHONPATH=$PWD
python3 -m scion scion-admin init --root /tmp/scion/dep   # metadata in SQLite; for Spanner add, for example,
#   --metadata '{"backend": "spanner", "project": "p", "instance": "i", "database": "scion", "create": true}'
#   ("endpoint": "http://127.0.0.1:9020" for the emulator; a "token_command" or the GCE metadata server otherwise)
python3 -m scion scion-admin create-repo --root /tmp/scion/dep monorepo        # --read/--write to restrict it
python3 -m scion scion-server --root /tmp/scion/dep --listen 127.0.0.1:7070 &
python3 -m scion scion-cache  --listen 127.0.0.1:7080 --upstream http://127.0.0.1:7070 &
python3 -m scion scion-daemon --socket /tmp/scion/d.sock --store /tmp/scion/node --upstream http://127.0.0.1:7080 &

scn="python3 -m scion scn --server http://127.0.0.1:7070 --repo monorepo --user me"
$scn api commit -m "first" --file src/x.py=scion/__init__.py --ref main   # a write without any checkout
$scn clone wc --objects unix:/tmp/scion/d.sock --sparse src
cd wc && echo hi >> src/x.py
python3 -m scion scn commit -m "change"        # created on the server; there is nothing to push
python3 -m scion scn review create --title "change"
python3 -m scion scn --server http://127.0.0.1:7070 --repo monorepo --user you review approve 1
python3 -m scion scn review land 1                # rebased onto main and published with one compare-and-swap
```

The review pages are at `http://127.0.0.1:7070/antique`. Directory permissions, protected refs, review
rules and webhooks go in `repos/<name>/policy.json`; principals, groups and tokens in `deployment.json`
(see `iam.py` and `antique.py`). After tightening a policy, run `scion-admin reindex-acl`.

For production-like transport, give every TCP hop TLS and the tiers client certificates (ADR-14):
`scion-admin gen-certs DIR` makes a development CA and certificates (it needs the `openssl` tool);
servers and caches take `--tls-cert/--tls-key/--client-ca`, caches and daemons take `--ca/--cert/--key`
for their upstreams, and users authenticate with tokens from `deployment.json` (`scion-admin hash-token`).
`scion-admin snapshot` publishes daemon snapshots, and `scion-daemon --snapshots DIR` warm-starts from them.

Operations and automation:

```bash
python3 -m scion scion-admin ingest --root /tmp/scion/dep --repo monorepo --git ~/src/project --rev main --verify
python3 -m scion scion-postmerge --server http://127.0.0.1:7070 --repo monorepo --workdir /tmp/pm \
    --objects unix:/tmp/scion/d.sock --cmd "python3 -m pytest -q" --auto-revert      # post-merge testing
python3 -m scion scion-superfan --url unix:/tmp/scion/d.sock --profile daemon --webhook https://chat/hook
python3 -m scion scion-superfan --url http://127.0.0.1:7070 --profile antique --rule "land_queue_depth > 50 for 3"
ANTHROPIC_API_KEY=... python3 -m scion scion-superfan --url http://127.0.0.1:7080 --profile cache \
    --webhook https://chat/hook --agent       # Claude investigates each finding and posts its analysis
python3 -m scion scion-admin backup --root /tmp/scion/dep --out /backups/today     # while servers run
python3 -m scion scion-admin restore --backup /backups/today --root /tmp/scion/dep2 --deep \
    --metadata '{"backend": "sqlite"}'          # optional: restore into another backend
```

After `pip install -e .`, the console scripts `scn`, `scion-server`, `scion-cache`, `scion-daemon`,
`scion-admin`, `scion-postmerge` and `scion-superfan` are available directly.

### `scn` commands

| | |
|---|---|
| working copy | `clone [--sparse dirs] [--virtual]`, `status`, `add`, `rm`, `restore`, `diff`, `commit`, `update`, `rebase`, `stack`, `sparse show/add/remove`, `materialize`, `watch start/stop` (inotify fsmonitor) |
| server queries | `log [path]`, `show`, `blame`, `history`, `cat`, `ls`, `search`, `grep [-i] [-F] PATTERN [PATH]`, `merge-base`, `diff -r A -r B [--merge-base]` |
| repository | `repos`, `whoami`, `refs`, `ref-log NAME`, `is-ancestor A B`, `release create NAME`, `audit [--verify]` |
| review | `review create/update/list/show/approve/comment/requirements/land/abandon/landing` |
| automation | `api <method> k=v ...` (any RPC), `api commit --file PATH=LOCAL` (write without a checkout), `revert CS [--land]`, `bisect --good G --bad B (--bad-if PATH:REGEX \| --good-if PATH:REGEX \| --cmd CMD)`, `gate [--ref]` (the deploy gate) |

## Layout

| Module | What it is |
|---|---|
| `objects.py`, `storage.py` | content-addressed, zlib-compressed objects; no packfiles; bounded LRU stores |
| `changeset.py`, `meta.py`, `spanner.py` | changesets; the metadata store's contract and its SQLite and Cloud Spanner (REST) implementations: the write-ahead log, refs by compare-and-swap, reviews, queues, audit |
| `trees.py` | incremental tree updates and subtree-skipping diffs |
| `derived.py`, `derived_types.py` | the generic derived-data mechanism and its six types |
| `repo.py` | server-side history, blame, ancestry, merge, rebase, revert |
| `merge3.py` | line-based three-way merge |
| `iam.py`, `ratelimit.py` | principals, tokens, repository and directory permissions, protected refs; rate limiting |
| `deployment.py` | one deployment hosting many repositories, each with its own policy |
| `rpc.py`, `server.py`, `tiers.py`, `snapshot.py` | the RPC layer (TLS, mutual TLS, failover), scion-server, scion-cache, scion-daemon, snapshots |
| `client.py`, `fsmonitor.py`, `cli.py` | `scn`: working copies (full, sparse, virtual), the inotify monitor, the CLI |
| `antique.py`, `classify.py` | code review with semantic approval rules, lock-free landing, landing index |
| `audit.py`, `notify.py`, `ui.py` | the hash-chained audit log, webhooks, and the review pages |
| `search.py` | path search over bloom-filtered search trees; server-side grep |
| `ingest.py` | streaming, incremental, verified git → Scion ingestion |
| `postmerge.py`, `tools/` | post-merge worker, deploy gate, bisect, revert pipeline, benchmarks (also against git), the migration pilot, development certificates |
| `superfan.py`, `superfan_agent.py` | per-component watchers of telemetry and logs (adaptive baselines, threshold rules, webhooks), and the Claude agent that investigates each finding |
| `backup.py` | consistent online backup, verified restore, and store verification |

## Measured here (4-core container)

Measured on the rebuild at B5 (`scion-admin bench`, the tests named, and `examples/demo.sh`). Servers,
caches and daemons run in one process for the benchmarks, so absolute times include their contention;
the end-to-end demo runs each in its own process. B6 then measured a real history, CPython's, and
compared Scion with git serving it (below).

| Benchmark | Result |
|---|---|
| One-file commit, repository of 100 / 1,000 / 10,000 files | 4.0 / 4.1 / 5.0 ms on disk; 1.8 / 1.8 / 2.1 ms with objects in memory; 3 trees written at every size. The cost tracks the change, not the repository (T-CORE-10, T-PERF-01) |
| Ancestry on a 10,000-changeset line | `is_ancestor(root, tip)` in 9 steps (0.13 ms), `merge_base` in 19, against 10,000 for a naive walk |
| 32 agents × 5 landings on 2 servers | all 160 landed at 21.7 landings/s with 32 ref moves (group commit); median time to land 0.33 s (T-SIM-01) |
| 64 agents × 10 landings on 2 servers | all 640 landed at 20.9 landings/s with 61 ref moves |
| Hit rates in steady state | 99.5% at a node serving 100 jobs; 99.0% at a cache behind 100 nodes, cold start included (T-SYS-01) |
| Checkout of 5,000 files through daemon → cache → server | cold 7.5 s; a second clone on the node 4.7 s with 0 cache requests; a sparse checkout of one 250-file project 0.22 s |
| Path queries at 500 and at 10,000 files | the same 27 object reads for read, list, history, blame and diff of one path (T-SYS-03) |
| Footprint | server, cache and daemon each 26–28 MB resident after the end-to-end demo |

### The CPython pilot (B6, M4; `examples/pilot.sh`, T-PILOT-01)

CPython's history was ingested in order, with checkpoints evenly spaced along its main line. At every
checkpoint each file was compared with git's, and a `scion-server` process served the history to a
client with no checkout. It reached 123,515 of CPython's 133,611 commits (92%): stopped at the seventh
checkpoint by a 20 GB disk budget, it was compared with git there (below), then resumed with a 24 GB
budget until the next checkpoint would not fit (checkpoints 8–9 ran under a restarted server). Blame and
the grep index of each checkpoint's revision were computed during the import (12 §12.9 decisions 8–9)
and are timed apart from ingestion.

| Checkpoint | Commits | Ingested per second | Blame, during import | Grep index, during import | Objects | Metadata | Peak memory: ingestion / server |
|---|---|---|---|---|---|---|---|
| 1 | 9,798 | 120 | 61 s | 109 s, 2,037 files | 0.60 GB | 0.28 GB | 131 / 33 MB |
| 2 | 19,597 | 91 | 62 s | 162 s, 2,237 files | 1.35 GB | 0.59 GB | 131 / 36 MB |
| 3 | 29,395 | 76 | 101 s | 207 s, 2,333 files | 2.31 GB | 0.94 GB | 133 / 39 MB |
| 4 | 39,194 | 52 | 193 s | 278 s, 3,071 files | 3.74 GB | 1.41 GB | 152 / 42 MB |
| 5 | 54,438 | 50 | 299 s | 309 s, 2,938 files | 6.14 GB | 1.91 GB | 152 / 63 MB |
| 6 | 89,740 | 50 | 686 s | 328 s, 2,805 files | 12.09 GB | 2.55 GB | 152 / 63 MB |
| 7 | 103,812 | 41 | 312 s | 348 s, 2,819 files | 15.10 GB | 3.07 GB | 152 / 69 MB |
| 8 | 113,650 | 36 | 315 s | 415 s, 3,251 files | 17.29 GB | 3.62 GB | 157 / 58 MB |
| 9 | 123,515 | 34 | 323 s | 458 s, 3,669 files | 19.61 GB | 4.23 GB | 160 / 66 MB |

Every checkpoint matched git file for file (5,369 files at the last). Queries through the server, as
CI makes them with no checkout, at the first and the last checkpoint (median of repeated calls):

| Query | 9,798 commits | 123,515 commits |
|---|---|---|
| log, 50 entries | 1.3 ms | 2.3 ms |
| `is_ancestor(first commit, tip)` | 0.6 ms, 6 steps | 1.2 ms, 9 steps |
| main-line ancestor halfway back | 0.6 ms | 1.0 ms |
| git sha → changeset | 0.6 ms | 0.8 ms |
| read `Python/ceval.c` | 2.1 ms | 5.7 ms |
| history of `Python/ceval.c` | 1.1 ms | 1.5 ms |
| blame of `Python/ceval.c` | 15 ms | 18 ms |
| grep for a literal | 67 ms, 240 files read for 245 matches | 452 ms, 16 files read for 13 matches |

What the pilot found:
* **Blame on demand was too slow for a migration.** Before the import computed it, the first blame of
  `Python/ceval.c` took 53 s at the first checkpoint and 247 s at the fifth; now 17–108 ms on the first
  call (108 ms on a server just restarted) and 15–42 ms after (decision 8).
  Its line diffs had been quadratic (ADR-27), and ancestry cost a step per merge (ADR-12): both fixed.
* **Grep's cost grows with the index, not the tree.** The index holds the files of every revision
  searched (about 25,000 file versions after 9 checkpoints), and a query fetches the postings of all
  its trigrams: at the seventh checkpoint, 130 ms of 264. Reading and matching the 15 candidate files
  took about 90 ms.
* **Indexing slows as SQLite's index grows**, from 53 to 125 ms per file: postings are keyed by trigram,
  so each file's land all over the B-tree.
* **Memory stays flat:** ingestion at 131–160 MB and the server at 33–69 MB as the history grew ×12.6.
* **Storage:** about 170 KB of objects per commit (the file versions, their trees, the history and
  search trees, and blame runs), plus 37 KB of metadata. Four fifths of the metadata is the grep index:
  3.4 GB for the 42.6 million postings of 25,160 file versions, about 80 bytes each in SQLite. At that
  rate an index of every version in the history (decision 9) would have taken about 95 GB.
* **A reconnect cost 100 ms.** The first query after checkpoints 2–7 took 106 ms: the server closes
  connections idle for 5 minutes, and the client waited before reconnecting as if the server were down.
  It now reconnects at once (T-OPS-01); checkpoints 8–9 ran with the fix.

### Against git on CPython (B6; `scion-admin bench --vs-git`, T-PERF-02)

The same history, CPython at the pilot's seventh checkpoint (103,812 commits, 4,111 files), served on
this host both ways (ADR-26): by git's `upload-pack` from a repository repacked with bitmaps, as a git
server keeps it, and by Scion's server, cache and daemon from the pilot's deployment. Server CPU counts
upload-pack and the processes it starts, against Scion's server and cache. Both of Scion's working copies
were identical to the committed bytes; git's own checkout converted 135 files (`.gitattributes`).

| | git | Scion |
|---|---|---|
| Checkout, wall time | full clone 36.2 s (second 39.2 s); shallow clone 4.0 s | cold node 5.2 s; warm node 4.2 s, with 0 cache requests |
| Server CPU per checkout | full clone 1.6 s; shallow clone 4.6 s | cold node 1.6 s (server 1.35, cache 0.28); warm node 0.01 s |
| Peak memory | 270 MB for each upload-pack, so for each clone at once | server 90 MB, cache 95 MB, daemon 154 MB, shared by every checkout |
| What the serving tier holds | the whole history, 270 MB packed | the checkout's 4,329 objects, 23.5 MB in the cache |

So, on one repository and one host: a full clone costs git's server as much CPU as Scion's first checkout
on a node (git sends the pack it keeps, which bitmaps make cheap), and a shallow clone 2.8 times as much
(git computes a new pack). Later checkouts on a node cost Scion's servers almost nothing (0.01 s),
while every git clone costs a server again. Scion's checkout is 7 to 8.6 times faster than a full clone
and a little slower than a shallow one (4.2–5.2 s against 4.0 s): its time goes to writing the files,
not to the history. The article's ratios (servers "200x smaller",
checkouts "two orders of magnitude faster") are for Anthropic's monorepo and fleet; here the history is
a 270 MB pack, and a full clone's cost grows with the history while Scion's grows with the checkout.

## Deliberate simplifications

* **Objects in a directory.** File contents and trees live in a directory shared by the servers,
  standing in for cloud blob storage (decided 2026-10-14). The metadata can be in Cloud Spanner; it is
  developed and tested against Google's emulator, so real Spanner is configuration, not yet a measured
  deployment.
* **No kernel virtual filesystem.** Virtual checkouts materialize files on demand through
  `scn cat`, `scn materialize` and `WorkingCopy.read()`. There is no FUSE layer.
* **The superfan agent needs an API key.** With `--agent`, Claude investigates each finding with
  read-only tools and posts its analysis under it. The agent is tested against a fake Messages API;
  running it for real needs `ANTHROPIC_API_KEY` and network access to the API.
* **Heuristic comment detection.** The semantic classifier recognizes documentation-only and
  comment-only changes for common languages, and treats everything else, including anything
  it cannot parse, as logic.

The article itself says Scion "is by no means a suitable replacement for git for general use".
That applies here too. This code exists to make the design concrete, testable and measurable.
