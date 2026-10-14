"""Backup and restore of a deployment's authoritative stores (FR-AD-06, NFR-13; UC-30).

What is authoritative: each repository's metadata (changesets, refs and the ref log, the
derived-data index, change requests, landings, post-merge jobs, the audit log) and its blob storage
(``objects/``), plus the identity document (``deployment.json``) and each repository's policy
(``policy.json``). Caches and daemons hold nothing that can't be fetched again, so they are not
backed up: losing any tier loses no data.

The order makes a backup consistent while the servers keep running:

1. every repository's metadata is copied first, as of one moment (MetaStore.export): SQLite's online
   backup API, or on Spanner a read of every table at one timestamp, the same timestamp for every
   repository (FR-ST-04), all read before any blob is copied, so the timestamp stays within
   Spanner's version retention (an hour by default) however long the copy takes. Either way the
   copy is a SQLite file, ``meta.db``: one backup format for both backends;
2. the blob storage is copied afterwards. Objects are immutable and stored before any metadata
   refers to them, so everything the snapshot refers to is already there; objects stored after the
   snapshot are extras that nothing references, which is harmless (UC-30, extension).

A manifest records the refs at the snapshot, counts and checksums. Taking a backup and restoring
one are audited (ADR-15). A restore checks the backup against its manifest, moves an existing
deployment root aside rather than deleting it, loads the metadata into the restored deployment's
backend (which may differ from the backup's; metadata already in a Spanner database is never
overwritten), and checks that the restored refs match the manifest and that their trees are complete.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import time

from .changeset import Changeset
from .deployment import Deployment
from .meta import open_metastore
from .objects import KIND_DIR, ObjectError, decode_stored
from .storage import FileObjectStore, key_oid

FORMAT = 1


class BackupError(Exception):
    pass


def _sha256(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_file(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


def _copy_objects(src: str, dst: str) -> tuple[int, int]:
    """Copy every stored object (not the temporary files of writes in progress)."""
    n = size = 0
    for d, _, names in os.walk(src):
        for name in names:
            if name.startswith(".tmp-"):
                continue
            s = os.path.join(d, name)
            t = os.path.join(dst, os.path.relpath(s, src))
            if not os.path.exists(t):
                _copy_file(s, t)
            n += 1
            size += os.path.getsize(t)
    return n, size


def _read_snapshot(meta_path: str) -> dict:
    db = sqlite3.connect(f"file:{meta_path}?mode=ro", uri=True)
    try:
        refs = {name: target for name, target in db.execute("SELECT name, target FROM refs ORDER BY name")}
        changesets = db.execute("SELECT COUNT(*) FROM changesets").fetchone()[0]
        audit = db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name = 'audit'").fetchone()[0]
        last_audit = db.execute("SELECT MAX(seq) FROM audit").fetchone()[0] if audit else None
    finally:
        db.close()
    return {"refs": refs, "changesets": changesets, "audit_seq": last_audit}


def backup(root: str, out: str, actor: str | None = None) -> dict:
    """Back up the deployment at ``root`` into the new directory ``out``; returns the manifest."""
    root, out = os.path.abspath(root), os.path.abspath(out)
    if os.path.exists(out) and os.listdir(out):
        raise BackupError(f"{out} is not empty")
    dep = Deployment(root)
    try:
        names = dep.names()
        os.makedirs(out, exist_ok=True)
        manifest = {"format": FORMAT, "created": time.time(), "source": root, "repos": {},
                    "deployment_json_sha256": None, "metadata_backend": dep.metadata.get("backend", "sqlite")}
        ident = os.path.join(root, "deployment.json")
        if os.path.exists(ident):
            _copy_file(ident, os.path.join(out, "deployment.json"))
            manifest["deployment_json_sha256"] = _sha256(os.path.join(out, "deployment.json"))
        at = None
        for name in names:  # 1: every repository's metadata, as of one moment
            src, dst = dep.repo_dir(name), os.path.join(out, "repos", name)
            _copy_file(os.path.join(src, "policy.json"), os.path.join(dst, "policy.json"))
            at = dep.repo(name).meta.export(os.path.join(dst, "meta.db"), at)
        for name in names:  # 2: then the blobs
            src, dst = dep.repo_dir(name), os.path.join(out, "repos", name)
            meta = os.path.join(dst, "meta.db")
            objects, size = _copy_objects(os.path.join(src, "objects"), os.path.join(dst, "objects"))
            entry = {"policy_sha256": _sha256(os.path.join(dst, "policy.json")), "meta_sha256": _sha256(meta),
                     "objects": objects, "object_bytes": size}
            if os.path.exists(meta):
                entry.update(_read_snapshot(meta))
            manifest["repos"][name] = entry
        with open(os.path.join(out, "manifest.json.tmp"), "w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        os.replace(os.path.join(out, "manifest.json.tmp"), os.path.join(out, "manifest.json"))
        digest = _sha256(os.path.join(out, "manifest.json"))
        for name in names:
            dep.repo(name).audit.append("backup", actor, out, {"manifest_sha256": digest,
                                                               "changesets": manifest["repos"][name].get("changesets")})
        return manifest
    finally:
        dep.close()


def check_backup(path: str) -> dict:
    """The manifest of an intact backup; BackupError when a file is missing or altered."""
    path = os.path.abspath(path)
    try:
        with open(os.path.join(path, "manifest.json")) as f:
            manifest = json.load(f)
    except (OSError, ValueError) as e:
        raise BackupError(f"{path} has no readable manifest: {e}") from None
    if manifest.get("format") != FORMAT:
        raise BackupError(f"unsupported backup format {manifest.get('format')!r}")
    problems = []
    if _sha256(os.path.join(path, "deployment.json")) != manifest.get("deployment_json_sha256"):
        problems.append("deployment.json")
    for name, entry in manifest["repos"].items():
        d = os.path.join(path, "repos", name)
        for f, key in (("policy.json", "policy_sha256"), ("meta.db", "meta_sha256")):
            if _sha256(os.path.join(d, f)) != entry.get(key):
                problems.append(f"repos/{name}/{f}")
        count = sum(1 for _, _, fs in os.walk(os.path.join(d, "objects")) for x in fs if not x.startswith(".tmp-"))
        if count < entry.get("objects", 0):
            problems.append(f"repos/{name}/objects ({count} of {entry['objects']} objects)")
    if problems:
        raise BackupError("the backup is damaged: " + ", ".join(problems))
    return manifest


def restore(path: str, root: str, force: bool = False, deep: bool = False, actor: str | None = None,
            metadata: dict | None = None) -> dict:
    """Restore the backup at ``path`` into ``root``. A non-empty ``root`` is moved aside with
    ``force``, never deleted. ``metadata`` is the restored deployment's metadata backend (the
    ``metadata`` section of deployment.json); by default the backup's own. Returns the verification
    report."""
    path, root = os.path.abspath(path), os.path.abspath(root)
    manifest = check_backup(path)
    identity = None
    if os.path.exists(os.path.join(path, "deployment.json")):
        with open(os.path.join(path, "deployment.json")) as f:
            identity = json.load(f)
    if metadata is not None:
        identity = {**(identity or {}), "metadata": metadata}
    config = (identity or {}).get("metadata") or {"backend": "sqlite"}
    staging = root + ".restoring"
    stores = {}
    try:
        if config.get("backend") != "sqlite":  # a shared database: check it before anything changes
            stores = {name: open_metastore(config, os.path.join(staging, "repos", name), name)
                      for name in manifest["repos"]}
            held = sorted(name for name, store in stores.items() if not store.is_empty())
            if held:
                raise BackupError(f"the metadata database already holds {', '.join(held)}; restore into a new one")
        moved = None
        if os.path.exists(root) and os.listdir(root):
            if not force:
                raise BackupError(f"{root} is not empty; --force moves it aside")
            moved = f"{root}.before-restore-{time.strftime('%Y%m%d-%H%M%S')}"
            os.replace(root, moved)
        if os.path.exists(staging):
            shutil.rmtree(staging)
        shutil.copytree(path, staging, ignore=shutil.ignore_patterns("manifest.json", "meta.db"))
        if metadata is not None:
            with open(os.path.join(staging, "deployment.json"), "w") as f:
                json.dump(identity, f, indent=2)
        for name in manifest["repos"]:
            store = stores.get(name) or stores.setdefault(
                name, open_metastore(config, os.path.join(staging, "repos", name), name))
            if os.path.exists(os.path.join(path, "repos", name, "meta.db")):
                store.load(os.path.join(path, "repos", name, "meta.db"))
    finally:
        for store in stores.values():
            store.close()
    os.replace(staging, root)
    report = verify(root, deep=deep, expect=manifest)
    report["moved_aside"] = moved
    dep = Deployment(root)
    try:
        for name in dep.names():
            dep.repo(name).audit.append("restore", actor, path, {"backup_created": manifest["created"],
                                                                 "ok": report["ok"]})
    finally:
        dep.close()
    return report


def verify(root: str, deep: bool = False, expect: dict | None = None) -> dict:
    """Check a deployment: every ref's tree is complete and every blob a changeset names is
    stored; with ``deep``, every stored object also decodes and matches its id (FR-OBJ-04). With a
    backup manifest in ``expect``, the refs and changeset counts must match it."""
    dep = Deployment(root)
    report = {"ok": True, "repos": {}}
    try:
        for name in dep.names():
            repo = dep.repo(name)
            r = {"refs": 0, "changesets": 0, "files_checked": 0, "missing": [], "corrupt": [], "mismatch": []}
            for ref, target, _ in repo.meta.list_refs():
                r["refs"] += 1
                try:
                    for p, kind, oid in repo.trees.walk(repo.root_tree(target)):
                        r["files_checked"] += 1
                        if kind != KIND_DIR and not repo.objects.has(oid):
                            r["missing"].append(f"{ref}:{p}")
                except (KeyError, ValueError, ObjectError, OSError) as e:  # a tree itself is missing or corrupt
                    r["missing"].append(f"{ref}: incomplete tree ({type(e).__name__}: {e})")
            after = None
            while batch := repo.meta.tail(after, 1000, data=True):
                for after, _, data in batch:
                    r["changesets"] += 1
                    for c in Changeset.decode(data).changes:
                        if c.blob and not repo.objects.has(c.blob):
                            r["missing"].append(c.blob)
            if deep:
                store = FileObjectStore(os.path.join(dep.repo_dir(name), "objects"))
                for key in store.iter_ids():
                    try:
                        decode_stored(store.get_stored(key), key_oid(key))
                    except (ObjectError, ValueError, TypeError):
                        r["corrupt"].append(key)
                r["objects_checked"] = True
            if expect is not None:
                want = expect["repos"].get(name)
                if want is None:
                    r["mismatch"].append("not in the backup")
                else:
                    refs = {ref: target for ref, target, _ in repo.meta.list_refs()}
                    if refs != want.get("refs", {}):
                        r["mismatch"].append("refs differ from the backup")
                    if r["changesets"] != want.get("changesets", 0):
                        r["mismatch"].append("changeset count differs from the backup")
            r["missing"] = r["missing"][:100]
            r["corrupt"] = r["corrupt"][:100]
            if r["missing"] or r["corrupt"] or r["mismatch"]:
                report["ok"] = False
            report["repos"][name] = r
        if expect is not None and set(expect["repos"]) - set(report["repos"]):
            report["ok"] = False
            report["absent"] = sorted(set(expect["repos"]) - set(report["repos"]))
    finally:
        dep.close()
    return report
