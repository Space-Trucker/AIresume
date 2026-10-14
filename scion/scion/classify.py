"""Semantic classification of changed files for review (FR-RV-05, ADR-09, R-05).

Each changed file is one of:

* ``docs``: documentation only: Markdown, reStructuredText or AsciiDoc anywhere, and plain-text
  files named as documentation (``README.txt``, ``LICENSE``, ``CHANGES.txt``...). A file is not
  documentation because of its directory: ``docs/conf.py`` is Python and ``requirements.txt`` a
  dependency manifest;
* ``comment_only``: only comments and insignificant whitespace changed;
* ``logic``: anything else, including binary files, kind changes, unknown languages and anything
  the classifier is unsure about.

The classifier is deliberately conservative. String literals are tracked and compared verbatim, so
comment markers inside strings are not comments and whitespace inside strings counts. In
shell-like languages ``#`` starts a comment only at the start of a word; in a Dockerfile only at
the start of a line. A comment is code where a tool reads it: a shebang, Python's coding line,
Go's build and compiler directives (and all of a cgo file's comments), Dockerfile parser directives.
A line comment that ends in a backslash may continue onto the next line (in C it does), so it is
never comment-only. In languages with regular-expression literals (JavaScript, TypeScript) a ``//``
after code on the same line is ambiguous, so only whole-line and block comments count there.
Indentation is structure in Python, YAML, INI-style configuration, Makefiles and Dockerfiles.
"""
from __future__ import annotations

import os
import re

# A language: line-comment markers, block-comment pairs, string delimiters, whether indentation
# is significant, whether "#" must start a word (or the line), whether trailing line comments are
# trusted, and the comments that are really directives: (only on the first n lines, pattern).
PY = {"line": ["#"], "block": [], "strings": ['"""', "'''", '"', "'"], "indent": True,
      "directives": (2, re.compile(r"#.*?coding[:=]"))}  # PEP 263
SHELL = {"line": ["#"], "block": [], "strings": ['"', "'"], "word_hash": True}
HASHY = {"line": ["#"], "block": [], "strings": ['"', "'"], "word_hash": True}
INDENTED = {**HASHY, "indent": True}  # YAML, INI-style configuration, Makefiles: indentation is structure
DOCKER = {"line": ["#"], "block": [], "strings": [], "whole_line": True, "indent": True,
          "directives": (None, re.compile(r"#\s*[A-Za-z_]+\s*="))}  # "# syntax=...", "# escape=..."
CLIKE = {"line": ["//"], "block": [("/*", "*/")], "strings": ['"', "'"]}
GO = {**CLIKE, "cgo": True, "directives": (None, re.compile(r"//(go:|line |export |\s*\+build)"))}
JSLIKE = {"line": ["//"], "block": [("/*", "*/")], "strings": ['"', "'", "`"], "no_trailing": True}
CSS = {"line": [], "block": [("/*", "*/")], "strings": ['"', "'"]}
SQL = {"line": ["--"], "block": [("/*", "*/")], "strings": ["'", '"']}
MARKUP = {"line": [], "block": [("<!--", "-->")], "strings": []}

LANGS = {
    ".py": PY, ".pyi": PY, ".bzl": PY, ".star": PY,
    ".sh": SHELL, ".bash": SHELL, ".zsh": SHELL,
    ".rb": HASHY, ".toml": HASHY, ".r": HASHY,
    ".yaml": INDENTED, ".yml": INDENTED, ".cfg": INDENTED, ".conf": INDENTED,
    ".c": CLIKE, ".h": CLIKE, ".cc": CLIKE, ".cpp": CLIKE, ".hpp": CLIKE, ".cxx": CLIKE, ".java": CLIKE,
    ".go": GO, ".rs": CLIKE, ".swift": CLIKE, ".kt": CLIKE, ".scala": CLIKE, ".cs": CLIKE,
    ".proto": CLIKE, ".dart": CLIKE, ".zig": CLIKE, ".scss": CLIKE, ".less": CLIKE,
    ".js": JSLIKE, ".jsx": JSLIKE, ".mjs": JSLIKE, ".cjs": JSLIKE, ".ts": JSLIKE, ".tsx": JSLIKE,
    ".css": CSS, ".sql": SQL, ".html": MARKUP, ".htm": MARKUP, ".xml": MARKUP, ".svg": MARKUP,
}
NAMED = {"Makefile": INDENTED, "GNUmakefile": INDENTED, "Dockerfile": DOCKER, "Containerfile": DOCKER,
         "BUILD": PY, "WORKSPACE": PY, "BUCK": PY, "CMakeLists.txt": HASHY}
DOC_EXTS = {".md", ".markdown", ".rst", ".adoc"}
DOC_NAMES = {"README", "LICENSE", "LICENCE", "COPYING", "NOTICE", "AUTHORS", "CONTRIBUTORS", "CONTRIBUTING",
             "CHANGES", "CHANGELOG", "NEWS", "HISTORY"}

DOCS, COMMENT_ONLY, LOGIC = "docs", "comment_only", "logic"
RANK = {DOCS: 0, COMMENT_ONLY: 1, LOGIC: 2}


class Ambiguous(Exception):
    """The text can't be split into code and comments with confidence."""


def language_for(path: str):
    base = os.path.basename(path)
    if base in NAMED:
        return NAMED[base]
    if base.startswith("Dockerfile.") or base.endswith(".dockerfile"):
        return DOCKER
    return LANGS.get(os.path.splitext(base)[1].lower())


def is_doc(path: str) -> bool:
    stem, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower()
    return ext in DOC_EXTS or (ext in ("", ".txt") and stem.upper() in DOC_NAMES)


def _literal(text: str) -> str:
    """Code that must survive whitespace normalization unchanged, as one token without whitespace."""
    return "\x00" + text.encode("utf-8", "surrogatepass").hex() + "\x00"


def strip_comments(text: str, lang: dict) -> str:
    """The text with comments removed; string literals and directives become single tokens, and a
    block comment within a line becomes a space (newlines inside block comments are kept)."""
    if "\x00" in text:
        raise Ambiguous("a NUL character")
    out, i, n, line = [], 0, len(text), 0
    strings = sorted(lang["strings"], key=len, reverse=True)
    first_lines, directive = lang.get("directives", (None, None))
    if text.startswith("#!"):  # a shebang chooses the interpreter: it is code
        i = text.find("\n") % (n + 1)
        out.append(_literal(text[:i]))
    line_start = i  # index where the current line's code began
    while i < n:
        c = text[i]
        if c == "\n":
            out.append(c)
            i += 1
            line += 1
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
            out.append(_literal(text[i:j]))
            line += text.count("\n", i, j)
            i = j
            continue
        block = next((b for b in lang["block"] if text.startswith(b[0], i)), None)
        if block is not None:
            j = text.find(block[1], i + len(block[0]))
            if j < 0:
                raise Ambiguous("unterminated block comment")
            newlines = text.count("\n", i, j)
            out.append("\n" * newlines or " ")  # a comment separates tokens
            line += newlines
            i = j + len(block[1])
            continue
        marker = next((m for m in lang["line"] if text.startswith(m, i)), None)
        if marker is not None:
            before = text[line_start:i]
            j = text.find("\n", i) % (n + 1)
            if directive is not None and (first_lines is None or line < first_lines) and directive.match(text, i):
                out.append(_literal(text[i:j]))  # a directive dressed as a comment
                i = j
                continue
            if (lang.get("whole_line") and before.strip()) or \
                    (lang.get("word_hash") and before and not before[-1].isspace()):
                out.append(c)  # "RUN a # b" in a Dockerfile, "$#" or "a#b" in a shell: not a comment
                i += 1
                continue
            if lang.get("no_trailing") and before.strip():
                raise Ambiguous("a line comment after code")
            if text[i:j].rstrip().endswith("\\"):
                raise Ambiguous("a line comment ending in a backslash may continue onto the next line")
            i = j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _normalize(text: str, lang: dict) -> list[str]:
    stripped = strip_comments(text, lang)
    if lang.get("indent"):  # indentation is significant: keep it; drop blank lines and trailing spaces
        return [line.rstrip() for line in stripped.split("\n") if line.strip()]
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
        if lang.get("cgo") and ('"C"' in old_t or '"C"' in new_t):
            return LOGIC  # cgo compiles the comments above 'import "C"'
        same = _normalize(old_t, lang) == _normalize(new_t, lang)
    except (UnicodeDecodeError, Ambiguous):
        return LOGIC
    return COMMENT_ONLY if same else LOGIC


def classify_diff(repo, base: str | None, head: str) -> list[dict]:
    """Every file that differs between ``base`` and ``head``, with its category. No reader's
    permissions filter the diff: the approval rules must see the files under restricted directories
    too, and whoever shows the result leaves out what its reader can't see."""
    out = []
    for path, x, y in repo.trees.diff(repo.root_tree(base), repo.root_tree(head)):
        old = repo.read_blob(x[1]) if x else None
        new = repo.read_blob(y[1]) if y else None
        cat = classify_file(path, old, new, x[0] if x else None, y[0] if y else None)
        out.append({"path": path, "status": "A" if x is None else "D" if y is None else "M", "category": cat})
    return out
