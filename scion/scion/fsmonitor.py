"""Filesystem monitor for working copies (Linux inotify via ctypes; no dependencies).

``scn watch`` starts a background watcher that records every changed path in a journal.
``scn status`` then examines only the paths reported since its last run, plus paths it already
knew were dirty, instead of stat-ing the whole working copy.

Before each query, a "sync cookie" file is created and the client waits until the watcher has
journaled it.  inotify events are ordered, so every change made before the query is visible to
it.  If the kernel queue overflows, the watcher restarts, or no watcher is running, status falls
back to a full scan.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import json
import os
import select
import signal
import struct
import subprocess
import sys
import time
import uuid

IN_MODIFY = 0x00000002
IN_ATTRIB = 0x00000004
IN_CLOSE_WRITE = 0x00000008
IN_MOVED_FROM = 0x00000040
IN_MOVED_TO = 0x00000080
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_DELETE_SELF = 0x00000400
IN_MOVE_SELF = 0x00000800
IN_Q_OVERFLOW = 0x00004000
IN_IGNORED = 0x00008000
IN_ONLYDIR = 0x01000000
IN_DONT_FOLLOW = 0x02000000
IN_ISDIR = 0x40000000

WATCH_MASK = (IN_MODIFY | IN_ATTRIB | IN_CLOSE_WRITE | IN_MOVED_FROM | IN_MOVED_TO | IN_CREATE |
              IN_DELETE | IN_DELETE_SELF | IN_MOVE_SELF | IN_ONLYDIR | IN_DONT_FOLLOW)
_EVENT = struct.Struct("iIII")
COOKIE_PREFIX = ".scn-cookie-"
SCN_DIR = ".scn"
RESCAN = "!RESCAN"


def _state_dir(root: str) -> str:
    return os.path.join(root, SCN_DIR, "fsmonitor")


def supported() -> bool:
    return sys.platform.startswith("linux")


class Watcher:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
        self.fd = self.libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1 failed")
        self.wds: dict[int, str] = {}
        self.dir = _state_dir(self.root)
        os.makedirs(self.dir, exist_ok=True)
        self.session = uuid.uuid4().hex
        self.journal = open(os.path.join(self.dir, "journal"), "w")  # new session: fresh journal
        self._write_meta("session", self.session)
        self._write_meta("pid", str(os.getpid()))
        self._add_tree("")
        self._heartbeat()

    def _write_meta(self, name: str, value: str) -> None:
        tmp = os.path.join(self.dir, f".{name}.tmp")
        with open(tmp, "w") as f:
            f.write(value)
        os.replace(tmp, os.path.join(self.dir, name))

    def _heartbeat(self) -> None:
        self._write_meta("heartbeat", str(time.time()))

    def _add_watch(self, rel: str) -> None:
        path = os.path.join(self.root, rel) if rel else self.root
        wd = self.libc.inotify_add_watch(self.fd, path.encode(), WATCH_MASK)
        if wd >= 0:
            self.wds[wd] = rel

    def _add_tree(self, rel: str) -> list[str]:
        found = []
        top = os.path.join(self.root, rel) if rel else self.root
        for dirpath, dirnames, filenames in os.walk(top):
            r = os.path.relpath(dirpath, self.root).replace(os.sep, "/")
            r = "" if r == "." else r
            if r == "":
                dirnames[:] = [d for d in dirnames if d != SCN_DIR]
            self._add_watch(r)
            found.extend(f"{r}/{f}" if r else f for f in filenames)
        return found

    def _record(self, paths) -> None:
        for p in paths:
            self.journal.write(p + "\n")
        self.journal.flush()

    def _handle(self, data: bytes) -> None:
        out = []
        pos = 0
        while pos < len(data):
            wd, mask, _cookie, length = _EVENT.unpack_from(data, pos)
            name = data[pos + _EVENT.size: pos + _EVENT.size + length].rstrip(b"\0").decode("utf-8", "surrogateescape")
            pos += _EVENT.size + length
            if mask & IN_Q_OVERFLOW:
                out.append(RESCAN)
                continue
            rel = self.wds.get(wd)
            if rel is None:
                continue
            if mask & IN_IGNORED:
                self.wds.pop(wd, None)
                continue
            path = f"{rel}/{name}" if rel and name else (name or rel)
            if path == SCN_DIR or path.startswith(SCN_DIR + "/"):
                continue
            if mask & IN_ISDIR and mask & (IN_CREATE | IN_MOVED_TO):
                out.extend(self._add_tree(path))
            out.append(path)
        if out:
            self._record(out)

    def run(self, stop=None) -> None:
        last_beat = time.time()
        while stop is None or not stop.is_set():
            r, _, _ = select.select([self.fd], [], [], 0.5)
            if r:
                try:
                    data = os.read(self.fd, 1 << 18)
                except BlockingIOError:
                    data = b""
                if data:
                    self._handle(data)
            if time.time() - last_beat > 1.0:
                self._heartbeat()
                last_beat = time.time()

    def close(self) -> None:
        os.close(self.fd)
        self.journal.close()


# ---------------------------------------------------------------------------------------------
# Client side
# ---------------------------------------------------------------------------------------------
def _read(root: str, name: str) -> str | None:
    try:
        with open(os.path.join(_state_dir(root), name)) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def is_running(root: str) -> bool:
    pid, beat = _read(root, "pid"), _read(root, "heartbeat")
    if not pid or not beat:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError):
        return False
    return time.time() - float(beat) < 5.0


def query(root: str, token: dict | None, sync_timeout: float = 2.0):
    """Return (new_token, changed_paths, rescan_needed), or None if no watcher is running."""
    if not supported() or not is_running(root):
        return None
    session = _read(root, "session")
    journal = os.path.join(_state_dir(root), "journal")
    cookie = COOKIE_PREFIX + uuid.uuid4().hex
    cookie_path = os.path.join(root, cookie)
    with open(cookie_path, "w"):
        pass
    try:
        deadline = time.time() + sync_timeout
        while True:
            with open(journal) as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                start = token["offset"] if token and token.get("session") == session and token["offset"] <= end else 0
                f.seek(start)
                lines = f.read().splitlines()
            if cookie in lines:
                break
            if time.time() > deadline:
                return None  # watcher is stuck: fall back to a full scan
            time.sleep(0.005)
    finally:
        os.unlink(cookie_path)
    new_token = {"session": session, "offset": end}
    fresh = token is None or token.get("session") != session
    paths = {l for l in lines if l and not l.startswith(COOKIE_PREFIX) and l != RESCAN}
    return new_token, paths, fresh or RESCAN in lines


def start(root: str) -> int:
    root = os.path.abspath(root)
    if is_running(root):
        return int(_read(root, "pid"))
    log = open(os.path.join(root, SCN_DIR, "fsmonitor.log"), "a")
    proc = subprocess.Popen([sys.executable, "-m", "scion.fsmonitor", root], stdout=log, stderr=log,
                            start_new_session=True,
                            env={**os.environ, "PYTHONPATH": os.path.dirname(os.path.dirname(__file__))})
    for _ in range(200):
        if is_running(root):
            break
        time.sleep(0.02)
    return proc.pid


def stop(root: str) -> bool:
    pid = _read(root, "pid")
    if not pid:
        return False
    try:
        os.kill(int(pid), signal.SIGTERM)
    except (OSError, ValueError):
        return False
    for name in ("pid", "heartbeat"):
        try:
            os.unlink(os.path.join(_state_dir(root), name))
        except FileNotFoundError:
            pass
    return True


def main(argv=None) -> None:
    root = (argv or sys.argv[1:])[0]
    w = Watcher(root)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        w.run()
    finally:
        w.close()


if __name__ == "__main__":
    main()
