"""Semantic classification of changed files for review (FR-RV-05, ADR-09, R-05).

Each changed file is one of:

* ``docs``: documentation only (Markdown, reStructuredText, plain text, anything under ``docs/``);
* ``comment_only``: only comments and insignificant whitespace changed;
* ``logic``: anything else, including binary files, kind changes, unknown languages and anything
  the classifier is unsure about.

The classifier is deliberately conservative. String literals are tracked, so comment markers
inside strings are not comments. In shell-like languages ``#`` starts a comment only at the start
of a word. In languages with regular-expression literals (JavaScript, TypeScript) a ``//`` after
code on the same line is ambiguous, so only whole-line and block comments count there.
"""
from __future__ import annotations

import os

# A language: line-comment markers, block-comment pairs, string delimiters, whether indentation
# is significant, whether "#" must start a word, and whether trailing line comments are trusted.
PY = {"line": ["#"], "block": [], "strings": ['"""', "'''", '"', "'"], "indent": True}
SHELL = {"line": ["#"], "block": [], "strings": ['"', "'"], "word_hash": True}
HASHY = {"line": ["#"], "block": [], "strings": ['"', "'"], "word_hash": True}
CLIKE = {"line": ["//"], "block": [("/*", "*/")], "strings": ['"', "'"]}
JSLIKE = {"line": ["//"], "block": [("/*", "*/")], "strings": ['"', "'", "`"], "no_trailing": True}
CSS = {"line": [], "block": [("/*", "*/")], "strings": ['"', "'"]}
SQL = {"line": ["--"], "block": [("/*", "*/")], "strings": ["'", '"']}
MARKUP = {"line": [], "block": [("<!--", "-->")], "strings": []}

LANGS = {
    ".py": PY, ".pyi": PY, ".bzl": PY, ".star": PY,
    ".sh": SHELL, ".bash": SHELL, ".zsh": SHELL,
    ".rb": HASHY, ".yaml": HASHY, ".yml": HASHY, ".toml": HASHY, ".cfg": HASHY, ".conf": HASHY, ".r": HASHY,
    ".c": CLIKE, ".h": CLIKE, ".cc": CLIKE, ".cpp": CLIKE, ".hpp": CLIKE, ".cxx": CLIKE, ".java": CLIKE,
    ".go": CLIKE, ".rs": CLIKE, ".swift": CLIKE, ".kt": CLIKE, ".scala": CLIKE, ".cs": CLIKE,
    ".proto": CLIKE, ".dart": CLIKE, ".zig": CLIKE, ".scss": CLIKE, ".less": CLIKE,
    ".js": JSLIKE, ".jsx": JSLIKE, ".mjs": JSLIKE, ".cjs": JSLIKE, ".ts": JSLIKE, ".tsx": JSLIKE,
    ".css": CSS, ".sql": SQL, ".html": MARKUP, ".htm": MARKUP, ".xml": MARKUP, ".svg": MARKUP,
}
NAMED = {"Makefile": HASHY, "Dockerfile": HASHY, "BUILD": PY, "WORKSPACE": PY, "BUCK": PY,
         "CMakeLists.txt": HASHY}
DOC_EXTS = {".md", ".markdown", ".rst", ".txt", ".adoc"}

DOCS, COMMENT_ONLY, LOGIC = "docs", "comment_only", "logic"
RANK = {DOCS: 0, COMMENT_ONLY: 1, LOGIC: 2}


class Ambiguous(Exception):
    """The text can't be split into code and comments with confidence."""


def language_for(path: str):
    base = os.path.basename(path)
    if base in NAMED:
        return NAMED[base]
    return LANGS.get(os.path.splitext(base)[1].lower())


def is_doc(path: str) -> bool:
    if path.startswith("docs/") or "/docs/" in path:
        return True
    return os.path.splitext(path)[1].lower() in DOC_EXTS and os.path.basename(path) not in NAMED


def strip_comments(text: str, lang: dict) -> str:
    """The text with comments removed (newlines inside block comments are kept)."""
    out, i, n = [], 0, len(text)
    strings = sorted(lang["strings"], key=len, reverse=True)
    line_start = 0  # index where the current line's code began
    while i < n:
        c = text[i]
        if c == "\n":
            out.append(c)
            i += 1
            line_start = i
            continue
        q = next((q for q in strings if text.startswith(q, i)), None)
        if q is not None:
            j = i + len(q)
            while j < n and not text.startswith(q, j):
                if text[j] == "\\":
                    j += 1
                elif text[j] == "\n" and len(q) == 1 and q != "`":
                    raise Ambiguous("unterminated string")
                j += 1
            if j >= n:
                raise Ambiguous("unterminated string")
            j += len(q)
            out.append(text[i:j])
            i = j
            continue
        block = next((b for b in lang["block"] if text.startswith(b[0], i)), None)
        if block is not None:
            j = text.find(block[1], i + len(block[0]))
            if j < 0:
                raise Ambiguous("unterminated block comment")
            out.append("\n" * text.count("\n", i, j))
            i = j + len(block[1])
            continue
        marker = next((m for m in lang["line"] if text.startswith(m, i)), None)
        if marker is not None:
            before = text[line_start:i]
            if lang.get("word_hash") and before and not before[-1].isspace():
                out.append(c)  # "$#" or "a#b": not a comment
                i += 1
                continue
            if lang.get("no_trailing") and before.strip():
                raise Ambiguous("a line comment after code")
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _normalize(text: str, lang: dict) -> list[str]:
    stripped = strip_comments(text, lang)
    if lang.get("indent"):  # indentation is significant: keep it; drop blank lines and trailing spaces
        return [line.rstrip() for line in stripped.splitlines() if line.strip()]
    return stripped.split()


def classify_file(path: str, old: bytes | None, new: bytes | None, old_kind: str | None = None,
                  new_kind: str | None = None) -> str:
    if is_doc(path):
        return DOCS
    if old is None or new is None:
        return LOGIC  # adding or deleting a file can change behavior even if it is all comments
    if old_kind and new_kind and old_kind != new_kind:
        return LOGIC  # a mode or kind change
    if "l" in (old_kind, new_kind):
        return LOGIC  # symlinks are code
    lang = language_for(path)
    if lang is None:
        return LOGIC
    try:
        old_t = (old or b"").decode("utf-8")
        new_t = (new or b"").decode("utf-8")
        same = _normalize(old_t, lang) == _normalize(new_t, lang)
    except (UnicodeDecodeError, Ambiguous):
        return LOGIC
    return COMMENT_ONLY if same else LOGIC


def classify_diff(repo, base: str | None, head: str) -> list[dict]:
    """Every file that differs between ``base`` and ``head``, with its category."""
    out = []
    for f in repo.diff(base, head):
        old = repo.read_blob(f["old"]["id"]) if f["old"] else None
        new = repo.read_blob(f["new"]["id"]) if f["new"] else None
        cat = classify_file(f["path"], old, new, f["old"]["kind"] if f["old"] else None,
                            f["new"]["kind"] if f["new"] else None)
        out.append({"path": f["path"], "status": f["status"], "category": cat})
    return out
