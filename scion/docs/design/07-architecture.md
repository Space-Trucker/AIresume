# 7. Architecture

## 7.1 Architectural drivers

| Driver | From | Shapes |
|---|---|---|
| Clients are always online | AS-01, FR-CS-01 | centralized authoritative service; thin client |
| Merge rate grows without bound | NFR-01 | lock-free changeset creation; CAS refs; group-commit landing |
| Checkout volume (tens of millions per day) | NFR-02 | content addressing; three cache tiers; want-only protocol; snapshots |
| Repository too big for any one machine | NFR-03, FR-OBJ-05 | no full copies; derived data built incrementally |
| Tiny team | CON-05, NFR-14 | no maintenance, stateless tiers, one generic derived-data mechanism |
| Sensitive code in a monorepo | NFR-10 | ACL index on objects; caches never store restricted objects; filtered APIs |
| Prototype constraints | CON-01/02 | standard library only; storage behind interfaces |

## 7.2 Architectural style

* **Centralized source of truth, decentralized caching.** Correctness lives in the server fleet
  and its storage. Every other tier is a disposable cache of immutable data.
* **Immutable, content-addressed data.** Changesets and objects are named by hashes, so caching
  needs no invalidation and writes are idempotent (AS-05).
* **Log plus derived views.** The changeset log is the only primary data. Every index (trees,
  history, skip lists, blame, search) is a deterministic, recursive projection of it. This is
  similar to event sourcing with materialized views.
* **Optimistic concurrency.** Refs are the only mutable state, and they change only by
  compare-and-swap.
* **Prior art.** Source control for huge monorepos has prior art, notably Google's Piper and
  Meta's Sapling. The article says Scion was built with their hard-won lessons in mind.
* **Ecosystem relevance.** The design embodies the ideas the article offers to git platforms:
  * a server that does not work like the client;
  * comprehensive server-side RPCs that could be standardized across forges ([../API.md](../API.md));
  * a negotiation protocol unlike today's (want-only, ADR-04);
  * sparse and shallow features that compose (sparse and virtual checkouts with no history on the client).

## 7.3 Logical view

Components: [6.2](06-uml.md#62-components). Packages: [6.4](06-uml.md#64-packages).
Domain model: [6.1](06-uml.md#61-domain-model).

| Layer | Modules | Responsibility |
|---|---|---|
| Storage | `objects`, `storage`, `meta`, `spanner` | compressed content-addressed objects; the metadata store (changeset log, refs, derived values, indexes, reviews, queues, audit) on SQLite or Cloud Spanner |
| Core | `changeset`, `trees`, `derived`, `derived_types`, `linediff`, `merge3`, `repo` | changeset semantics, incremental trees, derived data, history and blame, line diffs, ancestry, merge, rebase, revert |
| Policy | `iam`, `ratelimit`, `classify` | permissions, rate limits, change classification |
| Services | `rpc`, `server`, `tiers`, `snapshot`, `antique`, `search` | RPC surface, tiers, review and landing, search |
| Client | `client`, `fsmonitor`, `cli` | working copies, monitoring, CLI |
| Tooling | `ingest`, `postmerge`, `tools/*`, `superfan`, `superfan_agent` | migration, post-merge, bisect, revert, monitoring and its Claude agents, benchmarks (also against git) |

## 7.4 Process and concurrency view

| Concern | Mechanism |
|---|---|
| Changeset creation | idempotent append keyed by content hash; no locks; eager derived data computed right after |
| Derived data races | values are deterministic, written with insert-or-ignore; a per-process single-flight lock avoids duplicate work |
| Refs | single-row compare-and-swap; every success is appended to the ref log in the same transaction |
| Metadata transactions | SQLite: one writer at a time (WAL), readers never block. Spanner: every read-write operation is a transaction function, rerun with jittered backoff when Spanner aborts it; reads are strong single-use reads; rows that never change (changesets, derived values) are cached in-process |
| Landing | per-server, per-target group commit: one leader drains the queue, rebases a chain, does one CAS; retries with jittered exponential backoff up to a deadline (then 503 `retry`); servers never coordinate except through the CAS; CRs show `landing` while queued |
| Cache misses | single flight per object id; waiters re-read the store or re-request |
| Request handling | a thread per connection (HTTP/1.1 keep-alive; each response leaves in one write, with TCP_NODELAY); TLS handshakes run on the connection's thread; per-thread SQLite connections in WAL mode, or a pool of Spanner sessions |
| Superfan agents | one investigation per finding, a few at a time on a small thread pool; repeated findings are investigated once; the watcher never waits for the agent |
| Client fetch | breadth-first by tree level; blob batches fetched in parallel |
| Status | a filesystem watcher process journals events; the sync cookie orders queries after earlier events |
| Policies | each request stats `deployment.json` and the repository's `policy.json`; a changed file is reloaded at once and audited (FR-IAM-06) |
| Audit | appends take the store's write lock, so the hash chain stays linear across servers |

**Consistency model**
* **Changesets and objects:** immutable, read-your-writes from any server sharing the store.
* **Refs:** linearizable through compare-and-swap.
* **Derived data:** eventually present and always identical (a deterministic function of immutable inputs).
* **Tiers:** never stale for content (it is immutable). Only the ACL classification can change: at once
  for a repository that turns private, at re-index for directory rules; every tier learns of it through the
  repository's ACL epoch within about two epoch intervals and purges what it held (ADR-20, R-07).

## 7.5 Deployment and scaling view

Deployment diagram: [6.3](06-uml.md#63-deployment).

| Component | State | Scales by | Fails how | Effect of failure |
|---|---|---|---|---|
| scion-daemon | bounded disk cache | one per node | crash | jobs on that node fall back to the cache tier after restart; nothing is lost |
| scion-cache | memory | instances per region | crash | daemons fail over to another cache; single flight limits the herd on servers |
| scion-server | stateless (plus per-process caches) | instances | crash | caches and clients fail over; no data loss |
| Metadata store | authoritative | Cloud Spanner's own scaling (SQLite: one host) | outage | writes stop; tiers keep serving cached content |
| Object store | authoritative | the shared filesystem behind the directory | outage | misses fail; hits keep working |
| Superfan agent | none | one per watcher | crash, or the Claude API is down | findings still reach chat, without an analysis |

## 7.6 Data view

**Repositories (ADR-13).** A deployment root holds `repos/<name>/` directories, each with
`objects/`, `meta.db` and `policy.json`. A server serves every repository under its root. RPC
parameters and the object protocol carry `repo`; working copies record which repository they
belong to. Principals are deployment-wide: `deployment.json` at the root holds the tokens, service
principals, groups, deployment administrators, rate limits and default limits, and each
repository's `policy.json` holds who may read and write it, its administrators and its limits.

**Object identity:** `id = sha256(type || 0x00 || payload)`. Objects are stored as
`zlib(type || 0x00 || payload)`, which is exactly what crosses the wire.

| Type | Payload | Notes |
|---|---|---|
| `blob` | file bytes | public |
| `tree` | lines `"<kind> <id> <name>\n"`, sorted by name | public; kinds are f, x, l (link), d (directory) |
| `htree` | JSON rows `[name, kind, content_id, last_changeset, child_htree]` | internal: path history |
| `stree` | JSON rows `[name, kind, id, bloom_hex]` | internal: path search; directory blooms of 2,048 bits |
| `blame` | `{"runs": [[changeset, origin_line, count], ...]}` | internal |

**Changeset:** canonical JSON `{parents, author, message, timestamp, changes:[[path, op, kind, blob]], extra}`,
with `id = sha256("changeset\0" || json)`.

**Derived values (per changeset)**

| Type | Value |
|---|---|
| `tree` | root tree id |
| `graph` | `{g: generation, l: single-parent run length, s: [first-parent ancestor at 2^k]}` |
| `history` | htree root id |
| `copies` | `{dest: {from, type}}` |
| `search` | stree root id |
| `blame` | `{path: blame id or "binary"}` |

**Metadata schema:** see the ER diagram in [6.9](06-uml.md#69-metadata-store-er). Besides the changeset
log, refs and derived values, each repository's store holds the object index (`object_acl`: where each
object appears, `""` for a place everyone may read), possession grants (`object_grants`: an uploader
may commit by id bytes they uploaded even if the object is otherwise restricted), the audit chain
(`audit`) and Antique's tables (`crs`, `cr_revisions`, `cr_approvals`, `cr_comments`, `landings`,
`postmerge`).

## 7.7 Protocols

* **RPC:** `POST /rpc/<method>`, JSON in and out; error envelope `{error: {code, message, data}}`;
  stable HTTP statuses 400/401/403/404/409/429/500.
* **Identity headers:** `X-Scion-User`, `Authorization: Bearer`, `X-Scion-Tier`, `X-Scion-On-Behalf-Of`.
* **Objects:** `get_objects {repo, ids}` returns repeated `[32B id][1B flags][4B len][stored bytes]`.
  The flags are RESTRICTED, MISSING and DENIED. `put_objects?repo=<name>` takes the same framing.
* **Transport security (ADR-14):** `https://` endpoints use TLS 1.2 or later. With a client CA
  configured, the client certificate's common name is the service principal, and service
  principals must authenticate that way; users send bearer tokens.
* **Failover (NFR-09):** tiers and clients take several equivalent upstream endpoints; an endpoint
  that can't be reached is skipped, and requests that are safe to resend move on after a 5xx.
* **Daemon transport:** the same HTTP over a Unix domain socket.
* Full reference: [../API.md](../API.md).

## 7.8 Capacity estimate (from the article's numbers)

| Quantity | Estimate | Reasoning |
|---|---|---|
| Landings | 30,000/day ≈ 0.35/s average; design target 3.5/s sustained | 10× headroom (NFR-01) |
| Landing work per CAS | one rebase chain per batch | group commit makes the number of CAS attempts sublinear in the number of landers |
| Checkouts (CI alone) | 25M/day ≈ 290/s average | Article §Growing our monorepo; more with developer environments, agent sandboxes and research jobs |
| Naive git transfer | 25M × 25 GB ≈ 625 PB/day | matches the article's "over 600 PB" |
| Sparse checkout size (assumed) | 5,000 objects × 4 KB ≈ 20 MB | sparse by default (FR-CL-01) |
| Bytes served by daemons | 290/s × 20 MB ≈ 5.8 GB/s fleet-wide, all local | node-local Unix socket |
| Cache-tier traffic at 99% node hit rate | ≈ 58 MB/s across regions | NFR-02 |
| Server traffic at 99% cache hit rate | ≈ 0.6 MB/s | why the server fleet is small |
| Changeset log growth | 30k × ~2 KB ≈ 60 MB/day | changesets list changes only |
| Derived values per changeset | 5 eager rows + deferred blame | plus new objects only on changed paths |
| Regional cache memory | holds the hot set of the tip (≤ 25 GB compressed working copy) | an in-memory LRU of 32–64 GB per region instance |

## 7.9 Failure modes

| Failure | Detection | Handling | Requirement |
|---|---|---|---|
| Cache instance down | connection error | daemon fails over to the next cache | FR-TIER-09 |
| All caches down | errors at the daemon | jobs retry; tiering stops daemons from flooding servers | FR-TIER-07, NFR-08 |
| Thundering herd on a hot object | — | single flight in caches and daemons | FR-TIER-10 |
| A client floods the API | token bucket | 429 with Retry-After; the client backs off | FR-OP-06 |
| Corrupted object | hash mismatch | rejected at the daemon and client | FR-OBJ-04 |
| CAS contention while landing | CAS failure | rebase and retry with backoff, as a batch | FR-LD-03 |
| Landing conflict | three-way merge conflict | CR state `conflict`, 409 with details | FR-LD-04 |
| Kernel inotify overflow | overflow event | full status scan | FR-CL-04 |
| Watcher stuck | sync cookie timeout | full status scan | FR-CL-04 |
| Ingestion run with bad ordering | missing parent | refuse, write nothing | FR-MG-02 |
| Post-merge failure | test result | revert the stack (optional) | FR-PM-04 |
| Post-merge worker lost mid-job | no report within the lease | the job returns to the queue; the lost worker's late report is refused | FR-PM-01 (ADR-22) |
| A policy or identity file doesn't parse | load error | the last good version stays in force; audited and logged as an error | FR-IAM-06 (ADR-23) |
| An upstream of the wrong tier | `tier_info` | skipped and logged; checked again a minute later | FR-TIER-04 |

## 7.10 Cross-cutting concerns

* **Security:** see [08-security.md](08-security.md).
* **Observability:** `/healthz`, `/stats` and `/logs` everywhere; latency percentiles per method;
  superfans that read telemetry and logs and post findings (UC-26).
* **Idempotency:** changeset creation and object upload are idempotent; landing an already-landed
  CR returns its state.
* **Error model:** a machine-readable code plus a message; 409 carries `conflicts[]` for agents (NFR-18).

## 7.11 Architecture decision records

The article notes that engineers' irreplaceable contribution was "the design-level tradeoffs":
which problems to solve and at what scale. These records are where those tradeoffs are written
down, owned by humans and changed only by superseding them (12 §12.6).

| ADR | Decision | Context | Consequences | Alternatives rejected |
|---|---|---|---|---|
| ADR-01 | Centralized service for always-online clients | clients are agents and jobs (AS-01) | no offline mode; the server must be highly available | git with mirrors (stopped scaling: §Growing our monorepo) |
| ADR-02 | Changesets record changes relative to the first parent | write cost should track change size; main-line history (footnote) | trees are derived; merges' second-parent diffs aren't stored | storing full trees per commit (git) |
| ADR-03 | One generic, recursive derived-data mechanism | many indexes, small team | uniform backfill, eager or deferred, invisible to clients | bespoke indexes per feature |
| ADR-04 | Want-only fetch protocol | negotiation over "haves" is CPU-heavy on servers | more round trips (one per tree level), but every response is cacheable | git pack negotiation |
| ADR-05 | Identical RPC on every tier, strict tiering | topology-agnostic clients; failure isolation | tiers must authenticate their callers | free-form routing between tiers |
| ADR-06 | Restricted objects never cached; servers re-authorize | shared nodes, end-to-end confidentiality | restricted reads always reach the servers (more load for sensitive code) | per-user caches; encryption at rest per ACL |
| ADR-07 | Land with server-side rebase plus ref CAS, and per-server group commit. The target's first-parent chain only grows: a CR fast-forwards only when the tip is on its own first-parent chain; otherwise that chain is replayed onto the tip, a merge by its first-parent change list (BR-06). The CAS carries the landing's records: the index, the post-merge job and the CRs' new state commit with the ref's move, or none does | a global merge-queue lock doesn't scale (§What we learned, "We're completely rethinking our priors"); the B6 review found a merge of the target into a CR rewriting main's first-parent history, and a landing whose records could be lost after its CAS | concurrent landings can conflict; post-merge testing is required; a CR's merges of the target don't appear on the target (their content does); on Spanner one landing indexes at most about 8,000 changesets (the 80,000-mutation commit limit) | serialized merge queue; landing merge commits on the target; recording a landing after its CAS |
| ADR-08 | Post-merge testing with auto-revert and a deploy gate | pre-merge CI can't keep up | main can be briefly red; the deploy gate protects production | pre-merge testing of every change against the tip |
| ADR-09 | Semantic approval classes (docs, comment-only, logic) with owners | human attention is scarce | the classifier must be conservative (unknown means logic): a comment a tool reads (a shebang, a coding line, a build or parser directive, a comment continued by a backslash) is code, whitespace is insignificant only outside strings and where indentation isn't structure, and a file is documentation by its format, never by its directory; the rules read the unfiltered diff, and an approval counts for a scope only from someone who can read it | uniform approval counts |
| ADR-10 | SQLite (WAL) and a directory stand in for Spanner and blob storage. *Superseded for metadata by ADR-24; the directory stays (decision of 2026-10-14)* | prototype; CON-01/02 | single host; interfaces kept narrow for a swap | embedding a distributed store |
| ADR-11 | Python standard library only | CON-01; reviewable, portable | slower than a compiled implementation | adding dependencies (gRPC, FUSE, RocksDB) |
| ADR-12 | Generation numbers plus first-parent skip lists for ancestry. Generations fall strictly along a first-parent chain, so whether a changeset is on one is a descent through the skip lists, tried before any walk | O(log n) queries on very long histories; the CPython pilot measured 62 steps for `is_ancestor(root, tip)` once the history held merges, because a walk pays a step per merge | an extra derived row per changeset; main-line ancestry in O(log n) reads whatever merges the chain crosses (T-DD-06) | BFS over parents; reachability bitmaps |
| ADR-13 | Multi-repository hosting: one deployment hosts many named repositories, each with its own storage namespace and policy; every RPC and object request names its repository; caches key objects by (repository, id); objects of a repository whose repository-level read is not open to everyone are flagged restricted | FR-IAM-01/02; caches cannot evaluate repository-level read rules | private repositories bypass shared caching (always re-authorized at the server); public bytes are cached per repository | sharing objects across repositories in caches (leaks private bytes by id); per-user caches |
| ADR-14 | TLS for every TCP endpoint (stdlib `ssl`); mutual TLS between tiers, where the client certificate's common name is the service principal; users authenticate with bearer tokens over TLS; the daemon's Unix socket relies on file permissions | NFR-20; threats S1, S2, I6 | certificates to manage; dev mode can still run plaintext on localhost | trusting the network |
| ADR-15 | Hash-chained, append-only audit log per repository (policy loads, denials, admin actions, force-lands, releases, backups) with an RPC to read and verify it | FR-IAM-10; threats R1, R2 | tampering with the history is detectable by verifying the chain | plain log files |
| ADR-16 | Content search via an index of trigram → blob postings that covers the revisions searched and each import's final revision: before a revision is searched, the text blobs of its tree that the index lacks are indexed, examining only what differs from the last revision indexed in full; a query intersects the postings of its literal trigrams, walks the tree under the path prefix, and reads only candidate blobs | FR-SR-03; grep cost should not be "read every file". Amended 2026-10-14 (12 §12.9 decision 9): the first design indexed every text blob ever written, which for CPython's history would be about 1.2 billion postings (71–107 GB), while searches read a few revisions | an index row per (blob, trigram) for the blobs of searched revisions; the first search of a revision far from the last one indexed pays for the difference (an import pays for its final revision); regexes without a 3-character literal fall back to a scan | an external search engine (violates CON-01); indexing every blob of the history (grows with the history, not with what is searched) |
| ADR-17 | Interactive review UI as server-rendered HTML forms with a session cookie and a per-session CSRF token, calling the same Antique code paths as the RPCs | FR-RV-09; standard library only | no client-side framework; page reloads per action | a separate web application |
| ADR-18 | Reviewer notifications and component logs as small built-in mechanisms: webhooks with retry on CR events; an in-memory ring buffer of structured log entries per component (the last 2,000; a message repeated back to back updates one entry with a count), exposed at `GET /logs` to administrators and service principals, for superfans (*access: superseded by ADR-28*) | FR-RV-10, FR-OP-08 | best-effort delivery; logs are recent-only; a burst of one message can't flush the others | external queues and log stacks |
| ADR-19 | History and blame follow the first parent only, merges included (BR-06, decided at M0) | footnote 1; decision 4 | lines brought in by a merge are attributed to the merge | crediting the other parent's authors (rejected at M0) |
| ADR-20 | ACL epochs: each repository has an epoch that changes when it stops being readable by everyone and at every re-index of the object index; caches and daemons check it upstream at least every `epoch_seconds` (default 10) before serving a repository's objects, purge that repository when it changed, and save it beside a daemon's disk store; snapshots carry the epoch they were taken under and are imported only under the same epoch | the B2 review found that objects cached while public stayed on a daemon's disk, and in snapshots, after the repository turned private, surviving the restart that R-07 prescribed; restarting every daemon on every node is not an operation at this scale | a policy change reaches every tier within about two epoch intervals, without restarts; one small upstream call per repository per interval per tier; tiers that can't reach upstream keep serving what they hold | manual purges and restarts (the earlier procedure); per-object revalidation (one upstream call per hit) |
| ADR-21 | Objects are compressed per type: zlib level 6 for file contents; level 1 for trees and the other derived nodes; Huffman coding alone (no LZ77) for search trees. Trees and derived nodes a commit writes also go straight into the decoded-object cache | the B4 benchmark found one-file commits 52% slower at 10⁴ files than at 10² (NFR-05 allows 25%): every commit rewrites the nodes on its path, the search tree's bloom filters fill up as a repository grows, and level 6 compresses such dense data slowly (about 5 ms against 0.8 ms at level 1 for a 100-entry node); LZ77 can't shorten bloom filters at all, and each commit read back from disk the nodes the previous commit had just written | with objects in memory, the algorithm's commit cost grows ×1.03–1.22 from 10² to 10⁴ files (T-CORE-10 asserts ±25%), and commits are about 35% faster at every size; on disk, the shared machine's file system adds noise (×1.1–1.6 across runs); tree and derived objects are 5–20% larger; ids are unchanged, because they cover the uncompressed bytes | one level for everything (slow commits, or larger blobs); a binary search-tree encoding (a format change for a similar gain); deferring the search tree (slow first searches) |
| ADR-22 | Post-merge jobs are leased: a claim stamps the job with a claim token; a job not reported within the lease (default 2 hours, per repository) returns to the queue at the next claim; a report must carry its token | a worker that crashes after claiming left its job `running` forever, so that landing was never tested and could never be reverted | at-least-once testing of every landing; a slow worker whose lease ran out loses its result | no lease (silent gaps in testing); heartbeats (more traffic and code for the same guarantee) |
| ADR-23 | Configuration reloads keep the last good version: a `policy.json` or `deployment.json` that doesn't parse leaves the previous one in force, writes `policy.invalid` to the audit log and logs an error; only a repository's first load fails outright | a typo must neither open a repository (fail open) nor lock everyone out (an outage) | the operator sees the error in the audit log, the logs and the superfan; the fix applies on the next request | failing every request until the file is fixed; falling back to an empty policy |
| ADR-24 | Cloud Spanner holds the metadata, as in the article; SQLite stays as the single-host backend; `deployment.json` chooses. Spanner is reached through its REST API over HTTPS with the standard library (CON-01). One database per deployment; every table's key starts with the repository; keys avoid hotspots (hashes for changesets, per-ref versions for the ref log, counters only for low-rate ids). Every read-write operation is a transaction function rerun on abort; reads are strong; immutable rows are cached in-process. Development and tests use Google's official emulator; real Spanner is configuration: project, instance, database, and an access token from the GCE metadata server or a token command such as `gcloud auth print-access-token` | the article's refs are "a compare-and-swap on a single Spanner row" and its servers "write the results back to Spanner"; decided 2026-10-14 (12 §12.9) | metadata scales across machines like the rest of the fleet; each metadata call is an HTTPS round trip, so per-process caching matters more; the emulator runs one read-write transaction at a time and aborts the rest, so tests exercise the retry path hard; service-account key files are not supported directly (signing them needs RSA, which the standard library lacks) | the official client library (gRPC, third-party: breaks CON-01); PostgreSQL; replicating SQLite ourselves |
| ADR-25 | Superfan agents: each finding goes to Claude (the latest Opus model by default, configurable with `--agent-model`) through the Messages API over HTTPS with the standard library, in a loop the agent runs itself. Adaptive thinking at effort `high`; server-side refusal fallbacks on; read-only tools (stats, logs, baselines, recent findings); limits on model turns and output tokens; repeated findings investigated once. Tool results and log lines are data, never instructions. The analysis goes to the same Slack-compatible webhook as the finding | the article's superfans are Claude agents with "access to our telemetry and logs"; decided 2026-10-14; plain HTTPS was chosen with the option (CON-01) | each investigation costs model tokens, bounded per finding; the monitor never depends on the agent: without the API, findings still arrive, with a note | the official SDK (third-party: breaks CON-01); Managed Agents (its tools would still have to reach the components); no agent |
| ADR-26 | The comparison with git serves the same repository both ways on one host: git through `git upload-pack` (what a git server runs for every clone, measured with the CPU and peak memory of that process), Scion through its daemon, cache and server (measured on those processes); both produce the same working copy | the article's claims are relative to git servers ("requires significantly less CPU than git servers"; a footprint "200x smaller"); decided 2026-10-14 | the numbers are single-host and relative; they show where the costs go (git computes a pack for every clone; Scion's tiers serve stored objects) rather than fleet-wide savings | comparing against a hosted git service (not reproducible); synthetic models of git's cost |
| ADR-27 | Line diffs (blame, three-way merge) use Myers' O((N+M)·D) algorithm after matching the common prefix and suffix and leaving out the lines that occur on one side only (they can't be matched, so the result is still a shortest edit and D counts only lines that moved); an edit of more than 2,000 lines even then falls back to difflib | the CPython pilot found the first blame of `Python/ceval.c` taking 172 s at 10% of the history: blame diffs every file a changeset touches, and whole-file difflib matching without its junk heuristic is quadratic on files of repeated lines (changelogs, long C sources); with the heuristic, files made mostly of repeated lines align badly (a 24,000-line test lost 20,000 unchanged lines) | a diff costs about the size of the change (59 versions of ceval.c: 0.1 s instead of 2.3 s); the pilot's rerun then found Myers itself spending 8.4 of 12.6 s of a blame backfill on large edits, and leaving out one-sided lines cut the diffs of CPython's first 1,500 commits from 9.1 s to 1.0 s, with the same LCS lengths; alignments of ambiguous duplicate lines can differ from difflib's, all of them shortest edits; new blame values follow the new alignment. Lines end at "\n" only, as git counts them, in blame, grep, diffs and the review pages (a form feed or a lone "\r" is part of a line) | difflib with its junk heuristic (wrong alignments); patience diff (still needs a fallback when no line is unique); keeping difflib (minutes per hot file) |
| ADR-28 | `GET /logs` is open to administrators, service principals and the *log readers* named in deployment.json (`log_readers`, default `superfan`); the superfan's identity is a log reader, not a service principal | the B6 review found that a superfan, made a service principal so it could read logs, could act on behalf of any user, administrators included, with a token kept beside the Anthropic key in a process that sends logs to a third party | a stolen superfan token reads logs and nothing more; a deployment that already lists `superfan` among `service_principals` keeps that grant until it removes it | a log-only token scope; leaving the monitor a service |
