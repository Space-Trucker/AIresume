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
| Storage | `objects`, `storage`, `meta` | compressed content-addressed objects; changeset log, refs, derived values, indexes |
| Core | `changeset`, `trees`, `derived`, `derived_types`, `merge3`, `repo` | changeset semantics, incremental trees, derived data, history and blame, ancestry, merge, rebase, revert |
| Policy | `iam`, `ratelimit`, `classify` | permissions, rate limits, change classification |
| Services | `rpc`, `server`, `tiers`, `snapshot`, `antique`, `search` | RPC surface, tiers, review and landing, search |
| Client | `client`, `fsmonitor`, `cli` | working copies, monitoring, CLI |
| Tooling | `ingest`, `postmerge`, `tools/*`, `superfan` | migration, post-merge, bisect, revert, monitoring, benchmarks |

## 7.4 Process and concurrency view

| Concern | Mechanism |
|---|---|
| Changeset creation | idempotent append keyed by content hash; no locks; eager derived data computed right after |
| Derived data races | values are deterministic, written with insert-or-ignore; a per-process single-flight lock avoids duplicate work |
| Refs | single-row compare-and-swap; every success is appended to the ref log |
| Landing | per-server, per-target group commit: one leader drains the queue, rebases a chain, does one CAS; retries with jittered exponential backoff up to a deadline; servers never coordinate except through the CAS |
| Cache misses | single flight per object id; waiters re-read the store or re-request |
| Request handling | a thread per connection (HTTP/1.1 keep-alive); per-thread SQLite connections in WAL mode |
| Client fetch | breadth-first by tree level; blob batches fetched in parallel |
| Status | a filesystem watcher process journals events; the sync cookie orders queries after earlier events |

**Consistency model**
* **Changesets and objects:** immutable, read-your-writes from any server sharing the store.
* **Refs:** linearizable through compare-and-swap.
* **Derived data:** eventually present and always identical (a deterministic function of immutable inputs).
* **Tiers:** never stale for content (it is immutable). Only the ACL classification can change, by policy
  update, which requires re-indexing and a cache restart (R-07).

## 7.5 Deployment and scaling view

Deployment diagram: [6.3](06-uml.md#63-deployment).

| Component | State | Scales by | Fails how | Effect of failure |
|---|---|---|---|---|
| scion-daemon | bounded disk cache | one per node | crash | jobs on that node fall back to the cache tier after restart; nothing is lost |
| scion-cache | memory | instances per region | crash | daemons fail over to another cache; single flight limits the herd on servers |
| scion-server | stateless (plus per-process caches) | instances | crash | caches and clients fail over; no data loss |
| Metadata store | authoritative | the database's own scaling (Spanner) | outage | writes stop; tiers keep serving cached content |
| Blob storage | authoritative | the storage service | outage | misses fail; hits keep working |

## 7.6 Data view

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

**Metadata schema:** see the ER diagram in [6.9](06-uml.md#69-metadata-store-er).

## 7.7 Protocols

* **RPC:** `POST /rpc/<method>`, JSON in and out; error envelope `{error: {code, message, data}}`;
  stable HTTP statuses 400/401/403/404/409/429/500.
* **Identity headers:** `X-Scion-User`, `Authorization: Bearer`, `X-Scion-Tier`, `X-Scion-On-Behalf-Of`.
* **Objects:** `get_objects {ids}` returns repeated `[32B id][1B flags][4B len][stored bytes]`.
  The flags are RESTRICTED, MISSING and DENIED.
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

## 7.10 Cross-cutting concerns

* **Security:** see [08-security.md](08-security.md).
* **Observability:** `/healthz` and `/stats` everywhere; latency percentiles per method; superfans.
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
| ADR-07 | Land with server-side rebase plus ref CAS, and per-server group commit | a global merge-queue lock doesn't scale (§What we learned, "We're completely rethinking our priors") | concurrent landings can conflict; post-merge testing is required | serialized merge queue |
| ADR-08 | Post-merge testing with auto-revert and a deploy gate | pre-merge CI can't keep up | main can be briefly red; the deploy gate protects production | pre-merge testing of every change against the tip |
| ADR-09 | Semantic approval classes (docs, comment-only, logic) with owners | human attention is scarce | the classifier must be conservative (unknown means logic) | uniform approval counts |
| ADR-10 | SQLite (WAL) and a directory stand in for Spanner and blob storage | prototype; CON-01/02 | single host; interfaces kept narrow for a swap | embedding a distributed store |
| ADR-11 | Python standard library only | CON-01; reviewable, portable | slower than a compiled implementation | adding dependencies (gRPC, FUSE, RocksDB) |
| ADR-12 | Generation numbers plus first-parent skip lists for ancestry | O(log n) queries on very long histories | an extra derived row per changeset | BFS over parents; reachability bitmaps |
