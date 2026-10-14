# Adding a derived-data type

Everything that is not part of a changeset is derived data, computed by one generic mechanism
(`scion/derived.py`). A type defines how to compute its value for a changeset from that changeset
and the values of the same type for its parents. The manager walks back to the nearest ancestors
that already have values and derives forward in topological order. Values are written back to
the metadata store, and because they are deterministic, servers never need to coordinate.

```python
from scion.derived import DerivedType

class FileCount(DerivedType):
    name = "filecount"
    eager = False              # deferred: computed the first time someone asks
    depends_on = ("tree",)     # derived first for the same changeset (and its ancestors)

    def derive(self, repo, cs_id, cs, parent_values):
        base = int(parent_values[0]) if parent_values else 0
        delta = sum(1 if c.op == "A" else -1 if c.op == "D" else 0 for c in cs.changes)
        return str(base + delta)

repo.derived.register(FileCount())
repo.derived.get("filecount", repo.resolve("main"))
```

Guidelines:

* **Stay incremental.** Use the changeset's own `changes` (relative to the first parent) and the
  parents' values, so the cost tracks the size of the change. For tree-shaped data, write a
  `trees.TreeCodec` and call `trees.apply_augmented`, as `history` and `search` do.
* **Store large values as objects.** Put them in the object store and return the id, as `tree`,
  `history`, `search` and `blame` do. Internal object types are never served to clients.
* **Choose eager or deferred.** Make a type eager if every changeset needs it soon after creation
  (trees, graph); otherwise defer it (blame). `scion-admin derive --type NAME` backfills a
  deferred type ahead of demand, and `scion-admin ingest` computes blame for each commit it
  imports (decided 2026-10-14), so the first query after a migration doesn't pay for the history.
* **Change freely.** Clients only ever see query APIs, so a type's representation can change
  without touching any client.

The built-in types are `tree`, `graph` (generation numbers plus first-parent skip lists),
`history` (path history), `copies` (copy and rename detection), `search` (bloom-filtered path
index) and `blame`. The grep content index is not a derived type: it covers the revisions that
are searched rather than every changeset (ADR-16).
