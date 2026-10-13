# Scion RPC reference

Every query the `scn` client makes is one of these RPCs, so any CI job or tool can use them
without a checkout. The article suggests forges could standardize something similar.

**Transport.** Requests are `POST /rpc/<method>` with the body `{"params": {...}}`, and responses
are `{"result": ...}`. Errors return `{"error": {"code", "message", "data"}}` with these HTTP
statuses:
- 400: bad request
- 401: unauthenticated
- 403: permission denied or tiering violation
- 404: not found
- 409: merge conflict (`data.conflicts`)
- 429: rate limited (honor `Retry-After`)

**Headers.**
- `X-Scion-User`: the caller's identity.
- `Authorization: Bearer <token>`: required when the policy defines tokens.
- `X-Scion-Tier`: one of `client`, `daemon` or `cache`. The daemon and cache tiers must be the
  `scion-daemon` and `scion-cache` principals.
- `X-Scion-On-Behalf-Of`: lets a service principal pass along the end user's identity, whose
  permissions then apply.

**Repositories (ADR-13).** One deployment hosts many repositories. Every RPC below and the object
protocol take a `repo` parameter that names the repository (the CLI reads it from the working copy).

**Revisions.** Any `rev` accepts a ref name, a full changeset id, a unique id prefix of at least
4 hex characters, and `~N` (first-parent ancestor) and `^N` (Nth parent) suffixes, for example
`main~3` or `3fa2c9^2`.

**Request classes.** These drive rate limiting: **read**, **heavy**, **write** and **objects**.

## Metadata

| Method | Params | Returns | Class |
|---|---|---|---|
| `whoami` | | principal, effective user, tier, admin | read |
| `server_info` | | changeset count, refs, derived-data counts | read |
| `resolve` | `rev` | changeset id | read |
| `get_changeset` | `rev` | parents, author, message, timestamp, changes (relative to the first parent), generation, copies | read |
| `get_changesets` | `ids` | list of the above | read |
| `log` | `rev`, `limit`, `skip`, `path?`, `first_parent=true`, `ids_only?` | changesets, newest first (`path` → that path's history) | read |
| `root_tree` | `rev` | tree id | read |
| `list_dir` | `rev`, `path` | entries `{name, path, kind, id}`, filtered by the caller's permissions | read |
| `read_file` | `rev`, `path` | `{kind, blob, content_b64}` | read |
| `diff` | `b`, `a?` (default: first parent of `b`), `merge_base?`, `paths?`, `text?`, `context?` | `{a, b, files: [{path, status, old, new}], text?}` | read |
| `merge_base` | `a`, `b` | `{base, all}` | read |
| `is_ancestor` | `a`, `b` | bool | read |
| `fp_ancestor` | `rev`, `n` | the first-parent ancestor `n` steps back (O(log n)) | read |
| `file_history` | `rev`, `path`, `limit`, `follow_copies=true` | `[{cs, path}]` for a file or directory | heavy |
| `blame` | `rev`, `path` | `{lines: [{line, cs, origin_line, text}], changesets: {id: {author, timestamp, summary}}}` | heavy |
| `search_paths` | `rev`, `query`, `limit` | `{paths, trees_visited}` | heavy |
| `grep` | `rev`, `pattern`, `path?`, `regex=true`, `ignore_case?`, `limit` | `{matches: [{path, line, text}], files_scanned, truncated}` | heavy |
| `list_refs` / `get_ref` / `ref_log` | `name` | refs and their compare-and-swap history | read |

## Writes

| Method | Params | Notes |
|---|---|---|
| `has_objects` | `ids` | returns the ids the server does **not** have |
| `put_objects` | binary framing (below) | blobs only; integrity is verified; trees are always derived on the server |
| `create_changeset` | `parents`, `files: [{path, delete} \| {path, kind, blob} \| {path, kind, content_b64}]`, `message`, `author?`, `timestamp?`, `extra?`, `update_ref? {name, old, record_landing?}` | creates the changeset on the server; no locks; an optional ref compare-and-swap |
| `merge` | `ours`, `theirs`, `message?`, `ff?` | 409 with structured conflicts |
| `rebase` | `head`, `onto`, `base?` | rebases a whole stack: `{head, rebased: {old: new}}` |
| `revert` | `cs`, `onto`, `message?` | three-way revert of `cs` on top of `onto` |
| `update_ref` | `name`, `old` (null = must not exist), `new` (null = delete) | compare-and-swap on one row; protected refs are enforced |
| `derive` | `type`, `rev` | admins only: backfill a deferred derived-data type |

## Object protocol (identical on scion-daemon, scion-cache and scion-server)

`get_objects` takes `{"ids": [...]}` (at most 2,000 per request) and responds with
`application/octet-stream` containing repeated records:

```
[32-byte raw id][1-byte flags][4-byte big-endian length][zlib-compressed "type\0payload"]
flags: 0x1 restricted (do not cache)   0x2 missing   0x4 denied
```

The request lists only the objects the caller *wants*. It never describes what the caller
already has. Only `blob` and `tree` objects are served; derived structures stay internal.

Each tier accepts requests only from the tier directly below it:

| Tier | Accepts requests from |
|---|---|
| server | `cache` (plus `client` with `--allow-direct-objects`, for development) |
| cache | `daemon` |
| daemon | `client` |

## Antique (code review and landing)

| Method | Params | Notes |
|---|---|---|
| `antique.create` | `title`, `head`, `description?`, `target=main` | no branch is needed: the CR points at a changeset |
| `antique.update` | `id`, `head` | a new revision resets approvals |
| `antique.get` / `antique.list` | `id` / `state?`, `author?` | includes the evaluated requirements |
| `antique.approve` / `antique.comment` | `id` / `id`, `body`, `path?`, `line?` | self-approval never counts |
| `antique.requirements` | `id` | per-scope category (docs, comment-only, logic), needed vs present approvals and owner approvals |
| `antique.land` | `id`, `force?` | server-side rebase and a single compare-and-swap; per-server group commit; 409 on conflict |
| `antique.land_changeset` | `cs`, `ref` | services and admins: land a changeset without a CR (e.g. reverts) |
| `antique.find_landing` | `cs` (landed id or pre-rebase id) | `{cs, source, cr, ref, landed_at}`, an indexed lookup |
| `antique.postmerge_claim` / `postmerge_report` / `postmerge_status` | | the post-merge testing queue |

A read-only HTML view is served at `GET /antique` and `GET /antique/cr/<id>`. Every tier also
serves `GET /healthz` and `GET /stats`.
