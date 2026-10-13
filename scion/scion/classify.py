"""Semantic classification of file changes for code review.

Each changed file is classified as one of:
  docs          documentation only (Markdown, reStructuredText, text, files under docs/)
  comment_only  only comments and/or insignificant whitespace changed
  logic         anything else (including binary files, mode changes, unknown languages)

The classifier is conservative: when in doubt, it says "logic".  String literals are tracked so
that comment markers inside strings are not mistaken for comments.
"""
from __future__ import annotations

import os

HASH = {"line": ["#"], "block": [], "strings": ['"""', "'''", '"', "'"], "indent": True}
HASH_PLAIN = {"line": ["#"], "block": [], "strings": ['"', "'"], "indent": False}
CLIKE = {"line": ["//"], "block": [("/*", "*/")], "strings": ['"', "'", "`"], "indent": False}
CSS = {"line": [], "block": [("/*", "*/")], "strings": ['"', "'"], "indent": False}
SQL = {"line": ["--"], "block": [("/*", "*/")], "strings": ["'", '"'], "indent": False}
LUA = {"line": ["--"], "block": [("--[[", "]]")], "strings": ['"', "'"], "indent": False}
MARKUP = {"line": [], "block": [("<!--", "-->")], "strings": [], "indent": False}

LANGS = {
    ".py": HASH, ".pyi": HASH,
    ".sh": HASH_PLAIN, ".bash": HASH_PLAIN, ".zsh": HASH_PLAIN, ".rb": HASH_PLAIN,
    ".yaml": HASH_PLAIN, ".yml": HASH_PLAIN, ".toml": HASH_PLAIN, ".pl": HASH_PLAIN,
    ".r": HASH_PLAIN, ".cfg": HASH_PLAIN, ".conf": HASH_PLAIN, ".bzl": HASH, ".star": HASH,
    ".c": CLIKE, ".h": CLIKE, ".cc": CLIKE, ".cpp": CLIKE, ".hpp": CLIKE, ".cxx": CLIKE,
    ".java": CLIKE, ".js": CLIKE, ".jsx": CLIKE, ".mjs": CLIKE, ".ts": CLIKE, ".tsx": CLIKE,
    ".go": CLIKE, ".rs": CLIKE, ".swift": CLIKE, ".kt": CLIKE, ".scala": CLIKE, ".cs": CLIKE,
    ".proto": CLIKE, ".jsonc": CLIKE, ".dart": CLIKE, ".zig": CLIKE,
    ".css": CSS, ".scss": CLIKE, ".less": CLIKE,
    ".sql": SQL, ".lua": LUA, ".hs": SQL,
    ".html": MARKUP, ".htm": MARKUP, ".xml": MARKUP, ".svg": MARKUP,
}
NAMED = {"Makefile": HASH_PLAIN, "Dockerfile": HASH_PLAIN, "BUILD": HASH, "WORKSPACE": HASH,
         "BUCK": HASH, "CMakeLists.txt": HASH_PLAIN}
DOC_EXTS = {".md", ".markdown", ".rst", ".txt", ".adoc"}

DOCS, COMMENT_ONLY, LOGIC = "docs", "comment_only", "logic"
RANK = {DOCS: 0, COMMENT_ONLY: 1, LOGIC: 2}


def language_for(path: str):
    base = os.path.basename(path)
    if base in NAMED:
        return NAMED[base]
    return LANGS.get(os.path.splitext(base)[1].lower())


def is_doc(path: str) -> bool:
    if path.startswith("docs/") or "/docs/" in path:
        return True
    return os.path.splitext(path)[1].lower() in DOC_EXTS


def strip_comments(text: str, lang: dict) -> str:
    out = []
    i, n = 0, len(text)
    strings = sorted(lang["strings"], key=len, reverse=True)
    while i < n:
        matched = False
        for q in strings:
            if text.startswith(q, i):
                j = i + len(q)
                while j < n and not text.startswith(q, j):
                    j += 2 if text[j] == "\\" else 1
                j = min(n, j + len(q))
                out.append(text[i:j])
                i = j
                matched = True
                break
        if matched:
            continue
        for start, end in lang["block"]:
            if text.startswith(start, i):
                j = text.find(end, i + len(start))
                skipped = text[i:n if j < 0 else j + len(end)]
                out.append("\n" * skipped.count("\n"))
                i = n if j < 0 else j + len(end)
                matched = True
                break
        if matched:
            continue
        for marker in lang["line"]:
            if text.startswith(marker, i):
                j = text.find("\n", i)
                i = n if j < 0 else j
                matched = True
                break
        if matched:
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _normalize(text: str, lang: dict) -> list[str]:
    stripped = strip_comments(text, lang)
    if lang.get("indent"):
        # Indentation is significant: keep it, drop blank lines and trailing whitespace.
        return [l.rstrip() for l in stripped.splitlines() if l.strip()]
    return " ".join(stripped.split()).split(" ") if stripped.split() else []


def classify_file(path: str, old: bytes | None, new: bytes | None,
                  old_kind: str | None = None, new_kind: str | None = None) -> str:
    if is_doc(path):
        return DOCS
    if old is not None and new is not None and old_kind and new_kind and old_kind != new_kind:
        return LOGIC
    lang = language_for(path)
    if lang is None:
        return LOGIC
    try:
        old_t = (old or b"").decode("utf-8")
        new_t = (new or b"").decode("utf-8")
    except UnicodeDecodeError:
        return LOGIC
    return COMMENT_ONLY if _normalize(old_t, lang) == _normalize(new_t, lang) else LOGIC


def classify_diff(repo, base: str | None, head: str) -> list[dict]:
    out = []
    for f in repo.diff(base, head):
        old = repo.read_blob(f["old"]["id"]) if f["old"] else None
        new = repo.read_blob(f["new"]["id"]) if f["new"] else None
        cat = classify_file(f["path"], old, new,
                            f["old"]["kind"] if f["old"] else None,
                            f["new"]["kind"] if f["new"] else None)
        out.append({"path": f["path"], "status": f["status"], "category": cat})
    return out
