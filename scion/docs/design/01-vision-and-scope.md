# 1. Vision and scope

## 1.1 Problem statement

Coding is no longer the bottleneck. AI agents write and merge code faster than infrastructure
built for human scale can absorb it. The article reports three pressures:

* **Merge rate.** It grew from about 2,500 to more than 30,000 changes per day in four months, with
  "practically infinite" latent demand. Every bottleneck removed raises the rate again
  (Article §Introduction).
* **Size.** The main branch's history is about 100 GB and a compressed working copy is more than
  25 GB (Article §Growing our monorepo).
* **Checkout volume.** CI alone performs about 25 million checkouts per day, which would be more
  than 600 PB per day of git traffic if fetched naively (Article §Growing our monorepo).

git's decentralized design gives every clone the full repository, with offline diff, history,
blame and checkout. Here it works against the workload, because nearly every client is an agent
or job that is always online. The workarounds were shallow, sparse and promisor clones, several
hundred mirrors, and snapshot "seeds". They grew harder to run as the merge rate rose, and the
mirrors stopped scaling once the repository outgrew their disks and memory.

## 1.2 Vision

> A source-control service designed for clients that are always online: the server owns history
> and computation, clients fetch only what they read, every component scales horizontally, and
> landing code needs no global lock.

## 1.3 Business goals

| ID | Goal | Measure of success |
|---|---|---|
| G-1 | Remove source control as the development bottleneck | sustain the landing rate with ≥10× headroom; landing latency does not grow with the landing rate |
| G-2 | Make checkouts cheap | most checkouts served from node- or region-local tiers (≥99% hit rate per tier in steady state); checkout in seconds, not minutes |
| G-3 | Shrink infrastructure | CPU and memory of the serving fleet far below that of the git mirror fleet (the article reports 200×) |
| G-4 | Answer source-control questions without a repository | CI jobs and tools get history, blame, ancestry, diffs and search through an API, with no clone |
| G-5 | Keep a monorepo safe | directory-level permissions enforced end to end; review attention goes to consequential changes |
| G-6 | Migrate without stopping work | incremental, verifiable ingestion from git while both systems run |
| G-7 | Operate with very few people | stateless tiers, no repository maintenance, per-component monitoring |

## 1.4 Scope

**In scope**

1. The version control core: changesets, refs, content-addressed storage, derived data.
2. Server-side queries and writes: history, blame, diff, ancestry, merge, rebase, revert.
3. The checkout architecture: daemon → cache → server, the want-only fetch protocol, snapshots.
4. The `scn` client: full, sparse and virtual working copies, filesystem monitoring.
5. IAM: repository and directory permissions, protected refs, authentication, rate limiting.
6. Antique: change requests, semantic approval rules, lock-free landing, landing index.
7. Post-merge and pre-deploy testing, automated bisect and revert.
8. Code search over paths and contents.
9. git ingestion: streaming, incremental and verified.
10. Observability: per-component health and stats, superfan monitors, alerts.

**Out of scope (Won't, this release)**

| Item | Why |
|---|---|
| Offline or peer-to-peer workflows | contradicts the core assumption (AS-01); git remains the tool for that |
| A general-purpose git replacement | the article says Scion "is by no means a suitable replacement for git for general use" |
| A distributed database implementation | the prototype uses a stand-in behind an interface (CON-02) |
| A kernel virtual filesystem (FUSE) | virtual checkouts materialize through the client; a VFS adapter is future work |
| LLM agents living in chat (the article's superfans) | we provide the telemetry watcher and the alert hook; the agent is a deployment concern |
| Public hosting or productization | the article explains why it is hard to offer Scion broadly |

## 1.5 Constraints

| ID | Constraint |
|---|---|
| CON-01 | Lives in this repository under `scion/`, in Python 3.10+ with the standard library only |
| CON-02 | Storage sits behind narrow interfaces: SQLite stands in for Spanner and a directory for blob storage |
| CON-03 | Must coexist with git during migration (git stays the source of truth until cut-over) |
| CON-04 | Linux is the reference platform (inotify filesystem monitoring) |
| CON-05 | Small team: designs must keep operations cheap (no repository maintenance, stateless tiers) |

## 1.6 Assumptions

| ID | Assumption | If false |
|---|---|---|
| AS-01 | Clients (agents, jobs, developers) are online whenever they work | an offline mode would be needed, and server-side computation would no longer suffice |
| AS-02 | Trunk-based development in a monorepo | long-lived branches would need first-class merge history and blame |
| AS-03 | Most traffic comes from automated clients | interfaces must be machine-friendly first (structured errors, idempotency) |
| AS-04 | History and blame along the main line (first parent) is what people need (Article footnote 1) | changesets would also have to record diffs against other parents |
| AS-05 | Content-addressed objects never change once stored | caching without invalidation would not be safe |

## 1.7 Success criteria for this project (the prototype)

1. Every **Must** requirement in [03](03-requirements.md) is implemented and passes its acceptance test.
2. The scaling claims that can be reproduced on one host are measured: commit cost is flat in
   repository size, ancestry is O(log n), and a second checkout on a node never reaches the cache.
3. A hermetic simulation of a swarm of concurrent agents lands every change with no lost updates.
4. A real git repository is ingested and verified byte for byte.
