# 13. Glossary

| Term | Meaning |
|---|---|
| `scion-cache` | the regional in-memory object cache |
| `scion-server` | the authoritative API server |
| `scn` | the Scion client and CLI |
| Abort (Spanner) | Spanner's answer to a read-write transaction that conflicts with another: the transaction is rolled back and must run again from the start; Scion retries it with backoff (FR-ST-03) |
| Agent | an automated coding client (for example Claude) that reads and writes code through Scion |
| Antique | the code review and landing service |
| Approval rule | per-directory requirement for approvals, by change category (docs, comment-only, logic), optionally from owners |
| Audit log | the per-repository, hash-chained, append-only record of policy loads, denials, ref moves and administrative actions (ADR-15) |
| Backup | a consistent copy of a deployment's authoritative stores, taken while servers run: the metadata store first (SQLite online backup), then the blob storage, with a manifest of refs, counts and checksums (FR-AD-06) |
| Bisect | finding the first changeset on a first-parent range for which a predicate fails, in ⌈log₂ n⌉ server-side probes, without a checkout (FR-AUT-01) |
| Blame | for each line of a file, the changeset (and line) that introduced it |
| Blob | a content-addressed object holding file bytes |
| Bloom filter | a compact probabilistic set; here, the trigrams of every name beneath a directory, used to prune path searches |
| Change request (CR) | a review unit pointing at a changeset; has revisions, comments and approvals |
| Changeset | the unit of work: an entry in the write-ahead log listing the files changed relative to its first parent |
| Claim token | the token a post-merge worker receives with a job; its report must carry it, so a worker whose lease ran out can't overwrite the result of the worker that took the job over (ADR-22) |
| Cloud Spanner | Google's distributed, strongly consistent SQL database; the article's metadata store, and Scion's from B6 (ADR-24) |
| Compare-and-swap (CAS) | atomic "set X to new if X still equals expected"; the only way refs move |
| Content addressing | naming data by the hash of its contents, so it can never change under the same name |
| Content index | the deferred derived index of trigram → blob postings that lets grep read only the blobs that can match (ADR-16) |
| Daemon (`scion-daemon`) | the per-node object cache, reached by local jobs over a Unix socket |
| Deferred (derived type) | computed the first time someone asks, then stored |
| Deploy gate | picks the newest changeset that passed post-merge testing |
| Deployment | one Scion installation: `deployment.json` (principals, tokens, groups, limits) plus many repositories, each with its own `policy.json` (ADR-13) |
| Derived data | anything computed from changesets (trees, history, skip lists, blame, indexes) through the generic recursive mechanism |
| Eager (derived type) | computed when the changeset is created |
| Emulator (Spanner) | Google's official local Spanner emulator, used for development and tests; it runs one read-write transaction at a time and aborts the others (R-17) |
| Finding | what a superfan raises: novel (a metric far from its learned baseline), threshold (a configured rule), unreachable, restarted, or resolved; it carries the component's log lines around it |
| First parent | the main-line parent of a changeset; changes and history are expressed relative to it |
| fsmonitor | the filesystem watcher that lets `status` look only at changed paths |
| Generation number | 1 + the maximum generation of a changeset's parents; ancestors always have smaller ones |
| Git map | the two-way mapping between ingested git commits and their changesets (FR-MG-07) |
| Group commit | batching several concurrent landings into one rebase chain and one CAS |
| History tree (htree) | a derived tree whose entries carry the last changeset that changed each path |
| Landing | publishing an approved change on a target ref by server-side rebase plus CAS |
| Landing stack | every changeset one landing put on the target, which a revert must undo together |
| Lease | how long a claimed post-merge job may go without a report before it returns to the queue (ADR-22) |
| Log ring | the in-memory buffer of a component's recent structured log entries, served at `GET /logs` (ADR-18) |
| Merge base | the best common ancestor(s) of two changesets |
| Mutual TLS | TLS in which the client also presents a certificate; between tiers its common name is the service principal (ADR-14) |
| Object index | the per-repository record of where each object appears and which directory restricts it (`object_acl`); it decides which objects are restricted |
| On-behalf-of | a service principal forwarding the identity of the end user whose permissions apply |
| Possession grant | a short-lived record that a user uploaded the exact bytes of a restricted object, so they may commit those bytes by id |
| Post-merge testing | testing changes after they land, with automatic revert, instead of a pre-merge queue |
| Principal | an authenticated identity: a user, a group member, or a service (`antique`, `scion-cache`, `scion-daemon`, `postmerge`) |
| Read-write transaction | a Spanner transaction that reads and then commits writes atomically; locks are checked at commit, which may abort it |
| Ref | a pointer to a changeset, such as a branch or tag (the article: "pointers to commits, such as branches and tags"); discouraged except for `main` and release branches |
| Restricted object | an object under a read-restricted directory, or of a repository not readable by everyone; never cached by shared tiers |
| Revision | a changeset reference: id, prefix, ref, with `~N` / `^N` suffixes; also, one upload of a CR |
| Root tree | the tree object describing a changeset's full directory structure (derived) |
| Session (Spanner) | a server-side context in which Spanner requests run; clients keep a pool of them |
| Single flight | collapsing concurrent requests for the same missing object into one upstream request |
| Skip list | per-changeset pointers to first-parent ancestors 2^k steps back, for O(log n) jumps |
| Snapshot | a file of public objects reachable from a revision, used to warm-start daemons |
| Sparse checkout | a working copy containing only selected directories |
| Strict tiering | each tier serves object requests only from the tier directly below it |
| Superfan | a monitor obsessively focused on one component, reading its telemetry and its logs (FR-OP-03, FR-OP-08) |
| Superfan agent | Claude, investigating a superfan finding with read-only tools over the component's stats, logs and baselines, and posting its analysis beside the finding (FR-OP-09, ADR-25) |
| Sync cookie | a file created to prove the watcher has processed every earlier event |
| Tree | a content-addressed directory listing: name, kind, id |
| upload-pack | the git program a git server runs for every clone and fetch: it negotiates with the client and builds a pack; Scion's comparison with git measures it (ADR-26) |
| Virtual checkout | a working copy whose files appear only when read |
| Want-only protocol | fetching by naming the objects wanted, never describing what the client has |
| Working copy | files on disk plus `.scn/` state for one checkout |
| Write-ahead log | the append-only sequence of changesets |
