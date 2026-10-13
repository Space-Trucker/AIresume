# 13. Glossary

| Term | Meaning |
|---|---|
| Agent | an automated coding client (for example Claude) that reads and writes code through Scion |
| Antique | the code review and landing service |
| Approval rule | per-directory requirement for approvals, by change category (docs, comment-only, logic), optionally from owners |
| Blame | for each line of a file, the changeset (and line) that introduced it |
| Blob | a content-addressed object holding file bytes |
| Bloom filter | a compact probabilistic set; here, the trigrams of every name beneath a directory, used to prune path searches |
| Change request (CR) | a review unit pointing at a changeset; has revisions, comments and approvals |
| Changeset | the unit of work: an entry in the write-ahead log listing the files changed relative to its first parent |
| Compare-and-swap (CAS) | atomic "set X to new if X still equals expected"; the only way refs move |
| Content addressing | naming data by the hash of its contents, so it can never change under the same name |
| Daemon (`scion-daemon`) | the per-node object cache, reached by local jobs over a Unix socket |
| Deferred (derived type) | computed the first time someone asks, then stored |
| Deployment | one Scion installation: `deployment.json` (principals, tokens, groups, limits) plus many repositories, each with its own `policy.json` (ADR-13) |
| Deploy gate | picks the newest changeset that passed post-merge testing |
| Derived data | anything computed from changesets (trees, history, skip lists, blame, indexes) through the generic recursive mechanism |
| Eager (derived type) | computed when the changeset is created |
| First parent | the main-line parent of a changeset; changes and history are expressed relative to it |
| fsmonitor | the filesystem watcher that lets `status` look only at changed paths |
| Generation number | 1 + the maximum generation of a changeset's parents; ancestors always have smaller ones |
| Group commit | batching several concurrent landings into one rebase chain and one CAS |
| History tree (htree) | a derived tree whose entries carry the last changeset that changed each path |
| Landing | publishing an approved change on a target ref by server-side rebase plus CAS |
| Merge base | the best common ancestor(s) of two changesets |
| Mutual TLS | TLS in which the client also presents a certificate; between tiers its common name is the service principal (ADR-14) |
| On-behalf-of | a service principal forwarding the identity of the end user whose permissions apply |
| Post-merge testing | testing changes after they land, with automatic revert, instead of a pre-merge queue |
| Principal | an authenticated identity: a user, a group member, or a service (`antique`, `scion-cache`, `scion-daemon`, `postmerge`) |
| Ref | a pointer to a changeset, such as a branch or tag (the article: "pointers to commits, such as branches and tags"); discouraged except for `main` and release branches |
| Restricted object | an object under a read-restricted directory, or of a repository not readable by everyone; never cached by shared tiers |
| Revision | a changeset reference: id, prefix, ref, with `~N` / `^N` suffixes; also, one upload of a CR |
| Root tree | the tree object describing a changeset's full directory structure (derived) |
| `scion-cache` | the regional in-memory object cache |
| `scion-server` | the authoritative API server |
| `scn` | the Scion client and CLI |
| Single flight | collapsing concurrent requests for the same missing object into one upstream request |
| Skip list | per-changeset pointers to first-parent ancestors 2^k steps back, for O(log n) jumps |
| Snapshot | a file of public objects reachable from a revision, used to warm-start daemons |
| Sparse checkout | a working copy containing only selected directories |
| Strict tiering | each tier serves object requests only from the tier directly below it |
| Superfan | a monitor obsessively focused on one component's telemetry |
| Sync cookie | a file created to prove the watcher has processed every earlier event |
| Tree | a content-addressed directory listing: name, kind, id |
| Virtual checkout | a working copy whose files appear only when read |
| Want-only protocol | fetching by naming the objects wanted, never describing what the client has |
| Working copy | files on disk plus `.scn/` state for one checkout |
| Write-ahead log | the append-only sequence of changesets |
