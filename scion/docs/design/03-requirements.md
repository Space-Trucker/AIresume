# 3. Requirements specification

Each requirement is atomic and testable, carries a priority (**M**ust, **S**hould, **C**ould) and a
source, and has an acceptance criterion. Article references use its section names. "Derived"
means the requirement is engineering analysis needed to make an article statement work.

## 3.1 Functional requirements

### FR-CS Changesets and revisions

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-CS-01 | Changesets are created by the server. Clients never assemble history themselves. | M | §Principles: client-server asymmetry | A commit from any client results in a server-assigned changeset; the client has no write path into history storage. |
| FR-CS-02 | A changeset records parents, author, message, timestamp, and the files changed **relative to its first parent**, merges included. | M | §Data structures; footnote 1 | A merge's change list equals the diff between its first parent and its tree. |
| FR-CS-03 | File contents are referenced by content-addressed ids of compressed objects in blob storage. | M | §Data structures | The stored change entry holds an id that equals the hash of the stored content. |
| FR-CS-04 | A changeset's id is derived from its content, so creating an identical changeset twice is idempotent. | S | Derived (lets servers act without coordination) | Two identical creations produce one changeset and one log entry. |
| FR-CS-05 | Creating a changeset appends it to a write-ahead log without locks, cross-server coordination, or ref movement. | M | §Data structures | Creation never touches the refs table; concurrent creations on two servers both succeed. |
| FR-CS-06 | A changeset is readable from every server as soon as its creation returns. | M | §Data structures ("available everywhere, instantly") | Create on server A, then read on server B immediately: found. |
| FR-CS-07 | A revision can be named by a full id, a unique id prefix, a ref name, and `~N` / `^N` suffixes. | S | Derived (usability) | `main~2`, `<prefix>^2` and an ambiguous-prefix error all behave as specified. |
| FR-CS-08 | Creation is validated: parents exist; deleted paths exist; no file/directory collisions; no duplicate paths; valid path syntax. | M | Derived | Each invalid input returns a structured error and creates nothing. |
| FR-CS-09 | Creating a changeset costs time proportional to the size of the change, not of the repository. | M | §Principles: commits cheap and incremental | A one-file commit takes the same time (±25%) in repositories of 10² and 10⁴ files. |

### FR-REF Refs

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-REF-01 | Refs are optional. Changesets can be created, fetched, reviewed and landed without any ref pointing at them. | M | §Principles ("discourages refs") | A change request is created and landed for a changeset that no ref points to. |
| FR-REF-02 | Moving a ref is an atomic compare-and-swap on a single record, separate from changeset creation. | M | §Data structures | Concurrent moves with the same expected value: exactly one succeeds. |
| FR-REF-03 | Protected refs (for example `main`, `release/*`) can be moved only by authorized principals. | M | §Principles (main and release branches); derived | An unauthorized move returns 403; the landing service's move succeeds. |
| FR-REF-04 | Every ref movement is logged with old value, new value, actor and time. | S | Derived (audit) | The ref log forms an unbroken old→new chain. |
| FR-REF-05 | A release branch can be created from any changeset by an authorized principal. | S | §Principles (release branches) | Creating `release/x` at a changeset succeeds for the release role only. |

### FR-OBJ Object storage

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-OBJ-01 | All source-control data is content-addressed and immutable. | M | §Scaling Scion | Rewriting stored bytes is detected as an integrity failure. |
| FR-OBJ-02 | Objects are stored individually and compressed. There are no packfiles. | M | §Principles: horizontally scalable | The storage layout has one entry per object. |
| FR-OBJ-03 | No server, cache or client needs repository maintenance (gc, repack). | M | §Principles; §Scaling Scion | No maintenance command exists or is needed. Bounded stores evict on their own. |
| FR-OBJ-04 | Any consumer can verify an object's integrity from its id alone. | M | Derived (AS-05) | A tampered object is rejected by the daemon and the client. |
| FR-OBJ-05 | No component holds a fully materialized copy of the repository, not even the server. | M | §Principles: horizontally scalable | Trees are built on demand from changesets; no full working copy exists on the server. |

### FR-DD Derived data

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-DD-01 | Everything not part of a changeset is computed through **one generic mechanism**. | M | §Data structures | Every built-in derived structure is registered with the same mechanism. |
| FR-DD-02 | Each derived type is defined recursively: its value for a changeset is computed from that changeset and its values for the changeset's parents. | M | §Data structures | Deriving for a tip with no stored values computes all ancestors in topological order. |
| FR-DD-03 | Each type is either eager (computed when the changeset is created) or deferred (computed on first use). | M | §Data structures | An eager type has a value straight after creation; a deferred type has none until queried. |
| FR-DD-04 | A new derived type can be added without changing any client. | M | §Data structures | Registering a test-only type and querying it needs no client change. |
| FR-DD-05 | Any server can compute a value on the fly and write it back without coordinating with other servers. | M | §Scaling Scion | Two servers deriving the same value concurrently both succeed, with identical results. |
| FR-DD-06 | Operators can backfill a deferred type ahead of demand. | S | Derived from FR-DD-03 | The admin backfill command computes values for a revision and all its ancestors. |
| FR-DD-07 | Root trees per changeset. | M | §Scaling Scion (the fetch protocol starts from a root tree) | The root tree of any changeset is available. |
| FR-DD-08 | Path history: which changesets changed a file or directory. | M | §Data structures | History of a path lists exactly the changesets that modified it, newest first. |
| FR-DD-09 | File blame (line attribution). | M | §Data structures | Every blamed line's origin changeset contains that line at the reported position. |
| FR-DD-10 | Skip lists over the commit graph for fast ancestry. | M | §Data structures; §What we learned (ancestry index) | Ancestry over n linear changesets takes O(log n) steps. |
| FR-DD-11 | A copy-detection index (copies and renames). | S | §Data structures | A renamed file's history continues across the rename. |
| FR-DD-12 | A path-search index. | S | §Data structures | Path search prunes subtrees that cannot match. |

### FR-QRY Server-side queries

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-QRY-01 | Get one or more changesets by revision. | M | §Scaling Scion ("getting changesets") | Returns metadata, changes, generation, copies. |
| FR-QRY-02 | Log: first-parent or all-ancestor order, paginated, optionally limited to a path. | M | Derived | Pagination returns a contiguous, duplicate-free sequence. |
| FR-QRY-03 | Diff between any two changesets, structured and as text, optionally limited to paths. | M | §Scaling Scion ("computing diffs") | Matches a naive comparison of the two trees. |
| FR-QRY-04 | Diff of a changeset against its merge base with another revision, with no checkout. | M | §Principles: the working copy is optional | A CI job obtains the diff with only API calls. |
| FR-QRY-05 | Merge base(s) and ancestry checks. | M | §Scaling Scion ("finding merge bases") | Equals the brute-force set of best common ancestors. |
| FR-QRY-06 | History of a file or directory, following copies and renames. | M | §Principles; §Data structures | See FR-DD-08 and FR-DD-11. |
| FR-QRY-07 | Blame: who last changed each line. | M | §Principles | See FR-DD-09. |
| FR-QRY-08 | Read a file and list a directory at any revision. | M | Derived | Byte-identical to the committed content. |
| FR-QRY-09 | The first-parent ancestor N steps back. | S | Derived (bisect) | Returns the same changeset as walking N steps. |
| FR-QRY-10 | Every query the client uses is part of the public API. | M | §Principles: a comprehensive source control service | The client has no private endpoints. |

### FR-WR Server-side writes

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-WR-01 | Commit through the API, with content uploaded beforehand or inline; no checkout needed. | M | §Principles ("many write workloads can also skip the checkout") | A changeset is created and a ref optionally moved with API calls only. |
| FR-WR-02 | Merge two changesets with a three-way merge, reporting conflicts in a structured form. | M | §Principles: client-server asymmetry | A clean merge produces a merge changeset; a conflict returns per-path reasons. |
| FR-WR-03 | Rebase a stack of changesets onto another revision, dropping changes that are already applied. | M | same | The rebased stack's trees equal the original changes applied to the new base. |
| FR-WR-04 | Revert a changeset on top of any revision. | M | §Principles (revert pipelines) | The result undoes exactly that changeset's changes. |
| FR-WR-05 | Optionally create a changeset and compare-and-swap a ref in the same call. | C | Derived | Returns the changeset id and whether the ref moved. |
| FR-WR-06 | Uploads skip content the server already has. | S | Derived (bandwidth) | Re-uploading known blobs transfers nothing. |
| FR-WR-07 | Uploads above a configured per-file size limit are refused. | S | Derived (threat D3, risk R-10) | An oversized blob gets 413 and nothing is stored. |

### FR-FP Fetch protocol

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-FP-01 | Requests name only the objects the client **wants**. They never describe what it already has. | M | §Scaling Scion | The request format has no "have" field. |
| FR-FP-02 | The client starts from a root tree, fetches missing trees recursively, then missing blobs. | M | §Scaling Scion | A checkout's request log shows trees level by level, then blobs. |
| FR-FP-03 | Responses are per-object, not one monolithic pack, so a fetch can resume. | M | §Scaling Scion | An interrupted checkout resumes, reusing objects already received. |
| FR-FP-04 | Sparse and virtual checkouts need no special protocol support. | M | §Scaling Scion | Both modes use only the plain object request. |
| FR-FP-05 | daemon, cache and server answer the identical RPC; the client needn't know the topology. | M | §Scaling Scion | The same request against all three returns identical bytes. |
| FR-FP-06 | Objects travel in their stored compressed form, with no recompression, delta compression or "missing object" computation. | M | §Scaling Scion | A cache serves bytes byte-identical to what it received. |
| FR-FP-07 | Requests are batched and may run in parallel. | S | Derived | One request per batch of up to N ids; batches run concurrently. |

### FR-TIER Tiered serving

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-TIER-01 | One `scion-daemon` per node, reached over a local socket, storing objects for every job on that node. | M | §Scaling Scion | Two jobs on one node: the second fetch is served without reaching the cache. |
| FR-TIER-02 | The daemon's store is bounded and evicts least-recently-used objects. | M | Derived | The store never exceeds its configured size. |
| FR-TIER-03 | A daemon starts from a snapshot and refreshes it periodically. | M | §Scaling Scion | A fresh daemon serves the snapshot's revision with zero cache requests; a newer snapshot is imported. |
| FR-TIER-04 | Daemons talk only to their regional caches. | M | §Scaling Scion | Configuration accepts cache endpoints only; a direct server request is refused. |
| FR-TIER-05 | `scion-cache` is regional and in memory, and streams objects from memory. | M | §Scaling Scion | Hits are served without touching disk or the upstream. |
| FR-TIER-06 | Cache misses go to the authoritative servers, which read metadata and blob storage. | M | §Scaling Scion | A miss produces exactly one upstream request per batch. |
| FR-TIER-07 | Strict tiering: each tier serves object requests only from the tier directly below it. | M | §Scaling Scion | client→cache, daemon→server and user-claims-cache are refused (403). |
| FR-TIER-08 | Tiers hold no long-lived state and scale by adding instances. | M | §Scaling Scion | Restarting a cache loses nothing but warmth. |
| FR-TIER-09 | Each tier fails over between several upstream instances. | S | Derived (availability) | With one of two servers down, checkouts still succeed. |
| FR-TIER-10 | Concurrent misses for the same object become one upstream request (single flight). | S | Derived (protects upstreams) | Ten concurrent misses for one id produce one upstream call. |
| FR-TIER-11 | Operators publish snapshots of a revision to blob storage. | M | §Scaling Scion | The publish command writes a snapshot and updates a "latest" pointer atomically. |

### FR-CL Client (`scn`)

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-CL-01 | Check out a revision in full, sparse (listed directories) or virtual (on demand) mode. | M | §Principles: the working copy is optional | Each mode fetches only what it needs (see FR-FP-02). |
| FR-CL-02 | Keep a bounded local object cache. | M | §Principles: client-server asymmetry | The cache never exceeds its bound; the checkout is still correct. |
| FR-CL-03 | Lay out working-copy files with the correct kinds (regular, executable, symlink). | M | §Principles | Kinds round-trip through commit and checkout. |
| FR-CL-04 | Monitor the filesystem for changes so status doesn't scan everything. | M | §Principles | With the monitor running, status inspects only changed paths. |
| FR-CL-05 | Status, add, remove, restore and local diff. | M | §Principles ("ergonomic way to work with the server") | Behave as documented. |
| FR-CL-06 | Commit creates a changeset on the server. There is nothing to push. | M | §Principles | No push command exists; the change is visible to others immediately. |
| FR-CL-07 | Update to any revision, applying only the diff and refusing to overwrite local changes. | M | Derived | Bytes fetched are proportional to the diff; conflicting local edits are protected. |
| FR-CL-08 | Rebase the local stack onto a revision, executed by the server. | M | §Principles | Same as FR-WR-03, then the working copy is updated. |
| FR-CL-09 | Add and remove directories from a sparse profile. | S | Derived | Files appear and disappear accordingly. |
| FR-CL-10 | Virtual mode materializes files when read. | M | §Principles ("materialize files on demand") | Reading one file fetches only that file and the trees on its path. |
| FR-CL-11 | A CLI covering working-copy operations, server queries, review and automation. | M | §Principles | Every FR-QRY and FR-RV capability is reachable from the CLI. |
| FR-CL-12 | The client reaches objects through the node daemon by default and needs no knowledge of the topology. | M | §Scaling Scion | The configuration takes one object endpoint. |

### FR-IAM Access control

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-IAM-01 | Read and write access control at repository level. | M | §What we learned: security | Unauthorized reads and writes are refused. |
| FR-IAM-02 | Several repositories, each with its own policy, can be hosted. | S | §What we learned ("access control on repositories") | Two repositories with different policies on one deployment. |
| FR-IAM-03 | Read and write permissions on individual directories. | M | §What we learned: security | A user without access to `secrets/` can still work everywhere else. |
| FR-IAM-04 | Directory read restrictions are enforced on **every** read path: queries, diffs, search, blame, history, changeset listings, object protocol, snapshots. | M | Derived from FR-IAM-03 | No API returns restricted content or object bytes to an unauthorized user. |
| FR-IAM-05 | Shared intermediate tiers never cache restricted content. | M | Derived (confidentiality on shared nodes) | After an authorized fetch, the restricted ids are absent from cache and daemon stores. |
| FR-IAM-06 | Groups, administrators and service principals. | S | Derived | Membership changes take effect on the next request. |
| FR-IAM-07 | Principals are authenticated. | M | Derived | A missing or wrong credential returns 401 when authentication is configured. |
| FR-IAM-08 | Service principals act on behalf of end users, whose permissions then apply. | M | Derived (caches serve many users) | A daemon fetching for user U gets U's view, not its own. |
| FR-IAM-09 | After a policy change, existing data is re-indexed. | S | Derived | Newly restricted directories become restricted for existing objects. |
| FR-IAM-10 | Access-relevant events (policy changes, denials, ref moves) are auditable. | S | Derived (compliance) | An audit query lists them with actor and time. |
| FR-IAM-11 | Public bytes stay public: content that also appears at a readable path is not withheld. | S | Derived | A file with the same bytes as a secret, at a public path, is readable. |

### FR-RV Code review (Antique)

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-RV-01 | A change request (CR) points at a changeset; no branch is required. | M | §Principles (refs discouraged) | A CR is created from a bare changeset id. |
| FR-RV-02 | Authors upload new revisions. Approvals apply to a revision and reset on a new one. | M | Derived | After an update, the requirements are unsatisfied again. |
| FR-RV-03 | General and line-level comments. | M | Derived | Comments are stored with revision, path and line. |
| FR-RV-04 | Approvals. Self-approval never counts. | M | Derived | An author's own approval doesn't satisfy a rule. |
| FR-RV-05 | Each changed file is classified as docs, comment-only or logic. | M | §What we learned: security ("comment-only changes") | Comment edits in Python and C-like files classify as comment-only; comment markers inside strings do not. |
| FR-RV-06 | Approval rules per directory and per category, including owner approvals. | M | §What we learned: security ("complex semantic constraints") | A logic change under an owned directory needs an owner's approval. |
| FR-RV-07 | The evaluated requirements (needed vs present) are shown to authors and reviewers. | M | Derived | The UI and API show each scope's need and have. |
| FR-RV-08 | A review UI with a diff view. | M | §Introduction ("a code review surface") | The CR page shows metadata, requirements, comments and the diff. |
| FR-RV-09 | Approve and comment from the UI. | S | Derived | The UI actions call the same API. |
| FR-RV-10 | Reviewers are notified of review requests. | C | Derived | A webhook fires on CR creation. |

### FR-LD Landing

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-LD-01 | An approved CR lands by a server-side rebase onto the target's tip and an atomic compare-and-swap of the ref. | M | §What we learned: rethinking priors | The landed changeset descends from the old tip; the ref moved by CAS. |
| FR-LD-02 | There is no global repository lock and no serialized merge queue. | M | §What we learned ("haven't been able to replicate … a global repository lock") | Servers coordinate only through the ref CAS. |
| FR-LD-03 | Landing makes progress under heavy concurrency, without starvation. | M | Derived (from 30k+/day with growth) | 32 concurrent landers × 5 rounds on 2 servers: all land. |
| FR-LD-04 | Conflicts are reported in a structured form and the CR enters a conflict state; a new revision resolves it. | M | §What we learned ("Claude can typically fix these conflicts") | A 409 response lists paths and reasons; the CR lands after an update. |
| FR-LD-05 | Every landed changeset is indexed to its CR, ref and time, and can be looked up by its landed or original id. | M | §What we learned ("asking our code review tool") | The lookup is indexed and needs no scan of the log. |
| FR-LD-06 | Automation can land changesets without a CR when authorized (for example reverts). | S | Derived (revert pipeline) | Only service or admin principals can do this. |
| FR-LD-07 | Landing enqueues post-merge testing. | M | §What we learned (post-merge testing) | Every landing creates a queued job. |

### FR-PM Post-merge and pre-deploy testing

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-PM-01 | A queue of landed changesets awaiting tests; workers claim jobs atomically. | M | §What we learned | Two workers never claim the same job. |
| FR-PM-02 | Workers reuse one checkout and apply only the diff between jobs. | S | Derived (cost) | The second job fetches only changed files. |
| FR-PM-03 | Results (pass or fail, with logs) are recorded. | M | Derived | Status per job is visible. |
| FR-PM-04 | Optionally, a failing landing is reverted automatically, the whole stack included. | S | Derived (revert pipelines) | After a failure, main no longer contains the change. |
| FR-PM-05 | A deploy gate returns the newest changeset on a ref whose post-merge tests passed. | M | §What we learned (pre-deploy testing) | It never returns a failed or untested changeset. |

### FR-AUT Automation pipelines

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-AUT-01 | Automated bisect over the API: a first-parent range plus a predicate, with no clone required. | M | §Principles (bisect pipelines) | Finds the first bad changeset in ⌈log2(n)⌉ probes or fewer. |
| FR-AUT-02 | Automated revert pipeline over the API. | M | §Principles (revert pipelines) | Reverts and lands while others are landing concurrently. |

### FR-SR Code search

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-SR-01 | Path search backed by a derived index. | M | §Introduction ("code search"); §Data structures | Finds every matching path; visits far fewer trees than the repository has. |
| FR-SR-02 | Content search (regex) on the server, with no checkout. | M | §Introduction | Returns path, line and text matches. |
| FR-SR-03 | An indexed content search that scales to the full monorepo. | S | Derived (scale) | Query time is sublinear in repository size. |
| FR-SR-04 | Results are filtered by the caller's permissions. | M | FR-IAM-04 | Restricted paths never appear. |

### FR-MG Migration from git

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-MG-01 | Ingest git history as changesets, preserving the commit graph and first-parent semantics. | M | §What we learned (ingestion pipeline) | Changeset parents mirror commit parents. |
| FR-MG-02 | Preserve ordering invariants (parents before children) and refuse violations. | M | §What we learned ("implicit invariants around ingestion ordering") | A range with missing parents is refused and nothing is written. |
| FR-MG-03 | Incremental sync: only new commits are ingested. | M | Derived (migration while git is live) | A re-run ingests only the new commits. |
| FR-MG-04 | Memory use is bounded, independent of history size (streaming). | M | §What we learned ("20x less memory") | Memory stays flat as the commit count grows. |
| FR-MG-05 | Verify ingested trees against git, byte for byte. | M | Derived | Verification reports zero mismatches. |
| FR-MG-06 | Answer metadata queries (ancestry, blame) for git-hosted history before a Scion client exists. | S | §Scaling Scion ("Scion only answered these metadata queries") | Ingested history is queryable through the API with no `scn` client. |
| FR-MG-07 | Map git commit ids to changeset ids in both directions. | M | Derived | Lookup works both ways. |

### FR-OP Operations and observability

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-OP-01 | Every component exposes health and stats endpoints. | M | §What we learned (operational excellence) | `/healthz` and `/stats` respond on server, cache and daemon. |
| FR-OP-02 | Stats include per-tier hit rate, latency percentiles and error counts. | M | §Scaling Scion (hit rate > 99%) | The values are present and correct in tests. |
| FR-OP-03 | Superfans: a per-component monitor that learns baselines and flags novel anomalies. | S | §What we learned (superfans) | A sudden hit-rate drop raises a "novel" finding. |
| FR-OP-04 | Traditional threshold alerts. | M | §What we learned ("traditional alerts") | A configured threshold breach raises a finding. |
| FR-OP-05 | Findings are delivered to chat via a webhook. | S | §What we learned (Slack channels) | The webhook receives a Slack-compatible payload. |
| FR-OP-06 | Rate limiting per principal and request class, with concurrency caps. | M | §What we learned ("sophisticated rate limiting") | Excess requests receive 429 with a Retry-After header; the client backs off. |
| FR-OP-07 | Benchmarks for the scaling claims that can be reproduced locally. | S | Derived | The benchmark command reports commit scaling, ancestry and checkout numbers. |

### FR-AD Administration

| ID | Requirement | Pri | Source | Acceptance criterion |
|---|---|---|---|---|
| FR-AD-01 | Initialize a repository. | M | Derived | Creates empty storage. |
| FR-AD-02 | Publish a snapshot (FR-TIER-11). | M | §Scaling Scion | See FR-TIER-11. |
| FR-AD-03 | Backfill derived data (FR-DD-06). | S | — | See FR-DD-06. |
| FR-AD-04 | Re-index ACLs (FR-IAM-09). | S | — | See FR-IAM-09. |
| FR-AD-05 | Administrative ref operations, protections respected. | M | Derived | Set a ref with CAS semantics. |
| FR-AD-06 | Back up and restore the authoritative stores. | S | Derived (durability) | A restore reproduces identical refs and changesets. |

## 3.2 Non-functional requirements

| ID | Quality | Requirement | Target | Pri | Source |
|---|---|---|---|---|---|
| NFR-01 | Throughput | Sustain the landing rate with growth headroom | Design: ≥30,000 landings per day with 10× headroom (≈3.5/s sustained). Prototype: no starvation with 32 concurrent landers on 2 servers. | M | §Introduction |
| NFR-02 | Checkout volume | Serve very high checkout volumes from local tiers | Design: ~25M checkouts per day; ≥99% hit rate per tier in steady state. Prototype: a second checkout on a node makes 0 cache requests. | M | §Growing; §Scaling |
| NFR-03 | Size | No component needs the whole repository | 100 GB history and 25 GB working copy supported, because no component materializes everything | M | §Growing |
| NFR-04 | Latency | Checkouts take seconds | Sparse checkout of a typical project in < 10 s from a warm daemon | M | §Scaling Scion |
| NFR-05 | Incrementality | Commit cost tracks change size | ±25% across repositories of 10² to 10⁴ files | M | §Principles |
| NFR-06 | Algorithmic | Ancestry is O(log n) on linear history; history is O(depth) per result | Measured by step counters | M | §What we learned |
| NFR-07 | Scalability | Every component scales horizontally; tiers are stateless | Adding instances needs no data migration | M | §Principles |
| NFR-08 | Fault isolation | A tier's failure does not overload the tier above it | Strict tiering, single flight, rate limits | M | §Scaling Scion |
| NFR-09 | Availability | No single point of failure in serving | ≥2 instances per tier; failover with no client change | S | Derived |
| NFR-10 | Confidentiality | Restricted directories are protected end to end | Zero restricted bytes reach unauthorized users through any path | M | §What we learned |
| NFR-11 | Integrity | All objects are verified on consumption | 100% of objects received by a daemon or client | M | Derived |
| NFR-12 | Consistency | Refs are linearizable; derived data is deterministic; changesets are read-your-writes | CAS semantics; identical derived values on every server | M | §Data structures |
| NFR-13 | Durability | The authoritative stores are durable; tiers are disposable | Losing any tier loses no data | M | Derived |
| NFR-14 | Maintainability | No repository maintenance; derived types can be extended | No gc or repack; new types in one class | M | §Principles |
| NFR-15 | Testability | Fuzzing and hermetic simulation of every non-trivial interaction | Fuzzing against a naive model; a multi-agent simulation | M | §What we learned |
| NFR-16 | Observability | Every component is measurable | FR-OP-01/02 | M | §What we learned |
| NFR-17 | Footprint | Resource use far below the git mirror fleet | Prototype: in-memory caches sized in MB; servers hold no full copies | S | §Scaling Scion |
| NFR-18 | Usability | CLI familiar to git and Sapling users; errors machine-readable for agents | Structured JSON errors with stable codes | M | AS-03 |
| NFR-19 | Portability | Standard library only; Linux reference platform | No third-party imports | M | CON-01 |
| NFR-20 | Security hardening | Encrypted transport between components (mTLS) in production | Out of scope for the prototype; must be done before production | S | Derived |

## 3.3 Business rules

| ID | Rule |
|---|---|
| BR-01 | An author's approval never counts toward their own change request. |
| BR-02 | Approvals belong to one revision of a CR. |
| BR-03 | Comment-only and docs-only changes may need fewer approvals than logic changes, as configured. |
| BR-04 | Only the landing service and administrators move `main`; only release managers move `release/*`. |
| BR-05 | Restricted content is never stored by shared caches. |
| BR-06 | A changeset's history and blame follow its first parent (footnote 1), except for lines or files taken verbatim from another parent. |

## 3.4 External interfaces

* **RPC API:** HTTP/1.1 with JSON bodies, plus a binary framing for objects ([../API.md](../API.md)).
* **Daemon socket:** a Unix domain socket speaking the same protocol.
* **CLI:** `scn`, `scion-server`, `scion-cache`, `scion-daemon`, `scion-admin`.
* **Web:** the read-only Antique pages at `/antique`.
* **Storage:** the `MetaStore` interface (log, refs, derived values, indexes) and the `ObjectStore` interface.
* **Integrations:** the `git` CLI (ingestion) and webhooks (alerts).
