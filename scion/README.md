# Scion: agent-scale source control

> **Status: rebuilt through B4; B5 (system verification) remains.** The design baseline in
> [`docs/design/`](docs/design/00-process.md) was approved at M0 (2026-10-13). The earlier prototype was
> deleted by decision, and the system was rebuilt from the baseline in milestones: B1, the version control
> core; B2, the server API, the daemon → cache → server tiers with snapshots, the `scn` client (full,
> sparse and virtual checkouts), multiple repositories per deployment, and TLS with mutual TLS between
> tiers; B3, directory permissions enforced on every read path and tier, protected refs and release
> branches, a hash-chained audit log, and Antique: semantic review rules, review pages, webhooks and
> lock-free group-commit landing; and B4, git ingestion, post-merge testing with a deploy gate, bisect and
> revert pipelines, indexed grep, superfans reading telemetry and logs, benchmarks, and backup and restore.
> All 138 functional requirements are built and tested; B5 verifies the non-functional ones end to end.
> Progress is in [`docs/design/11-traceability.md`](docs/design/11-traceability.md).

A working implementation of the system described in Anthropic's engineering post
[*Redesigning source control at Anthropic*](https://www.anthropic.com/engineering/redesigning-source-control).
It includes the version control system (Scion), the code review and landing tool (Antique), code
search, directory-level IAM, the daemon → cache → server checkout architecture, and the
supporting tools the post mentions: git ingestion, automated bisect and revert, post-merge testing,
and "superfan" monitors.

It is pure Python 3.10+ with **no dependencies**. SQLite stands in for Spanner and a directory
stands in for cloud blob storage, each behind a narrow interface.

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
                                 ┌─────┴──────┐                       blob storage + metadata DB
                                 │scion-cache │  regional, in memory    (directory + SQLite here)
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
```

Running the pieces by hand:

```bash
export PYTHONPATH=$PWD
python3 -m scion scion-admin init --root /tmp/scion/dep
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
python3 -m scion scion-admin backup --root /tmp/scion/dep --out /backups/today     # while servers run
python3 -m scion scion-admin restore --backup /backups/today --root /tmp/scion/dep2 --deep
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
| `changeset.py`, `meta.py` | changesets, the write-ahead log, refs with compare-and-swap (the Spanner stand-in) |
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
| `postmerge.py`, `tools/` | post-merge worker, deploy gate, bisect, revert pipeline, benchmarks, development certificates |
| `superfan.py` | per-component watchers of telemetry and logs: adaptive baselines, threshold rules, webhooks |
| `backup.py` | consistent online backup, verified restore, and store verification |

## Measured here (4-core container)

These numbers come from the deleted prototype; the rebuild re-measures them in B5 (T-PERF-01).

| Benchmark | Result |
|---|---|
| One-file commit, repo of 100 / 1,000 / 10,000 files | 10.1 / 8.6 / 8.4 ms: the cost tracks the size of the change, not of the repo |
| `is_ancestor(root, tip)` over 3,001 linear changesets | 8 steps (0.11 ms) with skip lists vs 3,001 steps (4.5 ms) naive |
| 32 concurrent agents × 5 landings on 2 servers | all 160 landed, no lost updates, CAS-chained ref log |
| Second checkout on the same node | 0 requests to the cache: served by the node's daemon |

## Deliberate simplifications

* **Single-machine storage.** SQLite (WAL mode) and a directory replace Spanner and cloud
  storage. Several `scion-server` processes can share them on one host, and a cache can fail
  over between servers, but this is not a distributed database.
* **No kernel virtual filesystem.** Virtual checkouts materialize files on demand through
  `scn cat`, `scn materialize` and `WorkingCopy.read()`. There is no FUSE layer.
* **Superfans are watchers, not agents.** They read each component's telemetry and logs, learn
  adaptive baselines, and post findings with the surrounding log lines to stdout or a webhook. The
  article's superfans are Claude agents living in Slack; wiring an agent to the webhook is left to
  the deployment.
* **Heuristic comment detection.** The semantic classifier recognizes documentation-only and
  comment-only changes for common languages, and treats everything else, including anything
  it cannot parse, as logic.

The article itself says Scion "is by no means a suitable replacement for git for general use".
That applies here too. This code exists to make the design concrete, testable and measurable.
