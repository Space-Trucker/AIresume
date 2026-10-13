# Scion RPC reference

Every query the `scn` client makes is one of these RPCs, so any CI job or tool can use them
without a checkout. The article suggests forges could standardize something similar.

> **Availability.** Everything below is built and tested (milestones B2–B4; see
> [design/11-traceability.md](design/11-traceability.md)).

**Transport.** Requests are `POST /rpc/<method>` with the body `{"params": {...}}` and a
`Content-Length` (chunked bodies get 411), and responses are `{"result": ...}`. Errors return
`{"error": {"code", "message", "data"}}` with these HTTP statuses:
- 400: bad request, or an object that fails verification (`integrity`)
- 401: unauthenticated
- 403: permission denied or tiering violation
- 404: not found (unknown method, revision, path or repository)
- 409: merge conflict (`data.conflicts`)
- 413: request body over 512 MB, or a file over the repository's per-file limit
- 429: rate limited: wait `Retry-After` seconds (`data.retry_after` has the exact value)
- 502/503 from a cache or daemon: its upstream sent a bad object, or no upstream answered

**Endpoints.** `http://host:port` (development), `https://host:port` (TLS 1.2 or later) and
`unix:/path` (the node daemon). Servers and caches can require mutual TLS: then the client
certificate's common name is the service principal, and the `scion-cache` and `scion-daemon`
principals must authenticate that way (ADR-14). Clients and tiers accept several equivalent
endpoints and fail over between them.

**Headers.**
- `X-Scion-User`: the caller's identity.
- `Authorization: Bearer <token>`: required when `deployment.json` defines tokens (stored plain or
  as `sha256:<hex>`, see `scion-admin hash-token`).
- `X-Scion-Tier`: one of `client`, `daemon` or `cache`. The daemon and cache tiers must be the
  `scion-daemon` and `scion-cache` principals.
- `X-Scion-On-Behalf-Of`: lets a service principal pass along the end user's identity, whose
  permissions then apply.

**Repositories (ADR-13).** One deployment hosts many repositories. Every RPC below and the object
protocol take a `repo` parameter that names the repository (the CLI reads it from the working copy);
`deployment.json` may name a `default_repo` for requests without one. Each repository's
`policy.json` decides who may read and write it; a caller who may not read a repository gets 403
from every RPC on it, and DENIED for its objects.

**Revisions.** Any `rev` accepts a ref name, a full changeset id, a unique id prefix of at least
4 hex characters, and `~N` (first-parent ancestor) and `^N` (Nth parent) suffixes, for example
`main~3` or `3fa2c9^2`.

**Request classes.** These drive rate limiting: **read**, **heavy**, **write** and **objects**.

## Metadata

| Method | Params | Returns | Class |
|---|---|---|---|
| `whoami` | `repo?` | principal, effective user, tier, how the principal was established (`token`, `cert`, `trusted`), admin, and `repo_admin` | read |
| `list_repos` | | the repositories the caller may read: `{name, public, writable}` | read |
| `server_info` | `repo?` | with `repo`: changeset count, refs, derived-data counts; without: the readable repositories | read |
| `tier_info` | | `{tier, object_callers}`: every tier answers it, so a tier can check its upstream | read |
| `resolve` | `rev` | changeset id | read |
| `get_changeset` | `rev` | parents, author, message, timestamp, changes (relative to the first parent), generation, copies | read |
| `get_changesets` | `ids` | list of the above | read |
| `log` | `rev`, `limit`, `skip`, `path?`, `first_parent=true`, `ids_only?` | changesets, newest first (`path` → that path's history) | read |
| `root_tree` | `rev` | tree id | read |
| `list_dir` | `rev`, `path`, `probe?` | entries `{name, path, kind, id}`, filtered by the caller's permissions; 403 if nothing beneath is readable, or `null` with `probe` (how checkouts look past a denied tree without an audited denial) | read |
| `read_file` | `rev`, `path` | `{kind, blob, content_b64}` | read |
| `diff` | `b`, `a?` (default: first parent of `b`), `merge_base?`, `paths?`, `text?`, `context?` | `{a, b, files: [{path, status, old, new}], text?}` | read |
| `merge_base` | `a`, `b` | `{base, all}` | read |
| `is_ancestor` | `a`, `b` | bool | read |
| `fp_ancestor` | `rev`, `n` | the first-parent ancestor `n` steps back (O(log n)) | read |
| `file_history` | `rev`, `path`, `limit`, `follow_copies=true` | `[{cs, path}]` for a file or directory | heavy |
| `blame` | `rev`, `path` | `{lines: [{line, cs, origin_line, text}], changesets: {id: {author, timestamp, summary}}}` | heavy |
| `search_paths` | `rev`, `query`, `limit` | `{paths, trees_visited}` | heavy |
| `grep` | `rev`, `pattern`, `path?`, `regex=true`, `ignore_case?`, `limit` | `{matches: [{path, line, text}], files_scanned, indexed, truncated}`: with 3 or more literal characters, the trigram content index narrows the files read (`indexed`) | heavy |
| `git_lookup` | `git` or `cs` | `{git, cs}` for an ingested commit, either way round; `null` if not ingested | read |
| `list_refs` / `get_ref` / `ref_log` | `name` | refs and their compare-and-swap history | read |

## Writes

| Method | Params | Notes |
|---|---|---|
| `has_objects` | `ids` | writers only: returns the ids the server does **not** have, so uploads skip known content |
| `put_objects` | `POST /rpc/put_objects?repo=<name>` with the binary framing (below) | writers only; blobs only, each verified against its id; trees are always derived on the server; nothing is stored if any object is invalid or over the per-file limit (413) |
| `create_changeset` | `parents`, `files: [{path, delete} \| {path, kind, blob} \| {path, kind, content_b64}]`, `message`, `author?`, `timestamp?`, `extra?`, `update_ref? {name, old, record_landing?}` | creates the changeset on the server; no locks; an optional ref compare-and-swap, reported as `ref_updated`; the author is the caller unless the caller is an admin or a service; inline content over the per-file limit gets 413 |
| `merge` | `ours`, `theirs`, `message?`, `ff?` | 409 with structured conflicts |
| `rebase` | `head`, `onto`, `base?` | rebases a whole stack: `{head, rebased: {old: new}}` |
| `revert` | `cs`, `onto`, `message?` | three-way revert of `cs` on top of `onto` |
| `update_ref` | `name`, `old` (null = must not exist), `new` (null = delete) | compare-and-swap on one row; protected refs are enforced |
| `derive` | `type`, `rev` | admins only: backfill a deferred derived-data type |

## Object protocol (identical on scion-daemon, scion-cache and scion-server)

`get_objects` takes `{"repo": "<name>", "ids": [...]}` (at most 2,000 ids per request) and responds with
`application/octet-stream` containing repeated records:

```
[32-byte raw id][1-byte flags][4-byte big-endian length][zlib-compressed "type\0payload"]
flags: 0x1 restricted (do not cache)   0x2 missing   0x4 denied
```

The request lists only the objects the caller *wants*. It never describes what the caller
already has. Only `blob` and `tree` objects are served; derived structures stay internal.
Caches and daemons key what they store by (repository, id) and never store an object flagged
restricted: every object of a repository whose reads are not open to everyone is restricted. A
tier acting for a user sends `X-Scion-On-Behalf-Of`, so the user's permissions apply.

`acl_epochs {repos}` (same tiering as `get_objects`) returns each repository's ACL epoch. It changes
when a repository stops being readable by everyone and at every re-index; a tier checks it at least
every `--epoch-seconds` before serving a repository's objects and purges that repository when it
changed (ADR-20). Snapshots record the epoch they were taken under and are imported only under it.

Each tier accepts requests only from the tier directly below it:

| Tier | Accepts requests from |
|---|---|
| server | `cache` (plus `client` with `--allow-direct-objects`, for development) |
| cache | `daemon` |
| daemon | `client` |

## Antique (code review and landing)

| Method | Params | Notes |
|---|---|---|
| `antique.create` | `title`, `head`, `description?`, `target=main` | writers; no branch is needed: the CR points at a changeset; refused if the head is already in the target |
| `antique.update` | `id`, `head` | the author or an admin; a new revision resets approvals and clears a conflict |
| `antique.get` / `antique.list` | `id` / `state?`, `author?`, `limit?` | `get` includes the evaluated requirements; files and comments under directories the caller can't read are left out |
| `antique.approve` / `antique.comment` | `id` / `id`, `body`, `path?`, `line?` | approvals belong to the latest revision; self-approval never counts |
| `antique.requirements` | `id` | per-scope category (docs, comment-only, logic), needed vs present approvals and owner approvals |
| `antique.land` | `id`, `force?` | the author, a service or an admin; 403 listing the unmet scopes; the CR shows `landing` while queued; server-side rebase and one compare-and-swap with per-server group commit; 409 `conflict` with `data.conflicts`; 503 `retry` if contention outlasts the deadline; landing a landed CR returns it |
| `antique.abandon` | `id` | the author or an admin |
| `antique.land_changeset` | `cs`, `ref` | services and admins: land a changeset without a CR (e.g. reverts) |
| `antique.find_landing` | `cs` (landed id or pre-rebase id) | `{cs, source, cr, ref, landed_at, head}`, an indexed lookup; `null` if it never landed |
| `antique.landing_stack` | `cs` | every changeset of the landing that produced `cs`, newest first (what a revert must undo) |
| `antique.postmerge_claim` | | services and admins: claim the oldest queued job: `{id, cs, cr, ref, claim}`, or `null`. A job not reported within the lease (the policy's `review.postmerge_lease_seconds`, default 7200) is queued again |
| `antique.postmerge_report` | `id`, `passed`, `log?`, `claim?` | services and admins: record the result; with the `claim` from the claim, a report whose lease ran out (the job was claimed again) gets 400 |
| `antique.postmerge_reverted` | `id`, `reverts` | services and admins: mark a failed job's landing as reverted by these changesets |
| `antique.postmerge_status` | `ref`, `limit` | the post-merge testing queue, newest first |
| `antique.job_for` | `cs` | the newest post-merge job of a changeset, or `null` |
| `antique.deploy_gate` | `ref` | the newest changeset on `ref` whose tests passed, walking the main line from the tip: `{cs, job, cr, behind_tip}`, or `null`; never a failed, reverted or untested changeset |

Review rules, owners and webhooks live in the repository's `policy.json` under `review` (see
`antique.py`). Webhooks receive `{event, repo, text, cr, actor}` for `cr.created`, `cr.updated`,
`cr.approved`, `cr.commented`, `cr.conflict`, `cr.landed` and `cr.abandoned`.

## Refs, audit and administration

| Method | Params | Notes |
|---|---|---|
| `create_release` | `name`, `rev` | creates `release/<name>` (it must not exist) for principals allowed to move `release/*` |
| `audit_log` | `limit?`, `action?`, `before?` | admins: the repository's audit entries, newest first: `policy.load`, `policy.invalid`, `denied`, `ref.update`, `derive`, `acl.reindex`, `release.create`, `cr.force_land`, `land_changeset`, `admin.set_ref`, `ingest`, `backup`, `restore` |
| `audit_verify` | | admins: recompute the hash chain: `{ok, entries, first_bad, head}` |
| `reindex_acl` | | admins: rebuild the object index after a policy change (UC-22) |

## Error codes

Every error has a stable `code`: `bad_request`, `integrity`, `unauthenticated`, `permission_denied`,
`tiering`, `bad_tier`, `forbidden`, `not_found`, `unknown_method`, `conflict`, `too_large`,
`length_required`, `rate_limited`, `retry`, `bad_upstream`, `upstream_unavailable` and `internal`.

## Review pages

`GET /antique` lists change requests by repository and state, and `GET /antique/<repo>/cr/<id>`
shows one: requirements, approvals, comments (line comments inline in the diff) and the diff,
filtered by what the viewer may read. Sign in at `/antique/login` (user, plus token when tokens are
configured); the session cookie is HttpOnly and SameSite=Strict (Secure over TLS). Approve, comment
and land are forms that post to `/antique/<repo>/cr/<id>/{approve,comment,land}` with the session's
CSRF token, and run the same code as the RPCs.

## Health, stats and logs

Every tier serves `GET /healthz`, `GET /stats` and `GET /logs`.

* `/stats` (unauthenticated, so it names no repository): uptime; counters per RPC; errors by HTTP
  status; p50/p90/p99 latency per method; rate-limiter rejections. Caches and daemons add their
  object cache (`hits`, `misses`, `hit_rate`, `coalesced`, `upstream_requests`, bytes, evictions,
  `rejected_objects`, ACL-epoch purges and check failures); daemons add snapshot imports; servers
  add repository totals and the Antique landing queue (`land.*` counters, `land.queue_depth`,
  `postmerge.queued`, `postmerge.running`).
* `/logs?since=SEQ&limit=N&level=info` (administrators and service principals): the component's
  recent structured log entries, `{tier, last_seq, entries: [{seq, at, level, message, fields,
  repeats}]}`, oldest first. The ring keeps the last 2,000 entries; a message repeated back to back
  updates one entry and counts `repeats` (ADR-18). Superfans read it (FR-OP-08).
