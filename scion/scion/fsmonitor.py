"""Filesystem monitor for working copies (FR-CL-04; 06 §6.6 and §6.8, status).

A background watcher (Linux inotify through ``ctypes``) appends every changed path to a journal.
``scn status`` then checks only the paths journaled since its last query, plus the paths it already
knew were dirty, instead of stat-ing the whole working copy.

Before reading the journal, the client creates a *sync cookie* file and waits until the watcher has
journaled it. inotify delivers events in order, so every change made before the query is in the
journal by then. When no watcher is running, the watcher restarted (a new session), the kernel
queue overflowed, or the cookie does not arrive in time, the client falls back to a full scan.

Journal lines: ``P <path>`` a path changed, ``C <name>`` a sync cookie, ``O`` events were lost.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import os
import select
import signal
import struct
import subprocess
import sys
import time
import uuid

IN_MODIFY, IN_ATTRIB, IN_CLOSE_WRITE = 0x2, 0x4, 0x8
IN_MOVED_FROM, IN_MOVED_TO, IN_CREATE, IN_DELETE = 0x40, 0x80, 0x100, 0x200
IN_DELETE_SELF, IN_MOVE_SELF, IN_Q_OVERFLOW, IN_IGNORED = 0x400, 0x800, 0x4000, 0x8000
IN_ONLYDIR, IN_DONT_FOLLOW, IN_ISDIR = 0x01000000, 0x02000000, 0x40000000
WATCH_MASK = (IN_MODIFY | IN_ATTRIB | IN_CLOSE_WRITE | IN_MOVED_FROM | IN_MOVED_TO | IN_CREATE | IN_DELETE |
              IN_DELETE_SELF | IN_MOVE_SELF | IN_ONLYDIR | IN_DONT_FOLLOW)
_EVENT = struct.Struct("iIII")
SCN_DIR = ".scn"
ROTATE_BYTES = 16 << 20


def state_dir(root: str) -> str:
    return os.path.join(root, SCN_DIR, "fsmonitor")


def supported() -> bool:
    return sys.platform.startswith("linux")


class Watcher:
    """Runs in its own process: ``python -m scion.fsmonitor <root>``."""

    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
        self.fd = self.libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1 failed")
        self.dir = state_dir(self.root)
        self.cookies = os.path.join(self.dir, "cookies")
        os.makedirs(self.cookies, exist_ok=True)
        self.wds: dict[int, str | None] = {}  # watch descriptor -> directory (None: the cookie directory)
        self._open_session()
        self._watch(self.cookies, None)
        self._watch_tree("")
        self._meta("pid", str(os.getpid()))
        self._meta("session", self.session)  # written last: the watcher is ready

    def _open_session(self) -> None:
        self.session = uuid.uuid4().hex
        self.journal = open(os.path.join(self.dir, "journal"), "w")
        self.journal.write(f"S {self.session}\n")
        self.journal.flush()

    def _meta(self, name: str, value: str) -> None:
        tmp = os.path.join(self.dir, f".{name}.tmp")
        with open(tmp, "w") as f:
            f.write(value)
        os.replace(tmp, os.path.join(self.dir, name))

    def _watch(self, path: str, rel: str | None) -> bool:
        wd = self.libc.inotify_add_watch(self.fd, os.fsencode(path), WATCH_MASK)
        if wd < 0:
            return False
        self.wds[wd] = rel
        return True

    def _watch_tree(self, rel: str) -> list[str]:
        """Watch a directory and everything beneath it; returns the files found, which may have
        been created before their directory was watched."""
        found = []
        top = os.path.join(self.root, rel) if rel else self.root
        for dirpath, dirnames, filenames in os.walk(top):
            r = os.path.relpath(dirpath, self.root).replace(os.sep, "/")
            r = "" if r == "." else r
            if r == "":
                dirnames[:] = [d for d in dirnames if d != SCN_DIR]
            if not self._watch(dirpath, r):
                dirnames[:] = []
                continue
            found.extend(f"{r}/{f}" if r else f for f in filenames)
            found.extend(f"{r}/{d}" if r else d for d in dirnames if os.path.islink(os.path.join(dirpath, d)))
        return found

    def _handle(self, data: bytes) -> None:
        lines, pos = [], 0
        while pos < len(data):
            wd, mask, _cookie, length = _EVENT.unpack_from(data, pos)
            name = os.fsdecode(data[pos + _EVENT.size:pos + _EVENT.size + length].rstrip(b"\0"))
            pos += _EVENT.size + length
            if mask & IN_Q_OVERFLOW:
                lines.append("O")
                continue
            if wd not in self.wds:
                continue
            rel = self.wds[wd]
            if mask & IN_IGNORED:
                del self.wds[wd]
                continue
            if rel is None:  # the cookie directory
                if mask & (IN_CREATE | IN_MOVED_TO) and name:
                    lines.append(f"C {name}")
                continue
            if not name:
                continue  # an event on the watched directory itself; its parent reports it
            path = f"{rel}/{name}" if rel else name
            if rel == "" and name == SCN_DIR:
                continue
            lines.append(f"P {path}")
            if mask & IN_ISDIR and mask & (IN_CREATE | IN_MOVED_TO):
                lines.extend(f"P {p}" for p in self._watch_tree(path))
        if lines:
            self.journal.write("\n".join(lines) + "\n")
            self.journal.flush()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        poller = select.poll()
        poller.register(self.fd, select.POLLIN)
        while True:
            if poller.poll(1000):
                try:
                    data = os.read(self.fd, 1 << 16)
                except BlockingIOError:
                    continue
                self._handle(data)
            if not os.path.isdir(self.root):
                return
            if self.journal.tell() > ROTATE_BYTES:  # clients rescan once, then continue incrementally
                self.journal.close()
                self._open_session()
                self._meta("session", self.session)


# ======================================================================================= client
_children: dict[str, subprocess.Popen] = {}  # watchers this process started, so stop() can reap them


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _read(path: str) -> str | None:
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def running(root: str) -> int | None:
    pid = _read(os.path.join(state_dir(root), "pid"))
    return int(pid) if pid and pid.isdigit() and _pid_alive(int(pid)) else None


def start(root: str, timeout: float = 10.0) -> int:
    """Start a watcher for ``root`` (if none is running) and wait until it is watching."""
    root = os.path.abspath(root)
    pid = running(root)
    if pid:
        return pid
    d = state_dir(root)
    os.makedirs(d, exist_ok=True)
    for name in ("session", "pid"):
        if os.path.exists(os.path.join(d, name)):
            os.unlink(os.path.join(d, name))
    pkg_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, [pkg_parent, os.environ.get("PYTHONPATH")]))}
    with open(os.path.join(d, "watcher.log"), "ab") as log:
        proc = subprocess.Popen([sys.executable, "-m", "scion.fsmonitor", root], stdin=subprocess.DEVNULL,
                                stdout=log, stderr=log, start_new_session=True, env=env)
    _children[root] = proc
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _read(os.path.join(d, "session")):
            return proc.pid
        if proc.poll() is not None:
            raise RuntimeError(f"the fsmonitor exited; see {os.path.join(d, 'watcher.log')}")
        time.sleep(0.02)
    proc.terminate()
    raise RuntimeError("the fsmonitor did not start in time")


def stop(root: str) -> bool:
    pid = running(root)
    if not pid:
        return False
    os.kill(pid, signal.SIGTERM)
    proc = _children.pop(os.path.abspath(root), None)
    if proc is not None and proc.pid == pid:
        proc.wait(5)  # started by this process: reap it
        return True
    for _ in range(200):
        if not _pid_alive(pid):
            break
        time.sleep(0.01)
    return True


def query(root: str, token: list | None, timeout: float = 2.0):
    """Changes since ``token``: ``(new_token, paths, rescan)``, or None when no watcher answers.

    ``rescan`` means the caller must do a full scan (first query of a session, or lost events);
    the new token is valid either way."""
    root = os.path.abspath(root)
    d = state_dir(root)
    session = _read(os.path.join(d, "session"))
    if not session or not running(root):
        return None
    cookie = f"{os.getpid()}-{uuid.uuid4().hex}"
    cookie_path = os.path.join(d, "cookies", cookie)
    with open(cookie_path, "w"):
        pass
    try:
        rescan = token is None or token[0] != session
        offset = 0 if rescan else int(token[1])
        paths: set[str] = set()
        deadline = time.time() + timeout
        with open(os.path.join(d, "journal"), "rb") as j:
            j.seek(offset)
            buf = b""
            while True:
                chunk = j.read()
                if chunk:
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        offset += len(line) + 1
                        text = os.fsdecode(line)
                        if text.startswith("P "):
                            paths.add(text[2:])
                        elif text == "O":
                            rescan = True
                        elif text.startswith("S ") and text[2:] != session:
                            return None  # rotated under us: try again next time
                        elif text == f"C {cookie}":
                            return [session, offset], sorted(paths), rescan
                    continue
                if time.time() > deadline:
                    return None  # the watcher is stuck: fall back to a full scan
                time.sleep(0.005)
    finally:
        try:
            os.unlink(cookie_path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    Watcher(sys.argv[1]).run()
