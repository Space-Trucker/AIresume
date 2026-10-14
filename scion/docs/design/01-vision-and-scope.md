# 1. Vision and scope

## 1.1 Problem statement

Coding is no longer the bottleneck. AI agents write and merge code faster than infrastructure
built for human scale can absorb it. The article reports three pressures:

* **Merge rate.** Merges per day grew more than tenfold, and source control became the biggest
  development bottleneck. The rate went from around 2,500 code changes per day in May 2026 to over
  30,000 per day as of September, and the latent demand is "practically infinite". Every
  bottleneck removed immediately raises the rate again (Article §Opening).
* **Size.** The main branch's history alone is almost 100 GB, and a compressed working copy is
  over 25 GB (Article §Growing our monorepo).
* **Checkout volume.** CI alone performs on the order of 25 million checkouts per day, before
  counting developer environments, agent sandboxes and research jobs. Fetched naively, that would
  be over 600 PB of git traffic per day (Article §Growing our monorepo).

git's decentralized design gives every clone the full repository, with offline diff, history,
blame and checkout. Here it works against the workload, because nearly every client is an agent
or job that is always online. git's own tools for working with a slice of a repository are
shallow clones, sparse checkouts and promisor remotes. Beyond those, the standard workarounds for
large monorepos are internal git mirrors and repository snapshots ("seeds") kept in blob storage.
Anthropic used all of them, with several hundred mirrors at the peak, and they grew harder to
operate as the merge rate rose:
* Seeds fell further from the tip of main between refreshes.
* History operations such as diff and blame took more and more care to keep working on partial
  clones.
* The mirrors no longer scaled once the repository outgrew their disks or memory limits.

## 1.2 Vision

> A source-control service designed for clients that are always online: the server owns history
> and computation, clients fetch only what they read, every component scales horizontally, and
> landing code needs no global lock.

## 1.3 Business goals

| ID | Goal | Measure of success |
|---|---|---|
| G-1 | Remove source control as the development bottleneck | sustain the landing rate with ≥10× headroom; landing latency does not grow with the landing rate |
| G-2 | Make checkouts cheap | most checkouts served from node- or region-local tiers (≥99% hit rate per tier in steady state); checkout in seconds, not minutes |
| G-3 | Shrink infrastructure | CPU and memory of the serving fleet far below that of the git mirror fleet (the article reports 200× smaller, and a 25% CPU capacity win for CI from faster checkouts) |
| G-4 | Answer source-control questions without a repository | CI jobs and tools get history, blame, ancestry, diffs and search through cheap, programmatic API access, instead of keeping a local copy or relying on vendor-specific APIs |
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
| A build system or a CI system | the article names builds and CI as other human-scale bottlenecks, and Scion "requires its own … CI". Here, CI is a client of Scion, and Scion provides post-merge testing hooks (FR-PM-*) |

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
